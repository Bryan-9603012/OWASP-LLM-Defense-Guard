# 🎬 功能演示指南

## 📺 新增功能概述

本次更新為 LLM Secret Guard 添加了**三層級的模型選擇系統**：

```
┌─────────────────────────────────────────┐
│   .\run.ps1 -Interactive (推薦)        │
│   ↓                                     │
│  ┌──────────────────┬─────────────────┐ │
│  │                  │                 │ │
│  ↓                  ↓                 ↓ │
│ Single Test    Batch Test          Exit │
│  │                  │                   │
│  └──────────────────┴─────────────────┘ │
│        (詳見下方演示)                   │
└─────────────────────────────────────────┘
```

---

## 🎯 演示 1: 交互式單一模型測試

### 執行命令
```cmd
.\run.ps1 -SingleTest
```

### 流程演示

**步驟 1**: 顯示可用模型
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

Select model (number): _
```

**步驟 2a**: 選擇現有模型 (輸入 1)
```
Select model (number): 1

========================================
Single Model Test
========================================

[INFO]  Setup environment...
[INFO]  Creating venv...
[OK]    Venv created
[INFO]  Installing packages...
[OK]    Dependencies installed
[INFO]  Starting benchmark...
[INFO]  Model: mock
[OK]    Benchmark complete
[INFO]  Generating report...
[OK]    Report generated

========================================
Complete!
========================================

[OK]    Test finished for model: mock
```

**步驟 2b**: 下載新模型 (輸入 99)
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
  2) llama2
  3) mistral
  4) neural-chat

  99) Download new model
  0)  Exit

Select model (number): 4

[INFO]  Testing: neural-chat
[OK]    Benchmark complete
```

### 生成的結果
```
reports/report_mock.md                      ✅ 新生成
results/results_mock.csv                    ✅ 新生成
```

---

## 🎯 演示 2: 交互式批量模型測試

### 執行命令
```cmd
.\run.ps1 -BatchTest
```

### 流程演示

**步驟 1**: 列出所有可用模型
```
========================================
Batch Model Test
========================================

Available models to test:
  [  ] 1. mock
  [  ] 2. ollama:llama2
  [  ] 3. ollama:mistral
  [  ] 4. ollama:neural-chat

Enter model numbers to test (comma-separated, e.g., 1,2,3 or 'all'):
Selection: _
```

**步驟 2a**: 選擇特定模型 (輸入: 1,2,3)
```
Selection: 1,2,3

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

**步驟 2b**: 測試所有模型 (輸入: all)
```
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
[INFO]  Testing: ollama:neural-chat
[OK]    Benchmark complete
[INFO]  Generating combined report...
[OK]    Report generated

========================================
Batch Complete!
========================================

[OK]    Tested 4 models
  * mock
  * ollama:llama2
  * ollama:mistral
  * ollama:neural-chat
```

### 生成的結果
```
reports/
├─ report_mock.md                   ✅
├─ report_ollama_llama2.md          ✅
├─ report_ollama_mistral.md         ✅
└─ report_ollama_neural-chat.md     ✅

results/
├─ results_mock.csv                 ✅
├─ results_ollama_llama2.csv        ✅
├─ results_ollama_mistral.csv       ✅
└─ results_ollama_neural-chat.csv   ✅
```

---

## 🎯 演示 3: 完整交互式菜單

### 執行命令
```cmd
.\run.ps1 -Interactive
```

### 流程演示

**步驟 1**: 選擇測試模式
```
========================================
Test Mode Selection
========================================

1) Single Model Test (choose one model)
2) Batch Test (test multiple models)
0) Exit

Select mode (number): _
```

**如果選 1** (Single Model Test)
→ 進入演示 1 的流程

**如果選 2** (Batch Test)
→ 進入演示 2 的流程

**如果選 0** (Exit)
```
[INFO]  Exiting...
```

---

## 🎯 演示 4: 模型列表查詢

### 執行命令
```cmd
.\run.ps1 -ListModels
```

### 流程演示

**成功案例** (Ollama 正在運行)
```
========================================
Installed Ollama Models
========================================

[OK]    Installed:
  * llama2 (3.8 GB)
  * mistral (4.1 GB)
  * neural-chat (4.0 GB)
```

**失敗案例** (Ollama 未運行)
```
========================================
Installed Ollama Models
========================================

[FAIL]  Ollama not available
```

**解決方案**:
```cmd
# 啟動 Ollama 服務
ollama serve

# 在另一個終端執行
.\run.ps1 -ListModels
```

---

## 📊 演示 5: 完整使用流程

### 第一次使用的完整演示

**第 1 步**: 檢查依賴
```cmd
.\run.ps1 -CheckDeps
```

輸出:
```
========================================
Dependency Check
========================================

Status:
────────────────────
[OK]    Python
[OK]    WSL 2
[WARN]  Ollama (Optional)
────────────────────
```

**第 2 步**: 進入交互菜單
```cmd
.\run.ps1 -Interactive
```

輸出:
```
========================================
Test Mode Selection
========================================

1) Single Model Test (choose one model)
2) Batch Test (test multiple models)
0) Exit

Select mode (number): 1
```

**第 3 步**: 模型選擇 (輸入: 1)
```
========================================
Model Selection
========================================

Available models:
  1) mock (Built-in, fast)
  99) Download new model
  0)  Exit

Select model (number): 1
```

**第 4 步**: 測試執行
```
========================================
Single Model Test
========================================

[INFO]  Setup environment...
[OK]    Venv created
[INFO]  Installing packages...
[OK]    Dependencies installed
[INFO]  Starting benchmark...
[OK]    Benchmark complete
[INFO]  Generating report...
[OK]    Report generated

========================================
Complete!
========================================

[OK]    Test finished for model: mock
```

**第 5 步**: 查看報告
```cmd
start reports\report_mock.md
```

---

## 🎯 演示 6: 下載並測試新模型

### 完整流程

**第 1 步**: 進入測試
```cmd
.\run.ps1 -SingleTest
```

**第 2 步**: 選擇下載新模型 (輸入: 99)
```
Select model (number): 99
Enter model name (e.g., llama2, mistral, neural-chat): mistral
```

**第 3 步**: 自動下載並測試
```
========================================
Downloading Model
========================================

[INFO]  Downloading: mistral
[INFO]  This may take several minutes...
[INFO]  pulling manifest...
[OK]    Model downloaded successfully

========================================
Single Model Test
========================================

[INFO]  Starting benchmark...
[OK]    Benchmark complete
[INFO]  Generating report...
[OK]    Report generated

========================================
Complete!
========================================

[OK]    Test finished for model: ollama:mistral
```

**第 4 步**: 查看新報告
```cmd
start reports\report_ollama_mistral.md
```

---

## 📈 演示 7: 模型對比報告

### 執行批量測試獲得對比數據

```cmd
.\run.ps1 -BatchTest
# 選擇: all
```

### 生成的對比數據

**CSV 結果** (results_*.csv)
```
Model,Attack_Type,Leak_Score,Attempts,Success_Rate
mock,prompt_injection,0.35,100,35%
mock,fine_tuning,0.42,100,42%

llama2,prompt_injection,0.68,100,68%
llama2,fine_tuning,0.72,100,72%

mistral,prompt_injection,0.65,100,65%
mistral,fine_tuning,0.70,100,70%
```

**Markdown 報告** (reports_*.md)
```markdown
# LLM Secret Guard Report

## 模型: mock
- 總攻擊次數: 200
- 成功洩露: 77 次
- 成功率: 38.5%

## 模型: llama2
- 總攻擊次數: 200
- 成功洩露: 140 次
- 成功率: 70%

## 比較結論
llama2 相比 mock 更容易被攻擊...
```

---

## 🎨 UI 演示

### 顏色編碼

```
[OK]    操作成功 (綠色)
[FAIL]  操作失敗 (紅色)
[INFO]  信息提示 (青色)
[WARN]  警告提示 (黃色)
```

### 進度指示

```
┌────────────────────────────────────────┐
│ Setup environment                      │
├────────────────────────────────────────┤
│ [OK]    Venv created                   │
│ [OK]    Dependencies installed         │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│ Running Benchmark                      │
├────────────────────────────────────────┤
│ [INFO]  Model: mock                    │
│ [OK]    Benchmark complete             │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│ Generating Report                      │
├────────────────────────────────────────┤
│ [OK]    Report generated               │
└────────────────────────────────────────┘
```

---

## 💾 文件結構演示

### 單一測試後的文件結構
```
├── run.ps1 (已更新)
├── run_multi_models.ps1
├── run.bat
├── requirements.txt
├── src/
│   ├── main.py
│   ├── run_benchmark.py
│   ├── report_generator.py
│   └── ...
├── venv/ (新建)
├── results/
│   └── results_mock.csv (新建)
└── reports/
    └── report_mock.md (新建)
```

### 批量測試後的文件結構
```
├── results/
│   ├── results_mock.csv
│   ├── results_ollama_llama2.csv
│   ├── results_ollama_mistral.csv
│   └── results_ollama_neural-chat.csv
└── reports/
    ├── report_mock.md
    ├── report_ollama_llama2.md
    ├── report_ollama_mistral.md
    └── report_ollama_neural-chat.md
```

---

## ⏱️ 性能參考

### 執行時間估計

| 操作 | 時間 | 備註 |
|------|------|------|
| Mock 測試 | ~30 秒 | 快速測試 |
| Llama2 測試 | ~2-5 分鐘 | 取決於 GPU |
| Mistral 測試 | ~2-5 分鐘 | 取決於 GPU |
| 下載 Llama2 | ~5-10 分鐘 | 3.8 GB 下載 |
| 下載 Mistral | ~5-10 分鐘 | 4.1 GB 下載 |
| 批量測試 (3 模型) | ~10-20 分鐘 | 並行優化 |

---

## 🎓 學習路徑

### 初級 (第一次使用)
1. ✅ 運行 `.\run.ps1 -CheckDeps`
2. ✅ 運行 `.\run.ps1 -Interactive`
3. ✅ 選擇 Single Test，選擇 mock 模型
4. ✅ 查看生成的報告

### 中級 (探索功能)
1. ✅ 運行 `.\run.ps1 -SingleTest`
2. ✅ 下載一個 Ollama 模型 (選擇 99)
3. ✅ 運行 `.\run.ps1 -ListModels` 確認下載
4. ✅ 再次運行 `-SingleTest` 測試新模型

### 高級 (批量對比)
1. ✅ 下載多個 Ollama 模型
2. ✅ 運行 `.\run.ps1 -BatchTest`
3. ✅ 選擇 "all" 測試所有模型
4. ✅ 分析對比報告

---

**演示完成！** 🎉

所有功能已在本文檔中完整演示。
根據您的需求選擇相應的使用方法開始測試。
