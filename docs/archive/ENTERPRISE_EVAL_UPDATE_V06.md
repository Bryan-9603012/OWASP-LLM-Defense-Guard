# Defense v0.6：企業評估雛形更新

本版在 v0.5 乾淨介面與模型輸入流程上，加入更接近企業 LLM 上線前安全評估的功能。

## 新增功能

### 1. 防禦比較模式

互動式介面新增「防禦測試方式」：

- 單一防禦：只跑一種防禦模式
- 基本比較：自動跑 `none + skill_only + output_guard + full_guard`
- 完整比較：自動跑 `none + skill_only + input_guard + output_guard + full_guard`

用途：不用手動重跑多次即可比較模型本身、Skill 防禦、輸出防線與完整防禦。

### 2. 正常樣本測試 Benign Prompts

新增：

```text
data/benign_prompts.json
```

互動式介面會詢問是否啟用正常樣本測試。啟用後會把 benign prompts 追加到測試中，用於估算正常請求被誤擋的比例。

CLI 可使用：

```bash
python src/run_benchmark.py --include-benign --benign-file data/benign_prompts.json ...
```

### 3. False Positive / 企業評估指標

報表新增：

```text
enterprise_assessment.csv
```

主要欄位：

- `attack_block_rate`
- `false_positive_rate`
- `false_positive_count`
- `final_leak_rate`
- `critical_leak_count`
- `critical_leak_rate`
- `leak_prevention_rate`

### 4. Executive Summary

報表新增：

```text
executive_summary.md
```

內容包含：

- 整體風險
- 上線建議
- 最佳防禦組合
- 防禦比較摘要
- 建議措施
- 殘留風險

### 5. Audit Log

每次 run 會在該次 report folder 產生：

```text
audit_log.jsonl
```

每筆事件會保存：

- model / attack_id / sample_type
- defense_id / skill_profile
- defense_triggered / defense_reason
- input_blocked / output_blocked
- prompt_hash / raw_response_hash / final_response_hash
- custom_rule_hash

不直接把完整 prompt/response 寫進 audit log，以降低敏感資料保存風險。

## 建議測試流程

小模型快速比較：

```text
模型：gemma3:1b
範圍：快速測試
防禦測試方式：基本比較
Skill Profile：minimal 或 full_security
正常樣本測試：啟用
runs：1 或 3
```

正式比較：

```text
模型：gemma3:1b, qwen2.5:0.5b
範圍：自訂 A01,A20 / en_pure
防禦測試方式：基本比較
正常樣本測試：啟用
runs：3
```
