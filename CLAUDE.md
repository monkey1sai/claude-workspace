# Project: Enterprise AI Platform (claude-workspace)

## Overview
企業 AI 導入執行計畫，以 Mattermost + n8n + Dify + Claude API 構建自託管 AI 助理系統。
從個人驗證 (Phase 0) 到全公司推廣 (Phase 7) 的 8 階段計畫。

## Architecture
```
Users (Mattermost:8065)
  --> Outgoing Webhook (@ai-assistant trigger)
  --> n8n (localhost:5678) — Webhook 接收、訊息路由、流程編排
  --> Dify (localhost:3080) — Chatflow API (SSE streaming)
  --> Claude API (claude-sonnet-4-6 via Anthropic plugin)
  --> n8n (Parse SSE → 組合回應)
  --> Mattermost Bot API (回覆使用者)
```

## Project Structure
```
claude-workspace/
├── CLAUDE.md              # 本文件 — 專案規範與開發準則
├── PLAN.md                # 8 階段執行計畫總覽
├── README.md              # 專案入口說明
├── REQUIREMENTS.md        # 環境需求清單
├── phases/                # 各階段計畫書 + 執行結果
├── config/                # 範本設定檔（docker-compose, .env.example）
├── scripts/               # 工具腳本（claude-wrapper, mcp-test）
├── tasks/                 # 進度追蹤（todo.md）
├── phase-0/               # Phase 0 執行產出（驗證腳本）
└── phase-1/               # Phase 1 執行產出（Docker 部署設定）
    ├── n8n/               #   n8n docker-compose + workflow.json
    ├── dify/              #   Dify git clone + .env 設定
    └── mattermost/        #   Mattermost docker-compose
```

## Language Policy
- 所有文件、註解、commit message 使用**繁體中文 (zh-TW)**
- 程式碼、API endpoint、log、變數名稱保持英文
- 程式碼內註解優先使用繁體中文

## Code Style & Conventions

### General
- 簡潔優先：最少的代碼完成任務，不過度工程
- 不做推測性的未來功能
- 修改只觸及必要的部分

### JavaScript/Node.js
- 使用 `const` / `let`，不用 `var`
- 使用 `require()` (CommonJS) 風格（與 n8n Code node 相容）
- 字串使用單引號，除非需要插值
- 函式和參數加 JSDoc 註解（繁體中文）

### Docker / Infrastructure
- 所有敏感值存在 `.env` 檔案中，不 hardcode
- `docker-compose.yml` 使用 `env_file` 引用 `.env`
- n8n 和 Mattermost 使用 **bind mount**（`./volumes/`），不使用 named volume
- 服務間用 `host.docker.internal` 通訊（Docker Desktop）

### n8n Workflow
- Webhook node 的 `id` 必須是 UUID 格式
- Dify API 呼叫使用 `response_mode: streaming`，HTTP Request node 設 `responseFormat: text`
- 用 Code node 解析 SSE，不在 Code node 中做 HTTP 呼叫（沒有 fetch/$http）
- Workflow JSON 存在 `n8n/workflow.json`，可透過 REST API 匯入

## Security Rules
- **永遠不 commit**：`.env`、`credentials.env`、API keys、tokens
- `.gitignore` 必須排除所有敏感檔案
- Docker volume 資料不進版控
- 密碼最少 8 字元（Mattermost/n8n 要求）
- Dify `SECRET_KEY` 使用 `openssl rand -base64 42` 產生

## Development Workflow
1. 讀取 `tasks/todo.md` 了解當前進度
2. 讀取對應 phase 的計畫書（`phases/phase-N-*.md`）
3. 執行任務，過程中更新 `tasks/todo.md`
4. 完成後更新 `phases/phase-N-RESULTS.md`
5. 更新對應的 `phase-N/README.md` 包含重現步驟
6. 遇到問題記錄在 memory 的 `lessons.md`

## 部署文件維護規則（必須遵守）
每次完成以下事項時，**必須**檢查並更新所有相關部署文件：
- 完成一個 Phase
- 修正錯誤（特別是部署/配置相關）
- 部署方式有變動（如 named volume → bind mount）

需檢查的部署文件清單：

| 文件                         | 檢查重點                             |
| ---------------------------- | ------------------------------------ |
| `docs/rebuild-from-zero.md`  | 重建步驟是否與實際一致               |
| `phase-N/README.md`          | 目錄結構、docker-compose、重現步驟   |
| `phases/phase-N-RESULTS.md`  | 驗證結果、節點數、容器數             |
| `config/docker-compose.yml`  | 範本是否標註過時/已被取代            |
| `CLAUDE.md`                  | 技術決策、慣例是否更新               |
| `tasks/todo.md`              | 進度追蹤                             |

## Key Technical Decisions
| 決策 | 原因 |
|------|------|
| Mattermost 取代 Slack | 開源免費、資料在地端、API 相容 |
| Dify port 3080 | 預設 80 與 GitLab 衝突 |
| SSE streaming 解析 | Dify Chatflow 不支援 blocking mode |
| n8n REST API 部署 workflow | 自動化部署，不依賴手動 UI 操作 |

## Credentials Reference
所有帳號密碼集中在 `phase-1/credentials.env`（不進版控）。
需要密碼時參考該檔案，不要在其他地方重複記錄明文密碼。

## Phase Status

- Phase 0: DONE — Claude Code 能力驗證通過
- Phase 1: DONE — n8n + Dify + Mattermost 部署完成，端對端測試通過
- Phase 2: DONE — 人人可用，16-node workflow（意圖路由 + 額度控制 + 週報）
- Phase 3: DONE — 開發者 Agent，23-node workflow（code 子路由 + 直呼 Anthropic API）
- Phase 4-7: NOT STARTED
