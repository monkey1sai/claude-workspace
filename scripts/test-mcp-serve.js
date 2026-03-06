/**
 * MCP Server 測試腳本
 *
 * 測試 `claude mcp serve` 是否能正常啟動並回應 JSON-RPC 請求。
 *
 * 使用方式：
 *   終端 1：claude mcp serve
 *   終端 2：node scripts/test-mcp-serve.js
 *
 * 前置需求：
 *   - Claude Code CLI ≥ 2.1
 *   - Node.js ≥ 18
 */

const { spawn } = require('child_process');
const readline = require('readline');

// JSON-RPC 請求 ID 計數器
let requestId = 0;

function createJsonRpcRequest(method, params = {}) {
  return JSON.stringify({
    jsonrpc: '2.0',
    id: ++requestId,
    method,
    params,
  });
}

async function testMcpServe() {
  console.log('=== MCP Server 測試 ===\n');

  // 啟動 claude mcp serve
  console.log('1. 啟動 claude mcp serve...');
  const proc = spawn('claude', ['mcp', 'serve'], {
    stdio: ['pipe', 'pipe', 'pipe'],
  });

  const rl = readline.createInterface({ input: proc.stdout });

  // 收集回應
  const responses = [];
  rl.on('line', (line) => {
    try {
      const parsed = JSON.parse(line);
      responses.push(parsed);
      console.log('   收到回應:', JSON.stringify(parsed, null, 2).slice(0, 200));
    } catch {
      // 非 JSON 輸出，忽略
    }
  });

  proc.stderr.on('data', (data) => {
    const msg = data.toString().trim();
    if (msg) console.log('   stderr:', msg);
  });

  // 等待啟動
  await new Promise((resolve) => setTimeout(resolve, 3000));

  // 測試 1：initialize
  console.log('\n2. 發送 initialize 請求...');
  proc.stdin.write(
    createJsonRpcRequest('initialize', {
      protocolVersion: '2024-11-05',
      capabilities: {},
      clientInfo: { name: 'test-client', version: '1.0.0' },
    }) + '\n'
  );
  await new Promise((resolve) => setTimeout(resolve, 2000));

  // 測試 2：tools/list
  console.log('\n3. 發送 tools/list 請求...');
  proc.stdin.write(createJsonRpcRequest('tools/list') + '\n');
  await new Promise((resolve) => setTimeout(resolve, 2000));

  // 結束
  console.log('\n4. 關閉連線...');
  proc.stdin.end();
  proc.kill();

  // 報告
  console.log('\n=== 測試結果 ===');
  console.log(`收到 ${responses.length} 個回應`);

  if (responses.length >= 2) {
    console.log('✅ MCP Server 基本功能正常');

    // 檢查是否有 tools
    const toolsResponse = responses.find(
      (r) => r.result && r.result.tools
    );
    if (toolsResponse) {
      const toolNames = toolsResponse.result.tools.map((t) => t.name);
      console.log(`\n可用工具 (${toolNames.length}):`);
      toolNames.forEach((name) => console.log(`  - ${name}`));
    }
  } else {
    console.log('❌ MCP Server 回應不足，可能未正常啟動');
    console.log('   請確認 claude mcp serve 可在終端正常執行');
  }
}

testMcpServe().catch((err) => {
  console.error('測試失敗:', err.message);
  process.exit(1);
});
