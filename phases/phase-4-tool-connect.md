# Phase 4：工具串接（MCP Server）

> 時間：3-4 週
> 目標：AI Agent 能存取公司內部系統（DB、GitHub、Jira、文件庫）
> 效率提升：資料查詢自動化、跨系統整合
> 前置：Phase 3 完成

---

## 架構

```
Slack 使用者提問
        │
        ▼
n8n Router
   ├── 一般問答 ──→ Claude API
   ├── 程式任務 ──→ Claude Code Agent
   └── 資料查詢 ──→ Claude Code + MCP Servers
                         │
                    ┌────┼────┐
                    ▼    ▼    ▼
                  GitHub  DB  Jira
                  MCP    MCP  MCP
```

## MCP Server 概念

```
Claude Code ←──MCP Protocol──→ MCP Server ←──→ External Tool
  (Client)                     (Adapter)        (GitHub/DB/etc)
```

MCP（Model Context Protocol）是 Anthropic 開源的標準協議，讓 AI Agent 可以安全地存取外部工具。

## 步驟 1：GitHub MCP Server

### 1.1 安裝

```bash
# 使用官方 GitHub MCP Server
npm install -g @modelcontextprotocol/server-github
```

### 1.2 設定 Claude Code

在工作目錄建立 `.claude/settings.json`：

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

### 1.3 可用功能

| 功能 | MCP Tool | 使用場景 |
|------|----------|---------|
| 搜尋 Issues | `search_issues` | 找相關 bug report |
| 讀取 PR | `get_pull_request` | Code review |
| 列出 Repo | `list_repos` | 專案管理 |
| 讀取檔案 | `get_file_contents` | 遠端程式碼分析 |

## 步驟 2：資料庫 MCP Server

### 2.1 PostgreSQL MCP Server

```bash
npm install -g @modelcontextprotocol/server-postgres
```

### 2.2 設定

```json
{
  "mcpServers": {
    "company-db": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:5432/${DB_NAME}"
      ]
    }
  }
}
```

### 2.3 安全限制

```sql
-- 建立唯讀帳號
CREATE ROLE ai_reader WITH LOGIN PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE company_db TO ai_reader;
GRANT USAGE ON SCHEMA public TO ai_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO ai_reader;

-- 排除敏感資料表
REVOKE SELECT ON users_credentials FROM ai_reader;
REVOKE SELECT ON payment_info FROM ai_reader;
```

## 步驟 3：Jira / Linear MCP Server

### 選項 A：Linear（推薦，有官方 MCP）

```json
{
  "mcpServers": {
    "linear": {
      "command": "npx",
      "args": ["-y", "@anthropic/linear-mcp-server"],
      "env": {
        "LINEAR_API_KEY": "${LINEAR_API_KEY}"
      }
    }
  }
}
```

### 選項 B：Jira（使用社群 MCP）

```json
{
  "mcpServers": {
    "jira": {
      "command": "npx",
      "args": ["-y", "mcp-server-jira"],
      "env": {
        "JIRA_URL": "https://company.atlassian.net",
        "JIRA_EMAIL": "${JIRA_EMAIL}",
        "JIRA_API_TOKEN": "${JIRA_API_TOKEN}"
      }
    }
  }
}
```

## 步驟 4：文件庫 MCP Server

### Notion MCP Server

```json
{
  "mcpServers": {
    "notion": {
      "command": "npx",
      "args": ["-y", "@anthropic/notion-mcp-server"],
      "env": {
        "NOTION_API_KEY": "${NOTION_API_KEY}"
      }
    }
  }
}
```

### 使用場景

| 查詢 | 對應 MCP 操作 |
|------|--------------|
| 「最近有什麼關於 auth 的 issue？」 | GitHub: search_issues |
| 「上季營收多少？」 | DB: SELECT query |
| 「PROJ-123 的進度？」 | Linear/Jira: get_issue |
| 「onboarding 文件在哪？」 | Notion: search |

## 步驟 5：n8n 整合 MCP 查詢

```
[Slack Trigger]
    → [Intent Router]
        → "資料查詢" → [claude -p with MCP config]
                          → [Format Result]
                          → [Slack Reply]
```

### Wrapper 更新

```javascript
function callAgentWithMCP(prompt, options = {}) {
  const args = [
    '-p',
    '--output-format', 'json',
    '--max-turns', String(options.maxTurns || 10),
    prompt,
  ];

  return execFileSync('claude', args, {
    cwd: options.cwd || '/workspace/mcp-enabled',  // 有 MCP 設定的目錄
    encoding: 'utf-8',
    maxBuffer: 10 * 1024 * 1024,
    timeout: options.timeout || 300000,
    env: {
      ...process.env,
      GITHUB_TOKEN: process.env.GITHUB_TOKEN,
      // 其他 MCP Server 需要的環境變數
    },
  });
}
```

## 步驟 6：安全與審計

### 6.1 存取控制矩陣

| 角色 | GitHub | DB | Jira | Notion |
|------|--------|-----|------|--------|
| 工程師 | ✅ | ✅（唯讀） | ✅ | ✅ |
| PM | ❌ | ✅（唯讀） | ✅ | ✅ |
| 一般員工 | ❌ | ❌ | ❌ | ✅ |

### 6.2 審計日誌

每次 MCP 查詢記錄：

```json
{
  "timestamp": "2026-03-10T10:00:00Z",
  "user_id": "U12345",
  "mcp_server": "company-db",
  "operation": "SELECT",
  "query_summary": "查詢上季營收",
  "result_rows": 4,
  "duration_ms": 1200
}
```

---

## Phase 4 完成標準

- [ ] GitHub MCP Server 連線並可查詢
- [ ] DB MCP Server 連線（唯讀）
- [ ] 至少一個專案管理工具（Linear/Jira）連線
- [ ] Slack 使用者可透過 AI 查詢內部資料
- [ ] 存取控制矩陣實施
- [ ] 審計日誌記錄所有查詢
