# 恢復 Session 指南

> 每次開啟新的 Claude Code session 時，參考本文件快速恢復專案狀態。

## 啟動方式

```bash
cd D:/claude-workspace
claude
```

`CLAUDE.md` 和 `memory/MEMORY.md` 會**自動載入**，Claude 會知道架構、代碼風格、規範和歷史經驗。
但它不會主動讀取當前進度，需要你用第一句話引導。

---

## 推薦的開場白

### 通用（恢復全部狀態）

```
讀取 tasks/todo.md、phases/phase-1-RESULTS.md 和 phase-1/credentials.env，了解目前專案進度和服務狀態，然後告訴我下一步該做什麼。
```

### 接續特定 Phase

```
讀取 tasks/todo.md 和 phases/phase-1-RESULTS.md。Phase 0-1 已完成，我要開始 Phase 2。
```

### Debug / 排查問題

```
讀取 phase-1/credentials.env 和 phase-1/README.md。Mattermost → n8n → Dify 的管線出問題，幫我排查。
```

### 查看服務狀態

```
讀取 phase-1/credentials.env，檢查 n8n、Dify、Mattermost 三個服務是否正常運行，回報狀態。
```

---

## 自動載入 vs 手動讀取

| 來源 | 載入方式 | 提供什麼 |
|------|---------|---------|
| `CLAUDE.md` | 自動 | 架構、代碼風格、安全規則、開發流程 |
| `memory/MEMORY.md` | 自動 | 跨 session 的技術經驗和踩坑記錄 |
| `tasks/todo.md` | 需手動讀取 | 哪些任務完成、哪些待辦 |
| `phases/*-RESULTS.md` | 需手動讀取 | 各 phase 詳細測試結果 |
| `phase-1/credentials.env` | 需手動讀取 | 所有帳號密碼和 token（不在 git 中） |
| `phase-N/README.md` | 需手動讀取 | 該 phase 的部署方法和重現步驟 |

## 注意事項

- `credentials.env` 不在 git 版控中，只存在本機
- 如果服務已關閉，需先 `docker compose up -d` 重啟（見各 phase README.md）
- 隨著 phase 推進，開場白中的 RESULTS 檔案應改為最新的 phase
