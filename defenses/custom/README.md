# Custom Defense Rules

這個資料夾用來放使用者自訂防禦規則。

## 支援檔案

- `custom_skill.md`：真正自訂的模型內 Skill。啟用後會取代內建 Skill Profile，模型只會掛這份 Skill。
- `custom_input_patterns.txt`：補充 Input Guard Regex 規則，一行一條。
- `custom_output_patterns.txt`：補充 Output Guard Regex 規則，一行一條。

## 企業版設計原則

自訂 Skill 採用 **custom-only** 行為：

```text
system_prompt + custom_skill.md
```

不再支援：

```text
system_prompt + 內建 Skill Profile + custom_skill.md
```

這樣可以確保外部 Skill / 企業 Skill / 第三方 Skill 的測試結果乾淨、可稽核、可比較。
