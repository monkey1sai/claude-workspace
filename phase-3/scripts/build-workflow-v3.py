"""
Phase 3: 建構 workflow-v3.json
在 Phase 2 的 16-node workflow 基礎上新增 code 分支節點。

修改：
1. Intent Router — 修正 SQL 誤判，增強 code 關鍵字
2. IF General false 分支 → 改連 IF Code Intent（不再直連 Reply Phase Not Ready）

新增節點：
- IF Code Intent
- Code Sub-Router
- IF PR Review
- Fetch PR Diff
- Build Code Prompt
- Call Claude API for Code
- Format Code Response
"""

import json
import copy
import uuid
import os

# 讀取 Phase 2 workflow
workflow_path = os.path.join(os.path.dirname(__file__), '..', '..', 'phase-2', 'n8n', 'workflow-v2.json')
with open(workflow_path, 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# === 1. 修正 Intent Router 的 jsCode ===
for node in workflow['nodes']:
    if node['name'] == 'Intent Router':
        node['parameters']['jsCode'] = '''// 意圖路由：關鍵字分類（Phase 3 升級版）
// 修正：SQL 分析/解釋不再誤判為 data 意圖
const query = $json.query.toLowerCase();

// 分析動詞（有這些動詞時，即使包含 SQL 也歸類為 general/code）
const analysisVerbs = ['分析', '解釋', '說明', '最佳化', '優化', 'analyze', 'explain', 'optimize', 'review'];
const hasAnalysisVerb = analysisVerbs.some(v => query.includes(v));

// 程式碼相關關鍵字（Phase 3 開放）
const codeKeywords = [
  'review pr', 'pr review', 'code review', 'review code',
  'pr #', 'pr#', 'pull request',
  'write test', 'gen test', 'generate test',
  'debug', 'analyze bug', 'stack trace',
  'explain code', 'explain this',
  'refactor',
  '程式碼審查', '寫測試', '分析錯誤', '產生測試',
  '生成文件', 'generate doc', 'gen doc',
  '解釋程式碼', '重構'
];

// 資料查詢關鍵字（Phase 4 才開放）
// 注意：只有明確要求「查資料庫」「跑報表」才觸發，純 SQL 分析歸為 code
const dataKeywords = ['query db', '查資料庫', '跑報表', '資料庫查詢', '幫我查', '查一下資料'];

// 偵測程式碼區塊（使用者直接貼程式碼）
const hasCodeBlock = query.includes('```');

let intent = 'general';

// 先檢查是否有 code block
if (hasCodeBlock) {
  intent = 'code';
} else {
  // 檢查 code 關鍵字
  for (const kw of codeKeywords) {
    if (query.includes(kw)) { intent = 'code'; break; }
  }
  // 只有沒有分析動詞時才檢查 data 關鍵字
  if (intent === 'general' && !hasAnalysisVerb) {
    for (const kw of dataKeywords) {
      if (query.includes(kw)) { intent = 'data'; break; }
    }
  }
}

return [{json: { ...$json, intent }}];'''
        break

# === 2. 定義新節點 ===

# 節點位置（n8n canvas 座標）
BASE_X = 1400
BASE_Y = 300

new_nodes = []

# 2a. IF Code Intent
if_code_intent = {
    "parameters": {
        "conditions": {
            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
            "conditions": [{
                "id": str(uuid.uuid4()),
                "leftValue": "={{ $json.intent }}",
                "rightValue": "code",
                "operator": {"type": "string", "operation": "equals"}
            }]
        },
        "options": {}
    },
    "id": str(uuid.uuid4()),
    "name": "IF Code Intent",
    "type": "n8n-nodes-base.if",
    "typeVersion": 2,
    "position": [BASE_X, BASE_Y]
}
new_nodes.append(if_code_intent)

# 2b. Code Sub-Router
code_sub_router = {
    "parameters": {
        "jsCode": '''// 細分 code 子意圖 + 解析參數
const query = $json.query;
const queryLower = query.toLowerCase();

let subIntent = 'code-explain'; // 預設：程式碼說明
let params = {};

// PR Review：匹配 PR#123, PR 123, review pr 123 等
const prMatch = query.match(/(?:pr|pull\\s*request)\\s*#?\\s*(\\d+)/i);
if (prMatch || queryLower.includes('review pr') || queryLower.includes('pr review') || queryLower.includes('code review') || queryLower.includes('程式碼審查')) {
  subIntent = 'pr-review';
  params.prNumber = prMatch ? prMatch[1] : null;
  // 嘗試提取 repo（格式：owner/repo）
  const repoMatch = query.match(/(?:in|from|for)\\s+([\\w\\-]+\\/[\\w\\-]+)/i);
  params.repo = repoMatch ? repoMatch[1] : null;
}

// Bug 分析
else if (queryLower.includes('bug') || queryLower.includes('error') || queryLower.includes('analyze bug') || queryLower.includes('stack trace') || queryLower.includes('分析錯誤') || queryLower.includes('debug')) {
  subIntent = 'bug-analysis';
}

// 測試生成
else if (queryLower.includes('write test') || queryLower.includes('gen test') || queryLower.includes('寫測試') || queryLower.includes('測試') || queryLower.includes('產生測試')) {
  subIntent = 'test-gen';
}

// 文件生成
else if (queryLower.includes('doc') || queryLower.includes('文件') || queryLower.includes('generate doc') || queryLower.includes('生成文件')) {
  subIntent = 'doc-gen';
}

// 重構
else if (queryLower.includes('refactor') || queryLower.includes('重構')) {
  subIntent = 'code-explain';
}

// 提取程式碼區塊
const codeBlockMatch = query.match(/```[\\s\\S]*?```/);
const codeBlock = codeBlockMatch ? codeBlockMatch[0] : null;

return [{json: {
  ...$json,
  subIntent,
  params,
  codeBlock
}}];'''
    },
    "id": str(uuid.uuid4()),
    "name": "Code Sub-Router",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [BASE_X + 200, BASE_Y]
}
new_nodes.append(code_sub_router)

# 2c. IF PR Review
if_pr_review = {
    "parameters": {
        "conditions": {
            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
            "conditions": [{
                "id": str(uuid.uuid4()),
                "leftValue": "={{ $json.subIntent }}",
                "rightValue": "pr-review",
                "operator": {"type": "string", "operation": "equals"}
            }, {
                "id": str(uuid.uuid4()),
                "leftValue": "={{ $json.params.prNumber }}",
                "rightValue": "",
                "operator": {"type": "string", "operation": "exists"}
            }],
            "combinator": "and"
        },
        "options": {}
    },
    "id": str(uuid.uuid4()),
    "name": "IF PR Review",
    "type": "n8n-nodes-base.if",
    "typeVersion": 2,
    "position": [BASE_X + 400, BASE_Y]
}
new_nodes.append(if_pr_review)

# 2d. Fetch PR Diff（GitHub API）
fetch_pr_diff = {
    "parameters": {
        "method": "GET",
        "url": "=https://api.github.com/repos/{{ $json.params.repo || '<GITHUB_DEFAULT_REPO>' }}/pulls/{{ $json.params.prNumber }}",
        "sendHeaders": True,
        "headerParameters": {
            "parameters": [
                {"name": "Authorization", "value": "Bearer <GITHUB_TOKEN>"},
                {"name": "Accept", "value": "application/vnd.github.v3.diff"},
                {"name": "User-Agent", "value": "n8n-ai-assistant"}
            ]
        },
        "options": {
            "response": {
                "response": {
                    "responseFormat": "text"
                }
            },
            "timeout": 30000
        }
    },
    "id": str(uuid.uuid4()),
    "name": "Fetch PR Diff",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [BASE_X + 600, BASE_Y - 100]
}
new_nodes.append(fetch_pr_diff)

# 2e. Build Code Prompt
build_code_prompt = {
    "parameters": {
        "jsCode": '''// 根據子意圖組裝 system prompt + user message
const subIntent = $json.subIntent || $('Code Sub-Router').first().json.subIntent;
const query = $json.query || $('Code Sub-Router').first().json.query;
const codeBlock = $json.codeBlock || $('Code Sub-Router').first().json.codeBlock;

const systemPrompts = {
  'pr-review': '你是資深軟體工程師，負責 Code Review。分析以下 PR diff 並提供：\\n1. **摘要**：這個 PR 做了什麼\\n2. **問題**：潛在的 bug、安全風險、效能問題（標示嚴重程度：🔴高/🟡中/🟢低）\\n3. **建議**：改進建議\\n4. **結論**：是否建議合併（✅/⚠️/❌）\\n使用繁體中文回覆。',

  'bug-analysis': '你是資深 DevOps 工程師，擅長分析錯誤和 bug。分析以下錯誤資訊並提供：\\n1. **根因分析**：最可能的原因\\n2. **影響範圍**：受影響的功能\\n3. **修復建議**：具體的修復步驟\\n4. **預防措施**：如何避免再次發生\\n使用繁體中文回覆。',

  'code-explain': '你是技術文件撰寫者。用清晰易懂的方式解釋以下程式碼：\\n1. **功能概述**：這段程式碼的目的\\n2. **逐段說明**：關鍵邏輯的解釋\\n3. **使用範例**：如何使用（若適用）\\n使用繁體中文回覆。',

  'test-gen': '你是測試工程師。為以下程式碼生成測試：\\n1. 使用合適的測試框架（Jest/Mocha/pytest 等，根據語言判斷）\\n2. 涵蓋正常情況、邊界情況、錯誤處理\\n3. 測試命名清晰\\n4. 加上繁體中文註解\\n直接輸出可執行的測試程式碼。',

  'doc-gen': '你是技術文件撰寫者。為以下程式碼生成文件：\\n1. 函式/類別說明\\n2. 參數和回傳值\\n3. 使用範例\\n4. 注意事項\\n輸出 Markdown 格式，使用繁體中文。'
};

const systemPrompt = systemPrompts[subIntent] || systemPrompts['code-explain'];

// 組裝 user message
let userMessage = query;

// 如果是 PR review 且有 diff 資料
const prDiff = $json.data || $json.body || null;
if (subIntent === 'pr-review' && prDiff) {
  // 截斷過長的 diff（避免超過 context window）
  const diffText = typeof prDiff === 'string' ? prDiff : JSON.stringify(prDiff);
  const maxLen = 80000;
  const truncated = diffText.length > maxLen ? diffText.substring(0, maxLen) + '\\n... (diff 已截斷)' : diffText;
  userMessage = 'PR Diff:\\n\\n' + truncated;
}

// 從上游取得 channel 和 user 資訊
const channelId = $('Extract Message').first().json.channelId;
const userId = $('Extract Message').first().json.userId;
const userName = $('Extract Message').first().json.userName;
const rateRemaining = $('Rate Limiter').first().json.rateRemaining;
const dailyLimit = $('Rate Limiter').first().json.dailyLimit;

return [{json: {
  systemPrompt,
  userMessage,
  subIntent,
  channelId,
  userId,
  userName,
  rateRemaining,
  dailyLimit
}}];'''
    },
    "id": str(uuid.uuid4()),
    "name": "Build Code Prompt",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [BASE_X + 800, BASE_Y]
}
new_nodes.append(build_code_prompt)

# 2f. Call Claude API for Code
call_claude_api = {
    "parameters": {
        "method": "POST",
        "url": "https://api.anthropic.com/v1/messages",
        "sendHeaders": True,
        "headerParameters": {
            "parameters": [
                {"name": "x-api-key", "value": "<ANTHROPIC_API_KEY>"},
                {"name": "anthropic-version", "value": "2023-06-01"},
                {"name": "Content-Type", "value": "application/json"}
            ]
        },
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": '={{ JSON.stringify({ model: "claude-haiku-4-5-20251001", max_tokens: 4096, system: $json.systemPrompt, messages: [{ role: "user", content: $json.userMessage }] }) }}',
        "options": {
            "response": {
                "response": {
                    "responseFormat": "json"
                }
            },
            "timeout": 120000
        }
    },
    "id": str(uuid.uuid4()),
    "name": "Call Claude API for Code",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [BASE_X + 1000, BASE_Y]
}
new_nodes.append(call_claude_api)

# 2g. Format Code Response
format_code_response = {
    "parameters": {
        "jsCode": '''// 解析 Anthropic API 回應 + 格式化
const response = $json;
const content = response.content && response.content[0] ? response.content[0].text : '無法取得回應，請稍後再試。';

const subIntent = $('Build Code Prompt').first().json.subIntent;
const channelId = $('Build Code Prompt').first().json.channelId;
const userId = $('Build Code Prompt').first().json.userId;
const userName = $('Build Code Prompt').first().json.userName;
const rateRemaining = $('Build Code Prompt').first().json.rateRemaining;
const dailyLimit = $('Build Code Prompt').first().json.dailyLimit;

const icons = {
  'pr-review': ':mag:',
  'bug-analysis': ':beetle:',
  'code-explain': ':books:',
  'test-gen': ':white_check_mark:',
  'doc-gen': ':page_facing_up:'
};

const titles = {
  'pr-review': 'Code Review 結果',
  'bug-analysis': 'Bug 分析結果',
  'code-explain': '程式碼說明',
  'test-gen': '測試程式碼',
  'doc-gen': '文件生成結果'
};

const icon = icons[subIntent] || ':robot:';
const title = titles[subIntent] || 'AI 助手回覆';

// 截斷過長回覆（Mattermost 訊息限制 ~16000 字元）
let body = content;
if (body.length > 14000) {
  body = body.substring(0, 14000) + '\\n\\n... (回覆過長已截斷)';
}

const answer = icon + ' **' + title + '**\\n\\n' + body;

return [{json: {answer, channelId, userId, userName, rateRemaining, dailyLimit}}];'''
    },
    "id": str(uuid.uuid4()),
    "name": "Format Code Response",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [BASE_X + 1200, BASE_Y]
}
new_nodes.append(format_code_response)

# === 3. 加入新節點到 workflow ===
workflow['nodes'].extend(new_nodes)

# === 4. 修改連接 ===
connections = workflow['connections']

# 4a. IF General false 分支 → IF Code Intent（取代直連 Reply Phase Not Ready）
# n8n IF node v2: main[0] = TRUE, main[1] = FALSE
if 'IF General' in connections:
    if_general_conn = connections['IF General']
    if 'main' in if_general_conn:
        # main[0] (TRUE, 是 general) 保持不動 → Call Dify API
        # main[1] (FALSE, 不是 general) 改指向 IF Code Intent
        if_general_conn['main'][1] = [{"node": "IF Code Intent", "type": "main", "index": 0}]

# 4b. IF Code Intent 連接
# main[0] = TRUE (是 code 意圖) → Code Sub-Router
# main[1] = FALSE (不是 code，即 data 意圖) → Reply Phase Not Ready
connections["IF Code Intent"] = {
    "main": [
        [{"node": "Code Sub-Router", "type": "main", "index": 0}],
        [{"node": "Reply Phase Not Ready", "type": "main", "index": 0}]
    ]
}

# 4c. Code Sub-Router → IF PR Review
connections["Code Sub-Router"] = {
    "main": [
        [{"node": "IF PR Review", "type": "main", "index": 0}]
    ]
}

# 4d. IF PR Review 連接
# main[0] = TRUE (是 PR review) → Fetch PR Diff
# main[1] = FALSE (其他 code 子意圖) → Build Code Prompt
connections["IF PR Review"] = {
    "main": [
        [{"node": "Fetch PR Diff", "type": "main", "index": 0}],
        [{"node": "Build Code Prompt", "type": "main", "index": 0}]
    ]
}

# 4e. Fetch PR Diff → Build Code Prompt
connections["Fetch PR Diff"] = {
    "main": [
        [{"node": "Build Code Prompt", "type": "main", "index": 0}]
    ]
}

# 4f. Build Code Prompt → Call Claude API for Code
connections["Build Code Prompt"] = {
    "main": [
        [{"node": "Call Claude API for Code", "type": "main", "index": 0}]
    ]
}

# 4g. Call Claude API for Code → Format Code Response
connections["Call Claude API for Code"] = {
    "main": [
        [{"node": "Format Code Response", "type": "main", "index": 0}]
    ]
}

# 4h. Format Code Response → Log Usage（共用現有節點）
connections["Format Code Response"] = {
    "main": [
        [{"node": "Log Usage", "type": "main", "index": 0}]
    ]
}

# === 5. 更新 workflow 名稱 ===
workflow['name'] = 'Mattermost AI Assistant v3'

# === 6. 替換 token 為佔位符（確保不洩露） ===
workflow_json = json.dumps(workflow, ensure_ascii=False, indent=2)
# 不替換已有的佔位符，但確認新節點的佔位符正確

# === 7. 輸出 ===
output_path = os.path.join(os.path.dirname(__file__), '..', 'n8n', 'workflow-v3.json')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(workflow_json)

# 統計
node_count = len(workflow['nodes'])
connection_count = len(workflow['connections'])
print(f'workflow-v3.json 已建立')
print(f'節點數：{node_count}')
print(f'連接數：{connection_count}')
print(f'新增節點：{", ".join(n["name"] for n in new_nodes)}')
