# 🎯 模型選擇快速參考卡

## 🚀 三步快速開始

### 第 1 步: 選擇測試模式
```cmd
.\run.ps1 -Interactive
```

### 第 2 步: 選擇模型
- **Single Test**: 測試一個模型 ✓
- **Batch Test**: 測試多個模型 ✓

### 第 3 步: 查看結果
```cmd
start reports\report_*.md
```

---

## 🎛️ 快速命令

### 交互式菜單（推薦）
```cmd
.\run.ps1 -Interactive          # 完整菜單
.\run.ps1 -SingleTest           # 快速進入單一測試
.\run.ps1 -BatchTest            # 快速進入批量測試
```

### 模型信息
```cmd
.\run.ps1 -ListModels           # 列出已安裝的 Ollama 模型
.\run.ps1 -CheckDeps            # 驗證系統依賴
```

### 傳統命令
```cmd
.\run.ps1 -Full -Model mock                    # 測試 Mock
.\run.ps1 -Full -Model ollama:llama2           # 測試 Llama2
.\run.ps1 -Test -Model mock                    # 只運行測試
.\run.ps1 -Report                              # 只生成報告
```

---

## 📋 模型清單

### 內置模型
| 模型 | 大小 | 速度 | 何時使用 |
|------|------|------|---------|
| **mock** | < 1 MB | ⚡⚡⚡ | 快速測試 |

### Ollama 推薦模型
| 模型 | 大小 | 速度 | 何時使用 |
|------|------|------|---------|
| **orca-mini** | 1.9 GB | ⚡⚡ | 快速原型 |
| **phi** | 1.6 GB | ⚡⚡⚡ | 超輕量 |
| **neural-chat** | 4.0 GB | ⚡ | 對話優化 |
| **mistral** | 4.1 GB | ⚡ | 高效模型 |
| **llama2** | 3.8 GB | ⚡ | 性能均衡 |

### 下載模型
```cmd
# 互動式下載 (推薦)
.\run.ps1 -SingleTest
# 選擇 99 → 輸入模型名稱

# 命令行下載
ollama pull llama2
ollama pull mistral
ollama pull neural-chat
```

---

## 🎯 常見場景

### 🔹 快速測試 (30 秒)
```cmd
.\run.ps1 -Interactive
→ 選擇 1 (Single Test)
→ 選擇 1 (mock)
```

### 🔹 測試特定 Ollama 模型
```cmd
ollama pull llama2              # 先下載
.\run.ps1 -SingleTest           # 運行測試
# 選擇對應編號
```

### 🔹 對比多個模型
```cmd
.\run.ps1 -BatchTest
# 輸入: 1,2,3   (選擇多個編號)
# 或輸入: all   (測試全部)
```

### 🔹 下載新模型
```cmd
.\run.ps1 -SingleTest
# 選擇 99 → 輸入: neural-chat
# 下載完成後自動測試
```

### 🔹 自動完整流程
```cmd
.\run.ps1 -Full -Model mock
# 自動: 環境設置 → 依賴安裝 → 測試 → 報告
```

---

## 💾 結果位置

```
reports/              # 生成的報告
├─ report_mock.md
├─ report_ollama_llama2.md
└─ ...

results/              # 測試數據
├─ results_mock.csv
├─ results_ollama_llama2.csv
└─ ...
```

---

## 🔧 故障排除速查

| 問題 | 解決方案 |
|------|---------|
| "Ollama not available" | 運行 `ollama serve` |
| "No models installed" | 運行 `ollama pull llama2` |
| 虛擬環境錯誤 | 運行 `rmdir /s venv && .\run.ps1 -Setup` |
| 模型下載超時 | 嘗試較小的模型: `ollama pull orca-mini` |

---

## ✨ 提示

💡 **第一次使用?** → 運行 `.\run.ps1 -Interactive`

💡 **想快速測試?** → 運行 `.\run.ps1 -Full`

💡 **想對比模型?** → 運行 `.\run.ps1 -BatchTest` 後選 `all`

💡 **需要幫助?** → 運行 `.\run.ps1 -Help`

---

**詳細文檔**: 見 MODEL_SELECTION_GUIDE.md
