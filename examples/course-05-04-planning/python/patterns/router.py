"""
Router 模式：根据输入特征选择执行路径

Router 本质是"分类器 + 多条 Chain"。根据输入类型选择不同的执行路径，
每条路径内部按固定顺序执行。

适用场景：多类型任务入口（如问答、代码审查、任务执行走不同流程）。
"""

from dataclasses import dataclass, field
from typing import Callable, Optional
from scenario import StepResult, StepStatus
from .chain import ChainExecutor


# ═══════════════════════════════════════════════════════════════════════════
# 预定义的执行路径
# ═══════════════════════════════════════════════════════════════════════════

# 发布准备路径
RELEASE_ROUTE = ["检查 README", "运行测试", "整理 changelog", "生成 checklist"]

# Bug 修复路径
BUGFIX_ROUTE = ["运行测试", "整理 changelog"]

# 文档更新路径
DOCS_ROUTE = ["检查 README"]

# 功能开发路径
FEATURE_ROUTE = ["运行测试", "整理 changelog", "生成 checklist"]

DEFAULT_ROUTES = {
    "release": RELEASE_ROUTE,
    "bugfix": BUGFIX_ROUTE,
    "docs": DOCS_ROUTE,
    "feature": FEATURE_ROUTE,
}


@dataclass
class RouterResult:
    """Router 执行结果"""
    status: str
    category: str
    results: list[StepResult] = field(default_factory=list)
    context: dict = field(default_factory=dict)
    error: Optional[str] = None


class RouterExecutor:
    """
    Router 执行器——分类 + 路径选择 + 执行。

    核心逻辑：
    1. 根据用户输入分类（关键词匹配 / LLM 分类）
    2. 选择对应的执行路径
    3. 用 Chain 模式执行该路径
    4. 分类失败时走 default 兜底路径
    """

    def __init__(self, routes: Optional[dict[str, list[str]]] = None):
        self.routes = routes or DEFAULT_ROUTES

    def classify(self, query: str) -> str:
        """
        分类器——根据输入关键词判断任务类型。

        实际项目中这里可能是 LLM 调用或专用分类模型。
        这里用关键词匹配做演示。
        """
        query_lower = query.lower()

        # 关键词 → 分类
        keywords = {
            "release": ["发布", "release", "上线", "发版"],
            "bugfix": ["bug", "修复", "fix", "缺陷", "补丁"],
            "docs": ["文档", "doc", "readme", "说明"],
            "feature": ["功能", "feature", "新功能", "新增"],
        }

        for category, words in keywords.items():
            if any(w in query_lower for w in words):
                return category

        # 兜底：默认走 release（发布准备是最完整的流程，不合适的步骤会自行跳过）
        return "release"

    def execute(
        self,
        query: str,
        context: Optional[dict] = None,
        on_step_start: Optional[Callable[[str], None]] = None,
        on_step_end: Optional[Callable[[StepResult], None]] = None,
    ) -> RouterResult:
        """
        分类 → 路由 → 执行。

        Args:
            query: 用户请求文本
            context: 初始上下文
        """
        # 1. 分类
        category = self.classify(query)

        # 2. 选择路径
        steps = self.routes.get(category, self.routes.get("release", []))

        # 3. 执行
        chain = ChainExecutor(steps)
        chain_result = chain.execute(
            context=context,
            on_step_start=on_step_start,
            on_step_end=on_step_end,
        )

        return RouterResult(
            status=chain_result.status,
            category=category,
            results=chain_result.results,
            context=chain_result.context,
            error=chain_result.error,
        )

    def describe(self, query: str = "") -> str:
        """返回路由信息的文本描述"""
        category = self.classify(query) if query else "（无输入）"
        steps = self.routes.get(category, [])
        lines = [
            f"Router 执行计划（分类: {category}）:",
            "─" * 40,
        ]
        if query:
            lines.append(f"  输入: {query}")
            lines.append(f"  分类结果: {category}")
        lines.append(f"  执行路径: {' → '.join(steps)}")
        lines.append("─" * 40)
        lines.append("模式特征: 分类路由 | 默认兜底 | 路径内顺序执行")
        return "\n".join(lines)
