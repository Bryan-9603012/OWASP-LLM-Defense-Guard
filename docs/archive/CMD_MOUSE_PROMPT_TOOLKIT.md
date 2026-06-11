# CMD 內滑鼠點選模型選單

這版改用 `prompt_toolkit` 做終端機內的滑鼠選單。

## 重點

- 不會跳出 GUI 視窗。
- 選單仍然在 CMD / PowerShell / Windows Terminal 裡面。
- 可以用滑鼠點選項目。
- 也可以用方向鍵移動，Enter 確認。
- 如果環境不支援，會退回方向鍵或數字選單。

## 執行

```bat
cd envlogicproj_oneclick
python semi_auto_ollama.py
```

## 如果沒有安裝依賴

```bat
pip install -r requirements.txt
```

或只安裝滑鼠選單依賴：

```bat
pip install prompt_toolkit
```

## 備援模式

強制方向鍵選單：

```bat
python semi_auto_ollama.py --tui
```

強制數字選單：

```bat
python semi_auto_ollama.py --simple
```

## 注意

舊版 CMD 的 QuickEdit 可能會攔截滑鼠選取。如果滑鼠點了只是在反白文字，請優先使用 Windows Terminal 或 PowerShell。
