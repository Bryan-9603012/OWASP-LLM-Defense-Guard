# v25.3 Entrypoint G-Group Alignment

## Purpose

This patch aligns the formal Host-LLM G-group definitions across:

- Web UI (`sg_platform/app.py`)
- Interactive CLI (`semi_auto_ollama.py`)
- Report generator (`src/report_generator.py`)
- CLI help text (`src/run_benchmark.py`)
- README / current usage notes

The goal is to prevent different entrypoints from using different meanings for the same G-group label.

## Formal v25.3 G-groups

| Group | Defense ID | Name | Meaning |
|---|---|---|---|
| G0 | `none` | G0 No Defense | Baseline without Skill or guards |
| G1 | `skill_only` | G1 Skill-only | Model-level Skill defense only |
| G2 | `input_boundary` | G2 Input Boundary | Wrap user input as untrusted data |
| G3 | `input_guard` | G3 Input Guard | Programmatic input filtering only |
| G4 | `output_guard` | G4 Output Guard | Programmatic output filtering only |
| G5 | `io_guard` | G5 IO Guard | Input Guard + Input Boundary + Output Guard, no Skill |
| G6 | `full_guard` | G6 Full Guard | Skill + Input Guard + Input Boundary + Output Guard |

## CLI comparison modes

### Host LLM core comparison

Runs:

```text
G0, G1, G5, G6
```

### Host LLM full comparison

Runs:

```text
G0, G1, G2, G3, G4, G5, G6
```

## Removed from standard compare paths

The old v24 registry-enhanced G7 path is no longer part of the standard v25.3 Host-LLM compare modes.

Reason:

- G7 introduced registry / canary behavior as an additional variable.
- v25.3 keeps the formal comparison centered on Skill, Input Boundary, Input Guard, Output Guard, IO Guard, and Full Guard.
- Old G7 CSVs may still be rendered for backward compatibility, but new standard runs should use G0-G6 only.

## Files changed

- `semi_auto_ollama.py`
  - Core comparison changed from `G0/G1/G5/G6/G7` to `G0/G1/G5/G6`.
  - Full comparison changed from `G0-G7` to `G0-G6`.
  - G2 now maps to `input_boundary`.
  - G5 now maps to `io_guard`.
  - G6 now maps to `full_guard`.

- `src/report_generator.py`
  - Formal order changed to G0-G6.
  - Report wording updated to v25.3 formal G-group comparison.

- `sg_platform/app.py`
  - Normalization fixed so G5 means `G5 IO Guard` and G6 means `G6 Full Guard`.
  - Recommended card wording updated to `Core G0-G6 metrics`.

- `src/run_benchmark.py`
  - `--g-group-id` help text updated to G0-G6.

- `data/registry_disabled.json`
  - Description updated to explain that v25.3 formal G0-G6 runs keep registry disabled by default.

## Expected outcome

After this patch, Web UI, semi-auto CLI, and report generation should use the same formal G0-G6 definitions.
