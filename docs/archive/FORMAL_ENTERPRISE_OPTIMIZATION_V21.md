# FORMAL_ENTERPRISE_OPTIMIZATION_V21.md

## 版本定位

本版將 v20 的企業風險報告能力進一步整理成「正式實驗 + 企業導向」版本。核心原則是：

- 不改變原本 leak level 0–4 與 Defense Score 的計分邏輯。
- 不把 Guard 攔截成功混同為模型本身安全。
- 保留 Host-level / Ollama model endpoint 測試定位。
- 強化報告層，讓正式實驗可以同時回答模型風險、系統輸出風險、防禦代價與企業稽核問題。

## 新增重點

### 1. Raw Model Risk vs Final System Risk

新增 `guard_mitigation_summary.csv`：

- `raw_model_avg_score`
- `final_system_avg_score`
- `raw_model_leak_rate`
- `final_system_leak_rate`
- `raw_model_critical_rate`
- `final_system_critical_rate`
- `guard_mitigation_rate`
- `critical_mitigation_rate`

用途：分開觀察模型原始輸出是否洩漏，以及防禦後使用者可見輸出是否仍洩漏。

### 2. Attack Category × Defense Matrix

新增 `attack_defense_matrix.csv`：

- 依 `attack_category` 與 `defense_id` 統計 raw/final leak rate。
- 可用來比較固定防禦模式在不同攻擊類型上的效果。
- 不引入 adaptive routing，避免正式實驗增加變因。

### 3. Language × Defense Effectiveness

新增 `language_defense_effectiveness.csv`：

- 依模型、防禦模式、語言/混語風格統計。
- 用來觀察跨語言防禦能力，而不是只看整體平均分數。

### 4. Guard Rule Class Summary

新增 `defense_rule_class` 與 `defense_rule_source` 欄位，並輸出 `guard_rule_class_summary.csv`。

可讀分類包含：

- `prompt_injection`
- `system_prompt_extraction`
- `direct_secret_request`
- `transformation_leakage`
- `credential_extraction`
- `disguised_high_risk`
- `generic_high_risk`
- `allowed`
- `guard_disabled`
- `rule_error`

用途：報告時不用只看 regex 原文，而是能統計哪一類防禦規則被觸發。

### 5. Defense Overhead / Resource Cost

新增 per-row 欄位：

- `input_guard_latency_ms`
- `model_latency_ms`
- `output_guard_latency_ms`
- `total_case_latency_ms`
- `defense_overhead_level`
- `skill_overhead_tokens_est`
- `prompt_total_chars`

並輸出 `defense_overhead_summary.csv`。

用途：評估 Full Guard 或 Skill Profile 是否帶來過高 prompt/latency 成本。

### 6. Invalid Breakdown

新增 `invalid_breakdown.csv`：

- 依 model / defense / error_type 分析 invalid。
- invalid 仍不納入 Defense Score。
- valid-but-format-violation 不應與 scoring invalid 混稱。

### 7. Formal Experiment Readiness

新增 `formal_experiment_readiness.csv`：

- 確認 valid / invalid 比例。
- 是否包含 benign false-positive 測試。
- 是否存在 hash metadata。
- 是否適合正式實驗報告。

## 建議正式實驗組別

正式主實驗建議仍使用固定防禦模式比較：

| 組別 | 說明 |
|---|---|
| `none` | Baseline，無防禦 |
| `skill_only` | 測模型是否理解並遵守防禦 Skill |
| `input_guard` | 測輸入端規則攔截能力 |
| `output_guard` | 測輸出端遮蔽/阻擋能力 |
| `full_guard` | 測完整防禦流程 |

Adaptive Defense Routing 不建議放入主實驗，因為它會讓防禦策略本身變成新變因。可作為 v22 或延伸實驗。

## 建議正式執行參數

單模型、20 base attacks、4 language styles、3 runs、包含 benign false-positive：

```bash
python src/run_benchmark.py \
  --model gemma3:12b \
  --defense full_guard \
  --skill-profile full_security \
  --limit-base-attacks 20 \
  --styles all \
  --runs 3 \
  --include-benign \
  --official-mode \
  --prompt-trace \
  --output-action block
```

如果不想保存完整 prompt trace，可移除 `--prompt-trace`，但正式復現性會比較弱。

## 報告解讀順序

建議正式報告先看：

1. `formal_experiment_readiness.csv`
2. `summary_all.md`
3. `guard_mitigation_summary.csv`
4. `attack_defense_matrix.csv`
5. `language_defense_effectiveness.csv`
6. `enterprise_assessment.csv`
7. `defense_overhead_summary.csv`
8. `invalid_breakdown.csv`

## 重要限制

- 本工具仍是 Host-level Ollama model endpoint 測試，不是 Web LLM App 測試。
- Guard 攔截成功代表系統層防禦有效，不代表模型本身沒有洩漏傾向。
- Output redaction/block 可以降低最終輸出風險，但 raw_response 仍需保存與分析。
- benign prompts 是可用性與誤擋觀察，不取代 attack scoring。
