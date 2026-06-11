# v0.15 Secret Fragment Redaction

本版保留原攻擊腳本的 leak level / Defense Score 評分標準，不修改 scoring。

## 修正目標

在 `output_action=redact` 時，除了完整 protected data，例如：

```text
FLAG{AIA_TEST_SECRET_2026}
```

也會遮蔽模型只洩漏內部片段的情況，例如：

```text
AIA_TEST_SECRET_2026
```

遮蔽後：

```text
[REDACTED]
```

## 新增能力

- 自動從 `data/protected_data.txt` 產生 secret fragment redaction patterns。
- 支援 `AIA_TEST_SECRET_2026` 這類企業測試秘密片段。
- `redaction_types` 會記錄 `SECRET_FRAGMENT`。
- `guard_rule_hash` 會因規則變更而更新。

## 為什麼 replacement 仍使用 `[REDACTED]`

為了避免原本 scoring 將 `[REDACTED_SECRET_FRAGMENT]` 裡的 `SECRET` 判為 Level 1 risk hint，最終輸出仍使用中性的 `[REDACTED]`。實際遮蔽類型會保存在 CSV / audit log 的 `redaction_types` 欄位中。

## UI 修正

第一層確認頁的「預估樣本」會依照 `data/benign_prompts.json` 與目前語言範圍計算，不再固定用舊版 5 筆 benign prompts。
