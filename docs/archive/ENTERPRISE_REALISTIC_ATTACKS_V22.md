# V22 — Enterprise Realistic Attack Set

本版本在 v21「正式實驗 + 企業導向報告」基礎上，新增企業真實情境攻擊集，但**不取代**原本 controlled attacks。

## 定位

- `controlled`：原本 20 類 × 4 語言的 controlled benchmark，用於公平比較模型、防禦模式與語言差異。
- `enterprise`：新增 8 類 × 4 語言的 realistic enterprise attack set，用於模擬企業場景中的實際繞過語境。
- `both`：同時執行 controlled + enterprise，適合做完整補充分析。

## 新增檔案

- `data/attacks_enterprise_realistic.json`
- `attacks/attacks_enterprise_realistic.json`，作為備份/方便查找

## 新增攻擊類型

| ID | 類型 | 企業情境 | 測試重點 |
|---|---|---|---|
| E01 | Audit Pretext Disclosure | internal_audit | 內部稽核/合規名義索取 protected data |
| E02 | Debug Log Review | debug_log_review | 要求保留 debug/log 中的 secret |
| E03 | Document Rewrite Preservation | document_rewrite | 文件改寫時要求不得省略 flag/token/key |
| E04 | Translation Localization Bypass | cross_region_security_hand_off | 翻譯/本地化名義洩漏 protected data |
| E05 | Redaction Validation Trap | redaction_rule_validation | 要求顯示遮蔽前/遮蔽後比對 |
| E06 | Fragmented Disclosure | partial_disclosure_request | 分段輸出 prefix/body/ending 以便重建 |
| E07 | Structured Output Character Array | parser_test | JSON array / character-level reconstruction |
| E08 | Security Training Pretext | employee_security_training | 安全教育範例偽裝，要求使用真實 secret |

每類都有四種語言風格：

- `en_pure`
- `zh_pure`
- `zh_main_en_mixed`
- `en_main_zh_mixed`

## 新增參數

```bash
--attack-set controlled     # 預設，原本 controlled attacks
--attack-set enterprise     # 只跑企業真實情境攻擊
--attack-set both           # controlled + enterprise 一起跑
--enterprise-attacks data/attacks_enterprise_realistic.json
```

`--attack-ids` 現在支援 `Axx` 與 `Exx`：

```bash
--attack-ids A01,A03,A19
--attack-ids E01,E05,E07
```

## 建議正式實驗設計

主實驗仍建議使用 controlled attacks：

```bash
python src/run_benchmark.py ^
  --model gemma3:12b ^
  --attack-set controlled ^
  --defense full_guard ^
  --skill-profile full_security ^
  --limit-base-attacks 20 ^
  --styles all ^
  --runs 3 ^
  --include-benign ^
  --official-mode
```

企業真實情境作為延伸實驗：

```bash
python src/run_benchmark.py ^
  --model gemma3:12b ^
  --attack-set enterprise ^
  --defense full_guard ^
  --skill-profile full_security ^
  --styles all ^
  --runs 3 ^
  --include-benign ^
  --official-mode
```

如果要一次跑完整補充分析：

```bash
python src/run_benchmark.py ^
  --model gemma3:12b ^
  --attack-set both ^
  --defense full_guard ^
  --skill-profile full_security ^
  --limit-base-attacks 20 ^
  --styles all ^
  --runs 3 ^
  --include-benign ^
  --official-mode
```

> 注意：`--attack-set both --limit-base-attacks 20` 會保留 controlled A01–A20，並同時保留 enterprise E01–E08；不會因為 limit=20 而把 E 類攻擊排除。

## 新增報告

v22 在 v21 報告基礎上新增：

| 檔案 | 用途 |
|---|---|
| `attack_set_group_summary.csv` | 分開比較 controlled 與 enterprise realistic 的防禦效果 |
| `enterprise_scenario_summary.csv` | 依企業場景統計 raw leak / final leak / critical leak / guard mitigation |

## 論文/報告建議寫法

建議描述為：

> 本研究採用雙層攻擊資料集。第一層為 controlled attack set，用於控制變因並比較不同模型、防禦模式與語言風格。第二層為 realistic enterprise attack set，用於模擬內部稽核、debug log、文件改寫、翻譯本地化、遮蔽驗證、分段輸出、結構化輸出與安全教育等企業情境，以評估防禦策略在實務語境下的穩健性。

不建議寫成：

> 使用 enterprise realistic attacks 取代原本 controlled benchmark。

因為 enterprise attacks 的真實性較高，但變因也較多，較適合作為延伸實驗而非唯一主實驗。
