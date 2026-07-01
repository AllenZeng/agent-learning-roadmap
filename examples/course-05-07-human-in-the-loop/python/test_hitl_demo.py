import unittest

from hitl_demo import HitlMode, HitlPolicy, ProposedAction, Risk


class HitlPolicyTest(unittest.TestCase):
    def setUp(self):
        self.policy = HitlPolicy()

    def test_read_only_action_needs_no_hitl(self):
        risk, mode = self.policy.assess(
            ProposedAction("read_file", "notes.md", "读取笔记", reversible=True)
        )

        self.assertEqual(risk, Risk.LOW)
        self.assertEqual(mode, HitlMode.NONE)

    def test_delete_env_backup_requires_takeover(self):
        risk, mode = self.policy.assess(
            ProposedAction("delete_file", "/tmp/logs/.env.backup", "清理日志", reversible=False)
        )

        self.assertEqual(risk, Risk.CRITICAL)
        self.assertEqual(mode, HitlMode.TAKEOVER)

    def test_refund_with_high_amount_requires_takeover(self):
        risk, mode = self.policy.assess(
            ProposedAction(
                "refund",
                "order-1",
                "退款",
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
                "退款",
                reversible=False,
                external_effect=True,
                metadata={"amount": 299, "previous_refunds": 0},
            )
        )

        self.assertEqual(risk, Risk.HIGH)
        self.assertEqual(mode, HitlMode.CONFIRMATION)


if __name__ == "__main__":
    unittest.main()
