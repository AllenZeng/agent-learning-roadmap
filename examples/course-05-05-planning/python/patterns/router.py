"""
Router pattern：textInputtextExecution path

Router is essentially a classifier plus multiple Chains.textInputtextExecution path，
textpathtextfixed-order execution。

Use case：multi-type task entry（such as Q&A、code review、task execution using different flows)。
"""

from dataclasses import dataclass, field
from typing import Callable, Optional
from scenario import StepResult, StepStatus
from .chain import ChainExecutor


# ═══════════════════════════════════════════════════════════════════════════
# Predefined execution paths
# ═══════════════════════════════════════════════════════════════════════════

# Release preparation path
RELEASE_ROUTE = ["Check README", "Run tests", "Prepare changelog", "Generate checklist"]

# Bug-fix path
BUGFIX_ROUTE = ["Run tests", "Prepare changelog"]

# Documentation update path
DOCS_ROUTE = ["Check README"]

# Feature development path
FEATURE_ROUTE = ["Run tests", "Prepare changelog", "Generate checklist"]

DEFAULT_ROUTES = {
    "release": RELEASE_ROUTE,
    "bugfix": BUGFIX_ROUTE,
    "docs": DOCS_ROUTE,
    "feature": FEATURE_ROUTE,
}


@dataclass
class RouterResult:
    """Router Execution result"""
    status: str
    category: str
    results: list[StepResult] = field(default_factory=list)
    context: dict = field(default_factory=dict)
    error: Optional[str] = None


class RouterExecutor:
    """
    Router executor——classification + pathchoose + execute。

    Core logic：
    1. textuserInputclassification（keywordmatches / LLM classification)
    2. textExecution path
    3. use Chain modetextpath
    4. classificationfailedtext default textpath
    """

    def __init__(self, routes: Optional[dict[str, list[str]]] = None):
        self.routes = routes or DEFAULT_ROUTES

    def classify(self, query: str) -> str:
        """
        classificationtext——textInputkeywordtext。

        textmediumtext LLM textclassificationtext。
        textkeywordtext。
        """
        query_lower = query.lower()

        # Keyword -> category
        keywords = {
            "release": ["release", "release", "deploy", "release"],
            "bugfix": ["bug", "fix", "fix", "defect", "patch"],
            "docs": ["docs", "doc", "readme", "instructions"],
            "feature": ["feature", "feature", "new feature", "add"],
        }

        for category, words in keywords.items():
            if any(w in query_lower for w in words):
                return category

        # Fallback: default to release (release preparation is the most complete flow; unsuitable steps skip themselves)
        return "release"

    def execute(
        self,
        query: str,
        context: Optional[dict] = None,
        on_step_start: Optional[Callable[[str], None]] = None,
        on_step_end: Optional[Callable[[StepResult], None]] = None,
    ) -> RouterResult:
        """
        classification → route → execute。

        Args:
            query: usertext
            context: initial context
        """
        # 1. Classify
        category = self.classify(query)

        # 2. Choose path
        steps = self.routes.get(category, self.routes.get("release", []))

        # 3. Execute
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
        """return a text description of routing info"""
        category = self.classify(query) if query else "（noneInput)"
        steps = self.routes.get(category, [])
        lines = [
            f"Router Execution plan（classification: {category}):",
            "─" * 40,
        ]
        if query:
            lines.append(f"  Input: {query}")
            lines.append(f"  classificationResult: {category}")
        lines.append(f"  Execution path: {' → '.join(steps)}")
        lines.append("─" * 40)
        lines.append("Pattern features: classificationroute | defaulttext | pathtext")
        return "\n".join(lines)
