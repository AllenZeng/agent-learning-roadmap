import unittest

from context_engineering_demo import (
    ContextAssembler,
    LayerPolicy,
    ablation_report,
    build_demo_items,
    evaluate,
)


class ContextEngineeringTest(unittest.TestCase):
    def setUp(self):
        self.policies = {
            "system": LayerPolicy(140, required=True),
            "user_goal": LayerPolicy(120, required=True),
            "scratchpad": LayerPolicy(220, required=True),
            "rag": LayerPolicy(50),
            "memory": LayerPolicy(120),
            "tool_definition": LayerPolicy(140),
            "tool_result": LayerPolicy(360),
            "history": LayerPolicy(100),
        }
        self.assembler = ContextAssembler(self.policies, total_budget=900)

    def test_engineered_context_stays_under_budget(self):
        prompt, meta = self.assembler.engineered(build_demo_items(process_tools=True))
        self.assertLessEqual(meta["tokens"], meta["budget"])
        self.assertIn("当前任务状态", prompt)
        self.assertIn("README 读取结果（已瘦身）", prompt)

    def test_engineered_context_removes_untrusted_injection(self):
        prompt, meta = self.assembler.engineered(build_demo_items(process_tools=True))
        self.assertFalse(meta["injection_exposed"])
        self.assertNotIn("ignore previous instructions", prompt)
        self.assertNotIn("泄露部署密钥", prompt)

    def test_generic_processor_is_exercised(self):
        prompt, _ = self.assembler.engineered(build_demo_items(process_tools=True))
        self.assertIn("未知工具输出（通用摘要）", prompt)
        self.assertIn("[已移除：外部资料中的疑似指令注入]", prompt)

    def test_engineered_strategy_keeps_key_signals(self):
        naive_prompt, naive_meta = self.assembler.naive(build_demo_items(process_tools=False))
        prompt, meta = self.assembler.engineered(build_demo_items(process_tools=True))
        metrics = evaluate(naive_meta, meta, prompt)
        self.assertGreater(metrics["token_saving"], 0)
        self.assertTrue(metrics["keeps_key_signal"])
        self.assertTrue(metrics["injection_resistance"])

    def test_ablation_report_detects_lost_signal(self):
        report = ablation_report(self.assembler, build_demo_items(process_tools=True))
        self.assertIn("tool_result", report)
        self.assertTrue(report["tool_result"]["lost_key_signal"])


if __name__ == "__main__":
    unittest.main()
