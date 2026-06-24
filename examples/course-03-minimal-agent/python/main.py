"""Python 版最小 Agent 闭环的命令行入口。

这个文件把课程三的几个构件串起来：Prompt 来自 ``minimal_agent.prompt``，
决策来自脚本化或真实 LLM 适配器，工具是本地函数，``run_agent`` 负责状态更新
和循环控制。
"""

import argparse
import json
from pathlib import Path

from minimal_agent.agent import run_agent
from minimal_agent.llm import ScriptedLLM, deepseek_chat_llm, random_demo_latency_seconds
from minimal_agent.tools import build_tools


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the course 03 minimal agent loop example.")
    parser.add_argument("--goal", default="读取 data/notes.md，总结课程三最小 Agent 闭环，并写入 output/summary.md")
    parser.add_argument("--real-llm", action="store_true", help="Use DeepSeek Chat Completions API instead of the scripted demo LLM.")
    parser.add_argument("--max-steps", type=int, default=6)
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    llm_call = deepseek_chat_llm if args.real_llm else _demo_llm()

    result = run_agent(args.goal, tools=build_tools(root), llm_call=llm_call, max_steps=args.max_steps, logger=_print_event_log)
    _print_result(result)


def _print_result(result: dict) -> None:
    """打印单轮任务循环的结果和 Trace。"""

    print("STATUS:", result["status"])
    if result.get("answer"):
        print("ANSWER:", result["answer"])
    if result.get("reason"):
        print("REASON:", result["reason"])
    _print_trace_steps(result["trace"])


def _print_trace_steps(trace: list) -> None:
    """逐步打印 Trace；每一步都包含本次执行后的 State。"""
    print("\nTRACE STEPS:")
    for entry in trace:
        print("\n--- STEP %s ---" % entry["step"])
        print("DECISION:")
        print(json.dumps(entry["decision"], ensure_ascii=False, indent=2, default=str))
        if "observation" in entry:
            print("OBSERVATION:")
            print(json.dumps(entry["observation"], ensure_ascii=False, indent=2, default=str))
        print("STATE:")
        print(json.dumps(entry["state_snapshot"], ensure_ascii=False, indent=2, default=str))
        print("STOP_CHECK:")
        print(json.dumps(entry["stop_check"], ensure_ascii=False, indent=2, default=str))


def _print_event_log(event: dict) -> None:
    """实时打印 Runtime 事件：LLM 决策、工具调用、工具结果和状态变化。"""
    event_type = event["event"]
    step = event["step"]
    if event_type == "llm_decision":
        print("[LOG][step %s] LLM_DECISION %s" % (step, json.dumps(event["decision"], ensure_ascii=False, default=str)))
    elif event_type == "tool_call":
        print(
            "[LOG][step %s] TOOL_CALL %s %s"
            % (step, event["tool_name"], json.dumps(event["arguments"], ensure_ascii=False, default=str))
        )
    elif event_type == "tool_result":
        print(
            "[LOG][step %s] TOOL_RESULT %s"
            % (step, json.dumps(event["observation"], ensure_ascii=False, default=str))
        )
    elif event_type == "state_update":
        state = event["state"]
        print(
            "[LOG][step %s] STATE_UPDATE step_count=%s history=%s errors=%s stop_reason=%s"
            % (step, state["step_count"], len(state["history"]), len(state["errors"]), state["stop_reason"])
        )
    elif event_type == "stop_check":
        print("[LOG][step %s] STOP_CHECK continue=%s reason=%s" % (step, event["continue"], event["reason"]))


def _demo_llm() -> ScriptedLLM:
    """返回固定决策序列，便于离线学习和测试。"""
    return ScriptedLLM(
        [
            {
                "type": "call_tool",
                "thought": "先读取课程三示例资料。",
                "tool_name": "read_file",
                "arguments": {"path": "data/notes.md"},
            },
            {
                "type": "call_tool",
                "thought": "将摘要写入交付文件。",
                "tool_name": "write_file",
                "arguments": {
                    "path": "output/summary.md",
                    "content": "最小 Agent 闭环包含 Prompt、LLM 决策、工具交互、State 状态管理和循环控制。Runtime 负责组装上下文、执行工具、记录 Observation、更新 State，并判断是否继续。",
                },
            },
            {"type": "final_answer", "thought": "摘要文件已经写入。", "answer": "已生成 output/summary.md。"},
        ],
        delay_seconds=random_demo_latency_seconds,
    )


if __name__ == "__main__":
    main()
