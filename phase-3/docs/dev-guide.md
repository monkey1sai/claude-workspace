# Phase 3：開發者使用指南

> 適用對象：工程團隊
> 更新日期：2026-03-09

## 快速開始

在 Mattermost 的任何公開頻道中 @ai-assistant，搭配以下指令即可使用程式碼相關功能。

## 支援功能

### 1. Bug 分析 :beetle:

貼上錯誤訊息或 stack trace，AI 會分析根因並給出修復建議。

**觸發方式：**

```
@ai-assistant analyze bug
[貼上錯誤 log 或 stack trace]
```

```
@ai-assistant 分析錯誤
TypeError: Cannot read property 'map' of undefined
    at UserList.render (UserList.js:42)
```

**回覆格式：** 根因分析 → 影響範圍 → 修復步驟 → 預防措施

---

### 2. 測試生成 :white_check_mark:

貼上程式碼，AI 會自動生成測試。

**觸發方式：**

```
@ai-assistant write test
[貼上程式碼]
```

```
@ai-assistant 寫測試
function add(a, b) { return a + b; }
```

**回覆格式：** 可執行的測試程式碼（正常/邊界/錯誤情境）

---

### 3. 程式碼說明 :books:

貼上程式碼，AI 會逐段解釋。

**觸發方式：**

```
@ai-assistant explain
[貼上程式碼]
```

```
@ai-assistant 解釋程式碼
[貼上程式碼]
```

這是**預設子意圖** — 如果 AI 判斷為 code 意圖但無法匹配其他子意圖，會自動走程式碼說明。

**回覆格式：** 功能概述 → 逐段說明 → 使用範例

---

### 4. PR Review :mag:

指定 GitHub PR 號碼，AI 會取得 diff 並分析。

**觸發方式：**

```
@ai-assistant review pr #123 in owner/repo
```

**注意：** 需要在系統中設定有效的 GitHub Token 和 repo 名稱。

**回覆格式：** 摘要 → 問題列表（:red_circle:高/:yellow_circle:中/:green_circle:低） → 建議 → 結論

---

### 5. 文件生成 :page_facing_up:

貼上程式碼，AI 會生成 API 文件。

**觸發方式：**

```
@ai-assistant gen doc
[貼上程式碼]
```

```
@ai-assistant 生成文件
[貼上程式碼或函式]
```

**回覆格式：** 函式說明 → 參數 → 回傳值 → 使用範例

---

## 使用額度

- 與一般問答**共用 50 次/天**（每人）
- 每次回覆會顯示剩餘額度
- 額度每日 00:00 重置

## 注意事項

1. **回覆長度限制**：超過 14000 字元的回覆會被截斷
2. **程式碼長度限制**：建議單次貼上不超過 50KB
3. **無對話記憶**：每次 code 任務獨立處理，不記得之前的對話
4. **一般問答不受影響**：非程式碼相關的問題仍走原本的 AI 問答路線
5. **模型**：開發階段使用 Claude Haiku（速度快、成本低），正式上線後升級為 Sonnet

## 常見問題

**Q: 我貼了 SQL 但走了一般問答？**
A: 如果訊息中包含分析動詞（如「分析」、「解釋」、「optimize」），系統會優先判斷為分析任務而非資料查詢。這是刻意的設計，確保「分析 SQL 效能」走 code/general 路線而非 data 路線。

**Q: PR Review 顯示錯誤？**
A: 確認 GitHub Token 已設定且有該 repo 的讀取權限。目前 PR Review 需要有效的 token 才能運作。

**Q: 如何回報問題或建議？**
A: 在 #ai-feedback 頻道留言，包含你的輸入和收到的回覆截圖。
