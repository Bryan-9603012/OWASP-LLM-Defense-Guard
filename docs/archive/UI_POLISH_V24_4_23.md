# v24.4.23 UI Polish and Reports Usability Fix

This build applies final Web UI polish only. It does not change official benchmark logic, attack prompts, scoring, invalid-sample handling, protected asset behavior, G-group definitions, or Ollama calls.

## Changes

- Reports Center now prioritizes primary official outputs and hides nested per-group/model copies by default.
- Reports Center adds Primary / Recommended / Nested copy badges.
- Reports Center adds visible file count and a Show nested copies toggle.
- Recommended ZIP now prefers primary files instead of packing many duplicate nested copies.
- Raw Critical Leak and Delivered Critical Leak now use consistent risk color thresholds.
- Attack Matrix now uses stronger risk colors for delivered-critical vectors.
- Attack names now wrap instead of truncating names such as Multi-lingual Injection and Model Self Disclosure.
- Model Summary explanation is shortened and clearer.
- Risk Heatmap critical coloring is made more visible.

## Source of Truth

The Web UI remains a terminal-replacement layer. It passes parameters to `src/run_benchmark.py`, reads the official generated reports, and displays them. It does not perform independent scoring.
