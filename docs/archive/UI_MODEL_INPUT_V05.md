# UI v0.5：第一層模型輸入介面

本版將原本第一層的「小模型 / 中模型 / 單一模型」選單改成直接輸入測試模型。

## 支援輸入方式

### 單一模型

```text
gemma3:1b
```

### 多模型

支援逗號、空白、分號分隔：

```text
gemma3:1b, qwen2.5:0.5b, qwen2.5:1.5b
```

```text
gemma3:1b qwen2.5:0.5b qwen2.5:1.5b
```

### 群組名稱

可直接輸入 `model_groups.json` 裡的群組：

```text
small_models
medium_models
```

也支援簡寫：

```text
small
medium
小模型
中模型
```

### 從檔案載入

```text
@model_list.txt
```

檔案中可一行一個模型，也可用逗號分隔。空行與 `#` 開頭註解會被忽略。

### 使用所有已安裝模型

```text
installed
```

或：

```text
已安裝
*
```

## 後續流程

輸入模型後，仍會依序進入：

```text
測試範圍 → 防禦模式 → Skill Profile → 自訂規則 → runs → 生成參數 → 確認頁
```
