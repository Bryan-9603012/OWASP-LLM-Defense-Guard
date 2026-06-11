# v24.4.17 Web UI CSV Union Hard Fix

This version hardens `sg_platform/app.py::write_csv_rows()` so Web UI bridge aggregation never fails when official runner rows contain different enterprise/scoring fields across groups.

Fixes:
- Builds a union of all row keys, not only first-row keys.
- Preserves common columns first for readability.
- Normalizes each row before `DictWriter.writerow()`.
- Keeps `extrasaction="ignore"` and `restval=""` as a final safety net.

Important: after replacing files, fully stop the old Web UI server and restart `run_platform.bat`; otherwise the browser may still be connected to the old in-memory FastAPI process.
