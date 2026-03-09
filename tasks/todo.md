# Phase 2：人人可用 - 執行追蹤

## 步驟 1：Mattermost 設定
- [x] 建立 #ai-feedback 頻道（ao31r5mrbpbxjmsbaqojoa5bjo）
- [x] 建立 #ai-stats 頻道（pse5g5abxift5by3wttecycusc，Private）
- [x] Bot 加入所有公開頻道（town-square, off-topic, ai-feedback）
- [x] 確認 Outgoing Webhook 全頻道觸發（無 channel_id 限制）

## 步驟 2：n8n Workflow 升級
- [x] 修改 Extract Message — 增加 userId 提取
- [x] 新增 Rate Limiter（Static Data，50 次/人/天）
- [x] 新增 IF Rate OK 分支
- [x] 新增 Intent Router（關鍵字分類：general/code/data）
- [x] 新增 IF General 分支
- [x] 新增 Reply Rate Limited 回覆
- [x] 新增 Reply Phase Not Ready 回覆
- [x] 新增 Log Usage 統計記錄
- [x] 修改 Reply to Mattermost — 加回饋提示和剩餘額度

## 步驟 3：Dify System Prompt
- [x] System Prompt 文字備份（phase-2/prompts/system-prompt.md）
- [ ] 在 Dify UI 更新 Chatflow 的 System Prompt（需手動操作）

## 步驟 4：部署
- [x] PATCH 更新 workflow 到 n8n（k7a5SzArbN3XpgDq）
- [x] 啟用 workflow（active=true）

## 步驟 5：測試驗證
- [x] 一般問答 → AI 正常回覆 + 額度提示
- [x] 程式碼意圖 → 回覆「Phase 3 開放」
- [x] 資料查詢意圖 → 回覆「Phase 4 開放」
- [x] 多頻道觸發 → off-topic 正常回覆
- [x] Static Data 統計 → per-user 計數正確

## 步驟 6：文件
- [x] 使用者指南（phase-2/docs/user-guide.md）
- [x] 驗證結果（phases/phase-2-RESULTS.md）
- [x] 進度追蹤（tasks/todo.md — 本文件）

## 待辦
- [ ] Dify UI 手動更新 System Prompt
- [ ] 建立 Weekly Stats 自動報告 workflow
- [ ] 選定試行團隊
- [ ] 發布使用者指南到公司 wiki
