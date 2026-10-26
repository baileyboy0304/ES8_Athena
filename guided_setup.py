#!/usr/bin/env python3
"""Guided, resumable ES8 companion setup; never runs the unlock or wipes data."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import socket
from zoneinfo import ZoneInfo
import install as core

PROFILE = 'es8-gen2'


def snapshot(ha):
    return ({s['entity_id']: s for s in ha.call('get_states')},
            {e['entity_id']: e for e in ha.call('config/entity_registry/list')})


def available(states, entity):
    return states.get(entity, {}).get('state') not in (None, 'unknown', 'unavailable')


def va_sensors(states, registry):
    return sorted(e for e, r in registry.items() if r.get('platform') == 'view_assist'
                  and e.startswith('sensor.') and available(states, e))


def select(label, options):
    if not options:
        raise ValueError('No available ' + label + '. Complete its HA setup first.')
    print('\n' + label)
    for i, item in enumerate(options, 1):
        print(f'  {i}. {item}')
    while True:
        value = core.ask('Select number', '1' if len(options) == 1 else '')
        if value.isdigit() and 1 <= int(value) <= len(options):
            return options[int(value) - 1]
        print('Choose one of the listed numbers.')


def inherited_settings(config, states, registry, reference):
    if reference not in va_sensors(states, registry):
        raise ValueError('Choose an operational View Assist sensor.')
    weather = states[reference].get('attributes', {}).get('weather_entity')
    if not isinstance(weather, str) or not weather.startswith('weather.') or not available(states, weather):
        raise ValueError('Configure a working weather entity on that View Assist device first.')
    zone = config['time_zone']
    ZoneInfo(zone)
    return weather, zone


def validate_ready(states, registry, entity, cfg):
    """Block dashboard deployment on stale IDs, proxies and mismatched devices."""
    errors = []
    if entity not in va_sensors(states, registry):
        return ['Select an available View Assist sensor for this Echo Show.']
    attrs = states[entity].get('attributes', {})
    mic = attrs.get('mic_device', '')
    # VA versions store either the Assist entity ID or its HA device-registry ID.
    candidates = ([mic] if mic.startswith('assist_satellite.') else
                  [e for e, r in registry.items() if e.startswith('assist_satellite.')
                   and r.get('device_id') == mic])
    candidates = [e for e in candidates if registry.get(e, {}).get('platform') == 'vaca_vision'
                  and available(states, e)]
    mic_record = registry[candidates[0]] if len(candidates) == 1 else {}
    if not mic_record:
        errors.append('View Assist microphone must be an available VACAVision Assist satellite.')
    display = attrs.get('display_device', '')
    display_records = [registry[e] for e, s in states.items()
                       if display and s.get('state') == display and e in registry
                       and registry[e].get('platform') == 'vaca_vision']
    if (not display.startswith('va-') or not mic_record.get('device_id') or not any(
            r.get('device_id') == mic_record['device_id'] for r in display_records)):
        errors.append('Display ID and microphone must belong to the same VACAVision device; sign in on the ES8.')
    for key in ('mediaplayer_device', 'musicplayer_device'):
        try:
            core.validate_music_entity(states, registry, attrs.get(key, ''))
        except ValueError as error:
            errors.append(f'{key}: {error}')
    if attrs.get('mediaplayer_device') != attrs.get('musicplayer_device'):
        errors.append('Use the same physical Music Assistant player for alerts and music.')
    music = states.get(attrs.get('musicplayer_device'), {}).get('attributes', {})
    if music.get('mass_player_type') in ('group', 'stereo_pair'):
        errors.append('Select the physical Music Assistant player, not a sync group.')
    weather = attrs.get('weather_entity', '')
    if not weather.startswith('weather.') or not available(states, weather):
        errors.append('Set an available weather entity in this View Assist device’s options.')
    expected = '/' + cfg['va_slug'] + '/clock'
    if attrs.get('home_screen') != expected:
        errors.append('Set this View Assist device’s Home/default view to ' + expected)
    return errors


def usb(serial, *args):
    return subprocess.check_output(['adb', '-s', serial, *args], text=True, timeout=240).strip()


def resolve_usb():
    serial = subprocess.check_output(['adb', '-d', 'get-serialno'], text=True, timeout=15).strip()
    if not re.fullmatch(r'[A-Za-z0-9_-]+', serial) or serial == 'unknown':
        raise ValueError('Connect exactly one authorised USB Echo Show.')
    if usb(serial, 'shell', 'getprop ro.product.device') != 'athena':
        raise ValueError('The connected USB device is not an Echo Show 8 Gen 2.')
    return serial


def wait_for_app(serial, timeout=180):
    """Bounded read-only wait after reboot; never send commands to another USB device."""
    deadline = time.monotonic() + timeout
    print('Waiting for the Echo Show to boot, join Wi-Fi and start VACAVision. Allow any on-screen permissions.')
    while time.monotonic() < deadline:
        try:
            boot = subprocess.check_output(['adb', '-s', serial, 'shell', 'getprop sys.boot_completed'],
                                           text=True, timeout=5).strip()
            if boot == '1':
                output = subprocess.check_output(['adb', '-s', serial, 'shell', 'ifconfig wlan0'],
                                                 text=True, timeout=5)
                match = re.search(r'inet (?:addr:)?(\d+\.\d+\.\d+\.\d+)', output)
                if match:
                    with socket.create_connection((match[1], 26900), timeout=3):
                        print('VACAVision is listening at ' + match[1] + ':26900')
                        return
        except (OSError, subprocess.SubprocessError):
            pass
        print('Still waiting for boot / Wi-Fi / VACAVision...', flush=True)
        time.sleep(5)
    raise ValueError('Timed out waiting for VACAVision. Check power, USB, Wi-Fi and the ES8 permission dialogs, then resume.')


def music_panel(ha):
    panels = ha.call('get_panels')
    matches = ['/' + path for path in panels
               if path == 'music-assistant' or path.endswith('_music_assistant')]
    if len(matches) == 1:
        print('Music Assistant sidebar:', matches[0])
        return matches[0]
    return core.ask('Open Music Assistant from the HA sidebar and copy the URL path after host/port')


def gather_apks(serial, cfg):
    for service in core.profile(PROFILE)['services']:
        if service['id'] not in cfg['services']:
            continue
        if usb(serial, 'shell', 'pm path ' + service['package'] + ' 2>/dev/null || true').startswith('package:'):
            continue
        folder = core.ROOT / 'installation-data/apks' / PROFILE / service['id']
        while not list(folder.glob('*.apk')):
            print(f"\n{service['name']} needs your compatible APK files (all splits if applicable).")
            print('See devices/APK-VERSIONS.md. Proprietary apps are not downloaded automatically.')
            source = Path(core.ask('Folder containing its APK files; Ctrl+C to stop')).expanduser()
            files = sorted(source.glob('*.apk')) if source.is_dir() else []
            if not files:
                print('No APK files found. Try again.'); continue
            folder.mkdir(parents=True, exist_ok=True)
            for apk in files:
                shutil.copy2(apk, folder / apk.name)


def prepare_connection(ha, cfg, serial):
    """Save choices in VACAV through HA's authenticated setup API."""
    output = usb(serial, 'shell', 'ifconfig', 'wlan0')
    match = re.search(r'inet (?:addr:)?(\d+\.\d+\.\d+\.\d+)', output)
    if not match:
        raise ValueError('Echo Show has no Wi-Fi address yet. Connect it to Wi-Fi and retry.')
    # The public Sendspin identity links MA universal players even when MA omits IP/MAC.
    # Filter on the device so no pairing token or private key enters installer output.
    identity = ''
    try:
        lines = usb(serial, 'shell', "grep 'sendspin: player ' /data/local/hassmic/boot.log 2>/dev/null || true")
        found = re.findall(r'sendspin: player ([A-Za-z0-9_-]{43}) on ', lines)
        if found:
            identity = found[-1]
    except subprocess.SubprocessError:
        pass  # Named-player selection remains available if the log has rotated.
    start = ha.post('config/config_entries/flow', {
        'handler': 'vaca_vision', 'show_advanced_options': False})
    flow_id = start.get('flow_id')
    finished = start.get('type') in ('abort', 'create_entry')
    try:
        if not flow_id or start.get('type') != 'menu' or 'manual' not in start.get('menu_options', []):
            raise ValueError('VACAVision connection setup is unavailable.')
        path = 'config/config_entries/flow/' + flow_id
        form = ha.post(path, {'next_step_id': 'manual'})
        if form.get('type') != 'form' or form.get('step_id') != 'manual':
            raise ValueError('VACAVision did not offer its connection form.')
        result = ha.post(path, {'prepare_only': True, 'host': match[1], 'port': 26900,
            'name': cfg['device_name'], 'dashboard': '/' + cfg['home_slug'] + '/home',
            'sendspin_client_id': identity})
        finished = result.get('type') in ('abort', 'create_entry')
        if (result.get('type') != 'abort' or result.get('reason') != 'setup_prepared'
                or result.get('description_placeholders', {}).get('setup_protocol') != '2'):
            reason = result.get('reason', result.get('type', 'unknown'))
            if reason == 'setup_prepare_failed':
                raise ValueError('VACAVision is not reachable yet at ' + match[1] + ':26900. Wait for app startup, allow its on-screen permissions, and retry.')
            raise ValueError('VACAVision setup returned ' + str(reason) + '. Check the HACS integration version and restart HA after updating it.')
    finally:
        if flow_id and not finished:
            ha.delete('config/config_entries/flow/' + flow_id)
    print('Saved device name and dashboard in HA for', match[1])


def write_handoff(serial, cfg):
    """Only non-secret, allowlisted choices cross USB into the app's private files."""
    plan = {"version": 1, "name": cfg['device_name'], "services": cfg['services'],
            **{k: cfg[k] for k in ('home_slug', 'va_slug', 'tv_slug')}}
    lines = usb(serial, 'shell', "grep 'sendspin: player ' /data/local/hassmic/boot.log 2>/dev/null || true")
    found = re.findall(r'sendspin: player ([A-Za-z0-9_-]{43}) on ', lines)
    plan['sendspin_client_id'] = found[-1] if found else ''
    path = core.ROOT / 'installation-data/es8-install.json'
    core.save(path, plan)
    owner = usb(serial, 'shell', 'stat -c %u /data/data/com.mph1970.vacavision')
    if not owner.isdigit(): raise ValueError('Cannot identify the VACAV app owner.')
    target = '/data/data/com.mph1970.vacavision/files/es8-install.json'
    usb(serial, 'push', str(path), '/data/local/tmp/vacav-install.json')
    usb(serial, 'shell', 'mkdir -p /data/data/com.mph1970.vacavision/files && '
        'chown ' + owner + ':' + owner + ' /data/data/com.mph1970.vacavision/files && '
        'cp /data/local/tmp/vacav-install.json ' + target + ' && chown ' + owner + ':' + owner + ' ' + target +
        ' && chmod 600 ' + target + ' && restorecon ' + target + ' && rm /data/local/tmp/vacav-install.json')
    actual = json.loads(usb(serial, 'shell', 'cat ' + target))
    if actual != plan: raise ValueError('USB setup choices failed read-back verification.')
    print('Saved non-secret setup choices on the Echo Show.')


def run(check_only=False):
    core.verify()
    if check_only:
        print('Open your VACAVision device in HA: Configure → Install example dashboards → Open the dashboard installer. Select Refresh connections.')
        return True
    serial = resolve_usb()
    print('USB target:', serial)
    choice_file = core.ROOT / 'installation-data/choices/es8-gen2.json'
    progress_file = core.ROOT / 'installation-data/guided-progress.json'
    if choice_file.exists() and core.yes('Resume using saved installation choices?'):
        cfg = core.settings(PROFILE)
    else:
        p = core.profile(PROFILE)
        services = [s['id'] for s in p['services'] if core.yes('Install/use ' + s['name'] + '?')]
        cfg = dict(profile=PROFILE, services=services, va_entity='sensor.es8_setup',
                   weather_entity='weather.home', music_path='/music-assistant')
        cfg['device_name'] = core.ask('Device name')
        slug = re.sub(r'[^a-z0-9]+', '-', cfg['device_name'].lower()).strip('-') or 'echo-show'
        cfg.update(home_slug=slug+'-home', va_slug='view-assist-'+slug, tv_slug=slug+'-tv')
    if not cfg.get('device_name'):
        cfg['device_name'] = core.ask('Device name')
    if not 1 <= len(cfg['device_name']) <= 80:
        raise ValueError('Enter a device name between 1 and 80 characters.')
    # HA supplies timezone when the display connects; never assume the PC's zone.
    cfg.pop('timezone', None)
    core.save(choice_file, cfg)
    core.build(PROFILE)
    gather_apks(serial, cfg)
    command = [sys.executable, str(core.ROOT / 'devices/install-device.py'), '--profile', PROFILE, '--serial', serial]
    subprocess.run(command, check=True)
    fingerprint = hashlib.sha256(json.dumps({'services': cfg['services'], 'app': 19}, sort_keys=True).encode()).hexdigest()
    previous = core.read(progress_file) if progress_file.exists() else {}
    completed = previous.get('serial') == serial and previous.get('usb_choices') == fingerprint
    if not (completed and core.yes('USB installation previously completed. Keep it and continue to HA?')):
        subprocess.run(command + ['--apply'], check=True)
        core.save(progress_file, {'serial': serial, 'usb_choices': fingerprint})
    write_handoff(serial, cfg)
    if core.yes('Reboot this Echo Show now?'):
        usb(serial, 'reboot')
        wait_for_app(serial)
    print("""
Linux installation finished. Continue with README steps 2–6:
1. On the Echo Show, allow the app's on-screen permissions after it starts.
2. In HA, add the discovered VACA_Vision device and confirm its name.
3. Complete its voice-assistant setup and select the Assist pipeline.
4. Sign into HA on the Echo Show.
5. Create this device in View Assist using the README field-by-field settings.
6. For example dashboards: VACAVision → your device → Configure → Install example dashboards.
7. Test voice and music on this Echo. Sign into streaming services and test playback.
""")
    print('Device name:', cfg['device_name'])
    print('Example dashboard paths:')
    print('  Dashboard: /'+cfg['va_slug'])
    for label, view in [('Home','clock'),('Music','music'),('Intent','intent'),('List','list')]:
        print('  '+label+': /'+cfg['va_slug']+'/'+view)
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-ha', action='store_true', help='Print where to run the HA connection checks')
    args = parser.parse_args()
    try:
        sys.exit(0 if run(args.check_ha) else 1)
    except (KeyboardInterrupt, EOFError):
        print('\nStopped. Run ./vacav_setup.sh again to resume.'); sys.exit(1)
    except Exception as error:
        print('Stopped:', error, '\nCorrect the problem and run ./vacav_setup.sh again.'); sys.exit(1)
