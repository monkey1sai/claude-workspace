# Phase 2 人人可用 - 驗證結果

> 執行日期：2026-03-09
> 基礎：Phase 1 的 Mattermost + n8n + Dify 架構

## 架構升級

Phase 1（6 nodes 線性流程）→ Phase 2（16 nodes 含分支路由 + 週報）

```
主流程（Webhook 觸發）：
[Mattermost Webhook]
  → [Extract Message]（+userId）
  → [Rate Limiter]（每人每日 50 次）
  → [IF Rate OK?]
      ├─(yes)→ [Intent Router] → [IF General?]
      │           ├─(yes)→ [Call Dify API] → [Parse SSE] → [Log Usage] → [Reply to MM] → [Respond]
      │           └─(no)→ [Reply: Phase Not Ready] → [Respond]
      └─(no)→ [Reply: Rate Limited] → [Respond]

週報流程（Schedule 觸發，每週一 09:00）：
[Weekly Stats Trigger] → [Format Stats Report] → [Post to AI Stats]
```

## 新增功能

| 功能 | 實作方式 | 狀態 |
|------|---------|------|
| 每人每日額度控制 | n8n Static Data，每日自動重置 | ✅ |
| 意圖路由 | Code node 關鍵字分類（general/code/data） | ✅ |
| 額度提示 | 每次回覆底部顯示剩餘額度 | ✅ |
| 回饋機制 | #ai-feedback 頻道 + 回覆提示連結 | ✅ |
| 使用量統計 | Static Data 記錄 per-user 累計次數 | ✅ |
| 多頻道支援 | Bot 加入所有公開頻道，Webhook 全頻道觸發 | ✅ |
| System Prompt 客製化 | Dify Chatflow 內建（備份在 phase-2/prompts/） | ✅ |
| 週報自動報告 | Schedule Trigger 每週一 09:00 發送到 #ai-stats | ✅ |

## Mattermost 新頻道

| 頻道 | ID | 用途 |
|------|-----|------|
| #ai-feedback | ao31r5mrbpbxjmsbaqojoa5bjo | 使用者回饋收集 |
| #ai-stats | pse5g5abxift5by3wttecycusc | 使用量統計（Private，僅管理員） |

## 測試結果

| 測試項目 | 結果 | 備註 |
|---------|------|------|
| 一般問答 | ✅ | AI 正常回覆 + 額度提示 |
| 程式碼意圖路由 | ✅ | 回覆「功能開發中，Phase 3 開放」 |
| 資料查詢意圖路由 | ✅ | 回覆「功能開發中，Phase 4 開放」 |
| 多頻道觸發 | ✅ | off-topic 頻道正常回覆 |
| Rate Limiter 計數 | ✅ | per-user 獨立計數，日期變更自動重置 |
| Log Usage 統計 | ✅ | totalRequests + per-user total 正確累計 |
| 回饋提示 | ✅ | 底部顯示「剩餘額度：N/50 | 回饋 → #ai-feedback」 |
| 週報發送 | ✅ | Markdown 格式統計報告成功發送到 #ai-stats |

## 檔案結構

```
phase-2/
├── n8n/
│   └── workflow-v2.json       # 16-node workflow（佔位符版，含週報）
├── prompts/
│   └── system-prompt.md       # Dify System Prompt 備份
├── docs/
│   └── user-guide.md          # 使用者指南
└── scripts/
    └── setup-mattermost.sh    # （待建立）頻道設定自動化腳本
```

## n8n Workflow

- Workflow ID: `k7a5SzArbN3XpgDq`
- Workflow Name: `Mattermost AI Assistant v2`
- Nodes: 16
- Active: true

## Phase 2 完成標準

- [x] 全員可在 Mattermost @bot 提問並收到回覆
- [x] 每日額度機制生效（50 次/人/天）
- [x] 使用教學文件發布（phase-2/docs/user-guide.md）
- [ ] 試行團隊回饋正面（需實際使用者測試）
- [x] 使用量統計可查看（Static Data + #ai-stats 頻道）

## 待辦（Phase 2 後續）

- [x] 在 Dify UI 更新 System Prompt（透過 Playwright 自動化完成）
- [x] 建立 Weekly Stats 自動報告（同 workflow 內 Schedule Trigger）
- [ ] 選定試行團隊，收集回饋
- [ ] 將使用者指南發布到公司 wiki
