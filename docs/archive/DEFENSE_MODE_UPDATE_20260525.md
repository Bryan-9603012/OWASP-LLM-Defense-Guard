# Defense Mode Update 2026-05-25

本版本在既有正式實驗腳本上加入 `defense` 入口，沒有重寫 scoring / leak detector / invalid 邏輯。

## 新增內容

### 1. Defense 規則資料夾

```text
defenses/
├── defense_config.json
├── no_defense.txt
├── prompt_defense.txt
└── skill_defense.txt
```

目前內建三種主實驗防禦模式：

| defense_id | 名稱 | 類型 | 說明 |
|---|---|---|---|
| `none` | No Defense | `none` | baseline，不額外注入防禦規則 |
| `prompt_defense` | Prompt Defense | `inner_prompt` | 一般 system prompt 防洩漏規則 |
| `skill_defense` | Skill Defense | `inner_skill` | 結構化 LLM02 防禦 skill |

### 2. CLI 新增參數

```bash
python src/run_benchmark.py --model mock --defense none
python src/run_benchmark.py --model ollama:gemma3:12b --defense prompt_defense
python src/run_benchmark.py --model ollama:gemma3:12b --defense skill_defense
```

可指定自訂 defense config：

```bash
python src/run_benchmark.py --model mock --defense skill_defense --defense-config defenses/defense_config.json
```

### 3. 實驗流程

正式流程可採用：

```text
選模型
→ 選攻擊範圍
→ 選語言範圍
→ 選防禦模式
→ 輸入測試次數
→ 輸入 max_tokens / temperature 等參數
→ 開始測試
→ 查看結果與報表
```

### 4. Metadata 新增欄位

每筆 raw result 會記錄：

```text
defense_id
defense_name
defense_type
defense_prompt_file
defense_prompt_hash
defense_prompt_length_chars
base_system_prompt_hash
system_prompt_hash
```

其中：

- `base_system_prompt_hash`：原始 system prompt hash。
- `system_prompt_hash`：注入 defense 後的實際 system prompt hash。
- `defense_prompt_hash`：防禦規則檔案內容 hash，用來確認同批實驗使用同一版防禦規則。

### 5. 互動式選單更新

`semi_auto_ollama.py` 已加入「選擇防禦模式」步驟，會將選到的 defense mode 傳給 `src/run_benchmark.py`。

## 重要限制

本次加入的是 inner defense injection：

```text
載入防禦規則 → 注入 system prompt → LLM 回答 → 保存 raw response → scoring
```

目前沒有加入 outer defense 行為，例如：

```text
輸出後攔截
輸出後重寫
unsafe retry
自動 redaction
```

這樣可以保持主實驗仍然是在測模型/skill 的內層防禦能力，而不是測外部 filter。
