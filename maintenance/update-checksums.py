"""Maintainer helper after intentionally changing bundled component files."""
from pathlib import Path
import hashlib
import json
import subprocess

root = Path(__file__).resolve().parents[1]
entries = []
for folder in ('VACAV', 'devices'):
    directory = root / folder
    # Hash shipped files, never local Gradle caches or APK build intermediates.
    output = subprocess.check_output(['git', '-C', str(directory), 'ls-files', '-z'], text=True)
    for name in sorted(filter(None, output.split('\0'))):
        p = directory / name
        if p.is_file():
            entries.append({'path': p.relative_to(root).as_posix(), 'bytes': p.stat().st_size,
                            'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
(root / 'maintenance/checksums.json').write_text(json.dumps(entries, indent=2) + '\n', encoding='utf-8', newline='\n')
print('Recorded', len(entries), 'component hashes')
