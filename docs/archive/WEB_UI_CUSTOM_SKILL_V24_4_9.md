# v24.4.9 Web UI Custom Skill Exposure

This patch exposes the existing official-runner custom skill capability in the Web UI.

Scope:

- Adds Skill Manager page support for built-in skill profiles from `defenses/skill_profiles/profiles.json`.
- Adds Custom Skill editor for markdown files under `defenses/custom/`.
- Adds Experiment Center controls for:
  - `--skill-profile`
  - `--custom-skill-file`
- Keeps execution delegated to `src/run_benchmark.py`.

No experiment logic is changed:

- No Web scoring
- No Web skill engine
- No attack modification
- No invalid-sample logic modification
- No runner replacement

The Web layer only replaces terminal UI and passes official runner CLI flags.
