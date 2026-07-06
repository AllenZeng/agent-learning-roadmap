"""
Plan-Execute 模式：先生成计划，再按计划执行

这是 Planning 最经典的实现。面对复杂任务时，
先让模型把任务拆成结构化步骤，用户确认后再逐步执行。
执行过程中如果某步失败，可以触发重规划——从当前状态生成新的后续步骤。

适用场景：中长任务、多步骤、需要用户确认或中途重规划。
"""

from dataclasses import dataclass, field
from typing import Callable, Optional
from scenario import (
    StepResult, StepStatus, TOOL_REGISTRY,
    STEP_DEPENDENCIES, DEFAULT_MAX_RETRIES,
)


@dataclass
class PlanStep:
    """计划中的一个步骤"""
    name: str
    tool: str
    description: str = ""
    depends_on: list[str] = field(default_factory=list)
    retries: int = 0
    max_retries: int = DEFAULT_MAX_RETRIES
    status: str = "pending"   # pending | running | completed | failed | skipped


@dataclass
class Plan:
    """执行计划"""
    goal: str
    steps: list[PlanStep]
    completed_steps: list[str] = field(default_factory=list)


@dataclass
class PlanExecuteResult:
    """Plan-Execute 执行结果"""
    status: str                      # completed | failed | rejected
    plan: Optional[Plan] = None
    results: list[StepResult] = field(default_factory=list)
    replan_count: int = 0
    context: dict = field(default_factory=dict)
    error: Optional[str] = None


class PlanExecuteExecutor:
    """
    Plan-Execute 执行器。

    核心流程：
    1. generate_plan(goal) → 结构化计划
    2. 用户确认计划
    3. 逐步执行：
       - 成功 → 标记完成，继续下一步
       - 失败 → 重试（最多 max_retries 次）
       - 重试耗尽 → 触发 replan()，生成新的后续步骤
    4. 所有步骤完成 → 返回结果

    与 Chain 的关键区别：
    - Chain: 步骤固定，遇错即停
    - Plan-Execute: 步骤可动态调整，失败可重规划
    """

    def __init__(self, max_replan_count: int = 2):
        self.max_replan_count = max_replan_count
        self._replan_count = 0

    def generate_plan(self, goal: str) -> Plan:
        """
        生成执行计划——分析目标，拆解为结构化步骤。

        实际项目中这里是 LLM 调用，根据 goal + 可用工具列表生成计划。
        这里用规则模拟：根据 goal 关键词匹配步骤模板。
        """
        goal_lower = goal.lower()

        # Match step templates by goal
        if any(w in goal_lower for w in ["发布", "release"]):
            steps = [
                PlanStep(
                    name="检查 README", tool="检查 README",
                    description="检查 README 完整性：验证必要章节是否存在",
                    depends_on=[],
                ),
                PlanStep(
                    name="运行测试", tool="运行测试",
                    description="运行全量测试套件，确保所有 case 通过",
                    depends_on=[],
                ),
                PlanStep(
                    name="整理 changelog", tool="整理 changelog",
                    description="基于 git log 生成本次发布的 changelog",
                    depends_on=["运行测试"],
                ),
                PlanStep(
                    name="生成 checklist", tool="生成 checklist",
                    description="生成发布 checklist，汇总所有待确认项",
                    depends_on=["检查 README", "运行测试", "整理 changelog"],
                ),
            ]
        elif any(w in goal_lower for w in ["修复", "bug", "fix"]):
            steps = [
                PlanStep(
                    name="运行测试", tool="运行测试",
                    description="先运行测试，确认 bug 可复现",
                    depends_on=[],
                ),
                PlanStep(
                    name="整理 changelog", tool="整理 changelog",
                    description="记录修复内容",
                    depends_on=["运行测试"],
                ),
            ]
        else:
            # Generic step template
            steps = [
                PlanStep(
                    name="检查 README", tool="检查 README",
                    description="检查文档完整性",
                    depends_on=[],
                ),
                PlanStep(
                    name="运行测试", tool="运行测试",
                    description="运行测试验证",
                    depends_on=[],
                ),
            ]

        return Plan(goal=goal, steps=steps)

    def generate_plan_text(self, plan: Plan) -> str:
        """生成计划的可读文本（用于展示给用户确认）"""
        lines = [f"执行计划: {plan.goal}", "=" * 50, ""]
        for i, step in enumerate(plan.steps, 1):
            deps = f" [依赖: {', '.join(step.depends_on)}]" if step.depends_on else ""
            lines.append(f"  步骤 {i}. {step.name}{deps}")
            lines.append(f"      {step.description}")
        lines.append("")
        lines.append(f"  共 {len(plan.steps)} 个步骤")
        lines.append(f"  最大重试次数: {DEFAULT_MAX_RETRIES}")
        return "\n".join(lines)

    def replan(
        self,
        goal: str,
        completed_steps: list[str],
        failed_step: str,
        error: str,
    ) -> list[PlanStep]:
        """
        重规划——当某步失败时，基于当前状态生成新的后续步骤。

        这是 Plan-Execute 与 Chain 的核心差异：
        Chain 遇错即停，Plan-Execute 可以生成替代路径。

        Args:
            goal: 原始目标
            completed_steps: 已完成的步骤名称列表
            failed_step: 失败的步骤名称
            error: 失败原因
        """
        self._replan_count += 1

        # Choose a replanning strategy based on the failure reason
        new_steps = []

        if "FileNotFound" in error or "不存在" in error:
            # File missing -> skip the current step and use an alternative step
            new_steps.append(PlanStep(
                name=f"替代方案（{failed_step}）",
                tool="生成 checklist",
                description=f"由于 {failed_step} 失败（{error}），使用替代方案",
                depends_on=[],
            ))

        elif "测试失败" in error or "AssertionError" in error:
            # Test failed -> insert an "analyze failure reason" step
            new_steps.append(PlanStep(
                name=f"分析 {failed_step} 失败原因",
                tool="运行测试",
                description=f"重新运行测试以确认失败原因: {error}",
                depends_on=[],
            ))
            # Continue with the remaining steps of the original plan
            remaining = [s for s in ["整理 changelog", "生成 checklist"]
                        if s not in completed_steps]
            for s in remaining:
                new_steps.append(PlanStep(
                    name=s, tool=s,
                    description=f"继续执行: {s}",
                    depends_on=[new_steps[-1].name] if new_steps else [],
                ))

        else:
            # Generic error -> skip the failed step and continue remaining steps
            remaining = [s for s in ["整理 changelog", "生成 checklist"]
                        if s not in completed_steps and s != failed_step]
            for s in remaining:
                new_steps.append(PlanStep(
                    name=s, tool=s,
                    description=f"跳过 {failed_step}，继续执行: {s}",
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
        Plan-Execute 主流程。

        Args:
            goal: 任务目标
            context: 初始上下文
            auto_confirm: True 则跳过用户确认（演示模式）
            inject_failures: 步骤名 → 是否失败（用于演示重规划）
            on_plan: 计划生成后回调
            on_step_start: 步骤开始回调
            on_step_end: 步骤结束回调
            on_replan: 重规划回调
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
                error="等待用户确认计划后再执行",
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
                            description=f"依赖步骤: {dep_name}",
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
                    error=f"未找到工具: {step.tool}",
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
                            f"达到最大重规划次数 {self.max_replan_count}，"
                            f"停止在步骤 '{step.name}'"
                        )
                        result.replan_count = self._replan_count
                        return result

                    new_steps = self.replan(
                        goal=plan.goal,
                        completed_steps=plan.completed_steps,
                        failed_step=step.name,
                        error=step_result.error or "未知错误",
                    )
                    step.status = "failed"
                    signature = tuple(s.name for s in new_steps)

                    if on_replan:
                        on_replan(step.name, new_steps)

                    if not new_steps:
                        # Replanning produced no alternative steps, so the task fails
                        result.status = "failed"
                        result.error = f"步骤 '{step.name}' 失败且无法重规划"
                        result.replan_count = self._replan_count
                        return result

                    if signature in seen_replans:
                        result.status = "failed"
                        result.error = "重规划生成了重复步骤，停止以避免循环"
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
