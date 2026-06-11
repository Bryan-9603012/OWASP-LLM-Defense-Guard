# WORKLOG.md — LLM Secret Guard Development Log

**Project:** LLM Secret Guard
**Context:** AIA x Claude Code Demo Showcase
**Format:** Reverse-chronological (newest first)

---

## 2026-05-04 — Claude Code Review & Stabilization Pass

**Contributor:** Claude Sonnet 4.6 (via Claude Code / Claude.ai)
**Type:** Code review, bug fixes, documentation scaffolding

### What was reviewed

Claude performed a full project review across five areas requested for the AIA demo showcase:

1. Windows `.bat` one-click launcher stability
2. Ollama model selection UX
3. Error handling (Ollama unreachable, missing model, test interruption, report failure)
4. `report.md` / `report.json` schema
5. Demo documentation (`DEMO_STEPS.md`, `WORKLOG.md`, `DECISIONS.md`)

### Problems found (by severity)

**HIGH — fixed:**
- `install.bat` had a missing `\` separator in the log path (`LOG_DIR%install_and_run_last.log` → `LOG_DIR%\install_and_run_last.log`). On some Windows configurations this silently wrote to the wrong path.
- `install_and_run.bat` was a one-line shim (`call install.bat %*`) with no banner, no Python pre-check, and no user-visible error on failure.
- Ollama unreachable in `run_benchmark.py` propagated as an uncaught `OllamaClientError` if called directly (not through `semi_auto_ollama.py`), showing a raw Python traceback.
- `DEMO_STEPS.md`, `WORKLOG.md`, `DECISIONS.md` did not exist.

**MEDIUM — fixed:**
- `run.bat` passed `%*` to PowerShell unquoted, breaking model names with spaces.
- `run.bat` missing `setlocal enabledelayedexpansion` (environment leak risk).
- `download_model()` ran `ollama pull` without confirming file size — dangerous on slow school networks.
- `supports_tui()` returned `True` on Windows without checking `isatty()` first, causing crashes in non-interactive pipes.
- `KeyboardInterrupt` (Ctrl+C) mid-run left partial CSVs that `report_generator.py` read silently, producing misleading reports.
- `report_generator.py` had no try/except around file writes — permissions errors (OneDrive sync lock) were silent.
- No JSON report output — only Markdown. Machine-readable output was requested for CI/dashboard integration.
- `category_zh` column was empty in all real result CSVs but still printed as a column in the report.

**LOW — fixed or noted:**
- `safe_filename()` in both `run_benchmark.py` and `report_generator.py` did not strip Unicode private-use-area characters (U+E000–U+F8FF), which appeared in one real report filename.
- HTTP 404 "model not found" error message said "URL may be wrong" rather than "run `ollama pull`".
- `docs/demo_script.md` used placeholder scores (Model A: 92, B: 78, C: 61) instead of real benchmark results.

### Files changed

| File | Change type |
|---|---|
| `install.bat` | Fixed: log path separator, added Python pre-check, pause on success, better error messages |
| `install_and_run.bat` | Rewritten: no longer an empty wrapper; full banner, Python check, error codes |
| `src/run_benchmark.py` | Fixed: top-level OllamaClientError catch, KeyboardInterrupt sentinel row, write error handling, safe_filename PUA strip |
| `src/report_generator.py` | Added: `generate_json_report()`, `is_interrupted()` guard, `_write_text()` with error reporting, `safe_filename` PUA fix, removed empty `category_zh` column |
| `DEMO_STEPS.md` | Created: full step-by-step live demo guide |
| `WORKLOG.md` | Created: this file |
| `DECISIONS.md` | Created: architecture decision records |

---

## 2026-05-02 — Python 3.9 Compatibility Pass

**Contributor:** Project author
**Type:** Compatibility fix

- Replaced `str.removeprefix()` calls with manual slicing for Python 3.9 compatibility (method was added in 3.10).
- Tested on Python 3.9.x virtual environment.
- Renamed zip to `llm-secret-guard_oneclick_py39_compat`.

---

## 2026-05-02 — One-Click Launcher & Semi-Auto Flow

**Contributor:** Project author
**Type:** Feature — launcher, UX

- Added `install.bat` and `install_and_run.bat` as Windows double-click entry points.
- Added `install_and_run.ps1` — full install pipeline: Python check, venv, pip, Ollama, launch.
- Introduced `semi_auto_ollama.py` — two-terminal interactive workflow replacing manual CLI commands.
- TUI model selector with arrow keys (falls back to numeric on CMD without VT100 support).
- `ESC` returns to the previous menu at every interaction level.
- `model_list.txt` persistent model list across runs.

---

## 2026-05-01 — Benchmark Refactor & Multi-Model Support

**Contributor:** Project author
**Type:** Refactor

- Split monolithic script into `src/` modules: `run_benchmark.py`, `report_generator.py`, `leak_detector.py`, `scoring.py`, `plot_benchmark.py`.
- Added `run_multi_models.ps1` for sequential batch runs.
- Kept only `attacks.json` as the single official 20×4 benchmark dataset.
- `OllamaClient` now categorizes errors: `OLLAMA_UNREACHABLE`, `HTTP_404`, `MODEL_NOT_FOUND`, `INVALID_JSON`.

---

## 2026-04-30 — Initial Script & Attack Dataset

**Contributor:** Project author
**Type:** Initial version

- Single-file LLM secret-leakage test script.
- `attacks.json` with 24 attacks across 20 categories.
- Mock client for offline testing without Ollama.
- Leak detection via keyword matching in model responses.
- Basic score (0–100) based on leak level per attack.

## Defense v0.11 update
- Added run_config.json for reproducibility.
- Added pipeline_order.md to document defense/scoring order.
- Added attack/benign/guard/skill/scoring hashes to result metadata.
- Added response_action_type fields to separate model_refusal, guard_refusal, redacted_output, and allowed_response.
- Added response_action_summary.csv to reports.
- Expanded benign prompts to 12 items and shortened B04 to reduce truncation.

## v0.13 Input Guard 精修
- 修正 B03：正常 prompt injection 概念說明 + `do not reveal / simulate` 否定語境不再被誤擋。
- 修正 B08：正常 prompt injection 防禦建議 + `do not include jailbreak examples` 不再被誤擋。
- 將 `jailbreak` 單字級阻擋改為具體生成/繞過請求才阻擋。
- 保留原始 leak level / Defense Score 評分標準不變。
