# Web UI Result De-duplication Fix v24.4.10

This patch only changes Web UI result loading/aggregation behavior.
It does not change the official runner, attacks, skills, scoring, protected assets, or invalid-sample logic.

## Fixes

- Removes exact duplicate rows when displaying `raw_results_all.csv` in the Web UI.
- Prevents `raw_results_all.csv` and `raw_results.csv` from the same official-output folder being counted twice.
- Keeps job-level official results bound to the current Web job folder.
- Corrects Summary totals when older Web builds created duplicated merged CSVs.

Expected behavior for a run with:

```text
1 model × 2 attacks × 1 language × 4 defense groups × 1 round = 8
```

The Web UI should now show:

```text
Total: 8
Attack Samples: 8
Benign Samples: 0
```

instead of duplicated totals such as 16.
