import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from minimal_agent.agent import AgentState, SessionState, run_agent, run_turn
from minimal_agent.llm import ScriptedLLM
from minimal_agent.tools import build_tools


class MinimalAgentLoopTests(unittest.TestCase):
    def test_runs_multi_step_loop_and_writes_final_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            (workspace / "notes.md").write_text(
                "# Notes\n\nAgent = Prompt + LLM Decision + Tools + State + Loop Control.\n",
                encoding="utf-8",
            )

            llm = ScriptedLLM(
                [
                    {
                        "type": "call_tool",
                        "thought": "Need to read the source notes first.",
                        "tool_name": "read_file",
                        "arguments": {"path": "notes.md"},
                    },
                    {
                        "type": "call_tool",
                        "thought": "Need to persist a short summary.",
                        "tool_name": "write_file",
                        "arguments": {
                            "path": "summary.md",
                            "content": "Agent 最小闭环由 Prompt、LLM 决策、工具交互、State 和循环控制组成。",
                        },
                    },
                    {
                        "type": "final_answer",
                        "thought": "The requested summary has been written.",
                        "answer": "已写入 summary.md。",
                    },
                ]
            )

            result = run_agent(
                user_goal="读取 notes.md，总结后写入 summary.md",
                tools=build_tools(workspace),
                llm_call=llm,
                max_steps=5,
            )

            self.assertEqual(result["status"], "success")
            self.assertEqual(result["state"].stop_reason, "completed")
            self.assertEqual(result["state"].step_count, 2)
            self.assertEqual(len(result["trace"]), 3)
            self.assertEqual(result["trace"][0]["state_snapshot"]["step_count"], 1)
            self.assertEqual(len(result["trace"][0]["state_snapshot"]["history"]), 1)
            self.assertEqual(result["trace"][1]["state_snapshot"]["tool_results"][1]["tool"], "write_file")
            self.assertEqual(result["trace"][2]["state_snapshot"]["stop_reason"], "completed")
            self.assertIn("Prompt、LLM 决策", (workspace / "summary.md").read_text(encoding="utf-8"))

    def test_records_tool_errors_in_state(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            llm = ScriptedLLM(
                [
                    {
                        "type": "call_tool",
                        "thought": "Try reading the requested file.",
                        "tool_name": "read_file",
                        "arguments": {"path": "missing.md"},
                    },
                    {
                        "type": "fail",
                        "thought": "The file is not available.",
                        "reason": "missing input file",
                    },
                ]
            )

            result = run_agent(
                user_goal="读取 missing.md",
                tools=build_tools(workspace),
                llm_call=llm,
                max_steps=5,
            )

            state = result["state"]
            self.assertEqual(result["status"], "failed")
            self.assertEqual(state.stop_reason, "failed")
            self.assertEqual(len(state.errors), 1)
            self.assertEqual(state.errors[0]["error"]["code"], "file_not_found")
            self.assertEqual(state.tool_results[0]["status"], "error")

    def test_stops_when_same_tool_action_repeats(self):
        llm = ScriptedLLM(
            [
                {
                    "type": "call_tool",
                    "thought": "Search again.",
                    "tool_name": "search_text",
                    "arguments": {"query": "agent", "text": "agent loop"},
                },
                {
                    "type": "call_tool",
                    "thought": "Search again.",
                    "tool_name": "search_text",
                    "arguments": {"query": "agent", "text": "agent loop"},
                },
                {
                    "type": "call_tool",
                    "thought": "Search again.",
                    "tool_name": "search_text",
                    "arguments": {"query": "agent", "text": "agent loop"},
                },
            ]
        )

        result = run_agent(
            user_goal="不断搜索相同内容",
            tools=build_tools(ROOT),
            llm_call=llm,
            max_steps=8,
        )

        self.assertEqual(result["status"], "stopped")
        self.assertEqual(result["state"].stop_reason, "repeated_action")

    def test_state_recent_history_returns_tail(self):
        state = AgentState(user_goal="demo")
        state.history = [{"step": index} for index in range(8)]

        self.assertEqual(state.recent_history(3), [{"step": 5}, {"step": 6}, {"step": 7}])

    def test_session_keeps_multi_turn_conversation_history(self):
        session = SessionState()
        llm = ScriptedLLM(
            [
                {
                    "type": "final_answer",
                    "thought": "Answer the first turn.",
                    "answer": "第一轮回答。",
                },
                {
                    "type": "final_answer",
                    "thought": "Answer with the previous turn in context.",
                    "answer": "第二轮回答，已看到上一轮。",
                },
            ]
        )

        first = run_turn(
            session=session,
            user_message="第一轮：介绍最小 Agent。",
            tools=build_tools(ROOT),
            llm_call=llm,
        )
        second = run_turn(
            session=session,
            user_message="第二轮：基于上一轮再补充 State。",
            tools=build_tools(ROOT),
            llm_call=llm,
        )

        self.assertEqual(first["status"], "success")
        self.assertEqual(second["status"], "success")
        self.assertEqual(len(session.messages), 4)
        self.assertEqual(session.messages[0]["role"], "user")
        self.assertEqual(session.messages[1]["role"], "assistant")
        self.assertEqual(session.messages[2]["content"], "第二轮：基于上一轮再补充 State。")
        self.assertEqual(session.turns[1]["answer"], "第二轮回答，已看到上一轮。")
        self.assertEqual(llm.calls[1]["conversation"][-3]["content"], "第一轮：介绍最小 Agent。")
        self.assertEqual(llm.calls[1]["conversation"][-2]["content"], "第一轮回答。")

    def test_scripted_llm_can_simulate_response_latency(self):
        delays = []
        llm = ScriptedLLM(
            [{"type": "final_answer", "thought": "done", "answer": "ok"}],
            delay_seconds=lambda: 1.5,
            sleep_fn=delays.append,
        )

        decision = llm({"goal": "demo"})

        self.assertEqual(decision["answer"], "ok")
        self.assertEqual(delays, [1.5])
        self.assertEqual(llm.calls[0]["simulated_latency_seconds"], 1.5)

    def test_runtime_emits_execution_logs(self):
        events = []
        llm = ScriptedLLM(
            [
                {
                    "type": "call_tool",
                    "thought": "Search once.",
                    "tool_name": "search_text",
                    "arguments": {"query": "Agent", "text": "Agent loop"},
                },
                {"type": "final_answer", "thought": "Done.", "answer": "ok"},
            ]
        )

        result = run_agent(
            user_goal="搜索 Agent",
            tools=build_tools(ROOT),
            llm_call=llm,
            logger=events.append,
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(
            [event["event"] for event in events],
            [
                "llm_decision",
                "tool_call",
                "tool_result",
                "state_update",
                "stop_check",
                "llm_decision",
                "state_update",
                "stop_check",
            ],
        )
        self.assertEqual(events[1]["tool_name"], "search_text")
        self.assertEqual(events[2]["observation"]["status"], "success")
        self.assertEqual(events[-1]["reason"], "completed")


if __name__ == "__main__":
    unittest.main()
