# 企業 AI 導入執行計畫

> 核心目標：**提升員工效率**
> 導入策略：從個人驗證 → 團隊試行 → 全公司推廣
> 工具原則：押注開放標準（MCP + A2A），不鎖定單一廠商

---

## 架構全局圖

```
┌─────────────────────────────────────────────────────┐
│                  企業 AI 作業系統                      │
│                                                      │
│  介面層     Slack / Teams / Web Dashboard             │
│             (人人都能 @bot 互動)                       │
│                       ↕                               │
│  協調層     n8n（自動化路由）+ Dify（AI 應用）        │
│             (視覺化流程、權限、成本、審計)              │
│                       ↕                               │
│  Agent 層   Code Agent (claude -p)                    │
│             Research Agent (Claude API)                │
│             Data Agent (Claude API + DB MCP)           │
│             Office Agent (Claude Cowork)               │
│                       ↕                               │
│  標準層     MCP (agent ↔ tool)                        │
│             A2A (agent ↔ agent)                       │
│                       ↕                               │
│  工具層     GitHub · Jira · Slack · Google Drive      │
│             PostgreSQL · Figma · DocuSign · ...        │
└─────────────────────────────────────────────────────┘
```

---

## Phase 0：個人驗證（1 週）

**目標**：驗證 Claude Code Teams 和 `claude -p` 的可行性

- [ ] 確認 Claude Code CLI 版本 ≥ 2.1
- [ ] 啟用 Agent Teams 實驗功能
- [ ] 跑一個 2-agent 範例（reviewer + implementer）
- [ ] 測試 `claude -p --output-format json` 程式化呼叫
- [ ] 測試 `claude mcp serve` MCP Server 模式
- [ ] 記錄效能、成本、限制

詳見：[phases/phase-0-validation.md](phases/phase-0-validation.md)

---

## Phase 1：基礎建設（2 週）

**目標**：部署 n8n + Dify 自託管環境

- [ ] Docker Compose 部署 n8n
- [ ] Docker Compose 部署 Dify
- [ ] 設定 Slack App（Bot Token + Event Subscription）
- [ ] n8n ↔ Slack 基礎連線測試
- [ ] Dify ↔ Claude API 連線測試
- [ ] 基礎安全設定（HTTPS、網路隔離）

詳見：[phases/phase-1-infrastructure.md](phases/phase-1-infrastructure.md)

---

## Phase 2：人人可用（2 週）

**目標**：全員可透過 Slack 使用 AI 問答

**效率提升重點**：
- 即時回答技術/業務問題（省去搜尋和等人回覆的時間）
- 文件摘要和翻譯（省去逐頁閱讀的時間）
- 資料分析和報表初稿（省去手動整理的時間）

- [ ] n8n Slack trigger → Claude API → Slack reply 流程
- [ ] 意圖路由（一般問答 / 程式碼 / 資料查詢）
- [ ] 基礎 prompt template（針對公司業務領域）
- [ ] 每人每日使用額度設定
- [ ] 使用教學文件（非技術人員版）
- [ ] 試行團隊選定 + 回饋收集機制

---

## Phase 3：開發者 Agent（2 週）

**目標**：工程師可透過 Slack 指派程式碼任務

**效率提升重點**：
- Code review 自動化（從 1-2 小時 → 5 分鐘）
- Bug 調查初步分析（從 30 分鐘 → 即時）
- 測試程式碼產生（從 1 小時 → 自動）

- [ ] n8n → `claude -p` wrapper 建立
- [ ] Slack trigger: `@bot review PR #123`
- [ ] Slack trigger: `@bot analyze bug JIRA-456`
- [ ] Slack trigger: `@bot write tests for src/auth.ts`
- [ ] 結果格式化回 Slack（Markdown）
- [ ] sd0x-dev-flow hooks 在 CLI 層生效驗證

---

## Phase 4：工具連接（2 週）

**目標**：Agent 能存取公司內部系統

**效率提升重點**：
- 直接查 DB 回答業務問題（省去寫 SQL + 等 DBA）
- 自動讀取 Jira ticket context（省去來回釐清需求）
- Google Drive 文件搜尋和摘要（省去翻找時間）

- [ ] MCP Server: PostgreSQL / MySQL（唯讀）
- [ ] MCP Server: GitHub（PR、Issue）
- [ ] MCP Server: Jira / Linear（ticket 讀取）
- [ ] MCP Server: Google Drive（文件搜尋）
- [ ] MCP Server: Confluence（知識庫）
- [ ] 權限矩陣：誰能透過 AI 存取什麼資料

---

## Phase 5：Agent Team（4 週）

**目標**：多 agent 自動化完整 workflow

**效率提升重點**：
- Feature 開發從需求到 PR：人工參與從 8 小時 → 30 分鐘審核
- Bug fix 從回報到修復：從 4 小時 → 1 小時
- 設計審核從手動逐項 → 自動掃描 + 建議

- [ ] 定義 agent 角色（Architect, Developer, Reviewer, Tester）
- [ ] n8n workflow: Feature 開發 pipeline
- [ ] n8n workflow: Bug fix pipeline
- [ ] n8n workflow: 文件更新 pipeline
- [ ] Agent Team 間通訊機制（n8n sub-workflow 或 A2A）
- [ ] 人工審核閘門（關鍵節點需 Slack 確認）

---

## Phase 6：治理與監控（2 週）

**目標**：管理層可見 ROI、合規可控

- [ ] 成本追蹤 dashboard（每人/每部門/每 agent）
- [ ] 使用量統計（request 次數、token 消耗）
- [ ] 審計日誌（所有 AI 互動存 DB）
- [ ] PII 過濾規則
- [ ] 月度 ROI 報告模板
- [ ] 異常偵測（過量使用、異常 prompt）

---

## Phase 7：持續擴展

- [ ] A2A 協定導入（跨部門 agent 互通）
- [ ] Ollama 本地推理（簡單問答零成本）
- [ ] 更多部門 agent（HR、Finance、Legal）
- [ ] Claude Cowork 評估（辦公場景）
- [ ] Fine-tuning / RAG 導入（公司知識庫）

---

## 效率提升量化指標

| 場景 | 目前花費 | 導入後 | 節省 |
|------|---------|--------|------|
| 技術問答 | 15-30 min 搜尋/問人 | 1-2 min AI 回答 | 90% |
| Code Review | 1-2 hr 人工 review | 5 min AI + 15 min 人工確認 | 80% |
| Bug 初步調查 | 30-60 min | 5 min AI 分析 | 85% |
| 寫測試程式碼 | 1-2 hr | 10 min AI 產生 + 修正 | 85% |
| 文件摘要 | 30 min 閱讀 | 2 min AI 摘要 | 90% |
| SQL 查詢 | 15 min 寫 + 等 DBA | 2 min AI + DB MCP | 85% |
| 會議紀錄整理 | 30 min | 5 min AI 整理 | 80% |
| 新人 onboarding | 2 週摸索 | 3 天 + AI 輔助 | 70% |

---

## 成本估算

| 階段 | 月成本 | 說明 |
|------|--------|------|
| Phase 0-1 | $0 | 個人 Max plan + Docker 自託管 |
| Phase 2 | $200-500 | Claude API（按 token） |
| Phase 3 | +$200 | Claude Code Max plan（1-2 seat） |
| Phase 4 | +$0 | MCP Server 自託管 |
| Phase 5 | +$500-1000 | 更多 API 用量 |
| Phase 6-7 | 持平或下降 | Ollama 分流 + 效率提升 |

**ROI 估算**：假設 50 人團隊，每人每天省 1 小時
= 50 × 22 天 × 1 小時 × $50/hr = **$55,000/月**
成本 < $2,000/月，**ROI > 27x**

---

## 風險與緩解

| 風險 | 緩解措施 |
|------|---------|
| API 供應商中斷 | 多 provider（Claude + OpenAI + Ollama） |
| 資料外洩 | PII 過濾 + 自託管 + 網路隔離 |
| 員工抗拒 | 從效率提升切入，非取代工作 |
| 成本失控 | 每人每日額度 + 管理 dashboard |
| AI 產出品質 | 人工審核閘門 + sd0x-dev-flow auto-loop |
| 廠商鎖定 | 押注開放標準（MCP + A2A），中間層可換 |
