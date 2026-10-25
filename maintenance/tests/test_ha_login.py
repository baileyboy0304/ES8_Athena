import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import unittest
from unittest.mock import patch, Mock
from ha_login import Login, NoRedirect

class Authentication(unittest.TestCase):
    def test_mfa_refresh_and_revoke_kept_in_memory(self):
        session = Login('http://ha.local:8123')
        with patch.object(session, 'request', side_effect=[
            [{'type':'homeassistant','id':None}],
            {'type':'form','step_id':'init','flow_id':'one'},
            {'type':'form','step_id':'mfa','flow_id':'one','data_schema':[{'name':'code'}]},
            {'type':'create_entry','result':'code'},
            {'access_token':'first','refresh_token':'refresh','expires_in':1800},
            {'access_token':'second','expires_in':1800}, {}]) as request, \
                patch('builtins.input', return_value='admin'), patch('ha_login.getpass.getpass', side_effect=['password','123456']):
            session.sign_in()
            self.assertEqual(request.call_args_list[3].args[1]['code'], '123456')
            self.assertEqual(session.access_token(), 'first')
            session.expires = 0
            self.assertEqual(session.access_token(), 'second')
            session.close()
            self.assertEqual(request.call_args.args[1], {'action':'revoke','token':'refresh'})
            self.assertIsNone(session.refresh_token)
            self.assertIsNone(session._access)

    def test_two_wrong_attempts_stop_and_cancel_flow(self):
        session = Login('http://ha.local:8123')
        bad = {'type':'form','step_id':'init','flow_id':'one','errors':{'base':'invalid_auth'}}
        with patch.object(session, 'request', side_effect=[
            [{'type':'homeassistant','id':None}],
            {'type':'form','step_id':'init','flow_id':'one'}, bad, bad, {}]) as request, \
                patch('builtins.input', return_value='admin'), patch('ha_login.getpass.getpass', return_value='wrong'):
            with self.assertRaisesRegex(RuntimeError, 'Two login attempts'):
                session.sign_in()
            self.assertEqual(request.call_count, 5)
            self.assertEqual(request.call_args.kwargs['method'], 'DELETE')

    def test_password_requests_never_follow_redirects(self):
        self.assertIsNone(NoRedirect().redirect_request(None,None,302,'',{},'https://elsewhere.invalid'))
        for url in ('https://user:password@ha.local','file:///etc/passwd','https://ha.local/path','https://ha.local/?key=x'):
            with self.assertRaises(ValueError): Login(url)
