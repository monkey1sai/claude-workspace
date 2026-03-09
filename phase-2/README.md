# Phase 2：人人可用

## 概述

在 Phase 1 的端對端流程基礎上，加入額度控制、意圖路由、使用統計等功能，
讓全體員工可透過 Mattermost @ai-assistant 使用 AI 助手。

## 架構

```
Mattermost (@ai-assistant 觸發)
  → n8n Webhook
  → Extract Message（提取 query, channelId, userId）
  → Rate Limiter（每人每日 50 次）
  → Intent Router（general / code / data）
  → Call Dify API（SSE streaming）→ Parse → Log Usage → Reply

Weekly Stats（每週一 09:00）
  → Format Stats Report（讀取 Static Data）
  → Post to #ai-stats（Markdown 週報）
```

## 重現步驟

### 1. Mattermost 頻道設定

```bash
# 建立 ai-feedback 頻道
curl -X POST http://localhost:8065/api/v4/channels \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"team_id":"<TEAM_ID>","name":"ai-feedback","display_name":"AI Feedback","type":"O"}'

# 建立 ai-stats 頻道（Private）
curl -X POST http://localhost:8065/api/v4/channels \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"team_id":"<TEAM_ID>","name":"ai-stats","display_name":"AI Stats","type":"P"}'

# Bot 加入頻道
curl -X POST http://localhost:8065/api/v4/channels/<CHANNEL_ID>/members \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"<BOT_USER_ID>"}'
```

### 2. 部署 Workflow

```bash
# 替換 workflow-v2.json 中的佔位符
# <DIFY_APP_API_KEY> → 實際 Dify App API Key
# <MM_BOT_TOKEN> → 實際 Mattermost Bot Token

# 登入 n8n
curl -c cookie -X POST http://localhost:5678/rest/login \
  -H "Content-Type: application/json" \
  -d '{"emailOrLdapLoginId":"admin@local.host","password":"<N8N_PASSWORD>"}'

# 更新 workflow（PATCH）
curl -X PATCH -b cookie http://localhost:5678/rest/workflows/<WORKFLOW_ID> \
  -H "Content-Type: application/json" \
  -d @workflow-v2-with-tokens.json

# 啟用 workflow
curl -X POST -b cookie http://localhost:5678/rest/workflows/<WORKFLOW_ID>/activate \
  -H "Content-Type: application/json" \
  -d '{"versionId":"<VERSION_ID>"}'
```

### 3. Dify System Prompt

登入 Dify UI (http://localhost:3080)，編輯 Chatflow 的 System Prompt。
內容參見 `prompts/system-prompt.md`。

## 檔案說明

| 檔案 | 用途 |
|------|------|
| `n8n/workflow-v2.json` | 16-node workflow（佔位符版，含週報，不含真實 token） |
| `prompts/system-prompt.md` | Dify System Prompt 備份 |
| `docs/user-guide.md` | 使用者指南（非技術人員版） |
