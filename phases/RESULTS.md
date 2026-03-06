# Phase 0 驗證結果

> 驗證日期：2026-03-05
> 驗證者：Claude Code (claude-opus-4-6)

## 環境

- Claude Code 版本：2.1.69
- Node.js 版本：v22.20.0
- OS：Windows 11 Pro 10.0.26100
- Docker 版本：29.2.1
- jq：**未安裝**（Phase 0 不需要，後續可用 `choco install jq` 安裝）

## 測試結果

| 測試項目 | 結果 | 備註 |
|---------|------|------|
| claude -p 基礎 | ✅ | 成功回傳目錄結構描述，回應時間 ~10s |
| claude -p JSON 輸出 | ✅ | JSON 格式正確，可被 `JSON.parse()` 解析 |
| claude -p 讀寫檔案 | ✅ | 需加 `--allowedTools "Write,Read,Bash"` 才能寫入 |
| claude -p --max-turns | ✅ | 能控制執行範圍，4 turns 完成分析任務 |
| claude mcp serve | ✅ | JSON-RPC initialize 正常回應，tools/list 回傳完整工具清單 |
| Agent Teams | ⚠️ 部分通過 | 能啟動 team、分配 agent、建立檔案、inbox 通訊正常；但執行時間過長（>10min 未完成） |
| Wrapper Script | ✅ | 成功程式化呼叫，JSON 解析正常，回應時間 ~23s |

## 效能觀察

- 單次 `claude -p` 回應時間：10-23 秒（視任務複雜度）
- API 回應時間（duration_api_ms）：8.8s - 21.5s
- Agent Teams 任務完成時間：>10 分鐘（developer 完成寫碼 + inbox 通訊約 1 分鐘內，reviewer 啟動較慢）
- Token 消耗估算：
  - 單次簡單查詢：~$0.12-0.15 USD
  - Agent Teams（未完成）：預估 $0.5-1.0 USD/次
- Cache 效果顯著：cache_read_input_tokens 遠大於 cache_creation_input_tokens

## 關鍵發現

### 必須知道的技巧

1. **嵌套 session 問題**：在 Claude Code 內呼叫 `claude -p` 需要 `unset CLAUDECODE` 或在 env 中設為 `undefined`
2. **工具權限**：程式化呼叫需加 `--allowedTools` 明確授權工具使用，否則 Write/Edit 等工具會被拒絕
3. **MCP Server 測試**：可用 stdin pipe JSON-RPC 訊息來測試，不需額外 client

### Agent Teams 詳細觀察

- 自動建立了 3 個 agent：team-lead、developer、reviewer
- 使用 file inbox (`~/.claude/teams/<name>/inboxes/`) 進行通訊
- Developer agent 成功：建立 `app.js`（Express API）和 `package.json`
- Developer 透過 SendMessage 通知 Reviewer，inbox 中有完整的訊息記錄
- 配置檔記錄了每個 agent 的 model、prompt、角色等資訊
- **限制**：執行時間較長，適合非即時的批次任務

## 限制與問題

- jq 未安裝，但 Phase 0 驗證不需要（Node.js 可替代 JSON 處理）
- Agent Teams 為實驗功能，穩定性待觀察，執行時間較長
- `claude -p` 在無 `--allowedTools` 時，工具呼叫會被拒絕（需注意自動化腳本必須明確授權）
- 每次呼叫成本約 $0.12-0.15，批次使用需注意成本控制

## 結論

- [x] 可進入 Phase 1
- 建議：
  - 安裝 jq（`choco install jq`）
  - Agent Teams 可作為輔助功能，但核心 workflow 建議以 `claude -p` + Wrapper Script 為主
  - 程式化呼叫務必加 `--allowedTools` 參數
  - 考慮實作 cost tracking 來監控 API 消耗
