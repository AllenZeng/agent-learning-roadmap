"""
Graph pattern：model the task asnodeand edges in a directed graph

Graph text Plan-Execute text——textsteplist，
but a directed graph with branches、backtracking、parallelpathpaths。

eachnodeis an action or decision，edges represent conditional transitions（success/failed/needs confirmation)。
Graph textStatustext、text。

Use case：Statuscomplex、text、textpathtext。
"""

from dataclasses import dataclass, field
from typing import Callable, Optional
from scenario import StepResult, StepStatus, TOOL_REGISTRY


@dataclass
class Node:
    """graphmediumtextnode"""
    name: str
    action: Callable[[dict], StepResult]    # Action executed by the node
    on_success: Optional[str] = None         # Node to jump to after success
    on_error: Optional[str] = None           # Node to jump to after failure
    max_retries: int = 1
    retry_count: int = 0
    description: str = ""


@dataclass
class GraphResult:
    """Graph Execution result"""
    status: str                      # completed | failed
    path: list[str]                  # Actual execution path
    results: dict[str, StepResult] = field(default_factory=dict)
    context: dict = field(default_factory=dict)
    error: Optional[str] = None


class WorkflowGraph:
    """
    Workflowgraph——node + conditional edge + state machine。

    Core logic：
    - text entry nodestarted
    - textnodetext action
    - textResultchoose on_success text on_error text
    - text None（stopnode)textloop detected
    - textnodetextretryconfigure

    compared with Plan-Execute key difference：
    - Plan-Execute: text，failedtextreplan（text)
    - Graph: textpathtext（textfailedpath)，textStatustext
    """

    def __init__(self):
        self.nodes: dict[str, Node] = {}
        self._entry: Optional[str] = None

    def set_entry(self, name: str):
        """set entrynode"""
        self._entry = name

    def add_node(
        self,
        name: str,
        action: Callable[[dict], StepResult],
        on_success: Optional[str] = None,
        on_error: Optional[str] = None,
        max_retries: int = 1,
        description: str = "",
    ):
        """add anode"""
        self.nodes[name] = Node(
            name=name,
            action=action,
            on_success=on_success,
            on_error=on_error,
            max_retries=max_retries,
            description=description,
        )

    def run(
        self,
        context: Optional[dict] = None,
        on_node_start: Optional[Callable[[str], None]] = None,
        on_node_end: Optional[Callable[[str, StepResult, str], None]] = None,
    ) -> GraphResult:
        """
        from the entrynodestartedtext。

        Args:
            context: initial context
            on_node_start: nodestartedtext
            on_node_end: nodeend callback (node_name, result, next_node)
        """
        if not self._entry or self._entry not in self.nodes:
            return GraphResult(
                status="failed",
                path=[],
                error=f"entrynode '{self._entry}' does not exist",
            )

        ctx = context or {}
        result = GraphResult(status="completed", path=[], context=ctx)
        current = self._entry
        visited_count: dict[str, int] = {}  # Used for loop detection

        while current:
            node = self.nodes.get(current)
            if not node:
                result.error = f"node '{current}' does not exist"
                result.status = "failed"
                return result

            # Loop detection
            visited_count[current] = visited_count.get(current, 0) + 1
            if visited_count[current] > node.max_retries + 1:
                result.error = f"loop detected: node '{current}' was visited {visited_count[current]} times"
                result.status = "failed"
                return result

            result.path.append(current)

            if on_node_start:
                on_node_start(current)

            # Execute node action
            step_result = node.action(ctx)
            result.results[current] = step_result
            ctx[current] = step_result.output

            # Decide the next node
            if step_result.status == StepStatus.ERROR:
                node.retry_count += 1
                if node.retry_count < node.max_retries:
                    next_node = current  # Retry the current node
                else:
                    next_node = node.on_error
            else:
                next_node = node.on_success
                node.retry_count = 0  # Reset retry count after success

            if on_node_end:
                on_node_end(current, step_result, next_node or "(stop)")

            # Prevent infinite loops (the same node cannot run more than max_retries + 1 consecutive times)
            if next_node == current and node.retry_count >= node.max_retries:
                result.error = f"node '{current}' retry {node.retry_count} timesafter stillfailed"
                result.status = "failed"
                return result

            current = next_node

        result.status = "completed"
        return result

    def describe(self) -> str:
        """return a text description of the graph structure（Mermaid text)"""
        lines = ["Graph Workflow:", "─" * 50]
        lines.append(f"  entry: {self._entry}")
        lines.append("")
        lines.append("  nodeflow:")
        for name, node in self.nodes.items():
            entry_marker = " ◀ entry" if name == self._entry else ""
            lines.append(f"    [{name}]{entry_marker}")
            lines.append(f"      {node.description}")
            if node.on_success:
                lines.append(f"      ├─ success → [{node.on_success}]")
            else:
                lines.append(f"      ├─ success → (stop)")
            if node.on_error:
                lines.append(f"      └─ error   → [{node.on_error}]")
            else:
                lines.append(f"      └─ error   → (stop)")
            if node.max_retries > 1:
                lines.append(f"      🔄 maximumretry: {node.max_retries}")
        lines.append("─" * 50)
        lines.append("Pattern features: conditional transitions | failedbranches | loop detection | replayable")
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════
# Prebuilt "release preparation" workflow graph
# ═══════════════════════════════════════════════════════════════════════════

def build_release_workflow(inject_failures: Optional[dict[str, bool]] = None) -> WorkflowGraph:
    """
    build a"releasetext"textWorkflowgraph。

    graph structure:
                    ┌──────────┐
                    │ Check README │
                    └─────┬──────┘
                          │ success         error
                          ▼                 ▼
                    ┌──────────┐    ┌──────────────┐
                    │  Run tests   │    │ fix README   │
                    └─────┬──────┘    └──────┬───────┘
                          │                  │ success
                    success│ error           ▼
                          ▼     ▼       (stop: skiprelease)
                    ┌──────────┐
                    │Prepare changelog│
                    └─────┬──────┘
                          │ success    error
                          ▼            ▼
                    ┌──────────┐  (stop: changelogfailed)
                    │Generate checklist│
                    └─────┬──────┘
                          │ success    error
                          ▼            ▼
                      (complete!)    (stop: checklistfailed)
    """
    inject = inject_failures or {}
    graph = WorkflowGraph()

    def make_action(step_name: str) -> Callable[[dict], StepResult]:
        """create an action function that calls the specified tool action function"""
        def action(ctx: dict) -> StepResult:
            tool = TOOL_REGISTRY.get(step_name)
            if not tool:
                return StepResult(
                    step_name=step_name,
                    status=StepStatus.ERROR,
                    error=f"Tool not found: {step_name}",
                )
            should_fail = inject.get(step_name, False)
            return tool(fail=should_fail)
        return action

    # Node definitions
    graph.add_node(
        "check_readme",
        action=make_action("Check README"),
        on_success="run_tests",
        on_error="fix_readme",
        description="Check README completeness",
    )

    graph.add_node(
        "fix_readme",
        action=lambda ctx: StepResult(
            step_name="fix README",
            status=StepStatus.SUCCESS,
            output="Missing README content has been added.Recommendationsrerun the check。",
        ),
        on_success=None,  # Stop after fixing (requires human review)
        on_error=None,
        description="Try to automatically fix missing README sections",
    )

    graph.add_node(
        "run_tests",
        action=make_action("Run tests"),
        on_success="changelog",
        on_error="retry_tests",
        max_retries=2,
        description="Run full test suite",
    )

    graph.add_node(
        "retry_tests",
        action=lambda ctx: StepResult(
            step_name="retry tests",
            status=StepStatus.SUCCESS,
            output="Tests passed after retry (possibly an environment fluctuation)",
        ),
        on_success="changelog",
        on_error=None,  # Retry also failed -> stop
        description="retry tests（possibly caused by an environment fluctuation)",
    )

    graph.add_node(
        "changelog",
        action=make_action("Prepare changelog"),
        on_success="checklist",
        on_error=None,  # changelog failed -> stop
        description="Generate changelog from git log",
    )

    graph.add_node(
        "checklist",
        action=make_action("Generate checklist"),
        on_success=None,  # Done!
        on_error=None,    # checklist failed -> stop
        description="Generate release checklist",
    )

    graph.set_entry("check_readme")
    return graph
