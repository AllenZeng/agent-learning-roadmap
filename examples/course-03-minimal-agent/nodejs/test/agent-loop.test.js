const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const test = require("node:test");

const { AgentState, SessionState, runAgent, runTurn } = require("../src/agent");
const { ScriptedLLM } = require("../src/llm");
const { buildTools } = require("../src/tools");

test("runs a multi-step loop and writes the final file", async () => {
  const workspace = fs.mkdtempSync(path.join(os.tmpdir(), "minimal-agent-node-"));
  fs.writeFileSync(
    path.join(workspace, "notes.md"),
    "# Notes\n\nAgent = Prompt + LLM Decision + Tools + State + Loop Control.\n",
    "utf8",
  );

  const llm = new ScriptedLLM([
    {
      type: "call_tool",
      thought: "Need to read the source notes first.",
      tool_name: "read_file",
      arguments: { path: "notes.md" },
    },
    {
      type: "call_tool",
      thought: "Need to persist a short summary.",
      tool_name: "write_file",
      arguments: {
        path: "summary.md",
        content: "Agent 最小闭环由 Prompt、LLM 决策、工具交互、State 和循环控制组成。",
      },
    },
    {
      type: "final_answer",
      thought: "The requested summary has been written.",
      answer: "已写入 summary.md。",
    },
  ]);

  const result = await runAgent({
    userGoal: "读取 notes.md，总结后写入 summary.md",
    tools: buildTools(workspace),
    llmCall: llm.call.bind(llm),
    maxSteps: 5,
  });

  assert.equal(result.status, "success");
  assert.equal(result.state.stopReason, "completed");
  assert.equal(result.state.stepCount, 2);
  assert.equal(result.trace.length, 3);
  assert.equal(result.trace[0].stateSnapshot.stepCount, 1);
  assert.equal(result.trace[0].stateSnapshot.history.length, 1);
  assert.equal(result.trace[1].stateSnapshot.toolResults[1].tool, "write_file");
  assert.equal(result.trace[2].stateSnapshot.stopReason, "completed");
  assert.match(fs.readFileSync(path.join(workspace, "summary.md"), "utf8"), /Prompt、LLM 决策/);
});

test("records tool errors in state", async () => {
  const workspace = fs.mkdtempSync(path.join(os.tmpdir(), "minimal-agent-node-errors-"));
  const llm = new ScriptedLLM([
    {
      type: "call_tool",
      thought: "Try reading the requested file.",
      tool_name: "read_file",
      arguments: { path: "missing.md" },
    },
    {
      type: "fail",
      thought: "The file is not available.",
      reason: "missing input file",
    },
  ]);

  const result = await runAgent({
    userGoal: "读取 missing.md",
    tools: buildTools(workspace),
    llmCall: llm.call.bind(llm),
    maxSteps: 5,
  });

  assert.equal(result.status, "failed");
  assert.equal(result.state.stopReason, "failed");
  assert.equal(result.state.errors.length, 1);
  assert.equal(result.state.errors[0].error.code, "file_not_found");
  assert.equal(result.state.toolResults[0].status, "error");
});

test("stops when the same tool action repeats", async () => {
  const repeated = {
    type: "call_tool",
    thought: "Search again.",
    tool_name: "search_text",
    arguments: { query: "agent", text: "agent loop" },
  };
  const llm = new ScriptedLLM([repeated, repeated, repeated]);

  const result = await runAgent({
    userGoal: "不断搜索相同内容",
    tools: buildTools(process.cwd()),
    llmCall: llm.call.bind(llm),
    maxSteps: 8,
  });

  assert.equal(result.status, "stopped");
  assert.equal(result.state.stopReason, "repeated_action");
});

test("state recentHistory returns the tail", () => {
  const state = new AgentState({ userGoal: "demo" });
  state.history = Array.from({ length: 8 }, (_, step) => ({ step }));

  assert.deepEqual(state.recentHistory(3), [{ step: 5 }, { step: 6 }, { step: 7 }]);
});

test("session keeps multi-turn conversation history", async () => {
  const session = new SessionState();
  const llm = new ScriptedLLM([
    {
      type: "final_answer",
      thought: "Answer the first turn.",
      answer: "第一轮回答。",
    },
    {
      type: "final_answer",
      thought: "Answer with the previous turn in context.",
      answer: "第二轮回答，已看到上一轮。",
    },
  ]);

  const first = await runTurn({
    session,
    userMessage: "第一轮：介绍最小 Agent。",
    tools: buildTools(process.cwd()),
    llmCall: llm.call.bind(llm),
  });
  const second = await runTurn({
    session,
    userMessage: "第二轮：基于上一轮再补充 State。",
    tools: buildTools(process.cwd()),
    llmCall: llm.call.bind(llm),
  });

  assert.equal(first.status, "success");
  assert.equal(second.status, "success");
  assert.equal(session.messages.length, 4);
  assert.equal(session.messages[0].role, "user");
  assert.equal(session.messages[1].role, "assistant");
  assert.equal(session.messages[2].content, "第二轮：基于上一轮再补充 State。");
  assert.equal(session.turns[1].answer, "第二轮回答，已看到上一轮。");
  assert.equal(llm.calls[1].conversation.at(-3).content, "第一轮：介绍最小 Agent。");
  assert.equal(llm.calls[1].conversation.at(-2).content, "第一轮回答。");
});

test("scripted LLM can simulate response latency", async () => {
  const delays = [];
  const llm = new ScriptedLLM([{ type: "final_answer", thought: "done", answer: "ok" }], {
    delayMs: () => 1500,
    sleep: async (ms) => delays.push(ms),
  });

  const decision = await llm.call({ goal: "demo" });

  assert.equal(decision.answer, "ok");
  assert.deepEqual(delays, [1500]);
  assert.equal(llm.calls[0].simulatedLatencyMs, 1500);
});

test("runtime emits execution logs", async () => {
  const events = [];
  const llm = new ScriptedLLM([
    {
      type: "call_tool",
      thought: "Search once.",
      tool_name: "search_text",
      arguments: { query: "Agent", text: "Agent loop" },
    },
    { type: "final_answer", thought: "Done.", answer: "ok" },
  ]);

  const result = await runAgent({
    userGoal: "搜索 Agent",
    tools: buildTools(process.cwd()),
    llmCall: llm.call.bind(llm),
    logger: (event) => events.push(event),
  });

  assert.equal(result.status, "success");
  assert.deepEqual(
    events.map((event) => event.event),
    [
      "llm_decision",
      "tool_call",
      "tool_result",
      "state_update",
      "stop_check",
      "llm_decision",
      "state_update",
      "stop_check",
    ],
  );
  assert.equal(events[1].toolName, "search_text");
  assert.equal(events[2].observation.status, "success");
  assert.equal(events.at(-1).reason, "completed");
});
