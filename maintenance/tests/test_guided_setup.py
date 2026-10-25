"""HA handoff checks against both entity-ID and device-ID View Assist mappings."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import guided_setup as g

class Readiness(unittest.TestCase):
    def setUp(self):
        self.cfg = {'va_slug': 'view-assist-test'}
        self.attrs = {'mic_device':'assist_satellite.es8', 'display_device':'va-test',
                      'mediaplayer_device':'media_player.ma', 'musicplayer_device':'media_player.ma',
                      'weather_entity':'weather.home', 'home_screen':'/view-assist-test/clock'}
        self.states = {'sensor.va':{'state':'idle','attributes':self.attrs},
                       'assist_satellite.es8':{'state':'idle'},
                       'sensor.display':{'state':'va-test'},
                       'media_player.ma':{'state':'idle', 'attributes':{'mass_player_type':'player'}},
                       'weather.home':{'state':'cloudy'}}
        self.registry = {'sensor.va':{'platform':'view_assist'},
                         'assist_satellite.es8':{'platform':'vaca_vision','device_id':'es8-device'},
                         'sensor.display':{'platform':'vaca_vision','device_id':'es8-device'},
                         'media_player.ma':{'platform':'music_assistant'}}
    def errors(self):
        return g.validate_ready(self.states,self.registry,'sensor.va',self.cfg)
    def test_accepts_entity_mapping_and_inherits_existing_weather_timezone(self):
        self.assertEqual(self.errors(),[])
        self.assertEqual(g.inherited_settings({'time_zone':'Europe/London'},self.states,self.registry,'sensor.va'),
                         ('weather.home','Europe/London'))
    def test_accepts_va_device_registry_mapping(self):
        self.attrs['mic_device']='es8-device'
        self.assertEqual(self.errors(),[])
    def test_rejects_wrong_display_even_when_it_exists(self):
        self.registry['sensor.display']['device_id']='another-display'
        self.assertTrue(any('same VACAVision' in e for e in self.errors()))
    def test_rejects_proxy_unavailable_and_group(self):
        self.registry['media_player.ma']['platform']='vaca_vision'
        self.assertTrue(self.errors())
        self.registry['media_player.ma']['platform']='music_assistant'
        self.states['media_player.ma']['state']='unavailable'
        self.assertTrue(self.errors())
        self.states['media_player.ma']['state']='idle'
        self.states['media_player.ma']['attributes']['mass_player_type']='group'
        self.assertTrue(any('sync group' in e for e in self.errors()))
    def test_rejects_disconnected_mic_and_stale_home_weather(self):
        self.states['assist_satellite.es8']['state']='unavailable'
        self.attrs['home_screen']='/old/clock'
        self.attrs['weather_entity']='weather.gone'
        errors=self.errors()
        self.assertTrue(any('microphone' in e for e in errors))
        self.assertTrue(any('Home/default' in e for e in errors))
        self.assertTrue(any('weather' in e for e in errors))
    def test_existing_physical_player_group_members_do_not_make_it_a_group(self):
        self.states['media_player.ma']['attributes']['group_members']=['media_player.ma']
        self.assertEqual(self.errors(),[])
    def test_missing_va_and_unknown_weather_stop_inheritance(self):
        self.registry['sensor.va']['platform']='other'
        with self.assertRaises(ValueError):
            g.inherited_settings({'time_zone':'UTC'},self.states,self.registry,'sensor.va')
        self.assertTrue(self.errors())

class HandoffGate(unittest.TestCase):
    def test_read_only_mode_never_logs_in_or_accesses_usb(self):
        from unittest.mock import patch
        with patch.object(g.core, 'verify'), patch.object(g.core, 'HA') as ha, patch.object(g, 'resolve_usb') as usb:
            self.assertTrue(g.run(check_only=True))
            ha.assert_not_called()
            usb.assert_not_called()


if __name__ == "__main__": unittest.main()


class ConnectionPreparation(unittest.TestCase):
    def test_sends_latest_public_identity_with_name_and_dashboard(self):
        from unittest.mock import Mock, patch
        ha=Mock(); ha.post.side_effect=[{'type':'menu','flow_id':'test-flow','menu_options':['manual']},{'type':'form','step_id':'manual'},{'type':'abort','reason':'setup_prepared','description_placeholders':{'setup_protocol':'2'}}]
        with patch.object(g,'usb',side_effect=['inet addr:192.0.2.1', 'sendspin: player '+'A'*43+' on 28928\nsendspin: player '+'B'*43+' on 28928']):
            g.prepare_connection(ha,{'device_name':'Test','home_slug':'test-home'},'serial')
        data=ha.post.call_args.args[1]
        self.assertEqual(data['sendspin_client_id'],'B'*43)
        self.assertEqual(data['dashboard'],'/test-home/home')
        self.assertNotIn('eda_noise_psk',data)
    def test_missing_log_keeps_named_player_fallback(self):
        from unittest.mock import Mock, patch
        ha=Mock(); ha.post.side_effect=[{'type':'menu','flow_id':'test-flow','menu_options':['manual']},{'type':'form','step_id':'manual'},{'type':'abort','reason':'setup_prepared','description_placeholders':{'setup_protocol':'2'}}]
        with patch.object(g,'usb',side_effect=['inet addr:192.0.2.1','']):
            g.prepare_connection(ha,{'device_name':'Test','home_slug':'test-home'},'serial')
        self.assertEqual(ha.post.call_args.args[1]['sendspin_client_id'],'')
    def test_old_integration_requires_update_without_deleting_completed_flow(self):
        from unittest.mock import Mock, patch
        ha=Mock(); ha.post.side_effect=[{'type':'menu','flow_id':'test-flow','menu_options':['manual']},{'type':'form','step_id':'manual'},{'type':'abort','reason':'setup_prepared','flow_id':'finished'}]
        with patch.object(g,'usb',side_effect=['inet addr:192.0.2.1','']):
            with self.assertRaisesRegex(ValueError,'HACS integration version'):
                g.prepare_connection(ha,{'device_name':'Test','home_slug':'test-home'},'serial')
        ha.delete.assert_not_called()

class CredentialFreeInstall(unittest.TestCase):
    def test_normal_wizard_never_connects_to_ha(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp, patch.object(g.core, 'ROOT', Path(tmp)), \
             patch.object(g.core, 'verify'), patch.object(g.core, 'HA') as ha, \
             patch.object(g.core, 'profile', return_value={'services':[], 'home_slug':'test-home','va_slug':'test-va','tv_slug':'test-tv'}), \
             patch.object(g.core, 'ask', side_effect=['test-home','test-va','test-tv','Test Echo']) as ask, \
             patch.object(g.core, 'yes', return_value=False), patch.object(g.core, 'build'), \
             patch.object(g, 'resolve_usb', return_value='USB'), patch.object(g, 'gather_apks'), \
             patch.object(g, 'write_handoff') as handoff, patch.object(g.subprocess, 'run'):
            self.assertTrue(g.run())
            ha.assert_not_called()
            self.assertEqual(ask.call_count, 4)
            cfg = handoff.call_args.args[1]
            self.assertNotIn('token', cfg)
            self.assertNotIn('password', cfg)
            self.assertNotIn('timezone', cfg)

    def test_wait_timeout_reports_boot_and_permissions_not_hacs(self):
        from unittest.mock import patch
        with patch.object(g.time, 'monotonic', side_effect=[0, 2]):
            with self.assertRaisesRegex(ValueError, 'permission dialogs'):
                g.wait_for_app('USB', timeout=1)

    def test_wait_checks_boot_then_reachable_app(self):
        from unittest.mock import patch, MagicMock
        with patch.object(g.subprocess, 'check_output', side_effect=['1\n','inet addr:192.0.2.1']), \
             patch.object(g.socket, 'create_connection', return_value=MagicMock()) as connect:
            g.wait_for_app('USB')
            connect.assert_called_once_with(('192.0.2.1', 26900), timeout=3)
