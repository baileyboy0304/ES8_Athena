"""Provide a pinned offline keyboard after EDA removes Athena's stock IME."""
import hashlib
from pathlib import Path
import time
from urllib.request import urlopen

COMPONENT = 'rkr.simplekeyboard.inputmethod/.latin.LatinIME'
URL = 'https://github.com/rkkr/simple-keyboard/releases/download/149/app-release.apk'
SHA256 = '7914e9aaac823667c601b1143d2da6f221398c41a8bb63f48a9c9d46dce0d0a2'


def available(shell):
    return set(shell('ime list -a -s').splitlines())


def needs_keyboard(shell):
    current = shell('settings get secure default_input_method')
    return current not in available(shell)


def prepare(root):
    path = Path(root) / 'installation-data/keyboard/simple-keyboard-6.8.apk'
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with urlopen(URL, timeout=60) as response:
            data = response.read(2 * 1024 * 1024)
        if hashlib.sha256(data).hexdigest() != SHA256:
            raise RuntimeError('Simple Keyboard download checksum mismatch; nothing installed')
        path.write_bytes(data)
    if hashlib.sha256(path.read_bytes()).hexdigest() != SHA256:
        raise RuntimeError('Simple Keyboard checksum mismatch; remove the incorrect cached APK and retry')
    return path


def install(adb, shell, path):
    if COMPONENT not in available(shell):
        result = adb('install', '-r', str(path))
        if 'Success' not in result:
            raise RuntimeError('Simple Keyboard installation failed: ' + result)
        for _ in range(10):
            if COMPONENT in available(shell):
                break
            time.sleep(0.5)
        else:
            raise RuntimeError('Installed keyboard input method was not registered')
    shell('ime enable ' + COMPONENT)
    shell('ime set ' + COMPONENT)
    shell('settings put secure show_ime_with_hard_keyboard 1')
    if shell('settings get secure default_input_method') != COMPONENT:
        raise RuntimeError('Keyboard selection did not persist')
    print('Simple Keyboard 6.8 ready. Check it opens when tapping a sign-in field.')
