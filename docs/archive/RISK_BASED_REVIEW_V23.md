# Risk-based Strict Review V23

本版在 v22 formal enterprise realistic 基礎上加入可分級審查機制，重點是「嚴格但可比較」，不是把所有輸入都暴力正規化後再送給模型。

## 新增功能

### 1. `--review-level`

可用值：

| Level | 用途 | 說明 |
|---|---|---|
| `light` | 正常樣本 / false positive 觀察 | 只保留最低限度的 secret / credential 檢查。 |
| `standard` | 主實驗預設 | 延續原本 input/output guard 規則。 |
| `strict` | 嚴格審查 | 加強偵測拆字、分段、逐字元、`.txt` 包裝、圖片/程式碼包裝、編碼重建。 |
| `enterprise` | 企業嚴格審查 | 在 strict 基礎上加入 customer data、internal/config/database/credential 類風險。 |
| `attack_aware` | 攻擊感知審查 | 依 attack metadata / prompt 自動切換 light、standard、strict、enterprise。 |

範例：

```bash
python src/run_benchmark.py --model mock --defense full_guard --review-level attack_aware --output-action redact --quick-test
```

```bash
python src/run_benchmark.py --model ollama:gemma3:12b --defense full_guard --skill-profile full_security --review-level strict --output-action block --runs 1
```

## 2. Analysis-only normalization

本版會建立 guard 專用的 normalized copy：

- `raw`：原文
- `nfkc`：Unicode NFKC 正規化
- `lowered`：小寫化
- `compact`：移除空白/符號後的偵測字串

重要：normalized copy **只用於 guard 偵測**，不會取代原始 prompt，也不會被送入模型。

這是為了避免破壞正常問題，例如：

- C++
- JSON
- URL
- regex
- 程式碼片段

## 3. 新增報表欄位

CSV / audit log 會新增：

| 欄位 | 說明 |
|---|---|
| `configured_review_level` | 使用者命令指定的審查層級。 |
| `effective_review_level` | 單筆樣本實際採用的審查層級。 |
| `review_policy` | `static` 或 `attack_aware`。 |
| `review_risk_signal` | 為何選擇該層級。 |
| `normalized_checked` | 是否啟用 normalized copy 偵測。 |

## 4. 正式實驗建議

主實驗建議：

```text
G0 none
G1 skill_only + standard
G2 input_guard + standard
G3 output_guard + redact + standard
G4 full_guard + strict
G5 full_guard + attack_aware
```

企業補充實驗建議：

```text
enterprise attacks：
  none
  full_guard + strict
  full_guard + enterprise
  full_guard + attack_aware
```

## 5. 注意事項

- 原本 leak level 0–4 評分邏輯未改。
- 原本 invalid / truncated 判定邏輯未改。
- Review level 只影響 input/output guard 的偵測強度。
- `raw_response` 仍用來觀察模型本體風險。
- `final_response` 仍用來觀察系統輸出風險。
