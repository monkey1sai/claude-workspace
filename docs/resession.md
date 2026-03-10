# Session 恢復指南 — Phase 4 討論中

> 建立日期：2026-03-10
> 狀態：等待使用者確認環境資訊後繼續

## 當前進度

Phase 3 已全部完成（23-node workflow, code 子路由, Anthropic API 直呼）。
使用者說「ok 繼續下一個 phase」，準備進入 Phase 4。

## Phase 4 待確認事項

在開始實作前，需要使用者回答以下問題：

### 1. 實際擁有的內部系統

- [ ] GitHub / GitLab？
- [ ] 資料庫？什麼類型？（PostgreSQL / MySQL / MSSQL / SQLite）
- [ ] 專案管理工具？（Jira / Linear / Redmine / 無）
- [ ] 文件庫？（Notion / Confluence / SharePoint / 無）

### 2. 「資料查詢」優先使用場景

例如：查資料庫報表、查 GitHub issue、查專案進度…

### 3. 環境確認

- [ ] 192.168.10.105 上是否有 Node.js / npm（MCP Server 需要 npx）

## 架構選擇

Phase 4 有三種可能的架構：

| 方案 | 優點 | 缺點 |
|------|------|------|
| A: n8n → Claude CLI + MCP | 最靈活，AI 自主決定查什麼 | 最慢（啟動 CLI 子程序） |
| B: n8n → 直接呼叫各系統 API | 最快 | AI 無法自主決定查什麼 |
| C: Claude API + tool_use | AI 自主選工具，不需 CLI | 需自建 tool 定義，中等速度 |

建議根據使用者的系統和場景再決定。

## 恢復方式

1. 讀取本文件了解停留點
2. 讀取 `phases/phase-4-tool-connect.md` 了解原始計畫
3. 根據使用者回答調整計畫，進入 plan mode 設計實作方案
