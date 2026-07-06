"""Command-line entry point for the Python minimal Agent loop.

This file wires together the course 03 components: Prompt comes from ``minimal_agent.prompt``,
decisions come from a scripted or real LLM adapter, tools are local functions, and ``run_agent`` owns state updates
and loop control.
"""

import argparse
import json
from pathlib import Path

from minimal_agent.agent import run_agent
from minimal_agent.llm import ScriptedLLM, deepseek_chat_llm, random_demo_latency_seconds
from minimal_agent.tools import build_tools


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the course 03 minimal agent loop example.")
    parser.add_argument("--goal", default="Read data/notes.md, summarize the course 03 minimal Agent loop, and write output/summary.md")
    parser.add_argument("--real-llm", action="store_true", help="Use DeepSeek Chat Completions API instead of the scripted demo LLM.")
    parser.add_argument("--max-steps", type=int, default=6)
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    llm_call = deepseek_chat_llm if args.real_llm else _demo_llm()

    result = run_agent(args.goal, tools=build_tools(root), llm_call=llm_call, max_steps=args.max_steps, logger=_print_event_log)
    _print_result(result)


def _print_result(result: dict) -> None:
    """Print the result and Trace for one task loop."""

    print("STATUS:", result["status"])
    if result.get("answer"):
        print("ANSWER:", result["answer"])
    if result.get("reason"):
        print("REASON:", result["reason"])
    _print_trace_steps(result["trace"])


def _print_trace_steps(trace: list) -> None:
    """Print Trace step by step; each step includes State after this execution."""
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
    """Print runtime events in real time: LLM decisions, tool calls, tool results, and state changes."""
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
    """Return a fixed decision sequence for offline learning and tests."""
    return ScriptedLLM(
        [
            {
                "type": "call_tool",
                "thought": "First read the course 03 example material.",
                "tool_name": "read_file",
                "arguments": {"path": "data/notes.md"},
            },
            {
                "type": "call_tool",
                "thought": "Write the summary to the deliverable file.",
                "tool_name": "write_file",
                "arguments": {
                    "path": "output/summary.md",
                    "content": "The minimal Agent loop includes Prompt, LLM decisions, tool interaction, State management, and loop control. The runtime assembles context, executes tools, records Observations, updates State, and decides whether to continue.",
                },
            },
            {"type": "final_answer", "thought": "The summary file has been written.", "answer": "Generated output/summary.md."},
        ],
        delay_seconds=random_demo_latency_seconds,
    )


if __name__ == "__main__":
    main()
