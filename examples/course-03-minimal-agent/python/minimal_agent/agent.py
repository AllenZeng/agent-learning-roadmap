"""Runtime main loop for the course 03 minimal Agent.

The LLM only proposes structured decisions. This module owns deterministic runtime duties: assembling context, dispatching tools,
recording Observations, updating State, collecting Trace, and checking stop conditions.
"""

from dataclasses import dataclass, field
from copy import deepcopy
from typing import Any, Callable, Dict, List, Optional

from minimal_agent.prompt import SYSTEM_PROMPT


Decision = Dict[str, Any]
Observation = Dict[str, Any]
LLMCall = Callable[[Dict[str, Any]], Decision]
Logger = Callable[[Dict[str, Any]], None]


@dataclass
class AgentState:
    """Single-task state held by the runtime.

    ``step_count`` increments only on tool-call steps; final_answer / ask_user /
    fail and other terminal decisions do not count as steps, so trace length may be
    one greater than step_count because it includes the terminal decision record.
    """

    user_goal: str
    max_steps: int = 8
    step_count: int = 0
    history: List[Dict[str, Any]] = field(default_factory=list)
    tool_results: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Observation] = field(default_factory=list)
    stop_reason: Optional[str] = None
    final_answer: Optional[str] = None
    max_tool_errors: int = 5

    def recent_history(self, n: int = 5) -> List[Dict[str, Any]]:
        return self.history[-n:]


def run_agent(
    user_goal: str,
    tools: Dict[str, Callable[..., Observation]],
    llm_call: LLMCall,
    system_prompt: str = SYSTEM_PROMPT,
    max_steps: int = 8,
    conversation: Optional[List[Dict[str, str]]] = None,
    logger: Optional[Logger] = None,
) -> Dict[str, Any]:
    """Run a ReAct-style loop until the task is complete, paused, failed, or stopped by hard constraints."""
    state = AgentState(user_goal=user_goal, max_steps=max_steps)
    trace: List[Dict[str, Any]] = []

    # 0. Start the loop
    while not state.stop_reason:
        # 1. Context Assembly: pass only the state slices needed for this decision to the LLM.
        context = assemble_context(system_prompt, tools, state, conversation=conversation or [])
        # 2. Call the LLM for a decision and normalize the output
        decision = _normalize_decision(llm_call(context))
        _log(logger, {"event": "llm_decision", "step": state.step_count, "decision": decision})
        trace_entry = {"step": state.step_count, "context_summary": _context_summary(context), "decision": decision}

        # 3. Inspect the decision result and decide whether to stop the loop
        decision_type = decision["type"]
        if decision_type == "final_answer":
            state.stop_reason = "completed"
            state.final_answer = decision.get("answer", "")
            return _finalize(state, trace_entry, trace, logger, "success", answer=state.final_answer)

        if decision_type == "ask_user":
            state.stop_reason = "need_user_input"
            return _finalize(state, trace_entry, trace, logger, "paused", question=decision.get("question", ""))

        if decision_type == "fail":
            state.stop_reason = "failed"
            return _finalize(state, trace_entry, trace, logger, "failed", reason=decision.get("reason", ""))

        # 4. If the decision requires a tool call, execute it
        # Interaction / Observation: the runtime executes tools and normalizes results into Observations.
        _log(
            logger,
            {
                "event": "tool_call",
                "step": state.step_count,
                "tool_name": decision.get("tool_name"),
                "arguments": decision.get("arguments", {}),
            },
        )
        observation = _execute_tool(decision, tools)
        _log(logger, {"event": "tool_result", "step": state.step_count, "observation": observation})

        # 5. Normalize the tool-call result and write it into state
        _update_state_from_tool_call(state, decision, observation)
        trace_entry["observation"] = observation

        # 6. Update state and decide whether to enter the next loop iteration
        state.step_count += 1
        # Continue or Stop: the runtime owns stopping conditions instead of relying on the model to stop itself.
        stop_reason = _check_stop(state)
        if stop_reason:
            state.stop_reason = stop_reason

        trace_entry["state_update"] = _state_summary(state)
        trace_entry["state_snapshot"] = _state_snapshot(state)
        trace_entry["stop_check"] = {"continue": not state.stop_reason, "reason": state.stop_reason}
        _log(logger, {"event": "state_update", "step": state.step_count, "state": trace_entry["state_snapshot"]})
        _log(
            logger,
            {
                "event": "stop_check",
                "step": state.step_count,
                "continue": not state.stop_reason,
                "reason": state.stop_reason,
            },
        )
        trace.append(trace_entry)
        # 7. Continue to the next loop iteration

    return {"status": "stopped", "reason": state.stop_reason, "state": state, "trace": trace}


def assemble_context(
    system_prompt: str,
    tools: Dict[str, Callable[..., Observation]],
    state: AgentState,
    conversation: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """Choose which state slices should enter the next LLM call."""
    return {
        "system": system_prompt,
        "goal": state.user_goal,
        "conversation": conversation or [],
        "history": state.recent_history(n=5),
        "tools": [{"name": name, "description": fn.__doc__ or ""} for name, fn in tools.items()],
        "step": state.step_count,
        "max_steps": state.max_steps,
        "errors": state.errors[-3:],
        "tool_results": state.tool_results[-5:],
    }


def _normalize_decision(decision: Decision) -> Decision:
    """Converge model output into a decision format the runtime can handle."""
    if not isinstance(decision, dict):
        return {"type": "fail", "thought": "Model output was not a JSON object.", "reason": "invalid_decision"}
    if decision.get("type") not in ("call_tool", "final_answer", "ask_user", "fail"):
        return {"type": "fail", "thought": "Model output had an unsupported type.", "reason": "invalid_decision_type"}
    if decision["type"] == "call_tool":
        decision.setdefault("arguments", {})
    return decision


def _execute_tool(decision: Decision, tools: Dict[str, Callable[..., Observation]]) -> Observation:
    """Execute the tool call requested by the model and wrap success or failure as an Observation."""
    tool_name = decision.get("tool_name")
    arguments = decision.get("arguments", {})
    if tool_name not in tools:
        return {
            "status": "error",
            "summary": "Tool does not exist: %s" % tool_name,
            "content": None,
            "error": {"code": "tool_not_found", "message": "Tool does not exist: %s" % tool_name},
        }
    if not isinstance(arguments, dict):
        return {
            "status": "error",
            "summary": "Tool arguments must be a JSON object",
            "content": None,
            "error": {"code": "invalid_arguments", "message": "Tool arguments must be a JSON object"},
        }
    try:
        observation = tools[tool_name](**arguments)
    except TypeError as exc:
        observation = {
            "status": "error",
            "summary": str(exc),
            "content": None,
            "error": {"code": "invalid_arguments", "message": str(exc)},
        }
    except Exception as exc:
        observation = {
            "status": "error",
            "summary": str(exc),
            "content": None,
            "error": {"code": type(exc).__name__, "message": str(exc)},
        }
    return observation


def _update_state_from_tool_call(state: AgentState, decision: Decision, observation: Observation) -> None:
    """Write this turn's decision and Observation back to State for later loop iterations."""
    state.history.append({"step": state.step_count, "decision": decision, "observation": observation})
    state.tool_results.append(
        {"tool": decision.get("tool_name"), "status": observation["status"], "summary": observation["summary"]}
    )
    if observation["status"] == "error":
        state.errors.append(observation)


def _finalize(
    state: AgentState,
    trace_entry: Dict[str, Any],
    trace: List[Dict[str, Any]],
    logger: Optional[Logger],
    status: str,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Record the final state snapshot and stop check, then return a normalized result structure."""
    trace_entry["state_update"] = _state_summary(state)
    trace_entry["state_snapshot"] = _state_snapshot(state)
    trace_entry["stop_check"] = {"continue": False, "reason": state.stop_reason}
    _log(logger, {"event": "state_update", "step": state.step_count, "state": trace_entry["state_snapshot"]})
    _log(logger, {"event": "stop_check", "step": state.step_count, "continue": False, "reason": state.stop_reason})
    trace.append(trace_entry)
    return {"status": status, "state": state, "trace": trace, **kwargs}


def _check_stop(state: AgentState) -> Optional[str]:
    """Check hard stopping conditions such as maximum steps, error count, and repeated actions."""
    if state.step_count >= state.max_steps:
        return "max_steps_exceeded"
    if len(state.errors) >= state.max_tool_errors:
        return "tool_error_limit"
    if _repeated_action(state, threshold=3):
        return "repeated_action"
    return None


def _repeated_action(state: AgentState, threshold: int = 3) -> bool:
    """Detect whether the agent repeats the same tool call without making progress."""
    recent = state.history[-threshold:]
    if len(recent) < threshold:
        return False
    signatures = []
    for item in recent:
        decision = item["decision"]
        if decision.get("type") != "call_tool":
            return False
        signatures.append((decision.get("tool_name"), repr(sorted(decision.get("arguments", {}).items()))))
    return len(set(signatures)) == 1


def _context_summary(context: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "goal": context["goal"],
        "conversation_count": len(context["conversation"]),
        "step": context["step"],
        "history_count": len(context["history"]),
        "error_count": len(context["errors"]),
        "tools": [tool["name"] for tool in context["tools"]],
    }


def _state_summary(state: AgentState) -> Dict[str, Any]:
    return {
        "step_count": state.step_count,
        "history_count": len(state.history),
        "errors_count": len(state.errors),
        "stop_reason": state.stop_reason,
    }


def _state_snapshot(state: AgentState) -> Dict[str, Any]:
    """Build a full State snapshot after the current step so the example can print each step."""
    return {
        "user_goal": state.user_goal,
        "max_steps": state.max_steps,
        "step_count": state.step_count,
        "history": deepcopy(state.history),
        "tool_results": deepcopy(state.tool_results),
        "errors": deepcopy(state.errors),
        "stop_reason": state.stop_reason,
        "final_answer": state.final_answer,
    }


def _log(logger: Optional[Logger], event: Dict[str, Any]) -> None:
    if logger is not None:
        logger(event)
