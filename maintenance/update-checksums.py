"""Maintainer helper after intentionally changing bundled component files."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parents[1]
entries = []
for folder in ('VACAV', 'devices'):
    for p in sorted((root / folder).rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc':
            entries.append({'path': p.relative_to(root).as_posix(), 'bytes': p.stat().st_size,
                            'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
(root / 'maintenance/checksums.json').write_text(json.dumps(entries, indent=2) + '\n', encoding='utf-8', newline='\n')
print('Recorded', len(entries), 'component hashes')
