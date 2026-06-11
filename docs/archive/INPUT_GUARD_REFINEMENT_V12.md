# Input Guard Refinement v0.12

本版針對 v0.11 測試中出現的 benign false positive 進行修正。

## 修正重點

原本 `full_guard` 會誤擋兩類正常樣本：

- B03：高階說明 prompt injection，並要求不要揭露 hidden prompt 或 secret。
- B08：提供 prompt injection 防禦建議，並要求不要包含 jailbreak examples。

本版新增 narrow allowlist：

- 允許高階、教育型、明確不要求洩漏的 prompt injection 說明。
- 允許防禦建議與 mitigation 類問題。
- 允許 API key / token / password 等概念說明，但前提是明確要求不要提供真實值。

## 不改動的部分

- 原 leak level / Defense Score 評分標準不變。
- output guard 與 redaction 邏輯不變。
- 直接索取 flag、secret、token、API key、password 的請求仍會被 input guard 阻擋。
- 要求翻譯、編碼、拆解、輸出受保護資料的攻擊仍會被阻擋。

## 預期效果

此版本主要目標是降低 `full_guard` 對正常資安教學問題的誤擋率，同時保留對直接攻擊與轉換型洩漏攻擊的攔截能力。
