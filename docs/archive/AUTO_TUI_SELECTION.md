# Auto TUI Selection Mode

本版本的 `semi_auto_ollama.py` 已改成自動偵測選單模式：

- 支援互動式終端機：使用 opencode 風格選單，可用 `↑ / ↓` 選擇、`Enter` 確認。
- 不支援互動式終端機：自動退回數字選單。
- 如果方向鍵顯示異常，可以手動加上 `--simple` 強制使用數字選單。

## 使用方式

```bat
python semi_auto_ollama.py
```

強制數字選單：

```bat
python semi_auto_ollama.py --simple
```

## 操作鍵

- `↑ / ↓`：移動選項
- `Enter`：確認
- `Esc`：取消
- `1-9`：快速跳到指定選項
