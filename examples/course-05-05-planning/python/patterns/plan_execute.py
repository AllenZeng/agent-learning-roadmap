"""
Plan-Execute pattern：generate a plan first，then execute according to the plan

This is Planning text。when facing complex tasks，
first let the modelMove textstep，user confirmationthen execute step by step。
during executionmediumtextfailed，can triggerreplan——from currentStatusgenerate newlaterstep。

Use case：mediumtext、manystep、needsuser confirmationtextmediumtextreplan。
"""

from dataclasses import dataclass, field
from typing import Callable, Optional
from scenario import (
    StepResult, StepStatus, TOOL_REGISTRY,
    STEP_DEPENDENCIES, DEFAULT_MAX_RETRIES,
)


@dataclass
class PlanStep:
    """planmediumtextstep"""
    name: str
    tool: str
    description: str = ""
    depends_on: list[str] = field(default_factory=list)
    retries: int = 0
    max_retries: int = DEFAULT_MAX_RETRIES
    status: str = "pending"   # pending | running | completed | failed | skipped


@dataclass
class Plan:
    """Execution plan"""
    goal: str
    steps: list[PlanStep]
    completed_steps: list[str] = field(default_factory=list)


@dataclass
class PlanExecuteResult:
    """Plan-Execute Execution result"""
    status: str                      # completed | failed | rejected
    plan: Optional[Plan] = None
    results: list[StepResult] = field(default_factory=list)
    replan_count: int = 0
    context: dict = field(default_factory=dict)
    error: Optional[str] = None


class PlanExecuteExecutor:
    """
    Plan-Execute executor。

    core flow：
    1. generate_plan(goal) → structured plan
    2. user confirmationplan
    3. execute step by step：
       - success → textcomplete，textNext step
       - failed → retry（at most max_retries times)
       - retryexhausted → trigger replan()，generate newlaterstep
    4. textstepcomplete → ReturnResult

    compared with Chain key difference：
    - Chain: stepfixed，stop on error
    - Plan-Execute: steptext，failedtextreplan
    """

    def __init__(self, max_replan_count: int = 2):
        self.max_replan_count = max_replan_count
        self._replan_count = 0

    def generate_plan(self, goal: str) -> Plan:
        """
        textExecution plan——analysisGoal，textstep。

        textmediumtext LLM call，text goal + available toolstext。
        this uses rules to simulate：text goal keywordmatchessteptext。
        """
        goal_lower = goal.lower()

        # Match step templates by goal
        if any(w in goal_lower for w in ["release", "release"]):
            steps = [
                PlanStep(
                    name="Check README", tool="Check README",
                    description="Check README completeness：verify required sections exist",
                    depends_on=[],
                ),
                PlanStep(
                    name="Run tests", tool="Run tests",
                    description="Run full test suite，ensure all case pass",
                    depends_on=[],
                ),
                PlanStep(
                    name="Prepare changelog", tool="Prepare changelog",
                    description="based on git log textcosttimesreleasetext changelog",
                    depends_on=["Run tests"],
                ),
                PlanStep(
                    name="Generate checklist", tool="Generate checklist",
                    description="Generate release checklist，summarize all pending confirmation items",
                    depends_on=["Check README", "Run tests", "Prepare changelog"],
                ),
            ]
        elif any(w in goal_lower for w in ["fix", "bug", "fix"]):
            steps = [
                PlanStep(
                    name="Run tests", tool="Run tests",
                    description="textRun tests，confirm bug can be reproduced",
                    depends_on=[],
                ),
                PlanStep(
                    name="Prepare changelog", tool="Prepare changelog",
                    description="textfixtext",
                    depends_on=["Run tests"],
                ),
            ]
        else:
            # Generic step template
            steps = [
                PlanStep(
                    name="Check README", tool="Check README",
                    description="check documentation completeness",
                    depends_on=[],
                ),
                PlanStep(
                    name="Run tests", tool="Run tests",
                    description="run tests for validation",
                    depends_on=[],
                ),
            ]

        return Plan(goal=goal, steps=steps)

    def generate_plan_text(self, plan: Plan) -> str:
        """text（textuser confirmation)"""
        lines = [f"Execution plan: {plan.goal}", "=" * 50, ""]
        for i, step in enumerate(plan.steps, 1):
            deps = f" [dependencies: {', '.join(step.depends_on)}]" if step.depends_on else ""
            lines.append(f"  step {i}. {step.name}{deps}")
            lines.append(f"      {step.description}")
        lines.append("")
        lines.append(f"  total {len(plan.steps)} itemsstep")
        lines.append(f"  maximumretrytimestext: {DEFAULT_MAX_RETRIES}")
        return "\n".join(lines)

    def replan(
        self,
        goal: str,
        completed_steps: list[str],
        failed_step: str,
        error: str,
    ) -> list[PlanStep]:
        """
        replan——textfailedtext，textStatusgenerate newlaterstep。

        This is Plan-Execute compared with Chain text：
        Chain stop on error，Plan-Execute textpath。

        Args:
            goal: textGoal
            completed_steps: Completedtextsteptext
            failed_step: failedtextsteptext
            error: failure reason
        """
        self._replan_count += 1

        # Choose a replanning strategy based on the failure reason
        new_steps = []

        if "FileNotFound" in error or "does not exist" in error:
            # File missing -> skip the current step and use an alternative step
            new_steps.append(PlanStep(
                name=f"alternative ({failed_step})",
                tool="Generate checklist",
                description=f"because {failed_step} failed（{error})，use alternative",
                depends_on=[],
            ))

        elif "test failed" in error or "AssertionError" in error:
            # Test failed -> insert an "analyze failure reason" step
            new_steps.append(PlanStep(
                name=f"analysis {failed_step} failure reason",
                tool="Run tests",
                description=f"rerun tests to confirm the failure reason: {error}",
                depends_on=[],
            ))
            # Continue with the remaining steps of the original plan
            remaining = [s for s in ["Prepare changelog", "Generate checklist"]
                        if s not in completed_steps]
            for s in remaining:
                new_steps.append(PlanStep(
                    name=s, tool=s,
                    description=f"continue execution: {s}",
                    depends_on=[new_steps[-1].name] if new_steps else [],
                ))

        else:
            # Generic error -> skip the failed step and continue remaining steps
            remaining = [s for s in ["Prepare changelog", "Generate checklist"]
                        if s not in completed_steps and s != failed_step]
            for s in remaining:
                new_steps.append(PlanStep(
                    name=s, tool=s,
                    description=f"skip {failed_step}，continue execution: {s}",
                    depends_on=[],
                ))

        return new_steps

    def execute(
        self,
        goal: str,
        context: Optional[dict] = None,
        auto_confirm: bool = True,
        inject_failures: Optional[dict[str, bool]] = None,
        on_plan: Optional[Callable[[Plan], None]] = None,
        on_step_start: Optional[Callable[[str], None]] = None,
        on_step_end: Optional[Callable[[StepResult], None]] = None,
        on_replan: Optional[Callable[[str, list[PlanStep]], None]] = None,
    ) -> PlanExecuteResult:
        """
        Plan-Execute main flow。

        Args:
            goal: TaskGoal
            context: initial context
            auto_confirm: True textskipuser confirmation（demo mode)
            inject_failures: steptext → textfailed（for demoreplan)
            on_plan: callback after plan generation
            on_step_start: stepstartedtext
            on_step_end: steptext
            on_replan: replantext
        """
        self._replan_count = 0
        ctx = context or {}
        inject_failures = inject_failures or {}

        # ── Step 1: generate plan ──
        plan = self.generate_plan(goal)
        if on_plan:
            on_plan(plan)

        # ── Step 2: user confirmation (auto-confirmed in demo mode)──
        if not auto_confirm:
            return PlanExecuteResult(
                status="waiting_confirmation",
                plan=plan,
                context=ctx,
                error="textuser confirmationtext",
            )

        # ── Step 3: execute step by step ──
        result = PlanExecuteResult(status="completed", plan=plan, context=ctx)
        i = 0
        seen_replans: set[tuple[str, ...]] = set()

        while i < len(plan.steps):
            step = plan.steps[i]

            # Check whether dependencies are satisfied
            unmet = [d for d in step.depends_on if d not in plan.completed_steps]
            if unmet:
                # If dependencies are not satisfied, execute dependency steps first
                # Insert unsatisfied dependencies before the current position
                for dep_name in unmet:
                    if dep_name not in [s.name for s in plan.steps[:i]]:
                        dep_step = PlanStep(
                            name=dep_name, tool=dep_name,
                            description=f"dependency step: {dep_name}",
                            depends_on=[],
                        )
                        plan.steps.insert(i, dep_step)
                continue  # Process the current position again

            step.status = "running"
            if on_step_start:
                on_step_start(step.name)

            # Find and execute the tool
            tool = TOOL_REGISTRY.get(step.tool)
            if not tool:
                step_result = StepResult(
                    step_name=step.name,
                    status=StepStatus.ERROR,
                    error=f"Tool not found: {step.tool}",
                )
            else:
                # Check whether a failure should be injected
                should_fail = inject_failures.get(step.name, False)
                step_result = tool(fail=should_fail)

            result.results.append(step_result)
            ctx[step.name] = step_result.output

            if on_step_end:
                on_step_end(step_result)

            # ── Handle failure ──
            if step_result.status == StepStatus.ERROR:
                step.retries += 1

                if step.retries < step.max_retries:
                    # Retry
                    step.status = "pending"
                    continue
                else:
                    # Retries exhausted -> trigger replanning
                    if self._replan_count >= self.max_replan_count:
                        result.status = "failed"
                        result.error = (
                            f"reached maximum replan count {self.max_replan_count}，"
                            f"stopped at step '{step.name}'"
                        )
                        result.replan_count = self._replan_count
                        return result

                    new_steps = self.replan(
                        goal=plan.goal,
                        completed_steps=plan.completed_steps,
                        failed_step=step.name,
                        error=step_result.error or "texterror",
                    )
                    step.status = "failed"
                    signature = tuple(s.name for s in new_steps)

                    if on_replan:
                        on_replan(step.name, new_steps)

                    if not new_steps:
                        # Replanning produced no alternative steps, so the task fails
                        result.status = "failed"
                        result.error = f"step '{step.name}' failed and cannot be replanned"
                        result.replan_count = self._replan_count
                        return result

                    if signature in seen_replans:
                        result.status = "failed"
                        result.error = "replan generated duplicate steps; stopping to avoid a loop"
                        result.replan_count = self._replan_count
                        return result
                    seen_replans.add(signature)

                    # Replace the current and later steps with new steps
                    plan.steps = (
                        plan.steps[:i] +  # Processed steps (including the failed one)
                        new_steps           # Newly generated steps
                    )
                    result.replan_count = self._replan_count
                    continue

            # Success
            step.status = "completed"
            plan.completed_steps.append(step.name)
            i += 1

        result.status = "completed"
        result.replan_count = self._replan_count
        return result
