#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

if [ -x ".venv/Scripts/python.exe" ]; then
  PYTHON=".venv/Scripts/python.exe"
else
  PYTHON=".venv/bin/python"
fi

"$PYTHON" - <<'PY'
import sys
print('Using Python', sys.version)
if sys.version_info < (3, 9):
    raise SystemExit('ERROR: This Web UI build requires Python 3.9 or newer.')
PY

echo "Installing Python 3.9-compatible dependencies..."
"$PYTHON" -m pip install --upgrade pip setuptools wheel
"$PYTHON" -m pip install -r requirements.txt

echo "Starting Web UI at http://127.0.0.1:8080"
"$PYTHON" -m uvicorn sg_platform.app:app --host 127.0.0.1 --port 8080 --reload
