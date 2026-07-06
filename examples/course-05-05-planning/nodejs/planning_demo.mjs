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
  'Check README': {
    desc: 'Check README completeness - simulate file reading and content analysis',
    deps: [],
    run(fail = false) {
      if (fail) return { success: false, error: 'FileNotFoundError: README.md does not exist at the project root' };
      const required = ['Installation', 'Quick Start', 'API', 'Contributing'];
      const missing = required.filter(s => !MOCK_README.includes(s));
      if (missing.length) {
        return { success: true, output: `README exists but is missing sections: ${missing.join(', ')}. Recommendation: add the Contributing guide.` };
      }
      return { success: true, output: 'README is complete and contains all required sections.' };
    }
  },
  'Run tests': {
    desc: 'Run tests - simulate test execution',
    deps: [],
    run(fail = false) {
      if (fail) return { success: false, error: '1 tests failed: test_memory_cleanup_on_session_end', output: MOCK_TEST_FAILURE };
      return { success: true, output: '42 passed in 2.34s' };
    }
  },
  'Prepare changelog': {
    desc: 'Prepare changelog - simulate git log analysis and changelog generation',
    deps: ['Run tests'],
    run(fail = false) {
      if (fail) return { success: false, error: 'GitError: unable to get git log (not in a git repository)' };
      return { success: true, output: 'Changelog generated: v1.2.0 (2026-06-25) - Features: streaming output, retry mechanism / Fixes: memory leak, empty response' };
    }
  },
  'Generate checklist': {
    desc: 'Generate release checklist - simulate checklist generation',
    deps: ['Check README', 'Run tests', 'Prepare changelog'],
    run(fail = false) {
      if (fail) return { success: false, error: 'TemplateError: release template file is corrupted' };
      return { success: true, output: 'Release Checklist generated: README check | tests | Changelog | version number | API docs | release branch | pre-release validation' };
    }
  }
};

const DEFAULT_STEPS = ['Check README', 'Run tests', 'Prepare changelog', 'Generate checklist'];

// ═══════════════════════════════════════════════════════════════════════════
// Display helpers
// ═══════════════════════════════════════════════════════════════════════════

const CHECK = '✅';
const CROSS = '❌';
const GEAR = '⚙️';

function stepStart(name) {
  process.stdout.write(`  ${GEAR} Execute: ${name} ... `);
}

function stepEnd(result) {
  if (result.success) {
    console.log(`${CHECK} success`);
    if (result.output) console.log(`     ${result.output.slice(0, 80)}`);
  } else {
    console.log(`${CROSS} failed`);
    if (result.error) console.log(`     error: ${result.error}`);
  }
}

function summary(mode, status, steps, replans = 0) {
  console.log();
  console.log('─'.repeat(60));
  const icon = status === 'completed' ? CHECK : CROSS;
  console.log(`  ${icon} pattern: ${mode} | Status: ${status} | step count: ${steps}`);
  if (replans > 0) console.log(`     🔄 replan count: ${replans}`);
  console.log('─'.repeat(60));
}

function pressEnterToContinue(rl) {
  if (!process.stdin.isTTY) {
    console.log('  Non-interactive input: continuing automatically...');
    return Promise.resolve();
  }
  return new Promise(resolve => {
    rl.question('  Press Enter to continue...', () => resolve());
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
      results.push({ step: name, success: false, error: `Tool not found: ${name}` });
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
  release: ['Check README', 'Run tests', 'Prepare changelog', 'Generate checklist'],
  bugfix: ['Run tests', 'Prepare changelog'],
  docs: ['Check README'],
  feature: ['Run tests', 'Prepare changelog', 'Generate checklist'],
};

function classify(query) {
  const q = query.toLowerCase();
  if (/release|release|deploy|release/.test(q)) return 'release';
  if (/bug|fix|fix|defect|patch/.test(q)) return 'bugfix';
  if (/docs|doc|readme|instructions/.test(q)) return 'docs';
  if (/feature|feature|new feature|add/.test(q)) return 'feature';
  return 'release'; // Fallback
}

function executeRouter(query) {
  const category = classify(query);
  const steps = ROUTES[category] || ROUTES.release;
  console.log(`  Input: "${query}"`);
  console.log(`  classification: ${category} | path: ${steps.join(' → ')}`);
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

  if (/release|release/.test(goalLower)) {
    steps = [
      { name: 'Check README', tool: 'Check README', deps: [], desc: 'Check README completeness' },
      { name: 'Run tests', tool: 'Run tests', deps: [], desc: 'Run full test suite' },
      { name: 'Prepare changelog', tool: 'Prepare changelog', deps: ['Run tests'], desc: 'Generate changelog from git log' },
      { name: 'Generate checklist', tool: 'Generate checklist', deps: ['Check README', 'Run tests', 'Prepare changelog'], desc: 'Generate release checklist' },
    ];
  } else {
    steps = [
      { name: 'Check README', tool: 'Check README', deps: [], desc: 'check documentation completeness' },
      { name: 'Run tests', tool: 'Run tests', deps: [], desc: 'run tests for validation' },
    ];
  }

  return { goal, steps, completedSteps: [] };
}

function replan(goal, completedSteps, failedStep, error) {
  const newSteps = [];

  if (error.includes('FileNotFound') || error.includes('does not exist')) {
    newSteps.push({ name: `alternative (${failedStep})`, tool: 'Generate checklist', deps: [], desc: `because ${failedStep} failed，use alternative` });
  } else if (error.includes('test failed') || error.includes('AssertionError')) {
    newSteps.push({ name: `analysis ${failedStep} failure reason`, tool: 'Run tests', deps: [], desc: `rerun tests to confirm the failure reason: ${error}` });
    ['Prepare changelog', 'Generate checklist'].forEach(s => {
      if (!completedSteps.includes(s)) {
        newSteps.push({ name: s, tool: s, deps: [newSteps[0].name], desc: `continue execution: ${s}` });
      }
    });
  } else {
    ['Prepare changelog', 'Generate checklist'].forEach(s => {
      if (!completedSteps.includes(s) && s !== failedStep) {
        newSteps.push({ name: s, tool: s, deps: [], desc: `skip ${failedStep}，continue execution: ${s}` });
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
  console.log(`  Execution plan: ${plan.goal}`);
  console.log('  ' + '='.repeat(50));
  plan.steps.forEach((s, i) => {
    const deps = s.deps.length ? ` [dependencies: ${s.deps.join(', ')}]` : '';
    console.log(`    step ${i + 1}. ${s.name}${deps}`);
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
          plan.steps.splice(i, 0, { name: depName, tool: depName, deps: [], desc: `dependency step: ${depName}`, retries: 0, maxRetries });
        }
      });
      continue;
    }

    stepStart(step.name);
    const tool = TOOLS[step.tool];
    if (!tool) {
      const r = { step: step.name, success: false, error: `Tool not found: ${step.tool}` };
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
          error: `reached maximum replan count ${maxReplanCount}，stopped at step '${step.name}'`,
        };
      }

      const newSteps = replan(plan.goal, plan.completedSteps, step.name, result.error);
      replanCount++;
      console.log(`\n  🔄 replan！failed step: ${step.name}`);
      console.log(`     new steps (${newSteps.length} items):`);
      newSteps.forEach(s => console.log(`       - ${s.name}: ${s.desc}`));

      if (newSteps.length === 0) {
        return { status: 'failed', results, replanCount, error: `step '${step.name}' failed and cannot be replanned` };
      }

      const signature = newSteps.map(s => s.name).join('|');
      if (seenReplans.has(signature)) {
        return { status: 'failed', results, replanCount, error: 'replan generated duplicate steps; stopping to avoid a loop' };
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
      if (!tool) return { success: false, error: `Tool not found: ${stepName}` };
      return tool.run(injectFailures[stepName] || false);
    };
  }

  nodes['check_readme'] = {
    action: makeAction('Check README'),
    onSuccess: 'run_tests',
    onError: 'fix_readme',
    desc: 'Check README completeness',
  };

  nodes['fix_readme'] = {
    action: () => ({ success: true, output: 'Missing README content has been added.' }),
    onSuccess: null,
    onError: null,
    desc: 'Try to automatically fix missing README sections',
  };

  nodes['run_tests'] = {
    action: makeAction('Run tests'),
    onSuccess: 'changelog',
    onError: 'retry_tests',
    maxRetries: 2,
    desc: 'Run full test suite',
  };

  nodes['retry_tests'] = {
    action: () => ({ success: true, output: 'Tests passed after retry (possibly an environment fluctuation)' }),
    onSuccess: 'changelog',
    onError: null,
    desc: 'retry tests',
  };

  nodes['changelog'] = {
    action: makeAction('Prepare changelog'),
    onSuccess: 'checklist',
    onError: null,
    desc: 'Generate changelog from git log',
  };

  nodes['checklist'] = {
    action: makeAction('Generate checklist'),
    onSuccess: null,
    onError: null,
    desc: 'Generate release checklist',
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
      return { status: 'failed', path, error: `node '${current}' does not exist` };
    }

    // Loop detection
    visitCount[current] = (visitCount[current] || 0) + 1;
    const maxVisits = (node.maxRetries || 1) + 1;
    if (visitCount[current] > maxVisits) {
      return { status: 'failed', path, error: `loop detected: node '${current}' was visited ${visitCount[current]} times` };
    }

    path.push(current);
    console.log(`  ${GEAR} node [${current}] started...`);

    node.retryCount = node.retryCount || 0;
    const result = typeof node.action === 'function' ? node.action(ctx) : { success: false, error: 'action is not a function' };
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
    console.log(`     ${icon} complete -> next node: ${nextNode || '(stop)'}`);

    if (nextNode === current && node.retryCount >= (node.maxRetries || 1)) {
      return { status: 'failed', path, error: `node '${current}' retry ${node.retryCount} timesafter stillfailed` };
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
  console.log('  Pattern 1: Chain — fixed-order execution');
  console.log('━'.repeat(60));
  console.log();
  console.log('  Chain is the simplest pattern: steps run in a predefined order and stop on error.');
  console.log();

  await pressEnterToContinue(rl);
  console.log();

  const result = executeChain(DEFAULT_STEPS);
  summary('Chain', result.status, result.results.length);
}

async function demoChainFailure(rl) {
  console.log();
  console.log('━'.repeat(60));
  console.log('  Pattern 1b: Chain — when failure occurs');
  console.log('━'.repeat(60));
  console.log();
  console.log("  Chain's fatal weakness: when one middle step fails, all later steps are skipped.");
  console.log();

  await pressEnterToContinue(rl);
  console.log();

  const result = executeChain(DEFAULT_STEPS, { 'Run tests': true });
  if (result.status === 'failed') {
    console.log();
    console.log(`  ${CROSS} Chain mode: rank ${result.failedAt + 1}  step failed; stopping execution.`);
    console.log(`     later ${DEFAULT_STEPS.length - result.failedAt - 1} steps skipped`);
    console.log();
    console.log('  💡 This is why Plan-Execute and Graph are needed -');
    console.log('     they can retry, skip, or replan after failure.');
  }
}

async function demoRouter(rl) {
  console.log();
  console.log('━'.repeat(60));
  console.log('  Pattern 2: Router — choose path by input classification');
  console.log('━'.repeat(60));
  console.log();
  console.log('  Router is essentially a classifier plus multiple Chains.');

  const queries = [
    'Help me prepare the v1.2.0 release',
    'Fix the session pool memory leak bug',
    'Update README documentation instructions',
  ];

  for (const q of queries) {
    const c = classify(q);
    const steps = ROUTES[c];
    console.log(`  Input: "${q}"`);
    console.log(`  → classification: ${c} | path: ${steps.join(' → ')}`);
    console.log();
  }

  await pressEnterToContinue(rl);
  console.log();

  const result = executeRouter('Help me prepare the v1.2.0 release');
  summary(`Router (classification: ${result.category})`, result.status, result.results.length);
}

async function demoPlanExecute(rl) {
  console.log();
  console.log('━'.repeat(60));
  console.log('  Pattern 3: Plan-Execute — generate plan -> execute -> replan');
  console.log('━'.repeat(60));
  console.log();
  console.log('  Plan-Execute is the classic implementation of Planning.');

  await pressEnterToContinue(rl);

  const result = executePlanExecute('Prepare the v1.2.0 release');
  summary('Plan-Execute', result.status, result.results.length, result.replanCount);
}

async function demoPlanExecuteFailure(rl) {
  console.log();
  console.log('━'.repeat(60));
  console.log('  Pattern 3b: Plan-Execute — failed → replan');
  console.log('━'.repeat(60));
  console.log();
  console.log('  Inject a Run tests failure below and observe replanning behavior.');

  await pressEnterToContinue(rl);
  console.log();

  const result = executePlanExecute('Prepare the v1.2.0 release', { 'Run tests': true });
  summary('Plan-Execute (with replan)', result.status, result.results.length, result.replanCount);

  if (result.replanCount > 0) {
    console.log();
    console.log('  💡 Note: Plan-Execute automatically generates alternative steps after failure.');
    console.log('     This is something Chain cannot do——Chain stops on error.');
  }
}

async function demoGraph(rl) {
  console.log();
  console.log('━'.repeat(60));
  console.log('  Pattern 4: Graph — node + conditional edge + state machine');
  console.log('━'.repeat(60));
  console.log();
  console.log('  Graph generalizes Plan-Execute: the task is modeled as a directed graph.');

  await pressEnterToContinue(rl);
  console.log();

  const graph = buildReleaseGraph();
  const result = runGraph(graph);

  console.log();
  console.log('─'.repeat(60));
  console.log(`  Execution path: ${result.path.join(' → ')}`);
  summary('Graph', result.status, result.path.length);

  console.log();
  console.log('  💡 Key advantages of Graph：');
  console.log('     - each node can configure an independent failure branch（onError)');
  console.log('     - supports node-level retry（the test node configures maxRetries=2)');
  console.log('     - can be replayed and debugged precisely（execution path is deterministic)');
  console.log('     - modeling cost is high——introduce it only when state and branches are truly complex');
}

async function demoGraphFailure(rl) {
  console.log();
  console.log('━'.repeat(60));
  console.log('  Pattern 4b: Graph — failure-branch transition');
  console.log('━'.repeat(60));
  console.log();
  console.log('  Inject a Check README failure below and observe how it jumps to the fix node.');

  await pressEnterToContinue(rl);
  console.log();

  const graph = buildReleaseGraph({ 'Check README': true });
  const result = runGraph(graph);

  console.log();
  console.log('─'.repeat(60));
  console.log(`  Execution path: ${result.path.join(' → ')}`);
  summary('Graph (with failure branch)', result.status, result.path.length);

  console.log();
  console.log('  💡 Note：After README check fails, Graph automatically jumps to the Fix README node.');
  console.log('     This is something Chain cannot do——Chain has a fixed step order.');
}

async function demoCompare() {
  console.log();
  console.log('━'.repeat(60));
  console.log('  Summary comparison of four patterns');
  console.log('━'.repeat(60));
  console.log();

  const rows = [
    ['Dimension', 'Chain', 'Router', 'Plan-Execute', 'Graph'],
    ['Decision style', 'fixed order', 'classifier decides', 'plan + replan', 'conditional-edge transition'],
    ['Flexibility', 'lowest', 'medium (path selectable)', 'high (dynamic planning)', 'highest (arbitrary transitions)'],
    ['failure handling', 'stop on error', 'stop on error', 'retry+replan', 'jump to error node'],
    ['user confirmation', 'none', 'none', 'supported', 'node-level confirmation'],
    ['Debug difficulty', 'low', 'low', 'medium', 'high'],
    ['Modelingcost', 'low', 'low', 'medium', 'high'],
    ['Use case', 'stepfixed', 'multi-type entry', 'mediumtext', 'complexStatustext'],
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
  console.log('  💡 Selection guide:');
  console.log('     stepfully fixed → Chain');
  console.log('     multi-type entry   → Router');
  console.log('     needs global planning   → Plan-Execute');
  console.log('     complexStatustext   → Graph');
}

// ═══════════════════════════════════════════════════════════════════════════
// REPL main menu
// ═══════════════════════════════════════════════════════════════════════════

async function main() {
  console.log();
  console.log('='.repeat(60));
  console.log('  Planning / Workflow Patterns — releasetext');
  console.log('='.repeat(60));
  console.log();
  console.log('  Scenario：your Agent needscompletesoftwarereleasetext');
  console.log('  Task：Check README → Run tests → Prepare changelog → Generate checklist');
  console.log();

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  const question = (q) => new Promise(resolve => rl.question(q, resolve));

  const menuItems = [
    ['1', 'Chain normal execution', demoChain],
    ['1b', 'Chain encountersfailed', demoChainFailure],
    ['2', 'Router classificationroute', demoRouter],
    ['3', 'Plan-Execute normal execution', demoPlanExecute],
    ['3b', 'Plan-Execute failed→replan', demoPlanExecuteFailure],
    ['4', 'Graph normal execution', demoGraph],
    ['4b', 'Graph failure-branch transition', demoGraphFailure],
    ['5', 'Summary comparison of four patterns', async () => { await demoCompare(); }],
    ['0', 'Exit', null],
  ];

  while (true) {
    console.log();
    console.log('='.repeat(60));
    console.log('  Choose demo:');
    menuItems.forEach(([key, desc]) => {
      console.log(`  [${key}] ${desc}`);
    });
    console.log('='.repeat(60));

    const choice = (await question('  pleaseInputchoose > ')).trim();

    if (choice === '0') {
      console.log('\n  Goodbye!\n');
      break;
    }

    const item = menuItems.find(([key]) => key === choice);
    if (item && item[2]) {
      await item[2](rl);
    } else {
      console.log(`\n  ${CROSS} nonetext: ${choice}`);
    }
  }

  rl.close();
}

main().catch(console.error);
