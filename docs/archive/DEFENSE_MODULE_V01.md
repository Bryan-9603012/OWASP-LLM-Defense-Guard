# Defense Module v0.1

本版本將防禦功能直接整合進現有 benchmark pipeline，而不是拆成獨立專案。

## Defense Modes

| defense_id | 說明 |
|---|---|
| `none` | 不啟用任何額外防禦，作為 baseline。 |
| `skill_only` | 只注入 `defenses/skill_defense.txt`，測試模型是否能遵守防禦規則。 |
| `input_guard` | 只在送入模型前檢查 prompt，命中攻擊樣式則不呼叫模型，直接輸出安全拒答。 |
| `output_guard` | 只檢查模型原始輸出，若偵測洩漏則以安全拒答取代。 |
| `full_guard` | 同時啟用 Skill + Input Guard + Output Guard。 |

保留 `prompt_defense` 與 `skill_defense` 作為舊版相容模式。

## 新增 CSV 欄位

| 欄位 | 說明 |
|---|---|
| `raw_response` | 模型原始輸出。input guard 阻擋時為空。 |
| `final_response` | 經防禦模組處理後的最終輸出。 |
| `response` | 為了相容舊報表，等同 `final_response`。 |
| `raw_leak_level` | 對 raw response 的洩漏等級。 |
| `raw_score` | 對 raw response 的分數，可視為 Model Defense Score 的基礎。 |
| `final_leak_level` | 對 final response 的洩漏等級。 |
| `final_score` | 對 final response 的分數，可視為 System Defense Score 的基礎。 |
| `defense_triggered` | `none` / `input_guard` / `output_guard`。 |
| `defense_reason` | 觸發原因或規則。 |
| `input_blocked` | 是否在 input guard 階段被擋。 |
| `output_blocked` | 是否在 output guard 階段被擋。 |

## 建議第一輪驗證

```bash
python src/run_benchmark.py --model mock --defense full_guard --styles en_pure --limit-base-attacks 2 --runs 1 --no-report
```

正式跑 Ollama 時可改為：

```bash
python src/run_benchmark.py --model ollama:gemma3:12b --defense full_guard --styles en_pure --limit-base-attacks 20 --runs 3
```
