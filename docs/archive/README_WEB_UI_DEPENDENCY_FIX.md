# v24.4.3 Web UI Dependency Fix

This build keeps the Web UI as a UI-only bridge to the official runner. It does not change attacks, skills, scoring, valid/invalid logic, or experiment behavior.

## Fixed

The startup scripts now force-install the stable official Windows NumPy wheel:

```text
numpy==2.3.5
```

This avoids the experimental MinGW-W64 NumPy build warning and the Windows crash code `0xC0000005` / `3221225477` observed when the official runner imports NumPy/Pandas.

## Use

Run `run_platform.bat` again from this version. The first startup may take longer because NumPy is reinstalled in the project `.venv`.
