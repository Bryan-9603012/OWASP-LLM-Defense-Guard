# v19 Experiment Quality Assurance Update

本版重點不是改變 scoring，而是補強正式實驗的可驗證、可稽核與可重現性。

## 新增內容

1. `tools/validate_custom_skill.py`
   - 檢查自訂 Skill 檔案是否存在、是否為 Markdown、是否為空、長度/token 估算、是否有拒答與 secret 保護語意。
   - 若偵測到明顯反向危險指令，會阻止執行。

2. `experiment_manifest.json`
   - 每次正式執行會輸出模型、防禦、custom Skill hash、attack hash、token/temperature/runs、環境資訊與版本 hash。

3. 報表欄位補強
   - `custom_skill_hash`
   - `custom_skill_chars`
   - `custom_skill_est_tokens`
   - `custom_skill_first_heading`
   - `custom_skill_validation_status`
   - `custom_skill_validation_warnings`
   - `custom_skill_validation_errors`

4. `--official-mode`
   - 啟用更嚴格的正式實驗 QA 檢查。
   - 目前會檢查 attacks 檔案、protected data、runs/max_tokens、temperature=0、自訂 Skill 驗證狀態與 custom_only 行為。

5. `tools/smoke_test.py` / `run_smoke_test.bat`
   - 一鍵檢查 attacks/protected data/defense config/custom skill validator/mock quick run/manifest 是否正常。

## 正式測別人 Skill 的建議指令

```bash
python src/run_benchmark.py ^
  --model ollama:gemma3:12b ^
  --defense skill_only ^
  --custom-skill-file defenses/custom/company_skill.md ^
  --official-mode
```

自訂 Skill 仍維持 v18 的企業版設計：`custom_only`，不追加內建 Skill。
