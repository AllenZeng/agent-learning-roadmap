"""课程三最小 Agent 的 Runtime 主循环。

LLM 只负责提出结构化决策。本模块负责确定性的运行时职责：组装上下文、分发工具、
记录 Observation、更新 State、收集 Trace，以及检查停止条件。
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from minimal_agent.prompt import SYSTEM_PROMPT


Decision = Dict[str, Any]
Observation = Dict[str, Any]
LLMCall = Callable[[Dict[str, Any]], Decision]


@dataclass
class AgentState:
    """Runtime 持有的单次任务状态。"""

    user_goal: str
    max_steps: int = 8
    step_count: int = 0
    history: List[Dict[str, Any]] = field(default_factory=list)
    tool_results: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Observation] = field(default_factory=list)
    stop_reason: Optional[str] = None
    final_answer: Optional[str] = None

    def recent_history(self, n: int = 5) -> List[Dict[str, Any]]:
        return self.history[-n:]


def run_agent(
    user_goal: str,
    tools: Dict[str, Callable[..., Observation]],
    llm_call: LLMCall,
    system_prompt: str = SYSTEM_PROMPT,
    max_steps: int = 8,
) -> Dict[str, Any]:
    """运行 ReAct 风格循环，直到任务完成、暂停、失败或被硬约束停止。"""
    state = AgentState(user_goal=user_goal, max_steps=max_steps)
    trace: List[Dict[str, Any]] = []

    while not state.stop_reason:
        # Context Assembly：只把本轮决策需要的状态切片交给 LLM。
        context = assemble_context(system_prompt, tools, state)
        decision = _normalize_decision(llm_call(context))
        trace_entry = {"step": state.step_count, "context_summary": _context_summary(context), "decision": decision}

        decision_type = decision["type"]
        if decision_type == "final_answer":
            state.stop_reason = "completed"
            state.final_answer = decision.get("answer", "")
            trace_entry["state_update"] = _state_summary(state)
            trace_entry["stop_check"] = {"continue": False, "reason": state.stop_reason}
            trace.append(trace_entry)
            return {"status": "success", "answer": state.final_answer, "state": state, "trace": trace}

        if decision_type == "ask_user":
            state.stop_reason = "need_user_input"
            trace_entry["state_update"] = _state_summary(state)
            trace_entry["stop_check"] = {"continue": False, "reason": state.stop_reason}
            trace.append(trace_entry)
            return {"status": "paused", "question": decision.get("question", ""), "state": state, "trace": trace}

        if decision_type == "fail":
            state.stop_reason = "failed"
            trace_entry["state_update"] = _state_summary(state)
            trace_entry["stop_check"] = {"continue": False, "reason": state.stop_reason}
            trace.append(trace_entry)
            return {"status": "failed", "reason": decision.get("reason", ""), "state": state, "trace": trace}

        # Interaction / Observation：Runtime 执行工具，并把结果统一成 Observation。
        observation = _execute_tool(decision, tools)
        _update_state_from_tool_call(state, decision, observation)
        trace_entry["observation"] = observation

        state.step_count += 1
        # Continue or Stop：停止条件由 Runtime 判断，不依赖模型自觉。
        stop_reason = _check_stop(state)
        if stop_reason:
            state.stop_reason = stop_reason

        trace_entry["state_update"] = _state_summary(state)
        trace_entry["stop_check"] = {"continue": not state.stop_reason, "reason": state.stop_reason}
        trace.append(trace_entry)

    return {"status": "stopped", "reason": state.stop_reason, "state": state, "trace": trace}


def assemble_context(system_prompt: str, tools: Dict[str, Callable[..., Observation]], state: AgentState) -> Dict[str, Any]:
    """选择哪些状态切片应该进入下一次 LLM 调用。"""
    return {
        "system": system_prompt,
        "goal": state.user_goal,
        "history": state.recent_history(n=5),
        "tools": [{"name": name, "description": fn.__doc__ or ""} for name, fn in tools.items()],
        "step": state.step_count,
        "max_steps": state.max_steps,
        "errors": state.errors[-3:],
        "tool_results": state.tool_results[-5:],
    }


def _normalize_decision(decision: Decision) -> Decision:
    """把模型输出收敛到 Runtime 能处理的决策格式。"""
    if not isinstance(decision, dict):
        return {"type": "fail", "thought": "Model output was not a JSON object.", "reason": "invalid_decision"}
    if decision.get("type") not in ("call_tool", "final_answer", "ask_user", "fail"):
        return {"type": "fail", "thought": "Model output had an unsupported type.", "reason": "invalid_decision_type"}
    if decision["type"] == "call_tool":
        decision.setdefault("arguments", {})
    return decision


def _execute_tool(decision: Decision, tools: Dict[str, Callable[..., Observation]]) -> Observation:
    """执行模型请求的工具调用，并把成功或失败都包装成 Observation。"""
    tool_name = decision.get("tool_name")
    arguments = decision.get("arguments", {})
    if tool_name not in tools:
        return {
            "status": "error",
            "summary": "工具不存在: %s" % tool_name,
            "content": None,
            "error": {"code": "tool_not_found", "message": "工具不存在: %s" % tool_name},
        }
    if not isinstance(arguments, dict):
        return {
            "status": "error",
            "summary": "工具参数必须是 JSON object",
            "content": None,
            "error": {"code": "invalid_arguments", "message": "工具参数必须是 JSON object"},
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
    """把本轮决策和 Observation 写回 State，供后续循环使用。"""
    state.history.append({"step": state.step_count, "decision": decision, "observation": observation})
    state.tool_results.append(
        {"tool": decision.get("tool_name"), "status": observation["status"], "summary": observation["summary"]}
    )
    if observation["status"] == "error":
        state.errors.append(observation)


def _check_stop(state: AgentState) -> Optional[str]:
    """检查最大步数、错误次数和重复动作等硬停止条件。"""
    if state.step_count >= state.max_steps:
        return "max_steps_exceeded"
    if len(state.errors) >= 3:
        return "tool_error_limit"
    if _repeated_action(state, threshold=3):
        return "repeated_action"
    return None


def _repeated_action(state: AgentState, threshold: int = 3) -> bool:
    """检测 Agent 是否连续重复相同工具调用而没有推进。"""
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
