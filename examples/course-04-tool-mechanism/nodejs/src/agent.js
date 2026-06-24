/**
 * 课程四工具机制示例的 Runtime 主循环。
 *
 * LLM 只负责提出结构化工具调用意图。Runtime 负责工具 Schema 暴露、参数校验、
 * 权限检查、审计、执行、Observation 处理和状态更新。
 */
const { SYSTEM_PROMPT } = require("./prompt");
const { executeToolCall } = require("./tools");

class AgentState {
  /**
   * Runtime 持有的单次任务状态。
   *
   * ``stepCount`` 只在工具调用步骤递增；final_answer / ask_user /
   * fail 等终止决策不计入步骤数，因此 trace 长度可能比 stepCount
   * 多 1（多出一条终止决策记录）。
   */
  constructor({ userGoal, maxSteps = 8, maxToolErrors = 5 }) {
    this.userGoal = userGoal;
    this.maxSteps = maxSteps;
    this.maxToolErrors = maxToolErrors;
    this.stepCount = 0;
    this.history = [];
    this.toolResults = [];
    this.errors = [];
    this.auditLog = [];
    this.stopReason = null;
    this.finalAnswer = null;
  }

  recentHistory(n = 5) {
    return this.history.slice(-n);
  }
}

async function runAgent({
  userGoal,
  registry,
  permissions,
  llmCall,
  systemPrompt = SYSTEM_PROMPT,
  maxSteps = 8,
  conversation = [],
  logger = null,
}) {
  // State 和 Trace 独立于 LLM 保存，这样循环行为可以被回放和审计。
  const state = new AgentState({ userGoal, maxSteps });
  const trace = [];

  // 0. 启动循环
  while (!state.stopReason) {
    // 1. Context Assembly：只把本轮决策需要的状态切片交给 LLM。
    const context = assembleContext({ systemPrompt, registry, state, conversation });

    // 2. 调用 llm 进行决策，并对结果进行标准化处理
    const decision = normalizeDecision(await llmCall(context));
    logEvent(logger, { event: "llm_decision", step: state.stepCount, decision });
    const traceEntry = {
      step: state.stepCount,
      contextSummary: contextSummary(context),
      decision,
    };

    // 3. 对结果进行判断
    if (decision.type === "final_answer") {
      state.stopReason = "completed";
      state.finalAnswer = decision.answer || "";
      return finalize({ state, traceEntry, trace, logger, status: "success", fields: { answer: state.finalAnswer } });
    }

    if (decision.type === "ask_user") {
      state.stopReason = "need_user_input";
      return finalize({ state, traceEntry, trace, logger, status: "paused", fields: { question: decision.question || "" } });
    }

    if (decision.type === "fail") {
      state.stopReason = "failed";
      return finalize({ state, traceEntry, trace, logger, status: "failed", fields: { reason: decision.reason || "" } });
    }

    // Interaction / Observation：Runtime 执行工具，并把结果统一成 Observation。
    logEvent(logger, {
      event: "tool_call",
      step: state.stepCount,
      toolName: decision.tool_name,
      arguments: decision.arguments || {},
    });

    // 4. 决策结果是要调用工具，执行工具
    const observation = await executeToolCall({ decision, registry, permissions, auditLog: state.auditLog });
    logEvent(logger, { event: "tool_result", step: state.stepCount, observation });

    // 5. 标准化处理工具执行结果并写入 state
    updateStateFromToolCall({ state, decision, observation });
    traceEntry.observation = observation;

    state.stepCount += 1;
    // 6. Continue or Stop：停止条件由 Runtime 判断，不依赖模型自觉。
    const stopReason = checkStop(state);
    if (stopReason) {
      state.stopReason = stopReason;
    }

    traceEntry.stateUpdate = stateSummary(state);
    traceEntry.stateSnapshot = stateSnapshot(state);
    traceEntry.stopCheck = { continue: !state.stopReason, reason: state.stopReason };
    logEvent(logger, { event: "state_update", step: state.stepCount, state: traceEntry.stateSnapshot });
    logEvent(logger, {
      event: "stop_check",
      step: state.stepCount,
      continue: !state.stopReason,
      reason: state.stopReason,
    });
    trace.push(traceEntry);
    // 7. 进行下一次循环
  }

  return { status: "stopped", reason: state.stopReason, state, trace };
}

function finalize({ state, traceEntry, trace, logger, status, fields = {} }) {
  /** 记录最终状态快照和停止检查，返回统一的结果结构。 */
  traceEntry.stateUpdate = stateSummary(state);
  traceEntry.stateSnapshot = stateSnapshot(state);
  traceEntry.stopCheck = { continue: false, reason: state.stopReason };
  logEvent(logger, { event: "state_update", step: state.stepCount, state: traceEntry.stateSnapshot });
  logEvent(logger, { event: "stop_check", step: state.stepCount, continue: false, reason: state.stopReason });
  trace.push(traceEntry);
  return { status, state, trace, ...fields };
}

function assembleContext({ systemPrompt, registry, state, conversation = [] }) {
  // 选择哪些状态切片应该进入下一次 LLM 调用。
  return {
    system: systemPrompt,
    goal: state.userGoal,
    conversation,
    history: state.recentHistory(5),
    tools: registry.toContextTools(),
    step: state.stepCount,
    maxSteps: state.maxSteps,
    errors: state.errors.slice(-3),
    toolResults: state.toolResults.slice(-5),
    auditLog: state.auditLog.slice(-5),
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
  if (state.errors.length >= state.maxToolErrors) {
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
    conversationCount: context.conversation.length,
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
    auditCount: state.auditLog.length,
    stopReason: state.stopReason,
  };
}

function stateSnapshot(state) {
  // 生成当前步骤执行后的完整 State 快照，便于示例逐步打印。
  return {
    userGoal: state.userGoal,
    maxSteps: state.maxSteps,
    stepCount: state.stepCount,
    history: structuredClone(state.history),
    toolResults: structuredClone(state.toolResults),
    errors: structuredClone(state.errors),
    auditLog: structuredClone(state.auditLog),
    stopReason: state.stopReason,
    finalAnswer: state.finalAnswer,
  };
}

function logEvent(logger, event) {
  if (logger) {
    logger(event);
  }
}

module.exports = {
  AgentState,
  runAgent,
  assembleContext,
};
