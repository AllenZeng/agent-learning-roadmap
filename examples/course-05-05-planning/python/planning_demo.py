#!/usr/bin/env python3
"""
课程五 05-05 Planning / Workflow Patterns 示例

一个交互式 REPL，演示四种 Planning 模式处理"发布准备"任务：
  - Chain：固定顺序执行
  - Router：根据输入分类路由
  - Plan-Execute：生成计划、执行、重规划
  - Graph：节点图、条件跳转、失败分支

用法:
    python planning_demo.py

在 REPL 中你可以:
  - 选择不同模式执行同一任务
  - 注入失败观察重规划行为
  - 对比不同模式对同一任务的处理差异
"""

import sys
import os

# 确保可以导入同目录的模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scenario import (
    StepStatus, describe_tools, describe_dependencies, DEFAULT_RELEASE_STEPS,
)
from patterns.chain import ChainExecutor
from patterns.router import RouterExecutor
from patterns.plan_execute import PlanExecuteExecutor
from patterns.graph import build_release_workflow, GraphResult


# ═══════════════════════════════════════════════════════════════════════════
# 显示辅助函数
# ═══════════════════════════════════════════════════════════════════════════

CHECK = "✅"
CROSS = "❌"
ARROW = "→"
GEAR = "⚙️"
ROCKET = "🚀"


def print_header():
    print("\n" + "=" * 60)
    print("  Planning / Workflow Patterns — 发布助手示例")
    print("=" * 60)
    print()
    print("  场景：你的 Agent 需要完成软件发布准备工作")
    print("  任务：检查 README → 运行测试 → 整理 changelog → 生成 checklist")
    print()
    print("  可用工具:")
    print(describe_tools())
    print()
    print("  步骤依赖:")
    print(describe_dependencies())
    print()


def print_step_start(step_name: str):
    print(f"  {GEAR} 执行: {step_name} ... ", end="", flush=True)


def print_step_end(result):
    if result.status == StepStatus.SUCCESS:
        print(f"{CHECK} 成功 ({result.duration_ms:.0f}ms)")
        if result.output:
            # 只显示前 80 个字符
            preview = result.output[:80].replace("\n", " ")
            print(f"     {preview}...")
    else:
        print(f"{CROSS} 失败")
        if result.error:
            print(f"     错误: {result.error}")


def print_step_end_compact(result, prefix="     "):
    """紧凑输出单步结果（用于 Graph 模式）"""
    icon = CHECK if result.status == StepStatus.SUCCESS else CROSS
    msg = result.output[:60].replace("\n", " ") if result.output else (result.error or "")
    print(f"{prefix}{icon} {result.step_name}: {msg}")


def print_result_summary(mode: str, status: str, steps_count: int, replan_count: int = 0):
    """打印执行结果摘要"""
    print()
    print("─" * 60)
    icon = CHECK if status == "completed" else CROSS
    print(f"  {icon} 模式: {mode} | 状态: {status} | 步骤数: {steps_count}")
    if replan_count > 0:
        print(f"     🔄 重规划次数: {replan_count}")
    print("─" * 60)


# ═══════════════════════════════════════════════════════════════════════════
# 模式执行函数
# ═══════════════════════════════════════════════════════════════════════════

def demo_chain():
    """演示 Chain 模式"""
    print()
    print("━" * 60)
    print("  模式 1: Chain — 固定顺序执行")
    print("━" * 60)
    print()
    print("  Chain 是最简单的模式：步骤按预定顺序执行，遇错即停。")
    print("  适合步骤稳定、异常少的任务。")
    print()

    executor = ChainExecutor()
    print(executor.describe())
    print()

    input("  按 Enter 开始执行...")
    print()

    result = executor.execute(
        on_step_start=print_step_start,
        on_step_end=print_step_end,
    )

    print_result_summary("Chain", result.status, len(result.results))


def demo_chain_with_failure():
    """演示 Chain 模式遇到失败"""
    print()
    print("━" * 60)
    print("  模式 1b: Chain — 遇到失败时")
    print("━" * 60)
    print()
    print("  Chain 的致命弱点：中途某步失败后，后续步骤全部跳过。")
    print('  下面模拟「运行测试」步骤失败，看看会发生什么。')
    print()

    # 手动模拟 Chain 执行，注入测试失败
    steps = DEFAULT_RELEASE_STEPS
    from scenario import TOOL_REGISTRY, StepResult, StepStatus

    for i, step_name in enumerate(steps, 1):
        tool = TOOL_REGISTRY.get(step_name)
        if not tool:
            continue
        should_fail = (step_name == "运行测试")
        print_step_start(step_name)
        result = tool(fail=should_fail)
        print_step_end(result)

        if result.status == StepStatus.ERROR:
            print()
            print(f"  {CROSS} Chain 模式: 第 {i} 步失败，停止执行。")
            print(f"     后续 {len(steps) - i} 个步骤被跳过:")
            for skipped in steps[i:]:
                print(f"       - {skipped} (未执行)")
            print()
            print("  💡 这就是为什么需要 Plan-Execute 和 Graph——")
            print("     它们可以在失败后重试、跳过或重规划。")
            return

    print_result_summary("Chain (with failure)", "completed", len(steps))


def demo_router():
    """演示 Router 模式"""
    print()
    print("━" * 60)
    print("  模式 2: Router — 根据输入分类选择路径")
    print("━" * 60)
    print()
    print('  Router 本质是「分类器 + 多条 Chain」。')
    print("  不同任务类型走不同的执行路径。")
    print()

    executor = RouterExecutor()

    # 展示三个不同输入的路由结果
    queries = [
        "帮我做 v1.2.0 发布准备",
        "修复 session pool 内存泄漏 bug",
        "更新 README 文档说明",
    ]

    for query in queries:
        print(f"  输入: \"{query}\"")
        category = executor.classify(query)
        steps = executor.routes.get(category, [])
        print(f"  {ARROW} 分类: {category} | 路径: {' → '.join(steps)}")
        print()

    input('  按 Enter 用「发布准备」请求执行 Router ...')
    print()

    result = executor.execute(
        query="帮我做 v1.2.0 发布准备",
        on_step_start=print_step_start,
        on_step_end=print_step_end,
    )

    print_result_summary(f"Router (分类: {result.category})", result.status, len(result.results))


def demo_plan_execute():
    """演示 Plan-Execute 模式"""
    print()
    print("━" * 60)
    print("  模式 3: Plan-Execute — 生成计划 → 执行 → 重规划")
    print("━" * 60)
    print()
    print("  Plan-Execute 是 Planning 最经典的实现。")
    print("  先生成结构化计划，用户确认后执行。失败时可重规划。")
    print()

    executor = PlanExecuteExecutor()
    goal = "准备 v1.2.0 版本发布"
    plan = executor.generate_plan(goal)

    print(executor.generate_plan_text(plan))
    print()

    input("  按 Enter 确认计划并开始执行（正常模式，无失败注入）...")
    print()

    result = executor.execute(
        goal=goal,
        auto_confirm=True,
        on_step_start=print_step_start,
        on_step_end=print_step_end,
    )

    print_result_summary("Plan-Execute", result.status, len(result.results), result.replan_count)


def demo_plan_execute_with_failure():
    """演示 Plan-Execute 遇到失败后的重规划"""
    print()
    print("━" * 60)
    print("  模式 3b: Plan-Execute — 失败 → 重规划")
    print("━" * 60)
    print()
    print("  这是 Plan-Execute 与 Chain 的关键差异。")
    print('  下面注入「运行测试」失败，观察重规划行为。')
    print()

    executor = PlanExecuteExecutor()
    goal = "准备 v1.2.0 版本发布"
    plan = executor.generate_plan(goal)

    print(executor.generate_plan_text(plan))
    print()

    def on_replan_show(failed_step: str, new_steps):
        print(f"\n  🔄 重规划触发！")
        print(f"     失败步骤: {failed_step}")
        print(f"     新步骤 ({len(new_steps)} 个):")
        for s in new_steps:
            print(f"       - {s.name}: {s.description}")

    input('  按 Enter 开始执行（将注入「运行测试」失败）...')
    print()

    result = executor.execute(
        goal=goal,
        auto_confirm=True,
        inject_failures={"运行测试": True},
        on_step_start=print_step_start,
        on_step_end=print_step_end,
        on_replan=on_replan_show,
    )

    print_result_summary("Plan-Execute (with replan)", result.status, len(result.results), result.replan_count)

    if result.replan_count > 0:
        print()
        print("  💡 注意：Plan-Execute 在失败后自动生成了替代步骤。")
        print("     这是 Chain 做不到的——Chain 遇错即停。")


def demo_graph():
    """演示 Graph 模式"""
    print()
    print("━" * 60)
    print("  模式 4: Graph — 节点 + 条件边 + 状态机")
    print("━" * 60)
    print()
    print("  Graph 是 Plan-Execute 的泛化：任务建模为有向图。")
    print("  每个节点有 success 和 error 两条出边，可以跳转到不同节点。")
    print("  支持环路检测、节点级重试、失败分支。")
    print()

    graph = build_release_workflow()
    print(graph.describe())
    print()

    def on_node_start(node_name: str):
        print(f"  {GEAR} 节点 [{node_name}] 开始...")

    def on_node_end(node_name: str, result, next_node: str):
        icon = CHECK if result.status == StepStatus.SUCCESS else CROSS
        print(f"     {icon} 完成 → 下一节点: {next_node}")

    input("  按 Enter 开始执行 Graph（正常模式）...")
    print()

    result = graph.run(
        on_node_start=on_node_start,
        on_node_end=on_node_end,
    )

    print()
    print("─" * 60)
    print(f"  执行路径: {' → '.join(result.path)}")
    print_result_summary("Graph", result.status, len(result.path))

    print()
    print("  💡 Graph 的关键优势：")
    print("     - 每个节点可配置独立的失败分支（on_error）")
    print("     - 支持节点级重试（测试节点配置了 max_retries=2）")
    print("     - 可精确回放和调试（执行路径是确定的）")
    print("     - 建模成本高——只在状态和分支真的复杂时才引入")


def demo_graph_with_failure():
    """演示 Graph 遇到 README 检查失败时的分支跳转"""
    print()
    print("━" * 60)
    print("  模式 4b: Graph — 失败分支跳转")
    print("━" * 60)
    print()
    print("  Graph 的真正威力在失败分支。")
    print('  下面注入「检查 README」失败，观察它如何跳转到修复节点。')
    print()

    graph = build_release_workflow(inject_failures={"检查 README": True})

    def on_node_start(node_name: str):
        print(f"  {GEAR} 节点 [{node_name}] 开始...")

    def on_node_end(node_name: str, result, next_node: str):
        icon = CHECK if result.status == StepStatus.SUCCESS else CROSS
        print(f"     {icon} 完成 → 下一节点: {next_node}")

    input("  按 Enter 开始执行 Graph（注入 README 检查失败）...")
    print()

    result = graph.run(
        on_node_start=on_node_start,
        on_node_end=on_node_end,
    )

    print()
    print("─" * 60)
    print(f"  执行路径: {' → '.join(result.path)}")
    print_result_summary("Graph (with failure branch)", result.status, len(result.path))

    print()
    print('  💡 注意：README 检查失败后，Graph 自动跳转到「修复 README」节点。')
    print("     这是 Chain 做不到的——Chain 的步骤顺序是固定的。")
    print("     这也是 Plan-Execute 的不同方式——Graph 的失败路径在构建时就已定义。")


# ═══════════════════════════════════════════════════════════════════════════
# 对比模式
# ═══════════════════════════════════════════════════════════════════════════

def demo_compare():
    """对比四种模式的关键差异"""
    print()
    print("━" * 60)
    print("  四种模式对比总结")
    print("━" * 60)
    print()

    comparisons = [
        ("维度", "Chain", "Router", "Plan-Execute", "Graph"),
        ("决策方式", "固定顺序", "分类器决定", "计划+重规划", "条件边跳转"),
        ("灵活性", "最低", "中（路径可选）", "高（动态规划）", "最高（任意跳转）"),
        ("失败处理", "遇错即停", "遇错即停", "重试+重规划", "跳转到错误节点"),
        ("用户确认", "无", "无", "支持", "节点级确认"),
        ("并行支持", "无", "无", "有限", "有限"),
        ("调试难度", "低", "低", "中", "高"),
        ("建模成本", "低", "低", "中", "高"),
        ("适用场景", "步骤固定、异常少", "多类型入口", "中长任务、需规划", "状态复杂、分支多"),
    ]

    # 打印表格
    col_widths = [14, 16, 18, 18, 18]
    for row in comparisons:
        print("  ", end="")
        for i, cell in enumerate(row):
            print(f"{cell:<{col_widths[i]}}", end="")
        print()

    print()
    print("  💡 选择指南:")
    print("     步骤完全固定 → Chain")
    print("     多类型入口   → Router")
    print("     需全局规划   → Plan-Execute")
    print("     复杂状态机   → Graph")
    print()
    print("  ⚠️  不要把简单任务硬塞进 Graph——节点、边、状态和错误分支都需要维护成本。")


# ═══════════════════════════════════════════════════════════════════════════
# REPL 主菜单
# ═══════════════════════════════════════════════════════════════════════════

def main():
    print_header()

    menu_items = [
        ("1", "Chain 正常执行", demo_chain),
        ("1b", "Chain 遇到失败", demo_chain_with_failure),
        ("2", "Router 分类路由", demo_router),
        ("3", "Plan-Execute 正常执行", demo_plan_execute),
        ("3b", "Plan-Execute 失败→重规划", demo_plan_execute_with_failure),
        ("4", "Graph 正常执行", demo_graph),
        ("4b", "Graph 失败分支跳转", demo_graph_with_failure),
        ("5", "四种模式对比总结", demo_compare),
        ("0", "退出", None),
    ]

    while True:
        print()
        print("=" * 60)
        print("  选择演示:")
        for key, desc, _ in menu_items:
            if key == "0":
                print(f"  [{key}] {desc}")
            else:
                print(f"  [{key}] {desc}")
        print("=" * 60)

        choice = input("  请输入选择 > ").strip()

        if choice == "0":
            print("\n  再见！\n")
            break

        for key, desc, fn in menu_items:
            if choice == key and fn:
                fn()
                break
        else:
            # 检查是否是数字
            try:
                idx = int(choice) - 1
                menu_items[idx][2]()
            except (ValueError, IndexError):
                print(f"\n  {CROSS} 无效选择: {choice}")

if __name__ == "__main__":
    main()
