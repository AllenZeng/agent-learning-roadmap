/**
 * Course 04 tool mechanism example: tool definitions, argument validation, permissions, auditing, and Observation processing.
 *
 * In course 03, tools are just a set of ordinary functions; course 04 adds a layer around those functions:
 * runtime mechanics for tool definitions, Schema, permissions, auditing, retries, and Observation shaping.
 */
const fs = require("node:fs");
const path = require("node:path");

class ToolResult {
  /**
   * Normalized tool return structure.
   *
   * Success and failure both use the same structure so the model can reliably read `status`, `summary`,
   * and `error.code` on the next turn. This fits an Agent loop better than arbitrary strings or exception stacks from each tool.
   */
  constructor({ status, summary, content = null, error = null }) {
    this.status = status;
    this.summary = summary;
    this.content = content;
    this.error = error;
  }

  static success(summary, content = null) {
    return new ToolResult({ status: "success", summary, content });
  }

  static error(code, message, options = {}) {
    // `retryable`, `suggestedAction`, and `needsUser` are for the next LLM decision:
    // they tell the model whether the error can be retried, how it should be corrected, and whether user input is needed.
    return new ToolResult({
      status: "error",
      summary: message,
      error: {
        code,
        message,
        retryable: Boolean(options.retryable),
        suggestedAction: options.suggestedAction || "",
        needsUser: Boolean(options.needsUser),
      },
    });
  }

  toObject() {
    return {
      status: this.status,
      summary: this.summary,
      content: this.content,
      error: this.error,
    };
  }
}

class ToolDefinition {
  /**
   * Complete tool definition.
   *
   * - `description` describes applicable and non-applicable cases to help the model choose tools.
   * - `parameters` is a simplified JSON Schema that helps the runtime validate arguments.
   * - `riskLevel` and `idempotent` are used by permission and retry policies.
   * - `handler` is the function that actually performs the action and is not exposed to the model.
   */
  constructor({ name, description, parameters, handler, riskLevel = "low", idempotent = true, maxRetries = 0 }) {
    this.name = name;
    this.description = description;
    this.parameters = parameters;
    this.handler = handler;
    this.riskLevel = riskLevel;
    this.idempotent = idempotent;
    this.maxRetries = maxRetries;
  }

  toContext() {
    // Return the safe tool view injected into LLM context. The model can only see tool descriptions and Schema,
    // and cannot execute handlers directly; real execution must go through executeToolCall.
    return {
      name: this.name,
      description: this.description,
      parameters: this.parameters,
      riskLevel: this.riskLevel,
      idempotent: this.idempotent,
    };
  }
}

class ToolRegistry {
  /**
   * Tool registry.
   *
   * The registry solves two problems:
   * 1. the runtime can find the actual definition and handler by tool name.
   * 2. Context Assembly can generate a unified tool list for the model.
   */
  constructor(tools, options = {}) {
    this.tools = new Map(tools.map((tool) => [tool.name, tool]));
    // Maximum character budget before tool results enter context. Larger results become preview + ref,
    // so long files or logs are not pushed directly into the next LLM context.
    this.maxContextChars = options.maxContextChars || 1200;
  }

  get(name) {
    return this.tools.get(name);
  }

  toContextTools() {
    return Array.from(this.tools.values()).map((tool) => tool.toContext());
  }
}

class PermissionPolicy {
  /**
   * Deny-first permission policy: reject any tool that is not explicitly allowed.
   *
   * The example policy authorizes only by tool name. Real systems usually also check user, resource scope,
   * paths or IDs in arguments, risk level, and whether human confirmation already exists.
   */
  constructor({ allowedTools = [] } = {}) {
    this.allowedTools = new Set(allowedTools);
  }

  check(tool) {
    return this.allowedTools.has(tool.name);
  }
}

async function executeToolCall({ decision, registry, permissions, auditLog = [] }) {
  /**
   * Execute the full tool path.
   *
   * This is the key change from course 03 to course 04: the Agent loop no longer calls functions directly.
   * A model-produced tool call must pass through these steps in order:
   * 1. Tool existence check
   * 2. Argument structure check
   * 3. Schema argument validation
   * 4. Deny-first permission check
   * 5. Handler execution and idempotent retry
   * 6. Observation shaping
   * 7. Audit log recording
   */
  const toolName = decision.tool_name;
  const args = decision.arguments || {};

  // Check the registry first instead of calling a function directly from an object, so missing tools can return structured errors
  // and record the failure in auditLog.
  const tool = registry.get(toolName);

  if (!tool) {
    const observation = ToolResult.error("tool_not_found", `工具不存在: ${toolName}`, {
      suggestedAction: "检查工具名，或从可用工具列表中重新选择",
    }).toObject();
    audit(auditLog, toolName, args, "lookup", "denied", observation);
    return observation;
  }

  // arguments must be an object. The model may occasionally output a string, array, or null; the runtime
  // must intercept that before execution instead of leaking exceptions into tool handlers.
  if (!args || typeof args !== "object" || Array.isArray(args)) {
    const observation = ToolResult.error("invalid_arguments", "工具参数必须是 JSON object", {
      suggestedAction: "重新生成 arguments 对象",
    }).toObject();
    audit(auditLog, toolName, args, "validation", "denied", observation);
    return observation;
  }

  // Schema validation runs before permission checks, so basic issues like missing arguments or type errors are not misreported as
  // permission problems, making root causes easier to debug.
  const validationError = validateArguments(tool, args);
  if (validationError) {
    audit(auditLog, toolName, args, "validation", "denied", validationError);
    return validationError;
  }

  // Deny-first: tools are not executable by default unless allowed. This matters especially for medium-risk tools like write_file,
  // because even plausible model-generated arguments must be allowed uniformly by the runtime.
  if (!permissions.check(tool, args)) {
    const observation = ToolResult.error("permission_denied", `工具 '${tool.name}' 没有执行权限`, {
      suggestedAction: "请求用户授权，或选择已授权的低风险工具",
      needsUser: true,
    }).toObject();
    audit(auditLog, toolName, args, "permission", "denied", observation);
    return observation;
  }

  const startedAt = Date.now();
  let attempts = 0;
  while (true) {
    try {
      // Only here is the tool actually executed. All earlier steps only check whether it should be executed.
      const raw = await tool.handler(args);
      // Raw tool results are not always suitable for the next context; this step applies truncation,
      // references, and metadata enrichment.
      const observation = shapeObservation(raw, tool, args, registry.maxContextChars);
      observation.retryCount = attempts;
      observation.durationMs = Date.now() - startedAt;
      audit(auditLog, toolName, args, "execution", "allowed", observation);
      return observation;
    } catch (err) {
      // Retry only idempotent tools. Read-file and query tools can usually be retried; write, send, and order-placement
      // tools with side effects should not be retried automatically.
      if (tool.idempotent && attempts < tool.maxRetries) {
        attempts += 1;
        continue;
      }
      const observation = ToolResult.error(err.name || "Error", err.message, {
        suggestedAction: "检查参数和工具实现",
      }).toObject();
      observation.retryCount = attempts;
      audit(auditLog, toolName, args, "execution", "error", observation);
      return observation;
    }
  }
}

function buildToolRegistry(workspace, options = {}) {
  /**
   * Build the example tool set.
   *
   * This intentionally includes only three tools so learners can observe how each tool-definition field affects behavior:
   * - read_file: low risk, idempotent, retryable.
   * - write_file: medium risk, non-idempotent, requires explicit authorization.
   * - list_files: low risk, idempotent, used as the recovery path after file_not_found.
   */
  function readFile({ path: filePath }) {
    // Tools must still perform path-boundary checks internally. Even with outer Schema and permissions, out-of-bounds paths are
    // resource-level risks that each tool must guard against itself.
    let target;
    try {
      target = resolveWorkspacePath(workspace, filePath);
    } catch (err) {
      return ToolResult.error("path_not_allowed", err.message, {
        suggestedAction: "请选择 workspace 内的相对路径",
        needsUser: true,
      }).toObject();
    }
    if (!fs.existsSync(target)) {
      return ToolResult.error("file_not_found", `未找到文件: ${filePath}`, {
        suggestedAction: "使用 list_files 查看可用文件，或请用户确认路径",
        needsUser: true,
      }).toObject();
    }
    if (!fs.statSync(target).isFile()) {
      return ToolResult.error("not_a_file", `路径不是文件: ${filePath}`).toObject();
    }
    const content = fs.readFileSync(target, "utf8");
    return ToolResult.success(`读取到 ${content.length} 个字符: ${filePath}`, {
      content,
      path: filePath,
      totalChars: content.length,
    }).toObject();
  }

  function writeFile({ path: filePath, content }) {
    // This is a medium-risk tool: the write itself is simple in the handler, but whether writing is allowed should be decided by
    // PermissionPolicy before execution.
    const target = resolveWorkspacePath(workspace, filePath);
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.writeFileSync(target, content, "utf8");
    return ToolResult.success(`已写入 ${content.length} 个字符: ${filePath}`, { path: filePath }).toObject();
  }

  function listFiles() {
    // Error-recovery tool: when read_file returns file_not_found, the model can list
    // available files first, then ask the user for confirmation or switch to the correct path.
    const files = [];
    walk(workspace, (filePath) => files.push(path.relative(workspace, filePath)));
    return ToolResult.success(`找到 ${files.length} 个文件`, { files: files.sort() }).toObject();
  }

  return new ToolRegistry(
    [
      new ToolDefinition({
        name: "read_file",
        description:
          "读取 workspace 中的本地文件。适用于用户给出明确文件路径并要求查看、总结或搜索内容时。不要用于搜索互联网、不要读取 workspace 外部路径。",
        parameters: {
          type: "object",
          properties: {
            path: { type: "string", description: "workspace 内相对路径，例如 data/notes.md" },
          },
          required: ["path"],
        },
        handler: readFile,
        riskLevel: "low",
        idempotent: true,
        maxRetries: 1,
      }),
      new ToolDefinition({
        name: "write_file",
        description:
          "向 workspace 写入 UTF-8 文本文件。适用于用户明确要求保存结果时。不要用于删除、覆盖未确认的重要文件；写入动作需要权限。",
        parameters: {
          type: "object",
          properties: {
            path: { type: "string", description: "workspace 内输出路径" },
            content: { type: "string", description: "要写入的文本内容" },
          },
          required: ["path", "content"],
        },
        handler: writeFile,
        riskLevel: "medium",
        idempotent: false,
      }),
      new ToolDefinition({
        name: "list_files",
        description: "列出 workspace 内文件。适用于文件名不确定或 read_file 返回 file_not_found 后。",
        parameters: { type: "object", properties: {}, required: [] },
        handler: listFiles,
        riskLevel: "low",
        idempotent: true,
      }),
    ],
    options,
  );
}

function validateArguments(tool, args) {
  // Perform minimal validation based on the tool argument Schema.
  // The example implements only required-field, unknown-field, and basic type checks needed by the course. Real systems can integrate
  // libraries such as AJV or Zod to support rules like enum, minimum, and format.
  const required = tool.parameters.required || [];
  const properties = tool.parameters.properties || {};
  const missing = required.filter((name) => !(name in args));
  if (missing.length > 0) {
    return ToolResult.error("missing_required", `缺少必填参数: ${missing.join(", ")}`, {
      suggestedAction: `请补充参数: ${missing.join(", ")}`,
    }).toObject();
  }
  for (const [name, value] of Object.entries(args)) {
    const prop = properties[name];
    if (!prop) {
      return ToolResult.error("unknown_argument", `未知参数: ${name}`, {
        suggestedAction: "只传入 Schema 中声明的参数",
      }).toObject();
    }
    if (prop.type === "string" && typeof value !== "string") {
      return ToolResult.error("type_error", `参数 '${name}' 应为 string`).toObject();
    }
    if (prop.type === "integer" && !Number.isInteger(value)) {
      return ToolResult.error("type_error", `参数 '${name}' 应为 integer`).toObject();
    }
  }
  return null;
}

function shapeObservation(raw, tool, args, maxChars) {
  // Shape raw tool results into Observations suitable for injection into LLM context.
  // In course 03, tool results entered state/history as-is; course 04 adds a context budget:
  // long text gives the model only preview and fullContentRef so the next context is not flooded.
  if (raw.status !== "success") {
    return raw;
  }
  const content = raw.content;
  if (!content || typeof content.content !== "string" || content.content.length <= maxChars) {
    return raw;
  }
  const half = Math.floor(maxChars / 2);
  const text = content.content;
  return {
    status: "success",
    summary: raw.summary,
    contentTruncated: true,
    preview: `${text.slice(0, half)}\n... [truncated] ...\n${text.slice(-half)}`,
    fullContentRef: content.path || args.path,
    totalChars: text.length,
    error: null,
  };
}

function resolveWorkspacePath(workspace, requestedPath) {
  // Restrict model-generated paths to the workspace.
  // This is the tool-layer safety boundary: the model may generate ../ or absolute paths, and the runtime cannot trust them.
  const root = path.resolve(workspace);
  const target = path.resolve(root, requestedPath);
  if (target !== root && !target.startsWith(root + path.sep)) {
    throw new Error("path is outside the example workspace");
  }
  return target;
}

function walk(root, onFile) {
  for (const entry of fs.readdirSync(root, { withFileTypes: true })) {
    const fullPath = path.join(root, entry.name);
    if (entry.isDirectory()) {
      walk(fullPath, onFile);
    } else if (entry.isFile()) {
      onFile(fullPath);
    }
  }
}

function audit(auditLog, toolName, args, stage, result, observation) {
  // Record key points in the tool path.
  // The audit log is not a full Trace for the model; it is a safety record for developers and systems:
  // which tool, which arguments, at which stage it was allowed or rejected, and the final error code.
  auditLog.push({
    toolName,
    arguments: args,
    stage,
    result,
    status: observation.status,
    errorCode: observation.error?.code,
  });
}

module.exports = {
  PermissionPolicy,
  ToolDefinition,
  ToolRegistry,
  ToolResult,
  buildToolRegistry,
  executeToolCall,
};
