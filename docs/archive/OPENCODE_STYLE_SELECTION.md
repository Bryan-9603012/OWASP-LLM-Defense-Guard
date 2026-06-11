# Opencode-style 模型選擇功能

這版把 `semi_auto_ollama.py` 的模型選擇改成類似 opencode 的方向鍵選單。

## 使用方式

先在第一個終端機啟動 Ollama：

```bat
ollama serve
```

再在第二個終端機執行：

```bat
python semi_auto_ollama.py
```

## 操作方式

- `↑ / ↓`：上下選擇
- `Enter`：確認
- `Esc`：取消
- `1-9`：快速跳到對應項目

## 功能

1. 自動讀取已下載模型：來自 `http://127.0.0.1:11434/api/tags`。
2. 顯示常用模型清單：來自 `model_list.txt`。
3. 已下載模型會標示 `[已下載]`。
4. 清單內但尚未下載的模型會標示 `[未下載 / 清單]`。
5. 選到未下載模型時，會詢問是否執行 `ollama pull <model>`。
6. 手動輸入或下載新模型後，可加入 `model_list.txt`。

## 注意

如果終端機不支援方向鍵互動，程式會自動退回數字選單，不會壞掉。
