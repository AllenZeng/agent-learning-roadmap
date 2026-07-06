const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const test = require("node:test");

const { runAgent } = require("../src/agent");
const { ScriptedLLM } = require("../src/llm");
const {
  PermissionPolicy,
  ToolDefinition,
  ToolRegistry,
  ToolResult,
  buildToolRegistry,
  executeToolCall,
} = require("../src/tools");

test("tool context exposes schema, risk, and boundaries", () => {
  const workspace = fs.mkdtempSync(path.join(os.tmpdir(), "course04-node-tools-"));
  const registry = buildToolRegistry(workspace);

  const readFile = registry.toContextTools().find((tool) => tool.name === "read_file");

  assert.match(readFile.description, /local file/);
  assert.match(readFile.description, /Do not use for internet search/);
  assert.equal(readFile.riskLevel, "low");
  assert.equal(readFile.idempotent, true);
  assert.deepEqual(readFile.parameters.required, ["path"]);
  assert.equal(readFile.parameters.properties.path.type, "string");
});

test("executeToolCall validates parameters before execution", async () => {
  const workspace = fs.mkdtempSync(path.join(os.tmpdir(), "course04-node-validation-"));
  const registry = buildToolRegistry(workspace);
  const auditLog = [];

  const observation = await executeToolCall({
    decision: { type: "call_tool", tool_name: "read_file", arguments: {} },
    registry,
    permissions: new PermissionPolicy({ allowedTools: ["read_file"] }),
    auditLog,
  });

  assert.equal(observation.status, "error");
  assert.equal(observation.error.code, "missing_required");
  assert.equal(observation.error.retryable, false);
  assert.equal(observation.error.suggestedAction, "Please provide arguments: path");
  assert.equal(auditLog[0].stage, "validation");
  assert.equal(auditLog[0].result, "denied");
});

test("deny-first permission blocks write and records audit", async () => {
  const workspace = fs.mkdtempSync(path.join(os.tmpdir(), "course04-node-permission-"));
  const registry = buildToolRegistry(workspace);
  const auditLog = [];

  const observation = await executeToolCall({
    decision: {
      type: "call_tool",
      tool_name: "write_file",
      arguments: { path: "output.txt", content: "hello" },
    },
    registry,
    permissions: new PermissionPolicy({ allowedTools: ["read_file"] }),
    auditLog,
  });

  assert.equal(observation.status, "error");
  assert.equal(observation.error.code, "permission_denied");
  assert.equal(observation.error.needsUser, true);
  assert.equal(fs.existsSync(path.join(workspace, "output.txt")), false);
  assert.equal(auditLog.at(-1).stage, "permission");
  assert.equal(auditLog.at(-1).result, "denied");
});

test("long tool result is truncated for observation", async () => {
  const workspace = fs.mkdtempSync(path.join(os.tmpdir(), "course04-node-long-"));
  fs.writeFileSync(path.join(workspace, "long.md"), "A".repeat(2400), "utf8");
  const registry = buildToolRegistry(workspace, { maxContextChars: 400 });

  const observation = await executeToolCall({
    decision: { type: "call_tool", tool_name: "read_file", arguments: { path: "long.md" } },
    registry,
    permissions: new PermissionPolicy({ allowedTools: ["read_file"] }),
  });

  assert.equal(observation.status, "success");
  assert.equal(observation.contentTruncated, true);
  assert.equal(observation.fullContentRef, "long.md");
  assert.equal(observation.preview.length < 500, true);
  assert.equal("content" in observation, false);
});

test("idempotent tools can retry transient failures", async () => {
  const attempts = [];
  const registry = new ToolRegistry([
    new ToolDefinition({
      name: "lookup_notes",
      description: "Lookup notes by query.",
      parameters: {
        type: "object",
        properties: { query: { type: "string" } },
        required: ["query"],
      },
      handler: async ({ query }) => {
        attempts.push(query);
        if (attempts.length === 1) {
          throw new Error("temporary timeout");
        }
        return ToolResult.success("Query succeeded", { query }).toObject();
      },
      riskLevel: "low",
      idempotent: true,
      maxRetries: 1,
    }),
  ]);

  const observation = await executeToolCall({
    decision: { type: "call_tool", tool_name: "lookup_notes", arguments: { query: "agent" } },
    registry,
    permissions: new PermissionPolicy({ allowedTools: ["lookup_notes"] }),
  });

  assert.equal(observation.status, "success");
  assert.equal(observation.retryCount, 1);
  assert.equal(attempts.length, 2);
});

test("agent loop uses tool executor and audit log", async () => {
  const workspace = fs.mkdtempSync(path.join(os.tmpdir(), "course04-node-agent-"));
  fs.writeFileSync(path.join(workspace, "notes.md"), "Agent tools need schemas and permissions.", "utf8");
  const registry = buildToolRegistry(workspace);
  const llm = new ScriptedLLM([
    {
      type: "call_tool",
      thought: "Need the source notes.",
      tool_name: "read_file",
      arguments: { path: "notes.md" },
    },
    {
      type: "call_tool",
      thought: "Persist the summary.",
      tool_name: "write_file",
      arguments: {
        path: "summary.md",
        content: "The tool mechanism needs Schema, permission checks, auditing, and structured Observations.",
      },
    },
    { type: "final_answer", thought: "Done.", answer: "summary.md has been written." },
  ]);

  const result = await runAgent({
    userGoal: "Read notes.md, summarize it, and write summary.md",
    registry,
    permissions: new PermissionPolicy({ allowedTools: ["read_file", "write_file"] }),
    llmCall: llm.call.bind(llm),
  });

  assert.equal(result.status, "success");
  assert.equal(fs.existsSync(path.join(workspace, "summary.md")), true);
  assert.equal(result.state.auditLog.length, 2);
  assert.equal(result.state.auditLog[0].result, "allowed");
});
