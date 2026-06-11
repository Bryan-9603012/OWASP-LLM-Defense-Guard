# v24.4.24 Heatmap Dashboard UI Fix

This patch upgrades the Web UI visualization layer only.

## Changes

- Added Overview `Attack Risk Heatmap by Defense Group`.
  - Rows: A01-A20
  - Columns: official G groups loaded from the report
  - Default metric: Delivered Critical Leak Rate
  - Tooltips include Delivered Critical, Raw Critical, Defense Score, Worst Leak Level, and Valid count.

- Added Attack Analysis `Attack × Leak Level Heatmap`.
  - Rows: A01-A20
  - Columns: L0-L4
  - Count view is shown by default.
  - The old stacked Leak Level Distribution is preserved as a collapsible detail view.

- Updated leak-level color semantics:
  - L0 Safe: green
  - L1 Risk Hint: yellow
  - L2 Partial: orange
  - L3 Reconstructable: red
  - L4 Direct Leak: pink/dark red

- Kept official terminology:
  - G0 No Defense
  - G1 Skill-only
  - G5 Full Guard
  - G6 Attack-aware Full Guard
  - G7 Registry-enhanced Full Guard

## Not changed

This patch does not modify:

- official runner
- attacks
- defense groups
- scoring
- invalid-sample logic
- protected assets
- Ollama client
- CSV writer
