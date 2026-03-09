# 從零重建系統指南

> 最後更新：2026-03-09
> 適用情境：換電腦、系統重灌、災難復原

## 前置需求

| 工具 | 版本 |
|------|------|
| Docker Desktop | >= 24.0 |
| Docker Compose | >= 2.0 |
| Git | >= 2.0 |
| Python | >= 3.10 |
| Node.js | >= 18 |
| gh CLI | 已登入（`gh auth login`） |
| Claude Code | 已安裝 |

硬體建議：8+ CPU, 16GB+ RAM, 50GB+ SSD（三個服務共 14 個容器）

## 步驟 0：Clone 專案

```bash
git clone https://github.com/monkey1sai/claude-workspace.git
cd claude-workspace
```

## 步驟 1：建立敏感設定檔

以下檔案不在版控中，需手動建立。

### 1a. n8n 環境變數

建立 `phase-1/n8n/.env`：

```env
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=006931
N8N_HOST=localhost
N8N_PORT=5678
N8N_PROTOCOL=http
GENERIC_TIMEZONE=Asia/Taipei
```

### 1b. Mattermost 環境變數

建立 `phase-1/mattermost/.env`：

```env
POSTGRES_USER=mmuser
POSTGRES_PASSWORD=006931
POSTGRES_DB=mattermost

MM_SQLSETTINGS_DRIVERNAME=postgres
MM_SQLSETTINGS_DATASOURCE=postgres://mmuser:006931@mm-postgres:5432/mattermost?sslmode=disable&connect_timeout=10
MM_SERVICESETTINGS_SITEURL=http://localhost:8065
MM_SERVICESETTINGS_ENABLEBOTACCOUNTCREATION=true
MM_SERVICESETTINGS_ENABLEINCOMINGWEBHOOKS=true
MM_SERVICESETTINGS_ENABLEOUTGOINGWEBHOOKS=true
MM_SERVICESETTINGS_ENABLEPOSTUSERNAMEOVERRIDE=true
MM_SERVICESETTINGS_ENABLEPOSTICONOVERRIDE=true
```

### 1c. Dify 環境變數

```bash
cd phase-1/dify
git clone https://github.com/langgenius/dify.git
cd dify/docker
cp .env.example .env
```

編輯 `phase-1/dify/dify/docker/.env`，修改：

```env
SECRET_KEY=<用 openssl rand -base64 42 產生>
INIT_PASSWORD=006931
EXPOSE_NGINX_PORT=3080
EXPOSE_NGINX_SSL_PORT=3443
```

### 1d. 主要密碼備份

建立 `phase-1/credentials.env`（**不進版控**）：

```env
# === n8n ===
N8N_URL=http://localhost:5678
N8N_USER=admin@local.host
N8N_PASSWORD=006931Aa
N8N_WORKFLOW_ID=<部署後填入>

# === Mattermost ===
MM_URL=http://localhost:8065
MM_ADMIN_USER=admin
MM_ADMIN_PASSWORD=006931Aa
MM_ADMIN_TOKEN=<建立後填入>
MM_BOT_USERNAME=ai-assistant
MM_BOT_USER_ID=<建立後填入>
MM_BOT_TOKEN=<建立後填入>
MM_TEAM_ID=<建立後填入>
MM_TOWN_SQUARE_CHANNEL_ID=<建立後填入>
MM_WEBHOOK_ID=<建立後填入>

# === Dify ===
DIFY_URL=http://localhost:3080
DIFY_ADMIN_EMAIL=admin@example.com
DIFY_ADMIN_PASSWORD=006931Aa
DIFY_APP_ID=<建立後填入>
DIFY_APP_API_KEY=<建立後填入>
```

---

## 步驟 2：啟動 Docker 容器

依序啟動，每個等 healthy 再啟下一個。

```bash
# 2a. n8n
cd phase-1/n8n && docker compose up -d

# 2b. Dify（11 個容器，約 1-2 分鐘）
cd phase-1/dify/dify/docker && docker compose up -d

# 2c. Mattermost
cd phase-1/mattermost && docker compose up -d

# 驗證全部啟動
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "n8n|mattermost|dify|docker"
```

---

## 步驟 3：初始化服務

### 3a. n8n — 設定 Owner

瀏覽 http://localhost:5678，首次會要求設定 owner：
- Email: `admin@local.host`
- Password: `006931Aa`

### 3b. Dify — 初始化 + 設定 Model

```bash
# 初始化
curl -c /tmp/dify_cookies.txt -X POST http://localhost:3080/console/api/init \
  -H "Content-Type: application/json" \
  -d '{"password":"006931"}'

# 建立管理員
curl -b /tmp/dify_cookies.txt -X POST http://localhost:3080/console/api/setup \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","name":"Admin","password":"006931Aa","language":"zh-Hant"}'
```

登入 Dify UI (http://localhost:3080)：
1. Settings > Model Provider > Anthropic > 輸入 API Key
2. Studio > Create App > **Chatflow** > 命名 "AI Assistant"
3. 選模型 `claude-sonnet-4-6` > Publish
4. API Access > Create API Key > 記錄 `app-xxx` key
5. 記錄 App ID（URL 中的 UUID）

**更新 System Prompt**（參考 `phase-2/prompts/system-prompt.md`）：
- 在 Chatflow 編輯器中，點選 Start 節點
- 貼入 System Prompt 內容
- Publish

### 3c. Mattermost — 建立帳號 + Bot

```bash
# 取得容器名稱
CONTAINER=$(docker ps --filter "ancestor=mattermost/mattermost-team-edition:latest" --format "{{.Names}}")

# 建立 Admin
docker exec $CONTAINER mmctl user create \
  --email admin@local.host --username admin \
  --password 006931Aa --system-admin --local

# 建立 Team
docker exec $CONTAINER mmctl team create \
  --name main --display-name "Main Team" --local

# 加入 Team
docker exec $CONTAINER mmctl team users add main admin --local
```

登入 http://localhost:8065，取得 Admin Personal Access Token：
- Profile > Security > Personal Access Tokens > Create

```bash
MM_TOKEN="<admin token>"

# 建立 Bot
BOT_RESP=$(curl -s -X POST http://localhost:8065/api/v4/bots \
  -H "Authorization: Bearer $MM_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username":"ai-assistant","display_name":"AI Assistant"}')
BOT_USER_ID=$(echo $BOT_RESP | python -c "import sys,json; print(json.load(sys.stdin)['user_id'])")
echo "Bot User ID: $BOT_USER_ID"

# 建立 Bot Token
BOT_TOKEN_RESP=$(curl -s -X POST http://localhost:8065/api/v4/users/$BOT_USER_ID/tokens \
  -H "Authorization: Bearer $MM_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"description":"n8n integration"}')
BOT_TOKEN=$(echo $BOT_TOKEN_RESP | python -c "import sys,json; print(json.load(sys.stdin)['token'])")
echo "Bot Token: $BOT_TOKEN"

# Bot 加入 Team
TEAM_ID=$(curl -s http://localhost:8065/api/v4/teams/name/main \
  -H "Authorization: Bearer $MM_TOKEN" | python -c "import sys,json; print(json.load(sys.stdin)['id'])")

curl -s -X POST http://localhost:8065/api/v4/teams/$TEAM_ID/members \
  -H "Authorization: Bearer $MM_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"team_id\":\"$TEAM_ID\",\"user_id\":\"$BOT_USER_ID\"}"
```

### 3d. Mattermost — 關鍵設定（容易遺漏！）

```bash
# ⚠️ 必須設定！否則 Outgoing Webhook 無法連到 n8n
# 允許 webhook 連到內網地址
curl -s http://localhost:8065/api/v4/config \
  -H "Authorization: Bearer $MM_TOKEN" > /tmp/mm_config.json

python -c "
import json
c = json.load(open('/tmp/mm_config.json'))
c['ServiceSettings']['AllowedUntrustedInternalConnections'] = 'host.docker.internal 172.0.0.0/8 192.168.0.0/16 10.0.0.0/8'
json.dump(c, open('/tmp/mm_config_updated.json', 'w'))
"

curl -s -X PUT http://localhost:8065/api/v4/config \
  -H "Authorization: Bearer $MM_TOKEN" \
  -H "Content-Type: application/json" \
  -d @/tmp/mm_config_updated.json > /dev/null

echo "AllowedUntrustedInternalConnections 已設定"
```

### 3e. Mattermost — 建立頻道

```bash
# ai-feedback（公開）
curl -s -X POST http://localhost:8065/api/v4/channels \
  -H "Authorization: Bearer $MM_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"team_id\":\"$TEAM_ID\",\"name\":\"ai-feedback\",\"display_name\":\"AI Feedback\",\"type\":\"O\"}"

# ai-stats（私人，管理員用）
curl -s -X POST http://localhost:8065/api/v4/channels \
  -H "Authorization: Bearer $MM_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"team_id\":\"$TEAM_ID\",\"name\":\"ai-stats\",\"display_name\":\"AI Stats\",\"type\":\"P\"}"

# Bot 加入 Town Square
TOWN_SQUARE=$(curl -s http://localhost:8065/api/v4/teams/$TEAM_ID/channels/name/town-square \
  -H "Authorization: Bearer $MM_TOKEN" | python -c "import sys,json; print(json.load(sys.stdin)['id'])")

curl -s -X POST http://localhost:8065/api/v4/channels/$TOWN_SQUARE/members \
  -H "Authorization: Bearer $MM_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"$BOT_USER_ID\"}"
```

### 3f. Mattermost — 建立 Outgoing Webhook

```bash
# ⚠️ 不要綁定 channel_id，讓所有頻道都能觸發
curl -s -X POST http://localhost:8065/api/v4/hooks/outgoing \
  -H "Authorization: Bearer $MM_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"team_id\": \"$TEAM_ID\",
    \"display_name\": \"AI Assistant Trigger\",
    \"trigger_words\": [\"@ai-assistant\"],
    \"callback_urls\": [\"http://host.docker.internal:5678/webhook/mattermost-trigger\"],
    \"content_type\": \"application/json\"
  }"
```

---

## 步驟 4：部署 n8n Workflow

```bash
# 替換 workflow-v2.json 中的佔位符
cd phase-2/n8n
sed "s/<DIFY_APP_API_KEY>/$DIFY_APP_API_KEY/g; s/<MM_BOT_TOKEN>/$BOT_TOKEN/g" \
  workflow-v2.json > /tmp/workflow-deploy.json

# 登入 n8n
curl -c /tmp/n8n-cookie -X POST http://localhost:5678/rest/login \
  -H "Content-Type: application/json" \
  -d '{"emailOrLdapLoginId":"admin@local.host","password":"006931Aa"}'

# 建立 workflow
WORKFLOW_RESP=$(curl -s -b /tmp/n8n-cookie -X POST http://localhost:5678/rest/workflows \
  -H "Content-Type: application/json" \
  -d @/tmp/workflow-deploy.json)
WORKFLOW_ID=$(echo $WORKFLOW_RESP | python -c "import sys,json; print(json.load(sys.stdin)['data']['id'])")
VERSION_ID=$(echo $WORKFLOW_RESP | python -c "import sys,json; print(json.load(sys.stdin)['data']['versionId'])")
echo "Workflow ID: $WORKFLOW_ID, Version: $VERSION_ID"

# 啟用
curl -s -b /tmp/n8n-cookie -X POST \
  "http://localhost:5678/rest/workflows/$WORKFLOW_ID/activate" \
  -H "Content-Type: application/json" \
  -d "{\"versionId\":\"$VERSION_ID\"}"
```

---

## 步驟 5：驗證

```bash
# 5a. 直接測試 n8n webhook
curl --max-time 120 -X POST http://localhost:5678/webhook/mattermost-trigger \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"@ai-assistant hello\",\"channel_id\":\"$TOWN_SQUARE\",\"user_id\":\"test\",\"user_name\":\"tester\"}"
# 預期: {"text":"ok"}

# 5b. 檢查 Bot 回覆
curl -s http://localhost:8065/api/v4/channels/$TOWN_SQUARE/posts?per_page=3 \
  -H "Authorization: Bearer $BOT_TOKEN" | python -c "
import sys, json
data = json.load(sys.stdin)
for pid in data['order'][:3]:
    p = data['posts'][pid]
    print(f'{p[\"message\"][:100]}')
"

# 5c. 在 Mattermost UI 測試
# 瀏覽 http://localhost:8065，在 Town Square 輸入：
# @ai-assistant 你好
```

---

## 常見問題

### Bot 不回覆

1. **Outgoing Webhook 被擋**：確認 `AllowedUntrustedInternalConnections` 已設定（步驟 3d）
2. **容器 DNS 問題**：確認 docker-compose.yml 有 `extra_hosts: host.docker.internal:host-gateway`
3. **Workflow 未啟用**：到 n8n UI 確認 workflow 是 active 狀態
4. **訊息格式錯誤**：必須以 `@ai-assistant` 開頭，不能在 thread 回覆中使用

### Dify 回覆為空

1. 確認 Anthropic API Key 有效
2. 確認 Chatflow 已 Publish
3. 測試：`curl -X POST http://localhost:3080/v1/chat-messages -H "Authorization: Bearer <API_KEY>" -H "Content-Type: application/json" -d '{"inputs":{},"query":"hello","response_mode":"streaming","user":"test"}'`

### 服務停止/重啟後恢復

```bash
# 資料保存在 Docker volumes 中，重啟即可恢復
cd phase-1/n8n && docker compose up -d
cd phase-1/dify/dify/docker && docker compose up -d
cd phase-1/mattermost && docker compose up -d
```

無需重新初始化（帳號、workflow、頻道都在 volume 裡）。

### 完全刪除重建

```bash
# ⚠️ 會清除所有資料！
cd phase-1/n8n && docker compose down -v
cd phase-1/dify/dify/docker && docker compose down -v
cd phase-1/mattermost && docker compose down -v
# 然後從步驟 2 重新開始
```

---

## 服務總覽

| 服務 | URL | 帳號 | 用途 |
|------|-----|------|------|
| n8n | http://localhost:5678 | admin@local.host / 006931Aa | Workflow 引擎 |
| Dify | http://localhost:3080 | admin@example.com / 006931Aa | AI 模型管理 |
| Mattermost | http://localhost:8065 | admin / 006931Aa | 使用者介面 |

## 架構圖

```
使用者 (Mattermost :8065)
  → @ai-assistant 觸發 Outgoing Webhook
  → n8n (:5678) Webhook 接收
    → Extract Message（提取 query, userId）
    → Rate Limiter（50 次/人/天）
    → Intent Router（general/code/data）
    → Call Dify API (:3080, SSE streaming)
    → Parse SSE → Log Usage → Reply to Mattermost
  → Bot 回覆使用者

Weekly Stats（每週一 09:00）
  → Format Stats Report → Post to #ai-stats
```

## 檔案對照表

| 用途 | 版控中的檔案 | 需手動建立 |
|------|-------------|-----------|
| n8n 容器 | `phase-1/n8n/docker-compose.yml` | `phase-1/n8n/.env` |
| Dify 容器 | — | `phase-1/dify/dify/docker/.env` |
| Mattermost 容器 | `phase-1/mattermost/docker-compose.yml` | `phase-1/mattermost/.env` |
| MM 設定備份 | `phase-1/mattermost/config-export.json` | — |
| Workflow (Phase 2) | `phase-2/n8n/workflow-v2.json` | 佔位符需替換 |
| System Prompt | `phase-2/prompts/system-prompt.md` | 需貼到 Dify UI |
| 密碼集中管理 | — | `phase-1/credentials.env` |
