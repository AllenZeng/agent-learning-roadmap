const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const test = require("node:test");

const { AgentState, runAgent } = require("../src/agent");
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
