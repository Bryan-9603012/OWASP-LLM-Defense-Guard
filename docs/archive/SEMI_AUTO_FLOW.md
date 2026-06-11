# 兩終端機半自動 Ollama 測試流程

這個流程刻意不做全自動環境管理。

設計原則：

- 使用者自己先啟動 Ollama server。
- 測試腳本只負責選模型、必要時安裝模型、跑 benchmark、產生 report。
- 腳本不會自動啟動或停止 Ollama。
- 不設定 timeout，避免慢模型被誤判成錯誤。
- 錯誤會保留原因，例如 `OLLAMA_UNREACHABLE`、`HTTP_404`、`MODEL_NOT_FOUND`、`PROCESS_CRASH`。

## Terminal A：啟動 Ollama

```bash
ollama serve
```

這個終端機保持開著，不要關掉。

## Terminal B：執行測試流程

```bash
cd llm-secret-guard
python3 semi_auto_ollama.py
```

若 WSL / Windows localhost 對應不同，可以指定 URL：

```bash
OLLAMA_URL=http://127.0.0.1:11434 python3 semi_auto_ollama.py
```

## 流程

1. 檢查 Ollama API 是否可連線。
2. 列出目前已安裝模型。
3. 詢問使用者要測試哪個模型。
4. 如果模型不存在，詢問是否執行 `ollama pull <model>`。
5. 模型安裝完成後執行 benchmark。
6. 產生 report。
7. 結尾輸出測試結束、分數、ASR、Error Rate、錯誤原因與 report 路徑。

## 輸出

- `results/results_ollama_<model>.csv`
- `reports/report_ollama_<model>.md`

## 注意

如果出現：

```text
OLLAMA_UNREACHABLE
```

代表測試程式沒有連到 Ollama。請確認 Terminal A 的 `ollama serve` 還在執行，並確認 `OLLAMA_URL` 是否正確。


## 新增：攻擊資料集與圖表流程

目前半自動流程支援三種 attacks 檔案：

| 檔案 | 用途 |
|---|---|
| `attacks/attacks.json` | 原始 baseline |
| `attacks/attacks.json` | 20 類 × 1 筆，快速測試 |
| `attacks/attacks.json` | 20 類 × 5 筆，正式統計 |

執行 `python3 semi_auto_ollama.py` 時，流程會要求選擇 attacks 檔案。benchmark 結束後會自動執行：

```bash
python3 src/report_generator.py
python3 src/plot_benchmark.py
```

`src/plot_benchmark.py` 會使用 seaborn 產生：

| 輸出 | 說明 |
|---|---|
| `reports/figures/model_ranking.png` | 模型 Secret Protection Score 排名 |
| `reports/figures/failed_attack_categories.png` | 最常失敗的攻擊類別 |
| `reports/figures/model_ranking.csv` | 模型排名統計表 |
| `reports/figures/failed_categories.csv` | 攻擊類別失敗統計表 |

若只想針對 100 筆資料集畫圖：

```bash
python3 src/plot_benchmark.py --attack-set attacks
```
