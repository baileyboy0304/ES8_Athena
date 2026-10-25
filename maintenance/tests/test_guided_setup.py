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
    setUp = Readiness.setUp
    def test_read_only_mode_never_installs_or_accesses_usb(self):
        from unittest.mock import Mock, patch
        ha=Mock()
        ha.call.side_effect=lambda kind: {'get_config':{'components':['view_assist']},
            'get_states':[dict(v,entity_id=k) for k,v in self.states.items()],
            'config/entity_registry/list':[dict(v,entity_id=k) for k,v in self.registry.items()]}[kind]
        with patch.object(g.core,'verify'), patch.object(g.core,'HA',return_value=ha), \
             patch.object(g.core,'ask',return_value='http://ha.local:8123'), \
             patch.object(g.getpass,'getpass',return_value='test-token'), \
             patch.object(g.core,'settings',return_value=self.cfg), \
             patch.object(g,'select',return_value='sensor.va'), \
             patch.object(g,'resolve_usb') as usb, patch.object(g.core,'deploy_dashboards') as deploy:
            self.assertTrue(g.run(check_only=True))
            usb.assert_not_called(); deploy.assert_not_called()
            self.states['assist_satellite.es8']['state']='unavailable'
            self.assertFalse(g.run(check_only=True))
            deploy.assert_not_called()


if __name__ == "__main__": unittest.main()
