@echo off
setlocal
cd /d "%~dp0"
python tools\smoke_test.py
pause
