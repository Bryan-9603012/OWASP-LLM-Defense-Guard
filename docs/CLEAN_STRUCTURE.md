# Clean Project Structure

This cleaned package keeps the v25.6 defense / guard pipeline as the main project and moves historical notes, old outputs, and ad-hoc files away from the root folder.

## Main Entry Points

| File | Purpose |
|---|---|
| `README.md` | Project overview and normal usage. |
| `QUICK_START.md` | Fast start guide. |
| `semi_auto_ollama.py` | Main interactive launcher. |
| `src/run_benchmark.py` | Benchmark runner. |
| `sg_platform/app.py` | Streamlit / web dashboard entry. |
| `run_smoke_test.bat` | Smoke test helper. |

## Folder Layout

```text
LLM-Defense-Guard/
├── attacks/                 # attack sets used to evaluate defenses
├── configs/                 # action/data/model/automation configuration
├── data/                    # synthetic protected data and benign prompts
├── defenses/                # defense modes, skill profiles, custom rules
├── docs/
│   ├── archive/             # historical patch notes and old design notes
│   ├── architecture.md
│   └── demo_script.md
├── enterprise_guard/        # protected asset helpers
├── logs/                    # runtime logs, clean by default
├── prompts/                 # system prompt templates
├── reports/                 # generated reports, clean by default
├── results/                 # generated raw result CSVs, clean by default
├── scripts/                 # helper scripts and archived test scripts
├── sg_platform/             # dashboard / web UI
├── src/                     # core benchmark, guards, scoring, reporting
├── tests/                   # pytest tests
├── tools/                   # validation and asset management tools
├── semi_auto_ollama.py
├── run.bat / run.ps1 / run.sh
├── install.bat
└── requirements.txt
```

## Path Changes

| Old Path | New Path |
|---|---|
| `automation_config.json` | `configs/automation_config.json` |
| `model_groups.json` | `configs/model_groups.json` |
| `model_list.txt` | `configs/model_list.txt` |
| top-level patch notes | `docs/archive/` |
| `check.py` | `tools/check.py` |
| `test_*.bat`, `test_*.ps1` | `scripts/archive/` |

Code paths were updated for the moved config/model files.

## Cleaned Outputs

The following folders are intentionally clean in this package:

- `logs/`
- `reports/`
- `results/`

They contain only `.gitkeep` placeholders. New benchmark runs will regenerate outputs.
