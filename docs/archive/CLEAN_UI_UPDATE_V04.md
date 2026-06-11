# Clean UI Update v0.4

本版重點是把互動式介面整理成較乾淨的正式工具樣式。

## 主要變更

- 選單不再把所有說明塞在每個選項後面。
- 目前選到的項目會在下方顯示說明。
- 主選單簡化為：小模型測試 / 中模型測試 / 單一模型 / 離開。
- 測試範圍頁簡化為：快速測試 / 完整測試 / 依語言測試 / 依攻擊測試 / 自訂測試。
- 防禦模式頁只顯示防禦名稱，技術 ID 放在下方說明。
- Skill Profile 頁只顯示 profile 名稱，完整說明放在下方說明。
- 實驗確認頁改成精簡摘要，只保留模型、範圍、防禦、Skill、自訂規則、次數、參數與預估樣本。
- 修正自訂規則流程，現在會正確把 custom rules 傳入執行流程。

## 保留的能力

- `none / skill_only / input_guard / output_guard / full_guard`
- Skill Profile
- 自訂 Skill / Input Guard / Output Guard 規則
- raw / final response 分離
- CSV 與報表欄位記錄

## 建議測試流程

先使用：

```bash
python semi_auto_ollama.py
```

選擇：

```text
小模型測試 → 開始測試 → 快速測試 → full_guard → minimal → 不使用自訂規則 → runs=1 → 使用正式預設
```
