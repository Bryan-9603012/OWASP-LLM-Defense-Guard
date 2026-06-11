@echo off
setlocal EnableExtensions
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"
if exist "%SCRIPT_DIR%.venv\Scripts\activate.bat" call "%SCRIPT_DIR%.venv\Scripts\activate.bat"
python "%SCRIPT_DIR%semi_auto_ollama.py"
echo.
echo 按任意鍵關閉...
pause >nul
