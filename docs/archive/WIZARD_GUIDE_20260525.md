# Setup Wizard 使用說明

這版新增「安裝精靈式」啟動流程，適合 Windows 使用者直接雙擊執行。

## 主要入口

請雙擊：

```text
setup_wizard.bat
```

它會開啟 PowerShell 版安裝精靈 `setup_wizard.ps1`。

## 精靈功能

選單包含：

1. Full setup：檢查檔案、建立 `.venv`、安裝 `requirements.txt`、檢查 Ollama
2. Full setup and launch：安裝完成後直接進入互動式 benchmark menu
3. Mock quick test：不呼叫 Ollama，只測腳本流程
4. Ollama quick test：用指定 Ollama 模型跑 `--quick-test`
5. Plan-only preview：只預覽 attack / language / runs，不呼叫模型
6. Launch interactive benchmark menu：直接啟動原本互動式工具
7. Show installed Ollama models：列出本機 Ollama 模型

## 建議第一次使用流程

```text
1. 雙擊 setup_wizard.bat
2. 選 1 做完整安裝檢查
3. 選 3 跑 Mock quick test
4. 選 4 跑 Ollama quick test
5. 確認沒問題後選 6 進入正式互動式測試
```

## 正式實驗仍然遵守原本原則

這個 wizard 只負責安裝、檢查、啟動、quick test，不會改動：

- leak level 0-4
- valid_sample / invalid 邏輯
- scoring rule
- attacks.json
- defense prompt / skill 內容

## Log

精靈執行紀錄會寫入：

```text
logs/setup_wizard_last.log
```
