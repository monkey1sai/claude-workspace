# Phase 1：基礎建設

> 時間：2 週
> 目標：部署 n8n + Dify 自託管環境 + Slack Bot
> 前置：Phase 0 驗證通過
> 工作目錄：`D:\claude-workspace\phase-1`

---

## 步驟 1：部署 n8n

```bash
mkdir -p D:/claude-workspace/phase-1/n8n
cd D:/claude-workspace/phase-1/n8n
```

建立 `docker-compose.yml`：

```yaml
version: '3.8'
services:
  n8n:
    image: n8nio/n8n:latest
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=changeme   # ← 務必修改
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - GENERIC_TIMEZONE=Asia/Taipei
    volumes:
      - n8n_data:/home/node/.n8n

volumes:
  n8n_data:
```

```bash
docker compose up -d
# 開啟 http://localhost:5678
```

驗證：
- [ ] n8n Web UI 可存取
- [ ] 能建立一個 test workflow

## 步驟 2：部署 Dify

```bash
mkdir -p D:/claude-workspace/phase-1/dify
cd D:/claude-workspace/phase-1/dify

git clone https://github.com/langgenius/dify.git
cd dify/docker
cp .env.example .env
# 編輯 .env，修改 SECRET_KEY 和 DB 密碼

docker compose up -d
# 開啟 http://localhost/install
```

驗證：
- [ ] Dify Web UI 可存取
- [ ] 能設定 Claude API Key
- [ ] 能建立一個 test chatbot

## 步驟 3：建立 Slack App

1. 前往 https://api.slack.com/apps → Create New App
2. 選擇 "From scratch"
3. 設定名稱（如 `ai-assistant`）和 Workspace

### Bot Token Scopes（OAuth & Permissions）

```
app_mentions:read     — 偵測 @bot 提及
channels:history      — 讀取頻道訊息
channels:read         — 列出頻道
chat:write            — 發送訊息
files:read            — 讀取檔案
groups:history        — 讀取私人頻道
im:history            — 讀取 DM
im:write              — 發送 DM
users:read            — 讀取使用者資訊
```

### Event Subscriptions

Request URL: `http://<your-n8n-host>:5678/webhook/slack-events`

Subscribe to bot events:
```
app_mention           — 當有人 @bot
message.im            — 當有人 DM bot
```

4. Install to Workspace
5. 記錄 Bot User OAuth Token (`xoxb-...`)
6. 記錄 Signing Secret

驗證：
- [ ] Bot 出現在 Slack 中
- [ ] 可以 @bot（雖然還沒回覆）

## 步驟 4：n8n ↔ Slack 基礎連線

在 n8n 中建立 workflow：

```
[Slack Trigger] → [Set Response] → [Slack Send Message]
```

1. Slack Trigger node：設定 Bot Token
2. Set node：`response = "收到！正在處理..."`
3. Slack Send Message node：回覆到同一 channel

驗證：
- [ ] @bot hello → bot 回覆 "收到！正在處理..."

## 步驟 5：Dify ↔ Claude API 連線

1. Dify Settings → Model Provider → Anthropic
2. 輸入 API Key
3. 建立 test app（Simple Chatbot）
4. 測試對話功能

驗證：
- [ ] Dify chatbot 能用 Claude 回答問題

## 步驟 6：基礎安全

- [ ] n8n 修改預設密碼
- [ ] Dify 修改預設密碼
- [ ] Slack Bot Token 存入環境變數（不 hardcode）
- [ ] Docker network 隔離（n8n + dify 在同一 network）
- [ ] 確認只有必要 port 對外開放

---

## Phase 1 完成標準

- [ ] n8n 運行正常，Web UI 可存取
- [ ] Dify 運行正常，Claude API 已連線
- [ ] Slack Bot 建立完成，可偵測 @bot
- [ ] n8n → Slack 基礎回覆正常
- [ ] 安全設定完成
