import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tool_agent.agent import run_agent
from tool_agent.llm import ScriptedLLM
from tool_agent.tools import PermissionPolicy, ToolDefinition, ToolRegistry, ToolResult, build_tool_registry, execute_tool_call


class ToolMechanismTests(unittest.TestCase):
    def test_tool_context_exposes_schema_risk_and_boundaries(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = build_tool_registry(Path(tmpdir))

            context_tools = registry.to_context_tools()
            read_file = next(tool for tool in context_tools if tool["name"] == "read_file")

            self.assertIn("本地文件", read_file["description"])
            self.assertIn("不要用于搜索互联网", read_file["description"])
            self.assertEqual(read_file["risk_level"], "low")
            self.assertTrue(read_file["idempotent"])
            self.assertEqual(read_file["parameters"]["required"], ["path"])
            self.assertEqual(read_file["parameters"]["properties"]["path"]["type"], "string")

    def test_execute_tool_call_validates_parameters_before_execution(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = build_tool_registry(Path(tmpdir))
            policy = PermissionPolicy(allowed_tools={"read_file"})
            audit_log = []

            observation = execute_tool_call(
                {"type": "call_tool", "tool_name": "read_file", "arguments": {}},
                registry=registry,
                permissions=policy,
                audit_log=audit_log,
            )

            self.assertEqual(observation["status"], "error")
            self.assertEqual(observation["error"]["code"], "missing_required")
            self.assertEqual(observation["error"]["retryable"], False)
            self.assertEqual(observation["error"]["suggested_action"], "请补充参数: path")
            self.assertEqual(audit_log[0]["stage"], "validation")
            self.assertEqual(audit_log[0]["result"], "denied")

    def test_execute_tool_call_rejects_missing_tool_name_before_lookup(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = build_tool_registry(Path(tmpdir))
            audit_log = []

            observation = execute_tool_call(
                {"type": "call_tool", "arguments": {}},
                registry=registry,
                permissions=PermissionPolicy(allowed_tools={"read_file"}),
                audit_log=audit_log,
            )

            self.assertEqual(observation["status"], "error")
            self.assertEqual(observation["error"]["code"], "missing_tool_name")
            self.assertEqual(observation["error"]["suggested_action"], "请从可用工具列表中选择一个 tool_name")
            self.assertEqual(audit_log[0]["tool_name"], "")
            self.assertEqual(audit_log[0]["stage"], "validation")

    def test_deny_first_permission_blocks_write_and_records_audit(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            registry = build_tool_registry(workspace)
            policy = PermissionPolicy(allowed_tools={"read_file"})
            audit_log = []

            observation = execute_tool_call(
                {
                    "type": "call_tool",
                    "tool_name": "write_file",
                    "arguments": {"path": "output.txt", "content": "hello"},
                },
                registry=registry,
                permissions=policy,
                audit_log=audit_log,
            )

            self.assertEqual(observation["status"], "error")
            self.assertEqual(observation["error"]["code"], "permission_denied")
            self.assertEqual(observation["error"]["needs_user"], True)
            self.assertFalse((workspace / "output.txt").exists())
            self.assertEqual(audit_log[-1]["stage"], "permission")
            self.assertEqual(audit_log[-1]["result"], "denied")

    def test_long_tool_result_is_truncated_for_observation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            (workspace / "long.md").write_text("A" * 2400, encoding="utf-8")
            registry = build_tool_registry(workspace, max_context_chars=400)
            policy = PermissionPolicy(allowed_tools={"read_file"})

            observation = execute_tool_call(
                {"type": "call_tool", "tool_name": "read_file", "arguments": {"path": "long.md"}},
                registry=registry,
                permissions=policy,
            )

            self.assertEqual(observation["status"], "success")
            self.assertEqual(observation["content_truncated"], True)
            self.assertEqual(observation["full_content_ref"], "long.md")
            self.assertLess(len(observation["preview"]), 500)
            self.assertNotIn("content", observation)

    def test_idempotent_tools_can_retry_transient_failures(self):
        attempts = []

        def flaky_lookup(query):
            attempts.append(query)
            if len(attempts) == 1:
                raise TimeoutError("temporary timeout")
            return ToolResult.success("查询成功", {"query": query}).to_dict()

        registry = ToolRegistry(
            [
                ToolDefinition(
                    name="lookup_notes",
                    description="Lookup notes by query.",
                    parameters={
                        "type": "object",
                        "properties": {"query": {"type": "string"}},
                        "required": ["query"],
                    },
                    handler=flaky_lookup,
                    risk_level="low",
                    idempotent=True,
                    max_retries=1,
                )
            ]
        )

        observation = execute_tool_call(
            {"type": "call_tool", "tool_name": "lookup_notes", "arguments": {"query": "agent"}},
            registry=registry,
            permissions=PermissionPolicy(allowed_tools={"lookup_notes"}),
        )

        self.assertEqual(observation["status"], "success")
        self.assertEqual(observation["retry_count"], 1)
        self.assertEqual(len(attempts), 2)

    def test_agent_loop_uses_tool_executor_and_audit_log(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            (workspace / "notes.md").write_text("Agent tools need schemas and permissions.", encoding="utf-8")
            registry = build_tool_registry(workspace)
            policy = PermissionPolicy(allowed_tools={"read_file", "write_file"})
            llm = ScriptedLLM(
                [
                    {
                        "type": "call_tool",
                        "thought": "Need the source notes.",
                        "tool_name": "read_file",
                        "arguments": {"path": "notes.md"},
                    },
                    {
                        "type": "call_tool",
                        "thought": "Persist the summary.",
                        "tool_name": "write_file",
                        "arguments": {
                            "path": "summary.md",
                            "content": "工具机制需要 Schema、权限检查、审计和结构化 Observation。",
                        },
                    },
                    {"type": "final_answer", "thought": "Done.", "answer": "已写入 summary.md。"},
                ]
            )

            result = run_agent(
                "读取 notes.md，总结后写入 summary.md",
                registry=registry,
                permissions=policy,
                llm_call=llm,
            )

            self.assertEqual(result["status"], "success")
            self.assertTrue((workspace / "summary.md").exists())
            self.assertEqual(len(result["state"].audit_log), 2)
            self.assertEqual(result["state"].audit_log[0]["result"], "allowed")


if __name__ == "__main__":
    unittest.main()
