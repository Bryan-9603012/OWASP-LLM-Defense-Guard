# Current Version Guide

## Current stable version

`v25.4_output_guard_placeholder_fix`

## Recommended entrypoints

Use either:

```text
Web UI
```

or:

```text
semi_auto_ollama.py
```

Both now use the same formal G0-G6 Host-LLM definitions.

## Formal Host-LLM groups

| Group | Defense ID | Meaning |
|---|---|---|
| G0 | `none` | No defense baseline |
| G1 | `skill_only` | Skill-only model-level defense |
| G2 | `input_boundary` | Input Boundary only |
| G3 | `input_guard` | Input Guard only |
| G4 | `output_guard` | Output Guard only |
| G5 | `io_guard` | Input Guard + Input Boundary + Output Guard, no Skill |
| G6 | `full_guard` | Skill + Input Guard + Input Boundary + Output Guard |

## Recommended compare modes

### Core comparison

Use when you want the main formal comparison:

```text
G0, G1, G5, G6
```

### Full comparison

Use when you need to separate the individual guard modules:

```text
G0, G1, G2, G3, G4, G5, G6
```

## Notes

- v24-style G7 registry-enhanced comparison is not part of the standard v25.3 compare flow.
- Old result files that contain G7 can still be viewed for historical comparison.
- New official experiments should avoid mixing old G7 runs with v25.3 G0-G6 runs unless explicitly labeled as historical / compatibility data.

## v25.5 Addendum: Model Input and Auto Pull

The current Web UI official runner supports both single-model and batch-model input.

Formal model testing can be launched with:

- selected installed model,
- manually typed model name,
- one-model-per-line batch list.

When `Auto-pull missing models` is enabled, the Web bridge checks Ollama `/api/tags`, pulls missing models through `/api/pull`, records `batch_model_status.csv`, and then runs each model sequentially through the official runner. This does not change G0-G6 definitions or scoring.

## v25.6 Note

Output Guard now supports `auto / shadow / redact / block`, with `auto` as the formal default. v25.6 also adds enterprise protected-field detection for customer-profile style assets and emits `output_guard_selected_action` plus `output_guard_decision_reason` in reports.
