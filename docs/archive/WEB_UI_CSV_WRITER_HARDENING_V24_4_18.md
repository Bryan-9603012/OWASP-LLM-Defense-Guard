# v24.4.18 Web UI CSV Writer Hardening Fix

This build hardens CSV writing in three places:

- `sg_platform/app.py` Web UI merged official-run output writer.
- `src/run_benchmark.py` official runner `write_csv()`.
- `src/report_generator.py` report CSV writer.

Why: rows from different defense groups may contain different enterprise/scoring fields.
All writers now build union fieldnames and normalize every row before writing.

Important: after updating, fully stop the old Web UI process with Ctrl+C and restart `run_platform.bat`.
