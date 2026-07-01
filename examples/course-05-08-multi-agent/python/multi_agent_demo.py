#!/usr/bin/env python3
"""
课程五 05-08 Multi-Agent 示例

演示最小 Reviewer 模式：
  - Executor 负责产出技术方案
  - Reviewer 只接收最终产物和审查清单，不接收 Executor 的中间推理
  - Reviewer 用结构化结果逐条给出 PASS/FAIL、证据和修正建议
  - Runtime 最多允许两轮修正，仍失败则进入 disputed，等待人工裁决

用法：
  python3 multi_agent_demo.py
  python3 -m unittest test_multi_agent_demo.py
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AgentConfig:
    name: str
    inputs: set[str]
    tools: set[str]
    goal: str
    acceptance: str


@dataclass(frozen=True)
class CheckItem:
    id: str
    check: str
    how_to_verify: str
    severity: str


@dataclass(frozen=True)
class Issue:
    id: str
    description: str
    location: str
    severity: str
    suggestion: str


@dataclass(frozen=True)
class CheckResult:
    check_id: str
    passed: bool
    evidence: str
    suggestion: str | None = None


@dataclass(frozen=True)
class ReviewRequest:
    original_requirement: str
    artifact: str
    criteria: list[CheckItem]
    executor_private_trace: str | None = None


@dataclass(frozen=True)
class ReviewResponse:
    verdict: str
    checks: list[CheckResult]
    issues: list[Issue]


@dataclass
class Draft:
    output: str
    private_trace: str = ""


@dataclass
class ReviewerPatternResult:
    status: str
    output: str
    review_rounds: int
    review_trace: list[ReviewResponse] = field(default_factory=list)
    unresolved_issues: list[Issue] = field(default_factory=list)
    reason: str = ""


def count_agent_differences(left: AgentConfig, right: AgentConfig) -> dict[str, int | bool]:
    """课程 8.2 的“四个不同”：输入、工具、目标、验收标准。"""
    differences = {
        "inputs": left.inputs != right.inputs,
        "tools": left.tools != right.tools,
        "goal": left.goal != right.goal,
        "acceptance": left.acceptance != right.acceptance,
    }
    return {**differences, "total": sum(1 for value in differences.values() if value)}


class DemoExecutorAgent:
    """确定性 Executor：第一版故意留下安全问题，收到具体 issue 后修正。"""

    def __init__(self, fixable_issue_ids: set[str] | None = None):
        self.fixable_issue_ids = fixable_issue_ids
        self.revisions: list[list[str]] = []

    def run(self, task: str, fix_instructions: list[Issue] | None = None) -> Draft:
        applied = self._applicable_issue_ids(fix_instructions or [])
        self.revisions.append(sorted(applied))
        return Draft(
            output=self._render_artifact(applied),
            private_trace=(
                "为了本地演示先用明文 key；权限模型先简化成 admin；"
                "依赖版本先不锁定，后续再补。"
            ),
        )

    def _applicable_issue_ids(self, issues: list[Issue]) -> set[str]:
        issue_ids = {issue.id for issue in issues}
        if self.fixable_issue_ids is None:
            return issue_ids
        return issue_ids & self.fixable_issue_ids

    def _render_artifact(self, fixed: set[str]) -> str:
        api_line = (
            "12: input: string, max_length: 256"
            if "C1" in fixed
            else "12: input: string"
        )
        config_line = (
            '8: api_key: "${API_KEY}"'
            if "C2" in fixed
            else '8: api_key: "sk-demo-plaintext"'
        )
        permission_line = (
            "3-5: roles: reader, writer, admin"
            if "C3" in fixed
            else "3-5: roles: admin"
        )
        dependency_line = (
            "requirements.txt: fastapi==0.111.0"
            if "C4" in fixed
            else "requirements.txt: fastapi>=0.111"
        )
        return "\n".join(
            [
                "# API 模块技术方案",
                "",
                "## api_schema.yaml",
                api_line,
                "",
                "## config.yaml",
                config_line,
                "",
                "## permissions.py",
                permission_line,
                "",
                "## dependencies",
                dependency_line,
            ]
        )


class DemoReviewerAgent:
    """确定性 Reviewer：只能读最终产物和检查清单，不能看到 Executor 私有 trace。"""

    def __init__(self):
        self.review_requests: list[ReviewRequest] = []
        self.seen_private_traces: list[str] = []

    def run(self, request: ReviewRequest) -> ReviewResponse:
        self.review_requests.append(request)
        if request.executor_private_trace:
            self.seen_private_traces.append(request.executor_private_trace)

        checks: list[CheckResult] = []
        issues: list[Issue] = []
        for item in request.criteria:
            result = self._check(item, request.artifact)
            checks.append(result)
            if not result.passed:
                issues.append(
                    Issue(
                        id=item.id,
                        description=self._description(item.id),
                        location=self._location(item.id),
                        severity=item.severity,
                        suggestion=result.suggestion or "按审查项补齐缺失约束",
                    )
                )

        verdict = "approved" if not issues else "rejected"
        return ReviewResponse(verdict=verdict, checks=checks, issues=issues)

    def _check(self, item: CheckItem, artifact: str) -> CheckResult:
        if item.id == "C1":
            passed = "max_length: 256" in artifact
            return CheckResult(
                item.id,
                passed,
                "api_schema.yaml:12 包含 max_length" if passed else "api_schema.yaml:12 缺少 max_length",
                None if passed else "为 input 参数增加 max_length: 256",
            )
        if item.id == "C2":
            passed = "${API_KEY}" in artifact and "sk-demo-plaintext" not in artifact
            return CheckResult(
                item.id,
                passed,
                "config.yaml:8 使用环境变量" if passed else "config.yaml:8 出现明文 api_key",
                None if passed else "改用 ${API_KEY} 环境变量",
            )
        if item.id == "C3":
            passed = "reader, writer, admin" in artifact
            return CheckResult(
                item.id,
                passed,
                "permissions.py:3-5 区分 reader/writer/admin"
                if passed
                else "permissions.py:3-5 只有 admin 角色",
                None if passed else "拆分 reader 和 writer 角色",
            )
        if item.id == "C4":
            passed = "fastapi==0.111.0" in artifact
            return CheckResult(
                item.id,
                passed,
                "requirements.txt 使用 == 锁定版本"
                if passed
                else "requirements.txt 使用 >=，版本未锁定",
                None if passed else "使用 == 锁定依赖版本",
            )
        return CheckResult(item.id, False, "not_found", "补充可验证证据")

    def _description(self, check_id: str) -> str:
        descriptions = {
            "C1": "/api/data 缺少输入长度限制",
            "C2": "API key 明文存储",
            "C3": "权限模型缺少读写分离",
            "C4": "第三方依赖未锁定版本",
        }
        return descriptions.get(check_id, "未知审查项未通过")

    def _location(self, check_id: str) -> str:
        locations = {
            "C1": "api_schema.yaml:12",
            "C2": "config.yaml:8",
            "C3": "permissions.py:3-5",
            "C4": "requirements.txt",
        }
        return locations.get(check_id, "unknown")


class ReviewerPattern:
    """Executor 产出 -> Reviewer 审查 -> Executor 修正或上报分歧。"""

    def __init__(self, executor: DemoExecutorAgent, reviewer: DemoReviewerAgent, max_rounds: int = 2):
        self.executor = executor
        self.reviewer = reviewer
        self.max_rounds = max_rounds

    def run(self, task: str, criteria: list[CheckItem], verbose: bool = True) -> ReviewerPatternResult:
        draft = self.executor.run(task)
        review_trace: list[ReviewResponse] = []

        for round_index in range(self.max_rounds):
            if verbose:
                print(f"\n[Round {round_index + 1}] Reviewer 开始审查")

            request = ReviewRequest(
                original_requirement=task,
                artifact=draft.output,
                criteria=criteria,
                executor_private_trace=None,
            )
            review = self.reviewer.run(request)
            review_trace.append(review)

            if verbose:
                self._print_review(review)

            if review.verdict == "approved":
                return ReviewerPatternResult(
                    status="approved",
                    output=draft.output,
                    review_rounds=round_index + 1,
                    review_trace=review_trace,
                )

            if round_index < self.max_rounds - 1:
                if verbose:
                    print("[Runtime] 只把具体 issues 传回 Executor，不传主观评价。")
                draft = self.executor.run(task, fix_instructions=review.issues)

        return ReviewerPatternResult(
            status="disputed",
            output=draft.output,
            review_rounds=self.max_rounds,
            review_trace=review_trace,
            unresolved_issues=review_trace[-1].issues,
            reason="max_review_rounds",
        )

    def _print_review(self, review: ReviewResponse) -> None:
        print(f"verdict: {review.verdict}")
        for check in review.checks:
            status = "PASS" if check.passed else "FAIL"
            print(f"  {check.check_id}: {status} - {check.evidence}")
        if review.issues:
            print("issues:")
            for issue in review.issues:
                print(f"  - {issue.id} {issue.location}: {issue.description}")


def default_criteria() -> list[CheckItem]:
    return [
        CheckItem("C1", "输入长度限制", "检查 /api/data 的 input 参数是否声明 max_length", "must_fix"),
        CheckItem("C2", "密钥管理", "检查配置示例是否使用环境变量而不是明文 key", "must_fix"),
        CheckItem("C3", "权限模型", "检查是否区分 reader 和 writer 角色", "must_fix"),
        CheckItem("C4", "依赖锁定", "检查依赖是否使用 == 锁定版本", "should_fix"),
    ]


def print_config_difference_demo() -> None:
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
    print("四个不同检查:")
    for key in ["inputs", "tools", "goal", "acceptance"]:
        print(f"  {key}: {'different' if differences[key] else 'same'}")
    print(f"  total: {differences['total']}")


def main() -> None:
    print_config_difference_demo()
    pattern = ReviewerPattern(DemoExecutorAgent(), DemoReviewerAgent(), max_rounds=2)
    result = pattern.run("写一份 API 模块技术方案，并从安全角度审查", default_criteria())

    print("\n最终状态:", result.status)
    print("审查轮次:", result.review_rounds)
    if result.status == "approved":
        print("\n最终产物:\n" + result.output)
    else:
        print("未解决问题:", [issue.id for issue in result.unresolved_issues])


if __name__ == "__main__":
    main()
