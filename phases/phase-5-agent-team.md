# Phase 5：Agent 團隊協作

> 時間：3-4 週
> 目標：多個 AI Agent 協同完成複雜任務（自動化工作流程）
> 效率提升：端到端自動化、複雜任務拆解
> 前置：Phase 4 完成

---

## 架構

```
使用者：「分析 PROJ-123 並修復」
        │
        ▼
n8n Orchestrator
        │
        ├──→ Agent 1: Analyst
        │       讀取 Issue、收集 context
        │       輸出：分析報告
        │
        ├──→ Agent 2: Developer
        │       根據分析報告撰寫修復
        │       輸出：程式碼變更
        │
        ├──→ Agent 3: Reviewer
        │       Review 修復程式碼
        │       輸出：Review 結果
        │
        └──→ Agent 4: Reporter
                彙整所有結果回報 Slack
```

## 步驟 1：Agent 角色定義

### 1.1 Analyst Agent

```javascript
const analyst = {
  name: 'analyst',
  prompt: `你是資深軟體分析師。
任務：分析以下 issue 並產出結構化報告。

## 報告格式
1. 問題摘要
2. 影響範圍
3. 可能的根因（列出 1-3 個）
4. 建議修復方向
5. 風險評估（高/中/低）

## 約束
- 只讀操作，不修改任何檔案
- 報告控制在 500 字以內`,
  maxTurns: 5,
  permissions: ['Read', 'Grep', 'Glob'],
};
```

### 1.2 Developer Agent

```javascript
const developer = {
  name: 'developer',
  prompt: `你是資深軟體開發者。
根據分析報告撰寫修復程式碼。

## 要求
- 最小化變更範圍
- 包含錯誤處理
- 遵循現有程式碼風格
- 寫修復說明

## 約束
- 修改檔案前必須先讀取
- 不超過 3 個檔案的變更`,
  maxTurns: 10,
  permissions: ['Read', 'Edit', 'Grep', 'Glob'],
};
```

### 1.3 Reviewer Agent

```javascript
const reviewer = {
  name: 'reviewer',
  prompt: `你是嚴格的 Code Reviewer。
Review 開發者的修復程式碼。

## Review 維度
1. 正確性：修復是否解決了根因？
2. 安全性：有無新的安全風險？
3. 效能：有無效能退化？
4. 風格：是否符合專案慣例？

## 輸出
- APPROVE / REQUEST_CHANGES / REJECT
- 具體問題列表（如有）`,
  maxTurns: 5,
  permissions: ['Read', 'Grep', 'Glob'],
};
```

## 步驟 2：n8n Orchestration Workflow

```
[Slack Trigger: /auto-fix PROJ-123]
    │
    ▼
[Fetch Issue Details]（MCP: Linear/Jira）
    │
    ▼
[Agent 1: Analyst]（claude -p）
    │ 輸出：analysis.json
    ▼
[Decision Gate]
    ├── 風險 = 高 → Slack 通知，等人工確認
    └── 風險 = 中/低 → 繼續
        │
        ▼
    [Agent 2: Developer]（claude -p）
        │ 輸出：patch diff
        ▼
    [Agent 3: Reviewer]（claude -p）
        │
        ├── APPROVE → 建立 PR + Slack 通知
        ├── REQUEST_CHANGES → 回到 Developer（最多 2 輪）
        └── REJECT → Slack 通知 + 人工介入
```

### n8n Workflow JSON 片段

```javascript
// Analyst node
const analysisResult = callAgent(
  `分析這個 issue 並產出報告：\n${issueDetails}`,
  { maxTurns: 5, cwd: repoPath }
);

// Developer node（依賴 Analyst 輸出）
const fixResult = callAgent(
  `根據以下分析報告修復問題：\n${analysisResult.text}\n\n請在 repo 中找到相關程式碼並修復。`,
  { maxTurns: 10, cwd: repoPath }
);

// Reviewer node（依賴 Developer 輸出）
const reviewResult = callAgent(
  `Review 以下修復的 git diff：\n\`\`\`diff\n${gitDiff}\n\`\`\``,
  { maxTurns: 5, cwd: repoPath }
);
```

## 步驟 3：預定義 Agent 團隊模板

| 模板名稱 | Agent 組合 | 使用場景 |
|---------|-----------|---------|
| `auto-fix` | Analyst → Developer → Reviewer | Bug 修復 |
| `auto-review` | Reviewer × 2（交叉 review） | PR Review |
| `auto-doc` | Analyzer → DocWriter → Reviewer | 文件生成 |
| `auto-test` | Analyzer → TestWriter → Runner | 測試生成 |
| `research` | Researcher → Summarizer | 技術調研 |

## 步驟 4：Agent 通訊機制

### 4.1 檔案交換（簡單）

```
/workspace/agent-tasks/{task-id}/
  ├── input.json          # 原始任務
  ├── analysis.json       # Analyst 輸出
  ├── changes.diff        # Developer 輸出
  ├── review.json         # Reviewer 輸出
  └── final-report.json   # 彙整報告
```

### 4.2 n8n 資料流（推薦）

```
Node A 輸出 → $json → Node B 輸入
```

n8n 內建的資料傳遞機制，不需要額外檔案。

## 步驟 5：安全護欄

### 5.1 人機協作邊界

| 操作 | 自動 | 需人工確認 |
|------|------|-----------|
| 分析 Issue | ✅ | |
| 讀取程式碼 | ✅ | |
| 生成 Patch | ✅ | |
| Code Review | ✅ | |
| 建立 PR | | ✅ |
| Merge PR | | ✅ |
| Deploy | | ✅ |

### 5.2 自動中斷條件

```
- Developer 修改超過 5 個檔案 → 中斷
- Reviewer 連續 2 次 REJECT → 中斷
- 任何 Agent 執行超過 10 分鐘 → 中斷
- 修改涉及安全敏感檔案（auth/*、config/*）→ 中斷
```

## 步驟 6：監控與觀測

### 6.1 任務追蹤

```json
{
  "task_id": "task-20260315-001",
  "trigger": "slack:/auto-fix PROJ-123",
  "user": "U12345",
  "agents": [
    { "name": "analyst", "status": "completed", "duration_ms": 15000 },
    { "name": "developer", "status": "completed", "duration_ms": 45000 },
    { "name": "reviewer", "status": "completed", "duration_ms": 12000 }
  ],
  "outcome": "PR_CREATED",
  "pr_url": "https://github.com/company/repo/pull/456",
  "total_duration_ms": 72000
}
```

### 6.2 Slack 通知格式

```
🔧 Auto-Fix 任務完成

Issue: PROJ-123 — 登入頁面 500 錯誤
分析: 資料庫連線池耗盡（根因：未正確關閉連線）
修復: src/db/pool.ts — 加入 connection.release()
Review: ✅ APPROVED
PR: #456 — 等待合併

⏱ 總耗時: 72 秒
```

---

## Phase 5 完成標準

- [ ] 至少 2 個 Agent 團隊模板可用
- [ ] n8n orchestration workflow 正常運作
- [ ] Agent 間通訊機制穩定
- [ ] 安全護欄（人機邊界 + 自動中斷）生效
- [ ] 任務追蹤和 Slack 通知正常
- [ ] 工程團隊實際使用並回饋正面
