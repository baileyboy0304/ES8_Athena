# Package maintenance

These files support verification and development. Normal installation only needs
`python install.py verify`; do not regenerate checksums to bypass a failed check.

| File | Purpose |
|---|---|
| `source-versions.json` | Records the exact upstream checkers commit and bundled VACAV versions |
| `checksums.json` | SHA256 fingerprints of bundled VACAV/device files; detects missing or changed files |
| `update-checksums.py` | Regenerates those fingerprints after an intentional, reviewed package change |
| `tests/` | Small offline installer checks; no device or HA access |

Maintainer commands, run from the repository root:

```sh
python -B maintenance/update-checksums.py
python -B install.py verify
python -B -m unittest discover -s maintenance/tests -q
```

The upstream checkout is verified separately by its Git commit and tracked-file
status. Checksums detect changes; they do not authenticate a publisher.
