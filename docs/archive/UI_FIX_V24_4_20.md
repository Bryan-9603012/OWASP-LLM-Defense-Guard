# v24.4.20 Overview UI Metric Fix

This build only updates Web UI presentation logic. It does not change attacks, scoring, invalid-sample handling, protected assets, defense rules, or Ollama execution.

## Fixes

- Best Defense Group now selects the highest Defense Score, then Safe Rate, then lower Delivered Critical Leak, then Coverage. It no longer defaults to the first G-group row.
- Raw Leak / Delivered Leak labels are renamed to Raw Critical Leak / Delivered Critical Leak.
- Delivered Critical Leak uses warning color when >0 and <=5%, red when >5%, green only at 0%.
- Latest Findings only lists attacks with delivered/raw critical risk. Zero-risk vectors are not labeled as watchlisted.
- Risk Heatmap now includes a legend.
- Overall average cards clarify that they are aggregated across selected defense groups.
- Defense Groups note clarifies that Defense Score uses attack samples while False Positive / Benign Pass use benign samples.
