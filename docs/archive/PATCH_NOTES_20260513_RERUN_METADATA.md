# Patch Notes — Rerun List and Metadata Completion

Date: 2026-05-13

## Fixed

### 1. `rerun_list.csv` completion

`src/report_generator.py` now lists rerun candidates when any of the following happens for the same formal case:

```text
model + base_attack_id + prompt_style
```

Rules:

- `max(leak_level) - min(leak_level) >= 2`
- `std_score >= 30`
- at least one invalid sample exists, such as:
  - `TRUNCATED_RESPONSE`
  - `EMPTY_RESPONSE`
  - `OLLAMA_UNREACHABLE`
  - `OLLAMA_500`
  - `TIMEOUT`
  - `JSON_PARSE_ERROR`
  - `SCORING_ERROR`

This prevents invalid samples from being silently ignored.

### 2. Stable `rerun_list.csv` header

Even when no inconsistent case exists, `rerun_list.csv` now keeps a stable CSV header instead of becoming a nearly empty file.

Columns:

```text
model,attack_id,base_attack_id,prompt_style,reason,n_runs,valid_cases,invalid_cases,error_types,machine_ids,run_ids,leak_levels,scores,level_gap,std_score
```

### 3. Better model metadata collection

`src/run_benchmark.py` now collects Ollama model metadata more robustly:

- `model_digest` from `ollama list`
- `model_parameter_size` from `ollama show --json` or `ollama show`
- `model_quantization` from `ollama show --json` or `ollama show`

### 4. Better machine metadata collection

`ram_gb` is now collected without requiring `psutil`:

- first tries `psutil`
- then Linux / WSL `/proc/meminfo`
- then Windows `wmic`

Also records:

```text
hostname
```

## Important note

Old CSV files that already have blank `model_digest`, `model_parameter_size`, or `ram_gb` cannot be perfectly recovered on another machine. New runs will record these fields correctly at execution time.
