@echo off
setlocal
cd /d "%~dp0"

REM Python 3.9 compatibility launcher.
REM This project supports Python 3.9+ with pinned compatible dependencies.

if not exist .venv (
  py -3.9 -m venv .venv 2>nul
  if errorlevel 1 (
    py -m venv .venv 2>nul
  )
  if errorlevel 1 (
    python -m venv .venv
  )
)

set "PYTHON=.venv\Scripts\python.exe"

"%PYTHON%" -c "import sys; print('Using Python', sys.version); raise SystemExit(0 if sys.version_info >= (3,9) else 1)"
if errorlevel 1 (
  echo ERROR: This Web UI build requires Python 3.9 or newer.
  echo Please recreate .venv with Python 3.9+ or install Python 3.11.
  pause
  exit /b 1
)

echo Installing Python 3.9-compatible dependencies...
"%PYTHON%" -m pip install --upgrade pip setuptools wheel
"%PYTHON%" -m pip install -r requirements.txt

echo Starting Web UI at http://0.0.0.0:8080
"%PYTHON%" -m uvicorn sg_platform.app:app --host 0.0.0.0 --port 8080 --reload
pause
