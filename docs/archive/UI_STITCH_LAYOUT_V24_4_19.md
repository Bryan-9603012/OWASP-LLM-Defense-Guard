# v24.4.19 Stitch-inspired UI Layout

This version updates only the Web UI presentation layer. It keeps the official runner bridge as the source of truth.

## Updated
- Sidebar labels: UI Console, Defense Groups, Model Results, Asset Manager, Trace Viewer, Reports.
- Run Official Experiment page adopts a Stitch-style stepper layout.
- Default benchmark parameters remain aligned with the formal runner: gemma3:1b, max_tokens=800, ctx=4096, temp=0.0, seed=42, controlled attacks, 20 base attacks.
- Single-model result page is labeled Model Summary instead of Model Comparison.
- Experiment status page uses a runner-status dashboard layout.

## Not changed
- Attack prompts
- Scoring
- valid_sample / invalid logic
- G0/G1/G5/G6/G7 definitions
- protected asset loading
- CSV writer hardening
- Ollama client behavior
