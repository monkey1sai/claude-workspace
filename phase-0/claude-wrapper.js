const { execFileSync } = require('child_process');

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
    maxBuffer: 10 * 1024 * 1024, // 10MB
    timeout: options.timeout || 300000, // 5 min
    env: { ...process.env, CLAUDECODE: undefined },
  });

  return JSON.parse(result);
}

// 測試
const result = callClaude('列出目前目錄的檔案並說明每個檔案的用途');
console.log(JSON.stringify(result, null, 2));
