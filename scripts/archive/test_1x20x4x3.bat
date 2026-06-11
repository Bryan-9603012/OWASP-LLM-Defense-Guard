@echo off
setlocal EnableExtensions EnableDelayedExpansion
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"
set "PYTHON_EXE=python"
if exist "%SCRIPT_DIR%.venv\Scripts\python.exe" set "PYTHON_EXE=%SCRIPT_DIR%.venv\Scripts\python.exe"

echo ================================================
echo  LLM Secret Guard - 1 x 20 x 4 x 3 Test
echo ================================================
echo.
set /p MODEL_NAME=Enter model name ^(example: qwen2.5:7b, qwen2.5-coder:14b, mock^): 
if "%MODEL_NAME%"=="" set "MODEL_NAME=mock"
if /i "%MODEL_NAME%"=="mock" (
    set "MODEL_ARG=mock"
) else (
    echo %MODEL_NAME% | findstr /B /I "ollama:" >nul
    if errorlevel 1 (set "MODEL_ARG=ollama:%MODEL_NAME%") else (set "MODEL_ARG=%MODEL_NAME%")
)
set /p MACHINE_ID=Enter machine id ^(default PC01^): 
if "%MACHINE_ID%"=="" set "MACHINE_ID=PC01"

echo.
echo [RUN] %MODEL_ARG% on %MACHINE_ID%
"%PYTHON_EXE%" "%SCRIPT_DIR%src\run_benchmark.py" --model "%MODEL_ARG%" --attacks "attacks\attacks.json" --styles all --machine-id "%MACHINE_ID%" --runs 3 --limit-base-attacks 20 --temperature 0 --top-p 1 --top-k 40 --num-ctx 4096 --max-tokens 300 --seed 42
set "RC=%ERRORLEVEL%"
echo.
echo Exit code: %RC%
echo Press any key to close...
pause >nul
exit /b %RC%
