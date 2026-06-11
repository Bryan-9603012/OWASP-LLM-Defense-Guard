# v24.4.11 Web UI Report Source Alignment Fix

This patch fixes the mismatch between terminal results and Web UI Defense Group results.

## Fixed

1. **Report source priority**
   - Web UI now prefers formal terminal runner folders under `reports/compare_*`.
   - Then falls back to `reports/web_official_requests/run_*`.
   - Then falls back to root-level `reports/raw_results_all.csv`.
   - Per-group `official_outputs` files are only used as a last resort.

2. **Visible report context**
   - Defense page now shows:
     - loaded report path
     - protected asset id/name/risk
     - group mode
     - model/language

3. **Formal G-Group labels preserved**
   - G0/G1/G5/G6/G7 are no longer collapsed into the 4-item strategy audit naming.
   - Formal runner results now display as:
     - G0 No Defense
     - G1 Skill-only
     - G5 Full Guard
     - G6 Attack-aware Full Guard
     - G7 Registry-enhanced Full Guard

4. **Valid / Total column added**
   - Coverage is now easier to verify against terminal output.

5. **Action Rate clarified**
   - `Action Rate` was replaced by:
     - Output Intervention
     - Model Refusal
   - This avoids confusing model refusal with output guard block/redaction.

## Verification

Tested against the latest `reports.zip` case:

- Loaded report:
  `reports/compare_gemma3_1b_host_core_g0_g1_g5_g6_g7_lang_en_pure/raw_results_all.csv`
- Protected asset:
  `customer_profile_001 / Demo Customer Profile / risk=critical`
- Rows:
  150
- Groups:
  G0, G1, G5, G6, G7

The Web UI values now match the terminal runner summary.
