import contextlib
import io
import threading
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('reset_es8', Path(__file__).parents[1] / 'reset_es8.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class FakeReset(m.Reset):
    def __init__(self, root):
        super().__init__('TEST_USB', root, report_dir=root / 'reports')
        self.events = []
        self.fail = None

    def check_files(self): self.events.append('check_files')
    def check_device(self): self.events.append('check_device')
    def identity(self): self.events.append('identity')
    def check_preserved(self): self.events.append('preserved')
    def restore(self, part):
        self.events.append('restore_' + part)
        if self.fail == part: raise RuntimeError('read-back mismatch')
    def twrp(self, command):
        self.events.append(command)
        if self.fail == command: raise RuntimeError('TWRP failure')
    def verify_empty_data(self):
        self.events.append('verify_data')
        if self.fail == 'dirty_data': raise RuntimeError('Apps remain')
    def verify_empty_cache(self): self.events.append('verify_cache')
    def shell(self, command): self.events.append(command); return ''


class ResetTests(unittest.TestCase):
    def test_device_only_inspection_cannot_read_or_restore_images(self):
        reset = m.Reset('TEST_USB', None)
        with self.assertRaisesRegex(RuntimeError, 'Recovery image directory'):
            reset.check_files()
        with patch.object(reset, 'identity') as identity:
            with self.assertRaisesRegex(RuntimeError, 'Recovery image directory'):
                reset.restore('system')
            identity.assert_not_called()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.reset = FakeReset(self.root)
    def tearDown(self): self.temp.cleanup()

    def test_progress_reports_wait_and_completion(self):
        notified = threading.Event()
        lines = []
        def capture(message, **kwargs):
            lines.append(message)
            if 'still waiting' in message:
                notified.set()
        with patch('builtins.print', side_effect=capture):
            with m.progress('Transfer', interval=0.01):
                self.assertTrue(notified.wait(2))
        self.assertTrue(any('completed' in line for line in lines))

    def test_progress_failure_never_reports_completion(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with self.assertRaisesRegex(RuntimeError, 'failed'):
                with m.progress('Transfer'):
                    raise RuntimeError('failed')
        self.assertIn('stopped before completion', output.getvalue())
        self.assertNotIn('completed', output.getvalue())

    def test_wrong_confirmation_cannot_write(self):
        with self.assertRaises(RuntimeError): self.reset.apply(lambda _: 'ERASE TEST_USB')
        self.assertEqual(self.reset.events, ['check_files', 'check_device'])
        self.assertIsNone(self.reset.report_path)

    def test_recheck_identity_after_confirmation(self):
        def confirm(_):
            self.reset.check_device = lambda: m.require(False, 'device changed')
            return 'ERASE'
        with self.assertRaises(RuntimeError): self.reset.apply(confirm)
        self.assertFalse(any(e.startswith('restore_') for e in self.reset.events))

    def test_success_order_and_no_boot_or_recovery_write(self):
        self.reset.apply(lambda _: 'ERASE')
        events = self.reset.events
        self.assertLess(events.index('restore_system'), events.index('restore_vendor'))
        self.assertLess(events.index('restore_vendor'), events.index('format data'))
        self.assertLess(events.index('verify_data'), events.index('wipe cache'))
        self.assertIn('verify_cache', events)
        self.assertEqual(self.reset.report['status'], 'complete_left_in_twrp')
        self.assertTrue(self.reset.report['userdata_erased'])
        with self.assertRaises(RuntimeError): m.Reset.restore(self.reset, 'boot')
        with self.assertRaises(RuntimeError): m.Reset.restore(self.reset, 'recovery')

    def test_restore_failure_prevents_format(self):
        for part in ('system', 'vendor'):
            reset = FakeReset(self.root); reset.fail = part
            with self.assertRaises(RuntimeError): reset.apply(lambda _: 'ERASE')
            self.assertNotIn('format data', reset.events)
            self.assertEqual(reset.report['status'], 'failed_remain_in_twrp')
            self.assertNotIn('userdata_erased', reset.report)

    def test_format_failure_or_remaining_apps_cannot_report_success(self):
        for failure in ('format data', 'dirty_data', 'wipe cache'):
            reset = FakeReset(self.root); reset.fail = failure
            with self.assertRaises(RuntimeError): reset.apply(lambda _: 'ERASE')
            self.assertEqual(reset.report['status'], 'failed_remain_in_twrp')
            self.assertNotIn('userdata_erased', reset.report)

    def test_default_cli_never_calls_apply(self):
        with patch.object(m, 'Reset', return_value=self.reset), patch('sys.argv', ['reset_es8.py','--serial','TEST_USB','--backup-dir',str(self.root)]):
            m.main()
        self.assertEqual(self.reset.events, ['check_files','check_device'])

    def test_local_check_does_not_contact_device(self):
        with patch.object(m, 'Reset', return_value=self.reset), patch('sys.argv', ['reset_es8.py','--serial','TEST_USB','--backup-dir',str(self.root),'--check-files']):
            m.main()
        self.assertEqual(self.reset.events, ['check_files'])

    def test_auto_usb_selection_is_pinned(self):
        reset = m.Reset(None, self.root)
        selected = subprocess.CompletedProcess([], 0, stdout='TEST_USB\n', stderr='')
        with patch.object(m.subprocess, 'run', return_value=selected) as run:
            reset.run('get-devpath')
            reset.run('shell', 'id -u')
        self.assertEqual(run.call_args_list[0].args[0], ['adb', '-d', 'get-serialno'])
        self.assertEqual(run.call_args_list[1].args[0], ['adb', '-s', 'TEST_USB', 'get-devpath'])
        self.assertEqual(run.call_args_list[2].args[0], ['adb', '-s', 'TEST_USB', 'shell', 'id -u'])
        self.assertEqual(reset.report['serial'], 'TEST_USB')

    def test_auto_selection_failure_never_runs_device_commands(self):
        for code, output, error in [(1, '', 'no devices found'),
                                    (1, '', 'more than one device'),
                                    (1, '', 'device offline'),
                                    (0, 'unknown', ''),
                                    (0, '192.168.1.71:5555', '')]:
            reset = m.Reset(None, self.root)
            with patch.object(m.subprocess, 'run', return_value=subprocess.CompletedProcess(
                    [], code, stdout=output, stderr=error)) as run:
                with self.assertRaisesRegex(RuntimeError, 'single USB device'):
                    reset.identity()
                self.assertEqual(run.call_count, 1)

    def test_auto_selected_incompatible_device_rejected(self):
        reset = m.Reset(None, self.root)
        results = [subprocess.CompletedProcess([], 0, stdout=value, stderr='')
                   for value in ['TEST_USB', 'usb:1-3', 'TEST_USB', 'crown']]
        with patch.object(m.subprocess, 'run', side_effect=results):
            with self.assertRaisesRegex(RuntimeError, 'not an ES8 Gen 2'):
                reset.check_device()

    def test_cli_local_check_without_serial_never_contacts_adb(self):
        with patch.object(m.Reset, 'check_files') as check, patch.object(m.subprocess, 'run') as run, patch(
                'sys.argv', ['reset_es8.py', '--backup-dir', str(self.root), '--check-files']):
            m.main()
        check.assert_called_once()
        run.assert_not_called()

    def test_corrupt_source_rejected(self):
        reset = m.Reset('TEST_USB', self.root)
        (self.root/'boot-original.img').write_bytes(b'bad')
        reset.baseline['partitions']['boot']['bytes'] = 3
        with self.assertRaisesRegex(RuntimeError, 'SHA256'): reset.check_files()

    def test_network_wrong_model_and_wrong_recovery_rejected(self):
        reset = m.Reset('TEST_USB', self.root)
        replies = {'getprop ro.serialno':'TEST_USB', 'getprop ro.product.device':'athena',
                   'getprop ro.twrp.version':'3.7.0_9-0', 'id -u':'0'}
        with patch.object(reset, 'run', return_value=subprocess.CompletedProcess([],0,stdout='usb:1-3')), patch.object(reset, 'shell', side_effect=lambda cmd: replies[cmd]):
            reset.identity()
            for cmd,value in [('getprop ro.product.device','crown'),('getprop ro.twrp.version',''),('getprop ro.serialno','OTHER'),('id -u','2000')]:
                old=replies[cmd];replies[cmd]=value
                with self.assertRaises(RuntimeError): reset.identity()
                replies[cmd]=old
        with patch.object(reset, 'run', return_value=subprocess.CompletedProcess([],0,stdout='192.168.1.71:5555')):
            with self.assertRaises(RuntimeError): reset.identity()

    def test_twrp_failure_text_even_with_zero_exit_rejected(self):
        reset=m.Reset('TEST_USB',self.root)
        with patch.object(reset, 'shell', return_value='Unable to format /data'):
            with self.assertRaises(RuntimeError): reset.twrp('format data')

    def test_real_restore_rejects_bad_readback_and_never_marks_verified(self):
        reset=m.Reset('TEST_USB',self.root,report_dir=self.root/'reports')
        source=self.root/'system-original.img';source.write_bytes(b'reviewed image')
        reset.baseline['partitions']['system']={'bytes':source.stat().st_size,'sha256':m.digest(source)}
        reset.start_report()
        with patch.object(reset,'identity'), patch.object(reset,'node',return_value='/dev/block/mmcblk0p20'), patch.object(reset,'mounts',return_value=[]), patch.object(reset,'run') as run, patch.object(reset,'shell',return_value=''), patch.object(reset,'partition_hash',return_value='wrong'):
            with self.assertRaisesRegex(RuntimeError,'read-back'): reset.restore('system')
            self.assertEqual(run.call_args.args, ('exec-in','dd of=/dev/block/mmcblk0p20 bs=1048576'))
            self.assertNotIn('system',reset.report['verified'])

    def test_mounted_partition_stops_before_dd(self):
        reset=m.Reset('TEST_USB',self.root,report_dir=self.root/'reports')
        source=self.root/'system-original.img';source.write_bytes(b'reviewed image')
        reset.baseline['partitions']['system']={'bytes':source.stat().st_size,'sha256':m.digest(source)}
        with patch.object(reset,'identity'), patch.object(reset,'node',return_value='/dev/block/mmcblk0p20'), patch.object(reset,'mounts',return_value=['/system']), patch.object(reset,'shell',return_value=''), patch.object(reset,'run') as run:
            with self.assertRaisesRegex(RuntimeError,'still mounted'): reset.restore('system')
            run.assert_not_called()

    def test_remaining_files_rejected(self):
        reset=m.Reset('TEST_USB',self.root)
        with patch.object(reset, 'twrp'), patch.object(reset,'node',return_value='/dev/block/mmcblk0p1'), patch.object(reset,'mounts',return_value=['/data']), patch.object(reset,'shell',side_effect=['/data/media','','/data/media/0/download.apk']):
            with self.assertRaisesRegex(RuntimeError,'Files remain'): reset.verify_empty_data()


if __name__ == '__main__': unittest.main()
