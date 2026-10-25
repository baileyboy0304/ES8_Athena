#!/usr/bin/env python3
"""Restore the reviewed Athena baseline; default operation is read-only."""
from contextlib import contextmanager
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import threading
import time

HERE = Path(__file__).resolve().parent
BY_NAME = '/dev/block/platform/bootdevice/by-name/'
PARTITIONS = ('boot', 'recovery', 'system', 'vendor')
WRITABLE = ('system', 'vendor')


@contextmanager
def progress(label, interval=5):
    """Show elapsed time without implying that a quiet ADB command is advancing."""
    started = time.monotonic()
    stopped = threading.Event()

    def report():
        while not stopped.wait(interval):
            print(f'{label}: still waiting ({time.monotonic() - started:.0f}s elapsed)', flush=True)

    print(label + '...', flush=True)
    worker = threading.Thread(target=report, daemon=True)
    worker.start()
    try:
        yield
    except BaseException:
        print(f'{label}: stopped before completion', flush=True)
        raise
    else:
        print(f'{label}: completed ({time.monotonic() - started:.0f}s)', flush=True)
    finally:
        stopped.set()
        worker.join()


def digest(path):
    h = hashlib.sha256()
    total = path.stat().st_size
    done = 0
    last = time.monotonic()
    print(f'Checking image {path.name}: 0%', flush=True)
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(8 * 1024 * 1024), b''):
            h.update(chunk)
            done += len(chunk)
            now = time.monotonic()
            if now - last >= 2:
                print(f'Checking image {path.name}: {done * 100 / total:.0f}% '
                      f'({done / 1048576:.0f}/{total / 1048576:.0f} MiB)', flush=True)
                last = now
    print(f'Checking image {path.name}: 100%', flush=True)
    return h.hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


class Reset:
    def __init__(self, serial, backup_dir, adb='adb', report_dir=None):
        require(serial is None or bool(re.fullmatch(r'[A-Za-z0-9_-]+', serial)), 'Use a physical USB serial, not an IP address.')
        self.serial = serial
        self.backup_dir = Path(backup_dir).expanduser().resolve()
        self.adb = adb
        self.baseline = json.loads((HERE / 'baseline.json').read_text())
        self.report_dir = Path(report_dir or HERE / 'reports')
        self.report_path = None
        self.report = {'serial': serial, 'baseline': self.baseline['name'], 'status': 'not_started', 'verified': {}}

    def resolve_serial(self):
        if self.serial is not None:
            return
        # -d selects exactly one USB transport and rejects ambiguous connections.
        # Resolve once, then pin every check and write to that serial.
        result = subprocess.run([self.adb, '-d', 'get-serialno'],
                                text=True, capture_output=True)
        serial = result.stdout.strip()
        require(result.returncode == 0 and serial != 'unknown'
                and bool(re.fullmatch(r'[A-Za-z0-9_-]+', serial)),
                'Cannot select a single USB device. Connect exactly one authorised '
                'ES8, or specify --serial from adb devices -l. ' + result.stderr.strip())
        self.serial = serial
        self.report['serial'] = serial
        print('Selected USB device:', serial, flush=True)

    def run(self, *args, **kwargs):
        self.resolve_serial()
        return subprocess.run([self.adb, '-s', self.serial, *args], check=True, **kwargs)

    def shell(self, command):
        return self.run('shell', command, text=True, capture_output=True).stdout.strip()

    def check_files(self):
        for part in PARTITIONS:
            path = self.backup_dir / (part + '-original.img')
            expected = self.baseline['partitions'][part]
            require(path.is_file(), 'Missing image: ' + str(path))
            require(path.stat().st_size == expected['bytes'], 'Image size mismatch: ' + part)
            require(digest(path) == expected['sha256'], 'Image SHA256 mismatch: ' + part)
            print('Verified source image:', part, flush=True)

    def identity(self):
        # adb's transport path distinguishes USB from TCP even with a supplied serial.
        transport = self.run('get-devpath', text=True, capture_output=True).stdout.strip()
        require(transport.startswith('usb:'), 'Target must be connected by physical USB.')
        require(self.shell('getprop ro.serialno') == self.serial, 'Device serial property mismatch.')
        require(self.shell('getprop ro.product.device') == 'athena', 'Target is not an ES8 Gen 2 (athena).')
        require(self.shell('getprop ro.twrp.version') == self.baseline['twrp_version'],
                'Boot into the reviewed TWRP version first; the script never reboots automatically.')
        require(self.shell('id -u') == '0', 'Recovery ADB must run as root.')

    def node(self, part):
        require(part in (*PARTITIONS, 'userdata', 'cache'), 'Partition is not allowlisted.')
        node = self.shell('readlink -f ' + BY_NAME + part)
        require(bool(re.fullmatch(r'/dev/block/mmcblk[0-9]+p[0-9]+', node)), 'Unexpected partition node: ' + part)
        return node

    def partition_hash(self, part):
        node = self.node(part)
        with progress('Reading and hashing ' + part + ' on the ES8'):
            return self.shell('sha256sum ' + shlex.quote(node)).split()[0]

    def mounts(self, node):
        mounted = []
        for line in self.shell('cat /proc/mounts').splitlines():
            fields = line.split()
            if len(fields) < 2 or not fields[0].startswith('/dev/block/'):
                continue
            if self.shell('readlink -f ' + shlex.quote(fields[0])) == node:
                mounted.append(fields[1])
        return mounted

    def check_device(self):
        self.identity()
        nodes = [self.node(p) for p in (*PARTITIONS, 'userdata', 'cache')]
        require(len(nodes) == len(set(nodes)), 'Partition aliases overlap; refusing to write.')
        for part in PARTITIONS:
            size = int(self.shell('blockdev --getsize64 ' + shlex.quote(self.node(part))))
            require(size == self.baseline['partitions'][part]['bytes'], 'Partition size mismatch: ' + part)
        self.check_preserved()

    def check_preserved(self):
        for part in ('boot', 'recovery'):
            actual = self.partition_hash(part)
            require(actual == self.baseline['partitions'][part]['sha256'],
                    part + ' differs from the reviewed unlocked/TWRP baseline; stopping without replacing it.')
            self.report['verified'][part] = actual

    def save(self):
        require(self.report_path is not None, 'Report has not been opened.')
        self.report_path.write_text(json.dumps(self.report, indent=2) + '\n')

    def start_report(self):
        self.report_dir.mkdir(parents=True, exist_ok=True)
        stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        self.report_path = self.report_dir / ('reset-' + stamp + '.json')
        fd = os.open(self.report_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        os.close(fd)
        self.save()  # Fail before touching partitions if the report cannot be written.

    def restore(self, part):
        require(part in WRITABLE, 'Only system and vendor may be restored.')
        self.identity()
        source = self.backup_dir / (part + '-original.img')
        expected = self.baseline['partitions'][part]
        require(source.stat().st_size == expected['bytes'] and digest(source) == expected['sha256'],
                'Source image changed after preflight: ' + part)
        node = self.node(part)
        for mount in self.mounts(node):
            self.shell('umount ' + shlex.quote(mount))
        require(not self.mounts(node), part + ' is still mounted.')
        self.report['status'] = 'writing_' + part
        self.save()
        print('Restoring', part, '(boot/recovery are never written)', flush=True)
        with progress(f'Transferring {part} ({expected["bytes"] / 1048576:.0f} MiB) over USB'):
            with source.open('rb') as stream:
                self.run('exec-in', 'dd of=' + shlex.quote(node) + ' bs=1048576', stdin=stream)
        with progress('Flushing writes on the ES8'):
            self.shell('sync')
        actual = self.partition_hash(part)
        require(actual == expected['sha256'], part + ' read-back SHA256 mismatch. Remain in TWRP.')
        self.report['verified'][part] = actual
        self.report['status'] = 'verified_' + part
        self.save()

    def twrp(self, command):
        with progress('TWRP ' + command):
            output = self.shell('twrp ' + command)
        print(output, flush=True)
        require(not re.search(r'(?im)(\bfailed\b|\bfailure\b|\berror\b|\bunable\b|^E:)', output),
                'TWRP reported a problem during ' + command + '; inspect recovery before continuing.')

    def verify_empty_data(self):
        self.twrp('mount data')
        require('/data' in self.mounts(self.node('userdata')), 'Cannot verify the formatted data partition is mounted.')
        entries = self.shell('find /data -mindepth 1 -maxdepth 1').splitlines()
        require(set(entries) <= {'/data/lost+found', '/data/media', '/data/.layout_version'},
                'Unexpected entries remain in /data; reset is not verified.')
        # TWRP may recreate its own preferences; no application or user files may remain.
        require(not self.shell('find /data -type l'), 'Symlinks remain in /data; reset is not verified.')
        files = self.shell('find /data -type f').splitlines()
        allowed = {'/data/.layout_version', '/data/media/TWRP/.twrps', '/data/media/0/TWRP/.twrps'}
        require(set(files) <= allowed, 'Files remain in /data; reset is not verified.')

    def verify_empty_cache(self):
        self.twrp('mount cache')
        require('/cache' in self.mounts(self.node('cache')), 'Cannot verify the cache partition is mounted.')
        entries = self.shell('find /cache -mindepth 1 -maxdepth 1').splitlines()
        require(set(entries) <= {'/cache/lost+found', '/cache/recovery'},
                'Unexpected entries remain in /cache; reset is not verified.')

    def apply(self, confirm=input):
        # Recheck all inputs here too, so calling apply directly cannot bypass preflight.
        self.check_files()
        self.check_device()
        print('\nERASE ' + self.serial + ': restore stock system/vendor; format ALL userdata/internal storage and cache.')
        print('This removes Echo Dot Assist, VACAV, downloaded APKs, logins, Wi-Fi and local files. Stock firmware apps remain.')
        print('Bootloader/unlock partitions, boot and TWRP recovery are preserved. HA is not modified.')
        phrase = 'ERASE'
        require(confirm('Type exactly "' + phrase + '" to proceed: ').strip() == phrase, 'Confirmation did not match; no writes performed.')
        self.check_device()
        self.start_report()
        try:
            for part in WRITABLE:
                self.restore(part)
            self.check_preserved()
            self.identity()
            self.report['status'] = 'formatting_data'
            self.save()
            self.twrp('format data')
            self.verify_empty_data()
            self.report['status'] = 'wiping_cache'
            self.save()
            self.twrp('wipe cache')
            self.verify_empty_cache()
            self.shell('sync')
            self.check_preserved()
            self.report['status'] = 'complete_left_in_twrp'
            self.report['userdata_erased'] = True
            self.save()
            print('Reset verified. Left in TWRP; no reboot or root installation. Report:', self.report_path)
        except BaseException as exc:
            self.report['failed_stage'] = self.report['status']
            self.report['status'] = 'failed_remain_in_twrp'
            self.report['error'] = str(exc)
            self.save()
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--serial', help='Physical USB serial; omitted: select the single connected USB device')
    parser.add_argument('--backup-dir', type=Path, required=True, help='Directory containing the four reviewed *-original.img files')
    parser.add_argument('--adb', default='adb', help='ADB executable')
    parser.add_argument('--report-dir', type=Path, help='Private reset report directory')
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--check-files', action='store_true', help='Verify local images only; do not contact the device')
    modes.add_argument('--apply', action='store_true', help='Perform reset after preflight and typed confirmation')
    args = parser.parse_args()
    reset = Reset(args.serial, args.backup_dir, args.adb, args.report_dir)
    if args.apply:
        require(sys.stdin.isatty(), '--apply requires an interactive terminal; no unattended confirmation.')
        reset.apply()
    else:
        reset.check_files()
        if not args.check_files:
            reset.check_device()
        print('Read-only checks passed. No device writes, format or reboot performed.')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, ValueError, subprocess.CalledProcessError) as exc:
        print('STOP:', exc, file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print('Interrupted. If writing had started, remain in TWRP and inspect the reset report.', file=sys.stderr)
        sys.exit(130)
