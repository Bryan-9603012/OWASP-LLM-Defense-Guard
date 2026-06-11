# V18 更新：企業版真正自訂 Skill

## 核心變更

本版移除舊版的「內建 Skill Profile + 自訂 Skill」追加模式。

自訂 Skill 啟用後，模型上只會掛載：

```text
system_prompt.txt
+
custom_skill.md
```

不會再掛載：

```text
system_prompt.txt
+
full_security / secret_only / minimal 等內建 Skill Profile
+
custom_skill.md
```

## 為什麼這樣改

企業或第三方 Skill 評測需要清楚回答：

> 這份 Skill 本身是否有效？

如果保留追加模式，結果會同時受到內建 Skill 與外部 Skill 影響，難以解釋來源，也不利於企業稽核與公平比較。

## 使用方式

```bash
python src/run_benchmark.py \
  --model ollama:gemma3:12b \
  --defense skill_only \
  --custom-skill-file defenses/custom/company_skill.md
```

不需要也不支援 `--custom-skill-mode append`。

## 報表欄位

啟用自訂 Skill 後，報表會出現：

```text
skill_profile = custom_only
skill_profile_name = Custom Skill Only
loaded_skills = custom_skill
custom_skill_mode = custom_only
```

## 保留項目

Input Guard / Output Guard 的自訂 regex 仍屬於程式層補充規則，不是模型內 Skill。
正式比較外部 Skill 時，建議先只使用 `--custom-skill-file`，避免混入其他程式層變因。
