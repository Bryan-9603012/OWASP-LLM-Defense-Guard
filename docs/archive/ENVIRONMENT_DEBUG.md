# Environment Debug Logic

## Entry points

- `install.bat`: Windows CMD entry point. Good for double-click or CMD usage.
- `install_and_run.ps1`: real installer logic.
- `test_ollama.bat`: test-only CMD entry point.
- `test_ollama.ps1`: real test logic.

## Recommended commands

Install Python dependencies only:

```bat
install.bat -NoRun
```

Install Ollama automatically, then stop before testing:

```bat
install.bat -InstallOllama -NoRun
```

Start Ollama in another CMD window, then stop before testing:

```bat
install.bat -StartOllama -NoRun
```

Full flow:

```bat
install.bat -InstallOllama -StartOllama
```

Test only:

```bat
test_ollama.bat
```

## Detection order

1. Required project files
2. Required output folders
3. Python host: `py -3`, then `python`
4. Virtual environment: `.venv\Scripts\python.exe` and `.venv\Scripts\pip.exe`
5. Python dependencies from `requirements.txt`
6. Ollama command
7. Optional Ollama install via official installer
8. Optional Ollama server start
9. Ollama API check at `http://127.0.0.1:11434/api/tags`
10. Optional benchmark runner

## Log files

- `logs\install_and_run_last.log`
- `logs\test_ollama_last.log`
