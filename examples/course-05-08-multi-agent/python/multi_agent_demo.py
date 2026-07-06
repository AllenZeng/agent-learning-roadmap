#!/usr/bin/env python3
"""
课程五 05-08 Multi-Agent 示例

同一个离线示例项目演示课程正文里的三种协作模式：
  1. Reviewer：一个 Agent 写方案，另一个 Agent 独立审查
  2. Supervisor：一个 Supervisor 拆解任务，多个 Worker 并行产出结构化结果
  3. Parallel Specialists：多个专家看同一个输入，从不同维度并行分析

示例不调用真实 LLM，使用确定性函数模拟 Agent 行为，便于观察数据边界、
通信协议、停止条件和合并规则。
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


@dataclass(frozen=True)
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


@dataclass(frozen=True)
class Subtask:
    id: str
    topic: str
    worker: str
    scope: str
    exclude: str
    output_fields: tuple[str, ...]


@dataclass(frozen=True)
class WorkerResult:
    subtask_id: str
    worker: str
    topic: str
    status: str
    findings: list[str]
    risks: list[str]
    recommendations: list[str]
    missing_reason: str = ""


@dataclass(frozen=True)
class SupervisorPlan:
    subtasks: list[Subtask]


@dataclass(frozen=True)
class SupervisorResult:
    status: str
    plan: SupervisorPlan
    worker_results: list[WorkerResult]
    final_report: str
    missing_topics: list[str]


@dataclass(frozen=True)
class Dimension:
    name: str
    agent: str
    focus: str
    exclude: str


@dataclass(frozen=True)
class SpecialistFinding:
    id: str
    dimension: str
    location: str
    problem_type: str
    judgment: str
    evidence: str
    severity: str


@dataclass(frozen=True)
class SpecialistResult:
    dimension: str
    findings: list[SpecialistFinding]


@dataclass(frozen=True)
class MergedFinding:
    location: str
    problem_type: str
    judgment: str
    dimensions: list[str]
    evidence: list[str]
    severity: str


@dataclass(frozen=True)
class Conflict:
    location: str
    problem_type: str
    judgments: list[str]
    dimensions: list[str]


@dataclass(frozen=True)
class ParallelSpecialistsResult:
    findings: list[MergedFinding]
    conflicts: list[Conflict]
    dimension_summary: dict[str, int]


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
    """Reviewer 模式的 Executor：第一版故意留下问题，收到具体 issue 后修正。"""

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
        api_line = "12: input: string, max_length: 256" if "C1" in fixed else "12: input: string"
        config_line = '8: api_key: "${API_KEY}"' if "C2" in fixed else '8: api_key: "sk-demo-plaintext"'
        permission_line = "3-5: roles: reader, writer, admin" if "C3" in fixed else "3-5: roles: admin"
        dependency_line = "requirements.txt: fastapi==0.111.0" if "C4" in fixed else "requirements.txt: fastapi>=0.111"
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
    """Reviewer 只读最终产物和检查清单，不接收 Executor 私有 trace。"""

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

        return ReviewResponse(verdict="approved" if not issues else "rejected", checks=checks, issues=issues)

    def _check(self, item: CheckItem, artifact: str) -> CheckResult:
        if item.id == "C1":
            passed = "max_length: 256" in artifact
            return CheckResult(item.id, passed, "api_schema.yaml:12 包含 max_length" if passed else "api_schema.yaml:12 缺少 max_length", None if passed else "为 input 参数增加 max_length: 256")
        if item.id == "C2":
            passed = "${API_KEY}" in artifact and "sk-demo-plaintext" not in artifact
            return CheckResult(item.id, passed, "config.yaml:8 使用环境变量" if passed else "config.yaml:8 出现明文 api_key", None if passed else "改用 ${API_KEY} 环境变量")
        if item.id == "C3":
            passed = "reader, writer, admin" in artifact
            return CheckResult(item.id, passed, "permissions.py:3-5 区分 reader/writer/admin" if passed else "permissions.py:3-5 只有 admin 角色", None if passed else "拆分 reader 和 writer 角色")
        if item.id == "C4":
            passed = "fastapi==0.111.0" in artifact
            return CheckResult(item.id, passed, "requirements.txt 使用 == 锁定版本" if passed else "requirements.txt 使用 >=，版本未锁定", None if passed else "使用 == 锁定依赖版本")
        return CheckResult(item.id, False, "not_found", "补充可验证证据")

    def _description(self, check_id: str) -> str:
        return {
            "C1": "/api/data 缺少输入长度限制",
            "C2": "API key 明文存储",
            "C3": "权限模型缺少读写分离",
            "C4": "第三方依赖未锁定版本",
        }.get(check_id, "未知审查项未通过")

    def _location(self, check_id: str) -> str:
        return {
            "C1": "api_schema.yaml:12",
            "C2": "config.yaml:8",
            "C3": "permissions.py:3-5",
            "C4": "requirements.txt",
        }.get(check_id, "unknown")


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
                print(f"\n[Reviewer Round {round_index + 1}]")
            review = self.reviewer.run(
                ReviewRequest(original_requirement=task, artifact=draft.output, criteria=criteria, executor_private_trace=None)
            )
            review_trace.append(review)
            if verbose:
                print_review(review)

            if review.verdict == "approved":
                return ReviewerPatternResult("approved", draft.output, round_index + 1, review_trace)

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


class DemoSupervisorAgent:
    """Supervisor 只负责拆解和汇总，不做 Worker 的调研。"""

    def decompose(self, task: str) -> SupervisorPlan:
        fields = ("key_findings", "risks", "recommendations")
        return SupervisorPlan(
            subtasks=[
                Subtask("T1", "Tool Use", "tool_worker", "工具调用链路、失败模式、权限边界", "不分析 Memory 或 Multi-Agent 中的工具协作", fields),
                Subtask("T2", "Memory", "memory_worker", "短期记忆、长期记忆、检索式记忆的工程取舍", "不分析纯 RAG 检索排序细节", fields),
                Subtask("T3", "Planning", "planning_worker", "plan-and-execute、动态重规划、停止条件", "不分析多 Agent 派发策略", fields),
                Subtask("T4", "Multi-Agent", "multi_agent_worker", "Reviewer、Supervisor、Parallel Specialists 的协作边界", "不重复单 Agent Tool Use 机制", fields),
            ]
        )

    def synthesize(self, task: str, plan: SupervisorPlan, results: list[WorkerResult]) -> SupervisorResult:
        missing_topics = [result.topic for result in results if result.status != "ok"]
        lines = [f"# 汇总报告: {task}", ""]
        seen_findings: set[str] = set()
        for result in results:
            lines.append(f"## {result.topic}")
            if result.status != "ok":
                lines.append(f"- 数据缺失: {result.missing_reason}")
                lines.append("")
                continue
            for finding in result.findings:
                if finding not in seen_findings:
                    lines.append(f"- 发现: {finding}")
                    seen_findings.add(finding)
            for risk in result.risks:
                lines.append(f"- 风险: {risk}")
            for recommendation in result.recommendations:
                lines.append(f"- 建议: {recommendation}")
            lines.append("")
        return SupervisorResult(
            status="partial" if missing_topics else "complete",
            plan=plan,
            worker_results=results,
            final_report="\n".join(lines).strip(),
            missing_topics=missing_topics,
        )


class DemoResearchWorker:
    """Worker 按统一模板返回结构化字段，便于 Supervisor 合并。"""

    def __init__(self, name: str, should_fail: bool = False):
        self.name = name
        self.should_fail = should_fail
        self.received_subtasks: list[Subtask] = []

    def execute(self, subtask: Subtask) -> WorkerResult:
        self.received_subtasks.append(subtask)
        if self.should_fail:
            return WorkerResult(subtask.id, self.name, subtask.topic, "failed", [], [], [], "worker_timeout")
        library = {
            "Tool Use": (
                ["工具白名单比 prompt 约束更可靠", "工具结果必须进入可追踪 observation"],
                ["读写工具混给同一 Agent 会放大误操作风险"],
                ["按 Agent 注册最小工具集，并记录 tool_call_id"],
            ),
            "Memory": (
                ["长期记忆应先经过检索和摘要，而不是全量塞回上下文"],
                ["记忆写入需要显式触发条件"],
                ["把用户事实、任务状态、偏好分库存储"],
            ),
            "Planning": (
                ["计划需要可验证 checkpoint，不能只是一段自然语言列表"],
                ["动态重规划必须有停止条件"],
                ["把计划项设计成可执行、可验收的小步"],
            ),
            "Multi-Agent": (
                ["拆分价值来自输入、工具、目标、验收标准的真实差异"],
                ["合并阶段必须保留冲突和缺失，不应自动粉饰"],
                ["优先从 Reviewer 模式开始，再扩展 Supervisor 或多专家"],
            ),
        }
        findings, risks, recommendations = library[subtask.topic]
        return WorkerResult(subtask.id, self.name, subtask.topic, "ok", findings, risks, recommendations)


class SupervisorPattern:
    """Supervisor 拆解 -> Workers 执行 -> Supervisor 汇总。"""

    def __init__(self, supervisor: DemoSupervisorAgent, workers: dict[str, DemoResearchWorker]):
        self.supervisor = supervisor
        self.workers = workers

    def run(self, task: str, verbose: bool = True) -> SupervisorResult:
        plan = self.supervisor.decompose(task)
        results = [self.workers[subtask.worker].execute(subtask) for subtask in plan.subtasks]
        final = self.supervisor.synthesize(task, plan, results)
        if verbose:
            print("\n[Supervisor]")
            print(f"subtasks: {len(plan.subtasks)}, status: {final.status}, missing: {final.missing_topics}")
        return final


class DemoSpecialistAgent:
    """同一个 artifact，不同专家只输出自己维度的发现。"""

    def __init__(self, dimension: str):
        self.dimension = dimension

    def analyze(self, artifact: str, dimension: Dimension) -> SpecialistResult:
        findings = {
            "correctness": [
                SpecialistFinding("F1", "correctness", "checkout.py:18", "missing_validation", "problem", "amount 可以为负数", "must_fix"),
                SpecialistFinding("F2", "correctness", "checkout.py:33", "state_consistency", "problem", "扣库存和创建订单之间没有事务边界", "must_fix"),
            ],
            "security": [
                SpecialistFinding("F3", "security", "checkout.py:18", "missing_validation", "problem", "未校验 amount 可能绕过限额规则", "must_fix"),
                SpecialistFinding("F4", "security", "checkout.py:41", "credential_exposure", "problem", "日志打印 payment_token", "must_fix"),
                SpecialistFinding("F5", "security", "checkout.py:55", "idempotency", "safe", "幂等键由服务端生成且不过期窗口合理", "info"),
            ],
            "performance": [
                SpecialistFinding("F6", "performance", "checkout.py:27", "n_plus_one_query", "problem", "循环中逐个查询 coupon", "should_fix"),
                SpecialistFinding("F7", "performance", "checkout.py:55", "idempotency", "problem", "幂等记录未设置索引，订单高峰期会拖慢写入", "should_fix"),
            ],
        }[self.dimension]
        return SpecialistResult(dimension.name, findings)


class ParallelSpecialists:
    """多个专家并行处理同一输入的不同维度，并在合并时保留冲突。"""

    def __init__(self, specialists: dict[str, DemoSpecialistAgent]):
        self.specialists = specialists

    def run(self, artifact: str, dimensions: list[Dimension], verbose: bool = True) -> ParallelSpecialistsResult:
        results = [self.specialists[dimension.agent].analyze(artifact, dimension) for dimension in dimensions]
        final = self.merge(results)
        if verbose:
            print("\n[Parallel Specialists]")
            print(f"findings: {len(final.findings)}, conflicts: {len(final.conflicts)}")
        return final

    def merge(self, results: list[SpecialistResult]) -> ParallelSpecialistsResult:
        grouped: dict[tuple[str, str, str], list[SpecialistFinding]] = {}
        conflicts: list[Conflict] = []
        dimension_summary = {result.dimension: len(result.findings) for result in results}

        for result in results:
            for finding in result.findings:
                grouped.setdefault((finding.location, finding.problem_type, finding.judgment), []).append(finding)

        findings: list[MergedFinding] = []
        for (location, problem_type, judgment), items in grouped.items():
            findings.append(
                MergedFinding(
                    location=location,
                    problem_type=problem_type,
                    judgment=judgment,
                    dimensions=sorted({item.dimension for item in items}),
                    evidence=[item.evidence for item in items],
                    severity=max((item.severity for item in items), key=severity_rank),
                )
            )

        by_location_type: dict[tuple[str, str], set[str]] = {}
        by_location_dimensions: dict[tuple[str, str], set[str]] = {}
        for finding in findings:
            key = (finding.location, finding.problem_type)
            by_location_type.setdefault(key, set()).add(finding.judgment)
            by_location_dimensions.setdefault(key, set()).update(finding.dimensions)
        for (location, problem_type), judgments in by_location_type.items():
            if len(judgments) > 1:
                conflicts.append(
                    Conflict(
                        location=location,
                        problem_type=problem_type,
                        judgments=sorted(judgments),
                        dimensions=sorted(by_location_dimensions[(location, problem_type)]),
                    )
                )

        return ParallelSpecialistsResult(findings=findings, conflicts=conflicts, dimension_summary=dimension_summary)


def severity_rank(value: str) -> int:
    return {"info": 0, "should_fix": 1, "must_fix": 2}.get(value, -1)


def default_criteria() -> list[CheckItem]:
    return [
        CheckItem("C1", "输入长度限制", "检查 /api/data 的 input 参数是否声明 max_length", "must_fix"),
        CheckItem("C2", "密钥管理", "检查配置示例是否使用环境变量而不是明文 key", "must_fix"),
        CheckItem("C3", "权限模型", "检查是否区分 reader 和 writer 角色", "must_fix"),
        CheckItem("C4", "依赖锁定", "检查依赖是否使用 == 锁定版本", "should_fix"),
    ]


def default_workers(failing_worker: str | None = None) -> dict[str, DemoResearchWorker]:
    return {
        "tool_worker": DemoResearchWorker("tool_worker", should_fail=failing_worker == "tool_worker"),
        "memory_worker": DemoResearchWorker("memory_worker", should_fail=failing_worker == "memory_worker"),
        "planning_worker": DemoResearchWorker("planning_worker", should_fail=failing_worker == "planning_worker"),
        "multi_agent_worker": DemoResearchWorker("multi_agent_worker", should_fail=failing_worker == "multi_agent_worker"),
    }


def default_dimensions() -> list[Dimension]:
    return [
        Dimension("correctness", "correctness_agent", "逻辑错误、边界条件、异常处理、状态一致性", "不分析安全漏洞和性能瓶颈"),
        Dimension("security", "security_agent", "注入风险、密钥泄露、权限越界、敏感数据暴露", "不分析普通逻辑错误和性能瓶颈"),
        Dimension("performance", "performance_agent", "时间复杂度、I/O 瓶颈、索引和缓存策略", "不分析正确性和安全性影响"),
    ]


def default_specialists() -> dict[str, DemoSpecialistAgent]:
    return {
        "correctness_agent": DemoSpecialistAgent("correctness"),
        "security_agent": DemoSpecialistAgent("security"),
        "performance_agent": DemoSpecialistAgent("performance"),
    }


def print_review(review: ReviewResponse) -> None:
    print(f"verdict: {review.verdict}")
    for check in review.checks:
        status = "PASS" if check.passed else "FAIL"
        print(f"  {check.check_id}: {status} - {check.evidence}")


def main() -> None:
    reviewer_result = ReviewerPattern(DemoExecutorAgent(), DemoReviewerAgent()).run(
        "写一份 API 模块技术方案，并从安全角度审查", default_criteria()
    )
    print("\nReviewer 最终状态:", reviewer_result.status)

    supervisor_result = SupervisorPattern(DemoSupervisorAgent(), default_workers()).run(
        "调研 Agent 架构的四个主流方向"
    )
    print(supervisor_result.final_report)

    specialists_result = ParallelSpecialists(default_specialists()).run(
        "checkout.py 代码片段", default_dimensions()
    )
    for conflict in specialists_result.conflicts:
        print(f"冲突: {conflict.location} {conflict.problem_type} -> {conflict.judgments}")


if __name__ == "__main__":
    main()
