# Model List Flow

這版流程採用穩定的終端機方向鍵選單，不使用滑鼠點選，也不使用 prompt_toolkit 全螢幕介面。

## 主要改動

1. 模型選單標題只保留「選擇 Ollama 模型」。
2. 操作說明移到 `README.md`。
3. 模型顯示格式改為：`模型名 : 下載狀態`。
4. 原本的「下載新模型並加入清單」改為「查看 / 變更模型清單」。
5. 清單管理可新增並下載模型、只新增模型、或從清單移除模型。
6. 執行模式支援：
   - 跑單個模型
   - 跑 `model_list.txt` 清單中的模型

## 使用

```bat
python semi_auto_ollama.py
```

如果方向鍵選單異常：

```bat
python semi_auto_ollama.py --simple
```
