# Phase 3：開發者 Agent — 驗證結果

> 完成日期：2026-03-09
> Workflow：23 nodes（從 Phase 2 的 16 nodes 升級）
> 模型：claude-haiku-4-5-20251001（開發階段，正式上線換 Sonnet）

## 架構變更

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

## 新增節點（+7）

| 節點 | 類型 | 功能 |
|------|------|------|
| IF Code Intent | IF | 判斷 `intent === 'code'` |
| Code Sub-Router | Code | 細分子意圖 + 解析參數 |
| IF PR Review | IF | 判斷是否需要 GitHub API |
| Fetch PR Diff | HTTP Request | GitHub REST API 取得 PR diff |
| Build Code Prompt | Code | 根據子意圖組裝 system prompt + user message |
| Call Claude API for Code | HTTP Request | Anthropic API 直呼（非 streaming） |
| Format Code Response | Code | 解析回應 + 加 icon + 額度提示 |

## 支援的 Code 子意圖

| 子意圖 | 觸發關鍵字 | 圖示 |
|--------|-----------|------|
| Bug 分析 | `analyze bug`、`error`、`stack trace`、`分析錯誤` | :beetle: |
| 測試生成 | `write test`、`寫測試`、貼程式碼 + `測試` | :white_check_mark: |
| 程式碼說明 | `explain`、`解釋程式碼`（預設） | :books: |
| PR Review | `review pr #123 in owner/repo` | :mag: |
| 文件生成 | `gen doc`、`生成文件` | :page_facing_up: |

## 端對端測試結果

| # | 測試場景 | 結果 | 備註 |
|---|---------|------|------|
| 1 | Bug 分析（`analyze bug` + error log） | ✅ 通過 | :beetle: 結構化分析，3032 chars |
| 2 | 測試生成（`寫測試` + 程式碼區塊） | ✅ 通過 | :white_check_mark: 完整 Jest 測試，3237 chars |
| 3 | SQL 分析（之前被誤判為 data） | ✅ 修正成功 | 走 general → Dify，不再誤判 |
| 4 | 一般問答 | ✅ 不受影響 | 仍走 Dify 路線 |

## Intent Router 修正

**問題**：「分析 SQL 效能問題」被誤判為 `data` 意圖（因含 `sql` 關鍵字）

**修正**：新增 `analysisVerbs` 陣列（`分析`、`解釋`、`最佳化`、`optimize` 等），若存在分析動詞則抑制 `data` 意圖分類。

## 設計決策

| 決策 | 理由 |
|------|------|
| 直接呼叫 Anthropic API（不經 Dify） | 每種子任務需不同 system prompt，Dify 不夠靈活 |
| 開發階段用 Haiku | 最便宜、回應最快，上線再換 Sonnet |
| 共用 50 次/天額度 | 簡單統一，初期足夠 |
| Python 腳本建構 workflow JSON | 避免 bash `${}` 吞掉 n8n 表達式 |
| n8n PATCH 需 hash 欄位 | v2.10+ optimistic locking 機制 |

## 已知限制

- PR Review 需要有效的 GitHub Token 和 repo 名稱（目前使用 placeholder）
- 多模態（圖片分析）不支援 — Dify Chatflow 未啟用 Vision
- 回覆超過 14000 字元會被截斷
- Code 任務無對話記憶（每次獨立呼叫）

## 關鍵檔案

| 檔案 | 用途 |
|------|------|
| `phase-3/n8n/workflow-v3.json` | 23-node workflow（佔位符版本） |
| `phase-3/scripts/build-workflow-v3.py` | 建構 workflow JSON 的 Python 腳本 |
| `phase-3/prompts/code-prompts.md` | 各子意圖 system prompt 備份 |
| `phase-3/README.md` | Phase 3 完整文件 |
| `phase-3/docs/dev-guide.md` | 開發者使用指南 |
