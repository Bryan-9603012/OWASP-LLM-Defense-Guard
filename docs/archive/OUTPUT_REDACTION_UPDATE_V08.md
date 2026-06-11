# Defense v0.8：輸出處置方式 / Redaction Update

本版新增企業常見的 Output Guard 處置方式，讓輸出端不只支援整段拒答，也能選擇遮蔽敏感片段或只記錄風險。

## 新增輸出處置方式

| 模式 | CLI 值 | 說明 |
|---|---|---|
| 整段阻擋 | `block` | 偵測到敏感資料時，用安全拒答取代整段輸出。 |
| 敏感資料遮蔽 | `redact` | 只將敏感片段替換成 `[REDACTED]`，保留其餘內容。 |
| 只記錄不阻擋 | `shadow` | 保留模型原始輸出，只在 CSV / audit log / report 中記錄偵測結果。 |

## CLI 用法

```bash
python src/run_benchmark.py --model ollama:gemma3:1b --defense output_guard --output-action redact --styles en_pure --limit-base-attacks 5 --runs 1
```

```bash
python src/run_benchmark.py --model ollama:gemma3:1b --defense full_guard --output-action block --styles en_pure --limit-base-attacks 5 --runs 1
```

## 新增 CSV 欄位

```text
output_action
redaction_applied
redaction_count
redaction_types
```

## 評分邏輯

- `raw_response` 保留模型原始輸出。
- `final_response` 保存 output guard 處置後的輸出。
- `raw_score` 評估模型本身風險。
- `final_score` 評估使用者最後看到的系統風險。
- `redact` 模式會讓 `raw_response` 仍保留原始洩漏，`final_response` 則替換敏感片段。

## Audit Log

`audit_log.jsonl` 新增：

```text
output_action
redaction_applied
redaction_count
redaction_types
```

若 `output_action=shadow`，事件 action 會記錄為 `shadow`，但 final response 不會被修改。
