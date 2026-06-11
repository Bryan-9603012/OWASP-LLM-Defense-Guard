# 🎯 自動化實施總結

## ✅ 已完成的工作

您的 LLM Secret Guard 專案已完全自動化，包含 **WSL 和 Ollama 依賴檢查及自動安裝**。

---

## 📦 已建立的自動化工具

### 1. **主要自動化腳本**

#### PowerShell 腳本 (`run.ps1`)
完整的 Windows PowerShell 自動化工具，支援：
- ✅ 依賴檢查 (Python, WSL, Ollama)
- ✅ 自動安裝缺失依賴
- ✅ 虛擬環境設置
- ✅ 依賴安裝
- ✅ 基準測試執行
- ✅ 報告生成
- ✅ 多模型支援 (Mock, Ollama)

#### 批處理啟動器 (`run.bat`)
簡單的 Windows 批處理檔，自動調用 PowerShell 腳本

#### 多模型測試腳本 (`run_multi_models.ps1`)
批量測試多個模型並生成合併報告

---

## 🚀 快速開始命令

### 檢查依賴
```cmd
.\run.ps1 -CheckDeps
```

**輸出範例**:
```
Status:
────────────────────
[OK]    Python
[OK]    WSL 2
[OK]    Ollama
────────────────────
```

### 自動安裝缺失的依賴
```cmd
.\run.ps1 -AutoInstall
```

### 完整自動化流程 (推薦)
```cmd
.\run.ps1 -Full -Model mock
```

或使用批處理檔：
```cmd
.\run.bat -Full
```

### 其他有用命令
```cmd
.\run.ps1 -Setup              # 只設置環境
.\run.ps1 -Test -Model mock   # 只運行測試
.\run.ps1 -Report             # 只生成報告
.\run.ps1 -Clean              # 清理輸出
.\run.ps1 -ListModels         # 列出 Ollama 模型
.\run.ps1 -Help               # 顯示幫助
```

---

## 📋 所有可用選項

| 選項 | 說明 |
|------|------|
| `-CheckDeps` | 檢查 Python, WSL, Ollama 是否已安裝 |
| `-AutoInstall` | 交互式自動安裝缺失的依賴 |
| `-InstallWsl` | 安裝 WSL 2 (需要管理員) |
| `-InstallOllama` | 安裝 Ollama |
| `-ListModels` | 列出已安裝的 Ollama 模型 |
| `-Setup` | 建立虛擬環境並安裝 Python 依賴 |
| `-Test` | 運行基準測試 |
| `-Report` | 生成報告 |
| `-Full` | 完整流程 (Setup + Test + Report) |
| `-Clean` | 清理所有輸出文件 |
| `-Model <name>` | 指定模型 (預設: mock) |
| `-Help` | 顯示幫助 |

---

## 🔧 支援的模型

### Mock (始終可用)
```cmd
.\run.ps1 -Full -Model mock
```
- 速度: ⚡⚡⚡ 超快
- 要求: 無

### Ollama 本地模型 (需要 WSL + Ollama)
```cmd
.\run.ps1 -Full -Model ollama:llama2
.\run.ps1 -Full -Model ollama:mistral
.\run.ps1 -Full -Model ollama:neural-chat
```

**設置步驟**:
1. 運行: `.\run.ps1 -AutoInstall`
2. 選擇安裝 WSL 和 Ollama
3. 測試時自動加載模型

---

## 📊 當前系統狀態

### 環境檢查結果 (已驗證)
```
✅ Python              : 已安裝
✅ WSL 2               : 已安裝  
✅ Ollama              : 已安裝
```

### 最近生成的輸出
```
📁 reports/
   ├─ report_mock.md                    (Mock 模型報告)
   ├─ report_ollama_llama3.2_1b.md      (Ollama 報告)
   
📁 results/
   ├─ results_mock.csv                  (Mock 測試結果)
   ├─ results_ollama_llama3.2_1b.csv    (Ollama 測試結果)
```

---

## 📚 文檔指南

| 文件 | 說明 |
|------|------|
| **QUICK_START.md** | 📖 5 分鐘快速開始指南 |
| **AUTOMATION_GUIDE.md** | 📖 完整詳細文檔 (所有選項和技巧) |
| **run.ps1** | 🔧 主要 PowerShell 自動化腳本 |
| **run.bat** | 🔧 Windows 批處理啟動器 |
| **run_multi_models.ps1** | 🔧 多模型批量測試腳本 |
| **automation_config.json** | ⚙️ 自動化配置文件 |

---

## 🎯 常見使用場景

### 場景 1: 首次設置 (完整自動化)
```cmd
# 第 1 步：檢查依賴
.\run.ps1 -CheckDeps

# 第 2 步：自動安裝缺失的依賴
.\run.ps1 -AutoInstall

# 第 3 步：完整測試
.\run.ps1 -Full -Model mock

# 第 4 步：查看報告
start reports\report_mock.md
```

### 場景 2: 日常快速測試
```cmd
.\run.ps1 -Full -Model mock
```

### 場景 3: 測試 Ollama 本地模型
```cmd
# 確保已安裝
.\run.ps1 -CheckDeps

# 列出可用模型
.\run.ps1 -ListModels

# 測試特定模型
.\run.ps1 -Full -Model ollama:llama2
```

### 場景 4: 批量測試多個模型
```powershell
.\run_multi_models.ps1 -All -CombinedReport
```

### 場景 5: 清理並重新測試
```cmd
.\run.ps1 -Clean
.\run.ps1 -Full
```

---

## 🛠️ 故障排除

### ❌ 虛擬環境路徑問題
如果遇到 venv Scripts 路徑問題，手動重建：
```cmd
rmdir /s venv
.\run.ps1 -Setup
```

### ❌ Ollama 連接失敗
確保 Ollama 正在運行：
```cmd
# 檢查狀態
.\run.ps1 -ListModels

# 如果失敗，啟動 Ollama
ollama serve
```

### ❌ 執行策略錯誤
使用 PowerShell 管理員模式：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📈 工作流程圖

```
完整自動化流程 (.\run.ps1 -Full)
│
├─→ [依賴檢查]
│   ├─ Python ✅
│   ├─ WSL ✅
│   └─ Ollama ✅
│
├─→ [環境設置]
│   ├─ 建立虛擬環境 (venv/)
│   └─ 安裝依賴 (requirements.txt)
│
├─→ [基準測試]
│   ├─ 選擇模型
│   ├─ 執行測試
│   └─ 生成 CSV 結果
│
├─→ [報告生成]
│   ├─ 分析結果
│   └─ 生成 Markdown 報告
│
└─→ ✅ 完成！
```

---

## 💡 高級功能

### 自動安裝工作流程
```cmd
# 交互式自動安裝任何缺失的依賴
.\run.ps1 -AutoInstall

# 提示問題:
# - 是否安裝 WSL? (y/n)
# - 是否安裝 Ollama? (y/n)
```

### 多模型並行測試
```powershell
# 測試所有已安裝的模型
.\run_multi_models.ps1 -All

# 生成合併報告
.\run_multi_models.ps1 -All -CombinedReport
```

### 環境變數自訂
建立 `.env` 文件 (可選):
```bash
MODEL_TIMEOUT=30
OLLAMA_URL=http://localhost:11434
LOG_LEVEL=DEBUG
```

---

## ✅ 驗證清單

自動化工具已配置並驗證：

- [x] PowerShell 腳本語法正確
- [x] 依賴檢查功能完整
- [x] WSL 檢查工作正常
- [x] Ollama 檢查工作正常
- [x] 完整工作流程可執行
- [x] 報告生成成功
- [x] 所有文檔已建立
- [x] 快速啟動指南完成
- [x] 詳細使用指南完成

---

## 🚀 立即開始

### 最簡單的方式 (推薦)
```cmd
cd D:\screen\hc105\Documents\NPU\AIA-LLM_Attack_Test\can_ai_keep_a_secret\llm-secret-guard

# 檢查依賴
.\run.ps1 -CheckDeps

# 自動安裝缺失的依賴
.\run.ps1 -AutoInstall

# 運行完整流程
.\run.ps1 -Full

# 查看報告
start reports\report_mock.md
```

### 或使用批處理檔 (更簡單)
```cmd
cd D:\screen\hc105\Documents\NPU\AIA-LLM_Attack_Test\can_ai_keep_a_secret\llm-secret-guard
.\run.bat -Full
```

---

## 📞 文檔參考

- **快速開始**: 查看 [QUICK_START.md](QUICK_START.md)
- **完整指南**: 查看 [AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md)
- **配置**: 查看 [automation_config.json](automation_config.json)

---

## 🎉 完成！

您的 LLM Secret Guard 專案現已完全自動化，**無需 WSL 預安裝**：

✅ **依賴檢查**: 自動偵測 Python、WSL、Ollama
✅ **自動安裝**: 互動式安裝缺失的依賴
✅ **完整工作流**: 一鍵執行設置 → 測試 → 報告
✅ **多模型支援**: Mock 和 Ollama 模型
✅ **完整文檔**: 快速開始和詳細指南

**開始使用**: `.\run.ps1 -CheckDeps` 然後 `.\run.ps1 -Full`

---

**版本**: 1.0 | **最後更新**: 2026-04-29 | **狀態**: ✅ 完成
