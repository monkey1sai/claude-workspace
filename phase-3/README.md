# Phase 3：開發者 Agent

> 狀態：**已完成**
> 完成日期：2026-03-09
> 目的：讓 code 意圖的請求實際發揮作用（Bug 分析、測試生成、程式碼說明等）
> 前置：Phase 2 完成

## 概述

Phase 3 在 Phase 2 的意圖路由基礎上，新增了 code 分支的完整處理流程。
code 任務直接呼叫 Anthropic API（不經 Dify），每種子任務使用不同的 system prompt。

### 架構

```
[IF General]
  ├─ TRUE → [Call Dify API] → SSE 解析 → 回覆（Phase 2 一般問答，不變）
  └─ FALSE → [IF Code Intent]
               ├─ TRUE → [Code Sub-Router] → [IF PR Review]
               │          ├─ TRUE → [Fetch PR Diff] → [Build Code Prompt]
               │          └─ FALSE → [Build Code Prompt]
               │                       → [Call Claude API] → [Format Code Response]
               │                       → [Log Usage] → [Reply to MM] → [Respond]
               └─ FALSE → [Reply Phase Not Ready]（data 意圖，Phase 4）
```

### 設計決策

| 決策 | 理由 |
|------|------|
| 直接呼叫 Anthropic API | 每種子任務需不同 system prompt，Dify 不夠靈活 |
| 開發階段用 Haiku | 最便宜、回應最快，上線再換 Sonnet |
| 共用 50 次/天額度 | 簡單統一，初期足夠 |
| 修正 Intent Router | SQL 分析不再誤判為 data 意圖 |

## 支援的 Code 子意圖

| 子意圖 | 觸發方式 | 圖示 |
|--------|---------|------|
| Bug 分析 | `analyze bug`、`error`、`stack trace`、`分析錯誤` | :beetle: |
| 測試生成 | `write test`、`寫測試`、貼程式碼 + `測試` | :white_check_mark: |
| 程式碼說明 | `explain`、`解釋程式碼`（預設） | :books: |
| PR Review | `review pr #123 in owner/repo` | :mag: |
| 文件生成 | `gen doc`、`生成文件` | :page_facing_up: |

## 目錄結構

```
phase-3/
├── README.md                          # 本文件
├── n8n/
│   └── workflow-v3.json               # 23-node workflow（佔位符版本）
├── prompts/
│   └── code-prompts.md                # 各子意圖 system prompt 備份
├── scripts/
│   └── build-workflow-v3.py           # 建構 workflow JSON 的 Python 腳本
└── docs/
    └── dev-guide.md                   # 開發者使用指南（待建立）
```

## 部署步驟

### 前置：Anthropic API Key

在 `phase-1/credentials.env` 新增：

```
ANTHROPIC_API_KEY=sk-ant-api03-xxx
```

### 建構 + 部署

```bash
# 1. 建構 workflow JSON
cd D:/claude-workspace
python phase-3/scripts/build-workflow-v3.py

# 2. 替換佔位符後部署（需 Python 腳本處理 token 替換 + n8n REST API）
# 參考 phase-3/scripts/build-workflow-v3.py 的部署邏輯
```

### 佔位符

workflow-v3.json 中的佔位符：
- `<DIFY_APP_API_KEY>` → Dify App API Key
- `<MM_BOT_TOKEN>` → Mattermost Bot Token
- `<ANTHROPIC_API_KEY>` → Anthropic API Key
- `<GITHUB_TOKEN>` → GitHub Personal Access Token（PR Review 用）
- `<GITHUB_DEFAULT_REPO>` → 預設 GitHub repo（owner/name 格式）

## 已知限制

- PR Review 需要有效的 GitHub Token 和 repo 名稱（目前使用 placeholder）
- 多模態（圖片分析）不支援 — Dify Chatflow 未啟用 Vision
- 回覆超過 14000 字元會被截斷

## 驗證結果

| 測試 | 結果 |
|------|------|
| Bug 分析 (analyze bug + error log) | :beetle: 結構化分析，3032 chars |
| 測試生成 (寫測試 + 程式碼區塊) | :white_check_mark: 完整 Jest 測試，3237 chars |
| SQL 分析（之前被誤判為 data） | 修正成功，走 general → Dify |
| 一般問答 | 不受影響，仍走 Dify |
