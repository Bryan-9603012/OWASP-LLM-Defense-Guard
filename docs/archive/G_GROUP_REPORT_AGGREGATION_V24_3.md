# G-Group Report Aggregation v24.3

本版本只修正報表聚合，不改 Host LLM 防禦核心、attack set、scoring、invalid 判斷或 UI 主流程。

## 問題

v24.1 / v24.2 已能執行 G0/G1/G5/G6/G7，但部分 summary 報表仍以底層 `defense_id` 聚合。由於 G5、G6、G7 的底層模式都可能是 `full_guard`，正式分析時會被混在一起。

## 修正

新增欄位：

- `g_group_id`
- `g_group_name`
- `experiment_group_id`
- `experiment_group_name`

新增報表：

- `summary_by_g_group.csv`
- `g_group_core_comparison.csv`
- `defense_summary_by_g_group.csv`
- `enterprise_assessment_by_g_group.csv`
- `response_action_summary_by_g_group.csv`
- `guard_mitigation_by_g_group.csv`
- `invalid_breakdown_by_g_group.csv`
- `attack_g_group_matrix.csv`
- `language_g_group_effectiveness.csv`

## 相容性

新產生的資料會直接寫入 G-group 欄位。舊 v24.1/v24.2 pilot CSV 若沒有這些欄位，report generator 會從 `attack_set` / run-name 內的 `__group_Gx__` 自動推回。

## 正式分析建議

正式比較 G5/G6/G7 時，優先使用：

1. `g_group_core_comparison.csv`
2. `guard_mitigation_by_g_group.csv`
3. `response_action_summary_by_g_group.csv`
4. `invalid_breakdown_by_g_group.csv`

`summary_by_defense.csv` 保留給底層防禦模組分析，不建議用它直接比較 G5/G6/G7。
