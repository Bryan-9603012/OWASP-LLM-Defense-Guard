# v24.4.12 Web UI-only / Terminal Replacement Fix

本版目的：讓 Web UI 成為終端機正式 runner 的視覺化替代層，而不是另一套實驗參數入口。

## 修正

- 移除 Web UI Experiment Wizard 的 Mode / Scope / Defense / Runtime 參數表單。
- 側邊欄將 `Experiment Center` 改為 `UI Console`。
- 移除 `Runner Bridge` 導航與頁首 Bridge 狀態，避免使用者誤以為 Web UI 會自行建立另一套實驗。
- `UI Console` 僅顯示目前讀取的 report path、protected asset、group mode、model / language。
- Web UI 不再從頁面啟動 Web official runner；正式實驗仍由 `run.bat` 或 `python semi_auto_ollama.py` 執行。
- Web UI 持續負責：Overview、Defense Groups、Model Comparison、Attack Analysis、Asset Manager、Trace Viewer、Reports。

## 使用方式

1. 先用正式入口跑實驗：

```bat
run.bat
```

或：

```bat
python semi_auto_ollama.py
```

2. 跑完後啟動平台：

```bat
run_platform.bat
```

3. 打開 UI Console / Defense Groups，確認載入的是正式結果：

```text
reports/compare_*/raw_results_all.csv
```

## 設計原則

Web UI 不改變正式實驗的 attack set、G 組、防禦策略、scoring、invalid 判斷與 protected asset 邏輯。
