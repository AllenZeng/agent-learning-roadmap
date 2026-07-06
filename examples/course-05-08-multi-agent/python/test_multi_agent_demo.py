import unittest

from multi_agent_demo import (
    AgentConfig,
    DemoExecutorAgent,
    DemoReviewerAgent,
    DemoSupervisorAgent,
    MockLLM,
    ParallelSpecialists,
    ReviewerPattern,
    SupervisorPattern,
    count_agent_differences,
    default_agent_prompts,
    default_criteria,
    default_dimensions,
    default_specialists,
    default_workers,
)


class ReviewerPatternTest(unittest.TestCase):
    def test_default_agent_prompts_define_roles_and_response_contracts(self):
        prompts = default_agent_prompts()

        self.assertIn("Executor Agent", prompts["executor"].system_prompt)
        self.assertIn("Reviewer Agent", prompts["reviewer"].system_prompt)
        self.assertIn("ReviewResponse", prompts["reviewer"].response_contract)
        self.assertIn("不要读取 Executor private_trace", prompts["reviewer"].must_not)

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

        self.assertEqual(differences["total"], 4)
        self.assertTrue(differences["inputs"])
        self.assertTrue(differences["tools"])
        self.assertTrue(differences["goal"])
        self.assertTrue(differences["acceptance"])

    def test_reviewer_finds_specific_issues_before_executor_fixes_them(self):
        result = ReviewerPattern(DemoExecutorAgent(), DemoReviewerAgent()).run(
            "写一份 API 模块技术方案", default_criteria(), verbose=False
        )

        self.assertEqual(result.status, "approved")
        self.assertEqual(result.review_rounds, 2)
        self.assertIn("max_length: 256", result.output)
        self.assertIn("${API_KEY}", result.output)
        self.assertEqual(len(result.review_trace[0].issues), 4)
        self.assertEqual(result.review_trace[0].issues[0].location, "api_schema.yaml:12")
        self.assertEqual(result.review_trace[1].verdict, "approved")

    def test_reviewer_pattern_records_mock_llm_calls_with_role_prompts(self):
        llm = MockLLM()
        result = ReviewerPattern(
            DemoExecutorAgent(llm=llm),
            DemoReviewerAgent(llm=llm),
        ).run("写一份 API 模块技术方案", default_criteria(), verbose=False)

        self.assertEqual(result.status, "approved")
        self.assertEqual([call.agent for call in llm.calls], ["executor", "reviewer", "executor", "reviewer"])
        self.assertIn("Executor Agent", llm.calls[0].system_prompt)
        self.assertIn("Reviewer Agent", llm.calls[1].system_prompt)
        self.assertNotIn("private_trace", llm.calls[1].user_payload)

    def test_reviewer_never_receives_executor_private_trace(self):
        reviewer = DemoReviewerAgent()
        ReviewerPattern(DemoExecutorAgent(), reviewer).run(
            "写一份 API 模块技术方案", default_criteria(), verbose=False
        )

        self.assertEqual(reviewer.seen_private_traces, [])
        self.assertIsNone(reviewer.review_requests[0].executor_private_trace)

    def test_unresolved_issues_stop_as_disputed_after_max_rounds(self):
        result = ReviewerPattern(
            DemoExecutorAgent(fixable_issue_ids={"C1"}), DemoReviewerAgent(), max_rounds=2
        ).run("写一份 API 模块技术方案", default_criteria(), verbose=False)

        self.assertEqual(result.status, "disputed")
        self.assertEqual(result.review_rounds, 2)
        self.assertEqual([issue.id for issue in result.unresolved_issues], ["C2", "C3", "C4"])
        self.assertEqual(result.reason, "max_review_rounds")


class SupervisorPatternTest(unittest.TestCase):
    def test_supervisor_decomposes_into_bounded_subtasks_with_excludes(self):
        result = SupervisorPattern(DemoSupervisorAgent(), default_workers()).run(
            "调研 Agent 架构的四个主流方向", verbose=False
        )

        self.assertEqual(result.status, "complete")
        self.assertEqual(len(result.plan.subtasks), 4)
        self.assertTrue(all(subtask.exclude for subtask in result.plan.subtasks))
        self.assertTrue(all(subtask.output_fields == ("key_findings", "risks", "recommendations") for subtask in result.plan.subtasks))
        self.assertIn("## Tool Use", result.final_report)
        self.assertIn("## Multi-Agent", result.final_report)

    def test_supervisor_marks_worker_failure_as_missing_instead_of_hiding_it(self):
        result = SupervisorPattern(
            DemoSupervisorAgent(), default_workers(failing_worker="memory_worker")
        ).run("调研 Agent 架构的四个主流方向", verbose=False)

        self.assertEqual(result.status, "partial")
        self.assertEqual(result.missing_topics, ["Memory"])
        self.assertIn("数据缺失: worker_timeout", result.final_report)


class ParallelSpecialistsTest(unittest.TestCase):
    def test_parallel_specialists_deduplicate_same_location_and_problem_type(self):
        result = ParallelSpecialists(default_specialists()).run(
            "checkout.py 代码片段", default_dimensions(), verbose=False
        )

        amount_findings = [
            finding
            for finding in result.findings
            if finding.location == "checkout.py:18" and finding.problem_type == "missing_validation"
        ]
        self.assertEqual(len(amount_findings), 1)
        self.assertEqual(amount_findings[0].dimensions, ["correctness", "security"])
        self.assertEqual(amount_findings[0].severity, "must_fix")

    def test_parallel_specialists_preserve_conflicts_for_human_review(self):
        result = ParallelSpecialists(default_specialists()).run(
            "checkout.py 代码片段", default_dimensions(), verbose=False
        )

        self.assertEqual(len(result.conflicts), 1)
        self.assertEqual(result.conflicts[0].location, "checkout.py:55")
        self.assertEqual(result.conflicts[0].problem_type, "idempotency")
        self.assertEqual(result.conflicts[0].judgments, ["problem", "safe"])
        self.assertEqual(result.dimension_summary, {"correctness": 2, "security": 3, "performance": 2})


if __name__ == "__main__":
    unittest.main()
