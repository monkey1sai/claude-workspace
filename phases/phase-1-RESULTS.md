# Phase 1 基礎建設 - 驗證結果

> 執行日期：2026-03-05
> 變更：Slack 改為 Mattermost 自託管

## 架構調整

原計畫使用 Slack，改為 **Mattermost Team Edition** 自託管，原因：
- 完全開源免費，無需外部帳號
- 資料完全在地端，隱私可控
- API 與 Slack 高度相似，n8n 有原生支援

## 服務部署狀態

| 服務 | URL | 狀態 | 容器數 |
|------|-----|------|--------|
| n8n | http://localhost:5678 | ✅ 運行中 | 1 |
| Dify | http://localhost:3080 | ✅ 運行中 | 11 (api, web, worker, nginx, postgres, redis, weaviate, sandbox, ssrf_proxy, plugin_daemon, worker_beat) |
| Mattermost | http://localhost:8065 | ✅ 運行中 (healthy) | 2 (mattermost, postgres) |

## 帳號設定

| 服務 | 帳號 | 備註 |
|------|------|------|
| n8n | admin / 006931 | Web UI 登入 |
| Dify | admin@example.com / 006931Aa | 已透過 API 完成初始化 |
| Mattermost | admin / 006931Aa | System Admin，已加入 Main Team |

## Mattermost Bot 設定

- Bot Username: `ai-assistant`
- Bot User ID: `q56za1otz3rqjxxauebjuw5q1o`
- Bot Token: `x1g9oduxrbduuew15q58begd7a`
- Outgoing Webhook → `http://host.docker.internal:5678/webhook/mattermost-trigger`
- Trigger Word: `@ai-assistant`
- 已驗證 Bot 可在 Town Square 發送訊息

## 測試結果

| 測試項目 | 結果 | 備註 |
|---------|------|------|
| n8n Web UI | ✅ | HTTP 200 |
| Dify Web UI | ✅ | HTTP 307 (redirect to app) |
| Dify 初始化 | ✅ | 透過 /console/api/init + /console/api/setup 完成 |
| Mattermost Web UI | ✅ | healthy |
| Mattermost Admin 建立 | ✅ | mmctl CLI |
| Mattermost Bot 建立 | ✅ | REST API |
| Bot 發送訊息 | ✅ | Post ID: hdmhwkajmjgrxyy48t86e73eaa |
| Outgoing Webhook | ✅ | 已建立，指向 n8n |
| Dify ↔ Claude API | ✅ | Anthropic plugin 已安裝，claude-sonnet-4-6 已連線 |
| n8n ↔ Mattermost workflow | ✅ | Webhook → Dify SSE → Bot Reply，端對端測試通過 |

## 安全設定

- [x] n8n 密碼存於 .env（未 hardcode 到 docker-compose.yml）
- [x] Dify SECRET_KEY 已用 openssl rand 產生
- [x] Dify INIT_PASSWORD 已設定
- [x] Mattermost Bot Token 記錄在 credentials.env
- [x] .gitignore 已設定排除敏感檔案
- [x] Port 衝突解決（Dify 改用 3080，避免與 GitLab 的 80 衝突）
- [ ] Docker network 隔離（目前各服務各自獨立 network，可考慮建立共用 bridge）

## 檔案結構

```
D:\claude-workspace\phase-1\
├── credentials.env          # 所有憑證集中管理
├── .gitignore               # 排除敏感檔案
├── n8n/
│   ├── .env                 # n8n 環境變數
│   └── docker-compose.yml   # n8n 容器設定
├── dify/
│   └── dify/docker/
│       ├── .env             # Dify 環境變數 (port 3080)
│       └── docker-compose.yaml
└── mattermost/
    ├── .env                 # MM 環境變數
    └── docker-compose.yml   # MM + PostgreSQL
```

## n8n Workflow 詳細

- Workflow ID: `k7a5SzArbN3XpgDq`
- Webhook URL: `http://localhost:5678/webhook/mattermost-trigger`
- 流程: Mattermost Webhook → Extract Message → Call Dify API (SSE) → Parse SSE Response → Reply to Mattermost → Respond to Webhook
- n8n Owner: `admin@local.host` / `006931Aa`

## n8n API Keys

- API Key 已建立（JWT token，用於 REST API 存取）

## Phase 1 完成標準

- [x] n8n 運行正常，Web UI 可存取
- [x] Dify 運行正常，管理員帳號已建立
- [x] Mattermost Bot 建立完成，可發送訊息
- [x] Outgoing Webhook 已建立指向 n8n
- [x] 安全設定完成（.env 隔離、.gitignore）
- [x] Dify Claude API 已連線（Anthropic plugin + API Key "Dify-work-key"）
- [x] n8n → Mattermost 基礎回覆測試通過（中英文回覆皆正常）
