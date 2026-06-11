# v24.4.14 Python 3.9 Compatibility Fix

This build removes the Python 3.11+ dependency issue caused by `numpy==2.3.5` and uses Python 3.9-compatible dependency ranges.

## Changed

- `numpy==2.3.5` -> `numpy>=1.26.4,<2.0`
- `matplotlib>=3.7,<3.9`
- Web UI dependencies are now included in `requirements.txt`
- `run_platform.bat`, `run_platform_lan.bat`, and `run_platform.sh` no longer force-install NumPy 2.3.5
- Added Python 3.9 runtime check
- Added future annotations compatibility where needed

## Recommended clean install on Windows

```bat
rmdir /s /q .venv
run_platform.bat
```

If Python 3.9.6 is your only Python version, this version is intended to work with it.
