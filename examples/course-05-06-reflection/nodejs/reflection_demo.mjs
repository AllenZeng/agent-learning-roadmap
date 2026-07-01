#!/usr/bin/env node
/**
 * 课程五 05-06 Reflection 示例 (Node.js)
 *
 * 演示由外部失败信号触发的修正闭环：
 * 触发 -> 分类 -> 修正 -> 重新验证 -> 成功或停止。
 */

import readline from 'node:readline/promises';
import { stdin as input, stdout as output } from 'node:process';

class ActionResult {
  constructor(output, cost = 0) {
    this.output = output;
    this.cost = cost;
  }
}

class ValidationResult {
  constructor({ passed, message = '', evidence = '', errorType = '' }) {
    this.passed = passed;
    this.message = message;
    this.evidence = evidence;
    this.errorType = errorType;
  }
}

const mockNotes = {
  'agent-memory-mechanism.md': `
Memory 模块的 session 数据由 MemoryStore 管理。
expired session 数据由 MemoryStore.decay() 在每次 start_session 时清理，底层调用 _purge_old_records()。
注意：Memory 模块不提供 clear_expired() 方法。
`,
  'session-manager.md': `
正确做法：
    def cleanup(self):
        self.memory_store.decay()
`,
};

const buggyCleanupCode = `
def cleanup(self):
    for sid in list(self._sessions.keys()):
        if self._sessions[sid].expired:
            del self._sessions[sid]
`;

const correctCleanupCode = `
def cleanup(self):
    self.memory_store.decay()
`;

function validateJsonSchema(text) {
  const required = ['tool_name', 'args', 'reason'];
  const missing = required.filter(field => !text.includes(field));
  if (missing.length) {
    return new ValidationResult({
      passed: false,
      message: `Schema 校验失败：缺少必填字段 ${missing.join(', ')}`,
      evidence: `missing=${missing.join(',')}`,
      errorType: 'schema_error',
    });
  }
  return new ValidationResult({ passed: true, message: 'Schema 校验通过' });
}

function validateToolCall(text) {
  if (text.includes('limit=500')) {
    return new ValidationResult({
      passed: false,
      message: '参数错误：limit 必须在 1-100 之间',
      evidence: '工具返回: Error: limit must be 1-100 (got 500)',
      errorType: 'tool_param_error',
    });
  }
  if (text.includes('query=""')) {
    return new ValidationResult({
      passed: false,
      message: '参数错误：query 不能为空',
      evidence: '工具返回: Error: query parameter is required',
      errorType: 'tool_param_error',
    });
  }
  return new ValidationResult({ passed: true, message: '工具执行成功' });
}

function validateTests(code) {
  if (code.includes('memory_store.decay()')) {
    return new ValidationResult({ passed: true, message: '所有测试通过 (10/10)' });
  }
  if (code.includes('del self._sessions')) {
    return new ValidationResult({
      passed: false,
      message: '测试失败：test_memory_cleanup_on_session_end',
      evidence: 'AssertionError: assert 1 == 0; session 数据没有被 MemoryStore 清理',
      errorType: 'test_failure',
    });
  }
  return new ValidationResult({
    passed: false,
    message: '测试失败：代码无法解析',
    evidence: 'SyntaxError',
    errorType: 'test_failure',
  });
}

function validateCitation(text) {
  const refs = [...text.matchAll(/`(\w+\.\w+)\(\)`/g)].map(match => match[1]);
  for (const ref of refs) {
    const found = Object.values(mockNotes).some(note => note.includes(ref));
    if (!found) {
      return new ValidationResult({
        passed: false,
        message: `引用校验失败：${ref} 在笔记中未找到`,
        evidence: `搜索 notes，${ref} 0 匹配`,
        errorType: 'context_missing',
      });
    }
  }
  return new ValidationResult({ passed: true, message: '引用校验通过' });
}

function classifyError(validation) {
  return validation.errorType;
}

function reflectionLoop(action, validate, options = {}) {
  const maxRetries = options.maxRetries ?? 3;
  const costBudget = options.costBudget ?? 1.0;
  let cost = 0;
  let previousError = null;
  let previousSignature = null;
  const trace = [];

  for (let attempt = 0; attempt < maxRetries; attempt += 1) {
    const result = action(previousError, attempt);
    cost += result.cost;
    trace.push(`[尝试 ${attempt + 1}] 执行完成，成本 $${result.cost.toFixed(2)}`);

    const validation = validate(result.output);
    trace.push(`[尝试 ${attempt + 1}] 验证：${validation.passed ? '通过' : validation.message}`);
    if (validation.passed) {
      return { status: 'success', output: result.output, attempts: attempt + 1, cost, trace };
    }

    const errorType = classifyError(validation);
    const signature = `${errorType}:${validation.evidence}`;
    previousError = {
      type: errorType,
      message: validation.message,
      evidence: validation.evidence,
    };
    trace.push(`[尝试 ${attempt + 1}] 错误分类：${errorType}`);

    if (cost > costBudget) {
      trace.push(`[停止] 成本超限：$${cost.toFixed(2)} > $${costBudget.toFixed(2)}`);
      return { status: 'stopped', reason: 'cost_limit', output: result.output, attempts: attempt + 1, cost, trace };
    }
    if (previousSignature === signature) {
      trace.push('[停止] 相同错误重复出现，修正没有改变失败结果');
      return { status: 'stopped', reason: 'repeated_failure', output: result.output, attempts: attempt + 1, cost, trace };
    }
    previousSignature = signature;
  }

  return { status: 'stopped', reason: 'max_retries_exceeded', attempts: maxRetries, cost, trace };
}

function printResult(result) {
  for (const line of result.trace) console.log(`  ${line}`);
  console.log(`  => ${result.status}${result.reason ? ` (${result.reason})` : ''}, attempts=${result.attempts}, cost=$${result.cost.toFixed(2)}`);
}

async function wait(rl, auto) {
  if (!auto) await rl.question('\n  按 Enter 继续...');
}

async function demoV0(rl, auto) {
  console.log('\n--- V0 无反思：看到 TypeError 但继续执行 ---');
  await wait(rl, auto);
  console.log(`  npm test
  TypeError: Cannot read properties of undefined (reading 'files')
  Agent 把它记录成“测试完成（有警告）”，然后继续写 changelog。
  问题：失败信号没有触发停止、分类、修正和重试。`);
}

async function demoV1(rl, auto) {
  console.log('\n--- V1 格式修复：Schema 校验失败 -> 重生成 ---');
  await wait(rl, auto);
  const result = reflectionLoop(
    (previousError, attempt) => attempt === 0
      ? new ActionResult('{"tool": "search_notes", "query": "memory cleanup"}', 0.01)
      : new ActionResult('{"tool_name": "search_notes", "args": {"query": "memory cleanup"}, "reason": "查找 Memory 清理机制"}', 0.01),
    validateJsonSchema,
  );
  printResult(result);
}

async function demoV2(rl, auto) {
  console.log('\n--- V2 工具错误修正：参数错误 -> 分类 -> 修正参数 ---');
  await wait(rl, auto);
  const result = reflectionLoop(
    (previousError, attempt) => attempt === 0
      ? new ActionResult('search_notes(query="", limit=500)', 0.02)
      : new ActionResult('search_notes(query="memory cleanup decay", limit=20)', 0.02),
    validateToolCall,
  );
  printResult(result);
}

async function demoV3(rl, auto) {
  console.log('\n--- V3 测试驱动修正：测试失败 -> 修正代码 -> 重跑测试 ---');
  await wait(rl, auto);
  const result = reflectionLoop(
    (previousError, attempt) => new ActionResult(attempt === 0 ? buggyCleanupCode : correctCleanupCode, 0.03),
    validateTests,
  );
  printResult(result);
  console.log(result.output.trim().split('\n').map(line => `  ${line}`).join('\n'));
}

async function demoV4(rl, auto) {
  console.log('\n--- V4 引用校验：幻觉 API -> 补充检索 -> 可追溯引用 ---');
  await wait(rl, auto);
  const result = reflectionLoop(
    (previousError, attempt) => attempt === 0
      ? new ActionResult('问题来自 `memory.clear_expired()`，应该改成 `memory.remove_expired_sessions()`。', 0.02)
      : new ActionResult('问题来自 session cleanup 绕过 MemoryStore。笔记显示正确链路是 `MemoryStore.decay()` -> `_purge_old_records()`。', 0.02),
    validateCitation,
  );
  printResult(result);
}

async function demoStop(rl, auto) {
  console.log('\n--- 停止条件：相同错误重复出现 -> 硬停止 ---');
  await wait(rl, auto);
  const result = reflectionLoop(
    () => new ActionResult('{"tool": "search_notes"}', 0.01),
    validateJsonSchema,
  );
  printResult(result);
}

function printMenu() {
  console.log(`
Reflection 示例
  0 - V0 无反思
  1 - V1 格式修复
  2 - V2 工具错误修正
  3 - V3 测试驱动修正
  4 - V4 引用校验
  5 - 停止条件
  6 - 全部演示
  q - 退出`);
}

async function main() {
  const auto = process.argv.includes('--auto');
  const rl = readline.createInterface({ input, output });
  const demos = [demoV0, demoV1, demoV2, demoV3, demoV4, demoStop];

  if (auto) {
    for (const demo of demos) await demo(rl, true);
    rl.close();
    return;
  }

  printMenu();
  while (true) {
    const choice = (await rl.question('\n请选择演示：')).trim().toLowerCase();
    if (choice === 'q') break;
    if (choice === '6') {
      for (const demo of demos) await demo(rl, false);
    } else if (/^[0-5]$/.test(choice)) {
      await demos[Number(choice)](rl, false);
    } else {
      console.log('无效选项，请输入 0-6 或 q。');
    }
  }
  rl.close();
}

main();
