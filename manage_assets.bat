@echo off
chcp 65001 >nul
python tools\manage_protected_assets.py configs\protected_assets.json
pause
