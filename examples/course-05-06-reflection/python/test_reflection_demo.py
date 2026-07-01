import unittest

from reflection_demo import (
    ActionResult,
    BUGGY_CLEANUP_CODE,
    CORRECT_CLEANUP_CODE,
    MOCK_NOTES,
    ValidationResult,
    reflection_loop,
    validate_citation,
    validate_json_schema,
    validate_tests,
)


class ReflectionDemoTest(unittest.TestCase):
    def test_schema_error_is_fixed_by_second_attempt(self):
        def action(previous_error, attempt):
            if attempt == 0:
                return ActionResult(
                    output='{"tool": "search_notes", "query": "memory cleanup"}',
                    cost=0.01,
                )
            return ActionResult(
                output='{"tool_name": "search_notes", "args": {"query": "memory cleanup"}, "reason": "查找笔记"}',
                cost=0.01,
            )

        result = reflection_loop(action, validate_json_schema, verbose=False)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.attempts, 2)
        self.assertIn("tool_name", result.output)

    def test_test_failure_is_fixed_with_external_validation(self):
        def action(previous_error, attempt):
            if attempt == 0:
                return ActionResult(output=BUGGY_CLEANUP_CODE, cost=0.03)
            return ActionResult(output=CORRECT_CLEANUP_CODE, cost=0.03)

        result = reflection_loop(action, validate_tests, verbose=False)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.attempts, 2)
        self.assertIn("memory_store.decay()", result.output)

    def test_citation_validator_catches_missing_api(self):
        output = "错误原因是调用了 `memory.clear_expired()`。"

        validation = validate_citation(output, MOCK_NOTES)

        self.assertFalse(validation.passed)
        self.assertEqual(validation.error_type, "context_missing")
        self.assertIn("memory.clear_expired", validation.message)

    def test_repeated_error_stops_loop(self):
        def action(previous_error, attempt):
            return ActionResult(output='{"tool": "search_notes"}', cost=0.01)

        result = reflection_loop(action, validate_json_schema, max_retries=3, verbose=False)

        self.assertEqual(result.status, "stopped")
        self.assertEqual(result.reason, "repeated_failure")
        self.assertEqual(result.attempts, 2)

    def test_cost_limit_stops_loop(self):
        def action(previous_error, attempt):
            return ActionResult(output='{"tool": "search_notes"}', cost=0.75)

        def always_fails(output):
            return ValidationResult(
                passed=False,
                message="仍然失败",
                evidence="validator evidence",
                error_type="schema_error",
            )

        result = reflection_loop(
            action,
            always_fails,
            max_retries=3,
            cost_budget=0.5,
            verbose=False,
        )

        self.assertEqual(result.status, "stopped")
        self.assertEqual(result.reason, "cost_limit")
        self.assertEqual(result.attempts, 1)


if __name__ == "__main__":
    unittest.main()
