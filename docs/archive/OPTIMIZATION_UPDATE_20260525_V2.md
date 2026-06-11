# Optimization Update 2026-05-25 v2

本版在既有 defense mode 版本上做「工具化」優化，沒有改動 leak level scoring、valid_sample / invalid 核心邏輯，也沒有把外層 filter 混進主實驗。

## 新增功能

### 1. CLI quick test

用於快速驗證流程，不必手動設定 N=1、language=en、runs=1。

```bash
python src/run_benchmark.py --model mock --quick-test --defense skill_defense
python src/run_benchmark.py --model ollama:gemma3:12b --quick-test --defense skill_defense
```

效果：

```text
1 base attack × English only × 1 run
```

### 2. CLI plan-only

只列出本次會跑哪些 attack cases 與預期樣本數，不呼叫模型。

```bash
python src/run_benchmark.py --model mock --attack-ids A01,A02 --styles en_pure --runs 3 --defense none --plan-only
```

用途：正式跑之前確認 attack IDs、language、runs 是否選對。

### 3. CLI confirm

正式呼叫模型前顯示確認畫面。

```bash
python src/run_benchmark.py --model ollama:gemma3:12b --defense skill_defense --confirm
```

### 4. 互動式流程新增生成參數設定

`semi_auto_ollama.py` 現在會在選擇：

```text
模型 → 測試範圍 → 防禦模式 → 測試次數
```

之後新增：

```text
生成參數設定
```

可選：

```text
Default formal params
Custom params
```

目前 default：

```text
max_tokens=300
temperature=0.0
top_p=1.0
top_k=40
num_ctx=4096
seed=42
```

### 5. 互動式流程新增確認畫面

開始正式測試前會顯示：

```text
Models
Scope
Styles
Attack IDs
Base limit
Defense
Runs
Max tokens
Temperature
Expected samples
```

只有輸入 `Y` 才會開始。

### 6. Benchmark Config 顯示更完整

`src/run_benchmark.py` 的執行畫面新增：

```text
Base attacks
Expected rows
Max tokens
Temperature
```

方便確認正式實驗設定。

## 不變項

以下邏輯未更動：

```text
Leak Level 0–4
valid_sample / invalid
TRUNCATED_RESPONSE 判斷
format_violation 判斷
Defense Score 計算
raw response 保存
report generation
```

## 建議使用方式

### 先做 plan-only

```bash
python src/run_benchmark.py --model mock --attack-ids A01,A02 --styles all --runs 3 --defense skill_defense --plan-only
```

### 再做 quick test

```bash
python src/run_benchmark.py --model ollama:gemma3:12b --quick-test --defense skill_defense
```

### 最後跑正式測試

```bash
python src/run_benchmark.py --model ollama:gemma3:12b --attacks attacks/attacks.json --styles all --runs 3 --limit-base-attacks 20 --defense skill_defense --temperature 0 --top-p 1 --top-k 40 --num-ctx 4096 --max-tokens 300 --seed 42 --confirm
```
