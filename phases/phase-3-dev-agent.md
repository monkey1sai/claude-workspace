# Phase 3：開發者 Agent

> 時間：2-3 週
> 目標：工程團隊可透過 Slack 呼叫 Claude Code Agent 執行程式任務
> 效率提升：Code Review、Bug 分析、文件生成自動化
> 前置：Phase 2 完成

---

## 架構

```
Slack @ai-assistant /code-review PR#123
        │
        ▼
n8n Router（意圖判斷）
   ├── 一般問答 ──→ Claude API（Phase 2）
   └── 程式任務 ──→ claude -p wrapper ──→ 結果回 Slack
```

## 步驟 1：安裝 Claude Code CLI

```bash
# 在 n8n server 上安裝
npm install -g @anthropic-ai/claude-code

# 驗證
claude --version   # ≥ 2.1
```

## 步驟 2：建立 Claude Wrapper Service

建立 `scripts/claude-agent.js`：

```javascript
const { execFileSync } = require('child_process');
const path = require('path');

/**
 * 呼叫 Claude Code Agent 執行任務
 * @param {string} prompt - 任務描述
 * @param {object} options - 設定
 * @returns {object} Claude 回應 JSON
 */
function callAgent(prompt, options = {}) {
  const args = [
    '-p',
    '--output-format', 'json',
    '--max-turns', String(options.maxTurns || 10),
    prompt,
  ];

  const result = execFileSync('claude', args, {
    cwd: options.cwd || process.cwd(),
    encoding: 'utf-8',
    maxBuffer: 10 * 1024 * 1024,
    timeout: options.timeout || 300000,
  });

  return JSON.parse(result);
}

module.exports = { callAgent };
```

## 步驟 3：n8n 整合 Claude Code Agent

在 n8n 中新增 Code Review workflow：

```
[Slack Trigger: /code-review]
    → [Parse PR Number]
    → [Git Clone / Fetch PR]
    → [Execute Function: callAgent()]
    → [Format Review Result]
    → [Slack Thread Reply]
```

### Execute Function Node 設定

```javascript
const { execFileSync } = require('child_process');

const prNumber = $json.pr_number;
const repo = $json.repo || 'company/main-repo';

// Clone 或 pull 最新程式碼
execFileSync('git', ['fetch', 'origin', `pull/${prNumber}/head:pr-${prNumber}`], {
  cwd: '/workspace/repos/' + repo.split('/')[1],
});

// 呼叫 Claude Code 做 review
const result = execFileSync('claude', [
  '-p',
  '--output-format', 'json',
  '--max-turns', '5',
  `Review the changes in branch pr-${prNumber}. Focus on:
   1. Bug risks
   2. Security issues
   3. Performance concerns
   4. Code style
   Output a summary with severity levels.`,
], {
  cwd: '/workspace/repos/' + repo.split('/')[1],
  encoding: 'utf-8',
  maxBuffer: 10 * 1024 * 1024,
  timeout: 300000,
});

return { review: JSON.parse(result) };
```

## 步驟 4：支援的程式任務

| Slack 指令 | 說明 | Claude 任務 |
|-----------|------|------------|
| `/code-review PR#123` | Code Review | 分析 diff，找 bug/安全問題 |
| `/explain src/auth.ts` | 程式碼說明 | 讀取檔案並解釋 |
| `/bug-analyze ERROR_LOG` | Bug 分析 | 分析錯誤 log，找根因 |
| `/gen-test src/utils.ts` | 生成測試 | 為指定檔案寫測試 |
| `/doc-gen src/api/` | 文件生成 | 為 API 生成文件 |

## 步驟 5：安全控管

### 5.1 工作目錄隔離

```bash
# 每個任務在隔離的目錄中執行
/workspace/
  └── repos/
      └── main-repo/        # Read-only clone
          └── pr-reviews/    # 暫存區
```

### 5.2 Claude Code 權限限制

建立 `.claude/settings.json`：

```json
{
  "permissions": {
    "allow": ["Read", "Grep", "Glob"],
    "deny": ["Write", "Edit", "Bash"]
  }
}
```

> Review 和分析任務只需要 Read 權限，不需要修改檔案。

### 5.3 執行時間限制

```
每個任務 timeout: 5 分鐘
每人每日 agent 任務: 20 次
agent 任務僅限工程團隊
```

## 步驟 6：試行與回饋

1. 選 2-3 位資深工程師先試行
2. 收集 Code Review 品質回饋
3. 調整 prompt 和 max-turns
4. 逐步開放給全工程團隊

---

## Phase 3 完成標準

- [ ] Claude Code CLI 安裝並可執行
- [ ] Wrapper 能穩定呼叫 Claude Agent
- [ ] Slack /code-review 指令可用
- [ ] 至少支援 3 種程式任務
- [ ] 安全控管（權限 + timeout + 額度）
- [ ] 工程團隊回饋正面
