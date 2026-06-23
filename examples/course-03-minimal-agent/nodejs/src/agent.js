/**
 * 课程三最小 Agent 的 Runtime 主循环。
 *
 * LLM 只负责提出结构化决策。本模块负责确定性的运行时职责：组装上下文、分发工具、
 * 记录 Observation、更新 State、收集 Trace，以及检查停止条件。
 */
const { SYSTEM_PROMPT } = require("./prompt");

class AgentState {
  constructor({ userGoal, maxSteps = 8 }) {
    this.userGoal = userGoal;
    this.maxSteps = maxSteps;
    this.stepCount = 0;
    this.history = [];
    this.toolResults = [];
    this.errors = [];
    this.stopReason = null;
    this.finalAnswer = null;
  }

  recentHistory(n = 5) {
    return this.history.slice(-n);
  }
}

async function runAgent({ userGoal, tools, llmCall, systemPrompt = SYSTEM_PROMPT, maxSteps = 8 }) {
  // State 和 Trace 独立于 LLM 保存，这样循环行为可以被回放和审计。
  const state = new AgentState({ userGoal, maxSteps });
  const trace = [];

  while (!state.stopReason) {
    // Context Assembly：只把本轮决策需要的状态切片交给 LLM。
    const context = assembleContext({ systemPrompt, tools, state });
    const decision = normalizeDecision(await llmCall(context));
    const traceEntry = {
      step: state.stepCount,
      contextSummary: contextSummary(context),
      decision,
    };

    if (decision.type === "final_answer") {
      state.stopReason = "completed";
      state.finalAnswer = decision.answer || "";
      traceEntry.stateUpdate = stateSummary(state);
      traceEntry.stopCheck = { continue: false, reason: state.stopReason };
      trace.push(traceEntry);
      return { status: "success", answer: state.finalAnswer, state, trace };
    }

    if (decision.type === "ask_user") {
      state.stopReason = "need_user_input";
      traceEntry.stateUpdate = stateSummary(state);
      traceEntry.stopCheck = { continue: false, reason: state.stopReason };
      trace.push(traceEntry);
      return { status: "paused", question: decision.question || "", state, trace };
    }

    if (decision.type === "fail") {
      state.stopReason = "failed";
      traceEntry.stateUpdate = stateSummary(state);
      traceEntry.stopCheck = { continue: false, reason: state.stopReason };
      trace.push(traceEntry);
      return { status: "failed", reason: decision.reason || "", state, trace };
    }

    // Interaction / Observation：Runtime 执行工具，并把结果统一成 Observation。
    const observation = await executeTool({ decision, tools });
    updateStateFromToolCall({ state, decision, observation });
    traceEntry.observation = observation;

    state.stepCount += 1;
    // Continue or Stop：停止条件由 Runtime 判断，不依赖模型自觉。
    const stopReason = checkStop(state);
    if (stopReason) {
      state.stopReason = stopReason;
    }

    traceEntry.stateUpdate = stateSummary(state);
    traceEntry.stopCheck = { continue: !state.stopReason, reason: state.stopReason };
    trace.push(traceEntry);
  }

  return { status: "stopped", reason: state.stopReason, state, trace };
}

function assembleContext({ systemPrompt, tools, state }) {
  // 选择哪些状态切片应该进入下一次 LLM 调用。
  return {
    system: systemPrompt,
    goal: state.userGoal,
    history: state.recentHistory(5),
    tools: Object.entries(tools).map(([name, fn]) => ({ name, description: fn.description || "" })),
    step: state.stepCount,
    maxSteps: state.maxSteps,
    errors: state.errors.slice(-3),
    toolResults: state.toolResults.slice(-5),
  };
}

function normalizeDecision(decision) {
  // 把模型输出收敛到 Runtime 能处理的决策格式。
  if (!decision || typeof decision !== "object" || Array.isArray(decision)) {
    return { type: "fail", thought: "Model output was not a JSON object.", reason: "invalid_decision" };
  }
  if (!["call_tool", "final_answer", "ask_user", "fail"].includes(decision.type)) {
    return { type: "fail", thought: "Model output had an unsupported type.", reason: "invalid_decision_type" };
  }
  if (decision.type === "call_tool" && !decision.arguments) {
    decision.arguments = {};
  }
  return decision;
}

async function executeTool({ decision, tools }) {
  // 执行模型请求的工具调用，并把成功或失败都包装成 Observation。
  const toolName = decision.tool_name;
  const args = decision.arguments || {};
  if (!tools[toolName]) {
    return {
      status: "error",
      summary: `工具不存在: ${toolName}`,
      content: null,
      error: { code: "tool_not_found", message: `工具不存在: ${toolName}` },
    };
  }
  if (!args || typeof args !== "object" || Array.isArray(args)) {
    return {
      status: "error",
      summary: "工具参数必须是 JSON object",
      content: null,
      error: { code: "invalid_arguments", message: "工具参数必须是 JSON object" },
    };
  }

  try {
    return await tools[toolName](args);
  } catch (err) {
    return {
      status: "error",
      summary: err.message,
      content: null,
      error: { code: err.name || "Error", message: err.message },
    };
  }
}

function updateStateFromToolCall({ state, decision, observation }) {
  // 把本轮决策和 Observation 写回 State，供后续循环使用。
  state.history.push({ step: state.stepCount, decision, observation });
  state.toolResults.push({
    tool: decision.tool_name,
    status: observation.status,
    summary: observation.summary,
  });
  if (observation.status === "error") {
    state.errors.push(observation);
  }
}

function checkStop(state) {
  // 检查最大步数、错误次数和重复动作等硬停止条件。
  if (state.stepCount >= state.maxSteps) {
    return "max_steps_exceeded";
  }
  if (state.errors.length >= 3) {
    return "tool_error_limit";
  }
  if (repeatedAction(state, 3)) {
    return "repeated_action";
  }
  return null;
}

function repeatedAction(state, threshold = 3) {
  // 检测 Agent 是否连续重复相同工具调用而没有推进。
  const recent = state.history.slice(-threshold);
  if (recent.length < threshold) {
    return false;
  }
  const signatures = recent.map((item) => {
    if (item.decision.type !== "call_tool") {
      return null;
    }
    return JSON.stringify({
      tool: item.decision.tool_name,
      arguments: sortObject(item.decision.arguments || {}),
    });
  });
  return signatures.every(Boolean) && new Set(signatures).size === 1;
}

function sortObject(value) {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return value;
  }
  return Object.keys(value)
    .sort()
    .reduce((acc, key) => {
      acc[key] = value[key];
      return acc;
    }, {});
}

function contextSummary(context) {
  return {
    goal: context.goal,
    step: context.step,
    historyCount: context.history.length,
    errorCount: context.errors.length,
    tools: context.tools.map((tool) => tool.name),
  };
}

function stateSummary(state) {
  return {
    stepCount: state.stepCount,
    historyCount: state.history.length,
    errorsCount: state.errors.length,
    stopReason: state.stopReason,
  };
}

module.exports = {
  AgentState,
  runAgent,
  assembleContext,
};
