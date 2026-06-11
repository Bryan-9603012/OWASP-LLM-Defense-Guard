# CMD 內滑鼠點選模型選單

這版不是跳出 GUI 視窗，而是在 Windows CMD / Windows Terminal 的終端機畫面中直接用滑鼠點選。

## 使用方式

先開 Terminal A：

```bat
ollama serve
```

再開 Terminal B：

```bat
cd envlogicproj_oneclick
python semi_auto_ollama.py
```

預設流程：

1. 檢查 Ollama `/api/tags`
2. 在 CMD 中畫出模型選單
3. 用滑鼠左鍵點選模型那一行
4. 自動進入模型檢查、攻擊資料集選擇、執行次數設定、benchmark、report 產生

## 操作方式

```text
滑鼠左鍵點某一行  直接選擇該項目
↑ / ↓              鍵盤備援移動
Enter              確認目前反白項目
Esc                取消
1-9                快速跳到對應選項
```

## 備援模式

如果學校電腦的 CMD 滑鼠事件被攔截，可以用：

```bat
python semi_auto_ollama.py --tui
```

強制使用方向鍵選單。

或：

```bat
python semi_auto_ollama.py --simple
```

強制使用數字選單。

如果真的想要跳出 GUI 視窗，可以用：

```bat
python semi_auto_ollama.py --gui
```

## 注意事項

Windows CMD 的 QuickEdit 模式有時會攔截滑鼠，造成滑鼠只是在反白文字而不是送出 click event。本腳本會嘗試暫時關閉 QuickEdit 並啟用 mouse input；如果仍失敗，會自動退回鍵盤選單。
