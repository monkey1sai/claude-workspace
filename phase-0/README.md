# Phase 0：個人驗證

> 狀態：**已完成**
> 完成日期：2026-03-05
> 目的：驗證 Claude Code 的 agent 能力，確認可行性後進入 Phase 1

---

## 概述

Phase 0 是整個企業 AI 導入計畫的可行性驗證階段。在本機環境測試 Claude Code 的各種程式化呼叫模式，確認：

1. **`claude -p`** — 程式化呼叫是否能穩定回傳 JSON
2. **`claude mcp serve`** — MCP Server 模式是否正常
3. **Agent Teams** — 多 agent 協作是否可行
4. **Wrapper Script** — 是否能用 Node.js 封裝自動化呼叫

## 目錄結構

```
phase-0/
├── README.md            # 本文件
├── claude-wrapper.js    # Node.js 封裝腳本，用於程式化呼叫 claude -p
├── hello.js             # claude -p 測試產出的範例檔案
├── package.json         # Agent Teams 測試產出（Express API）
└── app.js               # Agent Teams 的 developer agent 自動產出
```

## 環境需求

| 工具 | 版本需求 | 實測版本 |
|------|---------|---------|
| Claude Code | >= 2.1 | 2.1.69 |
| Node.js | >= 18 | v22.20.0 |
| Docker | 任意（Phase 1 需要） | 29.2.1 |
| OS | Windows / macOS / Linux | Windows 11 Pro 10.0.26100 |

## 重現步驟

### 1. 測試 `claude -p`（程式化呼叫）

```bash
cd D:/claude-workspace/phase-0

# 基礎測試
claude -p "列出目前目錄的結構" --output-format json

# 讀寫檔案測試（需明確授權工具）
claude -p "建立一個 hello.js，內含 greet(name) 函式" \
  --output-format json \
  --allowedTools "Write,Read,Bash"

# 限制迴圈次數
claude -p "分析 package.json 的依賴" --max-turns 5 --output-format json
```

### 2. 測試 MCP Server 模式

```bash
# 啟動 MCP Server 並送入 JSON-RPC initialize
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}' | claude mcp serve
```

### 3. 測試 Agent Teams

```bash
# 設定環境變數
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=true

# 啟動互動模式
cd D:/claude-workspace/phase-0
claude

# 在互動模式中輸入：
# 「建立一個 2 人 agent team：reviewer 和 developer，
#   developer 寫一個 Express API，reviewer 做 code review」
```

Agent Teams 的工作成果會存在 `~/.claude/teams/` 目錄。

### 4. 測試 Wrapper Script

```bash
cd D:/claude-workspace/phase-0
node claude-wrapper.js
```

`claude-wrapper.js` 封裝了 `claude -p` 的呼叫，關鍵設計：

```javascript
const result = execFileSync('claude', args, {
  env: { ...process.env, CLAUDECODE: undefined }, // 避免嵌套 session 問題
});
```

## 測試結果摘要

| 測試項目 | 結果 | 備註 |
|---------|------|------|
| claude -p 基礎 | PASS | 回應時間 ~10s |
| claude -p JSON 輸出 | PASS | JSON.parse() 解析正常 |
| claude -p 讀寫檔案 | PASS | 需加 `--allowedTools` |
| claude -p --max-turns | PASS | 4 turns 完成分析 |
| claude mcp serve | PASS | JSON-RPC 回應正常 |
| Agent Teams | PARTIAL | 能執行，但耗時 >10min |
| Wrapper Script | PASS | 程式化呼叫正常，~23s |

## 關鍵發現

### 必須知道的技巧

1. **嵌套 session 問題**：在 Claude Code session 內呼叫 `claude -p` 會失敗。解法：在 env 中設 `CLAUDECODE: undefined`
2. **工具權限**：程式化呼叫需加 `--allowedTools "Write,Read,Bash"` 明確授權，否則工具呼叫會被拒絕
3. **MCP Server 測試**：可用 stdin pipe JSON-RPC 訊息測試，不需額外 client

### 效能與成本

- 單次 `claude -p` 回應時間：10-23 秒
- API 回應時間：8.8s - 21.5s
- Token 成本估算：每次 ~$0.12-0.15 USD
- Agent Teams：預估 $0.5-1.0 USD/次
- Cache 效果顯著：cache_read 遠大於 cache_creation

### 限制

- Agent Teams 為實驗功能，執行時間長，適合非即時的批次任務
- `claude -p` 無 `--allowedTools` 時工具呼叫會被靜默拒絕
- 每次呼叫有成本，批次使用需注意

## 結論

所有核心功能驗證通過，可進入 Phase 1 基礎建設。建議：
- 核心 workflow 以 `claude -p` + Wrapper Script 為主
- Agent Teams 作為輔助功能
- 實作 cost tracking 監控 API 消耗

## 相關文件

- 完整驗證結果：`D:\claude-workspace\phases\RESULTS.md`
- 原始計畫：`D:\claude-workspace\phases\phase-0-validation.md`
- 總體計畫：`D:\claude-workspace\PLAN.md`
