import unittest

from patterns.plan_execute import PlanExecuteExecutor


class PlanExecuteExecutorTest(unittest.TestCase):
    def test_waits_for_confirmation_without_executing_steps(self):
        executor = PlanExecuteExecutor()

        result = executor.execute(
            goal="Prepare the v1.2.0 release",
            auto_confirm=False,
        )

        self.assertEqual(result.status, "waiting_confirmation")
        self.assertIsNotNone(result.plan)
        self.assertEqual(result.results, [])
        self.assertIn("textuser confirmation", result.error)

    def test_stops_when_replan_limit_is_reached(self):
        executor = PlanExecuteExecutor(max_replan_count=0)

        result = executor.execute(
            goal="Prepare the v1.2.0 release",
            inject_failures={"Run tests": True},
        )

        self.assertEqual(result.status, "failed")
        self.assertEqual(result.replan_count, 0)
        self.assertIn("reached maximum replan count", result.error)


if __name__ == "__main__":
    unittest.main()
