/**
 * Claude Code CLI Wrapper
 *
 * 提供程式化呼叫 Claude Code Agent 的封裝。
 * 用於 n8n Execute Function Node 或獨立腳本。
 *
 * 使用方式：
 *   const { callClaude } = require('./claude-wrapper');
 *   const result = callClaude('列出目前目錄的檔案');
 *   console.log(result);
 */

const { execFileSync } = require('child_process');

/**
 * 呼叫 Claude Code Agent
 * @param {string} prompt - 任務描述
 * @param {object} [options] - 設定選項
 * @param {number} [options.maxTurns=10] - 最大迴圈次數
 * @param {number} [options.timeout=300000] - 逾時（毫秒）
 * @param {string} [options.cwd] - 工作目錄
 * @returns {object} Claude 回應的 JSON 物件
 */
function callClaude(prompt, options = {}) {
  const args = [
    '-p',
    '--output-format', 'json',
    '--max-turns', String(options.maxTurns || 10),
    prompt,
  ];

  const result = execFileSync('claude', args, {
    cwd: options.cwd || process.cwd(),
    encoding: 'utf-8',
    maxBuffer: 10 * 1024 * 1024,   // 10MB
    timeout: options.timeout || 300000, // 5 分鐘
  });

  return JSON.parse(result);
}

/**
 * 呼叫 Claude Code Agent（安全模式，僅讀取）
 */
function callClaudeReadOnly(prompt, options = {}) {
  return callClaude(prompt, {
    ...options,
    maxTurns: options.maxTurns || 5,
  });
}

// 如果直接執行此檔案，跑測試
if (require.main === module) {
  console.log('測試 Claude Wrapper...\n');

  try {
    const result = callClaude('回覆 "Hello from Claude Wrapper!" 這句話，不要多說。', {
      maxTurns: 1,
      timeout: 60000,
    });
    console.log('✅ 成功：', JSON.stringify(result, null, 2).slice(0, 500));
  } catch (err) {
    console.error('❌ 失敗：', err.message);
    process.exit(1);
  }
}

module.exports = { callClaude, callClaudeReadOnly };
