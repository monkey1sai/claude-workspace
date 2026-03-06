# 環境需求清單

## 必要軟體

| 軟體 | 用途 | 安裝方式 | 驗證指令 |
|------|------|---------|---------|
| Node.js ≥ 18 | Claude Code CLI 依賴 | https://nodejs.org | `node --version` |
| Python ≥ 3.10 | LangGraph / Agent SDK | https://python.org | `python --version` |
| Docker Desktop | n8n + Dify 自託管 | https://docker.com | `docker --version` |
| Docker Compose | 容器編排 | Docker Desktop 內建 | `docker compose version` |
| Git | 版本控制 | https://git-scm.com | `git --version` |
| jq | Hook JSON 處理 | `choco install jq` | `jq --version` |
| Claude Code CLI | AI Agent runtime | `npm install -g @anthropic-ai/claude-code` | `claude --version` |

## 帳號與 API Key

| 服務 | 用途 | 取得方式 |
|------|------|---------|
| Anthropic API Key | Claude API 呼叫 | https://console.anthropic.com |
| Claude Code Max Plan | CLI 完整功能 | https://claude.ai/pricing |
| Slack App | Bot 建立 | https://api.slack.com/apps |
| GitHub Token | MCP Server 認證 | GitHub Settings → Developer → PAT |

## 選用軟體

| 軟體 | 用途 | 安裝方式 |
|------|------|---------|
| Ollama | 本地 LLM（省成本） | https://ollama.com |
| LangGraph Studio | Agent 視覺化 debug | https://studio.langchain.com |
| LangSmith | 追蹤 / 觀察 | https://smith.langchain.com |

## 硬體建議

| 用途 | 最低 | 建議 |
|------|------|------|
| 開發機（個人） | 16GB RAM | 32GB RAM |
| n8n + Dify Server | 4 CPU, 8GB RAM, 50GB SSD | 8 CPU, 16GB RAM, 100GB SSD |
| Ollama 本地推理 | 16GB RAM + GPU 8GB | 32GB RAM + GPU 16GB+ |

## 網路需求

| 連線 | 必要性 | 用途 |
|------|--------|------|
| Anthropic API (api.anthropic.com) | 必要 | Claude 推理 |
| npm registry | 必要 | 套件安裝 |
| Docker Hub | 必要 | 容器映像 |
| Slack API (slack.com) | Phase 2+ | Bot 通訊 |
| GitHub API | Phase 4+ | MCP Server |
| 內部 DB | Phase 4+ | MCP Server |
