# Session Log — Claude Code Hooks, MCP, 企業 AI 導入

> 記錄日期：2026-03-05
> 工作區：`D:\claude-workspace`
> 目標：從個人使用推廣到公司導入，以提升員工效率為優先

---

## 對話摘要

### 1. 理解 sd0x-dev-flow 專案

sd0x-dev-flow 是 Claude Code 的自主開發 workflow 外掛（plugin），提供：

- 60 commands、44 skills、14 agents、5 hooks、11 rules
- 核心機制：Auto-Loop（編輯 → 自動 review → 修正 → 通過）
- 架構：`Command（入口）→ Skill（知識庫）→ Agent（子代理）`
- 僅佔 ~4% context window（8k tokens / 200k）

### 2. Hooks 原理深度解析

**Hook = Claude Code 生命週期的事件攔截器**

- 通訊協定：stdin JSON → exit code + stdout JSON
- exit 0 = 允許、exit 2 = 阻斷、其他 = 軟錯誤
- 狀態追蹤透過 `.claude_review_state.json`

生命週期事件：

| 事件 | 觸發時機 | 能否阻斷 |
|------|---------|---------|
| SessionStart | session 啟動 | 否 |
| UserPromptSubmit | 使用者送出 prompt | 是 |
| PreToolUse | 工具呼叫前 | 是 (exit 2) |
| PostToolUse | 工具呼叫後 | 否 |
| Stop | Claude 停止回應 | 是 (exit 2) |

本專案 5 個 Hooks：

1. **namespace-hint** (SessionStart) — 注入指令命名空間
2. **pre-edit-guard** (PreToolUse) — 阻擋 .env/.git 編輯
3. **post-edit-format** (PostToolUse) — prettier + 狀態追蹤
4. **post-tool-review-state** (PostToolUse) — 解析 sentinel 更新狀態
5. **stop-guard** (Stop) — 品質關卡未通過就阻止停止

### 3. Claude Code 作為 MCP

**雙向 MCP 節點**：

- **作為 Client**：連接外部 MCP Server（Codex、GitHub、DB）
- **作為 Server**：`claude mcp serve` 暴露 Read/Edit/Write/Bash/Grep/Glob

**Hooks vs MCP**：

- MCP = 擴展能力（Outside-in，「能做什麼」）
- Hooks = 控制行為（Inside-out，「該怎麼做」）

### 4. Auto-Loop 控制流

**雙層防禦**：

- 行為層：rules/auto-loop.md 告訴 Claude「必須做」
- 系統層：stop-guard.sh 強制「不做就不能停」

**完整資料流**：

```
Edit → PreToolUse (guard) → PostToolUse (format + 失效 review)
    → Claude 跑 review → PostToolUse (解析 sentinel)
    → Pass? → Claude 跑 precommit → PostToolUse (解析 sentinel)
    → Stop → stop-guard (檢查狀態) → 允許/阻止
```

**Sentinel 標準**：`✅ Ready` / `⛔ Blocked` / `## Overall: ✅ PASS`

### 5. PDF 文件產出

- 產出：`docs/claude-code-hooks-and-mcp-guide.html` + `.pdf`（21 頁）
- 內容：6 章節（概念總覽、Hooks 解析、MCP、Auto-Loop、實作練習、FAQ）

### 6. 當前位置分析

**你在 plugin 原始碼 repo，不在 hooks 運行的位置**

- sd0x-dev-flow 未安裝為 plugin（不在 `~/.claude/settings.json` 的 `enabledPlugins`）
- CLAUDE.md 和 rules 透過 cwd 載入有效
- Hooks 未生效（沒走 plugin install 流程）

**目前已安裝的 Hooks**：

| Plugin | 事件 | 功能 |
|--------|------|------|
| hookify | Pre/Post/Stop/UserPrompt | 通用 hook 框架 |
| ralph-loop | Stop | 自我參照迴圈 stop guard |
| security-guidance | PreToolUse (Edit/Write) | 安全提醒 |
| learning-output-style | SessionStart | 學習模式 |
| explanatory-output-style | SessionStart | 教學解說 |
| superpowers | SessionStart | skill 系統 |
| qodo-skills | SessionStart | Qodo rules 載入 |
| semgrep | SessionStart/PostToolUse/UserPrompt | 安全掃描 |

### 7. it2 vs sd0x-dev-flow

**完全無關**。it2 是 iTerm2 終端機 CLI 控制工具（Python, macOS only），跟 AI/MCP 無關。

### 8. 本機 Agent Team 建構策略

四種策略評估：

| 策略 | 方案 | UI | 學習曲線 |
|------|------|-----|---------|
| A | Claude Code Teams（最快） | ❌ CLI | 低 |
| B | Dify + Claude API（最快有 UI） | ✅ | 低 |
| C | CrewAI + sd0x-dev-flow（最佳團隊體驗） | ✅ Studio | 低 |
| D | LangGraph + Studio（最強觀察） | ✅ Studio | 高 |

### 9. Claude Code CLI MCP 替代 LLM API

**可以，但替代的是「LLM + 工具 + Agent Loop」整包**

三種實現方式：

| 方式 | 說明 | 適合 |
|------|------|------|
| `claude mcp serve` | 只暴露工具，不含 LLM 推理 | 只需工具存取 |
| `claude -p`（推薦） | 完整 agent session（LLM + 工具 + 迴圈） | 委派式 agent |
| Claude Agent SDK | 程式化 SDK | 深度整合 |

### 10. 企業導入架構

**核心原則：押注「開放標準」而非「某家廠商」**

2026 各大廠最新動態：

- **Anthropic**：Claude Cowork（辦公 agent）+ Opus 4.6（100 萬 context）+ MCP 捐贈 AAIF
- **OpenAI**：ChatGPT Agent + Frontier 企業平台 + Agents SDK
- **Google**：Gemini Enterprise（Agentspace 改名）+ A2A 協定 + Workspace Studio
- **Microsoft**：Agent Framework（AutoGen + Semantic Kernel）
- **Linux Foundation**：AAIF 成立（MCP 成為中立標準）

**長期贏家工具棧**：

| 層級 | 工具 | 理由 |
|------|------|------|
| 通訊標準 | MCP + A2A | AAIF 中立治理，所有大廠支持 |
| 協調/UI | n8n + Dify | 開源、自託管、model agnostic |
| LLM | Claude API + Ollama | 強推理 + 零成本本地 |
| 開發 Agent | Claude Code CLI | Agent Teams + MCP 深度整合 |
| 辦公 Agent | Claude Cowork | Slack/Google 連接器已就位 |
| 品質控制 | sd0x-dev-flow hooks | Auto-loop + sentinel + stop-guard |

### 11. 企業導入分階段計畫

以「提升員工效率」為優先：

| 階段 | 時間 | 做什麼 | 工具 |
|------|------|--------|------|
| 0 驗證 | 1 週 | 本機驗證 Claude Code Teams | Claude Code CLI |
| 1 基礎 | 2 週 | Docker 部署 n8n + Dify + Slack bot | n8n, Dify |
| 2 人人可用 | 2 週 | Slack @bot 接 Claude API | Slack, Claude API |
| 3 開發 Agent | 2 週 | n8n 接 claude -p | Claude Code CLI |
| 4 工具連接 | 2 週 | MCP Servers（Jira, GitHub, DB） | MCP |
| 5 Agent Team | 4 週 | 多 agent 自動化 workflow | n8n + Claude Code |
| 6 治理 | 2 週 | 權限、成本、審計、儀表板 | n8n RBAC |
| 7 擴展 | 持續 | A2A、更多部門、Ollama | A2A, Ollama |

---

## 相關產出檔案

| 檔案 | 位置 |
|------|------|
| Hooks & MCP PDF 指南 | `D:\._vscode2\sd0x-dev-flow\docs\claude-code-hooks-and-mcp-guide.pdf` |
| Hooks & MCP HTML 指南 | `D:\._vscode2\sd0x-dev-flow\docs\claude-code-hooks-and-mcp-guide.html` |
| 執行計畫 | `D:\claude-workspace\PLAN.md` |
| Phase 0 指南 | `D:\claude-workspace\phases\phase-0-validation.md` |
| 環境需求 | `D:\claude-workspace\REQUIREMENTS.md` |
