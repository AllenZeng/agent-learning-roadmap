/**
 * 课程四工具机制示例：工具定义、参数校验、权限、审计和 Observation 处理。
 *
 * course 03 的工具只是普通函数集合；course 04 在普通函数外面加了一层
 * Runtime 机制：工具定义、Schema、权限、审计、重试和 Observation 整形。
 */
const fs = require("node:fs");
const path = require("node:path");

class ToolResult {
  /**
   * 统一工具返回结构。
   *
   * 成功和失败都走同一结构，模型下一轮才能稳定读取 `status`、`summary`
   * 和 `error.code`。这比每个工具随意返回字符串或异常堆栈更适合 Agent loop。
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
    // `retryable`、`suggestedAction` 和 `needsUser` 是给下一轮 LLM 决策用的：
    // 它们告诉模型这个错误能否重试、应该怎么修正、是否需要用户介入。
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
   * 工具的完整定义。
   *
   * - `description` 说明适用/不适用场景，帮助模型选工具。
   * - `parameters` 是简化版 JSON Schema，帮助 Runtime 校验参数。
   * - `riskLevel` 和 `idempotent` 给权限与重试策略使用。
   * - `handler` 才是真正执行动作的函数，不会暴露给模型。
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
    // 返回注入 LLM 上下文的安全工具视图。模型只能看到工具说明和 Schema，
    // 不能直接执行 handler；真正执行必须经过 executeToolCall。
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
   * 工具注册表。
   *
   * Registry 解决两个问题：
   * 1. Runtime 可以通过工具名找到实际定义和 handler。
   * 2. Context Assembly 可以统一生成给模型看的工具列表。
   */
  constructor(tools, options = {}) {
    this.tools = new Map(tools.map((tool) => [tool.name, tool]));
    // 工具结果进入上下文前的最大字符预算。超过后转成 preview + ref，
    // 避免把长文件或长日志直接塞进下一轮 LLM 上下文。
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
   * Deny-first 权限策略：未显式允许的工具一律拒绝。
   *
   * 示例策略只按工具名授权。真实系统通常还会检查用户、资源范围、
   * 参数中的路径/ID、风险等级，以及是否已有人工确认。
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
   * 执行完整工具链路。
   *
   * 这是课程四相对课程三最关键的变化：Agent loop 不再直接调用函数。
   * 模型输出的 tool call 必须依次经过：
   * 1. 工具存在性检查
   * 2. arguments 结构检查
   * 3. Schema 参数校验
   * 4. Deny-first 权限检查
   * 5. handler 执行与幂等重试
   * 6. Observation 整形
   * 7. 审计日志记录
   */
  const toolName = decision.tool_name;
  const args = decision.arguments || {};

  // 先查注册表，而不是直接从对象上调函数。这样工具不存在时能返回结构化错误，
  // 并把失败记录进 auditLog。
  const tool = registry.get(toolName);

  if (!tool) {
    const observation = ToolResult.error("tool_not_found", `工具不存在: ${toolName}`, {
      suggestedAction: "检查工具名，或从可用工具列表中重新选择",
    }).toObject();
    audit(auditLog, toolName, args, "lookup", "denied", observation);
    return observation;
  }

  // arguments 必须是对象。模型偶尔会输出字符串、数组或 null；Runtime
  // 需要在执行前拦截，不能把异常泄漏到工具 handler 内部。
  if (!args || typeof args !== "object" || Array.isArray(args)) {
    const observation = ToolResult.error("invalid_arguments", "工具参数必须是 JSON object", {
      suggestedAction: "重新生成 arguments 对象",
    }).toObject();
    audit(auditLog, toolName, args, "validation", "denied", observation);
    return observation;
  }

  // Schema 校验在权限检查之前执行。这样缺参数、类型错误等低级问题不会被误报为
  // 权限问题，调试时能更快定位根因。
  const validationError = validateArguments(tool, args);
  if (validationError) {
    audit(auditLog, toolName, args, "validation", "denied", validationError);
    return validationError;
  }

  // Deny-first：没被允许的工具默认不能执行。尤其是 write_file 这类中风险工具，
  // 即使模型生成了看似合理的参数，也必须由 Runtime 统一放行。
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
      // 到这里才真正执行工具。前面的所有步骤都只是在检查“是否应该执行”。
      const raw = await tool.handler(args);
      // 原始工具结果不一定适合直接进入下一轮上下文；这里统一做截断、
      // 引用和元数据补充。
      const observation = shapeObservation(raw, tool, args, registry.maxContextChars);
      observation.retryCount = attempts;
      observation.durationMs = Date.now() - startedAt;
      audit(auditLog, toolName, args, "execution", "allowed", observation);
      return observation;
    } catch (err) {
      // 只重试幂等工具。读文件、查询类工具通常可以重试；写入、发送、下单
      // 等有副作用工具不应该自动重试。
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
   * 构造示例工具集。
   *
   * 这里故意只放 3 个工具，便于学习者观察每个工具定义字段如何影响行为：
   * - read_file: 低风险、幂等、可重试。
   * - write_file: 中风险、非幂等、需要显式授权。
   * - list_files: 低风险、幂等，用于 file_not_found 后的恢复路径。
   */
  function readFile({ path: filePath }) {
    // 工具内部仍然要做路径边界检查。即使外层有 Schema 和权限，路径越界这种
    // 资源级风险也必须由工具自身兜底。
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
    // 这是中风险工具：写入本身在 handler 里很简单，但是否允许写入应该由
    // PermissionPolicy 在执行前判断。
    const target = resolveWorkspacePath(workspace, filePath);
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.writeFileSync(target, content, "utf8");
    return ToolResult.success(`已写入 ${content.length} 个字符: ${filePath}`, { path: filePath }).toObject();
  }

  function listFiles() {
    // 错误恢复工具：当 read_file 返回 file_not_found 时，模型可以先列出
    // 可用文件，再请求用户确认或改用正确路径。
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
  // 根据工具参数 Schema 做最小校验。
  // 示例只实现课程需要的必填、未知字段和基础类型检查。真实系统可以接入
  // AJV、Zod 等库来支持 enum、minimum、format 等规则。
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
  // 把工具原始结果整理成适合注入 LLM 上下文的 Observation。
  // course 03 里工具结果原样进入 state/history；course 04 增加上下文预算：
  // 长文本只给模型 preview 和 fullContentRef，避免下一轮上下文被长文本挤爆。
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
  // 把模型生成的路径限制在 workspace 内。
  // 这是工具层的安全边界：模型可能生成 ../ 或绝对路径，Runtime 不能信任。
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
  // 记录工具链路的关键节点。
  // 审计日志不是给模型看的完整 Trace，而是给开发者/系统看的安全记录：
  // 哪个工具、什么参数、在哪个阶段被允许或拒绝、最终错误码是什么。
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
