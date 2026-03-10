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
- [x] 在 Dify UI 更新 Chatflow 的 System Prompt（透過 Playwright 自動化完成）

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

## 步驟 7：Weekly Stats 自動報告

- [x] 新增 Weekly Stats Trigger（Schedule, 每週一 09:00）
- [x] 新增 Format Stats Report（Code node, 讀取 Static Data 格式化 Markdown）
- [x] 新增 Post to AI Stats（HTTP Request, 發送到 #ai-stats）
- [x] PATCH 部署 workflow（13 → 16 nodes）
- [x] 測試發送週報到 #ai-stats 頻道

## 待辦

- [ ] 選定試行團隊
- [ ] 發布使用者指南到公司 wiki

---

# Phase 3：開發者 Agent - 執行追蹤

> 完成日期：2026-03-09

## 步驟 1：目錄結構 + 環境準備

- [x] 建立 phase-3/ 目錄結構
- [x] 確認 Anthropic API Key 可直接呼叫
- [x] 在 credentials.env 新增 ANTHROPIC_API_KEY

## 步驟 2：修改 Intent Router

- [x] 新增 analysisVerbs 修正 SQL 分析被誤判為 data 意圖
- [x] 增強 code 關鍵字（含中英文）

## 步驟 3：新增 code 分支節點（16 → 23 nodes）

- [x] IF Code Intent — 判斷 intent === 'code'
- [x] Code Sub-Router — 細分子意圖（pr-review/bug-analysis/code-explain/test-gen/doc-gen）
- [x] IF PR Review — 判斷是否需要 GitHub API
- [x] Fetch PR Diff — GitHub REST API 取得 PR diff
- [x] Build Code Prompt — 根據子意圖組裝 system prompt + user message
- [x] Call Claude API for Code — Anthropic API 直呼（claude-haiku-4-5-20251001）
- [x] Format Code Response — 解析回應 + 加 icon + 額度提示

## 步驟 4：Python 腳本建構 workflow JSON

- [x] 建立 phase-3/scripts/build-workflow-v3.py
- [x] 產生 phase-3/n8n/workflow-v3.json（23 nodes，佔位符版本）
- [x] 修正 IF branch 連接（main[0]=TRUE, main[1]=FALSE）
- [x] 修正 n8n PATCH API 需要 hash 欄位（optimistic locking）

## 步驟 5：部署 + 端對端測試

- [x] PATCH 更新 workflow 到 n8n（k7a5SzArbN3XpgDq）
- [x] 啟用 workflow
- [x] Bug 分析測試通過（:beetle: 結構化分析，3032 chars）
- [x] 測試生成測試通過（:white_check_mark: 完整 Jest 測試，3237 chars）
- [x] SQL 分析修正驗證（走 general → Dify，不再誤判為 data）
- [x] 一般問答不受影響（仍走 Dify）

## 步驟 6：文件 + Commit

- [x] System prompt 備份（phase-3/prompts/code-prompts.md）
- [x] Phase 3 README（phase-3/README.md）
- [x] 驗證結果（phases/phase-3-RESULTS.md）
- [x] 開發者使用指南（phase-3/docs/dev-guide.md）
- [x] 更新 memory/lessons.md + MEMORY.md
- [x] Git commit + push（1f12745）
