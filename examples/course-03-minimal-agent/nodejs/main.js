/**
 * Node.js 版最小 Agent 闭环的命令行入口。
 *
 * 这个文件把课程三的几个构件串起来：Prompt 位于 src/prompt.js，决策来自脚本化
 * 或真实 LLM 适配器，工具是本地函数，runAgent 负责状态和循环控制。
 */
const path = require("node:path");
const readline = require("node:readline/promises");

const { runAgent, runTurn, SessionState } = require("./src/agent");
const { ScriptedLLM, openAIResponsesLLM, randomDemoLatencyMs } = require("./src/llm");
const { buildTools } = require("./src/tools");

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const root = __dirname;
  const scriptedLLM = demoLLM();
  const llmCall = args.realLlm ? openAIResponsesLLM : scriptedLLM.call.bind(scriptedLLM);
  if (args.chat) {
    await runChat({ root, llmCall, maxSteps: Number(args.maxSteps || 6), logger: printEventLog });
    return;
  }

  const result = await runAgent({
    userGoal: args.goal || "读取 data/notes.md，总结课程三最小 Agent 闭环，并写入 output/summary.md",
    tools: buildTools(root),
    llmCall,
    maxSteps: Number(args.maxSteps || 6),
    logger: printEventLog,
  });
  printResult(result);
}

async function runChat({ root, llmCall, maxSteps, logger }) {
  const session = new SessionState();
  const tools = buildTools(root);
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  console.log("进入多轮对话模式。输入 exit 或 quit 结束。");
  try {
    while (true) {
      const userMessage = (await rl.question("User> ")).trim();
      if (!userMessage) {
        continue;
      }
      if (userMessage.toLowerCase() === "exit" || userMessage.toLowerCase() === "quit") {
        break;
      }
      const result = await runTurn({ session, userMessage, tools, llmCall, maxSteps, logger });
      console.log("Assistant>", result.answer || result.question || result.reason || result.status);
      printTraceSteps(result.trace);
      console.log("SESSION_MESSAGES:", session.messages.length, "TURNS:", session.turns.length);
    }
  } finally {
    rl.close();
  }
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
  // 固定决策序列，便于离线学习和测试。
  return new ScriptedLLM(
    [
      {
        type: "call_tool",
        thought: "先读取课程三示例资料。",
        tool_name: "read_file",
        arguments: { path: "data/notes.md" },
      },
      {
        type: "call_tool",
        thought: "将摘要写入交付文件。",
        tool_name: "write_file",
        arguments: {
          path: "output/summary.md",
          content:
            "最小 Agent 闭环包含 Prompt、LLM 决策、工具交互、State 状态管理和循环控制。Runtime 负责组装上下文、执行工具、记录 Observation、更新 State，并判断是否继续。",
        },
      },
      {
        type: "final_answer",
        thought: "摘要文件已经写入。",
        answer: "已生成 output/summary.md。",
      },
      {
        type: "final_answer",
        thought: "基于会话历史回答。",
        answer: "这是第二轮回答，SessionState 已保留前面的对话。",
      },
      {
        type: "final_answer",
        thought: "继续基于会话历史回答。",
        answer: "这是第三轮回答，可以继续查看 session.messages。",
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
    } else if (arg === "--chat") {
      parsed.chat = true;
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
