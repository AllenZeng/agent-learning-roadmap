import unittest

from multi_agent_demo import (
    AgentConfig,
    CheckItem,
    ReviewerPattern,
    DemoExecutorAgent,
    DemoReviewerAgent,
    count_agent_differences,
)


class MultiAgentDemoTest(unittest.TestCase):
    def setUp(self):
        self.criteria = [
            CheckItem(
                id="C1",
                check="输入长度限制",
                how_to_verify="检查 /api/data 的 input 参数是否声明 max_length",
                severity="must_fix",
            ),
            CheckItem(
                id="C2",
                check="密钥管理",
                how_to_verify="检查配置示例是否使用环境变量而不是明文 key",
                severity="must_fix",
            ),
            CheckItem(
                id="C3",
                check="权限模型",
                how_to_verify="检查是否区分 reader 和 writer 角色",
                severity="must_fix",
            ),
            CheckItem(
                id="C4",
                check="依赖锁定",
                how_to_verify="检查依赖是否使用 == 锁定版本",
                severity="should_fix",
            ),
        ]

    def test_agent_configs_have_at_least_two_real_differences(self):
        executor = AgentConfig(
            name="Executor",
            inputs={"requirement", "retrieved_notes", "draft_trace"},
            tools={"search_notes", "write_file"},
            goal="完成技术方案",
            acceptance="方案覆盖业务需求",
        )
        reviewer = AgentConfig(
            name="Reviewer",
            inputs={"final_artifact", "security_criteria"},
            tools={"read_file", "run_checklist"},
            goal="找出安全问题",
            acceptance="审查清单逐条通过",
        )

        differences = count_agent_differences(executor, reviewer)

        self.assertGreaterEqual(differences["total"], 2)
        self.assertTrue(differences["inputs"])
        self.assertTrue(differences["tools"])
        self.assertTrue(differences["goal"])
        self.assertTrue(differences["acceptance"])

    def test_reviewer_finds_specific_issues_before_executor_fixes_them(self):
        executor = DemoExecutorAgent()
        reviewer = DemoReviewerAgent()
        pattern = ReviewerPattern(executor, reviewer, max_rounds=2)

        result = pattern.run("写一份 API 模块技术方案", self.criteria, verbose=False)

        self.assertEqual(result.status, "approved")
        self.assertEqual(result.review_rounds, 2)
        self.assertIn("max_length: 256", result.output)
        self.assertIn("${API_KEY}", result.output)
        self.assertEqual(len(result.review_trace[0].issues), 4)
        self.assertEqual(result.review_trace[0].issues[0].location, "api_schema.yaml:12")
        self.assertEqual(result.review_trace[1].verdict, "approved")

    def test_reviewer_never_receives_executor_private_trace(self):
        executor = DemoExecutorAgent()
        reviewer = DemoReviewerAgent()
        pattern = ReviewerPattern(executor, reviewer, max_rounds=2)

        pattern.run("写一份 API 模块技术方案", self.criteria, verbose=False)

        self.assertEqual(reviewer.seen_private_traces, [])
        self.assertEqual(reviewer.review_requests[0].executor_private_trace, None)

    def test_unresolved_issues_stop_as_disputed_after_max_rounds(self):
        executor = DemoExecutorAgent(fixable_issue_ids={"C1"})
        reviewer = DemoReviewerAgent()
        pattern = ReviewerPattern(executor, reviewer, max_rounds=2)

        result = pattern.run("写一份 API 模块技术方案", self.criteria, verbose=False)

        self.assertEqual(result.status, "disputed")
        self.assertEqual(result.review_rounds, 2)
        self.assertIn("C2", [issue.id for issue in result.unresolved_issues])
        self.assertEqual(result.reason, "max_review_rounds")


if __name__ == "__main__":
    unittest.main()
