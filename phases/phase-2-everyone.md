# Phase 2：人人可用

> 時間：2 週
> 目標：全員可透過 Slack 使用 AI 問答
> 效率提升：即時問答、文件摘要、資料分析初稿
> 前置：Phase 1 完成

---

## 架構

```
Slack @ai-assistant 你好
        │
        ▼
n8n Slack Trigger
        │
        ▼
n8n Router（意圖判斷）
   ├── 一般問答 ──→ Claude API ──→ Slack 回覆
   ├── 程式碼 ────→ （Phase 3 啟用）
   └── 資料查詢 ──→ （Phase 4 啟用）
```

## 步驟 1：n8n 完整 Slack ↔ Claude 流程

在 n8n 中建立 workflow：

```
[Slack Trigger]
    → [Rate Limiter]（檢查每日額度）
    → [Claude API HTTP Request]（問 Claude）
    → [Format Response]（Markdown 格式化）
    → [Slack Send Message]（回覆）
```

### Claude API HTTP Request 設定

```
Method: POST
URL: https://api.anthropic.com/v1/messages
Headers:
  x-api-key: {{ $env.ANTHROPIC_API_KEY }}
  anthropic-version: 2023-06-01
  content-type: application/json
Body:
{
  "model": "claude-sonnet-4-6",
  "max_tokens": 4096,
  "messages": [
    {
      "role": "user",
      "content": "{{ $json.text }}"
    }
  ],
  "system": "你是公司的 AI 助手。用繁體中文回答。保持簡潔專業。"
}
```

## 步驟 2：每日額度控制

使用 n8n 的 Redis 或 SQLite node 追蹤每人用量：

```
每次請求 → 檢查 user_id 今日計數
  ├── < 50 次 → 放行，計數 +1
  └── ≥ 50 次 → 回覆「今日額度已用完，明天再試」
```

## 步驟 3：System Prompt 設定

根據公司業務客製化：

```
你是 [公司名] 的 AI 助手。

## 你可以幫助的事情
- 回答技術問題（程式、架構、工具）
- 文件摘要和翻譯
- 寫作潤稿（email、報告、文件）
- 資料分析建議
- 會議紀錄整理

## 你不應該做的事情
- 不透露公司機密資訊
- 不做財務或法律建議
- 不存取公司內部系統（Phase 4 才啟用）

## 回覆格式
- 使用繁體中文
- 保持簡潔（Slack 閱讀友好）
- 程式碼用 code block
- 長回覆用 thread
```

## 步驟 4：使用教學文件

建立給非技術人員的教學（存入公司 wiki）：

```markdown
# AI 助手使用指南

## 怎麼用？
在 Slack 任何頻道或 DM 中輸入 @ai-assistant + 你的問題

## 範例

### 問答
@ai-assistant OAuth 2.0 的 refresh token 怎麼運作？

### 摘要
@ai-assistant 幫我摘要以下會議紀錄：
（貼上內容）

### 翻譯
@ai-assistant 翻譯成英文：
（貼上內容）

### 寫作
@ai-assistant 幫我寫一封 email 回覆客戶延遲交付的情況

## 注意事項
- 不要貼入密碼、API Key 等機密資訊
- 每天有 50 次使用額度
- AI 回覆僅供參考，重要決策請人工確認
```

## 步驟 5：試行團隊 + 回饋

1. 選 1-2 個團隊（建議：工程 + PM）先試行
2. 建立 #ai-feedback 頻道收集回饋
3. 每週彙整使用數據和回饋
4. 調整 system prompt 和額度

---

## Phase 2 完成標準

- [ ] 全員可在 Slack @bot 提問並收到回覆
- [ ] 每日額度機制生效
- [ ] 使用教學文件發布
- [ ] 試行團隊回饋正面
- [ ] 使用量統計可查看
