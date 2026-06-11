# v25.2 UI Group / Attack Scope Fix

## 修正重點

1. Web UI 正式防禦組已更新為 v25 Input/Output Guard 分組：
   - G0 No Defense
   - G1 Skill-only
   - G2 Input Boundary
   - G3 Input Guard
   - G4 Output Guard
   - G5 IO Guard
   - G6 Full Guard

2. 舊版 v24 的 G5/G6/G7 名稱仍保留相容，但不再作為 v25 UI 預設組別。

3. Include benign / normal samples 改為預設不勾選。
   - 原因：正式攻擊測試時，benign cases 會增加樣本數，容易讓 Total Samples 看起來與 attack_ids 不一致。
   - 需要測 false positive / over-block 時再手動勾選。

4. Attack IDs 欄位補上提醒：
   - `attack_ids=all` 時，`limit_base_attacks` 才會生效。
   - 若填 `A01,A20`，代表只跑兩個 base attacks，`limit_base_attacks=20` 會被忽略。

## 不影響的部分

本次只改 Web UI 預設分組、CLI mapping、報表顯示名稱與說明文字。沒有改：

- attacks.json
- scoring / invalid logic
- leak level detector
- input/output guard 核心規則
- Ollama 呼叫流程

## v25.3 follow-up

v25.3 further aligns `semi_auto_ollama.py` with the Web UI G0-G6 definitions.  The standard Host-LLM compare modes now use:

- Core: G0, G1, G5, G6
- Full: G0, G1, G2, G3, G4, G5, G6

The old v24 G7 registry-enhanced group is not part of the default v25.3 compare path.
