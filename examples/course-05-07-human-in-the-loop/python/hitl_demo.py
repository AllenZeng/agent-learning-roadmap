#!/usr/bin/env python3
"""
课程五 05-07 Human-in-the-loop 示例

演示 Agent 在不同风险等级下如何选择确认、澄清、接管、审核和教学反馈。

用法：
  python3 hitl_demo.py           # 交互模式
  python3 hitl_demo.py --auto    # 自动模式
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Callable, Iterable


class Risk(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class HitlMode(str, Enum):
    NONE = "none"
    CONFIRMATION = "confirmation"
    CLARIFICATION = "clarification"
    TAKEOVER = "takeover"
    REVIEW = "review"
    TEACHING_FEEDBACK = "teaching_feedback"


@dataclass
class ProposedAction:
    tool: str
    target: str
    reason: str
    reversible: bool
    external_effect: bool = False
    metadata: dict | None = None


@dataclass
class HitlDecision:
    mode: HitlMode
    risk: Risk
    decision: str
    reason: str


class HitlPolicy:
    """基于工具、参数和上下文选择 HITL 模式。"""

    def assess(self, action: ProposedAction) -> tuple[Risk, HitlMode]:
        target = action.target
        metadata = action.metadata or {}

        if action.tool in {"read_file", "search_notes"}:
            return Risk.LOW, HitlMode.NONE

        if action.tool == "refund":
            amount = metadata.get("amount", 0)
            previous_refunds = metadata.get("previous_refunds", 0)
            if amount > 1000 or previous_refunds >= 3:
                return Risk.CRITICAL, HitlMode.TAKEOVER
            return Risk.HIGH, HitlMode.CONFIRMATION

        if action.tool == "database_migration":
            return Risk.CRITICAL, HitlMode.TAKEOVER

        if action.tool == "delete_file":
            if "/.ssh/" in target or target.endswith(".env") or ".env" in target:
                return Risk.CRITICAL, HitlMode.TAKEOVER
            if not action.reversible:
                return Risk.HIGH, HitlMode.CONFIRMATION
            return Risk.MEDIUM, HitlMode.CONFIRMATION

        if action.tool in {"write_file", "send_email"}:
            return Risk.MEDIUM, HitlMode.CONFIRMATION

        return Risk.MEDIUM, HitlMode.CONFIRMATION


class AuditLog:
    def __init__(self, path: str = "hitl_audit.jsonl"):
        self.path = path

    def reset(self) -> None:
        if os.path.exists(self.path):
            os.remove(self.path)

    def record(self, action: ProposedAction, hitl: HitlDecision) -> None:
        entry = {
            "ts": datetime.now().isoformat(timespec="seconds"),
            "action": asdict(action),
            "hitl": {
                "mode": hitl.mode.value,
                "risk": hitl.risk.value,
                "decision": hitl.decision,
                "reason": hitl.reason,
            },
        }
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def load(self) -> list[dict]:
        if not os.path.exists(self.path):
            return []
        with open(self.path, encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]


class TeachingMemory:
    def __init__(self, path: str = "hitl_memory.json"):
        self.path = path
        self.items = self._load()

    def _load(self) -> list[dict]:
        if not os.path.exists(self.path):
            return []
        with open(self.path, encoding="utf-8") as f:
            return json.load(f)

    def reset(self) -> None:
        self.items = []
        if os.path.exists(self.path):
            os.remove(self.path)

    def remember(self, category: str, content: str, source: str) -> None:
        item = {
            "category": category,
            "content": content,
            "source": source,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        self.items.append(item)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.items, f, ensure_ascii=False, indent=2)


class HumanSimulator:
    def __init__(self, auto: bool):
        self.auto = auto

    def choose(self, prompt: str, options: dict[str, str], default: str) -> str:
        print(prompt)
        for key, label in options.items():
            marker = " (默认)" if key == default else ""
            print(f"  {key}. {label}{marker}")

        if self.auto:
            print(f"  自动选择: {default}\n")
            return default

        choice = input("  请选择: ").strip() or default
        print()
        return choice if choice in options else default


class HitlAgent:
    def __init__(self, auto: bool = False):
        self.policy = HitlPolicy()
        self.audit = AuditLog()
        self.memory = TeachingMemory()
        self.human = HumanSimulator(auto)

    def reset(self) -> None:
        self.audit.reset()
        self.memory.reset()

    def propose(self, action: ProposedAction) -> HitlDecision:
        risk, mode = self.policy.assess(action)
        if mode == HitlMode.NONE:
            decision = HitlDecision(mode, risk, "auto_execute", "只读或低风险操作，无需介入")
        elif mode == HitlMode.TAKEOVER:
            decision = self._takeover(action, risk)
        else:
            decision = self._confirmation(action, risk)
        self.audit.record(action, decision)
        return decision

    def _confirmation(self, action: ProposedAction, risk: Risk) -> HitlDecision:
        metadata = action.metadata or {}
        prompt = "\n[确认模式] Agent 请求执行操作：\n"
        prompt += f"  工具: {action.tool}\n"
        prompt += f"  目标: {action.target}\n"
        prompt += f"  原因: {action.reason}\n"
        prompt += f"  风险: {risk.value}\n"
        if metadata.get("impact"):
            prompt += f"  影响: {metadata['impact']}\n"
        if metadata.get("anomalies"):
            prompt += f"  异常项: {', '.join(metadata['anomalies'])}\n"

        choice = self.human.choose(
            prompt,
            {
                "a": "批准执行",
                "s": "只执行安全子集",
                "r": "拒绝",
                "m": "转为人工处理",
            },
            default=metadata.get("default_decision", "s"),
        )
        mapping = {
            "a": ("approved", "人类批准完整操作"),
            "s": ("safe_subset", "人类选择只执行风险更低的子集"),
            "r": ("rejected", "人类拒绝操作"),
            "m": ("manual", "人类要求接管"),
        }
        decision, reason = mapping[choice]
        return HitlDecision(HitlMode.CONFIRMATION, risk, decision, reason)

    def _takeover(self, action: ProposedAction, risk: Risk) -> HitlDecision:
        print("\n[接管模式] Agent 不会自主执行该操作。")
        print(f"  工具: {action.tool}")
        print(f"  目标: {action.target}")
        print(f"  原因: {action.reason}")
        print("  已生成执行说明，由人类完成后再让 Agent 继续。")
        if action.tool == "database_migration":
            print("  建议命令: psql \"$DATABASE_URL\" -f ./migration.sql")
        print()
        return HitlDecision(HitlMode.TAKEOVER, risk, "manual_required", "关键风险操作需要人类执行")

    def clarify_recent_articles(self) -> str:
        choice = self.human.choose(
            "\n[澄清模式] 用户说“整理最近的文章”，Agent 需要明确“最近”指什么：",
            {
                "a": "最近 7 天创建的文章（3 篇）",
                "b": "最近修改过的文章（8 篇）",
                "c": "最近打开过的文章（5 篇）",
                "d": "其他，我手动说明",
            },
            default="b",
        )
        labels = {
            "a": "created_in_7_days",
            "b": "modified_recently",
            "c": "opened_recently",
            "d": "custom",
        }
        decision = HitlDecision(HitlMode.CLARIFICATION, Risk.MEDIUM, labels[choice], "人类定义模糊意图")
        self.audit.record(
            ProposedAction("organize_articles", "articles", "用户指令存在多义性", reversible=True),
            decision,
        )
        return labels[choice]

    def review_release_doc(self) -> None:
        print("\n[审核模式] Agent 生成了发布文档草稿，并主动标注不确定点：")
        print("  1. 架构变更摘要：已生成")
        print("  2. API 兼容性说明：已生成")
        print("  3. 回滚方案：待确认，数据库回滚窗口不确定")
        print("  4. 发布 checklist：可能遗漏数据库备份")
        choice = self.human.choose(
            "  请审核：",
            {
                "p": "通过",
                "e": "要求补充数据库备份步骤",
                "r": "退回重写",
            },
            default="e",
        )
        decision = "approved" if choice == "p" else "needs_revision"
        self.audit.record(
            ProposedAction("write_file", "release_notes.md", "生成发布文档", reversible=True),
            HitlDecision(HitlMode.REVIEW, Risk.MEDIUM, decision, "人类审核 Agent 产出"),
        )

        if choice == "e":
            self.apply_teaching_feedback(
                "发布 checklist 必须包含数据库备份步骤",
                "release_checklist",
            )

    def apply_teaching_feedback(self, correction: str, category: str) -> None:
        print("\n[教学反馈模式] 人类指出：", correction)
        print("  Agent 即时修正当前文档，并写入可复用偏好。")
        self.memory.remember(category, correction, "human_review")
        self.audit.record(
            ProposedAction("update_memory", category, "从人工反馈中学习", reversible=True),
            HitlDecision(HitlMode.TEACHING_FEEDBACK, Risk.MEDIUM, "remembered", correction),
        )
        print()

    def analyze_audit(self) -> None:
        entries = self.audit.load()
        stats: dict[str, dict[str, int]] = {}
        for entry in entries:
            tool = entry["action"]["tool"]
            decision = entry["hitl"]["decision"]
            stats.setdefault(tool, {"total": 0, "approved": 0, "manual": 0, "rejected": 0})
            stats[tool]["total"] += 1
            if decision in {"approved", "safe_subset", "auto_execute"}:
                stats[tool]["approved"] += 1
            if decision in {"manual", "manual_required"}:
                stats[tool]["manual"] += 1
            if decision == "rejected":
                stats[tool]["rejected"] += 1

        print("\n[HITL 数据分析] 基于本次审计日志生成策略建议：")
        for tool, data in stats.items():
            rate = data["approved"] / data["total"]
            if rate >= 0.95 and data["manual"] == 0:
                advice = "可考虑降低确认频率"
            elif data["manual"] > 0 or rate < 0.7:
                advice = "保持或提高介入强度"
            else:
                advice = "保持当前策略"
            print(f"  - {tool}: {data['total']} 次，自动/通过率 {rate:.0%} -> {advice}")

        if self.memory.items:
            print("\n[Memory] 从教学反馈沉淀的偏好：")
            for item in self.memory.items:
                print(f"  - {item['category']}: {item['content']}")


def run_batch_delete_demo(agent: HitlAgent) -> None:
    print("\n=== 1. 风险分级 + 批次确认 ===")
    candidates = [
        "/tmp/logs/access_20260501.log",
        "/tmp/logs/error_20260515.log",
        "/tmp/logs/debug_20260520.log",
        "/tmp/logs/.env.backup",
    ]
    action = ProposedAction(
        tool="delete_file",
        target="/tmp/logs/*",
        reason="清理超过 30 天的日志文件",
        reversible=False,
        metadata={
            "impact": "将删除 3 个 .log 文件，共 48MB；检测到 1 个非日志异常项不会默认删除",
            "anomalies": ["/tmp/logs/.env.backup"],
            "default_decision": "s",
            "candidates": candidates,
        },
    )
    decision = agent.propose(action)
    if decision.decision == "safe_subset":
        print("  执行结果: 只删除 .log 文件，保留 /tmp/logs/.env.backup\n")
    elif decision.decision == "approved":
        print("  执行结果: 删除全部候选文件\n")
    else:
        print("  执行结果: 未执行删除\n")


def run_refund_demo(agent: HitlAgent) -> None:
    print("\n=== 2. 退款操作的上下文确认 ===")
    refund = ProposedAction(
        tool="refund",
        target="order ORD-20260629-0042",
        reason="用户反馈产品功能与描述不符，订单未发货",
        reversible=False,
        external_effect=True,
        metadata={
            "amount": 299,
            "previous_refunds": 0,
            "impact": "全额退款 ¥299.00；用户注册 2 年，此前 0 次退款",
            "default_decision": "a",
        },
    )
    agent.propose(refund)

    suspicious_refund = ProposedAction(
        tool="refund",
        target="order ORD-20260629-0099",
        reason="高额订单且用户近期多次退款",
        reversible=False,
        external_effect=True,
        metadata={"amount": 2400, "previous_refunds": 5},
    )
    agent.propose(suspicious_refund)


def run_takeover_demo(agent: HitlAgent) -> None:
    print("\n=== 3. 关键风险操作进入接管模式 ===")
    action = ProposedAction(
        tool="database_migration",
        target="production users.email type change",
        reason="迁移脚本会修改生产数据库 schema",
        reversible=False,
        external_effect=True,
    )
    agent.propose(action)


def run_demo(auto: bool) -> None:
    agent = HitlAgent(auto=auto)
    agent.reset()

    print("=" * 68)
    print("  Human-in-the-loop — 当 Agent 不该自己决定时")
    print("=" * 68)

    run_batch_delete_demo(agent)
    agent.clarify_recent_articles()
    run_refund_demo(agent)
    run_takeover_demo(agent)
    agent.review_release_doc()
    agent.analyze_audit()

    print("\n输出文件:")
    print("  - hitl_audit.jsonl")
    print("  - hitl_memory.json")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--auto", action="store_true", help="自动选择默认决策，方便完整演示")
    args = parser.parse_args()
    run_demo(auto=args.auto)


if __name__ == "__main__":
    main()
