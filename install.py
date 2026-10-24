#!/usr/bin/env python3
"""ES8 Athena: local configuration, VACAV installation, and VA dashboards."""
import argparse
import copy
import datetime as dt
import getpass
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from zoneinfo import ZoneInfo
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
PACKAGE = 'com.mph1970.vacavision'
ACTIVITY = PACKAGE + '/com.msp1974.vacompanion.MainActivity'
STANDARD = ['alarm', 'alert', 'calendar', 'camera', 'info', 'infopic', 'intent',
            'list', 'locate', 'music', 'sports', 'thermostat', 'webpage']

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')

def ask(question, default=''):
    answer = input(question + (f' [{default}]' if default else '') + ': ').strip()
    return answer or default

def yes(question):
    while True:
        answer = ask(question + ' (Y/N)', 'N').lower()
        if answer in ('y', 'yes', 'n', 'no'):
            return answer in ('y', 'yes')

def stamp():
    return dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f')

def profile(name):
    if not re.fullmatch(r'[a-z0-9_-]+', name):
        raise ValueError('Invalid profile name')
    return read(ROOT / 'devices' / name / 'profile.json')

def settings(name):
    return read(ROOT / 'installation-data/choices' / (name + '.json'))

def choose(name):
    p = profile(name)
    print('\n' + p['name'] + ': configure dashboards and optional streaming apps.')
    print('Streaming is optional. Answer No to every app if you do not want streaming.')
    print('This wizard also saves your View Assist sensor, weather entity and dashboard paths.')
    print('On ES8, selected apps receive internet TCP 80/443 access, including ads and telemetry.')
    print('Apple TV on ES8 uses Silk; its exception covers all sites opened in Silk.')
    selected = [s['id'] for s in p['services'] if yes('Include ' + s['name'] + '?')]
    entity = ask('View Assist sensor entity', 'sensor.es8' if name == 'es8-gen2' else 'sensor.portal')
    weather = ask('Weather entity', 'weather.home')
    if not re.fullmatch(r'sensor\.[a-z0-9_]+', entity) or not re.fullmatch(r'weather\.[a-z0-9_]+', weather):
        raise ValueError('Use real sensor.* and weather.* entity IDs from Home Assistant')
    ma = ask('Music Assistant HA sidebar path (copy from your browser)', '/music-assistant')
    if not ma.startswith('/') or ma.startswith('//') or any(c.isspace() for c in ma):
        raise ValueError('Use a local HA path starting with one slash')
    local_zone = Path('/etc/timezone')
    timezone = ask('Device timezone (IANA name, e.g. Europe/London)',
                   local_zone.read_text().strip() if local_zone.exists() else 'UTC')
    try:
        ZoneInfo(timezone)
    except (KeyError, ValueError):
        raise ValueError('Use a valid IANA timezone, e.g. Europe/London') from None
    cfg = dict(profile=name, services=selected, va_entity=entity, weather_entity=weather, timezone=timezone,
               music_path=ma, **{k: p[k] for k in ('va_slug', 'home_slug', 'tv_slug')})
    for key in ('va_slug', 'home_slug', 'tv_slug'):
        cfg[key] = ask(key.replace('_', ' ').title(), cfg[key])
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)+', cfg[key]):
            raise ValueError('Dashboard slugs must contain a hyphen and only lowercase letters/digits')
    if len({cfg[k] for k in ('va_slug', 'home_slug', 'tv_slug')}) != 3:
        raise ValueError('Dashboard slugs must be distinct')
    dest = ROOT / 'installation-data/choices' / (name + '.json')
    if dest.exists() and not yes('Replace saved choices?'):
        return
    save(dest, cfg)
    print('Saved', dest, '\nNext: python install.py dashboards --profile ' + name)

BACKGROUND = 'radial-gradient(ellipse at 4% 5%, #1d3d59 0, transparent 55%), linear-gradient(120deg, #132b40, #101e30 72%)'

def tile(name, icon, target, url=False):
    card = copy.deepcopy(read(ROOT / 'devices/dashboards/custom/navigation.json'))
    card['styles']['name'].append({'white-space': 'normal'})
    card.update(name=name, icon=icon, tap_action={
        'action': 'url' if url else 'navigate',
        'url_path' if url else 'navigation_path': target})
    return card

def launcher_view(title, path, cards, scale=1):
    # One panel owns the full background; masonry must not split navigation and apps.
    for card in cards:
        if card['type'] == 'custom:button-card':
            card['styles']['card'] += [{'width': 'calc(140px * var(--va-clock-shortcut-scale, 1))'},
                                       {'height': 'calc(110px * var(--va-clock-shortcut-scale, 1))'}]
            card['styles']['grid'] += [{'grid-template-rows': 'calc(34px * var(--va-clock-shortcut-scale, 1)) auto'}]
            card['styles']['name'] += [{'text-overflow': 'clip'}, {'overflow': 'visible'}]
    return {'title': title, 'path': path, 'type': 'panel', 'cards': [{
        'type': 'custom:button-card', 'show_name': False, 'show_icon': False,
        'tap_action': {'action': 'none'},
        'styles': {
            'card': [{'background': BACKGROUND}, {'border': 'none'}, {'border-radius': '0'},
                     {'min-height': '100vh'}, {'padding': '28px'}, {'box-sizing': 'border-box'},
                     {'--va-clock-shortcut-scale': str(scale)}],
            'grid': [{'grid-template-areas': '"content"'}, {'grid-template-columns': '1fr'},
                     {'align-items': 'start'}, {'align-content': 'start'}, {'height': '100%'},
                     {'grid-template-rows': 'min-content'}],
            'custom_fields': {'content': [{'position': 'absolute'}, {'top': '28px'}, {'left': '28px'}]}},
        'custom_fields': {'content': {'card': {
            'type': 'grid', 'columns': min(5, max(1, len(cards))), 'square': False, 'cards': cards}}}}]}

def build(name):
    import yaml
    p, cfg = profile(name), settings(name)
    replacements = {'@@VA_ENTITY@@': cfg['va_entity'], '@@VA_PATH@@': '/' + cfg['va_slug'],
                    '@@SHORTCUT_SCALE@@': str(p['shortcut_scale']),
                    'weather.home': cfg['weather_entity'], '/view-assist': '/' + cfg['va_slug'],
                    '/home-launcher/home': '/' + cfg['home_slug'] + '/home',
                    '/view_assist/': '/local/es8-athena/'}
    def substitute(value):
        if isinstance(value, str):
            pattern = '|'.join(re.escape(k) for k in sorted(replacements, key=len, reverse=True))
            return re.sub(pattern, lambda match: replacements[match.group(0)], value)
        if isinstance(value, dict):
            return {k: substitute(v) for k, v in value.items()}
        if isinstance(value, list):
            return [substitute(v) for v in value]
        return value
    home_path, tv_path = '/' + cfg['home_slug'] + '/home', '/' + cfg['tv_slug'] + '/tv'
    nav = {'type': 'horizontal-stack', 'cards': [tile('Home', 'mdi:home-outline', home_path), tile('TV', 'mdi:television-classic', tv_path)]}
    clock = substitute(read(ROOT / 'devices/dashboards/custom/clock.json'))
    # Retain the user's updated clock face, responsive styling and weather strip.
    clock['cards'][0]['custom_fields']['heading']['card'] = copy.deepcopy(nav)
    # body_template supplies two columns; this clock has one named-area column.
    clock['cards'][0]['styles']['grid'].append({'grid-template-columns': 'minmax(0, 1fr)'})
    weather = substitute(read(ROOT / 'devices/dashboards/custom/weather.json'))
    weather['cards'] = [{'type': 'vertical-stack', 'cards': [copy.deepcopy(nav)] + weather['cards']}]
    upstream = ROOT / 'devices/dashboards/upstream'
    base = yaml.safe_load((upstream / 'dashboard/dashboard.yaml').read_text(encoding='utf-8'))
    templates = base.get('button_card_templates', {})
    templates.update(read(ROOT / 'devices/dashboards/custom/templates.json'))
    views = [clock, weather]
    for key in STANDARD:
        card = yaml.safe_load((upstream / 'views' / key / (key + '.yaml')).read_text(encoding='utf-8'))
        # Upstream files are cards, not complete Lovelace views.
        views.append({'title': key.title(), 'path': key, 'type': 'panel',
                      'cards': [{'type': 'vertical-stack', 'cards': [copy.deepcopy(nav), substitute(card)]}]})
    va = {'title': 'View Assist', 'button_card_templates': substitute(templates), 'views': views}
    home = {'title': p['name'], 'views': [launcher_view('Home', 'home', [
        tile('View Assist', 'mdi:microphone', '/' + cfg['va_slug'] + '/clock'),
        tile('Music Assistant', 'mdi:music-note-outline', '/' + cfg['home_slug'] + '/music'),
        tile('TV', 'mdi:television-classic', tv_path)], p['shortcut_scale'])]}
    music = {'type': 'custom:athena-music-card', 'home_path': home_path, 'path': cfg['music_path'], 'display_entity': cfg['va_entity']}
    addon = re.fullmatch(r'/(?:app/)?([a-z0-9]+_music_assistant)', cfg['music_path'])
    if addon:
        music['addon'] = addon.group(1)
    home['views'].append({'title': 'Music Assistant', 'path': 'music', 'type': 'panel', 'cards': [music]})
    services = [s for s in p['services'] if s['id'] in cfg['services']]
    tv_cards = [tile('Home', 'mdi:home-outline', home_path)]
    tv_cards += [tile(s['name'], s['icon'], s['url'], True) for s in services]
    if not services:
        tv_cards.append({'type': 'markdown', 'content': 'No streaming services selected. Run the installer to add services.'})
    tv = {'title': 'TV', 'views': [launcher_view('TV', 'tv', tv_cards, p['shortcut_scale'])]}
    out = ROOT / 'installation-data/generated' / name
    for key, obj in [('va', va), ('home', home), ('tv', tv)]:
        save(out / (key + '.json'), obj)
        (out / (key + '.yaml')).write_text(yaml.safe_dump(obj, sort_keys=False, allow_unicode=True), encoding='utf-8')
    (out / 'android.conf').write_text('web_packages=' + ' '.join(s['package'] for s in services) + '\n', encoding='utf-8')
    save(out / 'choices.json', cfg)
    print('Prepared', out, '\nHome:', home_path, '\nVA:', '/' + cfg['va_slug'] + '/clock', '\nTV:', tv_path)
    return cfg

class HA:
    def __init__(self, url, token):
        import websocket
        parsed = urlsplit(url)
        if parsed.scheme not in ('http', 'https') or not parsed.netloc or parsed.username or parsed.query or parsed.fragment or parsed.path not in ('', '/'):
            raise ValueError('Enter the HA base URL, e.g. http://homeassistant.local:8123')
        self.base_url, self.token = url.rstrip('/'), token
        self.ws = websocket.create_connection(('wss' if parsed.scheme == 'https' else 'ws') + '://' + parsed.netloc + '/api/websocket', timeout=30)
        self.seq = 0
        self.ws.recv()
        self.ws.send(json.dumps({'type': 'auth', 'access_token': token}))
        if json.loads(self.ws.recv()).get('type') != 'auth_ok':
            raise RuntimeError('HA authentication failed')
    def call(self, kind, **kwargs):
        self.seq += 1
        self.ws.send(json.dumps(dict(id=self.seq, type=kind, **kwargs)))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get('id') == self.seq:
                if not msg.get('success'):
                    raise RuntimeError(str(msg.get('error')))
                return msg.get('result')

    def post(self, path, body):
        request = Request(self.base_url + '/api/' + path,
            data=json.dumps(body).encode(), headers={
                'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json'})
        try:
            with urlopen(request, timeout=30) as response:
                return json.load(response)
        except HTTPError as error:
            raise RuntimeError('HA rejected configuration: ' + error.read().decode()) from None

def create_view_assist(name):
    """Use VA's normal config flow, including on versions with an old UI filter."""
    cfg = settings(name)
    ha = HA(ask('Home Assistant base URL'),
            getpass.getpass('HA administrator token (not saved): '))
    try:
        states = {s['entity_id']: s for s in ha.call('get_states')}
        friendly = ask('New View Assist device name')
        mic = ask('VACAV Assist entity (assist_satellite.*)')
        speaker = ask('VACAV Music entity (media_player.*)')
        display = ask('VACAV display ID value (va-..., not sensor.*)')
        if not friendly or not display.startswith('va-'):
            raise ValueError('A device name and the actual va- display ID are required')
        for entity, domain in [(mic, 'assist_satellite.'), (speaker, 'media_player.')]:
            if not entity.startswith(domain) or entity not in states:
                raise ValueError('Missing/wrong entity: ' + entity)
        if not any(s['state'] == display for s in states.values()):
            raise ValueError('Display ID is not reported by HA; copy the VACAV display sensor value')
        if any(s.get('attributes', {}).get('display_device') == display for s in states.values()):
            raise ValueError('A VA device already uses this display ID; use its options instead')
        print('Create VA:', friendly, '\nMicrophone:', mic, '\nPlayer:', speaker,
              '\nDisplay:', display, '\nDashboard:', '/' + cfg['va_slug'])
        if not yes('Create this View Assist device?'):
            return
        flow = ha.post('config/config_entries/flow', {'handler': 'view_assist', 'show_advanced_options': True})
        path = 'config/config_entries/flow/' + flow['flow_id']
        flow = ha.post(path, {'type': 'view_audio'})
        fields = {f['name']: f for f in flow.get('data_schema', [])}
        required = {'name', 'mic_device', 'mediaplayer_device', 'musicplayer_device', 'display_device'}
        if flow.get('step_id') != 'options' or not required.issubset(fields):
            raise RuntimeError('Unsupported VA setup form; complete setup in HA')
        options = fields['display_device'].get('selector', {}).get('select', {}).get('options', [])
        displays = {o['value'] if isinstance(o, dict) else o for o in options}
        if display not in displays:
            raise RuntimeError('VA has not discovered this display. Sign into HA on the display, '
                               'load the prepared setup page, then run this command again.')
        result = ha.post(path, {'name': friendly, 'mic_device': mic,
            'mediaplayer_device': speaker, 'musicplayer_device': speaker, 'display_device': display})
        if result.get('type') != 'create_entry':
            raise RuntimeError('VA did not finish creation: ' + str(result.get('errors', result.get('type'))))
        print('Created View Assist device:', friendly)
        print('Now set its dashboard/defaults in HA as described in README step 7,')
        print('then copy the new VA sensor ID into the choices wizard before step 8.')
    finally:
        ha.ws.close()

def placeholder_dashboard(title, view_path):
    return {'title': title, 'views': [{'title': 'Setup', 'path': view_path,
        'cards': [{'type': 'markdown', 'content':
            '# Welcome — setup is in progress\n\n'
            'Your display has reached Home Assistant.\n\n'
            'On the installation computer, finish the View Assist device settings '
            'in README step 7, then install the dashboards in step 8. '
            'This page will be replaced by your finished dashboard.\n\n'
            'If setup has finished, refresh this page.'}]}]}

def prepare_dashboards(name):
    """Create safe landing pages before pairing; never overwrite a dashboard."""
    cfg = settings(name)
    ha = HA(ask('Home Assistant base URL'),
            getpass.getpass('HA long-lived access token (not saved): '))
    try:
        known = {d['url_path'] for d in ha.call('lovelace/dashboards/list')}
        for key, title, view in [('home_slug', 'Athena Home', 'home'),
                                  ('va_slug', 'View Assist', 'clock'),
                                  ('tv_slug', 'TV', 'tv')]:
            slug = cfg[key]
            if slug in known:
                print('Kept existing dashboard:', slug)
                continue
            ha.call('lovelace/dashboards/create', url_path=slug, title=title,
                    icon='mdi:tablet-dashboard', show_in_sidebar=True, require_admin=False)
            config = placeholder_dashboard(title, view)
            ha.call('lovelace/config/save', url_path=slug, config=config)
            if ha.call('lovelace/config', url_path=slug) != config:
                raise RuntimeError('Placeholder read-back mismatch: ' + slug)
            print('Prepared setup page:', slug)
    finally:
        ha.ws.close()

def deploy_dashboards(name):
    cfg = build(name)
    url = ask('Home Assistant base URL')
    token = getpass.getpass('HA long-lived access token (not saved): ')
    ha = HA(url, token)
    backup = ROOT / 'installation-data/backups' / ('dashboards-' + stamp())
    try:
        known = {d['url_path']: d for d in ha.call('lovelace/dashboards/list')}
        states = {s['entity_id'] for s in ha.call('get_states')}
        missing = [cfg[k] for k in ('va_entity', 'weather_entity') if cfg[k] not in states]
        if missing:
            raise RuntimeError('Create/correct these HA entities first: ' + ', '.join(missing))
        plan = []
        for kind, key in [('home', 'home_slug'), ('va', 'va_slug'), ('tv', 'tv_slug')]:
            slug = cfg[key]
            before = ha.call('lovelace/config', url_path=slug) if slug in known else None
            if slug in known and known[slug].get('mode') != 'storage':
                raise RuntimeError(slug + ' is not a storage dashboard')
            save(backup / (slug + '.json'), {'url_path': slug, 'dashboard': known.get(slug), 'config': before})
            plan.append((kind, slug, before))
        print('Will save:', ', '.join(slug for _, slug, _ in plan))
        print('Existing dashboard contents will be replaced. Backup:', backup)
        if not yes('Install these three prepared dashboards?'):
            return
        resource_url = '/local/es8-athena/athena-music-card.js?v=2'
        resources = ha.call('lovelace/resources')
        existing_resource = next((r for r in resources if r.get('url', '').split('?')[0] == resource_url.split('?')[0]), None)
        if existing_resource and existing_resource['url'] != resource_url:
            ha.call('lovelace/resources/update', resource_id=existing_resource['id'], res_type='module', url=resource_url)
        elif not existing_resource:
            ha.call('lovelace/resources/create', res_type='module', url=resource_url)
        for kind, slug, before in plan:
            if before is not None and ha.call('lovelace/config', url_path=slug) != before:
                raise RuntimeError(slug + ' changed since backup; stopped')
            config = read(ROOT / 'installation-data/generated' / name / (kind + '.json'))
            if slug not in known:
                ha.call('lovelace/dashboards/create', url_path=slug, title=config['title'],
                        icon='mdi:tablet-dashboard', show_in_sidebar=True, require_admin=False)
            ha.call('lovelace/config/save', url_path=slug, config=config)
            if ha.call('lovelace/config', url_path=slug) != config:
                raise RuntimeError('Dashboard read-back mismatch: ' + slug)
            print('Installed', slug)
    finally:
        ha.ws.close()

def install_ha(target):
    target = Path(target).expanduser().resolve()
    if not (target / 'configuration.yaml').is_file():
        raise ValueError('Point --ha-config to the HA config directory containing configuration.yaml')
    source = ROOT / 'VACAV/integration/custom_components/vaca_vision'
    dest = target / 'custom_components/vaca_vision'
    backup = ROOT / 'installation-data/backups' / ('ha-' + stamp())
    print('Install VACAV prototype.10 to', dest)
    if not yes('Home Assistant is stopped or ready for restart; continue?'):
        return
    if dest.exists():
        shutil.copytree(dest, backup / 'vaca_vision')
        print('Previous integration saved:', backup)
    shutil.copytree(source, dest, dirs_exist_ok=True)
    # Own asset namespace: does not replace VA-managed assets or overlays.
    asset = target / 'www/es8-athena'
    shutil.copytree(ROOT / 'devices/dashboards/upstream', asset, dirs_exist_ok=True)
    shutil.copytree(ROOT / 'devices/dashboards/assets', asset, dirs_exist_ok=True)
    print('Files installed. Restart HA, then follow README.md steps 6–8 for pairing and VA mapping.')

def verify():
    lock = read(ROOT / 'maintenance/source-versions.json')
    eda = ROOT / 'echo-dot-assist'
    if not (eda / '.git').exists():
        raise RuntimeError('EDA submodule missing. Run: git submodule update --init echo-dot-assist')
    head = subprocess.check_output(['git','-C',str(eda),'rev-parse','HEAD'], text=True).strip()
    if head != lock['eda_base']:
        raise RuntimeError('EDA commit differs from maintenance/source-versions.json')
    subprocess.run(['git','-C',str(eda),'diff','--exit-code','HEAD','--'],check=True,stdout=subprocess.DEVNULL)
    bad = []
    for f in read(ROOT / 'maintenance/checksums.json'):
        p = ROOT / f['path']
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != f['sha256']:
            bad.append(f['path'])
    if bad:
        raise RuntimeError('Component checksums differ: ' + ', '.join(bad))
    print('EDA checkout is unchanged at the recorded upstream commit. Component/dashboard checksums match.')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['choose', 'device', 'dashboards', 'prepare-dashboards', 'create-view-assist', 'deploy-dashboards', 'install-ha', 'verify'])
    parser.add_argument('--profile', choices=['es8-gen2', 'portal_plus_gen_2'], default='es8-gen2')
    parser.add_argument('--ha-config')
    parser.add_argument('--serial', help='USB serial for device; optional with exactly one USB device connected')
    parser.add_argument('--apply', action='store_true', help='Apply device installation after review')
    parser.add_argument('--export-apps', action='store_true', help='Export installed streaming APKs before wiping')
    args = parser.parse_args()
    if args.command != 'device' and (args.serial or args.apply or args.export_apps):
        parser.error('--serial, --apply and --export-apps require the device command')
    if args.command == 'device':
        command = [sys.executable, '-B', str(ROOT / 'devices/install-device.py'),
                   '--profile', args.profile]
        if args.serial is not None: command.extend(['--serial', args.serial])
        if args.apply: command.append('--apply')
        if args.export_apps: command.append('--export-apps')
        subprocess.run(command, check=True)
        return
    if args.command == 'verify': verify()
    elif args.command == 'choose': choose(args.profile)
    elif args.command == 'dashboards': build(args.profile)
    elif args.command == 'prepare-dashboards': prepare_dashboards(args.profile)
    elif args.command == 'create-view-assist': create_view_assist(args.profile)
    elif args.command == 'deploy-dashboards': deploy_dashboards(args.profile)
    elif args.command == 'install-ha':
        if not args.ha_config: parser.error('--ha-config is required')
        verify(); install_ha(args.ha_config)

if __name__ == '__main__':
    try: main()
    except (ValueError, RuntimeError, OSError, subprocess.CalledProcessError) as error:
        sys.exit(str(error))
