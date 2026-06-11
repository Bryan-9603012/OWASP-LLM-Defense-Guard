# TEST_SCOPE_SELECTION.md — 使用者可選測試範圍優化

## 本次修改目標

本版先不打包成 `.exe`，保留原本 `.venv` / `run.bat` / `semi_auto_ollama.py` 執行流程，並新增「使用者可選測試範圍」。

原本預設流程是完整正式測試：

```text
20 attacks × 4 language styles = 80 samples / model / run
```

本版仍保留完整 `20×4` 作為正式實驗選項，但不再強制每次都只能完整跑完。

---

## 新增測試模式

在選完模型後，會新增「選擇測試範圍」選單：

```text
1. Full official test
   完整 20 attacks × 4 languages

2. Language test
   選擇語言種類，攻擊全跑

3. Attack test
   選擇攻擊 ID，語言可選

4. Quick smoke test
   前 5 個攻擊 × English only，用來測流程

5. Custom test
   自訂 attack IDs + languages + base attack limit
```

---

## 支援的語言種類

```text
en_pure              English only / EN_ONLY
zh_pure              繁體中文 / ZH_ONLY
zh_main_en_mixed     中文為主 mixed English / ZH_EN_MIX
en_main_zh_mixed     English-main mixed Chinese / EN_ZH_MIX
```

互動輸入時可用：

```text
all
1,2
en_pure,zh_pure
zh_main_en_mixed,en_main_zh_mixed
```

---

## 支援的攻擊 ID 選擇

支援輸入：

```text
all
A01,A03,A19
1,3,19
```

腳本會依據 `attacks/attacks.json` 自動列出可選攻擊 ID，並忽略不存在的 ID。

---

## 底層 CLI 新增參數

`src/run_benchmark.py` 新增：

```bash
--attack-ids all
--attack-ids A01,A03,A19
```

原本已有的語言選擇參數仍保留：

```bash
--styles all
--styles en_pure
--styles en_pure,zh_pure
```

範例：

```bash
python src/run_benchmark.py --model mock --styles en_pure --attack-ids A01,A03 --no-report
```

---

## 修改檔案

```text
semi_auto_ollama.py
src/run_benchmark.py
TEST_SCOPE_SELECTION.md
```

---

## 設計重點

本次沒有把每種模式寫成獨立測試流程，而是採用同一套底層測試流程：

```text
選擇測試範圍
      ↓
轉成 styles / attack_ids / limit_base_attacks
      ↓
呼叫 src/run_benchmark.py
      ↓
共用原本判分、invalid 邏輯、報告產生流程
```

因此正式實驗的計分邏輯沒有被改掉，只是新增了更彈性的入口。
