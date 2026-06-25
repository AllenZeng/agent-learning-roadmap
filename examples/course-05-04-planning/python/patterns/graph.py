"""
Graph 模式：将任务建模为节点和边的有向图

Graph 是 Plan-Execute 的泛化——计划不再是一维步骤列表，
而是一个可以有分支、回溯、并行路径的有向图。

每个节点是一个动作或判断，边代表条件跳转（成功/失败/需确认）。
Graph 适合复杂状态机、需要回放和恢复的任务。

适用场景：状态复杂、分支多、需要精确控制流转路径的任务。
"""

from dataclasses import dataclass, field
from typing import Callable, Optional
from scenario import StepResult, StepStatus, TOOL_REGISTRY


@dataclass
class Node:
    """图中的一个节点"""
    name: str
    action: Callable[[dict], StepResult]    # 节点要执行的动作
    on_success: Optional[str] = None         # 成功后跳转到哪个节点
    on_error: Optional[str] = None           # 失败后跳转到哪个节点
    max_retries: int = 1
    retry_count: int = 0
    description: str = ""


@dataclass
class GraphResult:
    """Graph 执行结果"""
    status: str                      # completed | failed
    path: list[str]                  # 实际执行路径
    results: dict[str, StepResult] = field(default_factory=dict)
    context: dict = field(default_factory=dict)
    error: Optional[str] = None


class WorkflowGraph:
    """
    工作流图——节点 + 条件边 + 状态机。

    核心逻辑：
    - 从 entry 节点开始
    - 执行当前节点的 action
    - 根据结果选择 on_success 或 on_error 边跳转
    - 循环直到到达 None（终止节点）或检测到环路
    - 支持每个节点的重试配置

    与 Plan-Execute 的关键区别：
    - Plan-Execute: 计划是列表，失败后重规划（生成新列表）
    - Graph: 所有路径在构建时已定义（包括失败路径），运行时只是状态跳转
    """

    def __init__(self):
        self.nodes: dict[str, Node] = {}
        self._entry: Optional[str] = None

    def set_entry(self, name: str):
        """设置入口节点"""
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
        """添加一个节点"""
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
        从入口节点开始执行图。

        Args:
            context: 初始上下文
            on_node_start: 节点开始时回调
            on_node_end: 节点结束时回调 (node_name, result, next_node)
        """
        if not self._entry or self._entry not in self.nodes:
            return GraphResult(
                status="failed",
                path=[],
                error=f"入口节点 '{self._entry}' 不存在",
            )

        ctx = context or {}
        result = GraphResult(status="completed", path=[], context=ctx)
        current = self._entry
        visited_count: dict[str, int] = {}  # 用于环路检测

        while current:
            node = self.nodes.get(current)
            if not node:
                result.error = f"节点 '{current}' 不存在"
                result.status = "failed"
                return result

            # 环路检测
            visited_count[current] = visited_count.get(current, 0) + 1
            if visited_count[current] > node.max_retries + 1:
                result.error = f"检测到环路: 节点 '{current}' 被访问了 {visited_count[current]} 次"
                result.status = "failed"
                return result

            result.path.append(current)

            if on_node_start:
                on_node_start(current)

            # 执行节点动作
            step_result = node.action(ctx)
            result.results[current] = step_result
            ctx[current] = step_result.output

            # 决定下一个节点
            if step_result.status == StepStatus.ERROR:
                node.retry_count += 1
                if node.retry_count < node.max_retries:
                    next_node = current  # 重试当前节点
                else:
                    next_node = node.on_error
            else:
                next_node = node.on_success
                node.retry_count = 0  # 成功后重置重试计数

            if on_node_end:
                on_node_end(current, step_result, next_node or "（终止）")

            # 防止无限循环（同一个节点连续执行不超过 max_retries+1 次）
            if next_node == current and node.retry_count >= node.max_retries:
                result.error = f"节点 '{current}' 重试 {node.retry_count} 次后仍然失败"
                result.status = "failed"
                return result

            current = next_node

        result.status = "completed"
        return result

    def describe(self) -> str:
        """返回图结构的文本描述（Mermaid 风格）"""
        lines = ["Graph 工作流:", "─" * 50]
        lines.append(f"  入口: {self._entry}")
        lines.append("")
        lines.append("  节点流程:")
        for name, node in self.nodes.items():
            entry_marker = " ◀ 入口" if name == self._entry else ""
            lines.append(f"    [{name}]{entry_marker}")
            lines.append(f"      {node.description}")
            if node.on_success:
                lines.append(f"      ├─ success → [{node.on_success}]")
            else:
                lines.append(f"      ├─ success → (终止)")
            if node.on_error:
                lines.append(f"      └─ error   → [{node.on_error}]")
            else:
                lines.append(f"      └─ error   → (终止)")
            if node.max_retries > 1:
                lines.append(f"      🔄 最大重试: {node.max_retries}")
        lines.append("─" * 50)
        lines.append("模式特征: 条件跳转 | 失败分支 | 环路检测 | 可回放")
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════
# 预构建的"发布准备"工作流图
# ═══════════════════════════════════════════════════════════════════════════

def build_release_workflow(inject_failures: Optional[dict[str, bool]] = None) -> WorkflowGraph:
    """
    构建一个"发布准备"的工作流图。

    图结构:
                    ┌──────────┐
                    │ 检查 README │
                    └─────┬──────┘
                          │ success         error
                          ▼                 ▼
                    ┌──────────┐    ┌──────────────┐
                    │  运行测试   │    │ 修复 README   │
                    └─────┬──────┘    └──────┬───────┘
                          │                  │ success
                    success│ error           ▼
                          ▼     ▼       (终止: 跳过发布)
                    ┌──────────┐
                    │整理 changelog│
                    └─────┬──────┘
                          │ success    error
                          ▼            ▼
                    ┌──────────┐  (终止: changelog失败)
                    │生成 checklist│
                    └─────┬──────┘
                          │ success    error
                          ▼            ▼
                      (完成!)    (终止: checklist失败)
    """
    inject = inject_failures or {}
    graph = WorkflowGraph()

    def make_action(step_name: str) -> Callable[[dict], StepResult]:
        """创建一个调用指定工具的 action 函数"""
        def action(ctx: dict) -> StepResult:
            tool = TOOL_REGISTRY.get(step_name)
            if not tool:
                return StepResult(
                    step_name=step_name,
                    status=StepStatus.ERROR,
                    error=f"未找到工具: {step_name}",
                )
            should_fail = inject.get(step_name, False)
            return tool(fail=should_fail)
        return action

    # 节点定义
    graph.add_node(
        "check_readme",
        action=make_action("检查 README"),
        on_success="run_tests",
        on_error="fix_readme",
        description="检查 README 完整性",
    )

    graph.add_node(
        "fix_readme",
        action=lambda ctx: StepResult(
            step_name="修复 README",
            status=StepStatus.SUCCESS,
            output="README 缺失内容已补充。建议重新运行检查。",
        ),
        on_success=None,  # 修复后终止（需要人工检查）
        on_error=None,
        description="尝试自动修复 README 缺失章节",
    )

    graph.add_node(
        "run_tests",
        action=make_action("运行测试"),
        on_success="changelog",
        on_error="retry_tests",
        max_retries=2,
        description="运行全量测试套件",
    )

    graph.add_node(
        "retry_tests",
        action=lambda ctx: StepResult(
            step_name="重试测试",
            status=StepStatus.SUCCESS,
            output="重试后测试通过（可能是环境波动）",
        ),
        on_success="changelog",
        on_error=None,  # 重试也失败 → 终止
        description="重试测试（可能是环境波动导致）",
    )

    graph.add_node(
        "changelog",
        action=make_action("整理 changelog"),
        on_success="checklist",
        on_error=None,  # changelog 失败 → 终止
        description="基于 git log 生成 changelog",
    )

    graph.add_node(
        "checklist",
        action=make_action("生成 checklist"),
        on_success=None,  # 完成！
        on_error=None,    # checklist 失败 → 终止
        description="生成发布 checklist",
    )

    graph.set_entry("check_readme")
    return graph
