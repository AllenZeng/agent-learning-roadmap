#!/usr/bin/env python3
"""
Course 05-07 Human-in-the-loop example

text Agent textRiskstext、text、text、text。

Usage:
  python3 hitl_demo.py
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


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
    """text、textcontextchoose HITL pattern。"""

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
    def choose(self, prompt: str, options: dict[str, str], default: str) -> str:
        print(prompt)
        for key, label in options.items():
            marker = " (default)" if key == default else ""
            print(f"  {key}. {label}{marker}")

        choice = input("  Please choose: ").strip() or default
        print()
        return choice if choice in options else default


class HitlAgent:
    def __init__(self):
        self.policy = HitlPolicy()
        self.audit = AuditLog()
        self.memory = TeachingMemory()
        self.human = HumanSimulator()

    def reset(self) -> None:
        self.audit.reset()
        self.memory.reset()

    def propose(self, action: ProposedAction) -> HitlDecision:
        risk, mode = self.policy.assess(action)
        if mode == HitlMode.NONE:
            decision = HitlDecision(mode, risk, "direct_execute", "textlowRiskstext，nonetext")
        elif mode == HitlMode.TAKEOVER:
            decision = self._takeover(action, risk)
        else:
            decision = self._confirmation(action, risk)
        self.audit.record(action, decision)
        return decision

    def _confirmation(self, action: ProposedAction, risk: Risk) -> HitlDecision:
        metadata = action.metadata or {}
        prompt = "\n[confirmation mode] Agent requests operation execution：\n"
        prompt += f"  tool: {action.tool}\n"
        prompt += f"  Goal: {action.target}\n"
        prompt += f"  reason: {action.reason}\n"
        prompt += f"  Risks: {risk.value}\n"
        if metadata.get("impact"):
            prompt += f"  impact: {metadata['impact']}\n"
        if metadata.get("anomalies"):
            prompt += f"  anomalies: {', '.join(metadata['anomalies'])}\n"

        choice = self.human.choose(
            prompt,
            {
                "a": "approveexecute",
                "s": "execute onlysafe subset",
                "r": "reject",
                "m": "switch tomanual handling",
            },
            default=metadata.get("default_decision", "s"),
        )
        mapping = {
            "a": ("approved", "humanapprovetext"),
            "s": ("safe_subset", "humantextRiskstextlowtext"),
            "r": ("rejected", "humanrejecttext"),
            "m": ("manual", "humantext"),
        }
        decision, reason = mapping[choice]
        return HitlDecision(HitlMode.CONFIRMATION, risk, decision, reason)

    def _takeover(self, action: ProposedAction, risk: Risk) -> HitlDecision:
        print("\n[takeover mode] Agent will not execute this operation autonomously。")
        print(f"  tool: {action.tool}")
        print(f"  Goal: {action.target}")
        print(f"  reason: {action.reason}")
        print("  textinstructions，texthumancompletetext Agent text。")
        if action.tool == "database_migration":
            print("  Recommendationstext: psql \"$DATABASE_URL\" -f ./migration.sql")
        print()
        return HitlDecision(HitlMode.TAKEOVER, risk, "manual_required", "Critical-risk operations require human execution")

    def clarify_recent_articles(self) -> str:
        choice = self.human.choose(
            "\n[clarification mode] usertext“organize recent articles”，Agent needs to clarify“recent”means what：",
            {
                "a": "recent 7 text（3 files)",
                "b": "recently modified articles（8 files)",
                "c": "recently opened articles（5 files)",
                "d": "texthe，textinstructions",
            },
            default="b",
        )
        labels = {
            "a": "created_in_7_days",
            "b": "modified_recently",
            "c": "opened_recently",
            "d": "custom",
        }
        decision = HitlDecision(HitlMode.CLARIFICATION, Risk.MEDIUM, labels[choice], "humantext")
        self.audit.record(
            ProposedAction("organize_articles", "articles", "userinstructionstext", reversible=True),
            decision,
        )
        return labels[choice]

    def review_release_doc(self) -> None:
        print("\n[review mode] Agent textreleasedocstext，and proactively marked uncertainties：")
        print("  1. architecture-change summary：text")
        print("  2. API textinstructions：text")
        print("  3. rollback plan：pending confirmation，database rollback window is uncertain")
        print("  4. release checklist：may miss database backup")
        choice = self.human.choose(
            "  Please review：",
            {
                "p": "pass",
                "e": "textstep",
                "r": "return for rewrite",
            },
            default="e",
        )
        decision = "approved" if choice == "p" else "needs_revision"
        self.audit.record(
            ProposedAction("write_file", "release_notes.md", "textreleasedocs", reversible=True),
            HitlDecision(HitlMode.REVIEW, Risk.MEDIUM, decision, "humantext Agent text"),
        )

        if choice == "e":
            self.apply_teaching_feedback(
                "release checklist textstep",
                "release_checklist",
            )

    def apply_teaching_feedback(self, correction: str, category: str) -> None:
        print("\n[teaching-feedback mode] humantext：", correction)
        print("  Agent textcorrectiontextdocs，textWritetext。")
        self.memory.remember(category, correction, "human_review")
        self.audit.record(
            ProposedAction("update_memory", category, "textmediumtext", reversible=True),
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
            if decision in {"approved", "safe_subset", "direct_execute"}:
                stats[tool]["approved"] += 1
            if decision in {"manual", "manual_required"}:
                stats[tool]["manual"] += 1
            if decision == "rejected":
                stats[tool]["rejected"] += 1

        print("\n[HITL textanalysis] texttimesAudit logtextRecommendations：")
        for tool, data in stats.items():
            rate = data["approved"] / data["total"]
            if rate >= 0.95 and data["manual"] == 0:
                advice = "textlowtext"
            elif data["manual"] > 0 or rate < 0.7:
                advice = "texthightext"
            else:
                advice = "keep current policy"
            print(f"  - {tool}: {data['total']} times，direct execution/approval rate {rate:.0%} -> {advice}")

        if self.memory.items:
            print("\n[Memory] preferences distilled from teaching feedback：")
            for item in self.memory.items:
                print(f"  - {item['category']}: {item['content']}")


def run_batch_delete_demo(agent: HitlAgent) -> None:
    print("\n=== 1. Riskstext + texttimesconfirm ===")
    candidates = [
        "/tmp/logs/access_20260501.log",
        "/tmp/logs/error_20260515.log",
        "/tmp/logs/debug_20260520.log",
        "/tmp/logs/.env.backup",
    ]
    action = ProposedAction(
        tool="delete_file",
        target="/tmp/logs/*",
        reason="clean older than 30 days of log files",
        reversible=False,
        metadata={
            "impact": "textdelete 3 items .log text，total 48MB；text 1 textdefaultdelete",
            "anomalies": ["/tmp/logs/.env.backup"],
            "default_decision": "s",
            "candidates": candidates,
        },
    )
    decision = agent.propose(action)
    if decision.decision == "safe_subset":
        print("  Execution result: textdelete .log text，kept /tmp/logs/.env.backup\n")
    elif decision.decision == "approved":
        print("  Execution result: deletetext\n")
    else:
        print("  Execution result: not executeddelete\n")


def print_refund_result(decision: HitlDecision, order_id: str) -> None:
    if decision.decision == "approved":
        print(f"  Execution result: submitted {order_id} textrefundtext，textWriterefundtext\n")
    elif decision.decision == "safe_subset":
        print(f"  Execution result: textrefund，textMove  {order_id} textmanual reviewtext\n")
    elif decision.decision == "manual":
        print(f"  Execution result: humantext，Agent textrefundtextkeptdecisioncontext\n")
    elif decision.decision == "manual_required":
        print(f"  Execution result: textRisksrefundnot executed，Agent textProcessinginstructions，textmanual handling\n")
    else:
        print(f"  Execution result: textreject {order_id} textrefundtext，textuserinstructionsreason\n")


def print_takeover_result(decision: HitlDecision, task_name: str) -> None:
    if decision.decision == "manual_required":
        print(f"  Execution result: {task_name} not executed by Agent execute；Agent textStatus，texthumantext“Completed”\n")
    elif decision.decision == "approved":
        print(f"  Execution result: {task_name} textapprove，textRecommendationstextsystemmediumkepttext\n")
    else:
        print(f"  Execution result: {task_name} not executed，textmediumtext\n")


def run_refund_demo(agent: HitlAgent) -> None:
    print("\n=== 2. refundtextcontextconfirm ===")
    refund = ProposedAction(
        tool="refund",
        target="order ORD-20260629-0042",
        reason="usertextfeaturetext，order has not shipped",
        reversible=False,
        external_effect=True,
        metadata={
            "amount": 299,
            "previous_refunds": 0,
            "impact": "textrefund ¥299.00；usertext 2 text，previously 0 timesrefund",
            "default_decision": "a",
        },
    )
    decision = agent.propose(refund)
    print_refund_result(decision, "ORD-20260629-0042")

    suspicious_refund = ProposedAction(
        tool="refund",
        target="order ORD-20260629-0099",
        reason="hightextusertexttimesrefund",
        reversible=False,
        external_effect=True,
        metadata={"amount": 2400, "previous_refunds": 5},
    )
    decision = agent.propose(suspicious_refund)
    print_refund_result(decision, "ORD-20260629-0099")


def run_takeover_demo(agent: HitlAgent) -> None:
    print("\n=== 3. textRiskstext ===")
    action = ProposedAction(
        tool="database_migration",
        target="production users.email type change",
        reason="text schema",
        reversible=False,
        external_effect=True,
    )
    decision = agent.propose(action)
    print_takeover_result(decision, "production database migration")


def run_demo() -> None:
    agent = HitlAgent()
    agent.reset()

    print("=" * 68)
    print("  Human-in-the-loop — when Agent text")
    print("=" * 68)

    run_batch_delete_demo(agent)
    agent.clarify_recent_articles()
    run_refund_demo(agent)
    run_takeover_demo(agent)
    agent.review_release_doc()
    agent.analyze_audit()

    print("\nOutput files:")
    print("  - hitl_audit.jsonl")
    print("  - hitl_memory.json")


def main() -> None:
    run_demo()


if __name__ == "__main__":
    main()
