# Web UI Dependency Note

This package uses the Web UI only as a replacement for the terminal menu. The experiment logic is still delegated to the original official runner:

```text
src/run_benchmark.py
```

The Web UI and official runner must use the same project virtual environment:

```text
.venv
```

`run_platform.bat`, `run_platform_lan.bat`, and `run_platform.sh` now install both:

- original runner dependencies from `requirements.txt`
- Web UI dependencies: `fastapi`, `uvicorn`, `jinja2`, `python-multipart`
- `requests`, required by the Ollama client used by the official runner

If you see `ModuleNotFoundError: No module named 'requests'`, restart the platform using `run_platform.bat` from this project folder. Do not install packages into another copy of the project.
