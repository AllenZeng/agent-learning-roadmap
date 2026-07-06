#!/usr/bin/env python3
"""
Course 05-08 Multi-Agent example

The same offline example project demonstrates three collaboration patterns from the course:
  1. Reviewer: one Agent writes a proposal while another independently reviews it
  2. Supervisor: one Supervisor decomposes the task while multiple Workers produce structured results in parallel
  3. Parallel Specialists: multiple specialists inspect the same input and analyze it in parallel from different dimensions

The example does not call a real LLM; deterministic functions simulate Agent behavior so data boundaries,
communication protocols, stopping conditions, and merge rules are easy to observe.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AgentConfig:
    name: str
    inputs: set[str]
    tools: set[str]
    goal: str
    acceptance: str


@dataclass(frozen=True)
class AgentPrompt:
    """In a real system, this role definition would be passed to the model as the system prompt."""

    name: str
    role: str
    system_prompt: str
    response_contract: str
    must_not: tuple[str, ...] = ()


@dataclass(frozen=True)
class LLMCall:
    agent: str
    system_prompt: str
    user_payload: dict[str, Any]
    response_contract: str


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


class MockLLM:
    """Offline simulated LLM adapter: records the prompt and returns deterministic structured responses."""

    def __init__(self):
        self.calls: list[LLMCall] = []

    def complete(self, prompt: AgentPrompt, user_payload: dict[str, Any]) -> dict[str, Any]:
        self.calls.append(
            LLMCall(
                agent=prompt.name,
                system_prompt=prompt.system_prompt,
                user_payload=user_payload,
                response_contract=prompt.response_contract,
            )
        )
        if prompt.name == "executor":
            fixed = set(user_payload.get("applied_issue_ids", []))
            return {
                "output": render_api_plan(fixed),
                "private_trace": (
                    "For the local demo, first use a plaintext key; simplify the permission model to admin;"
                    "dependency versions are not pinned yet and will be completed later."
                ),
            }
        if prompt.name == "reviewer":
            return {"review": build_review_response(user_payload["criteria"], user_payload["artifact"])}
        if prompt.name == "supervisor":
            return {"note": "decompose_or_synthesize"}
        if prompt.name.endswith("_worker") or prompt.name.endswith("_agent"):
            return {"note": "specialized_analysis"}
        return {"note": "mock_response"}


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
    """The four differences from course 8.2: input, tools, goal, and acceptance criteria."""
    differences = {
        "inputs": left.inputs != right.inputs,
        "tools": left.tools != right.tools,
        "goal": left.goal != right.goal,
        "acceptance": left.acceptance != right.acceptance,
    }
    return {**differences, "total": sum(1 for value in differences.values() if value)}


class DemoExecutorAgent:
    """Executor in Reviewer mode: the first version intentionally leaves issues and corrects them after receiving specific issues."""

    def __init__(
        self,
        fixable_issue_ids: set[str] | None = None,
        llm: MockLLM | None = None,
        prompt: AgentPrompt | None = None,
    ):
        self.fixable_issue_ids = fixable_issue_ids
        self.llm = llm or MockLLM()
        self.prompt = prompt or default_agent_prompts()["executor"]
        self.revisions: list[list[str]] = []

    def run(self, task: str, fix_instructions: list[Issue] | None = None) -> Draft:
        applied = self._applicable_issue_ids(fix_instructions or [])
        self.revisions.append(sorted(applied))
        response = self.llm.complete(
            self.prompt,
            {
                "task": task,
                "fix_instructions": [issue.__dict__ for issue in fix_instructions or []],
                "applied_issue_ids": sorted(applied),
            },
        )
        return Draft(output=response["output"], private_trace=response["private_trace"])

    def _applicable_issue_ids(self, issues: list[Issue]) -> set[str]:
        issue_ids = {issue.id for issue in issues}
        if self.fixable_issue_ids is None:
            return issue_ids
        return issue_ids & self.fixable_issue_ids


class DemoReviewerAgent:
    """The Reviewer reads only the final artifact and checklist, not the Executor private trace."""

    def __init__(self, llm: MockLLM | None = None, prompt: AgentPrompt | None = None):
        self.llm = llm or MockLLM()
        self.prompt = prompt or default_agent_prompts()["reviewer"]
        self.review_requests: list[ReviewRequest] = []
        self.seen_private_traces: list[str] = []

    def run(self, request: ReviewRequest) -> ReviewResponse:
        self.review_requests.append(request)
        if request.executor_private_trace:
            self.seen_private_traces.append(request.executor_private_trace)

        response = self.llm.complete(
            self.prompt,
            {
                "original_requirement": request.original_requirement,
                "artifact": request.artifact,
                "criteria": request.criteria,
            },
        )
        return response["review"]

    def _check(self, item: CheckItem, artifact: str) -> CheckResult:
        return check_item(item, artifact)

    def _description(self, check_id: str) -> str:
        return issue_description(check_id)

    def _location(self, check_id: str) -> str:
        return issue_location(check_id)


class ReviewerPattern:
    """Executor output -> Reviewer review -> Executor correction or disagreement escalation."""

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
                    print("[Runtime] Only concrete issues are sent back to the Executor, not subjective judgments.")
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
    """The Supervisor only decomposes and summarizes; it does not do Worker research."""

    def __init__(self, llm: MockLLM | None = None, prompt: AgentPrompt | None = None):
        self.llm = llm or MockLLM()
        self.prompt = prompt or default_agent_prompts()["supervisor"]

    def decompose(self, task: str) -> SupervisorPlan:
        self.llm.complete(self.prompt, {"operation": "decompose", "task": task})
        fields = ("key_findings", "risks", "recommendations")
        return SupervisorPlan(
            subtasks=[
                Subtask("T1", "Tool Use", "tool_worker", "tool-calling path, failure modes, permission boundaries", "do not analyze tool collaboration inside Memory or Multi-Agent systems", fields),
                Subtask("T2", "Memory", "memory_worker", "engineering tradeoffs among short-term memory, long-term memory, and retrieval memory", "do not analyze pure RAG retrieval-ranking details", fields),
                Subtask("T3", "Planning", "planning_worker", "plan-and-execute, dynamic replanning, stopping conditions", "do not analyze Multi-Agent dispatch strategies", fields),
                Subtask("T4", "Multi-Agent", "multi_agent_worker", "collaboration boundaries of Reviewer, Supervisor, and Parallel Specialists", "do not repeat single-Agent Tool Use mechanics", fields),
            ]
        )

    def synthesize(self, task: str, plan: SupervisorPlan, results: list[WorkerResult]) -> SupervisorResult:
        self.llm.complete(self.prompt, {"operation": "synthesize", "task": task, "result_count": len(results)})
        missing_topics = [result.topic for result in results if result.status != "ok"]
        lines = [f"# Summary report: {task}", ""]
        seen_findings: set[str] = set()
        for result in results:
            lines.append(f"## {result.topic}")
            if result.status != "ok":
                lines.append(f"- missing data: {result.missing_reason}")
                lines.append("")
                continue
            for finding in result.findings:
                if finding not in seen_findings:
                    lines.append(f"- Finding: {finding}")
                    seen_findings.add(finding)
            for risk in result.risks:
                lines.append(f"- Risks: {risk}")
            for recommendation in result.recommendations:
                lines.append(f"- Recommendations: {recommendation}")
            lines.append("")
        return SupervisorResult(
            status="partial" if missing_topics else "complete",
            plan=plan,
            worker_results=results,
            final_report="\n".join(lines).strip(),
            missing_topics=missing_topics,
        )


class DemoResearchWorker:
    """Workers return structured fields using a unified template so the Supervisor can merge them."""

    def __init__(
        self,
        name: str,
        should_fail: bool = False,
        llm: MockLLM | None = None,
        prompt: AgentPrompt | None = None,
    ):
        self.name = name
        self.should_fail = should_fail
        self.llm = llm or MockLLM()
        self.prompt = prompt or default_agent_prompts().get(name, default_agent_prompts()["research_worker"])
        self.received_subtasks: list[Subtask] = []

    def execute(self, subtask: Subtask) -> WorkerResult:
        self.received_subtasks.append(subtask)
        self.llm.complete(self.prompt, {"subtask": subtask})
        if self.should_fail:
            return WorkerResult(subtask.id, self.name, subtask.topic, "failed", [], [], [], "worker_timeout")
        library = {
            "Tool Use": (
                ["Tool allowlists are more reliable than prompt constraints", "Tool results must enter traceable observations"],
                ["Giving read and write tools to the same Agent amplifies misuse risk"],
                ["Register the minimal tool set per Agent and record tool_call_id"],
            ),
            "Memory": (
                ["Long-term memory should go through retrieval and summarization before being inserted into context, not be inserted wholesale"],
                ["Memory writes need explicit trigger conditions"],
                ["Store user facts, task state, and preferences in separate stores"],
            ),
            "Planning": (
                ["Plans need verifiable checkpoints, not just a natural-language list"],
                ["Dynamic replanning must have stopping conditions"],
                ["Design plan items as executable and acceptable small steps"],
            ),
            "Multi-Agent": (
                ["Decomposition value comes from real differences in input, tools, goals, and acceptance criteria"],
                ["The merge stage must preserve conflicts and missing data instead of smoothing them over"],
                ["Start with Reviewer mode first, then expand to Supervisor or multiple specialists"],
            ),
        }
        findings, risks, recommendations = library[subtask.topic]
        return WorkerResult(subtask.id, self.name, subtask.topic, "ok", findings, risks, recommendations)


class SupervisorPattern:
    """Supervisor decomposes -> Workers execute -> Supervisor summarizes."""

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
    """For the same artifact, each specialist outputs findings only for their own dimension."""

    def __init__(self, dimension: str, llm: MockLLM | None = None, prompt: AgentPrompt | None = None):
        self.dimension = dimension
        self.llm = llm or MockLLM()
        self.prompt = prompt or default_agent_prompts().get(f"{dimension}_agent", default_agent_prompts()["specialist_agent"])

    def analyze(self, artifact: str, dimension: Dimension) -> SpecialistResult:
        self.llm.complete(self.prompt, {"artifact": artifact, "dimension": dimension})
        findings = {
            "correctness": [
                SpecialistFinding("F1", "correctness", "checkout.py:18", "missing_validation", "problem", "amount can be negative", "must_fix"),
                SpecialistFinding("F2", "correctness", "checkout.py:33", "state_consistency", "problem", "there is no transaction boundary between inventory deduction and order creation", "must_fix"),
            ],
            "security": [
                SpecialistFinding("F3", "security", "checkout.py:18", "missing_validation", "problem", "unvalidated amount may bypass limit rules", "must_fix"),
                SpecialistFinding("F4", "security", "checkout.py:41", "credential_exposure", "problem", "logs print payment_token", "must_fix"),
                SpecialistFinding("F5", "security", "checkout.py:55", "idempotency", "safe", "idempotency keys are generated server-side and the expiration window is reasonable", "info"),
            ],
            "performance": [
                SpecialistFinding("F6", "performance", "checkout.py:27", "n_plus_one_query", "problem", "loop queries coupons one by one", "should_fix"),
                SpecialistFinding("F7", "performance", "checkout.py:55", "idempotency", "problem", "idempotency records lack an index and will slow writes during order peaks", "should_fix"),
            ],
        }[self.dimension]
        return SpecialistResult(dimension.name, findings)


class ParallelSpecialists:
    """Multiple specialists process different dimensions of the same input in parallel and preserve conflicts during merge."""

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


def default_agent_prompts() -> dict[str, AgentPrompt]:
    return {
        "executor": AgentPrompt(
            name="executor",
            role="proposal executor",
            system_prompt=(
                "You are the Executor Agent. Your job is to produce a deliverable plan based on the user's requirements,"
                "process only structured issues returned by the Reviewer, and do not read the Reviewer's private reasoning."
            ),
            response_contract="Return {output: markdown, private_trace: string}",
            must_not=("do not declare the review passed by yourself", "do not write unverified assumptions as facts"),
        ),
        "reviewer": AgentPrompt(
            name="reviewer",
            role="independent reviewer",
            system_prompt=(
                "You are the Reviewer Agent. Your job is to review only the final artifact and checklist,"
                "and provide pass/fail, evidence, severity, and actionable recommendations for each item."
            ),
            response_contract="Return ReviewResponse: {verdict, checks[], issues[]}",
            must_not=("Do not read Executor private_trace", "do not modify the artifact itself"),
        ),
        "supervisor": AgentPrompt(
            name="supervisor",
            role="task orchestrator",
            system_prompt=(
                "You are the Supervisor Agent. Your job is to decompose tasks and define scope/exclude for each subtask,"
                "and preserve missing data and conflicts during summarization."
            ),
            response_contract="Return SupervisorPlan or SupervisorResult",
            must_not=("do not do specialist research for Workers", "do not hide failed Workers"),
        ),
        "research_worker": AgentPrompt(
            name="research_worker",
            role="topic research Worker",
            system_prompt=(
                "You are a Research Worker. You only process your assigned topic and return structured fields for key_findings, risks,"
                "and recommendations."
            ),
            response_contract="Return WorkerResult",
            must_not=("do not analyze areas excluded by exclude", "do not output free-form prose"),
        ),
        "specialist_agent": AgentPrompt(
            name="specialist_agent",
            role="single-dimension specialist",
            system_prompt=(
                "You are a Specialist Agent. Analyze the same input only from the specified dimension and output mergeable findings,"
                "do not make final judgments for other dimensions."
            ),
            response_contract="Return SpecialistResult",
            must_not=("do not automatically resolve cross-dimension conflicts", "do not expand beyond the focus dimension"),
        ),
        "tool_worker": AgentPrompt(
            name="tool_worker",
            role="Tool Use topic Worker",
            system_prompt="You only study the tool-calling path, failure modes, and permission boundaries.",
            response_contract="Return WorkerResult",
            must_not=("do notanalysis Memory text Multi-Agent mediumtext",),
        ),
        "memory_worker": AgentPrompt(
            name="memory_worker",
            role="Memory topic Worker",
            system_prompt="You only study engineering tradeoffs among short-term memory, long-term memory, and retrieval memory.",
            response_contract="Return WorkerResult",
            must_not=("do notanalysistext RAG text",),
        ),
        "planning_worker": AgentPrompt(
            name="planning_worker",
            role="Planning topic Worker",
            system_prompt="You only study plan-and-execute, dynamic replanning, and stopping conditions.",
            response_contract="Return WorkerResult",
            must_not=("do notanalysismany Agent text",),
        ),
        "multi_agent_worker": AgentPrompt(
            name="multi_agent_worker",
            role="Multi-Agent topic Worker",
            system_prompt="You only study collaboration boundaries of Reviewer, Supervisor, and Parallel Specialists.",
            response_contract="Return WorkerResult",
            must_not=("do nottext Agent Tool Use text",),
        ),
        "correctness_agent": AgentPrompt(
            name="correctness_agent",
            role="correctness specialist",
            system_prompt="You only check logic errors, boundary conditions, exception handling, and state consistency.",
            response_contract="Return SpecialistResult",
            must_not=("do not analyze security vulnerabilities or performance bottlenecks",),
        ),
        "security_agent": AgentPrompt(
            name="security_agent",
            role="security specialist",
            system_prompt="You only check injection risks, secret leakage, permission boundary violations, and sensitive data exposure.",
            response_contract="Return SpecialistResult",
            must_not=("do not analyze ordinary logic errors or performance bottlenecks",),
        ),
        "performance_agent": AgentPrompt(
            name="performance_agent",
            role="performance specialist",
            system_prompt="You only check time complexity, I/O bottlenecks, indexes, and caching strategy.",
            response_contract="Return SpecialistResult",
            must_not=("do not analyze correctness or security impact",),
        ),
    }


def render_api_plan(fixed: set[str]) -> str:
    api_line = "12: input: string, max_length: 256" if "C1" in fixed else "12: input: string"
    config_line = '8: api_key: "${API_KEY}"' if "C2" in fixed else '8: api_key: "sk-demo-plaintext"'
    permission_line = "3-5: roles: reader, writer, admin" if "C3" in fixed else "3-5: roles: admin"
    dependency_line = "requirements.txt: fastapi==0.111.0" if "C4" in fixed else "requirements.txt: fastapi>=0.111"
    return "\n".join(
        [
            "# API Module Technical Plan",
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


def build_review_response(criteria: list[CheckItem], artifact: str) -> ReviewResponse:
    checks: list[CheckResult] = []
    issues: list[Issue] = []
    for item in criteria:
        result = check_item(item, artifact)
        checks.append(result)
        if not result.passed:
            issues.append(
                Issue(
                    id=item.id,
                    description=issue_description(item.id),
                    location=issue_location(item.id),
                    severity=item.severity,
                    suggestion=result.suggestion or "Fill missing constraints according to review items",
                )
            )
    return ReviewResponse(verdict="approved" if not issues else "rejected", checks=checks, issues=issues)


def check_item(item: CheckItem, artifact: str) -> CheckResult:
    if item.id == "C1":
        passed = "max_length: 256" in artifact
        return CheckResult(item.id, passed, "api_schema.yaml:12 contains max_length" if passed else "api_schema.yaml:12 Missing max_length", None if passed else "Add max_length: 256 to the input parameter")
    if item.id == "C2":
        passed = "${API_KEY}" in artifact and "sk-demo-plaintext" not in artifact
        return CheckResult(item.id, passed, "config.yaml:8 uses environment variables" if passed else "config.yaml:8 contains plaintext api_key", None if passed else "Use the ${API_KEY} environment variable")
    if item.id == "C3":
        passed = "reader, writer, admin" in artifact
        return CheckResult(item.id, passed, "permissions.py:3-5 distinguishes reader/writer/admin" if passed else "permissions.py:3-5 only has the admin role", None if passed else "Split reader and writer roles")
    if item.id == "C4":
        passed = "fastapi==0.111.0" in artifact
        return CheckResult(item.id, passed, "requirements.txt uses == pinned versions" if passed else "requirements.txt uses >=, versions are not pinned", None if passed else "Use == to pin dependency versions")
    return CheckResult(item.id, False, "not_found", "Add verifiable evidence")


def issue_description(check_id: str) -> str:
    return {
        "C1": "/api/data MissingInput length limit",
        "C2": "API key stored in plaintext",
        "C3": "Permission model is missing read/write separation",
        "C4": "Third-party dependencies are not pinned",
    }.get(check_id, "Unknown review item failed")


def issue_location(check_id: str) -> str:
    return {
        "C1": "api_schema.yaml:12",
        "C2": "config.yaml:8",
        "C3": "permissions.py:3-5",
        "C4": "requirements.txt",
    }.get(check_id, "unknown")


def default_criteria() -> list[CheckItem]:
    return [
        CheckItem("C1", "Input length limit", "Check whether the input parameter of /api/data declares max_length", "must_fix"),
        CheckItem("C2", "secret management", "Check whether the config example uses environment variables instead of plaintext keys", "must_fix"),
        CheckItem("C3", "permission model", "Check whether reader and writer roles are separated", "must_fix"),
        CheckItem("C4", "dependency pinning", "Check whether dependencies use == pinned versions", "should_fix"),
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
        Dimension("correctness", "correctness_agent", "logic errors, boundary conditions, exception handling, state consistency", "textanalysistext"),
        Dimension("security", "security_agent", "injection risks, secret leakage, permission boundary violations, sensitive data exposure", "textanalysistexterrortext"),
        Dimension("performance", "performance_agent", "time complexity, I/O bottlenecks, indexes, caching strategy", "textanalysistext"),
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
        "Write a technical plan for the API module，and review it from a security perspective", default_criteria()
    )
    print("\nReviewer final status:", reviewer_result.status)

    supervisor_result = SupervisorPattern(DemoSupervisorAgent(), default_workers()).run(
        "Research four mainstream directions in Agent architecture"
    )
    print(supervisor_result.final_report)

    specialists_result = ParallelSpecialists(default_specialists()).run(
        "checkout.py code snippet", default_dimensions()
    )
    for conflict in specialists_result.conflicts:
        print(f"Conflict: {conflict.location} {conflict.problem_type} -> {conflict.judgments}")


if __name__ == "__main__":
    main()
