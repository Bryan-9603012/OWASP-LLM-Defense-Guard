# LLM Secret Guard Internal Platform v0.1

內網試跑版 Web Platform，採用 Stitch 風格的 dark enterprise security UI。

## 功能
- Overview：讀取 reports CSV 或使用 demo data 顯示總覽
- Model Comparison：模型 Defense Score / Safe Rate / Critical Leak / Invalid Rate 比較
- Defense Groups：G-group 防禦組別比較
- Attack Analysis：A01-A20 洩漏等級分布分析
- Protected Asset Manager：讀取與新增 `configs/protected_assets.json`
- Trace Viewer：查詢 raw results / prompt trace 摘要
- Reports Export：列出可下載的 CSV / Markdown / ZIP / PDF 類報表

## 啟動方式
Windows 本機：
```bat
run_platform.bat
```
Windows 內網：
```bat
run_platform_lan.bat
```
Linux / WSL：
```bash
bash run_platform.sh
```

本機瀏覽：`http://127.0.0.1:8080`
內網瀏覽：`http://你的主機IP:8080`

## 資料來源
平台會優先讀取專案根目錄下的：
```text
reports/raw_results_all.csv
reports/g_group_core_comparison.csv
configs/protected_assets.json
```
如果找不到 reports，會自動顯示 demo data，方便先確認 UI。

## 安全注意
- Trace Viewer 預設會遮蔽常見 secret pattern 與 protected asset value。
- 第一版不直接從 Web 啟動正式實驗，避免影響 v24.x 核心流程。
- 建議只在內網或 localhost 試跑，不要公開到 Internet。

## v0.2 Data Source Indicator

平台右上角會顯示目前資料來源：

- `Data Source: Demo Data`：沒有偵測到 `reports/raw_results_all.csv`，目前顯示的是 UI 測試用假資料。
- `Data Source: Live Reports`：已讀取 `reports/raw_results_all.csv` 或巢狀 run 目錄中的正式結果。

首頁上方也會顯示 `Demo Mode` 或 `Live Report Mode` 提示，避免把示範資料誤判成正式實驗數據。

## v24.3.6 - Experiment Center

This version adds a web-based Experiment Center for internal LAN smoke tests.

### What it can do

- Select one or more local Ollama models.
- Choose attack scope: `A01,A02` or `all`.
- Choose languages: `en`, `zh`, `zh-en`, `en-zh`.
- Choose defense group.
- Adjust rounds, max tokens, temperature, and Ollama URL.
- Run the evaluation from the web page.
- Write results to:
  - `reports/raw_results_all.csv`
  - `reports/web_runs/<run_id>/raw_results_all.csv`
  - `reports/web_runs/<run_id>/prompt_trace/`

### Important

This is intended for small internal smoke tests and UI-driven parameter tuning. For large formal experiments, keep using the original CLI runner so reproducibility and long-run stability remain controlled.

## v24.3.7 - Web Comparison Modes

Experiment Center now supports multiple evaluation modes:

- `Single Run`: one selected defense group, useful for quick smoke tests and parameter tuning.
- `Defense Comparison / G-Group`: runs the same model/attack/language settings across multiple defense groups and writes `reports/g_group_core_comparison.csv`.
- `Model Comparison`: compares multiple models under one defense group.
- `Full Matrix`: runs models × attacks × languages × defense groups. Use this only with small scopes in the web UI.

The web runner also records both raw and delivered leak levels:

- `raw_leak_level`: model-level leakage before output redaction.
- `delivered_leak_level`: user-visible leakage after output filtering/redaction.
- `defense_action`: `ALLOW`, `REDACTED`, or `ERROR`.

Recommended first comparison test:

```text
Evaluation Mode: Defense Comparison / G-Group
Model Scope: gemma3:1b
Attack Scope: A01,A02
Languages: en,zh
Comparison Defense Groups: No Defense,Prompt Defense,Input Boundary Defense,Output Filter Defense,Policy Defense,Hybrid Defense
Rounds: 1
Max Tokens: 256
Temperature: 0.2
```

## v24.3.9 UI Refresh

新增 Stitch-style UI 優化：

- Experiment Center 改為 5-step Evaluation Wizard：Mode → Scope → Defense → Runtime → Review。
- Evaluation Mode 改為卡片式選擇：Single Run、Defense Comparison / G-Group、Model Comparison、Full Matrix。
- Defense 設定會依 Evaluation Mode 自動切換顯示，避免單一 Defense Group 與 Comparison Defense Groups 混淆。
- Overview 改成平台式總覽，新增 Best Defense Group、Most Dangerous Attack、Raw Leak、Delivered Leak 與 Latest Findings。
- Attack Analysis 改成 A01-A20 matrix + leak level distribution 風格。
- 頂部狀態列改為 Demo Data / Live Reports 分段顯示。

注意：Web Experiment Center 適合 smoke test、調參與 demo；大量正式數據仍建議保留 CLI 流程。


## v24.3.11 notes

- Restored skill-oriented defense groups in the Web UI: `Skill Only`, `Custom Asset Only`, and `Skill + Custom Asset`.
- Default Defense Comparison / G-Group now uses the formal-style four groups: `No Defense`, `Skill Only`, `Custom Asset Only`, `Skill + Custom Asset`.
- Web Experiment Center runs are explicitly marked as `run_source=web_trial`, `formal_mode=False`, and `runner_type=simplified_web_trial_runner`.
- The web runner remains intended for smoke tests, parameter tuning, and demos. Formal data should still be produced by the official CLI runner/scorer/skill pipeline unless the web backend is explicitly wired to that runner.


## v24.3.12 UI-only official-runner bridge

這版的核心原則是：**Web 只替代終端機 UI，不替代正式實驗邏輯**。

- Web Experiment Center 只負責收集參數、產生 `experiment_config.json`。
- Web 不再使用簡化版 scoring / runner 產生正式數據。
- 若要從網頁按 Start 後直接執行，請複製：

```text
configs/official_runner_bridge.example.json
```

成：

```text
configs/official_runner_bridge.json
```

然後把 `enabled` 改成 `true`，並把 `command` 指到你原本正式 CLI runner。範例：

```json
{
  "enabled": true,
  "command": ["{python}", "run_benchmark.py", "--config", "{config}"],
  "cwd": "{root}"
}
```

可用 placeholder：

```text
{python} 目前 Python 執行檔
{root} 專案根目錄
{config} Web 產生的 experiment_config.json
{run_dir} 本次 request 的輸出資料夾
{reports} reports 資料夾
{job_id} Web job id
```

如果你的正式 runner 目前不支援 `--config`，建議新增一個很薄的 adapter 去讀 `{config}` 並呼叫原本核心函式；不要在 Web layer 另寫一套判分邏輯。

## v24.3.13 - Runner Bridge UI

本版新增 **Runner Bridge** 頁面，讓 Web 平台真正維持「只取代終端機 UI」的定位：

```text
Web Evaluation Wizard
  -> 產生 experiment_config.json
  -> 呼叫原本正式 runner
  -> 原本 runner 使用既有 attacks / skill / custom assets / scoring / invalid 邏輯
  -> 原本 runner 輸出 reports
  -> Web Dashboard 讀取 reports 顯示
```

### 設定方式

1. 啟動平台後進入左側 `Runner Bridge`。
2. 選擇你原本的正式 runner 腳本，例如：
   - `run_benchmark.py`
   - `semi_auto_ollama.py`
   - `main.py`
3. 確認正式 runner 支援 `--config <experiment_config.json>` 或等價參數。
4. 勾選 `Enable official runner bridge`。
5. 按 `Save Bridge Settings`。
6. 回到 `Experiment Center` 啟動測試。

### 重要原則

Web 層不重新實作 scoring、不重新包裝 prompt、不取代 skill 或 valid_sample 邏輯。若正式 runner 尚未支援 config mode，請先在正式 runner 加入 non-interactive config mode，再透過 Runner Bridge 呼叫。
