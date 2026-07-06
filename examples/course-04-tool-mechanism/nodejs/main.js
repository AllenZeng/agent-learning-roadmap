/**
 * Node.js entry point for the course 04 tool mechanism example.
 *
 * This file builds on the course 03 minimal loop to demonstrate tool Schema, permission checks, audit logs,
 * structured Observations, and result truncation inside the runtime.
 */
const path = require("node:path");

const { runAgent } = require("./src/agent");
const { ScriptedLLM, deepSeekChatLLM, randomDemoLatencyMs } = require("./src/llm");
const { PermissionPolicy, buildToolRegistry } = require("./src/tools");

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const root = __dirname;
  const scriptedLLM = demoLLM();
  const llmCall = args.realLlm ? deepSeekChatLLM : scriptedLLM.call.bind(scriptedLLM);
  const registry = buildToolRegistry(root);
  const permissions = new PermissionPolicy({ allowedTools: ["read_file", "write_file", "list_files"] });

  const result = await runAgent({
    userGoal: args.goal || "Read data/notes.md, summarize the course 04 tool mechanism, and write output/summary.md",
    registry,
    permissions,
    llmCall,
    maxSteps: Number(args.maxSteps || 6),
    logger: printEventLog,
  });
  printResult(result);
}

function printResult(result) {
  console.log("STATUS:", result.status);
  if (result.answer) {
    console.log("ANSWER:", result.answer);
  }
  if (result.reason) {
    console.log("REASON:", result.reason);
  }
  printTraceSteps(result.trace);
}

function printTraceSteps(trace) {
  console.log("\nTRACE STEPS:");
  for (const entry of trace) {
    console.log(`\n--- STEP ${entry.step} ---`);
    console.log("DECISION:");
    console.log(JSON.stringify(entry.decision, null, 2));
    if (entry.observation) {
      console.log("OBSERVATION:");
      console.log(JSON.stringify(entry.observation, null, 2));
    }
    console.log("STATE:");
    console.log(JSON.stringify(entry.stateSnapshot, null, 2));
    console.log("STOP_CHECK:");
    console.log(JSON.stringify(entry.stopCheck, null, 2));
  }
}

function printEventLog(event) {
  const step = event.step;
  if (event.event === "llm_decision") {
    console.log(`[LOG][step ${step}] LLM_DECISION ${JSON.stringify(event.decision)}`);
  } else if (event.event === "tool_call") {
    console.log(`[LOG][step ${step}] TOOL_CALL ${event.toolName} ${JSON.stringify(event.arguments)}`);
  } else if (event.event === "tool_result") {
    console.log(`[LOG][step ${step}] TOOL_RESULT ${JSON.stringify(event.observation)}`);
  } else if (event.event === "state_update") {
    const state = event.state;
    console.log(
      `[LOG][step ${step}] STATE_UPDATE stepCount=${state.stepCount} history=${state.history.length} errors=${state.errors.length} stopReason=${state.stopReason}`,
    );
  } else if (event.event === "stop_check") {
    console.log(`[LOG][step ${step}] STOP_CHECK continue=${event.continue} reason=${event.reason}`);
  }
}

function demoLLM() {
  // Fixed decision sequence for offline learning and tests.
  return new ScriptedLLM(
    [
      {
        type: "call_tool",
        thought: "First read the course 04 example material.",
        tool_name: "read_file",
        arguments: { path: "data/notes.md" },
      },
      {
        type: "call_tool",
        thought: "Write the summary to the deliverable file.",
        tool_name: "write_file",
        arguments: {
          path: "output/summary.md",
          content:
            "The tool mechanism splits tool calls into Schema exposure, argument validation, permission checks, execution, Observation processing, audit logs, and State Update.",
        },
      },
      {
        type: "final_answer",
        thought: "The summary file has been written.",
        answer: "Generated output/summary.md.",
      },
    ],
    { delayMs: randomDemoLatencyMs },
  );
}

function parseArgs(argv) {
  const parsed = {};
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--real-llm") {
      parsed.realLlm = true;
    } else if (arg === "--goal") {
      parsed.goal = argv[index + 1];
      index += 1;
    } else if (arg === "--max-steps") {
      parsed.maxSteps = argv[index + 1];
      index += 1;
    }
  }
  return parsed;
}

if (require.main === module) {
  main().catch((err) => {
    console.error(err);
    process.exitCode = 1;
  });
}
