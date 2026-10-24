"""Regression checks for MA exposure without requiring a running HA instance."""
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

class Exposure(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        names = ['homeassistant', 'homeassistant.components',
                 'homeassistant.components.media_player',
                 'homeassistant.components.music_assistant',
                 'homeassistant.components.music_assistant.helpers',
                 'homeassistant.exceptions', 'music_test', 'music_test.entity']
        modules = {n: ModuleType(n) for n in names}
        modules[names[2]].MediaPlayerEntity = type('MediaPlayerEntity', (), {})
        modules[names[2]].MediaPlayerEntityFeature = SimpleNamespace()
        modules[names[5]].HomeAssistantError = RuntimeError
        class Overlay:
            def __init__(self, runtime, *args): self.runtime = runtime
        modules['music_test.entity'].OverlayEntity = Overlay
        self.player = SimpleNamespace(available=True)
        self.client = SimpleNamespace(
            players=SimpleNamespace(get=lambda player_id: self.player),
            config=SimpleNamespace(get_player_config_value=AsyncMock(return_value=True)))
        modules[names[4]].get_music_assistant_client = lambda *a: self.client
        self.modules = patch.dict(sys.modules, modules)
        self.modules.start()
        self.addCleanup(self.modules.stop)
        path = Path(__file__).resolve().parents[2] / 'VACAV/integration/custom_components/vaca_vision/upstream_music.py'
        spec = importlib.util.spec_from_file_location('music_test.upstream_music', path)
        self.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.m)
        self.hass = SimpleNamespace(config_entries=SimpleNamespace(
            async_get_entry=lambda _: SimpleNamespace(domain='music_assistant', entry_id='ma')))
        self.values = {'ma_entry_id': 'ma', 'ma_player_id': 'player'}

    async def test_exposed_player_is_valid_and_proxy_stays_available(self):
        await self.m.validate_music(self.hass, self.values)
        entity = self.m.UpstreamMusic(SimpleNamespace(values=self.values))
        entity.hass = self.hass
        self.assertTrue(entity.available)
        self.player.available = False
        self.assertFalse(entity.available)

    async def test_unexposed_player_requires_fix_before_saving(self):
        self.client.config.get_player_config_value.return_value = False
        with self.assertRaisesRegex(ValueError, 'ma_player_not_exposed'):
            await self.m.validate_music(self.hass, self.values)

    async def test_missing_player_rejected(self):
        self.player = None
        with self.assertRaisesRegex(ValueError, 'ma_player_missing'):
            await self.m.validate_music(self.hass, self.values)
