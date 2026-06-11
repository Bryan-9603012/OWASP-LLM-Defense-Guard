# Double-click Debug Guide

If the terminal opens and closes immediately, it usually means the batch file exited after an error.
This version keeps the terminal open and writes logs.

## Files

- `install_and_run.bat` writes log to `logs/install_and_run_last.log`
- `test_ollama.bat` writes log to `logs/test_ollama_last.log`

## Recommended test order

```powershell
.\install_and_run.bat -NoRun
```

Then open another terminal:

```powershell
ollama serve
```

Then run:

```powershell
.\test_ollama.bat
```

## If Windows blocks the file

Right-click the zip file or `.bat` file:

1. Properties
2. Check `Unblock` if it appears
3. Apply
4. Run again

## If PowerShell execution policy blocks it

The `.bat` already uses:

```powershell
-ExecutionPolicy Bypass
```

So normally you do not need to change system policy.
