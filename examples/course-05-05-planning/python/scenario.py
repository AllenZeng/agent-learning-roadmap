"""
场景定义：发布准备任务

为 Planning 四种模式提供统一的测试场景——一个软件项目的发布准备工作。
包含：模拟工具、任务定义、失败注入机制。
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
    """单个步骤的执行结果"""
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
    """检查 README 完整性——模拟文件读取和内容分析"""
    time.sleep(0.3)  # Simulate I/O
    if fail:
        return StepResult(
            step_name="检查 README",
            status=StepStatus.ERROR,
            error="FileNotFoundError: README.md 不存在于项目根目录",
        )

    # Check required sections
    required_sections = ["Installation", "Quick Start", "API", "Contributing"]
    missing = [s for s in required_sections if s not in MOCK_README]

    if missing:
        return StepResult(
            step_name="检查 README",
            status=StepStatus.SUCCESS,
            output=f"README 存在但缺少章节: {', '.join(missing)}。建议补充 Contributing 指南。",
        )
    return StepResult(
        step_name="检查 README",
        status=StepStatus.SUCCESS,
        output="README 完整，包含所有必要章节。",
    )


def run_tests(fail: bool = False) -> StepResult:
    """运行测试——模拟测试执行"""
    time.sleep(0.8)  # Simulate test run
    if fail:
        return StepResult(
            step_name="运行测试",
            status=StepStatus.ERROR,
            output=MOCK_TEST_FAILURE,
            error="1 个测试失败: test_memory_cleanup_on_session_end",
        )
    return StepResult(
        step_name="运行测试",
        status=StepStatus.SUCCESS,
        output=MOCK_TEST_OUTPUT,
    )


def generate_changelog(fail: bool = False) -> StepResult:
    """整理 changelog——模拟 git log 分析和 changelog 生成"""
    time.sleep(0.4)
    if fail:
        return StepResult(
            step_name="整理 changelog",
            status=StepStatus.ERROR,
            error="GitError: 无法获取 git log（不在 git 仓库中）",
        )

    changelog = """## v1.2.0 (2026-06-25)

### Features
- 工具调用支持流式输出 (def5678)
- 指数退避重试机制 (mno7890)

### Fixes
- 修复 session pool 内存泄漏 (abc1234)
- 处理 LLM 空响应 (jkl3456)

### Docs
- 更新 API 文档 (ghi9012)
"""
    return StepResult(
        step_name="整理 changelog",
        status=StepStatus.SUCCESS,
        output=f"Changelog 已生成:\n{changelog}",
    )


def create_checklist(fail: bool = False) -> StepResult:
    """生成发布 checklist——模拟清单生成"""
    time.sleep(0.2)
    if fail:
        return StepResult(
            step_name="生成 checklist",
            status=StepStatus.ERROR,
            error="TemplateError: release 模板文件损坏",
        )

    checklist = """## Release Checklist - v1.2.0

- [ ] README 完整性检查通过
- [ ] 所有测试通过 (42/42)
- [ ] Changelog 已更新
- [ ] 版本号已更新 (setup.py, package.json)
- [ ] API 文档已同步
- [ ] 发布分支已创建
- [ ] 预发布环境验证通过
"""
    return StepResult(
        step_name="生成 checklist",
        status=StepStatus.SUCCESS,
        output=f"Release Checklist 已生成:\n{checklist}",
    )


# ═══════════════════════════════════════════════════════════════════════════
# Tool registry: step_name -> callable
# ═══════════════════════════════════════════════════════════════════════════

TOOL_REGISTRY: dict[str, Callable[..., StepResult]] = {
    "检查 README": check_readme,
    "运行测试": run_tests,
    "整理 changelog": generate_changelog,
    "生成 checklist": create_checklist,
}

# Step dependencies: which steps must run before which other steps
STEP_DEPENDENCIES = {
    "检查 README": [],           # No dependencies
    "运行测试": [],               # No dependencies (can run in parallel with README check)
    "整理 changelog": ["运行测试"],  # Must run after tests pass
    "生成 checklist": ["检查 README", "运行测试", "整理 changelog"],  # Must run after all steps
}

# Default release preparation steps (used by Chain mode)
DEFAULT_RELEASE_STEPS = [
    "检查 README",
    "运行测试",
    "整理 changelog",
    "生成 checklist",
]

# Default retry count per step
DEFAULT_MAX_RETRIES = 2


def get_tool(name: str) -> Optional[Callable[..., StepResult]]:
    """根据名称获取工具函数"""
    return TOOL_REGISTRY.get(name)


def describe_tools() -> str:
    """返回工具列表的描述文本"""
    lines = []
    for name, fn in TOOL_REGISTRY.items():
        doc = (fn.__doc__ or "").strip().split("\n")[0]
        deps = STEP_DEPENDENCIES.get(name, [])
        dep_str = f" (依赖: {', '.join(deps)})" if deps else ""
        lines.append(f"  - {name}: {doc}{dep_str}")
    return "\n".join(lines)


def describe_dependencies() -> str:
    """返回依赖关系的文本描述"""
    lines = []
    for step, deps in STEP_DEPENDENCIES.items():
        if deps:
            lines.append(f"  {step} ← 需要先完成: {', '.join(deps)}")
        else:
            lines.append(f"  {step} ← 无依赖，可独立执行")
    return "\n".join(lines)
