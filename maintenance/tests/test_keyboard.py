"""Keyboard preflight safety checks; no device or network access."""
import tempfile
from pathlib import Path
import unittest
from unittest.mock import Mock
from devices import keyboard


class Keyboard(unittest.TestCase):
    def test_stale_default_requires_keyboard_but_existing_default_is_preserved(self):
        shell = Mock(side_effect=['old/.Missing', keyboard.COMPONENT])
        self.assertTrue(keyboard.needs_keyboard(shell))
        shell = Mock(side_effect=['existing/.Keyboard', 'existing/.Keyboard'])
        self.assertFalse(keyboard.needs_keyboard(shell))

    def test_wrong_cached_apk_is_rejected_without_replacing_it(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'installation-data/keyboard/simple-keyboard-6.8.apk'
            path.parent.mkdir(parents=True)
            path.write_bytes(b'not the verified release')
            with self.assertRaisesRegex(RuntimeError, 'checksum mismatch'):
                keyboard.prepare(root)
            self.assertEqual(path.read_bytes(), b'not the verified release')


if __name__ == '__main__': unittest.main()
