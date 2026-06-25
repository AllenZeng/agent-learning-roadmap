import unittest

from patterns.plan_execute import PlanExecuteExecutor


class PlanExecuteExecutorTest(unittest.TestCase):
    def test_waits_for_confirmation_without_executing_steps(self):
        executor = PlanExecuteExecutor()

        result = executor.execute(
            goal="准备 v1.2.0 版本发布",
            auto_confirm=False,
        )

        self.assertEqual(result.status, "waiting_confirmation")
        self.assertIsNotNone(result.plan)
        self.assertEqual(result.results, [])
        self.assertIn("等待用户确认", result.error)

    def test_stops_when_replan_limit_is_reached(self):
        executor = PlanExecuteExecutor(max_replan_count=0)

        result = executor.execute(
            goal="准备 v1.2.0 版本发布",
            inject_failures={"运行测试": True},
        )

        self.assertEqual(result.status, "failed")
        self.assertEqual(result.replan_count, 0)
        self.assertIn("达到最大重规划次数", result.error)


if __name__ == "__main__":
    unittest.main()
