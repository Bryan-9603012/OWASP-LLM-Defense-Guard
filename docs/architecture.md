# 專案架構說明

## V1：固定題庫 Benchmark

```text
protected_data.txt
        ↓
system_prompt.txt
        ↓
attacks.json
        ↓
run_benchmark.py
        ↓
Target LLM Client
        ↓
leak_detector.py
        ↓
results.csv
        ↓
report_generator.py
        ↓
report.md
```

## 設計原則

1. 固定 flag
2. 固定 system prompt
3. 固定 attacks.json
4. 固定模型參數
5. 單輪測試每題重新建立 session
6. 多輪測試固定輪數與固定內容
7. 不根據 AI 回覆臨時追加問題

## V2：AI vs AI 自動攻防

```text
Attacker LLM
        ↓
Target LLM
        ↓
Judge / Detector
        ↓
Attacker LLM 調整下一輪攻擊
```

V2 放在 `src/agents/` 中擴充。
