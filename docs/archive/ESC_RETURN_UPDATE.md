# ESC 返回行為更新

本版將互動流程統一成：

- 選單畫面：按 `Esc` 返回上一層。
- 第一層主選單：按 `Esc` 等同離開。
- 手動輸入畫面：按 `Esc` 返回上一層，不需要輸入 `b`、`back` 或 `q`。
- 確認畫面：按 `Esc` 視為取消，不執行下載、加入清單等副作用動作。

## 已套用的輸入畫面

- 手動輸入模型名稱
- 新增模型到清單
- 新增並下載模型
- 手動輸入 attacks 檔案路徑
- 輸入本次執行次數
- 按 Enter 返回的等待畫面

## 建議操作

在 CMD / PowerShell / Windows Terminal 中：

```bat
python semi_auto_ollama.py
```

方向鍵選單可用：

- `↑ / ↓` 移動
- `Enter` 確認
- `Esc` 返回

如果互動選單異常，可使用：

```bat
python semi_auto_ollama.py --simple
```
