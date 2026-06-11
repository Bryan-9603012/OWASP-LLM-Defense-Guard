# v0.16 Compare Runner Debug 修正說明

本版針對互動式介面中 `compare_basic` / `compare_all` 的執行顯示進行 debug 與強化。

## 問題背景

在比較模式下，使用者會在確認頁看到：

- `none`
- `skill_only`
- `output_guard`
- `full_guard`

但實際執行畫面中，每一次 `run_benchmark.py` 呼叫都只會帶入單一：

```bash
--defense full_guard
```

這容易讓人誤以為 compare mode 沒有正確展開。

## 實際設計

`semi_auto_ollama.py` 的 compare mode 是由外層 runner 展開：

```text
compare_basic
  ├── run_benchmark.py --defense none
  ├── run_benchmark.py --defense skill_only
  ├── run_benchmark.py --defense output_guard
  └── run_benchmark.py --defense full_guard
```

因此每一條指令只會有一個 `--defense` 是正常的。

## 本版修正

1. 確認頁新增「執行方式」說明，明確列出會依序執行的 defense ids。
2. 執行前新增「比較模式展開」區塊。
3. 每次執行指令前顯示目前是第幾組防禦，例如 `第 3/4 組：output_guard`。
4. 合併報告資料夾新增 `compare_plan.json`，記錄 compare mode 展開後的 defense ids 與 collected CSVs。
5. 若 compare mode 缺少預期防禦組，會在確認頁與執行前顯示警告。

## 判讀方式

若畫面顯示：

```text
[比較模式] 目前執行第 4/4 組：full_guard
[執行] ... --defense full_guard ...
```

代表目前正在跑第 4 組，不代表只跑 `full_guard`。

跑完後可查看：

```text
reports/compare_<model>_<plan>_<scope>/compare_plan.json
```

確認本次比較是否包含所有 defense modes。
