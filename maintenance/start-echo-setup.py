#!/usr/bin/env python3
"""Bridge the reviewed post-reset TWRP state to the unchanged upstream installer."""
import hashlib
import importlib.util
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / 'echo-dot-assist'


def main():
    if len(sys.argv) > 1:
        raise ValueError('Run ./echo_setup.sh without arguments. It detects the single USB device.')
    serial = subprocess.check_output(['adb', '-d', 'get-serialno'], text=True).strip()
    if serial == 'unknown' or not re.fullmatch(r'[A-Za-z0-9_-]+', serial):
        raise ValueError('Connect exactly one USB Echo Show.')
    def adb(*args):
        return subprocess.check_output(['adb', '-s', serial, *args], text=True, timeout=240).strip()
    if not adb('get-devpath').startswith('usb:') or adb('shell', 'getprop ro.product.device') != 'athena':
        raise ValueError('This wrapper supports only the USB Echo Show 8 Gen 2 (athena).')
    recovery = adb('shell', 'getprop ro.twrp.version')
    restart = False
    if recovery:
        if recovery != '3.7.0_9-0' or adb('shell', 'id -u') != '0':
            raise ValueError('Use the reviewed TWRP 3.7.0_9-0 recovery.')
        # This wrapper is for our reset baseline, not an arbitrary Athena firmware.
        spec = importlib.util.spec_from_file_location('reset_es8', ROOT/'reset-es8/reset_es8.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        baseline = module.Reset(serial, None)  # Device-only inspection; no recovery images are read.
        print('Checking boot, recovery, system and vendor over USB; this can take several minutes.', flush=True)
        baseline.check_device()
        for part in ('system', 'vendor'):
            if baseline.partition_hash(part) != baseline.baseline['partitions'][part]['sha256']:
                raise ValueError('This is not the reviewed post-reset baseline. Follow the upstream Athena guide for this firmware.')
        source = UPSTREAM / 'firmware/athena/boot-root.zip'
        setup = (UPSTREAM / 'devices/athena/setup.sh').read_text()
        expected = re.search(r'^BOOTROOT_SHA256=([a-f0-9]{64})$', setup, re.M)[1]
        if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest() != expected:
            raise ValueError('Place the upstream guide’s verified boot-root.zip in echo-dot-assist/firmware/athena/.')
        print('Already unlocked in TWRP: no unlocker ZIP is needed. USB target:', serial)
        if input('Install the verified root ZIP and reboot, then start Echo Dot Assist setup? [y/N]: ').strip().lower() not in ('y','yes'):
            return
        adb('push', str(source), '/tmp/boot-root.zip')
        output = adb('shell', 'twrp install /tmp/boot-root.zip')
        print(output)
        if re.search(r'(?im)(\bfailed\b|\bfailure\b|\berror\b|\bunable\b|^E:)', output):
            raise ValueError('TWRP reported a root-install problem. Remain in recovery and inspect it.')
        adb('shell', 'rm /tmp/boot-root.zip')
        adb('reboot')
        deadline = time.monotonic() + 180
        while time.monotonic() < deadline:
            try:
                if (adb('shell','getprop sys.boot_completed') == '1' and
                        adb('shell','id -u') == '0' and adb('shell','getprop ro.build.display.id') == 'PS75741.7080N'):
                    restart = True
                    break
            except subprocess.SubprocessError:
                pass
            print('Waiting for rooted Fire OS to start...', flush=True)
            time.sleep(5)
        if not restart:
            raise ValueError('Rooted PS75741.7080N did not become ready; inspect the Echo before continuing.')
    env = dict(os.environ, ANDROID_SERIAL=serial)
    args = [str(UPSTREAM / 'scripts/setup.sh'), 'athena'] + (['--restart'] if restart else [])
    os.execve(args[0], args, env)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print('Stopped:', exc, file=sys.stderr)
        sys.exit(1)
