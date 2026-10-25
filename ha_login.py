"""Interactive HA login with MFA and an in-memory, revocable session."""
import getpass
import json
import time
from urllib.error import HTTPError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler

CLIENT_ID = 'https://github.com/baileyboy0304/ES8_Athena/'


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Never forward a password or session to a redirect destination.
        return None


class Login:
    def __init__(self, url):
        parsed = urlsplit(url)
        if (parsed.scheme not in ('http', 'https') or not parsed.netloc or parsed.username
                or parsed.query or parsed.fragment or parsed.path not in ('', '/')):
            raise ValueError('Enter the Home Assistant base URL, including http:// or https://.')
        self.url = url.rstrip('/')
        self.refresh_token = None
        self._access = None
        self.expires = 0
        self.opener = build_opener(NoRedirect)

    def request(self, path, data=None, form=False, method=None):
        body = None if data is None else (urlencode(data) if form else json.dumps(data)).encode()
        req = Request(self.url + path, data=body, method=method, headers={
            'Content-Type': 'application/x-www-form-urlencoded' if form else 'application/json'})
        try:
            with self.opener.open(req, timeout=30) as response:
                raw = response.read()
                return json.loads(raw) if raw else {}
        except HTTPError as exc:
            if exc.code == 403:
                raise RuntimeError('Home Assistant refused access (403). This PC may be IP-banned; '
                                   'check HA before attempting another login.') from None
            raise RuntimeError(f'Home Assistant login request failed (HTTP {exc.code}); no automatic retry.') from None

    def sign_in(self):
        print('Sign into Home Assistant at ' + self.url)
        if self.url.startswith('http://'):
            print('This address uses HTTP. Use it only on your trusted LAN; use HTTPS for a remote connection.')
        providers = self.request('/auth/providers')
        provider = next((p for p in providers if p['type'] == 'homeassistant'), None)
        if provider is None:
            raise ValueError('This HA instance does not offer Home Assistant username/password login.')
        flow = self.request('/auth/login_flow', {'client_id': CLIENT_ID,
            'redirect_uri': CLIENT_ID, 'handler': [provider['type'], provider.get('id')]})
        flow_id = flow.get('flow_id')
        failures = 0
        try:
            while flow.get('type') == 'form':
                if flow.get('errors'):
                    failures += 1
                    if failures >= 2:
                        raise RuntimeError('Two login attempts were rejected. Stopping to avoid further HA IP-ban failures.')
                    print('HA rejected those credentials or MFA code. Check them carefully; repeated failures can IP-ban this PC.')
                step = flow.get('step_id')
                if step == 'init':
                    data = {'username': input('HA username: ').strip(),
                            'password': getpass.getpass('HA password: ')}
                elif step == 'mfa':
                    fields = {f['name'] for f in flow.get('data_schema', [])}
                    if fields != {'code'}:
                        raise ValueError('This MFA method is not supported by the terminal installer. Use a code-based HA MFA method.')
                    data = {'code': getpass.getpass('HA two-factor authentication code: ').strip()}
                elif step == 'select_mfa_module':
                    options = flow['data_schema'][0].get('options', [])
                    if isinstance(options, dict):
                        options = list(options.items())
                    for i, option in enumerate(options, 1):
                        print(f'{i}. {option[1]}')
                    choice = input('MFA method number: ').strip()
                    if not choice.isdigit() or not 1 <= int(choice) <= len(options):
                        raise ValueError('Choose a listed MFA method.')
                    data = {'multi_factor_auth_module': options[int(choice)-1][0]}
                else:
                    raise ValueError('Unsupported HA login step: ' + str(step))
                data['client_id'] = CLIENT_ID
                flow = self.request('/auth/login_flow/' + flow_id, data)
                del data
            if flow.get('type') != 'create_entry':
                raise RuntimeError('HA login did not complete: ' + str(flow.get('reason', 'unexpected response')))
            flow_id = None
            result = self.request('/auth/token', {'grant_type': 'authorization_code',
                'code': flow['result'], 'client_id': CLIENT_ID}, form=True)
            self.refresh_token = result['refresh_token']
            self._update(result)
            return self
        finally:
            if flow_id:
                try:
                    self.request('/auth/login_flow/' + flow_id, method='DELETE')
                except Exception:
                    pass

    def _update(self, result):
        self._access = result['access_token']
        self.expires = time.monotonic() + result['expires_in'] - 60

    def access_token(self):
        if not self.refresh_token:
            raise RuntimeError('HA session is closed; sign in again.')
        if time.monotonic() >= self.expires:
            self._update(self.request('/auth/token', {'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token, 'client_id': CLIENT_ID}, form=True))
        return self._access

    def close(self):
        if self.refresh_token:
            try:
                # Supported by older HA releases as well as current versions.
                self.request('/auth/token', {'action': 'revoke', 'token': self.refresh_token}, form=True)
            except Exception:
                print('Could not revoke the installer session. Remove it in HA Profile → Security → Refresh tokens.')
            finally:
                self.refresh_token = self._access = None
