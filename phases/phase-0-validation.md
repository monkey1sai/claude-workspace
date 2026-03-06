# Phase 0：個人驗證

> 時間：1 週
> 目標：在本機驗證 Claude Code 的 agent 能力，確認可行性
> 成本：$0（使用現有 Max plan）
> 工作目錄：`D:\claude-workspace\phase-0`

---

## 步驟 1：確認環境

```bash
# 建立工作目錄
mkdir -p D:/claude-workspace/phase-0
cd D:/claude-workspace/phase-0

# 確認版本
claude --version          # 需要 ≥ 2.1
node --version            # 需要 ≥ 18
jq --version              # 需要安裝（choco install jq）
docker --version          # Phase 1 需要
```

## 步驟 2：測試 `claude -p`（程式化呼叫）

```bash
# 基礎測試：問一個問題
claude -p "列出目前目錄的結構" --output-format json

# 程式碼任務測試：寫一個函式
claude -p "建立一個 hello.js，內含 greet(name) 函式" --output-format json

# 限制迴圈次數
claude -p "分析 package.json 的依賴" --max-turns 5 --output-format json
```

驗證重點：
- [ ] JSON 輸出可被程式解析
- [ ] Claude 能讀寫檔案
- [ ] `--max-turns` 能控制執行範圍

## 步驟 3：測試 `claude mcp serve`（MCP Server 模式）

```bash
# 終端 1：啟動 MCP Server
claude mcp serve

# 終端 2：用 node 測試呼叫（另開一個終端）
# 參考 scripts/test-mcp-serve.js
```

驗證重點：
- [ ] MCP Server 能正常啟動
- [ ] 可透過 JSON-RPC 呼叫 Read/Edit 等工具
- [ ] 回應格式符合 MCP 規範

## 步驟 4：測試 Agent Teams（實驗功能）

```bash
# 設定環境變數
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=true

# 啟動 Claude Code
cd D:/claude-workspace/phase-0
claude

# 在 Claude Code 中測試：
# 「建立一個 2 人 agent team：reviewer 和 developer，
#  developer 寫一個 Express API，reviewer 做 code review」
```

驗證重點：
- [ ] Agent Teams 能正常啟動
- [ ] 兩個 agent 能各自獨立工作
- [ ] Agent 間能透過 file inbox 通訊
- [ ] 結果可觀察（查看 ~/.claude/teams/）

## 步驟 5：測試 Wrapper Script

建立 `D:\claude-workspace\phase-0\claude-wrapper.js`：

```javascript
const { execFileSync } = require('child_process');

function callClaude(prompt, options = {}) {
  const args = [
    '-p',
    '--output-format', 'json',
    '--max-turns', String(options.maxTurns || 10),
    prompt,
  ];

  const result = execFileSync('claude', args, {
    cwd: options.cwd || process.cwd(),
    encoding: 'utf-8',
    maxBuffer: 10 * 1024 * 1024, // 10MB
    timeout: options.timeout || 300000, // 5 min
  });

  return JSON.parse(result);
}

// 測試
const result = callClaude('列出目前目錄的檔案並說明每個檔案的用途');
console.log(JSON.stringify(result, null, 2));
```

```bash
cd D:/claude-workspace/phase-0
node claude-wrapper.js
```

驗證重點：
- [ ] Wrapper 能正常呼叫並取得 JSON 結果
- [ ] 錯誤處理正常（timeout、非零 exit code）
- [ ] 可控制 maxTurns 和 timeout

## 步驟 6：記錄結果

建立 `D:\claude-workspace\phase-0\RESULTS.md`：

```markdown
# Phase 0 驗證結果

## 環境
- Claude Code 版本：
- Node.js 版本：
- OS：

## 測試結果

| 測試項目 | 結果 | 備註 |
|---------|------|------|
| claude -p 基礎 | ✅/❌ | |
| claude -p JSON 輸出 | ✅/❌ | |
| claude mcp serve | ✅/❌ | |
| Agent Teams | ✅/❌ | |
| Wrapper Script | ✅/❌ | |

## 效能觀察
- 單次 claude -p 回應時間：
- Agent Teams 任務完成時間：
- Token 消耗估算：

## 限制與問題
-
-

## 結論
- [ ] 可進入 Phase 1
- [ ] 需要調整（說明：）
```

---

## Phase 0 完成標準

全部打勾才能進入 Phase 1：

- [ ] `claude -p` 能穩定回傳 JSON
- [ ] `claude mcp serve` 能啟動並回應
- [ ] Agent Teams 能跑完一個簡單任務
- [ ] Wrapper Script 能程式化呼叫
- [ ] 記錄了效能和限制
- [ ] RESULTS.md 已填寫
