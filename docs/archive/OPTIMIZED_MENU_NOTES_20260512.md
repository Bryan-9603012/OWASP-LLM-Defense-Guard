# Optimized Menu Patch Notes - 2026-05-12

This package is based on the uploaded `llm-secret-guard_llm02_32attacks_fix3_languagebars` version.

## Added / Updated

- `src/run_benchmark.py`
  - `--styles all|en_pure,zh_pure,zh_main_en_mixed,en_main_zh_mixed`
  - `--runs N`
  - `--machine-id PC01`
  - `--limit-base-attacks 20`
  - `--merge csv1 csv2 ...`
  - experiment metadata: model digest, Ollama version, hashes, machine info, inference params
  - per-attack context reset
  - raw CSV columns for prompt/response hash, recoverable leak, evidence, decoded value

- `src/leak_detector.py`
  - Level 0~4 scoring policy
  - recoverable leak detection: Base64, hex, URL, unicode/byte escape, ASCII code, character-by-character and segment reconstruction

- `src/scoring.py`
  - 100/75/50/0/0 scoring

- `src/report_generator.py`
  - summary_all.md
  - raw_results_all.csv
  - per-model folders under `reports/run_xxx/models/<model>/`
  - four style reports per model
  - evidence files
  - rerun_list.csv for inconsistent cases
  - experiment_metadata.md/csv

- `run_experiment.bat`
  - menu runner
  - Full Test asks for model name

- `test_1x20x4x3.bat`
  - direct 1 model x 20 attacks x 4 styles x 3 runs pilot/full test

## Recommended test command

```bat
test_1x20x4x3.bat
```

or:

```bat
python src\run_benchmark.py --model ollama:qwen2.5:7b --attacks attacks\attacks.json --styles all --machine-id PC01 --runs 3 --limit-base-attacks 20 --temperature 0 --top-p 1 --top-k 40 --num-ctx 4096 --max-tokens 300 --seed 42
```
