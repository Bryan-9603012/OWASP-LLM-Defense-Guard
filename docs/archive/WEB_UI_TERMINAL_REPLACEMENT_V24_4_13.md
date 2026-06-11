# v24.4.13 Web UI Terminal-Replacement Runner

This version restores Web UI parameter submission, but removes the old simplified Web experiment runner.

## Design rule

The Web UI is only a terminal replacement:

1. User selects model, attack scope, language, G groups, skill profile, and protected asset in Web UI.
2. Web UI converts those selections into `src/run_benchmark.py` CLI arguments.
3. `src/run_benchmark.py` performs the official experiment, scoring, invalid handling, prompt tracing, and report generation.
4. Web UI reloads the resulting `raw_results_all.csv` / reports and displays them.

The Web UI does **not** implement a separate attack runner, leak scorer, defense logic, or invalid-sample logic.

## Main changes

- `/experiments` now provides an official-runner form.
- `/experiments/start` creates a UI job and delegates to `src/run_benchmark.py`.
- Formal G groups exposed in UI: G0, G1, G5, G6, G7.
- Web UI passes selected `protected_asset_id` to the official runner using `--protected-assets` and `--protected-asset-id`.
- Added default `customer_profile_001` synthetic customer asset.
- Job status page shows delegated official-runner progress and loads report rows after completion.

## Recommended usage

```bat
run_platform.bat
```

Then open the Web UI, go to **Run Official Experiment**, select parameters, start the official runner, and inspect results in Overview / Defense Groups / Traces / Reports.
