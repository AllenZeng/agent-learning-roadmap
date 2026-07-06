#!/usr/bin/env python3
"""
课程五 05-06 Reflection 示例

一个交互式 REPL，演示 Reflection 的反馈决策闭环：
  - V0：无反思 — Agent 看到 TypeError 却继续执行
  - V1：格式修复 — Schema 校验失败触发重生成
  - V2：工具错误处理 — 参数错误触发分类与处理决策
  - V3：测试驱动处理 — 外部测试框架驱动下一步决策

用法:
    python reflection_demo.py

在 REPL 中你可以:
  - 观察 V0 中 Agent 忽略错误的完整过程
  - 对比 V1-V3 每阶段新增的反馈处理能力
  - 触发停止条件，观察 Reflection 循环如何终止
"""

import sys
import os
from dataclasses import dataclass, field
from typing import Callable, Optional
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════
# 基础类型
# ═══════════════════════════════════════════════════════════════════════════

class ValidationStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"


@dataclass
class ActionResult:
    """Agent 执行动作的结果"""
    output: str
    cost: float = 0.0
    attempt: int = 0


@dataclass
class ValidationResult:
    """外部验证器的结果（不是模型自评！）"""
    passed: bool
    message: str = ""
    evidence: str = ""
    error_type: str = ""  # schema_error | tool_param_error | test_failure | context_missing | env_error


@dataclass
class ReflectionResult:
    """一次完整的 Reflection 循环结果"""
    status: str  # success | stopped
    output: str = ""
    attempts: int = 0
    cost: float = 0.0
    reason: str = ""
    trace: list = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════
# 模拟场景数据
# ═══════════════════════════════════════════════════════════════════════════

# 模拟的笔记内容（用于引用校验）
MOCK_NOTES = {
    "agent-memory-mechanism.md": """
## 写入决策与遗忘机制

Memory 模块的 session 数据由 MemoryStore 管理。
expired session 数据由 decay() 在每次 start_session 时清理，底层调用 _purge_old_records()。

写入逻辑在 src/memory/write.py 中实现了两层守卫：
1. 容量守卫：当 store 大小超过 max_size 时拒绝写入
2. TTL 守卫：当 key 的 ttl 过期时先清理再写入

注意：Memory 模块不提供 clear_expired() 方法。过期清理是自动的、被动的。
""",
    "session-manager.md": """
## Session Manager API

session_manager.py 的 cleanup 方法用于手动清理过期 session。
正确用法是调用 MemoryStore.decay() 触发级联清理，而不是直接操作 _store 字典。

错误示例（不要这样做）：
    def cleanup(self):
        for sid in list(self._sessions.keys()):
            if self._sessions[sid].expired:
                del self._sessions[sid]  # 绕过了 decay() 的清理逻辑！

正确做法：
    def cleanup(self):
        self.memory_store.decay()  # 触发完整的过期清理链
"""
}

# 模拟的测试套件结果
MOCK_TEST_PASS = """============================= test session starts ==============================
collected 10 items

tests/test_memory.py ..........                                          [100%]

============================== 10 passed in 1.23s ==============================
"""

MOCK_TEST_FAIL = """============================= test session starts ==============================
collected 10 items

tests/test_memory.py ........F.                                          [100%]

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
========================= 1 failed, 9 passed in 1.45s =========================
"""

# 用于 V3 的"正确代码"和"错误代码"
CORRECT_CLEANUP_CODE = '''
def cleanup(self):
    """清理过期 session"""
    self.memory_store.decay()
'''

BUGGY_CLEANUP_CODE = '''
def cleanup(self):
    """清理过期 session"""
    for sid in list(self._sessions.keys()):
        if self._sessions[sid].expired:
            del self._sessions[sid]
'''


# ═══════════════════════════════════════════════════════════════════════════
# 外部验证器（注意：这些都是外部系统，不是 LLM 自评！）
# ═══════════════════════════════════════════════════════════════════════════

def validate_json_schema(output: str) -> ValidationResult:
    """V1: JSON Schema 校验 — 确定性规则检查"""
    required_fields = ["tool_name", "args", "reason"]
    missing = [f for f in required_fields if f not in output]
    if missing:
        return ValidationResult(
            passed=False,
            message=f"Schema 校验失败：缺少必填字段 {', '.join(missing)}",
            evidence=f"输出中只包含字段: {[k for k in ['tool_name','args','reason'] if k in output]}",
            error_type="schema_error"
        )
    return ValidationResult(passed=True, message="Schema 校验通过")


def validate_tool_params(params: dict) -> ValidationResult:
    """V2: 工具参数校验 — 检查参数是否在合法范围内"""
    if "limit" in params:
        limit = params["limit"]
        if not isinstance(limit, int) or limit < 1 or limit > 100:
            return ValidationResult(
                passed=False,
                message=f"参数错误：limit 必须在 1-100 之间，当前值 {limit}",
                evidence=f"工具返回: Error: limit must be 1-100 (got {limit})",
                error_type="tool_param_error"
            )
    if "query" in params:
        query = params["query"]
        if not query or not isinstance(query, str) or query.strip() == "":
            return ValidationResult(
                passed=False,
                message="参数错误：query 不能为空",
                evidence="工具返回: Error: query parameter is required and must be non-empty",
                error_type="tool_param_error"
            )
    return ValidationResult(passed=True, message="参数校验通过")


def validate_citation(output: str, notes: dict) -> ValidationResult:
    """V4: 引用校验 — 逐条检查输出中的引用能否在知识库中找到原文"""
    # 从输出中提取被引用的 API/实体名
    import re
    # 查找类似 `memory.clear_expired()` 的引用
    api_pattern = re.findall(r'`(\w+\.\w+)\(\)`', output)
    # 也查找 "API 'xxx'" 形式的引用
    named_pattern = re.findall(r"API '(\w+\.\w+)'", output)

    all_refs = set(api_pattern + named_pattern)

    for ref in all_refs:
        found = False
        for note_name, note_content in notes.items():
            if ref in note_content:
                found = True
                break
        if not found:
            return ValidationResult(
                passed=False,
                message=f"引用校验失败：'{ref}' 在笔记中未找到",
                evidence=f"搜索 './notes/' 下所有文件，'{ref}' 0 匹配",
                error_type="context_missing"
            )

    return ValidationResult(passed=True, message="引用校验通过")


def validate_tests(code: str) -> ValidationResult:
    """V3: 测试驱动验证 — 运行外部测试框架"""
    # 模拟：检查代码是否使用了正确的 API
    if "memory_store.decay()" in code:
        return ValidationResult(passed=True, message="所有测试通过 (10/10)")
    elif "del self._sessions" in code:
        return ValidationResult(
            passed=False,
            message="测试失败: test_memory_cleanup_on_session_end — AssertionError: assert 1 == 0",
            evidence=MOCK_TEST_FAIL,
            error_type="test_failure"
        )
    return ValidationResult(
        passed=False,
        message="测试失败: 代码无法解析",
        evidence="SyntaxError: invalid syntax at line 3",
        error_type="test_failure"
    )


def validate_env_check(action_name: str) -> ValidationResult:
    """环境检查 — 模拟外部环境验证（如 git repo 是否存在）"""
    if action_name == "git_log" and "--not-a-repo" in os.getcwd():
        return ValidationResult(
            passed=False,
            message="工具执行失败: git log → fatal: not a git repository",
            evidence="fatal: not a git repository (or any of the parent directories): .git",
            error_type="env_error"
        )
    return ValidationResult(passed=True)


# ═══════════════════════════════════════════════════════════════════════════
# 反馈分类器
# ═══════════════════════════════════════════════════════════════════════════

def classify_feedback(validation: ValidationResult) -> str:
    """根据验证结果分类反馈类型"""
    return validation.error_type


# ═══════════════════════════════════════════════════════════════════════════
# Reflection 循环 — 核心实现
# ═══════════════════════════════════════════════════════════════════════════

def reflection_loop(
    action: Callable[[Optional[dict], int], ActionResult],
    validate: Callable[[str], ValidationResult],
    max_retries: int = 3,
    cost_budget: float = 1.0,
    verbose: bool = True,
) -> ReflectionResult:
    """
    带 Reflection 的执行循环。

    关键设计：
    - validate 必须是外部验证器（测试、schema、引用对比），不能是模型自评
    - 如果选择自动修正，必须改变输入（prompt/参数/上下文），不是简单重跑
    - 停止条件硬编码，不由模型决定
    """
    cost_spent = 0.0
    last_error = None
    trace = []

    for attempt in range(max_retries):
        # 1. 执行动作（注入上次失败的事实信息）
        result = action(last_error, attempt)
        cost_spent += result.cost
        trace.append(f"[尝试 {attempt + 1}] 执行完成，成本 ${result.cost:.2f}")

        # 2. 外部验证（不是模型自评！）
        validation = validate(result.output)
        trace.append(f"[尝试 {attempt + 1}] 验证: {'✅ 通过' if validation.passed else '❌ ' + validation.message}")

        if validation.passed:
            if verbose:
                print(f"\n  ✅ Reflection 成功！第 {attempt + 1} 次尝试通过验证")
                print(f"     总成本: ${cost_spent:.3f}，总尝试: {attempt + 1}")
            return ReflectionResult(
                status="success",
                output=result.output,
                attempts=attempt + 1,
                cost=cost_spent,
                trace=trace
            )

        # 3. 分类失败，准备下一轮处理上下文
        error_type = classify_feedback(validation)
        last_error = {
            "type": error_type,
            "message": validation.message,
            "evidence": validation.evidence,
        }
        trace.append(f"[尝试 {attempt + 1}] 反馈分类: {error_type}")

        # 4. 停止条件检查
        # 4a. 成本上限
        if cost_spent > cost_budget:
            trace.append(f"[停止] 成本超限: ${cost_spent:.2f} > ${cost_budget:.2f}")
            if verbose:
                print(f"\n  🛑 成本超限停止: ${cost_spent:.2f} > ${cost_budget:.2f}")
            return ReflectionResult(
                status="stopped", reason="cost_limit",
                attempts=attempt + 1, cost=cost_spent,
                output=result.output, trace=trace
            )

        # 4b. 相同反馈重复出现（处理后反馈类型和 evidence 完全一致）
        if attempt >= 1:
            # 简化检测：如果连续两次反馈类型相同，判定为相同反馈
            trace.append(f"[停止] 相同反馈重复出现 ({error_type})，已尝试 {attempt + 1} 次")
            if verbose:
                print(f"\n  🛑 相同反馈重复停止: {error_type} 已连续出现 {attempt + 1} 次")
                print("     处理未改变失败结果，可能根因分类错误")
            return ReflectionResult(
                status="stopped", reason="repeated_failure",
                attempts=attempt + 1, cost=cost_spent,
                output=result.output, trace=trace
            )

        if verbose:
            print(f"  🔄 第 {attempt + 1} 次失败 ({error_type})，处理后重试...")
            print(f"     证据: {validation.evidence[:100]}...")

    # 超过最大重试次数
    trace.append(f"[停止] 超过最大重试次数 ({max_retries})")
    if verbose:
        print(f"\n  🛑 超过最大重试次数: {max_retries}")
    return ReflectionResult(
        status="stopped", reason="max_retries_exceeded",
        attempts=max_retries, cost=cost_spent,
        output=result.output if 'result' in dir() else "", trace=trace
    )


# ═══════════════════════════════════════════════════════════════════════════
# 显示辅助
# ═══════════════════════════════════════════════════════════════════════════

CHECK = "✅"
CROSS = "❌"
GEAR = "⚙️"
BULB = "💡"
STOP = "🛑"
LOOP = "🔄"


def print_header():
    print("\n" + "=" * 64)
    print("  Reflection — 基于反馈的决策闭环示例")
    print("=" * 64)
    print()
    print("  场景：知识助手 Agent 在三种任务中的 Reflection 表现")
    print()
    print("  演示选项:")
    print("    0 — V0 无反思：Agent 看到 TypeError，继续写 changelog")
    print("    1 — V1 格式修复：Schema 校验失败 → 重生成")
    print("    2 — V2 工具错误处理：参数错误 → 分类 → 决策 → 重试或停止")
    print("    3 — V3 测试驱动处理：测试失败 → 定位断言 → 修正代码或停止")
    print("    4 — 完整 Reflection 循环：触发→分类→决策→处理→验证或停止")
    print("    5 — 停止条件触发：相同反馈重复出现 → 硬停止")
    print("    6 — 对比总结")
    print("    q — 退出")
    print()


def section(title: str):
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")


# ═══════════════════════════════════════════════════════════════════════════
# 演示场景
# ═══════════════════════════════════════════════════════════════════════════

def demo_v0_no_reflection():
    """
    V0：无反思 — Agent 看到 TypeError 却继续执行。

    对应课程 6.1：Agent 在执行"运行测试"时遇到 TypeError，
    但它把错误输出当成普通 Observation 记录下来，然后继续写 changelog。
    """
    section("V0：无反思 — Agent 看到错误，继续往下走")

    print("""
  场景：发布准备流程。Agent 执行到"运行测试"这一步。

  [14:00] Agent 执行: npm test
  [14:01] 输出:
    TypeError: Cannot read properties of undefined (reading 'files')
        at runTests (test_runner.js:42:18)

  Agent 看到了这个输出。它做了什么？""")

    input("\n  [按 Enter 看 Agent 的反应...]")

    print("""
  Agent 的"思考":
    "测试执行完成。输出显示了一个 TypeError。
     这可能是测试环境的问题。
     让我把它记录到执行日志中。"

  Agent 的行为:
    1. 在状态中记录: "测试: 完成（有警告）"
    2. 继续执行下一步: "整理 changelog"
    3. 最终汇报: "✅ 发布准备已完成"

  ┌─────────────────────────────────────────────────────────────┐
  │ 问题：Agent 缺少"看到反馈信号→分类→决策→处理或停止"的闭环  │
  │                                                             │
  │ 这不是工具问题，不是 Planning 问题，不是 Memory 问题。      │
  │ 这是 Reflection 的缺失。                                     │
  │                                                             │
  │ 类比：仪表盘亮红灯，司机看了一眼，在日志里记下               │
  │       "14:32 红灯亮了"，然后继续以 120km/h 往前开。         │
  └─────────────────────────────────────────────────────────────┘
""")


def demo_v1_format_fix():
    """
    V1：格式修复 — Schema 校验失败触发重生成。

    对应课程 6.4.2-6.4.4：Schema 校验失败 → 反馈分类 → 重生成。
    """
    section("V1：格式修复 — Schema 校验失败 → 重生成")

    print("""
  场景：Agent 需要输出结构化 JSON，包含 tool_name、args、reason 三个字段。

  最基础的 Reflection 起点——不是"让模型反思内容质量"，
  而是用确定性规则检查输出格式。""")

    input("\n  [按 Enter 执行...]")

    # 模拟第一次尝试：缺字段
    bad_output = '{"tool": "search_notes", "query": "memory cleanup"}'
    print(f"\n  Agent 第 1 次输出: {bad_output}")
    print(f"  Schema 要求: tool_name, args, reason 三个字段必填")

    def action_v1(prev_error, attempt):
        if attempt == 0:
            # 第一次：缺字段
            return ActionResult(
                output='{"tool": "search_notes", "query": "memory cleanup"}',
                cost=0.01
            )
        else:
            # 修正后：补全字段
            return ActionResult(
                output='{"tool_name": "search_notes", "args": {"query": "memory cleanup"}, "reason": "用户询问 memory 清理机制"}',
                cost=0.01
            )

    result = reflection_loop(
        action=action_v1,
        validate=validate_json_schema,
        max_retries=3,
        verbose=True
    )

    print(f"\n  📋 Reflection 结果: {result.status}")
    print(f"     输出: {result.output}")
    print(f"     尝试次数: {result.attempts}，成本: ${result.cost:.3f}")

    print("""
  💡 关键点:
     - Schema 校验是确定性规则——字段存在/不存在，没有模糊空间
     - 不要过早加"内容反思"——先修格式问题，内容质量让用户判断
     - 这是 Reflection 最安全的起点：实现简单、验证明确、不会引入新错误
""")


def demo_v2_tool_error_fix():
    """
    V2：工具错误处理 — 参数错误触发分类与处理决策。

    对应课程 6.4.2-6.4.4：工具返回参数错误 → 分类 → 决定修正参数并重试。
    """
    section("V2：工具错误处理 — 参数错误 → 分类 → 决策")

    print("""
  场景：Agent 调用 search_notes 搜索笔记，但参数不合法。

  知识助手想搜索 Memory 相关内容，但 query 为空、limit 超出范围。""")

    input("\n  [按 Enter 执行...]")

    bad_params = '{"tool_name": "search_notes", "args": {"query": "", "limit": 500}, "reason": "查 memory 清理"}'
    print(f"\n  Agent 第 1 次调用: {bad_params}")

    def action_v2(prev_error, attempt):
        if attempt == 0:
            # 第一次：参数错误
            return ActionResult(
                output='search_notes(query="", limit=500) → Error: limit must be 1-100',
                cost=0.02
            )
        elif attempt == 1:
            # 修正：改参数值
            return ActionResult(
                output='search_notes(query="memory cleanup decay", limit=20) → 找到 3 条结果',
                cost=0.02
            )

    def validate_v2(output: str) -> ValidationResult:
        if "Error: limit must be" in output:
            return ValidationResult(
                passed=False,
                message="参数错误: limit=500 超出范围",
                evidence="工具返回: Error: limit must be 1-100 (got 500)",
                error_type="tool_param_error"
            )
        if "找到" in output and "结果" in output:
            return ValidationResult(passed=True, message="工具执行成功")
        return ValidationResult(
            passed=False,
            message="query 不能为空",
            evidence="工具返回: Error: query parameter is required",
            error_type="tool_param_error"
        )

    result = reflection_loop(
        action=action_v2,
        validate=validate_v2,
        max_retries=3,
        verbose=True
    )

    print(f"\n  📋 Reflection 结果: {result.status}")
    print(f"     尝试次数: {result.attempts}，成本: ${result.cost:.3f}")

    print("""
  💡 关键点:
     - 反馈分类决定处理方向：参数错误→改参数，不要连工具一起换
     - 自动修正必须改变输入：limit=500→20, query=""→"memory cleanup decay"
     - 区分可重试（网络超时）、可修正（参数错误）、不可恢复（权限不足）
""")


def demo_v3_test_driven_fix():
    """
    V3：测试驱动处理 — 外部测试框架驱动下一步决策。

    对应课程 6.4.2-6.4.5：测试失败 → 反馈分类 → 处理策略 → 重新验证或停止。
    """
    section("V3：测试驱动处理 — 测试失败 → 定位 → 修正代码或停止")

    print("""
  场景：Agent 修复了 session_manager.py 的 cleanup 方法，但代码有 bug。

  Agent 提交的代码绕过了 decay() 的清理逻辑，直接操作 _store 字典。
  外部测试框架捕获了这个问题。""")

    input("\n  [按 Enter 执行...]")

    print(f"\n  Agent 第 1 次提交的代码:")
    print(f"  {BUGGY_CLEANUP_CODE}")

    def action_v3(prev_error, attempt):
        if attempt == 0:
            return ActionResult(output=BUGGY_CLEANUP_CODE, cost=0.03)
        else:
            # 修正：使用正确的 API
            return ActionResult(output=CORRECT_CLEANUP_CODE, cost=0.03)

    result = reflection_loop(
        action=action_v3,
        validate=validate_tests,
        max_retries=3,
        verbose=True
    )

    print(f"\n  📋 Reflection 结果: {result.status}")
    print(f"     修正后代码: {result.output.strip()}")
    print(f"     尝试次数: {result.attempts}，成本: ${result.cost:.3f}")

    print("""
  💡 关键点:
     - validate 是外部测试框架，不是"让 LLM 再看看"
     - 修正后必须重新跑测试——"改了就算好了"不成立
     - 测试输出提供具体证据（报错行、断言值），修正才能精准
""")


def demo_full_reflection_loop():
    """
    完整 Reflection 循环：引用校验场景。

    对应课程 6.4.6 实战回放。
    """
    section("完整 Reflection 循环：触发→分类→决策→处理→验证或停止")

    print("""
  场景：用户让 Agent 分析代码中的 bug。Agent 引用了不存在的 API。

  这是课程 6.4.6 的回放——Agent 编造了 memory.clear_expired()，
  引用校验捕获了这个幻觉。""")

    input("\n  [按 Enter 执行...]")

    print("""
  [10:00] 用户："这段代码在处理 session 清理时好像有问题，帮我看看。"

  Agent（第 1 次尝试）：
    "问题在 session_manager.py 的 cleanup 方法中。该方法调用了
     memory.clear_expired()，但这个 API 在 Memory 模块中不存在——
     正确的 API 应该是 memory.remove_expired_sessions()。"
""")

    def action_citation(prev_error, attempt):
        if attempt == 0:
            # 幻觉输出：编造了 clear_expired()
            return ActionResult(
                output="问题在 session_manager.py 的 cleanup 方法中。该方法调用了 "
                       "`memory.clear_expired()`，但这个 API 在 Memory 模块中不存在——"
                       "正确的 API 应该是 `memory.remove_expired_sessions()`。",
                cost=0.02
            )
        else:
            # 修正后：基于检索结果的正确引用
            return ActionResult(
                output="问题在 session_manager.py 的 cleanup 方法中。笔记显示 Memory "
                       "模块的过期清理由 `decay()` → `_purge_old_records()` 完成 "
                       "[来源: agent-memory-mechanism.md §写入决策与遗忘机制]。"
                       "但 session_manager 的 cleanup 直接操作了 session 存储而没有调用 "
                       "decay()，导致过期记录被跳过。",
                cost=0.02
            )

    result = reflection_loop(
        action=action_citation,
        validate=lambda output: validate_citation(output, MOCK_NOTES),
        max_retries=3,
        verbose=True
    )

    print(f"\n  📋 Reflection 结果: {result.status}")
    print(f"     最终输出: {result.output[:120]}...")
    print(f"     尝试次数: {result.attempts}，成本: ${result.cost:.3f}")

    print("""
  💡 关键点:
     - 触发是被动的：validate() 返回 passed=false 才触发
     - 分类决定处理方向：幻觉→上下文缺失→补充检索
     - 自动修正改变输入：第 2 次 prompt 中多了检索到的原文
     - 处理后重新验证：不是"改了就算好了"
""")


def demo_stop_conditions():
    """
    停止条件触发演示：相同反馈重复出现 → 硬停止。

    对应课程 6.4.5：停止条件。
    """
    section("停止条件触发：相同反馈重复出现 → 硬停止")

    print("""
  场景：Agent 的 JSON 输出持续缺少 tool_name 字段。

  第 1 次：缺 tool_name
  第 2 次：缺 tool_name（处理没改变输入，只是重跑了相同 prompt）
  → 停止条件触发：相同反馈重复出现

  如果停止条件被绕过，Agent 可能会围绕同一个反馈反复处理。""")

    input("\n  [按 Enter 执行...]")

    # 永远返回缺 tool_name 的输出（模拟处理无效的情况）
    def action_stuck(prev_error, attempt):
        output = '{"tool": "search_notes", "args": {"query": "test"}}'
        return ActionResult(output=output, cost=0.01)

    result = reflection_loop(
        action=action_stuck,
        validate=validate_json_schema,
        max_retries=3,
        verbose=True
    )

    print(f"\n  📋 Reflection 结果: {result.status}")
    print(f"     停止原因: {result.reason}")
    for t in result.trace:
        print(f"     {t}")

    print("""
  💡 关键点:
     - 停止条件必须硬编码——模型在第 5 次处理时仍会说"这次应该对了"
     - 停止条件之间是 OR 关系：任意一个满足就停止
     - 相同反馈检测对比的是反馈类型（schema_error），不是完整错误字符串
     - 如果处理策略没有改变输入，第二次就是浪费——应该停止
""")


def demo_summary():
    """对比总结"""
    section("Reflection 四个阶段的对比总结")

    print("""
  ┌──────────┬──────────────────────┬──────────────────────────────┐
  │ 阶段     │ 做什么               │ 解决什么问题                  │
  ├──────────┼──────────────────────┼──────────────────────────────┤
  │ V0 无反思│ 失败直接返回          │ 验证任务是否真的需要决策闭环  │
  │ V1 格式  │ Schema 重校验+重生成  │ 结构化输出稳定性              │
  │ V2 工具  │ 参数/超时/权限分类处理│ 工具调用稳定性                │
  │ V3 测试  │ 测试失败→定位→处理决策│ 代码类任务质量                │
  │ V4 引用  │ 知识库原文反向验证     │ 知识问答可信度                │
  └──────────┴──────────────────────┴──────────────────────────────┘

  三个贯穿全链路的主线：

  1. 验证必须外部化
     Reflection 的可信度完全取决于验证器的可信度。
     → 测试框架、Schema 校验、引用原文对比、用户驳回
     → 不是"让 LLM 自己检查"

  2. 分类先于处理，根因先于症状
     看到"测试失败"就重跑——这不是 Reflection，这是祈祷。
     → 先问"为什么失败"：代码逻辑错？测试环境坏？幻觉？
     → 自动修正必须改变输入，不能只是重跑相同 prompt

  3. 停止条件是安全阀，不能交给模型决定
     模型没有"该停了"的直觉。
     → 最大重试 3 次、相同反馈 2 次即停、成本上限 $1
     → 必须硬编码，必须在运行时强制执行

  ───────────────────────────────────────────────────────────────

  什么时候不需要 Reflection：
     - 输出可以用确定性规则直接修正
     - 失败成本很低，简单重跑更便宜
     - 没有外部反馈信号（模型自评不可靠）
     - 任务对延迟非常敏感

  实用判断：
    "如果有明确反馈信号，并且自动处理成本低于失败成本，Reflection 值得引入。
     如果只是让模型'再想想'，通常不值得。"
""")


# ═══════════════════════════════════════════════════════════════════════════
# 主 REPL
# ═══════════════════════════════════════════════════════════════════════════

DEMOS = {
    "0": ("V0 无反思", demo_v0_no_reflection),
    "1": ("V1 格式修复", demo_v1_format_fix),
    "2": ("V2 工具错误处理", demo_v2_tool_error_fix),
    "3": ("V3 测试驱动处理", demo_v3_test_driven_fix),
    "4": ("完整 Reflection 循环", demo_full_reflection_loop),
    "5": ("停止条件触发", demo_stop_conditions),
    "6": ("对比总结", demo_summary),
}


def main():
    print_header()

    while True:
        try:
            choice = input("  请选择演示 (0-6, q 退出): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  再见！")
            break

        if choice.lower() == "q":
            print("  再见！")
            break

        if choice in DEMOS:
            name, fn = DEMOS[choice]
            fn()
            print(f"\n  ── {name} 演示完毕 ──")
            print("  （提示：选择 6 查看对比总结，q 退出）")
        else:
            print(f"  无效选项 '{choice}'。请输入 0-6 或 q 退出。")


if __name__ == "__main__":
    main()
