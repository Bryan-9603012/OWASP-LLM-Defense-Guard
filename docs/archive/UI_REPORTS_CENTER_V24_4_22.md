# v24.4.22 Reports Center UI Fix

本版只優化 Web UI 的 Reports 頁，不改正式 runner、scoring、attack prompts、G 組、防禦規則或 Ollama 呼叫。

## 主要變更

- Reports 頁從單純檔案清單改成報表中心。
- 新增 Loaded Report Context：Run ID、Report Root、Model/Language、Protected Asset、Total Rows、Files、Modified。
- 新增 Recommended Downloads：Executive Summary、G-Group Comparison、Raw Results、Attack Summary、Experiment Config、Evidence Pack、Charts Pack、Full Report ZIP。
- 新增分類：Summary、CSV Data、Charts、Evidence、Metadata、Per-Group、Raw Files。
- 新增搜尋、Group 篩選、Type 篩選。
- 新增 Download ZIP：Raw Data、Recommended、Evidence、Charts、Full Report。
- 保留 All Files 進階模式，避免使用者找不到原始檔。

## 設計原則

Web UI 只整理正式 runner 輸出，不重新計分。重要總表優先顯示，per-group 與 nested duplicate 檔案保留在進階檔案表中。
