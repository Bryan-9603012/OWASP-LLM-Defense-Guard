# 中文介面更新紀錄（2026-05-25）

本版將互動式測試流程主要介面改為繁體中文，包含：

- 測試範圍選單
- 語言選擇提示
- 防禦模式選單
- 生成參數選單
- 實驗設定確認頁
- 執行中狀態訊息
- 結果摘要訊息
- 批次完成訊息

保留 `defense_id`、`style_id`、`attack_id`、`max_tokens`、`temperature`、`top_p`、`top_k`、`num_ctx`、`seed` 等技術欄位原名，避免影響 CSV、CLI 參數與後續資料分析。

防禦模式顯示名稱已改為中文：

| defense_id | 中文名稱 |
|---|---|
| none | 無防禦 |
| skill_only | 只使用 Skill 防禦 |
| input_guard | 只使用輸入檢查 |
| output_guard | 只使用輸出檢查 |
| full_guard | 完整防禦 |
| prompt_defense | 提示詞防禦（舊版相容） |
| skill_defense | Skill 防禦（舊版相容） |
