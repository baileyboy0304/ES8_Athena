#!/usr/bin/env python3
"""Guided, resumable ES8 companion setup; never runs the unlock or wipes data."""
import argparse
import getpass
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
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


def handoff(cfg):
    print(f'''
GO TO HOME ASSISTANT NOW
1. Restart HA if integration files were just installed. Add/configure VACA_Vision:
   role ES8 with upstream Echo Dot Assist (standard_upstream_eda), this ES8's IP,
   app port 26900, voice port 26053, your device name and Assist pipeline.
   Reuse an existing encryption key if present; otherwise leave it blank.
   Do not create a second ESPHome voice owner for this ES8.
2. Set startup dashboard /{cfg['home_slug']}/home. Sign into HA ON THE ES8.
3. In Music Assistant, pair Echo Dot Assist's Sendspin player using the upstream
   setup token if not already paired. Enable Expose player to Home Assistant.
   In VACAVision options choose the MA integration and MA player ID.
4. In your EXISTING View Assist installation, add/configure this ES8 device:
   display = VACAVision display sensor VALUE (va-...), microphone = its Assist
   satellite, alerts AND music = official MA physical-player entity, not proxy.
   Set weather through VA, Use announce on, ducking zero, native voice indicator.
   Dashboard: /{cfg['va_slug']}    Home: /{cfg['va_slug']}/clock
   If the VA picker excludes VACAVision, README explains the optional helper.
5. Verify a spoken reply and music playback come from THIS Echo Show.
Return here when ready. The next stage checks HA before offering dashboards.
''')


def run(check_only=False):
    core.verify()
    url = core.ask('Home Assistant base URL')
    token = getpass.getpass('HA administrator long-lived token (not saved): ')
    ha = core.HA(url, token)
    try:
        states, registry = snapshot(ha)
        config = ha.call('get_config')
        if 'view_assist' not in config.get('components', []):
            raise ValueError('View Assist must already be installed and operational in HA.')
        choice_file = core.ROOT / 'installation-data/choices/es8-gen2.json'
        progress_file = core.ROOT / 'installation-data/guided-progress.json'
        if check_only:
            cfg = core.settings(PROFILE)
        else:
            serial = resolve_usb()
            print('USB target:', serial)
            if choice_file.exists() and core.yes('Resume using saved installation choices?'):
                cfg = core.settings(PROFILE)
                ZoneInfo(config['time_zone'])
                cfg['timezone'] = config['time_zone']
            else:
                reference = select('Existing View Assist device to inherit weather from', va_sensors(states, registry))
                weather, zone = inherited_settings(config, states, registry, reference)
                p = core.profile(PROFILE)
                print('Weather from View Assist:', weather, '| Timezone from HA:', zone)
                print('Streaming is optional; VACAVision web access is always included.')
                services = [s['id'] for s in p['services'] if core.yes('Install/use ' + s['name'] + '?')]
                cfg = dict(profile=PROFILE, services=services, va_entity='sensor.es8_setup',
                           weather_entity=weather, timezone=zone,
                           music_path=core.ask('Existing Music Assistant sidebar path (after host/port)', '/music-assistant'))
                if not cfg['music_path'].startswith('/') or cfg['music_path'].startswith('//') or any(c.isspace() for c in cfg['music_path']):
                    raise ValueError('Use a local Music Assistant sidebar path beginning with one slash.')
                for key in ('home_slug', 'va_slug', 'tv_slug'):
                    cfg[key] = core.ask(key.replace('_', ' ').title(), p[key])
                    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)+', cfg[key]):
                        raise ValueError('Dashboard names need a hyphen and lowercase letters/digits.')
                if len({cfg[k] for k in ('home_slug', 'va_slug', 'tv_slug')}) != 3:
                    raise ValueError('Use three distinct dashboard names.')
            core.save(choice_file, cfg)
            core.build(PROFILE)
            core.prepare_dashboards(PROFILE, ha)
            gather_apks(serial, cfg)
            command = [sys.executable, str(core.ROOT / 'devices/install-device.py'), '--profile', PROFILE, '--serial', serial]
            subprocess.run(command, check=True)  # Always recheck real device prerequisites.
            fingerprint = hashlib.sha256(json.dumps({'services':cfg['services'], 'timezone':cfg['timezone']}, sort_keys=True).encode()).hexdigest()
            progress = core.read(progress_file) if progress_file.exists() else {}
            completed = progress.get('serial') == serial and progress.get('usb_choices') == fingerprint
            if not (completed and core.yes('USB installation previously completed. Keep it and continue to HA?')):
                subprocess.run(command + ['--apply'], check=True)
                core.save(progress_file, {'serial':serial, 'usb_choices':fingerprint})
                print('Reboot the Echo Show once before checking streaming playback.')
                if core.yes('Reboot this Echo Show now?'):
                    usb(serial, 'reboot')
            if core.yes('Install/update the bundled HA integration through a mounted HA config folder?'):
                core.install_ha(core.ask('Path to HA config folder containing configuration.yaml'))
            else:
                print('Copy VACAV/integration/custom_components/vaca_vision into HA custom_components,')
                print('and devices/dashboards/{upstream,assets} contents into HA www/es8-athena, then restart HA.')
            handoff(cfg)
        # Close before the human handoff; HA may restart. Never persist the token.
        ha.ws.close(); ha = None
        while True:
            if not check_only and not core.yes('Finished the HA steps and ready for connection checks?'):
                print('Progress saved. Run ./vacav_setup.sh again when ready.'); return False
            try:
                ha = core.HA(url, token)
                states, registry = snapshot(ha)
                entity = select('View Assist sensor for THIS Echo Show', va_sensors(states, registry))
                errors = validate_ready(states, registry, entity, cfg)
                if errors:
                    raise ValueError('\n'.join(errors))
                print('HA checks passed: VA, VACAVision microphone/display, MA entities, weather and Home path.')
                print('The entity API cannot prove the physical speaker or sound. Confirm those on the device.')
                if check_only:
                    return True
                if not core.yes('Have you heard an Assist reply and music from this Echo Show?'):
                    print('Finish the physical playback check before installing dashboards.'); return False
                cfg.update(va_entity=entity, weather_entity=states[entity]['attributes']['weather_entity'])
                core.save(choice_file, cfg)
                if core.deploy_dashboards(PROFILE, ha):
                    print('Setup complete. Sign into selected streaming apps on the ES8 and test playback.')
                    return True
                print('Dashboard installation cancelled. Run ./vacav_setup.sh again to resume.'); return False
            except (ValueError, RuntimeError, OSError) as error:
                print('Not ready:', error)
                if check_only:
                    return False
                print('Correct the HA settings and try again, or answer No to resume later.')
            finally:
                if ha:
                    ha.ws.close(); ha = None
    finally:
        if ha:
            ha.ws.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-ha', action='store_true', help='Read-only HA readiness checks; no USB or installation')
    args = parser.parse_args()
    try:
        sys.exit(0 if run(args.check_ha) else 1)
    except (KeyboardInterrupt, EOFError):
        print('\nStopped. Run ./vacav_setup.sh again to resume.'); sys.exit(1)
    except Exception as error:
        print('Stopped:', error, '\nCorrect the problem and run ./vacav_setup.sh again.'); sys.exit(1)
