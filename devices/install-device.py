#!/usr/bin/env python3
"""Install VACAV and selected apps over USB after the normal EDA installer."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from install import ROOT, PACKAGE, ACTIVITY, profile, settings, build, yes, save, stamp, verify

def resolve_serial(serial):
    if serial is None:
        try:
            # ADB -d selects USB only and refuses zero/multiple USB devices.
            # Resolve once, then pin every later command to that same serial.
            serial = subprocess.check_output(
                ['adb', '-d', 'get-serialno'], stderr=subprocess.STDOUT, timeout=15
            ).decode().strip()
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            raise RuntimeError('Could not select one USB ADB device. Connect and authorise one device, '
                               'or use --serial YOUR_USB_SERIAL when several are connected. '
                               'Run adb devices -l to check.') from None
    if not serial or serial == 'unknown' or not re.fullmatch(r'[A-Za-z0-9_-]+', serial):
        raise ValueError('Provide a valid USB serial, not network ADB')
    return serial

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--serial', help='USB ADB serial; optional with exactly one USB device connected')
    parser.add_argument('--profile', choices=['es8-gen2', 'portal_plus_gen_2'], default='es8-gen2')
    parser.add_argument('--apply', action='store_true', help='Install after review; otherwise inspect only')
    parser.add_argument('--export-apps', action='store_true', help='Export streaming APKs to private installation-data/apks before wiping')
    a = parser.parse_args()
    a.serial = resolve_serial(a.serial)
    def adb(*args):
        return subprocess.check_output(['adb', '-s', a.serial, *args], stderr=subprocess.STDOUT, timeout=240).decode().strip()
    def shell(command):
        return adb('shell', command)
    def package_paths(package):
        return shell('pm path ' + package + ' 2>/dev/null || true')
    model = shell('getprop ro.product.device')
    firmware = shell('getprop ro.build.display.id')
    if a.profile == 'es8-gen2' and (model != 'athena' or firmware != 'PS75741.7080N'):
        raise RuntimeError('Expected athena on PS75741.7080N; no changes made')
    if a.profile == 'portal_plus_gen_2' and model == 'athena':
        raise RuntimeError('Portal profile cannot provision Athena')
    print('USB target:', a.serial, model, firmware)
    p = profile(a.profile)
    if a.export_apps:
        results = []
        for service in p['services']:
            paths = [line.removeprefix('package:') for line in package_paths(service['package']).splitlines() if line.startswith('package:')]
            folder = ROOT / 'installation-data/apks' / a.profile / service['id']
            if folder.exists():
                raise RuntimeError('Export already exists; preserve it or move it before exporting: ' + str(folder))
            folder.mkdir(parents=True)
            for i, remote in enumerate(paths):
                if not re.fullmatch(r'/[A-Za-z0-9_./=+~-]+\.apk', remote):
                    raise RuntimeError('Unexpected package path')
                dest = folder / f'{i:02d}.apk'
                adb('pull', remote, str(dest))
                digest = hashlib.sha256(dest.read_bytes()).hexdigest()
                if shell('sha256sum ' + remote).split()[0] != digest:
                    raise RuntimeError('APK export hash mismatch')
                results.append(dict(service=service['id'], package=service['package'], file=str(dest.relative_to(ROOT)), sha256=digest))
            print(service['name'] + ':', len(paths), 'APK(s) exported')
        save(ROOT / 'installation-data' / (a.profile + '-apps.json'), results)
        return
    verify()
    cfg = build(a.profile)
    selected = [s for s in p['services'] if s['id'] in cfg['services']]
    package_dir = ROOT / 'VACAV/integration/custom_components/vaca_vision/packages'
    apk = package_dir / 'vision-standard.apk' if a.profile == 'es8-gen2' else ROOT / 'VACAV/payloads/portal_plus_gen_2.apk'
    if a.profile == 'es8-gen2':
        if shell('id -u') != '0':
            raise RuntimeError('Run EDA setup first: root USB ADB is required')
        if shell('test -f /system/hassmic/boot.sh && echo yes || true') != 'yes':
            raise RuntimeError('echo-dot-assist system installation not found; run ./echo-dot-assist/scripts/setup.sh athena first')
    print('VACAV APK:', apk.name)
    print('Streaming:', ', '.join(s['name'] for s in selected) or 'none')
    missing = []
    for service in selected:
        if not package_paths(service['package']).startswith('package:'):
            files = list((ROOT / 'installation-data/apks' / a.profile / service['id']).glob('*.apk'))
            if not files: missing.append(service['id'])
    if missing:
        raise RuntimeError('Missing app(s): ' + ', '.join(missing) + '. Put their lawful APK/splits in installation-data/apks/PROFILE/SERVICE/ or export before wiping.')
    if not a.apply:
        print('Inspection complete. Repeat with --apply when ready; no device changes made.')
        return
    if not yes('Install VACAV, selected apps, and the selected streaming policy on this USB device?'):
        return
    backup = ROOT / 'installation-data/backups' / ('device-' + stamp())
    backup.mkdir(parents=True)
    # Save current permissions/settings for targeted rollback, without app data or sign-in tokens.
    old = {k: shell(command) for k, command in {
        'home': 'cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME',
        'accessibility_services': 'settings get secure enabled_accessibility_services',
        'accessibility_enabled': 'settings get secure accessibility_enabled',
        'vacav_appops': 'appops get ' + PACKAGE + ' 2>/dev/null || true'}.items()}
    save(backup / 'before.json', old)
    result = adb('install', '-r', str(apk))
    if 'Success' not in result: raise RuntimeError('VACAV APK installation failed: ' + result)
    for service in selected:
        if package_paths(service['package']).startswith('package:'): continue
        files = sorted((ROOT / 'installation-data/apks' / a.profile / service['id']).glob('*.apk'))
        result = adb('install-multiple' if len(files) > 1 else 'install', '-r', *map(str, files))
        if 'Success' not in result: raise RuntimeError('App installation failed: ' + result)
        if not package_paths(service['package']).startswith('package:'):
            raise RuntimeError('APK did not install the expected package: ' + service['package'])
    shell('appops set ' + PACKAGE + ' WRITE_SETTINGS allow')
    if a.profile == 'es8-gen2':
        from devices.streaming import configure
        configure(adb, shell, cfg, backup)
        shell('appops set ' + PACKAGE + ' SYSTEM_ALERT_WINDOW allow')
        print('Floating Home/Keep on/Brightness controls need DUMP to identify active playback windows.')
        print('The app reads bounded window/media-session status; it does not save screen contents.')
        if yes('Enable floating streaming controls (grant DUMP)?'):
            shell('pm grant ' + PACKAGE + ' android.permission.DUMP')
        if 'itvx' in cfg['services'] and yes('Enable VACAV’s exact ITVX Google-services-warning helper?'):
            component = PACKAGE + '/com.msp1974.vacompanion.utils.ItvxWarningService'
            current = shell('settings get secure enabled_accessibility_services')
            entries = [] if current in ('null', '') else current.split(':')
            if component not in entries: entries.append(component)
            joined = ':'.join(entries)
            if not re.fullmatch(r'[A-Za-z0-9_./:$]+', joined): raise RuntimeError('Unexpected accessibility service value')
            shell('settings put secure enabled_accessibility_services ' + joined)
            shell('settings put secure accessibility_enabled 1')
        shell('cmd package set-home-activity ' + ACTIVITY)
    shell('am start -n ' + ACTIVITY)
    print('Installed. Backup:', backup, '\nFinish VACAV sign-in and HA/VA pairing using README.md steps 6–8.\nChoose a Device name in the HA VACAV setup form (for example Kitchen Athena).')

if __name__ == '__main__':
    try: main()
    except subprocess.CalledProcessError as error:
        output = error.output or b''
        if isinstance(output, bytes):
            output = output.decode(errors='replace')
        sys.exit(str(error) + ('\n' + output.strip() if output else ''))
    except (RuntimeError, ValueError, OSError) as error:
        sys.exit(str(error))
