# Defense Skill Profile v0.2

本版把原本單一 `skill_defense.txt` 拆成多個可組合 Skill，並新增 Skill Profile。

## 新增目錄

```text
defenses/
├── skills/
│   ├── base_security_skill.md
│   ├── secret_protection_skill.md
│   ├── prompt_injection_defense_skill.md
│   ├── transformation_defense_skill.md
│   ├── system_prompt_protection_skill.md
│   └── enterprise_refusal_style_skill.md
└── skill_profiles/
    ├── profiles.json
    ├── minimal.json
    ├── secret_only.json
    ├── injection_only.json
    ├── transformation_only.json
    ├── full_security.json
    └── enterprise_strict.json
```

## Skill Profile

| profile | 用途 |
|---|---|
| `minimal` | 只載入基礎安全規則，適合小模型初測 |
| `secret_only` | 聚焦敏感資料保護，適合 LLM02 主線 |
| `injection_only` | 單獨測 prompt injection 防禦 |
| `transformation_only` | 單獨測翻譯、編碼、拆字等轉換型洩漏 |
| `full_security` | 載入全部安全 skill，適合正式測試 |
| `enterprise_strict` | 企業嚴格模式預案 |

## CLI 使用方式

```bash
python src/run_benchmark.py --model mock --defense skill_only --skill-profile minimal --styles en_pure --limit-base-attacks 1 --runs 1

python src/run_benchmark.py --model ollama:gemma3:1b --defense skill_only --skill-profile full_security --styles en_pure --limit-base-attacks 20 --runs 3

python src/run_benchmark.py --model ollama:gemma3:1b --defense full_guard --skill-profile full_security --styles en_pure --limit-base-attacks 20 --runs 3
```

## CSV 新增欄位

```text
skill_profile
skill_profile_name
loaded_skills
skill_length_chars
skill_est_tokens
```

這些欄位用來分析不同 Skill Profile 對小模型的影響，尤其是 prompt 長度對穩定性與截斷的影響。

## 介面更新

當防禦模式選擇 `skill_only`、`full_guard`、`prompt_defense` 或 `skill_defense` 時，互動式介面會多出一頁：

```text
選擇 Skill Profile
```

如果選的是 `none`、`input_guard` 或 `output_guard`，則不會出現 Skill Profile 頁。

## 顯示修正

原本確認頁顯示：

```text
攻擊 ID : all
攻擊數限制 : 5
```

現在改成：

```text
攻擊範圍 : 全部攻擊清單
實際執行 : 前 5 個 base attack
```

避免誤會成真的要跑全部攻擊。
