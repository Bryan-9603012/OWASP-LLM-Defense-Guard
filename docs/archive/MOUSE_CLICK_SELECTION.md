# 滑鼠點選模型功能

這版把模型選擇改成預設使用滑鼠點選視窗。

## 預設行為

執行：

```bat
python semi_auto_ollama.py
```

流程會先檢查 Ollama API，讀取已下載模型，接著彈出一個小視窗：

- 用滑鼠點選模型
- 按「確定 / Start」確認
- 也可以雙擊模型直接確認
- Esc 或「取消」可離開

如果滑鼠視窗無法開啟，程式會自動退回：

1. opencode 風格方向鍵選單
2. 數字選單

## 備用模式

強制使用方向鍵選單：

```bat
python semi_auto_ollama.py --tui
```

強制使用數字選單：

```bat
python semi_auto_ollama.py --simple
```

## 模型清單

常用模型會保存在：

```text
model_list.txt
```

如果選到不在清單內的模型，程式會詢問是否加入清單，方便下次直接點選。

## 注意

這個功能使用 Python 內建的 `tkinter`，Windows 的 Python 通常會內建，不需要額外安裝套件。
