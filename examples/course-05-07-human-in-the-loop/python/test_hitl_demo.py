import unittest
from contextlib import redirect_stdout
from io import StringIO

from hitl_demo import (
    HitlDecision,
    HitlMode,
    HitlPolicy,
    ProposedAction,
    Risk,
    print_refund_result,
    print_takeover_result,
)


class HitlPolicyTest(unittest.TestCase):
    def setUp(self):
        self.policy = HitlPolicy()

    def test_read_only_action_needs_no_hitl(self):
        risk, mode = self.policy.assess(
            ProposedAction("read_file", "notes.md", "textnotes", reversible=True)
        )

        self.assertEqual(risk, Risk.LOW)
        self.assertEqual(mode, HitlMode.NONE)

    def test_delete_env_backup_requires_takeover(self):
        risk, mode = self.policy.assess(
            ProposedAction("delete_file", "/tmp/logs/.env.backup", "clean logs", reversible=False)
        )

        self.assertEqual(risk, Risk.CRITICAL)
        self.assertEqual(mode, HitlMode.TAKEOVER)

    def test_refund_with_high_amount_requires_takeover(self):
        risk, mode = self.policy.assess(
            ProposedAction(
                "refund",
                "order-1",
                "refund",
                reversible=False,
                external_effect=True,
                metadata={"amount": 2400, "previous_refunds": 0},
            )
        )

        self.assertEqual(risk, Risk.CRITICAL)
        self.assertEqual(mode, HitlMode.TAKEOVER)

    def test_normal_refund_requires_confirmation(self):
        risk, mode = self.policy.assess(
            ProposedAction(
                "refund",
                "order-2",
                "refund",
                reversible=False,
                external_effect=True,
                metadata={"amount": 299, "previous_refunds": 0},
            )
        )

        self.assertEqual(risk, Risk.HIGH)
        self.assertEqual(mode, HitlMode.CONFIRMATION)


class HitlResultHandlingTest(unittest.TestCase):
    def capture(self, fn, *args):
        output = StringIO()
        with redirect_stdout(output):
            fn(*args)
        return output.getvalue()

    def test_refund_rejection_prints_follow_up_action(self):
        output = self.capture(
            print_refund_result,
            HitlDecision(HitlMode.CONFIRMATION, Risk.HIGH, "rejected", "humanrejecttext"),
            "ORD-1",
        )

        self.assertIn("textreject ORD-1 textrefundtext", output)

    def test_takeover_prints_waiting_state(self):
        output = self.capture(
            print_takeover_result,
            HitlDecision(HitlMode.TAKEOVER, Risk.CRITICAL, "manual_required", "Critical-risk operations require human execution"),
            "production database migration",
        )

        self.assertIn("Agent textStatus", output)


if __name__ == "__main__":
    unittest.main()
