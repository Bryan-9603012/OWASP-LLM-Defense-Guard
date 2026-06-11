# Live Run UI Fix v25.1

This patch fixes a Web UI confusion during official-runner execution.

## Fixed

- The top banner no longer says `Demo Mode` while an official runner job is actively running.
- During active runs, the UI now shows `Runner Active` and explains that reports will switch to Live Report Mode after `raw_results_all.csv` is generated.
- The Run Status page auto-refreshes every 3 seconds while running.
- The Web bridge now streams official runner stdout into the log file and parses progress lines like `[3/20] A03 ...`, so progress can update before the subprocess fully finishes.

## Not changed

- Scoring logic is not changed.
- Invalid-sample logic is not changed.
- Attack set, skill logic, and output guard logic are not changed.
- This patch only improves the Web UI status/report-source behavior.
