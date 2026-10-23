"""Small offline checks of cross-profile output; no HA/ADB/network calls."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

REAL = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('installer', REAL / 'install.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class Dashboards(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        m.ROOT = Path(self.tmp.name)
        for folder in ('devices',):
            shutil.copytree(REAL / folder, m.ROOT / folder)
    def tearDown(self):
        m.ROOT = REAL
        self.tmp.cleanup()
    def generate(self, name, selected):
        p = m.profile(name)
        c = dict(profile=name, services=selected, va_entity='sensor.test_display',
                 weather_entity='weather.test', music_path='/test-ma',
                 **{k:p[k] for k in ('va_slug','home_slug','tv_slug')})
        m.save(m.ROOT / 'installation-data/choices' / (name + '.json'), c)
        m.build(name)
        out = m.ROOT / 'installation-data/generated' / name
        return {k: m.read(out / (k + '.json')) for k in ('va','home','tv')}, out
    def test_es8_all_services_and_standard_views(self):
        data, out = self.generate('es8-gen2', ['netflix','iplayer','itvx','apple_tv'])
        self.assertEqual({v['path'] for v in data['va']['views']}, {'clock','weather',*m.STANDARD})
        tiles = data['tv']['views'][0]['cards'][1]['cards']
        self.assertEqual(len(tiles), 4)
        self.assertIn('B.fullscreen=true', tiles[-1]['tap_action']['url_path'])
        self.assertIn('com.netflix.mediaclient.echo', (out/'android.conf').read_text())
    def test_no_services_no_exceptions(self):
        data, out = self.generate('es8-gen2', [])
        self.assertEqual((out/'android.conf').read_text(), 'web_packages=\n')
        self.assertEqual(data['tv']['views'][0]['cards'][1]['type'], 'markdown')
    def test_portal_paths_are_not_double_substituted(self):
        data, out = self.generate('portal_plus_gen_2', ['netflix','apple_tv','sstv'])
        text = json.dumps(data)
        self.assertNotIn('portal-portal', text)
        self.assertNotIn('@@', text)
        self.assertNotIn('com.netflix.mediaclient.echo', text)
        self.assertIn('com.apple.atve.androidtv.appletv', text)
        self.assertIn('/view-assist-portal/clock', text)
        self.assertNotIn('sensor.portal_study', text)
    def test_navigation_and_home_three_buttons(self):
        data, _ = self.generate('es8-gen2', ['iplayer'])
        self.assertEqual(len(data['home']['views'][0]['cards'][0]['cards']),3)
        for view in data['va']['views']:
            if view['path']=='clock': nav=view['cards'][0]['custom_fields']['heading']['card']
            else: nav=view['cards'][0]['cards'][0]
            self.assertEqual([x['name'] for x in nav['cards']], ['Home','TV'])

if __name__ == '__main__': unittest.main()
