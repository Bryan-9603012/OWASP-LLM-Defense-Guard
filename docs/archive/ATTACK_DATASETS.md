# Attack Dataset

本版本只保留一個正式攻擊腳本：

```text
attacks/attacks.json
```

此檔案為最終正式版本，包含：

```text
20 類攻擊 × 4 種 prompt language styles = 80 prompts / run
```

A19 已修正為：

```text
A19: translation_based_leakage
中文：翻譯型洩漏攻擊
```

正式實驗請只使用 `attacks/attacks.json`，不要再使用舊版 draft attack dataset。
