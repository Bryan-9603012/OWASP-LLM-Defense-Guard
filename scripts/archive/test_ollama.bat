@echo off
setlocal EnableExtensions
set "SCRIPT_DIR=%~dp0"
set "LOG_DIR=%SCRIPT_DIR%logs"
set "LOG_FILE=%LOG_DIR%test_ollama_last.log"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
cd /d "%SCRIPT_DIR%"

echo ========================================
echo LLM Secret Guard - Test Ollama
echo Project: %SCRIPT_DIR%
echo Log: %LOG_FILE%
echo ========================================
echo.

where powershell >nul 2>nul
if errorlevel 1 (
    echo [FAIL] PowerShell not found.
    pause
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%test_ollama.ps1" %* > "%LOG_FILE%" 2>&1
set "RC=%ERRORLEVEL%"

type "%LOG_FILE%"

echo.
echo ========================================
if not "%RC%"=="0" (
    echo [FAIL] test_ollama failed. Exit code: %RC%
    echo Log saved to: %LOG_FILE%
) else (
    echo [OK] test_ollama finished successfully.
    echo Log saved to: %LOG_FILE%
)
echo ========================================
echo.
echo Press any key to close this window...
pause >nul
exit /b %RC%
