#!/usr/bin/env bash
# Guided VACAVision setup after the upstream Echo Dot Assist installer.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if [[ $(uname -s) != Linux ]]; then
  echo 'Run this installer on your Linux PC with USB access.' >&2
  exit 1
fi
python_bin=''
for candidate in .venv/bin/python python3 python3.14 python3.13 python3.12 python3.11; do
  if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; sys.exit(sys.version_info < (3,11))' 2>/dev/null; then
    python_bin=$candidate
    break
  fi
done
if [[ -z $python_bin ]]; then
  echo 'Install Python 3.11 or newer and its venv package, then run ./setup.sh again.' >&2
  exit 1
fi
command -v adb >/dev/null || { echo 'Install Android platform-tools (adb), then run ./setup.sh again.' >&2; exit 1; }
if [[ $python_bin != .venv/bin/python ]]; then
  "$python_bin" -m venv .venv
fi
.venv/bin/python -m pip install --disable-pip-version-check -r requirements.txt
exec .venv/bin/python guided_setup.py "$@"
