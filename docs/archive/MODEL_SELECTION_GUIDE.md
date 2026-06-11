# 🎯 模型選擇和批量測試指南

## 📋 概述

LLM Secret Guard 現在支援**三種測試模式**：
1. **互動式模式** - 選擇單一或批量測試
2. **單一模型測試** - 測試一個模型並生成報告
3. **批量模型測試** - 同時測試多個模型

---

## 🚀 快速開始

### 進入交互式菜單（推薦首次使用）
```cmd
.\run.ps1 -Interactive
```

**輸出**:
```
========================================
Test Mode Selection
========================================

1) Single Model Test (choose one model)
2) Batch Test (test multiple models)
0) Exit

Select mode (number): _
```

### 單一模型測試
```cmd
.\run.ps1 -SingleTest
```

### 批量模型測試
```cmd
.\run.ps1 -BatchTest
```

---

## 📌 詳細使用說明

### 1️⃣ 交互式單一模型測試 (-SingleTest)

**命令**:
```cmd
.\run.ps1 -SingleTest
```

**流程**:
```
1. 顯示可用模型列表
   - mock (內置快速模型)
   - 已安裝的 Ollama 模型清單
   
2. 選擇模型或下載新模型
   - 選擇編號選擇現有模型
   - 選擇 99 下載新模型
   
3. 自動執行
   - 設置虛擬環境
   - 安裝依賴
   - 運行基準測試
   - 生成報告
```

**範例對話**:
```
========================================
Model Selection
========================================

Available models:
  1) mock (Built-in, fast)

  Installed Ollama Models:
  2) llama2
  3) mistral

  99) Download new model
  0)  Exit

Select model (number): 1

========================================
Single Model Test
========================================

[INFO]  Setup environment...
[OK]    Venv already exists
[INFO]  Starting benchmark...
[OK]    Benchmark complete
[INFO]  Generating report...
[OK]    Report generated

========================================
Complete!
========================================

[OK]    Test finished for model: mock
```

### 2️⃣ 交互式批量模型測試 (-BatchTest)

**命令**:
```cmd
.\run.ps1 -BatchTest
```

**流程**:
```
1. 列出所有可用模型
   - mock (內置模型)
   - 所有已安裝的 Ollama 模型
   
2. 選擇要測試的模型
   - 輸入編號 (逗號分隔) 例: 1,2,3
   - 或輸入 "all" 測試所有模型
   
3. 自動執行所有測試
   - 逐個運行每個模型的基準測試
   - 每個模型完成後自動進行下一個
   - 最後生成合併報告
```

**範例對話**:
```
========================================
Batch Model Test
========================================

Available models to test:
  [  ] 1. mock
  [  ] 2. ollama:llama2
  [  ] 3. ollama:mistral

Enter model numbers to test (comma-separated, e.g., 1,2,3 or 'all'):
Selection: all

========================================
Starting batch tests
========================================

[INFO]  Testing: mock
[OK]    Benchmark complete
[INFO]  Testing: ollama:llama2
[OK]    Benchmark complete
[INFO]  Testing: ollama:mistral
[OK]    Benchmark complete
[INFO]  Generating combined report...
[OK]    Report generated

========================================
Batch Complete!
========================================

[OK]    Tested 3 models
  * mock
  * ollama:llama2
  * ollama:mistral
```

### 3️⃣ 下載新模型

在模型選擇時，選擇選項 **99** 下載新模型：

```
Select model (number): 99
Enter model name (e.g., llama2, mistral, neural-chat): neural-chat

========================================
Downloading Model
========================================

[INFO]  Downloading: neural-chat
[INFO]  This may take several minutes...
[OK]    Model downloaded successfully

========================================
Model Selection
========================================

Available models:
  1) mock (Built-in, fast)

  Installed Ollama Models:
  2) neural-chat

  99) Download new model
  0)  Exit
```

---

## 📊 可用模型列表

### 內置模型 (始終可用)
| 模型 | 說明 | 速度 | 大小 |
|------|------|------|------|
| **mock** | 模擬模型（用於測試） | ⚡⚡⚡ | < 1 MB |

### Ollama 推薦模型 (需要下載)
| 模型 | 參數量 | 大小 | 說明 |
|------|--------|------|------|
| **llama2** | 7B | ~3.8 GB | Meta 開源模型，性能均衡 |
| **mistral** | 7B | ~4.1 GB | 高效模型，較快推理 |
| **neural-chat** | 7B | ~4.0 GB | 對話優化模型 |
| **orca-mini** | 3B | ~1.9 GB | 輕量級模型 |
| **phi** | 2.7B | ~1.6 GB | 超輕量級模型 |

### 下載模型示例
```cmd
# 互動式下載
.\run.ps1 -SingleTest
# 然後選擇 99，輸入模型名稱

# 或使用命令行直接下載 (需要已安裝 Ollama)
ollama pull llama2
ollama pull mistral
ollama pull neural-chat
```

---

## 🎯 常見使用場景

### 場景 1: 快速測試 Mock 模型
```cmd
.\run.ps1 -Interactive
# 選擇 1 (Single Model Test)
# 選擇 1 (mock)
# 自動完成，耗時 ~30 秒
```

### 場景 2: 測試單個 Ollama 模型
```cmd
# 首先確保模型已下載
ollama pull llama2

# 然後運行測試
.\run.ps1 -SingleTest
# 選擇 llama2 編號
```

### 場景 3: 比較多個模型
```cmd
.\run.ps1 -BatchTest
# 選擇 "all" 測試所有已安裝的模型
# 自動生成對比報告
```

### 場景 4: 測試特定模型組合
```cmd
.\run.ps1 -BatchTest
# 輸入: 1,2,3
# 測試 mock + llama2 + mistral
```

### 場景 5: 下載新模型後測試
```cmd
.\run.ps1 -SingleTest
# 選擇 99 下載新模型
# 下載完成後自動運行測試
```

---

## 📋 命令參考

### 交互式命令
```cmd
# 進入互動選擇菜單
.\run.ps1 -Interactive

# 直接進入單一模型測試
.\run.ps1 -SingleTest

# 直接進入批量模型測試
.\run.ps1 -BatchTest
```

### 信息命令
```cmd
# 列出所有已安裝的 Ollama 模型及其大小
.\run.ps1 -ListModels

# 檢查系統依賴
.\run.ps1 -CheckDeps
```

### 傳統命令 (支持自動指定模型)
```cmd
# 測試指定模型
.\run.ps1 -Full -Model mock
.\run.ps1 -Full -Model ollama:llama2

# 只運行測試
.\run.ps1 -Test -Model ollama:mistral

# 只生成報告
.\run.ps1 -Report
```

---

## 🔧 進階配置

### 環境變數自訂

建立 `.env` 文件在專案根目錄 (可選):
```bash
MODEL_TIMEOUT=60
OLLAMA_URL=http://localhost:11434
LOG_LEVEL=DEBUG
```

### 模型配置文件

編輯 `automation_config.json`:
```json
{
  "automation": {
    "models": [
      {
        "name": "mock",
        "type": "mock",
        "enabled": true,
        "description": "Mock model for testing",
        "timeout": 30,
        "requires": []
      },
      {
        "name": "llama2",
        "type": "ollama",
        "enabled": true,
        "description": "Meta's Llama 2 model",
        "timeout": 300,
        "requires": ["ollama", "wsl"]
      }
    ]
  }
}
```

---

## 🐛 故障排除

### ❌ "Ollama not available"

**原因**: Ollama 服務未運行

**解決方案**:
```cmd
# 1. 確認 Ollama 已安裝
.\run.ps1 -CheckDeps

# 2. 啟動 Ollama 服務
ollama serve

# 3. 在新終端運行測試
.\run.ps1 -SingleTest
```

### ❌ "No models installed"

**原因**: Ollama 沒有下載任何模型

**解決方案**:
```cmd
# 方法 1: 互動式下載
.\run.ps1 -SingleTest
# 選擇 99 並輸入模型名稱

# 方法 2: 命令行下載
ollama pull llama2
```

### ❌ 模型下載超時

**原因**: 網絡連接或模型太大

**解決方案**:
```cmd
# 1. 檢查網絡連接
ping ollama.ai

# 2. 下載較小的模型
ollama pull orca-mini

# 3. 手動增加超時
# 編輯 automation_config.json 中的 timeout 值
```

### ❌ 虛擬環境問題

**原因**: venv 損壞或不相容

**解決方案**:
```cmd
# 清理並重建虛擬環境
rmdir /s venv
.\run.ps1 -Setup

# 然後重新運行測試
.\run.ps1 -SingleTest
```

---

## 💡 最佳實踐

### ✅ 開始測試前

1. 檢查依賴:
```cmd
.\run.ps1 -CheckDeps
```

2. 確認 Ollama 正在運行 (如果使用 Ollama 模型):
```cmd
ollama serve
```

3. 如需要，啟動 WSL 服務:
```cmd
wsl --update
```

### ✅ 首次測試流程

```cmd
# 1. 檢查環境
.\run.ps1 -CheckDeps

# 2. 進入互動菜單
.\run.ps1 -Interactive

# 3. 選擇單一測試
# 4. 選擇 mock 模型
# 5. 自動完成，查看報告
```

### ✅ 多模型對比

```cmd
# 1. 下載多個模型
ollama pull llama2
ollama pull mistral

# 2. 運行批量測試
.\run.ps1 -BatchTest

# 3. 選擇 "all"
# 4. 等待所有模型完成
# 5. 查看對比報告
```

---

## 📊 報告輸出

### 單一模型報告
```
reports/
├─ report_mock.md           (Mock 模型報告)
├─ report_ollama_llama2.md  (Llama2 報告)
└─ report_ollama_mistral.md (Mistral 報告)
```

### 測試結果
```
results/
├─ results_mock.csv           (Mock 測試數據)
├─ results_ollama_llama2.csv  (Llama2 測試數據)
└─ results_ollama_mistral.csv (Mistral 測試數據)
```

### 查看報告
```cmd
# 打開最新的 Mock 報告
start reports\report_mock.md

# 查看所有報告
dir reports\*.md
```

---

## 🎓 進階技巧

### 並行模型測試
```cmd
# 在不同終端分別測試不同模型
.\run.ps1 -Full -Model mock
.\run.ps1 -Full -Model ollama:llama2
```

### 只下載模型不測試
```cmd
# 互動式選擇 99 下載
.\run.ps1 -SingleTest
# 選擇 99，下載完成後選擇 0 退出
```

### 重新測試而不清理數據
```cmd
# 只運行測試
.\run.ps1 -Test -Model mock
```

### 生成新報告
```cmd
# 基於現有結果生成報告
.\run.ps1 -Report
```

---

## 📚 相關文檔

- **QUICK_START.md** - 5 分鐘快速開始
- **AUTOMATION_GUIDE.md** - 完整詳細指南
- **AUTOMATION_SUMMARY.md** - 實施總結
- **README.md** - 專案說明

---

## ✅ 驗證清單

使用新功能時的檢查清單：

- [ ] 運行 `.\run.ps1 -CheckDeps` 驗證環境
- [ ] 如需 Ollama 模型，先運行 `ollama serve`
- [ ] 使用 `.\run.ps1 -Interactive` 進入菜單
- [ ] 選擇 -SingleTest 或 -BatchTest
- [ ] 等待測試完成
- [ ] 查看 `reports/` 中的結果
- [ ] 檢查 `results/` 中的數據

---

**版本**: 1.0 | **最後更新**: 2026-04-29 | **狀態**: ✅ 完成
