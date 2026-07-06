"""
text：releasetext

text Planning text——textreleasetext。
text：text、text、failedtext。
"""

import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional


# ═══════════════════════════════════════════════════════════════════════════
# Step result
# ═══════════════════════════════════════════════════════════════════════════

class StepStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class StepResult:
    """textsteptextExecution result"""
    step_name: str
    status: StepStatus
    output: str = ""
    error: Optional[str] = None
    duration_ms: float = 0.0


# ═══════════════════════════════════════════════════════════════════════════
# Mock tool set
# ═══════════════════════════════════════════════════════════════════════════

# Mock README content (intentionally missing some required sections)
MOCK_README = """# MyAgent

A lightweight Agent framework.

## Installation

```bash
pip install myagent
```

## Quick Start

```python
from myagent import Agent
agent = Agent()
agent.run("Hello")
```

## API

See docs/api.md for details.
"""

# Mock git log
MOCK_GIT_LOG = """abc1234 (HEAD -> main) fix: resolve memory leak in session pool
def5678 feat: add streaming support for tool calls
ghi9012 docs: update API documentation
jkl3456 fix: handle empty response from LLM
mno7890 feat: add retry with exponential backoff
"""

# Mock test results
MOCK_TEST_OUTPUT = """============================= test session starts ==============================
collected 42 items

tests/test_agent.py ...................                                  [ 45%]
tests/test_tools.py ............                                         [ 73%]
tests/test_session.py .......                                            [ 90%]
tests/test_memory.py ....                                                [100%]

============================== 42 passed in 2.34s ==============================
"""

MOCK_TEST_FAILURE = """============================= test session starts ==============================
collected 42 items

tests/test_agent.py ...................                                  [ 45%]
tests/test_tools.py ............                                         [ 73%]
tests/test_session.py .......                                            [ 90%]
tests/test_memory.py .F..                                                [100%]

=================================== FAILURES ===================================
______________________ test_memory_cleanup_on_session_end ______________________

    def test_memory_cleanup_on_session_end():
        mem = MemoryStore()
        mem.start_session("test")
        mem.write({"key": "value"})
        mem.end_session()
>       assert len(mem._store) == 0
E       AssertionError: assert 1 == 0
E        +  where 1 = len({'session:test': {'key': 'value'}})

tests/test_memory.py:28: AssertionError
========================= 1 failed, 41 passed in 2.56s =========================
"""


def check_readme(fail: bool = False) -> StepResult:
    """Check README completeness - simulate file reading and content analysis"""
    time.sleep(0.3)  # Simulate I/O
    if fail:
        return StepResult(
            step_name="Check README",
            status=StepStatus.ERROR,
            error="FileNotFoundError: README.md does not exist at the project root",
        )

    # Check required sections
    required_sections = ["Installation", "Quick Start", "API", "Contributing"]
    missing = [s for s in required_sections if s not in MOCK_README]

    if missing:
        return StepResult(
            step_name="Check README",
            status=StepStatus.SUCCESS,
            output=f"README exists but is missing sections: {', '.join(missing)}. Recommendation: add the Contributing guide.",
        )
    return StepResult(
        step_name="Check README",
        status=StepStatus.SUCCESS,
        output="README is complete and contains all required sections.",
    )


def run_tests(fail: bool = False) -> StepResult:
    """Run tests - simulate test execution"""
    time.sleep(0.8)  # Simulate test run
    if fail:
        return StepResult(
            step_name="Run tests",
            status=StepStatus.ERROR,
            output=MOCK_TEST_FAILURE,
            error="1 tests failed: test_memory_cleanup_on_session_end",
        )
    return StepResult(
        step_name="Run tests",
        status=StepStatus.SUCCESS,
        output=MOCK_TEST_OUTPUT,
    )


def generate_changelog(fail: bool = False) -> StepResult:
    """Prepare changelog - simulate git log analysis and changelog generation"""
    time.sleep(0.4)
    if fail:
        return StepResult(
            step_name="Prepare changelog",
            status=StepStatus.ERROR,
            error="GitError: unable to get git log (not in a git repository)",
        )

    changelog = """## v1.2.0 (2026-06-25)

### Features
- tool callingtext (def5678)
- textretrytext (mno7890)

### Fixes
- fix session pool text (abc1234)
- Processing LLM text (jkl3456)

### Docs
- Updated API docs (ghi9012)
"""
    return StepResult(
        step_name="Prepare changelog",
        status=StepStatus.SUCCESS,
        output=f"Changelog text:\n{changelog}",
    )


def create_checklist(fail: bool = False) -> StepResult:
    """Generate release checklist - simulate checklist generation"""
    time.sleep(0.2)
    if fail:
        return StepResult(
            step_name="Generate checklist",
            status=StepStatus.ERROR,
            error="TemplateError: release template file is corrupted",
        )

    checklist = """## Release Checklist - v1.2.0

- [ ] README text
- [ ] All tests passed (42/42)
- [ ] Changelog textUpdated
- [ ] textUpdated (setup.py, package.json)
- [ ] API docstext
- [ ] releasetext
- [ ] textreleasetext
"""
    return StepResult(
        step_name="Generate checklist",
        status=StepStatus.SUCCESS,
        output=f"Release Checklist text:\n{checklist}",
    )


# ═══════════════════════════════════════════════════════════════════════════
# Tool registry: step_name -> callable
# ═══════════════════════════════════════════════════════════════════════════

TOOL_REGISTRY: dict[str, Callable[..., StepResult]] = {
    "Check README": check_readme,
    "Run tests": run_tests,
    "Prepare changelog": generate_changelog,
    "Generate checklist": create_checklist,
}

# Step dependencies: which steps must run before which other steps
STEP_DEPENDENCIES = {
    "Check README": [],           # No dependencies
    "Run tests": [],               # No dependencies (can run in parallel with README check)
    "Prepare changelog": ["Run tests"],  # Must run after tests pass
    "Generate checklist": ["Check README", "Run tests", "Prepare changelog"],  # Must run after all steps
}

# Default release preparation steps (used by Chain mode)
DEFAULT_RELEASE_STEPS = [
    "Check README",
    "Run tests",
    "Prepare changelog",
    "Generate checklist",
]

# Default retry count per step
DEFAULT_MAX_RETRIES = 2


def get_tool(name: str) -> Optional[Callable[..., StepResult]]:
    """text"""
    return TOOL_REGISTRY.get(name)


def describe_tools() -> str:
    """text"""
    lines = []
    for name, fn in TOOL_REGISTRY.items():
        doc = (fn.__doc__ or "").strip().split("\n")[0]
        deps = STEP_DEPENDENCIES.get(name, [])
        dep_str = f" (dependencies: {', '.join(deps)})" if deps else ""
        lines.append(f"  - {name}: {doc}{dep_str}")
    return "\n".join(lines)


def describe_dependencies() -> str:
    """Returndependenciestext"""
    lines = []
    for step, deps in STEP_DEPENDENCIES.items():
        if deps:
            lines.append(f"  {step} ← textcomplete: {', '.join(deps)}")
        else:
            lines.append(f"  {step} ← No dependencies，text")
    return "\n".join(lines)
