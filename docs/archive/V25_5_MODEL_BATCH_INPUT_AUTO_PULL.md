# V25.5 Model Batch Input & Auto Pull

## Purpose

This update makes the Web UI model selector more flexible for formal experiments:

- Users can select an installed model from the Ollama list.
- Users can manually type a single Ollama model name.
- Users can enter multiple models in batch mode.
- Missing models can be pulled automatically through Ollama before testing.
- Batch runs execute sequentially, not in parallel, to avoid local GPU/RAM overload.

## Web UI Changes

The **Model / Runtime Configuration** section now supports:

| Field | Description |
|---|---|
| Model Mode | `Single model` or `Batch models` |
| Installed Model | Dropdown populated from Ollama `/api/tags` when available |
| Manual Model | One custom model name such as `gemma3:12b` |
| Batch Models | One model per line, or comma-separated |
| Auto-pull missing models | Pull missing models before benchmark |
| Skip pull failures / missing models | Continue with available models instead of failing the whole job |

Recommended batch input format:

```text
gemma3:1b
gemma3:12b
llama3.1:8b
qwen2.5:7b
```

## Model Name Validation

The UI bridge validates model names before execution. Allowed characters are:

```text
A-Z a-z 0-9 . _ : / -
```

This avoids shell-injection style input while preserving normal Ollama naming.

## Preflight Flow

Before launching `src/run_benchmark.py`, the Web UI bridge now performs:

```text
1. Read requested model list
2. Query Ollama /api/tags
3. Identify missing models
4. Pull missing models when enabled
5. Write batch_model_status.csv
6. Run the official benchmark sequentially per model and defense group
```

## Output

Each Web-launched official job now writes:

```text
reports/web_official_requests/run_<timestamp>_<job>/batch_model_status.csv
```

Columns:

```text
model,installed_before,missing,auto_pull,pull_status,message
```

The job status page also shows the model preflight / pull status table.

## Scope Boundary

This update does **not** change:

- G0-G6 defense definitions
- scoring logic
- leak-level definitions
- attack datasets
- valid/invalid logic
- report calculation

It only improves Web UI model input, missing-model handling, and batch model orchestration.
