/**
 * Course 05-05 Planning / Workflow Patterns example (Node.js)
 *
 * Demonstrates four Planning patterns for a "release preparation" task:
 *   - Chain: fixed-order execution
 *   - Router: route by input classification
 *   - Plan-Execute: generate a plan, execute, and replan
 *   - Graph: node graph, conditional transitions, and failure branches
 *
 * Usage:
 *   node planning_demo.mjs
 */

import * as readline from 'node:readline';
import { setTimeout as sleep } from 'node:timers/promises';

// ═══════════════════════════════════════════════════════════════════════════
// Mock tool set
// ═══════════════════════════════════════════════════════════════════════════

const MOCK_README = `# MyAgent

A lightweight Agent framework.

## Installation
\`\`\`bash
pip install myagent
\`\`\`

## Quick Start
\`\`\`python
from myagent import Agent
agent = Agent()
agent.run("Hello")
\`\`\`

## API
See docs/api.md for details.
`;

const MOCK_TEST_FAILURE = `______________________ test_memory_cleanup_on_session_end ______________________
    def test_memory_cleanup_on_session_end():
        mem = MemoryStore()
        mem.start_session("test")
        mem.write({"key": "value"})
        mem.end_session()
>       assert len(mem._store) == 0
E       AssertionError: assert 1 == 0
tests/test_memory.js:28: AssertionError
========================= 1 failed, 41 passed =========================`;

const TOOLS = {
  '检查 README': {
    desc: '检查 README 完整性——模拟文件读取和内容分析',
    deps: [],
    run(fail = false) {
      if (fail) return { success: false, error: 'FileNotFoundError: README.md 不存在于项目根目录' };
      const required = ['Installation', 'Quick Start', 'API', 'Contributing'];
      const missing = required.filter(s => !MOCK_README.includes(s));
      if (missing.length) {
        return { success: true, output: `README 存在但缺少章节: ${missing.join(', ')}。建议补充 Contributing 指南。` };
      }
      return { success: true, output: 'README 完整，包含所有必要章节。' };
    }
  },
  '运行测试': {
    desc: '运行测试——模拟测试执行',
    deps: [],
    run(fail = false) {
      if (fail) return { success: false, error: '1 个测试失败: test_memory_cleanup_on_session_end', output: MOCK_TEST_FAILURE };
      return { success: true, output: '42 passed in 2.34s' };
    }
  },
  '整理 changelog': {
    desc: '整理 changelog——模拟 git log 分析和 changelog 生成',
    deps: ['运行测试'],
    run(fail = false) {
      if (fail) return { success: false, error: 'GitError: 无法获取 git log（不在 git 仓库中）' };
      return { success: true, output: 'Changelog 已生成: v1.2.0 (2026-06-25) - Features: 流式输出, 重试机制 / Fixes: 内存泄漏, 空响应' };
    }
  },
  '生成 checklist': {
    desc: '生成发布 checklist——模拟清单生成',
    deps: ['检查 README', '运行测试', '整理 changelog'],
    run(fail = false) {
      if (fail) return { success: false, error: 'TemplateError: release 模板文件损坏' };
      return { success: true, output: 'Release Checklist 已生成: README ✓ | 测试 ✓ | Changelog ✓ | 版本号 | API 文档 | 发布分支 | 预发布验证' };
    }
  }
};

const DEFAULT_STEPS = ['检查 README', '运行测试', '整理 changelog', '生成 checklist'];

// ═══════════════════════════════════════════════════════════════════════════
// Display helpers
// ═══════════════════════════════════════════════════════════════════════════

const CHECK = '✅';
const CROSS = '❌';
const GEAR = '⚙️';

function stepStart(name) {
  process.stdout.write(`  ${GEAR} 执行: ${name} ... `);
}

function stepEnd(result) {
  if (result.success) {
    console.log(`${CHECK} 成功`);
    if (result.output) console.log(`     ${result.output.slice(0, 80)}`);
  } else {
    console.log(`${CROSS} 失败`);
    if (result.error) console.log(`     错误: ${result.error}`);
  }
}

function summary(mode, status, steps, replans = 0) {
  console.log();
  console.log('─'.repeat(60));
  const icon = status === 'completed' ? CHECK : CROSS;
  console.log(`  ${icon} 模式: ${mode} | 状态: ${status} | 步骤数: ${steps}`);
  if (replans > 0) console.log(`     🔄 重规划次数: ${replans}`);
  console.log('─'.repeat(60));
}

function pressEnterToContinue(rl) {
  if (!process.stdin.isTTY) {
    console.log('  非交互输入：自动继续...');
    return Promise.resolve();
  }
  return new Promise(resolve => {
    rl.question('  按 Enter 继续...', () => resolve());
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Pattern 1: Chain
// ═══════════════════════════════════════════════════════════════════════════

function executeChain(steps, injectFailures = {}) {
  const results = [];
  for (let i = 0; i < steps.length; i++) {
    const name = steps[i];
    const tool = TOOLS[name];
    if (!tool) {
      results.push({ step: name, success: false, error: `未找到工具: ${name}` });
      return { status: 'failed', results, failedAt: i };
    }
    stepStart(name);
    const result = tool.run(injectFailures[name] || false);
    results.push({ step: name, ...result });
    stepEnd(result);
    if (!result.success) {
      return { status: 'failed', results, failedAt: i, error: result.error };
    }
  }
  return { status: 'completed', results };
}

// ═══════════════════════════════════════════════════════════════════════════
// Pattern 2: Router
// ═══════════════════════════════════════════════════════════════════════════

const ROUTES = {
  release: ['检查 README', '运行测试', '整理 changelog', '生成 checklist'],
  bugfix: ['运行测试', '整理 changelog'],
  docs: ['检查 README'],
  feature: ['运行测试', '整理 changelog', '生成 checklist'],
};

function classify(query) {
  const q = query.toLowerCase();
  if (/发布|release|上线|发版/.test(q)) return 'release';
  if (/bug|修复|fix|缺陷|补丁/.test(q)) return 'bugfix';
  if (/文档|doc|readme|说明/.test(q)) return 'docs';
  if (/功能|feature|新功能|新增/.test(q)) return 'feature';
  return 'release'; // Fallback
}

function executeRouter(query) {
  const category = classify(query);
  const steps = ROUTES[category] || ROUTES.release;
  console.log(`  输入: "${query}"`);
  console.log(`  分类: ${category} | 路径: ${steps.join(' → ')}`);
  console.log();
  const chainResult = executeChain(steps);
  return { ...chainResult, category };
}

// ═══════════════════════════════════════════════════════════════════════════
// Pattern 3: Plan-Execute
// ═══════════════════════════════════════════════════════════════════════════

function generatePlan(goal) {
  const goalLower = goal.toLowerCase();
  let steps;

  if (/发布|release/.test(goalLower)) {
    steps = [
      { name: '检查 README', tool: '检查 README', deps: [], desc: '检查 README 完整性' },
      { name: '运行测试', tool: '运行测试', deps: [], desc: '运行全量测试套件' },
      { name: '整理 changelog', tool: '整理 changelog', deps: ['运行测试'], desc: '基于 git log 生成 changelog' },
      { name: '生成 checklist', tool: '生成 checklist', deps: ['检查 README', '运行测试', '整理 changelog'], desc: '生成发布 checklist' },
    ];
  } else {
    steps = [
      { name: '检查 README', tool: '检查 README', deps: [], desc: '检查文档完整性' },
      { name: '运行测试', tool: '运行测试', deps: [], desc: '运行测试验证' },
    ];
  }

  return { goal, steps, completedSteps: [] };
}

function replan(goal, completedSteps, failedStep, error) {
  const newSteps = [];

  if (error.includes('FileNotFound') || error.includes('不存在')) {
    newSteps.push({ name: `替代方案（${failedStep}）`, tool: '生成 checklist', deps: [], desc: `由于 ${failedStep} 失败，使用替代方案` });
  } else if (error.includes('测试失败') || error.includes('AssertionError')) {
    newSteps.push({ name: `分析 ${failedStep} 失败原因`, tool: '运行测试', deps: [], desc: `重新运行测试以确认失败原因: ${error}` });
    ['整理 changelog', '生成 checklist'].forEach(s => {
      if (!completedSteps.includes(s)) {
        newSteps.push({ name: s, tool: s, deps: [newSteps[0].name], desc: `继续执行: ${s}` });
      }
    });
  } else {
    ['整理 changelog', '生成 checklist'].forEach(s => {
      if (!completedSteps.includes(s) && s !== failedStep) {
        newSteps.push({ name: s, tool: s, deps: [], desc: `跳过 ${failedStep}，继续执行: ${s}` });
      }
    });
  }

  return newSteps;
}

function executePlanExecute(goal, injectFailures = {}, maxRetries = 2, maxReplanCount = 2) {
  const plan = generatePlan(goal);
  const results = [];
  const ctx = {};
  let replanCount = 0;
  const seenReplans = new Set();

  console.log();
  console.log(`  执行计划: ${plan.goal}`);
  console.log('  ' + '='.repeat(50));
  plan.steps.forEach((s, i) => {
    const deps = s.deps.length ? ` [依赖: ${s.deps.join(', ')}]` : '';
    console.log(`    步骤 ${i + 1}. ${s.name}${deps}`);
    console.log(`       ${s.desc}`);
  });
  console.log();

  let i = 0;
  while (i < plan.steps.length) {
    const step = plan.steps[i];

    // Check dependencies
    const unmet = step.deps.filter(d => !plan.completedSteps.includes(d));
    if (unmet.length > 0) {
      unmet.forEach(depName => {
        if (!plan.steps.slice(0, i).find(s => s.name === depName)) {
          plan.steps.splice(i, 0, { name: depName, tool: depName, deps: [], desc: `依赖步骤: ${depName}`, retries: 0, maxRetries });
        }
      });
      continue;
    }

    stepStart(step.name);
    const tool = TOOLS[step.tool];
    if (!tool) {
      const r = { step: step.name, success: false, error: `未找到工具: ${step.tool}` };
      results.push(r);
      stepEnd(r);
      return { status: 'failed', results, replanCount, error: r.error };
    }

    const result = tool.run(injectFailures[step.name] || false);
    const stepResult = { step: step.name, ...result };
    results.push(stepResult);
    stepEnd(stepResult);
    ctx[step.name] = result.output || '';

    if (!result.success) {
      step.retries = (step.retries || 0) + 1;
      if (step.retries < (step.maxRetries || maxRetries)) {
        continue; // Retry
      }

      // Replan
      if (replanCount >= maxReplanCount) {
        return {
          status: 'failed',
          results,
          replanCount,
          error: `达到最大重规划次数 ${maxReplanCount}，停止在步骤 '${step.name}'`,
        };
      }

      const newSteps = replan(plan.goal, plan.completedSteps, step.name, result.error);
      replanCount++;
      console.log(`\n  🔄 重规划！失败步骤: ${step.name}`);
      console.log(`     新步骤 (${newSteps.length} 个):`);
      newSteps.forEach(s => console.log(`       - ${s.name}: ${s.desc}`));

      if (newSteps.length === 0) {
        return { status: 'failed', results, replanCount, error: `步骤 '${step.name}' 失败且无法重规划` };
      }

      const signature = newSteps.map(s => s.name).join('|');
      if (seenReplans.has(signature)) {
        return { status: 'failed', results, replanCount, error: '重规划生成了重复步骤，停止以避免循环' };
      }
      seenReplans.add(signature);

      plan.steps = [...plan.steps.slice(0, i), ...newSteps];
      continue;
    }

    plan.completedSteps.push(step.name);
    i++;
  }

  return { status: 'completed', results, replanCount, context: ctx };
}

// ═══════════════════════════════════════════════════════════════════════════
// Pattern 4: Graph
// ═══════════════════════════════════════════════════════════════════════════

function buildReleaseGraph(injectFailures = {}) {
  const nodes = {};

  function makeAction(stepName) {
    return (ctx) => {
      const tool = TOOLS[stepName];
      if (!tool) return { success: false, error: `未找到工具: ${stepName}` };
      return tool.run(injectFailures[stepName] || false);
    };
  }

  nodes['check_readme'] = {
    action: makeAction('检查 README'),
    onSuccess: 'run_tests',
    onError: 'fix_readme',
    desc: '检查 README 完整性',
  };

  nodes['fix_readme'] = {
    action: () => ({ success: true, output: 'README 缺失内容已补充。' }),
    onSuccess: null,
    onError: null,
    desc: '尝试自动修复 README 缺失章节',
  };

  nodes['run_tests'] = {
    action: makeAction('运行测试'),
    onSuccess: 'changelog',
    onError: 'retry_tests',
    maxRetries: 2,
    desc: '运行全量测试套件',
  };

  nodes['retry_tests'] = {
    action: () => ({ success: true, output: '重试后测试通过（可能是环境波动）' }),
    onSuccess: 'changelog',
    onError: null,
    desc: '重试测试',
  };

  nodes['changelog'] = {
    action: makeAction('整理 changelog'),
    onSuccess: 'checklist',
    onError: null,
    desc: '基于 git log 生成 changelog',
  };

  nodes['checklist'] = {
    action: makeAction('生成 checklist'),
    onSuccess: null,
    onError: null,
    desc: '生成发布 checklist',
  };

  return { nodes, entry: 'check_readme' };
}

function runGraph(graph) {
  const path = [];
  const results = {};
  const ctx = {};
  const visitCount = {};

  let current = graph.entry;

  while (current) {
    const node = graph.nodes[current];
    if (!node) {
      return { status: 'failed', path, error: `节点 '${current}' 不存在` };
    }

    // Loop detection
    visitCount[current] = (visitCount[current] || 0) + 1;
    const maxVisits = (node.maxRetries || 1) + 1;
    if (visitCount[current] > maxVisits) {
      return { status: 'failed', path, error: `检测到环路: 节点 '${current}' 被访问 ${visitCount[current]} 次` };
    }

    path.push(current);
    console.log(`  ${GEAR} 节点 [${current}] 开始...`);

    node.retryCount = node.retryCount || 0;
    const result = typeof node.action === 'function' ? node.action(ctx) : { success: false, error: 'action 不是函数' };
    results[current] = { step: current, ...result };
    ctx[current] = result.output || '';

    let nextNode;
    if (!result.success) {
      node.retryCount++;
      if (node.retryCount < (node.maxRetries || 1)) {
        nextNode = current; // Retry
      } else {
        nextNode = node.onError;
      }
    } else {
      nextNode = node.onSuccess;
      node.retryCount = 0;
    }

    const icon = result.success ? CHECK : CROSS;
    console.log(`     ${icon} 完成 → 下一节点: ${nextNode || '（终止）'}`);

    if (nextNode === current && node.retryCount >= (node.maxRetries || 1)) {
      return { status: 'failed', path, error: `节点 '${current}' 重试 ${node.retryCount} 次后仍然失败` };
    }

    current = nextNode;
  }

  return { status: 'completed', path, results };
}

// ═══════════════════════════════════════════════════════════════════════════
// Demo functions
// ═══════════════════════════════════════════════════════════════════════════

async function demoChain(rl) {
  console.log();
  console.log('━'.repeat(60));
  console.log('  模式 1: Chain — 固定顺序执行');
  console.log('━'.repeat(60));
  console.log();
  console.log('  Chain 是最简单的模式：步骤按预定顺序执行，遇错即停。');
  console.log();

  await pressEnterToContinue(rl);
  console.log();

  const result = executeChain(DEFAULT_STEPS);
  summary('Chain', result.status, result.results.length);
}

async function demoChainFailure(rl) {
  console.log();
  console.log('━'.repeat(60));
  console.log('  模式 1b: Chain — 遇到失败时');
  console.log('━'.repeat(60));
  console.log();
  console.log('  Chain 的致命弱点：中途某步失败后，后续步骤全部跳过。');
  console.log();

  await pressEnterToContinue(rl);
  console.log();

  const result = executeChain(DEFAULT_STEPS, { '运行测试': true });
  if (result.status === 'failed') {
    console.log();
    console.log(`  ${CROSS} Chain 模式: 第 ${result.failedAt + 1} 步失败，停止执行。`);
    console.log(`     后续 ${DEFAULT_STEPS.length - result.failedAt - 1} 个步骤被跳过`);
    console.log();
    console.log('  💡 这就是为什么需要 Plan-Execute 和 Graph——');
    console.log('     它们可以在失败后重试、跳过或重规划。');
  }
}

async function demoRouter(rl) {
  console.log();
  console.log('━'.repeat(60));
  console.log('  模式 2: Router — 根据输入分类选择路径');
  console.log('━'.repeat(60));
  console.log();
  console.log('  Router 本质是"分类器 + 多条 Chain"。');

  const queries = [
    '帮我做 v1.2.0 发布准备',
    '修复 session pool 内存泄漏 bug',
    '更新 README 文档说明',
  ];

  for (const q of queries) {
    const c = classify(q);
    const steps = ROUTES[c];
    console.log(`  输入: "${q}"`);
    console.log(`  → 分类: ${c} | 路径: ${steps.join(' → ')}`);
    console.log();
  }

  await pressEnterToContinue(rl);
  console.log();

  const result = executeRouter('帮我做 v1.2.0 发布准备');
  summary(`Router (分类: ${result.category})`, result.status, result.results.length);
}

async function demoPlanExecute(rl) {
  console.log();
  console.log('━'.repeat(60));
  console.log('  模式 3: Plan-Execute — 生成计划 → 执行 → 重规划');
  console.log('━'.repeat(60));
  console.log();
  console.log('  Plan-Execute 是 Planning 最经典的实现。');

  await pressEnterToContinue(rl);

  const result = executePlanExecute('准备 v1.2.0 版本发布');
  summary('Plan-Execute', result.status, result.results.length, result.replanCount);
}

async function demoPlanExecuteFailure(rl) {
  console.log();
  console.log('━'.repeat(60));
  console.log('  模式 3b: Plan-Execute — 失败 → 重规划');
  console.log('━'.repeat(60));
  console.log();
  console.log('  下面注入"运行测试"失败，观察重规划行为。');

  await pressEnterToContinue(rl);
  console.log();

  const result = executePlanExecute('准备 v1.2.0 版本发布', { '运行测试': true });
  summary('Plan-Execute (with replan)', result.status, result.results.length, result.replanCount);

  if (result.replanCount > 0) {
    console.log();
    console.log('  💡 注意：Plan-Execute 在失败后自动生成了替代步骤。');
    console.log('     这是 Chain 做不到的——Chain 遇错即停。');
  }
}

async function demoGraph(rl) {
  console.log();
  console.log('━'.repeat(60));
  console.log('  模式 4: Graph — 节点 + 条件边 + 状态机');
  console.log('━'.repeat(60));
  console.log();
  console.log('  Graph 是 Plan-Execute 的泛化：任务建模为有向图。');

  await pressEnterToContinue(rl);
  console.log();

  const graph = buildReleaseGraph();
  const result = runGraph(graph);

  console.log();
  console.log('─'.repeat(60));
  console.log(`  执行路径: ${result.path.join(' → ')}`);
  summary('Graph', result.status, result.path.length);

  console.log();
  console.log('  💡 Graph 的关键优势：');
  console.log('     - 每个节点可配置独立的失败分支（onError）');
  console.log('     - 支持节点级重试（测试节点配置了 maxRetries=2）');
  console.log('     - 可精确回放和调试（执行路径是确定的）');
  console.log('     - 建模成本高——只在状态和分支真的复杂时才引入');
}

async function demoGraphFailure(rl) {
  console.log();
  console.log('━'.repeat(60));
  console.log('  模式 4b: Graph — 失败分支跳转');
  console.log('━'.repeat(60));
  console.log();
  console.log('  下面注入"检查 README"失败，观察它如何跳转到修复节点。');

  await pressEnterToContinue(rl);
  console.log();

  const graph = buildReleaseGraph({ '检查 README': true });
  const result = runGraph(graph);

  console.log();
  console.log('─'.repeat(60));
  console.log(`  执行路径: ${result.path.join(' → ')}`);
  summary('Graph (with failure branch)', result.status, result.path.length);

  console.log();
  console.log('  💡 注意：README 检查失败后，Graph 自动跳转到"修复 README"节点。');
  console.log('     这是 Chain 做不到的——Chain 的步骤顺序是固定的。');
}

async function demoCompare() {
  console.log();
  console.log('━'.repeat(60));
  console.log('  四种模式对比总结');
  console.log('━'.repeat(60));
  console.log();

  const rows = [
    ['维度', 'Chain', 'Router', 'Plan-Execute', 'Graph'],
    ['决策方式', '固定顺序', '分类器决定', '计划+重规划', '条件边跳转'],
    ['灵活性', '最低', '中（路径可选）', '高（动态规划）', '最高（任意跳转）'],
    ['失败处理', '遇错即停', '遇错即停', '重试+重规划', '跳转到错误节点'],
    ['用户确认', '无', '无', '支持', '节点级确认'],
    ['调试难度', '低', '低', '中', '高'],
    ['建模成本', '低', '低', '中', '高'],
    ['适用场景', '步骤固定', '多类型入口', '中长任务', '复杂状态机'],
  ];

  const widths = [14, 16, 18, 18, 18];
  rows.forEach(row => {
    let line = '  ';
    row.forEach((cell, i) => {
      line += cell.padEnd(widths[i]);
    });
    console.log(line);
  });

  console.log();
  console.log('  💡 选择指南:');
  console.log('     步骤完全固定 → Chain');
  console.log('     多类型入口   → Router');
  console.log('     需全局规划   → Plan-Execute');
  console.log('     复杂状态机   → Graph');
}

// ═══════════════════════════════════════════════════════════════════════════
// REPL main menu
// ═══════════════════════════════════════════════════════════════════════════

async function main() {
  console.log();
  console.log('='.repeat(60));
  console.log('  Planning / Workflow Patterns — 发布助手示例');
  console.log('='.repeat(60));
  console.log();
  console.log('  场景：你的 Agent 需要完成软件发布准备工作');
  console.log('  任务：检查 README → 运行测试 → 整理 changelog → 生成 checklist');
  console.log();

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  const question = (q) => new Promise(resolve => rl.question(q, resolve));

  const menuItems = [
    ['1', 'Chain 正常执行', demoChain],
    ['1b', 'Chain 遇到失败', demoChainFailure],
    ['2', 'Router 分类路由', demoRouter],
    ['3', 'Plan-Execute 正常执行', demoPlanExecute],
    ['3b', 'Plan-Execute 失败→重规划', demoPlanExecuteFailure],
    ['4', 'Graph 正常执行', demoGraph],
    ['4b', 'Graph 失败分支跳转', demoGraphFailure],
    ['5', '四种模式对比总结', async () => { await demoCompare(); }],
    ['0', '退出', null],
  ];

  while (true) {
    console.log();
    console.log('='.repeat(60));
    console.log('  选择演示:');
    menuItems.forEach(([key, desc]) => {
      console.log(`  [${key}] ${desc}`);
    });
    console.log('='.repeat(60));

    const choice = (await question('  请输入选择 > ')).trim();

    if (choice === '0') {
      console.log('\n  再见！\n');
      break;
    }

    const item = menuItems.find(([key]) => key === choice);
    if (item && item[2]) {
      await item[2](rl);
    } else {
      console.log(`\n  ${CROSS} 无效选择: ${choice}`);
    }
  }

  rl.close();
}

main().catch(console.error);
