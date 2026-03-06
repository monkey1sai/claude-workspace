# Phase 7：擴展與演進

> 時間：持續迭代
> 目標：導入 A2A 協議、本地模型、更多部門、持續優化
> 效率提升：跨組織 Agent 互通、降低成本、覆蓋更多場景
> 前置：Phase 6 完成

---

## 架構演進

```
Phase 6 架構                          Phase 7 架構
┌──────────┐                   ┌──────────────────────────┐
│  Slack   │                   │  Slack / Teams / Web UI  │
└────┬─────┘                   └───────────┬──────────────┘
     │                                     │
┌────┴─────┐                   ┌───────────┴──────────────┐
│   n8n    │         →→→       │     n8n + A2A Gateway    │
└────┬─────┘                   └───────────┬──────────────┘
     │                              ┌──────┼──────┐
┌────┴─────┐                   ┌────┴──┐ ┌─┴────┐ ┌┴─────┐
│  Claude  │                   │Claude │ │Ollama│ │外部AI│
│  Code    │                   │ Code  │ │(本地)│ │Agent │
└────┬─────┘                   └───┬───┘ └──┬───┘ └──┬───┘
     │                             │        │        │
┌────┴─────┐                   ┌───┴────────┴────────┴───┐
│MCP Server│                   │     MCP + A2A Servers    │
└──────────┘                   └─────────────────────────┘
```

## 7.1 A2A（Agent-to-Agent）協議

### 什麼是 A2A？

Google 發起的開放標準，讓不同 AI Agent 可以互相發現、溝通和協作。

```
Agent A (Claude) ←──A2A Protocol──→ Agent B (Gemini/GPT)
   │                                      │
   └── MCP Servers                        └── MCP Servers
```

### A2A vs MCP

| 面向 | MCP | A2A |
|------|-----|-----|
| 用途 | Agent ↔ 工具 | Agent ↔ Agent |
| 比喻 | USB 接口 | HTTP 協議 |
| 關係 | 互補 | 互補 |

### 導入 A2A

```javascript
// A2A Agent Card（每個 Agent 的自我介紹）
const agentCard = {
  name: 'company-ai-assistant',
  description: '公司 AI 助手，可回答問題、做 Code Review、查詢內部資料',
  capabilities: ['chat', 'code-review', 'data-query'],
  protocols: ['MCP', 'A2A'],
  endpoint: 'https://ai.company.internal/a2a',
};

// A2A 讓外部 Agent 可以呼叫我們的 Agent
// 例如：合作夥伴的 AI 可以查詢我們的 API 文件
```

### 使用場景

| 場景 | A2A 互動 |
|------|---------|
| 跨部門 Agent 協作 | 行銷 Agent ↔ 數據 Agent |
| 合作夥伴整合 | 我方 Agent ↔ 供應商 Agent |
| 多模型協作 | Claude Agent ↔ Gemini Agent（各擅所長） |

## 7.2 本地模型（Ollama）

### 為什麼需要本地模型？

| 因素 | Cloud（Claude） | Local（Ollama） |
|------|----------------|----------------|
| 成本 | 按 token 計費 | 固定硬體成本 |
| 隱私 | 資料離開內網 | 資料不出內網 |
| 速度 | 網路延遲 | 本地快速 |
| 能力 | 最強 | 夠用 |

### 策略：分流

```
使用者請求
    │
    ▼
[智慧路由]
    ├── 簡單問答（FAQ、翻譯）→ Ollama（免費）
    ├── 中等任務（摘要、格式化）→ Ollama 或 Claude Haiku（低成本）
    └── 複雜任務（分析、程式、推理）→ Claude Sonnet/Opus（高品質）
```

### 部署 Ollama

```bash
# 安裝
curl -fsSL https://ollama.com/install.sh | sh

# 下載模型
ollama pull llama3.3:70b      # 通用
ollama pull codellama:34b     # 程式碼
ollama pull qwen2.5:32b       # 中文

# API 端點
# http://localhost:11434/api/generate
```

### n8n 路由設定

```javascript
function routeToModel(request) {
  const complexity = estimateComplexity(request.text);

  if (complexity === 'simple') {
    return {
      provider: 'ollama',
      model: 'llama3.3:70b',
      endpoint: 'http://localhost:11434/api/generate',
      cost: 0,
    };
  }

  if (complexity === 'medium') {
    return {
      provider: 'anthropic',
      model: 'claude-haiku-4-5-20251001',
      cost: 'low',
    };
  }

  return {
    provider: 'anthropic',
    model: 'claude-sonnet-4-6',
    cost: 'standard',
  };
}
```

## 7.3 更多部門導入

### 導入優先順序

| 優先 | 部門 | AI 應用 | 預期效益 |
|------|------|---------|---------|
| 1 | 工程 | Code Review、Bug 分析、文件 | 節省 30% review 時間 |
| 2 | PM | 需求分析、競品調研、會議摘要 | 節省 20% 文書時間 |
| 3 | 客服 | FAQ 自動回覆、工單分類 | 降低 40% 回應時間 |
| 4 | 行銷 | 文案生成、數據分析、報告 | 提升產出量 2x |
| 5 | HR | 履歷篩選、政策問答 | 節省 50% 篩選時間 |
| 6 | 法務 | 合約審查、法規查詢 | 初步審查自動化 |

### 部門專屬 System Prompt

```javascript
const departmentPrompts = {
  engineering: '你是資深軟體工程顧問...',
  pm: '你是產品管理助手，擅長需求分析和規劃...',
  support: '你是客服助手，回答需禮貌、精確、附上參考文件...',
  marketing: '你是行銷文案助手，風格活潑但專業...',
  hr: '你是 HR 助手，回答需符合勞基法規定...',
  legal: '你是法律助手，回答附帶免責聲明...',
};
```

## 7.4 進階功能路線圖

### 短期（1-2 個月）

- [ ] RAG（檢索增強生成）：連接公司知識庫
- [ ] 語音輸入：Slack Huddle → 語音轉文字 → AI 處理
- [ ] 排程任務：每日自動生成報表

### 中期（3-6 個月）

- [ ] 多模態：圖片分析（設計稿 review、圖表解讀）
- [ ] 自訂 Agent：各部門可自建專屬 Agent
- [ ] Agent Marketplace：內部 Agent 市集

### 長期（6-12 個月）

- [ ] A2A 跨組織：與合作夥伴 Agent 互通
- [ ] 自主 Agent：可自動觸發並完成端到端任務
- [ ] AI 輔助決策：資料驅動的建議引擎

## 7.5 持續優化指標

### KPI 追蹤

| 指標 | 目標 | 量測方式 |
|------|------|---------|
| 月活躍使用者 | > 80% 員工 | Slack 使用者統計 |
| 平均回應時間 | < 5 秒 | API 日誌 |
| 使用者滿意度 | > 4.0/5.0 | 月度問卷 |
| 每月成本/人 | < $20 | 成本報表 |
| 工作時間節省 | > 5 小時/人/月 | 自評問卷 |

### 成本優化策略

```
1. Prompt caching（減少重複 token）
2. 本地模型分流（簡單任務不用 Claude）
3. 回應快取（相同問題不重複呼叫）
4. Batch API（非即時任務批次處理，成本 -50%）
```

---

## Phase 7 完成標準（持續）

- [ ] A2A 基礎架構設定完成
- [ ] Ollama 本地模型部署並分流運作
- [ ] 至少 3 個部門正式導入
- [ ] RAG 知識庫連線
- [ ] KPI 追蹤機制建立
- [ ] 月度優化報告產出
