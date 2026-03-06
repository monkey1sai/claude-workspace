# Phase 6：治理與管控

> 時間：2-3 週
> 目標：建立企業級 AI 使用治理框架（RBAC、成本追蹤、審計）
> 效率提升：可量化的 ROI、合規性、可擴展基礎
> 前置：Phase 5 完成

---

## 架構

```
┌─────────────────────────────────────────────┐
│              Admin Dashboard                 │
│  使用量 │ 成本 │ 角色管理 │ 審計日誌 │ 政策  │
└──────────────────┬──────────────────────────┘
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
   PostgreSQL    Redis     n8n Workflows
   (審計日誌)   (即時計數)  (政策執行)
```

## 步驟 1：角色存取控制（RBAC）

### 1.1 角色定義

| 角色 | 一般問答 | 程式任務 | MCP 查詢 | Agent 團隊 | 管理 |
|------|---------|---------|----------|-----------|------|
| employee | ✅ 50次/日 | ❌ | ❌ | ❌ | ❌ |
| engineer | ✅ 100次/日 | ✅ 20次/日 | ✅ GitHub, DB | ✅ | ❌ |
| pm | ✅ 100次/日 | ❌ | ✅ Jira, Notion | ❌ | ❌ |
| lead | ✅ 200次/日 | ✅ 50次/日 | ✅ All | ✅ | ❌ |
| admin | ✅ 無限 | ✅ 無限 | ✅ All | ✅ | ✅ |

### 1.2 資料庫 Schema

```sql
-- 使用者角色表
CREATE TABLE user_roles (
  slack_user_id VARCHAR(20) PRIMARY KEY,
  role VARCHAR(20) NOT NULL DEFAULT 'employee',
  department VARCHAR(50),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 角色權限表
CREATE TABLE role_permissions (
  role VARCHAR(20),
  feature VARCHAR(50),
  daily_limit INTEGER,
  PRIMARY KEY (role, feature)
);

-- 初始資料
INSERT INTO role_permissions VALUES
  ('employee', 'chat', 50),
  ('engineer', 'chat', 100),
  ('engineer', 'code_agent', 20),
  ('engineer', 'mcp_query', 50),
  ('engineer', 'agent_team', 10),
  ('pm', 'chat', 100),
  ('pm', 'mcp_query', 50),
  ('lead', 'chat', 200),
  ('lead', 'code_agent', 50),
  ('lead', 'mcp_query', 100),
  ('lead', 'agent_team', 20),
  ('admin', 'chat', -1),  -- -1 = unlimited
  ('admin', 'code_agent', -1),
  ('admin', 'mcp_query', -1),
  ('admin', 'agent_team', -1);
```

### 1.3 n8n 權限檢查 Node

```javascript
// 在每個 workflow 開頭加入
const userId = $json.user_id;
const feature = $json.feature;  // 'chat', 'code_agent', etc.

// 查詢 Redis 取得今日使用次數
const todayKey = `usage:${userId}:${feature}:${new Date().toISOString().slice(0, 10)}`;
const currentCount = await redis.get(todayKey) || 0;

// 查詢角色權限
const permission = await db.query(
  `SELECT daily_limit FROM role_permissions rp
   JOIN user_roles ur ON ur.role = rp.role
   WHERE ur.slack_user_id = $1 AND rp.feature = $2`,
  [userId, feature]
);

if (!permission.rows.length) {
  return { allowed: false, reason: '無此功能權限' };
}

const limit = permission.rows[0].daily_limit;
if (limit !== -1 && currentCount >= limit) {
  return { allowed: false, reason: `今日額度已用完（${limit}次）` };
}

// 放行並計數
await redis.incr(todayKey);
await redis.expire(todayKey, 86400);
return { allowed: true, remaining: limit === -1 ? '無限' : limit - currentCount - 1 };
```

## 步驟 2：成本追蹤

### 2.1 Token 計算

```javascript
// 記錄每次 API 呼叫的 token 消耗
const costRecord = {
  timestamp: new Date().toISOString(),
  user_id: userId,
  feature: feature,
  model: 'claude-sonnet-4-6',
  input_tokens: response.usage.input_tokens,
  output_tokens: response.usage.output_tokens,
  estimated_cost_usd: (
    response.usage.input_tokens * 0.003 / 1000 +
    response.usage.output_tokens * 0.015 / 1000
  ),
};
```

### 2.2 成本報表

```sql
-- 每日成本摘要
CREATE VIEW daily_cost_summary AS
SELECT
  DATE(timestamp) AS date,
  department,
  feature,
  COUNT(*) AS request_count,
  SUM(input_tokens) AS total_input_tokens,
  SUM(output_tokens) AS total_output_tokens,
  SUM(estimated_cost_usd) AS total_cost_usd
FROM api_usage_log u
JOIN user_roles r ON u.user_id = r.slack_user_id
GROUP BY DATE(timestamp), department, feature;

-- 月度部門成本
CREATE VIEW monthly_department_cost AS
SELECT
  TO_CHAR(timestamp, 'YYYY-MM') AS month,
  department,
  SUM(estimated_cost_usd) AS monthly_cost_usd,
  COUNT(DISTINCT user_id) AS active_users
FROM api_usage_log u
JOIN user_roles r ON u.user_id = r.slack_user_id
GROUP BY TO_CHAR(timestamp, 'YYYY-MM'), department;
```

### 2.3 成本警報

```
每日成本 > $50 → Slack 通知 admin
每週成本 > $300 → Slack 通知 admin + 自動降低非必要額度
單一使用者單日 > $10 → 自動暫停 + 通知
```

## 步驟 3：審計日誌

### 3.1 日誌 Schema

```sql
CREATE TABLE audit_log (
  id BIGSERIAL PRIMARY KEY,
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  user_id VARCHAR(20) NOT NULL,
  action VARCHAR(50) NOT NULL,      -- 'chat', 'code_review', 'db_query', etc.
  feature VARCHAR(50),
  request_summary TEXT,              -- 使用者要求摘要（脫敏）
  response_summary TEXT,             -- 回應摘要
  mcp_servers_used TEXT[],           -- 使用的 MCP Servers
  files_accessed TEXT[],             -- 存取的檔案
  duration_ms INTEGER,
  token_count INTEGER,
  status VARCHAR(20)                 -- 'success', 'error', 'denied', 'timeout'
);

-- 索引
CREATE INDEX idx_audit_user ON audit_log(user_id);
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp);
CREATE INDEX idx_audit_action ON audit_log(action);
```

### 3.2 敏感資料脫敏

```javascript
function sanitizeForAudit(text) {
  return text
    .replace(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g, '[EMAIL]')
    .replace(/\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b/g, '[CARD]')
    .replace(/\b(sk-|xoxb-|ghp_|glpat-)[a-zA-Z0-9]+\b/g, '[API_KEY]')
    .replace(/password\s*[:=]\s*\S+/gi, 'password=[REDACTED]');
}
```

## 步驟 4：Admin Dashboard

### 4.1 技術選型

```
Dify Dashboard App（簡單版）
  或
n8n + PostgreSQL + Metabase（進階版）
```

### 4.2 Dashboard 頁面

| 頁面 | 內容 |
|------|------|
| 總覽 | 今日請求數、活躍使用者、今日成本、錯誤率 |
| 使用量 | 按部門/角色/功能的使用趨勢圖 |
| 成本 | 月度成本、部門分攤、預測 |
| 角色管理 | CRUD 使用者角色 |
| 審計 | 可搜尋的審計日誌 |
| 政策 | 額度設定、功能開關 |

## 步驟 5：合規政策

### 5.1 資料處理政策

```markdown
# AI 使用政策（範本）

## 允許
- 一般問答、技術諮詢
- 公開資料的分析和摘要
- 程式碼 Review 和生成

## 禁止
- 輸入客戶個資（PII）
- 輸入財務機密資料
- 輸入密碼、API Key 等憑證
- 用 AI 做最終決策（需人工確認）

## 資料保留
- API 呼叫日誌保留 90 天
- 審計日誌保留 1 年
- 對話內容不保留（僅保留摘要）
```

### 5.2 自動政策執行

```javascript
// 輸入過濾器：偵測敏感資料
function detectSensitiveInput(text) {
  const patterns = [
    { name: 'credit_card', regex: /\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b/ },
    { name: 'api_key', regex: /\b(sk-|xoxb-|ghp_|AKIA)[a-zA-Z0-9]{20,}\b/ },
    { name: 'password', regex: /password\s*[:=]\s*\S{8,}/i },
  ];

  const detected = patterns.filter(p => p.regex.test(text));
  return detected.length > 0 ? detected.map(d => d.name) : null;
}
```

---

## Phase 6 完成標準

- [ ] RBAC 角色系統運作正常
- [ ] 每日額度機制按角色生效
- [ ] 成本追蹤和報表可查看
- [ ] 成本警報機制生效
- [ ] 審計日誌完整記錄所有操作
- [ ] 敏感資料脫敏機制生效
- [ ] Admin Dashboard 基本功能可用
- [ ] AI 使用政策發布並宣導
