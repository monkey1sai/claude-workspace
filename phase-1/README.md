# Phase 1：基礎建設

> 狀態：**已完成**
> 完成日期：2026-03-06
> 目的：部署 n8n + Dify + Mattermost 自託管環境，建立端對端 AI 助理管線
> 前置：Phase 0 驗證通過

---

## 概述

Phase 1 部署了企業 AI 系統的三大基礎元件，並完成端對端整合：

```
使用者 (Mattermost) --@ai-assistant--> Outgoing Webhook
    --> n8n (Webhook 接收 + 訊息處理)
    --> Dify (Chatflow + Claude claude-sonnet-4-6)
    --> n8n (解析 SSE 回應)
    --> Mattermost Bot API (回覆使用者)
```

### 架構決策

- **Mattermost** 取代原計畫的 Slack：完全開源免費、資料在地端、API 相似度高
- **Dify Chatflow** 使用 SSE streaming：Chatflow 不支援 blocking mode，需在 n8n 端解析 SSE
- **Port 調整**：Dify 改用 3080（預設 80 與 GitLab 衝突）

## 目錄結構

```
phase-1/
├── README.md              # 本文件
├── credentials.env        # 所有服務的憑證（.gitignore 排除）
├── .gitignore             # 排除敏感檔案和 volumes
├── n8n/
│   ├── .env               # n8n 環境變數
│   ├── docker-compose.yml # n8n 容器（1 container）
│   └── workflow.json      # Mattermost AI Assistant workflow 定義
├── dify/
│   └── dify/              # Dify git clone（含 docker/ 子目錄）
│       └── docker/
│           ├── .env       # Dify 環境變數（port 3080, SECRET_KEY）
│           └── docker-compose.yaml  # Dify 容器（11 containers）
└── mattermost/
    ├── .env               # Mattermost + PostgreSQL 環境變數
    └── docker-compose.yml # Mattermost 容器（2 containers）
```

## 服務清單

| 服務 | URL | 容器數 | 用途 |
|------|-----|--------|------|
| n8n | http://localhost:5678 | 1 | 自動化工作流引擎，接收 webhook 並協調 API 呼叫 |
| Dify | http://localhost:3080 | 11 | AI 應用平台，管理 LLM 模型、建立 Chatflow |
| Mattermost | http://localhost:8065 | 2 | 團隊通訊平台（Slack 替代），使用者互動入口 |

## 環境需求

| 工具 | 版本 |
|------|------|
| Docker | >= 24.0 (實測 29.2.1) |
| Docker Compose | >= 2.0 |
| OS | Windows 11 / macOS / Linux |
| 記憶體 | 建議 >= 8GB（三個服務共 14 容器） |

## 重現步驟

### 步驟 1：部署 n8n

```bash
cd D:/claude-workspace/phase-1/n8n

# 確認 .env 已設定（N8N_BASIC_AUTH_USER, N8N_BASIC_AUTH_PASSWORD 等）
docker compose up -d

# 驗證
curl -s -o /dev/null -w "%{http_code}" http://localhost:5678/
# 預期: 200
```

首次啟動後瀏覽 http://localhost:5678 設定 owner 帳號。

### 步驟 2：部署 Dify

```bash
cd D:/claude-workspace/phase-1/dify

# 若尚未 clone
git clone https://github.com/langgenius/dify.git
cd dify/docker
cp .env.example .env

# 編輯 .env，修改以下關鍵設定：
#   SECRET_KEY=<用 openssl rand -base64 42 產生>
#   INIT_PASSWORD=006931
#   EXPOSE_NGINX_PORT=3080
#   EXPOSE_NGINX_SSL_PORT=3443

docker compose up -d
# 等待約 1-2 分鐘讓所有 11 個容器啟動完成
```

#### Dify 初始化（API 方式）

```bash
# 步驟 1: 驗證 INIT_PASSWORD，取得 session cookie
curl -c /tmp/dify_cookies.txt -X POST http://localhost:3080/console/api/init \
  -H "Content-Type: application/json" \
  -d '{"password":"006931"}'

# 步驟 2: 建立管理員帳號
curl -b /tmp/dify_cookies.txt -X POST http://localhost:3080/console/api/setup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "name": "Admin",
    "password": "006931Aa",
    "language": "zh-Hant"
  }'
```

#### 設定 Anthropic Model Provider

1. 瀏覽 http://localhost:3080 登入
2. Settings > Model Provider > Anthropic
3. 安裝 Anthropic plugin（若顯示「安裝」按鈕）
4. 輸入 API Key

#### 建立 Chatflow App

1. Studio > Create App > Chatflow
2. 命名為 "AI Assistant"
3. 選擇模型 claude-sonnet-4-6
4. Publish
5. API Access > Create API Key（記錄 `app-xxx` key）

### 步驟 3：部署 Mattermost

```bash
cd D:/claude-workspace/phase-1/mattermost

# 確認 .env 已設定（PostgreSQL 和 MM 環境變數）
docker compose up -d

# 等待 healthy 狀態
docker compose ps
```

#### 建立 Admin 帳號

```bash
# 取得容器名稱
CONTAINER=$(docker ps --filter "ancestor=mattermost/mattermost-team-edition:latest" --format "{{.Names}}")

# 建立管理員（密碼需 >= 8 字元）
docker exec $CONTAINER mmctl user create \
  --email admin@local.host --username admin \
  --password 006931Aa --system-admin --local

# 建立 Team
docker exec $CONTAINER mmctl team create \
  --name main --display-name "Main Team" --local

# 加入 Team
docker exec $CONTAINER mmctl team users add main admin --local
```

#### 建立 Bot

```bash
MM_TOKEN="<admin personal access token>"

# 建立 Bot
curl -X POST http://localhost:8065/api/v4/bots \
  -H "Authorization: Bearer $MM_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username":"ai-assistant","display_name":"AI Assistant"}'

# 為 Bot 建立 Token
curl -X POST http://localhost:8065/api/v4/users/<bot_user_id>/tokens \
  -H "Authorization: Bearer $MM_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"description":"n8n integration"}'

# 將 Bot 加入 Team
curl -X POST http://localhost:8065/api/v4/teams/<team_id>/members \
  -H "Authorization: Bearer $MM_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"team_id":"<team_id>","user_id":"<bot_user_id>"}'
```

#### 建立 Outgoing Webhook

```bash
curl -X POST http://localhost:8065/api/v4/hooks/outgoing \
  -H "Authorization: Bearer $MM_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "team_id": "<team_id>",
    "channel_id": "<town_square_channel_id>",
    "display_name": "AI Assistant Trigger",
    "trigger_words": ["@ai-assistant"],
    "callback_urls": ["http://host.docker.internal:5678/webhook/mattermost-trigger"],
    "content_type": "application/json"
  }'
```

### 步驟 4：建立 n8n Workflow

透過 n8n REST API 匯入 workflow：

```bash
# 登入取得 session cookie
curl -c /tmp/n8n_cookies.txt http://localhost:5678/rest/login -X POST \
  -H "Content-Type: application/json" \
  -d '{"emailOrLdapLoginId":"admin@local.host","password":"006931Aa"}'

# 匯入 workflow
curl -b /tmp/n8n_cookies.txt http://localhost:5678/rest/workflows -X POST \
  -H "Content-Type: application/json" \
  -d @n8n/workflow.json

# 啟用 workflow（需帶 versionId）
curl -b /tmp/n8n_cookies.txt \
  "http://localhost:5678/rest/workflows/<workflow_id>/activate" -X POST \
  -H "Content-Type: application/json" \
  -d '{"versionId":"<version_id>"}'
```

匯入前需替換 `workflow.json` 中的佔位符：
- `<DIFY_APP_API_KEY>` → 實際的 Dify App API Key（如 `app-xxx`）
- `<MM_BOT_TOKEN>` → 實際的 Mattermost Bot Token

或直接在 n8n Web UI 匯入 `n8n/workflow.json` 後手動修改。

### 步驟 5：端對端測試

```bash
# 模擬 Mattermost Outgoing Webhook
curl --max-time 120 -X POST http://localhost:5678/webhook/mattermost-trigger \
  -H "Content-Type: application/json" \
  -d '{
    "text": "@ai-assistant hello",
    "channel_id": "<town_square_channel_id>",
    "user_id": "test",
    "user_name": "tester"
  }'
# 預期回應: {"text":"ok"}

# 檢查 Mattermost 是否收到 Bot 回覆
curl http://localhost:8065/api/v4/channels/<channel_id>/posts?per_page=3 \
  -H "Authorization: Bearer <bot_token>"
```

或直接在 Mattermost Web UI (http://localhost:8065) 的 Town Square 頻道輸入 `@ai-assistant 你好`。

## n8n Workflow 說明

Workflow 名稱：**Mattermost AI Assistant**

```
[Mattermost Webhook] --> [Extract Message] --> [Call Dify API] --> [Parse SSE Response] --> [Reply to Mattermost] --> [Respond to Webhook]
```

| Node | 類型 | 說明 |
|------|------|------|
| Mattermost Webhook | webhook | 接收 POST `/webhook/mattermost-trigger` |
| Extract Message | code | 從 webhook payload 擷取使用者訊息，移除 trigger word |
| Call Dify API | httpRequest | POST 到 Dify `/v1/chat-messages`，取得 SSE streaming 原始文字 |
| Parse SSE Response | code | 解析 SSE `data:` 行，組合所有 `answer` 欄位為完整回覆 |
| Reply to Mattermost | httpRequest | 透過 Bot Token POST 到 Mattermost `/api/v4/posts` |
| Respond to Webhook | respondToWebhook | 回傳 `{"text":"ok"}` 給 Outgoing Webhook |

Workflow JSON 定義檔：`n8n/workflow.json`

## 帳號資訊

所有帳號密碼集中在 `credentials.env`（已被 .gitignore 排除）。

| 服務 | 帳號 | 用途 |
|------|------|------|
| n8n | admin@local.host / 006931Aa | Web UI 登入、REST API |
| Dify | admin@example.com / 006931Aa | Web UI 管理介面 |
| Mattermost | admin / 006931Aa | System Admin |
| Mattermost Bot | ai-assistant | Bot Token 用於 API 呼叫 |
| Dify App | app-VGTApbBnp2W2zVFNXKdmfDf5 | Chatflow API Key |

## 安全設定

- [x] 敏感資訊存於 `.env` 和 `credentials.env`，不進版控
- [x] `.gitignore` 排除 `.env`、`credentials.env`、`volumes/`
- [x] Dify SECRET_KEY 使用 `openssl rand` 隨機產生
- [x] 各服務 Port 僅綁定 localhost
- [ ] Docker network 隔離（目前各服務獨立 network，可改為共用 bridge）

## 已知問題與解法

| 問題 | 解法 |
|------|------|
| Dify Chatflow 不支援 blocking mode | 使用 streaming + SSE 解析 |
| n8n Code node 無 `fetch`/`$http` | 改用 HTTP Request node + Code node 組合 |
| Mattermost 密碼最少 8 字元 | 使用 `006931Aa` |
| Dify port 80 與 GitLab 衝突 | 改為 3080 |
| n8n webhook 需 UUID 格式 node ID | 建立 workflow 時使用正確 UUID |

## 不在版控中的檔案

以下檔案因安全或容量考量不在 git 版控中，部署時需手動建立：

| 檔案 | 說明 | 建立方式 |
|------|------|---------|
| `credentials.env` | 所有服務的帳號密碼和 Token | 依上方步驟產生後記錄 |
| `n8n/.env` | n8n 環境變數 | 參考 `config/.env.example` |
| `mattermost/.env` | Mattermost + PostgreSQL 環境變數 | 見步驟 3 |
| `dify/dify/` | Dify 完整原始碼（git clone） | `git clone https://github.com/langgenius/dify.git` |
| `dify/dify/docker/.env` | Dify 環境變數 | `cp .env.example .env` 並修改 |
| Docker volumes | n8n_data, mm_pgdata 等運行時資料 | `docker compose up -d` 自動建立 |

## 停止與重啟

```bash
# 停止所有服務
cd D:/claude-workspace/phase-1/n8n && docker compose down
cd D:/claude-workspace/phase-1/dify/dify/docker && docker compose down
cd D:/claude-workspace/phase-1/mattermost && docker compose down

# 重新啟動（資料保存在 Docker volumes 中）
cd D:/claude-workspace/phase-1/n8n && docker compose up -d
cd D:/claude-workspace/phase-1/dify/dify/docker && docker compose up -d
cd D:/claude-workspace/phase-1/mattermost && docker compose up -d
```

## 結果摘要

所有 Phase 1 完成標準已達成：

- [x] n8n 運行正常，Web UI 可存取
- [x] Dify 運行正常，Claude API 已連線（claude-sonnet-4-6 via Anthropic plugin）
- [x] Mattermost Bot 建立完成，可發送訊息
- [x] Outgoing Webhook 已建立，指向 n8n
- [x] n8n Workflow 端對端測試通過（中英文皆正常）
- [x] 安全設定完成（.env 隔離、.gitignore）

## 相關文件

- 完整驗證結果：`D:\claude-workspace\phases\phase-1-RESULTS.md`
- 原始計畫：`D:\claude-workspace\phases\phase-1-infrastructure.md`
- 總體計畫：`D:\claude-workspace\PLAN.md`
- 進度追蹤：`D:\claude-workspace\tasks\todo.md`
