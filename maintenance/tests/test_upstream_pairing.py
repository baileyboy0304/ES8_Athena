"""Arbitration trust boundaries and interruption-safe EDA key provisioning."""
import asyncio
import base64
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace as NS
import unittest
from unittest.mock import AsyncMock, Mock, patch


class Pairing(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        names = ['aioesphomeapi', 'homeassistant', 'homeassistant.components',
                 'homeassistant.components.tag', 'homeassistant.helpers',
                 'homeassistant.helpers.storage']
        modules = {n: ModuleType(n) for n in names}
        self.invalid = type('InvalidKey', (Exception,), {})
        self.factory = Mock()
        modules['aioesphomeapi'].APIClient = self.factory
        modules['aioesphomeapi'].InvalidEncryptionKeyAPIError = self.invalid
        modules['aioesphomeapi'].ZERO_NOISE_PSK = 'zero-key'
        self.scan = AsyncMock()
        modules['homeassistant.components.tag'].async_scan_tag = self.scan
        self.saved = None
        async def load(): return self.saved
        async def save(data): self.saved = data.copy()
        self.store = NS(async_load=AsyncMock(side_effect=load), async_save=AsyncMock(side_effect=save))
        modules['homeassistant.helpers.storage'].Store = Mock(return_value=self.store)
        self.patch = patch.dict(sys.modules, modules); self.patch.start(); self.addCleanup(self.patch.stop)
        path = Path(__file__).resolve().parents[2]/'VACAV/integration/custom_components/vaca_vision/upstream_pairing.py'
        spec = importlib.util.spec_from_file_location('pairing_test', path)
        self.m = importlib.util.module_from_spec(spec); spec.loader.exec_module(self.m)
        self.info = NS(project_name='hassmic.athena', mac_address='aa:bb', api_encryption_provisionable=True)
        self.cli = NS(connect=AsyncMock(), device_info=AsyncMock(return_value=self.info),
                      disconnect=AsyncMock(), noise_encryption_set_key=AsyncMock(return_value=True),
                      send_home_assistant_state=Mock())
        self.factory.return_value = self.cli
        self.values = {'host':'192.0.2.1', 'eda_mac':'aa:bb'}
        self.hass = NS(data={}, states=NS(get=Mock(return_value=NS(state='timestamp'))))

    async def test_key_is_persisted_before_device_accepts_it_and_reused(self):
        async def set_key(key):
            self.assertIsNotNone(self.saved)
            self.assertFalse(self.saved['confirmed'])
            self.assertEqual(key, self.saved["key"].encode("ascii"))
            self.assertEqual(len(base64.b64decode(key, validate=True)), 32)
            return True
        self.cli.noise_encryption_set_key.side_effect = set_key
        result = await self.m.authenticated_values(self.hass, self.values)
        self.assertTrue(self.saved['confirmed'])
        self.assertEqual(self.factory.call_args.kwargs['noise_psk'], 'zero-key')
        again = await self.m.authenticated_values(self.hass, self.values)
        self.assertEqual(result, again)
        self.assertEqual(self.factory.call_count, 1)

    async def test_concurrent_setup_uses_one_key(self):
        async def connect():
            await asyncio.sleep(0)
        self.cli.connect.side_effect = connect
        first, second = await asyncio.gather(
            self.m.authenticated_values(self.hass, self.values),
            self.m.authenticated_values(self.hass, self.values))
        self.assertEqual(first['eda_noise_psk'], second['eda_noise_psk'])
        self.cli.noise_encryption_set_key.assert_awaited_once()

    async def test_supplied_key_is_not_rotated(self):
        values = {**self.values, 'eda_noise_psk':'owner-key'}
        self.assertEqual(await self.m.authenticated_values(self.hass, values), values)
        self.factory.assert_not_called()

    async def test_wrong_device_is_never_provisioned(self):
        self.info.mac_address = 'cc:dd'
        with self.assertRaisesRegex(ValueError, 'identity_changed'):
            await self.m.authenticated_values(self.hass, self.values)
        self.cli.noise_encryption_set_key.assert_not_awaited()
        self.store.async_save.assert_not_awaited()

    async def test_interruption_after_device_acceptance_recovers_saved_key(self):
        self.saved = {'key':'saved-key','mac':'aa:bb','confirmed':False}
        result = await self.m.authenticated_values(self.hass, self.values)
        self.assertEqual(result['eda_noise_psk'], 'saved-key')
        self.assertTrue(self.saved['confirmed'])
        self.cli.noise_encryption_set_key.assert_not_awaited()

    async def test_interruption_before_key_acceptance_reuses_pending_key(self):
        self.saved = {'key':base64.b64encode(b'x'*32).decode(),
                      'mac':'aa:bb','confirmed':False}
        rejected = NS(connect=AsyncMock(side_effect=self.invalid), disconnect=AsyncMock())
        self.factory.side_effect = [rejected, self.cli]
        result = await self.m.authenticated_values(self.hass, self.values)
        self.assertEqual(result['eda_noise_psk'], self.saved['key'])
        self.cli.noise_encryption_set_key.assert_awaited_once_with(self.saved['key'].encode())
        self.assertTrue(self.saved['confirmed'])

    async def test_confirmed_key_never_reprovisions_device(self):
        self.saved = {'key':'confirmed-key','mac':'aa:bb','confirmed':True}
        result = await self.m.authenticated_values(self.hass, self.values)
        self.assertEqual(result['eda_noise_psk'],'confirmed-key')
        self.factory.assert_not_called()

    async def test_network_error_never_falls_back_or_rotates(self):
        self.saved = {'key':'saved-key','mac':'aa:bb','confirmed':False}
        self.cli.connect.side_effect = TimeoutError
        with self.assertRaises(TimeoutError):
            await self.m.authenticated_values(self.hass, self.values)
        self.assertEqual(self.factory.call_count, 1)
        self.cli.noise_encryption_set_key.assert_not_awaited()

    async def test_bridge_rejects_general_actions_and_unrelated_states(self):
        tasks = []
        bridge = self.m.ArbitrationTags(self.hass, self.cli, 'device', tasks.append)
        tag = 'hassmic_' + 'a'*64
        valid = dict(service='esphome.tag_scanned',is_event=True,data={'tag_id':tag},data_template={},variables={})
        for changes in ({'service':'light.turn_on'}, {'is_event':False},
                        {'data':{'tag_id':'unrelated'}}, {'variables':{'x':'y'}}):
            bridge.on_action(NS(**{**valid, **changes}))
        self.assertEqual(tasks, [])
        bridge.on_action(NS(**valid)); await tasks.pop()
        self.scan.assert_awaited_once_with(self.hass, tag, 'device')
        for entity, attr in [('sensor.private',None), ('tag.unrelated',None), ('tag.'+tag,'secret')]:
            bridge.on_state(entity,attr)
        self.cli.send_home_assistant_state.assert_not_called()
        bridge.on_state('tag.'+tag)
        self.cli.send_home_assistant_state.assert_called_once_with('tag.'+tag,None,'timestamp')
        bridge.close(); bridge.on_action(NS(**valid)); bridge.on_state('tag.'+tag)
        self.assertEqual(tasks,[])
        self.assertEqual(self.cli.send_home_assistant_state.call_count,1)
