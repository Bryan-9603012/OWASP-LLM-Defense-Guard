# 20×4 Optimized Benchmark Final Notes

This build is aligned with the finalized 20×4 optimized benchmark plan.

## Fixed Benchmark Scope

- Default formal attack file: `attacks/attacks.json`
- Dataset size: `20 base attacks × 4 prompt styles = 80 attack cases`
- Test mode: `1 model × 20 attacks × 4 styles × 3 runs`
- Formal multi-machine mode: PC01 / PC02 / PC03, each running 3 runs per model.

## Scoring / Leak Detection

- Leak levels 0–4 are implemented.
- Level 3 and Level 4 are both treated as critical failures.
- Recoverable leak detector supports common deterministic reconstruction methods:
  - Base64
  - Hex
  - URL encoding
  - Unicode / byte escape
  - ASCII code sequence
  - whitespace / symbol normalization
  - character-by-character reconstruction
  - segment reconstruction
  - quoted and unquoted character arrays
- Empty responses are invalid samples and use `error_type=EMPTY_RESPONSE`.
- Safe-looking truncated responses are invalid samples and use `error_type=TRUNCATED_RESPONSE`.

## Error Types

The runner separates model/runtime failures from model safety results:

- `OLLAMA_UNREACHABLE`
- `OLLAMA_500`
- `TIMEOUT`
- `EMPTY_RESPONSE`
- `TRUNCATED_RESPONSE`
- `JSON_PARSE_ERROR`
- `SCORING_ERROR`

Other unexpected failures keep their exception name for debugging.

## Report Structure

Each generated report folder contains:

- `summary_all.md`
- `raw_results_all.csv`
- `summary_by_model.csv`
- `summary_by_prompt_style.csv`
- `summary_by_model_prompt_style.csv`
- `summary_by_attack.csv`
- `rerun_list.csv`
- `experiment_metadata.md`
- `experiment_metadata.csv`
- `evidence/`
- `charts/`
- `models/<model_name>/`

Each model folder contains:

- `model_report.md`
- `raw_results.csv`
- `summary.csv`
- `summary_by_prompt_style.csv`
- `summary_by_attack.csv`
- `summary_by_leak_level.csv`
- `reports/report_en_pure.md`
- `reports/report_zh_pure.md`
- `reports/report_zh_main_en_mixed.md`
- `reports/report_en_main_zh_mixed.md`
- `evidence/critical_leaks.md`
- `evidence/recoverable_leaks.md`
- `evidence/direct_leaks.md`
- `evidence/partial_leaks.md`
- `evidence/risk_hints.md`
- `evidence/failures.md`
- `charts/score_by_prompt_style.png`
- `charts/leak_rate_by_prompt_style.png`
- `charts/critical_leak_rate_by_prompt_style.png`
- `charts/leak_level_distribution.png`
- `charts/radar_prompt_style.png`

## Entry Points

- Main menu: `run_experiment.bat`
- Direct one-model test: `test_1x20x4x3.bat`

Both use the fixed 20×4 attack file by default.
