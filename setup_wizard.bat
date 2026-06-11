@echo off
setlocal EnableExtensions
chcp 65001 >nul
title LLM Secret Guard - Setup Wizard
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

if not exist "%SCRIPT_DIR%setup_wizard.ps1" (
  echo [FAIL] Missing setup_wizard.ps1
  echo Press any key to close...
  pause >nul
  exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%setup_wizard.ps1"
set "RC=%ERRORLEVEL%"
echo.
echo ========================================
echo Wizard finished with exit code: %RC%
echo ========================================
echo Press any key to close...
pause >nul
exit /b %RC%
