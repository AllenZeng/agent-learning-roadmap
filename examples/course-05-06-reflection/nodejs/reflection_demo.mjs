#!/usr/bin/env node
/**
 * Course 05-06 Reflection example (Node.js)
 *
 * Demonstrates a decision loop triggered by external feedback signals:
 * trigger -> classify -> decide -> handle -> verify or stop.
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
Memory text session data is managed by MemoryStore managed。
expired session data is managed by MemoryStore.decay() Inevery time start_session text，text _purge_old_records()。
Note：Memory text clear_expired() method。
`,
  'session-manager.md': `
text：
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
      message: `Schema textfailed：Missingtext ${missing.join(', ')}`,
      evidence: `missing=${missing.join(',')}`,
      errorType: 'schema_error',
    });
  }
  return new ValidationResult({ passed: true, message: 'Schema validation passed' });
}

function validateToolCall(text) {
  if (text.includes('limit=500')) {
    return new ValidationResult({
      passed: false,
      message: 'wrong argument：limit must be between 1-100 and',
      evidence: 'tool returned: Error: limit must be 1-100 (got 500)',
      errorType: 'tool_param_error',
    });
  }
  if (text.includes('query=""')) {
    return new ValidationResult({
      passed: false,
      message: 'wrong argument：query cannot be empty',
      evidence: 'tool returned: Error: query parameter is required',
      errorType: 'tool_param_error',
    });
  }
  return new ValidationResult({ passed: true, message: 'textsuccess' });
}

function validateTests(code) {
  if (code.includes('memory_store.decay()')) {
    return new ValidationResult({ passed: true, message: 'All tests passed (10/10)' });
  }
  if (code.includes('del self._sessions')) {
    return new ValidationResult({
      passed: false,
      message: 'test failed：test_memory_cleanup_on_session_end',
      evidence: 'AssertionError: assert 1 == 0; session text MemoryStore text',
      errorType: 'test_failure',
    });
  }
  return new ValidationResult({
    passed: false,
    message: 'test failed：textnonetext',
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
        message: `citation validationfailed：${ref} InnotesmediumtextFound`,
        evidence: `search notes，${ref} 0 matches`,
        errorType: 'context_missing',
      });
    }
  }
  return new ValidationResult({ passed: true, message: 'text' });
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
    trace.push(`[attempt ${attempt + 1}] executecomplete，cost $${result.cost.toFixed(2)}`);

    const validation = validate(result.output);
    trace.push(`[attempt ${attempt + 1}] validation：${validation.passed ? 'pass' : validation.message}`);
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
    trace.push(`[attempt ${attempt + 1}] textclassification：${errorType}`);

    if (cost > costBudget) {
      trace.push(`[stop] costover limit：$${cost.toFixed(2)} > $${costBudget.toFixed(2)}`);
      return { status: 'stopped', reason: 'cost_limit', output: result.output, attempts: attempt + 1, cost, trace };
    }
    if (previousSignature === signature) {
      trace.push('[stop] same feedback repeated，ProcessingtextfailedResult');
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

async function wait(rl) {
  await rl.question('\n  Press Enter to continue...');
}

async function demoV0(rl) {
  console.log('\n--- V0 no reflection：saw TypeError textcontinue execution ---');
  await wait(rl);
  console.log(`  npm test
  TypeError: Cannot read properties of undefined (reading 'files')
  Agent Move ittext“testscomplete（text)”，then continues writing changelog。
  Problem：feedback signal did not trigger stopping、classification、textProcessing。`);
}

async function demoV1(rl) {
  console.log('\n--- V1 format fix：Schema textfailed -> regenerate ---');
  await wait(rl);
  const result = reflectionLoop(
    (previousError, attempt) => attempt === 0
      ? new ActionResult('{"tool": "search_notes", "query": "memory cleanup"}', 0.01)
      : new ActionResult('{"tool_name": "search_notes", "args": {"query": "memory cleanup"}, "reason": "text Memory text"}', 0.01),
    validateJsonSchema,
  );
  printResult(result);
}

async function demoV2(rl) {
  console.log('\n--- V2 tool error handling：wrong argument -> classification -> decision ---');
  await wait(rl);
  const result = reflectionLoop(
    (previousError, attempt) => attempt === 0
      ? new ActionResult('search_notes(query="", limit=500)', 0.02)
      : new ActionResult('search_notes(query="memory cleanup decay", limit=20)', 0.02),
    validateToolCall,
  );
  printResult(result);
}

async function demoV3(rl) {
  console.log('\n--- V3 test-driven handling：test failed -> correctiontext ---');
  await wait(rl);
  const result = reflectionLoop(
    (previousError, attempt) => new ActionResult(attempt === 0 ? buggyCleanupCode : correctCleanupCode, 0.03),
    validateTests,
  );
  printResult(result);
  console.log(result.output.trim().split('\n').map(line => `  ${line}`).join('\n'));
}

async function demoV4(rl) {
  console.log('\n--- V4 citation validation：text API -> text -> text ---');
  await wait(rl);
  const result = reflectionLoop(
    (previousError, attempt) => attempt === 0
      ? new ActionResult('text `memory.clear_expired()`，text `memory.remove_expired_sessions()`。', 0.02)
      : new ActionResult('text session cleanup text MemoryStore。notestext `MemoryStore.decay()` -> `_purge_old_records()`。', 0.02),
    validateCitation,
  );
  printResult(result);
}

async function demoStop(rl) {
  console.log('\n--- text：same feedback repeated -> hard stop ---');
  await wait(rl);
  const result = reflectionLoop(
    () => new ActionResult('{"tool": "search_notes"}', 0.01),
    validateJsonSchema,
  );
  printResult(result);
}

function printMenu() {
  console.log(`
Reflection text
  0 - V0 no reflection
  1 - V1 format fix
  2 - V2 tool error handling
  3 - V3 test-driven handling
  4 - V4 citation validation
  5 - text
  q - Exit`);
}

async function main() {
  const rl = readline.createInterface({ input, output });
  const demos = [demoV0, demoV1, demoV2, demoV3, demoV4, demoStop];

  printMenu();
  while (true) {
    const choice = (await rl.question('\nPlease choosetext：')).trim().toLowerCase();
    if (choice === 'q') break;
    if (/^[0-5]$/.test(choice)) {
      await demos[Number(choice)](rl);
    } else {
      console.log('nonetext，pleaseInput 0-5 text q。');
    }
  }
  rl.close();
}

main();
