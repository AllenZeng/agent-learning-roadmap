"""
Chain 模式：固定顺序执行

最基础的 Planning 模式。步骤按预定顺序依次执行，每步的输出成为下一步的输入。
无分支、无重规划、无条件跳转——确定性最强，调试最简单。

适用场景：步骤稳定、异常少、不需要动态决策的任务。
"""

from dataclasses import dataclass, field
from typing import Callable, Optional
from scenario import (
    StepResult, StepStatus, TOOL_REGISTRY, DEFAULT_RELEASE_STEPS,
)


@dataclass
class ChainResult:
    """Chain 执行结果"""
    status: str = "completed"        # "completed" | "failed" | "partial"
    results: list[StepResult] = field(default_factory=list)
    context: dict = field(default_factory=dict)
    failed_at: Optional[int] = None
    error: Optional[str] = None


class ChainExecutor:
    """
    Chain 执行器——按固定顺序依次执行步骤。

    核心逻辑：
    - 顺序执行步骤列表
    - 每步的输出写入 context
    - 遇到错误时：如果该步骤标记了 allow_skip，则跳过继续；否则停止
    - 无分支、无重试、无动态调整
    """

    def __init__(self, steps: Optional[list[str]] = None):
        self.steps = steps or DEFAULT_RELEASE_STEPS
        self._context: dict = {}

    def execute(
        self,
        context: Optional[dict] = None,
        on_step_start: Optional[Callable[[str], None]] = None,
        on_step_end: Optional[Callable[[StepResult], None]] = None,
    ) -> ChainResult:
        """
        按固定顺序执行所有步骤。

        Args:
            context: 初始上下文
            on_step_start: 步骤开始时回调（用于 UI 更新）
            on_step_end: 步骤结束时回调
        """
        self._context = context or {}
        result = ChainResult(context=self._context)

        for i, step_name in enumerate(self.steps):
            # Notify that the step has started
            if on_step_start:
                on_step_start(step_name)

            # Find the tool
            tool = TOOL_REGISTRY.get(step_name)
            if not tool:
                step_result = StepResult(
                    step_name=step_name,
                    status=StepStatus.ERROR,
                    error=f"未找到工具: {step_name}",
                )
                result.results.append(step_result)
                result.status = "failed"
                result.failed_at = i
                result.error = f"未找到工具: {step_name}"
                if on_step_end:
                    on_step_end(step_result)
                return result

            # Execute the step
            step_result = tool()
            result.results.append(step_result)
            self._context[step_name] = step_result.output

            if on_step_end:
                on_step_end(step_result)

            # Error handling: Chain mode stops on errors by default
            if step_result.status == StepStatus.ERROR:
                result.status = "failed"
                result.failed_at = i
                result.error = step_result.error
                return result

        result.status = "completed"
        return result

    def describe(self) -> str:
        """返回执行计划的文本描述"""
        lines = ["Chain 执行计划（固定顺序）:", "─" * 40]
        for i, step in enumerate(self.steps, 1):
            tool = TOOL_REGISTRY.get(step)
            desc = (tool.__doc__ or "").strip().split("\n")[0] if tool else "未知步骤"
            lines.append(f"  {i}. {step} → {desc}")
        lines.append("─" * 40)
        lines.append("模式特征: 无分支 | 无重试 | 遇错即停 | 顺序执行")
        return "\n".join(lines)
