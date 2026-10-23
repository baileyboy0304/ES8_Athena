"""USB selection and public CLI dispatch checks; no real ADB/device access."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('device_installer', ROOT / 'devices/install-device.py')
device = importlib.util.module_from_spec(spec)
spec.loader.exec_module(device)
import install


class UsbSelection(unittest.TestCase):
    def test_single_usb_is_resolved_without_network_fallback(self):
        with patch.object(device.subprocess, 'check_output', return_value=b'TEST_USB\n') as adb:
            self.assertEqual(device.resolve_serial(None), 'TEST_USB')
            self.assertEqual(adb.call_args.args[0], ['adb', '-d', 'get-serialno'])

    def test_no_or_multiple_usb_devices_stop(self):
        for message in (b'error: no devices found', b'error: more than one device'):
            with self.subTest(message=message), patch.object(
                device.subprocess, 'check_output',
                side_effect=subprocess.CalledProcessError(1, ['adb'], output=message)
            ):
                with self.assertRaisesRegex(RuntimeError, '--serial'):
                    device.resolve_serial(None)

    def test_explicit_serial_is_preserved_and_network_address_rejected(self):
        with patch.object(device.subprocess, 'check_output') as adb:
            self.assertEqual(device.resolve_serial('TEST_USB'), 'TEST_USB')
            with self.assertRaises(ValueError):
                device.resolve_serial('192.0.2.1:5555')
            adb.assert_not_called()

    def test_public_entry_point_allows_omitted_serial_and_forwards_override(self):
        for extra in ([], ['--serial', 'TEST_USB']):
            with self.subTest(extra=extra), patch.object(
                sys, 'argv', ['install.py', 'device', '--apply', *extra]
            ), patch.object(install.subprocess, 'run') as run:
                install.main()
                command = run.call_args.args[0]
                self.assertEqual(Path(command[2]), ROOT / 'devices/install-device.py')
                self.assertEqual('--serial' in command, bool(extra))
                if extra:
                    self.assertEqual(command[command.index('--serial') + 1], 'TEST_USB')


if __name__ == '__main__':
    unittest.main()
