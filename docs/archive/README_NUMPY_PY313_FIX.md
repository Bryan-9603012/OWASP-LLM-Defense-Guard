# NumPy Python 3.13 Fix

This build pins NumPy to `numpy==2.3.5` because the project venv may run on Python 3.13.

`numpy==1.26.4` does not provide a compatible wheel for Python 3.13, so pip reports `No matching distribution found`.

The Web UI still only acts as a UI bridge to the official runner; no experiment logic, scoring, attacks, skill, custom asset, or invalid-sample handling is changed.
