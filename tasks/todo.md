# Phase 1：基礎建設 - 執行追蹤

## 步驟 1：部署 n8n
- [x] 建立 docker-compose.yml + .env
- [x] docker compose up -d
- [x] 驗證 Web UI 可存取 (localhost:5678) - HTTP 200

## 步驟 2：部署 Dify
- [x] git clone + 設定 .env (SECRET_KEY, INIT_PASSWORD, port 3080)
- [x] docker compose up -d (11 容器)
- [x] 驗證 Web UI 可存取 (localhost:3080)
- [x] 透過 API 完成初始化 (/console/api/init + /console/api/setup)

## 步驟 3：建立 Mattermost (替代 Slack)
- [x] docker-compose.yml + .env
- [x] docker compose up -d (healthy)
- [x] 建立 admin 帳號 (mmctl)
- [x] 建立 Main Team
- [x] 建立 ai-assistant Bot + Token
- [x] 驗證 Bot 可發送訊息

## 步驟 4：n8n ↔ Mattermost 連線
- [x] 建立 Outgoing Webhook 指向 n8n
- [x] 在 n8n 建立 workflow (API 自動建立，Webhook → Dify → Mattermost)

## 步驟 5：Dify ↔ Claude API
- [x] 登入 Dify UI 設定 Model Provider → Anthropic API Key (Dify-work-key)

## 步驟 6：基礎安全
- [x] .env 隔離敏感資訊
- [x] .gitignore 排除 credentials
- [x] Dify SECRET_KEY 隨機產生
- [x] Port 衝突解決 (Dify 3080)
