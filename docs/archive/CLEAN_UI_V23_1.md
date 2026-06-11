# Clean UI Update v23.1

本版在 v23 Risk-based Strict Review 基礎上整理互動式 UI，目標是降低設定流程的工程參數感，讓一般正式實驗流程更乾淨。

## 改動

### 1. 互動式 UI 不再直接詢問 review-level

`semi_auto_ollama.py` 會依防禦模式自動選擇審查策略：

| 防禦計畫 | 自動審查策略 |
|---|---|
| `full_guard` | `attack_aware` |
| `input_guard` / `output_guard` | `standard` |
| `none` / `skill_only` | `standard`，主要維持報表欄位一致 |

CLI 仍然保留：

```bash
python src/run_benchmark.py --review-level strict
python src/run_benchmark.py --review-level attack_aware
```

### 2. 互動式 UI 不再直接詢問 output-action

`semi_auto_ollama.py` 會依防禦模式自動選擇輸出處置：

| 條件 | 自動輸出處置 |
|---|---|
| 有 `output_guard` / `full_guard` | `redact` |
| 沒有 output guard | `block`，但實際上不影響結果 |

CLI 仍然保留：

```bash
python src/run_benchmark.py --output-action block
python src/run_benchmark.py --output-action redact
python src/run_benchmark.py --output-action shadow
```

### 3. Skill 掛載驗證預設關閉

互動式 UI 預設不再詢問 `Prompt Trace / Skill Probe`，避免正式測試流程過長。需要 debug 時仍可直接用 CLI：

```bash
python src/run_benchmark.py --prompt-trace --skill-probe
```

## 設計原則

互動式 UI 只保留高層決策：

```text
模型 → 測試範圍 → 防禦計畫 → Skill Profile → 自訂規則 → benign → 次數 → 生成參數 → 確認
```

低層參數改為自動預設，並在確認畫面顯示實際採用值。
