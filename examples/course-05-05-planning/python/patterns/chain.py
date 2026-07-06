"""
Chain pattern: fixed-order execution

The most basic Planning pattern. Steps run in a predefined order, and each output becomes the input to the next step.
No branches, no replanning, no conditional transitions: strongest determinism and easiest debugging.

Use when steps are stable, exceptions are rare, and dynamic decisions are unnecessary.
"""

from dataclasses import dataclass, field
from typing import Callable, Optional
from scenario import (
    StepResult, StepStatus, TOOL_REGISTRY, DEFAULT_RELEASE_STEPS,
)


@dataclass
class ChainResult:
    """Chain Execution result"""
    status: str = "completed"        # "completed" | "failed" | "partial"
    results: list[StepResult] = field(default_factory=list)
    context: dict = field(default_factory=dict)
    failed_at: Optional[int] = None
    error: Optional[str] = None


class ChainExecutor:
    """
    Chain executor: executes steps in fixed order.

    Core logic：
    - execute sequentiallysteplist
    - each step writes output to context
    - on error: if the step is marked allow_skip, skip and continue; otherwise stop
    - no branches, no retries, no dynamic adjustment
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
        Execute all steps in fixed order.

        Args:
            context: initial context
            on_step_start: callback when a step starts (for UI updates)
            on_step_end: callback when a step ends
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
                    error=f"Tool not found: {step_name}",
                )
                result.results.append(step_result)
                result.status = "failed"
                result.failed_at = i
                result.error = f"Tool not found: {step_name}"
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
        """Return a text description of the execution plan"""
        lines = ["Chain Execution plan（fixed order):", "─" * 40]
        for i, step in enumerate(self.steps, 1):
            tool = TOOL_REGISTRY.get(step)
            desc = (tool.__doc__ or "").strip().split("\n")[0] if tool else "unknown step"
            lines.append(f"  {i}. {step} → {desc}")
        lines.append("─" * 40)
        lines.append("Pattern features: no branches | no retry | stop on error | sequential execution")
        return "\n".join(lines)
