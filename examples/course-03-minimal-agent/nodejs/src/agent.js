/**
 * Runtime main loop for the course 03 minimal Agent.
 *
 * The LLM only proposes structured decisions. This module owns deterministic runtime duties: assembling context, dispatching tools,
 * recording Observations, updating State, collecting Trace, and checking stop conditions.
 */
const { SYSTEM_PROMPT } = require("./prompt");

class AgentState {
  /**
   * Single-task state held by the runtime.
   *
   * ``stepCount`` increments only on tool-call steps; final_answer / ask_user /
   * fail and other terminal decisions do not count as steps, so trace length may be
   * one greater than stepCount because it includes the terminal decision record.
   */
  constructor({ userGoal, maxSteps = 8, maxToolErrors = 5 }) {
    this.userGoal = userGoal;
    this.maxSteps = maxSteps;
    this.maxToolErrors = maxToolErrors;
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

async function runAgent({
  userGoal,
  tools,
  llmCall,
  systemPrompt = SYSTEM_PROMPT,
  maxSteps = 8,
  conversation = [],
  logger = null,
}) {
  // State and Trace are stored outside the LLM so loop behavior can be replayed and audited.
  const state = new AgentState({ userGoal, maxSteps });
  const trace = [];

  // 0. Start the loop
  while (!state.stopReason) {
    // 1. Context Assembly: pass only the state slices needed for this decision to the LLM.
    const context = assembleContext({ systemPrompt, tools, state, conversation });

    // 2. Call the LLM for a decision and normalize the result
    const decision = normalizeDecision(await llmCall(context));
    logEvent(logger, { event: "llm_decision", step: state.stepCount, decision });
    const traceEntry = {
      step: state.stepCount,
      contextSummary: contextSummary(context),
      decision,
    };

    // 3. Inspect the result
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

    // Interaction / Observation: the runtime executes tools and normalizes results into Observations.
    logEvent(logger, {
      event: "tool_call",
      step: state.stepCount,
      toolName: decision.tool_name,
      arguments: decision.arguments || {},
    });

    // 4. If the decision is a tool call, execute the tool
    const observation = await executeTool({ decision, tools });
    logEvent(logger, { event: "tool_result", step: state.stepCount, observation });

    // 5. Normalize the tool execution result and write it into state
    updateStateFromToolCall({ state, decision, observation });
    traceEntry.observation = observation;

    state.stepCount += 1;
    // 6. Continue or Stop: the runtime owns stopping conditions instead of relying on the model to stop itself.
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
    // 7. Continue to the next loop iteration
  }

  return { status: "stopped", reason: state.stopReason, state, trace };
}

function finalize({ state, traceEntry, trace, logger, status, fields = {} }) {
  /** Record the final state snapshot and stop check, then return a normalized result structure. */
  traceEntry.stateUpdate = stateSummary(state);
  traceEntry.stateSnapshot = stateSnapshot(state);
  traceEntry.stopCheck = { continue: false, reason: state.stopReason };
  logEvent(logger, { event: "state_update", step: state.stepCount, state: traceEntry.stateSnapshot });
  logEvent(logger, { event: "stop_check", step: state.stepCount, continue: false, reason: state.stopReason });
  trace.push(traceEntry);
  return { status, state, trace, ...fields };
}

function assembleContext({ systemPrompt, tools, state, conversation = [] }) {
  // Choose which state slices should enter the next LLM call.
  return {
    system: systemPrompt,
    goal: state.userGoal,
    conversation,
    history: state.recentHistory(5),
    tools: Object.entries(tools).map(([name, fn]) => ({ name, description: fn.description || "" })),
    step: state.stepCount,
    maxSteps: state.maxSteps,
    errors: state.errors.slice(-3),
    toolResults: state.toolResults.slice(-5),
  };
}

function normalizeDecision(decision) {
  // Converge model output into a decision format the runtime can handle.
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
  // Execute the tool call requested by the model and wrap success or failure as an Observation.
  const toolName = decision.tool_name;
  const args = decision.arguments || {};
  if (!tools[toolName]) {
    return {
      status: "error",
      summary: `Tool does not exist: ${toolName}`,
      content: null,
      error: { code: "tool_not_found", message: `Tool does not exist: ${toolName}` },
    };
  }
  if (!args || typeof args !== "object" || Array.isArray(args)) {
    return {
      status: "error",
      summary: "Tool arguments must be a JSON object",
      content: null,
      error: { code: "invalid_arguments", message: "Tool arguments must be a JSON object" },
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
  // Write this turn's decision and Observation back to State for later loop iterations.
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
  // Check hard stopping conditions such as maximum steps, error count, and repeated actions.
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
  // Detect whether the agent repeats the same tool call without making progress.
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
    stopReason: state.stopReason,
  };
}

function stateSnapshot(state) {
  // Build a full State snapshot after the current step so the example can print each step.
  return {
    userGoal: state.userGoal,
    maxSteps: state.maxSteps,
    stepCount: state.stepCount,
    history: structuredClone(state.history),
    toolResults: structuredClone(state.toolResults),
    errors: structuredClone(state.errors),
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
