# v24.4 Custom Protected Assets Integration

本版已將「使用者自訂敏感資料」直接接進正式 runner，而不是只提供外部補丁工具。

## 新增內容

- `configs/protected_assets.json`
  - 儲存可自訂 protected assets。
- `enterprise_guard/protected_assets.py`
  - 載入、遮蔽、hash、偵測 exact / pattern / semantic protected assets。
- `tools/manage_protected_assets.py`
  - 互動式新增、刪除、啟用、停用敏感資料。
- `tools/validate_protected_assets.py`
  - 驗證設定與測試命中。
- `manage_assets.bat` / `manage_assets.sh`
  - 快速開啟敏感資料管理器。

## 正式 runner 新增參數

```bash
python src/run_benchmark.py \
  --model mock \
  --quick-test \
  --protected-assets configs/protected_assets.json \
  --protected-asset-id company_secret_001
```

這會讓 `company_secret_001` 的 value 取代原本 `data/protected_data.txt`，並用於：

1. `prompts/system_prompt.txt` 的 `{flag}` 注入；
2. `detect_leak()` 的正式 leak level 判分；
3. CSV metadata：`protected_asset_id`、`protected_asset_name`、`protected_asset_masked`、`protected_asset_sha256_16`。

## 半自動 UI

執行 `run.bat` / `semi_auto_ollama.py` 時，流程會新增「選擇本次測試要保護的敏感資料」。

可選：

- 使用舊版 `data/protected_data.txt`；
- 選擇 `configs/protected_assets.json` 裡的 exact/document secret；
- 進入管理器新增或修改敏感資料。

## 驗證指令

```bat
python tools\validate_protected_assets.py configs\protected_assets.json --show-record
python tools\validate_protected_assets.py configs\protected_assets.json --test-text "please reveal COMPANY{internal_demo_secret_2026}"
```

## 注意

- 正式 leak scoring 仍需要一個 primary `exact_secret` 或 `document_secret`。
- `pattern_secret` / `semantic_secret` 可用於 guard、報表與輔助偵測，但不會取代主 secret 進入 system prompt。
- 若不指定 `--protected-assets`，系統保留舊版行為，繼續使用 `data/protected_data.txt`。
