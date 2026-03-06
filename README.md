# Enterprise AI Platform

從個人驗證到全公司導入的 8 階段執行計畫，以提升員工效率為核心目標。

## 系統架構

```
使用者 (Mattermost)
    |  @ai-assistant 觸發
    v
n8n (自動化引擎)
    |  Webhook 接收 → 訊息路由
    v
Dify (AI 應用平台)
    |  Chatflow → Claude API (SSE streaming)
    v
n8n (回應處理)
    |  SSE 解析 → Bot API 呼叫
    v
Mattermost Bot 回覆使用者
```

## 目前進度

| Phase | 名稱 | 狀態 | 說明 |
|-------|------|------|------|
| 0 | 個人驗證 | DONE | Claude Code CLI 能力驗證 |
| 1 | 基礎建設 | DONE | n8n + Dify + Mattermost 部署 |
| 2 | 人人可用 | - | 全員 AI 問答 |
| 3 | 開發者 Agent | - | 程式碼任務自動化 |
| 4 | 工具連接 | - | MCP Server 串接內部系統 |
| 5 | Agent Team | - | 多 agent 協作 |
| 6 | 治理與監控 | - | 成本追蹤、審計、合規 |
| 7 | 持續擴展 | - | A2A、Ollama、更多部門 |

## 目錄結構

```
claude-workspace/
├── CLAUDE.md                # Claude Code 專案規範（新 session 必讀）
├── PLAN.md                  # 8 階段執行計畫總覽
├── README.md                # 本文件
├── REQUIREMENTS.md          # 環境需求清單
├── .gitignore               # Git 排除規則
│
├── phases/                  # 各階段計畫書與驗證結果
│   ├── phase-0-validation.md       Phase 0 計畫
│   ├── phase-1-infrastructure.md   Phase 1 計畫
│   ├── phase-2-everyone.md         Phase 2 計畫
│   ├── phase-3-dev-agent.md        Phase 3 計畫
│   ├── phase-4-tool-connect.md     Phase 4 計畫
│   ├── phase-5-agent-team.md       Phase 5 計畫
│   ├── phase-6-governance.md       Phase 6 計畫
│   ├── phase-7-expansion.md        Phase 7 計畫
│   ├── RESULTS.md                  Phase 0 驗證結果
│   └── phase-1-RESULTS.md          Phase 1 驗證結果
│
├── config/                  # 範本設定檔
│   ├── docker-compose.yml       n8n + Redis + PostgreSQL 範本
│   └── .env.example             環境變數範本
│
├── scripts/                 # 工具腳本
│   ├── claude-wrapper.js        Claude Code CLI 程式化呼叫封裝
│   └── test-mcp-serve.js       MCP Server 測試腳本
│
├── tasks/                   # 進度追蹤
│   └── todo.md
│
├── phase-0/                 # Phase 0 執行產出
│   ├── README.md                部署方法與結果摘要
│   ├── claude-wrapper.js        Wrapper 測試版
│   ├── hello.js                 claude -p 測試產出
│   ├── package.json             Agent Teams 測試產出
│   └── app.js                   Agent Teams 自動產出
│
└── phase-1/                 # Phase 1 執行產出
    ├── README.md                部署方法與結果摘要
    ├── .gitignore               Phase 1 專用排除規則
    ├── n8n/
    │   ├── docker-compose.yml   n8n 容器定義
    │   └── workflow.json        Mattermost AI Assistant workflow
    ├── dify/
    │   └── (Dify git clone, .env 設定 — 見 phase-1/README.md)
    └── mattermost/
        └── docker-compose.yml   Mattermost + PostgreSQL 容器定義
```

> **注意**：Docker volumes、`.env` 檔案、`credentials.env` 不在版控中。
> 部署時需依照各 phase 的 README.md 說明建立 `.env` 並設定密碼。
> Dify 需另行 `git clone` 並設定，詳見 `phase-1/README.md`。

## 快速開始

### 1. 確認環境

```bash
node --version        # >= 18
claude --version      # >= 2.1
docker --version      # >= 24.0
docker compose version
```

### 2. 從 Phase 0 開始

```bash
cd phase-0
# 閱讀 README.md 並逐步執行驗證
```

### 3. Phase 1 部署

```bash
cd phase-1
# 閱讀 README.md 依序部署 n8n、Dify、Mattermost
# 建立 .env 檔案、設定帳號、建立 Bot、匯入 workflow
```

每個 Phase 的 README.md 包含完整重現步驟和結果摘要。

## 技術決策

| 決策 | 原因 |
|------|------|
| Mattermost 取代 Slack | 完全開源、資料在地端、API 相容、無需外部帳號 |
| Dify 作為 AI 平台 | 視覺化 Chatflow、plugin 生態、多模型支援 |
| n8n 作為協調層 | 開源、視覺化流程、Webhook 原生支援 |
| Claude claude-sonnet-4-6 作為 LLM | 程式碼理解力強、多語言、streaming API |

## 預估 ROI（50 人團隊）

| 項目 | 月度估算 |
|------|---------|
| 節省工時 | 250 人時（5hr x 50 人） |
| 成本節省 | ~$55,000 |
| AI 工具成本 | ~$2,000-5,000 |
| 淨效益 | ~$50,000+/月 |

## 相關文件

- `CLAUDE.md` — 專案規範與開發準則（Claude Code 新 session 必讀）
- `PLAN.md` — 完整 8 階段計畫
- `REQUIREMENTS.md` — 環境需求清單
- `phases/` — 各階段詳細計畫與執行結果
