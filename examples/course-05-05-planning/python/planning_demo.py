#!/usr/bin/env python3
"""
Course 05 05-05 Planning / Workflow Patterns text

An interactive REPL，demonstrates four Planning patternProcessing"releasetext"Task：
  - Chain：fixed-order execution
  - Router：textInputclassificationroute
  - Plan-Execute：text、execute、replan
  - Graph：nodegraph、conditional transitions、failedbranches

Usage:
    python planning_demo.py

In REPL mediumyou can:
  - text
  - textfailedtextreplanbehavior
  - textProcessingtext
"""

import sys
import os

# Ensure modules in the same directory can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scenario import (
    StepStatus, describe_tools, describe_dependencies, DEFAULT_RELEASE_STEPS,
)
from patterns.chain import ChainExecutor
from patterns.router import RouterExecutor
from patterns.plan_execute import PlanExecuteExecutor
from patterns.graph import build_release_workflow, GraphResult


# ═══════════════════════════════════════════════════════════════════════════
# Display helper functions
# ═══════════════════════════════════════════════════════════════════════════

CHECK = "✅"
CROSS = "❌"
ARROW = "→"
GEAR = "⚙️"
ROCKET = "🚀"


def print_header():
    print("\n" + "=" * 60)
    print("  Planning / Workflow Patterns — releasetext")
    print("=" * 60)
    print()
    print("  Scenario：your Agent needscompletesoftwarereleasetext")
    print("  Task：Check README → Run tests → Prepare changelog → Generate checklist")
    print()
    print("  available tools:")
    print(describe_tools())
    print()
    print("  stepdependencies:")
    print(describe_dependencies())
    print()


def print_step_start(step_name: str):
    print(f"  {GEAR} Execute: {step_name} ... ", end="", flush=True)


def print_step_end(result):
    if result.status == StepStatus.SUCCESS:
        print(f"{CHECK} success ({result.duration_ms:.0f}ms)")
        if result.output:
            # Show only the first 80 characters
            preview = result.output[:80].replace("\n", " ")
            print(f"     {preview}...")
    else:
        print(f"{CROSS} failed")
        if result.error:
            print(f"     error: {result.error}")


def print_step_end_compact(result, prefix="     "):
    """textResult（text Graph pattern)"""
    icon = CHECK if result.status == StepStatus.SUCCESS else CROSS
    msg = result.output[:60].replace("\n", " ") if result.output else (result.error or "")
    print(f"{prefix}{icon} {result.step_name}: {msg}")


def print_result_summary(mode: str, status: str, steps_count: int, replan_count: int = 0):
    """textExecution resulttext"""
    print()
    print("─" * 60)
    icon = CHECK if status == "completed" else CROSS
    print(f"  {icon} pattern: {mode} | Status: {status} | step count: {steps_count}")
    if replan_count > 0:
        print(f"     🔄 replan count: {replan_count}")
    print("─" * 60)


# ═══════════════════════════════════════════════════════════════════════════
# Pattern execution functions
# ═══════════════════════════════════════════════════════════════════════════

def demo_chain():
    """text Chain mode"""
    print()
    print("━" * 60)
    print("  Pattern 1: Chain — fixed-order execution")
    print("━" * 60)
    print()
    print("  Chain is the simplest pattern: steps run in a predefined order and stop on error.")
    print("  is suitable forsteptext、tasks with few exceptions。")
    print()

    executor = ChainExecutor()
    print(executor.describe())
    print()

    input("  text Enter startedexecute...")
    print()

    result = executor.execute(
        on_step_start=print_step_start,
        on_step_end=print_step_end,
    )

    print_result_summary("Chain", result.status, len(result.results))


def demo_chain_with_failure():
    """text Chain modeencountersfailed"""
    print()
    print("━" * 60)
    print("  Pattern 1b: Chain — when failure occurs")
    print("━" * 60)
    print()
    print("  Chain's fatal weakness: when one middle step fails, all later steps are skipped.")
    print('  simulate below「Run tests」stepfailed，see what happens。')
    print()

    # Manually simulate Chain execution and inject a test failure
    steps = DEFAULT_RELEASE_STEPS
    from scenario import TOOL_REGISTRY, StepResult, StepStatus

    for i, step_name in enumerate(steps, 1):
        tool = TOOL_REGISTRY.get(step_name)
        if not tool:
            continue
        should_fail = (step_name == "Run tests")
        print_step_start(step_name)
        result = tool(fail=should_fail)
        print_step_end(result)

        if result.status == StepStatus.ERROR:
            print()
            print(f"  {CROSS} Chain mode: rank {i}  step failed; stopping execution.")
            print(f"     later {len(steps) - i} steps skipped:")
            for skipped in steps[i:]:
                print(f"       - {skipped} (not executed)")
            print()
            print("  💡 This is why Plan-Execute and Graph are needed -")
            print("     they can retry, skip, or replan after failure.")
            return

    print_result_summary("Chain (with failure)", "completed", len(steps))


def demo_router():
    """text Router pattern"""
    print()
    print("━" * 60)
    print("  Pattern 2: Router — choose path by input classification")
    print("━" * 60)
    print()
    print('  Router text「classificationtext + text Chain」。')
    print("  textExecution path。")
    print()

    executor = RouterExecutor()

    # Show routing results for three different inputs
    queries = [
        "Help me prepare the v1.2.0 release",
        "Fix the session pool memory leak bug",
        "Update README documentation instructions",
    ]

    for query in queries:
        print(f"  Input: \"{query}\"")
        category = executor.classify(query)
        steps = executor.routes.get(category, [])
        print(f"  {ARROW} classification: {category} | path: {' → '.join(steps)}")
        print()

    input('  text Enter use「releasetext」request to execute Router ...')
    print()

    result = executor.execute(
        query="Help me prepare the v1.2.0 release",
        on_step_start=print_step_start,
        on_step_end=print_step_end,
    )

    print_result_summary(f"Router (classification: {result.category})", result.status, len(result.results))


def demo_plan_execute():
    """text Plan-Execute pattern"""
    print()
    print("━" * 60)
    print("  Pattern 3: Plan-Execute — generate plan -> execute -> replan")
    print("━" * 60)
    print()
    print("  Plan-Execute is the classic implementation of Planning.")
    print("  first generate a structured plan，user confirmationtext。failedtextreplan。")
    print()

    executor = PlanExecuteExecutor()
    goal = "Prepare the v1.2.0 release"
    plan = executor.generate_plan(goal)

    print(executor.generate_plan_text(plan))
    print()

    input("  text Enter textstartedexecute（text，nonefailedtext)...")
    print()

    result = executor.execute(
        goal=goal,
        auto_confirm=True,
        on_step_start=print_step_start,
        on_step_end=print_step_end,
    )

    print_result_summary("Plan-Execute", result.status, len(result.results), result.replan_count)


def demo_plan_execute_with_failure():
    """text Plan-Execute encountersfailedtextreplan"""
    print()
    print("━" * 60)
    print("  Pattern 3b: Plan-Execute — failed → replan")
    print("━" * 60)
    print()
    print("  This is Plan-Execute compared with Chain text。")
    print('  text「Run tests」failed，textreplanbehavior。')
    print()

    executor = PlanExecuteExecutor()
    goal = "Prepare the v1.2.0 release"
    plan = executor.generate_plan(goal)

    print(executor.generate_plan_text(plan))
    print()

    def on_replan_show(failed_step: str, new_steps):
        print(f"\n  🔄 replantrigger！")
        print(f"     failed step: {failed_step}")
        print(f"     new steps ({len(new_steps)} items):")
        for s in new_steps:
            print(f"       - {s.name}: {s.description}")

    input('  text Enter startedexecute（will inject「Run tests」failed)...')
    print()

    result = executor.execute(
        goal=goal,
        auto_confirm=True,
        inject_failures={"Run tests": True},
        on_step_start=print_step_start,
        on_step_end=print_step_end,
        on_replan=on_replan_show,
    )

    print_result_summary("Plan-Execute (with replan)", result.status, len(result.results), result.replan_count)

    if result.replan_count > 0:
        print()
        print("  💡 Note: Plan-Execute automatically generates alternative steps after failure.")
        print("     This is something Chain cannot do——Chain stops on error.")


def demo_graph():
    """text Graph pattern"""
    print()
    print("━" * 60)
    print("  Pattern 4: Graph — node + conditional edge + state machine")
    print("━" * 60)
    print()
    print("  Graph generalizes Plan-Execute: the task is modeled as a directed graph.")
    print("  eachnodetext success text error two outgoing edges，textnode。")
    print("  supports loop detection、nodetextretry、failedbranches。")
    print()

    graph = build_release_workflow()
    print(graph.describe())
    print()

    def on_node_start(node_name: str):
        print(f"  {GEAR} node [{node_name}] started...")

    def on_node_end(node_name: str, result, next_node: str):
        icon = CHECK if result.status == StepStatus.SUCCESS else CROSS
        print(f"     {icon} complete -> next node: {next_node}")

    input("  text Enter startedexecute Graph（text)...")
    print()

    result = graph.run(
        on_node_start=on_node_start,
        on_node_end=on_node_end,
    )

    print()
    print("─" * 60)
    print(f"  Execution path: {' → '.join(result.path)}")
    print_result_summary("Graph", result.status, len(result.path))

    print()
    print("  💡 Key advantages of Graph：")
    print("     - each node can configure an independent failure branch（on_error)")
    print("     - supports node-level retry（testsnodetext max_retries=2)")
    print("     - can be replayed and debugged precisely（execution path is deterministic)")
    print("     - modeling cost is high——introduce it only when state and branches are truly complex")


def demo_graph_with_failure():
    """text Graph encounters README textfailedtext"""
    print()
    print("━" * 60)
    print("  Pattern 4b: Graph — failure-branch transition")
    print("━" * 60)
    print()
    print("  Graph textfailedbranches。")
    print('  text「Check README」failed，textittextfixnode。')
    print()

    graph = build_release_workflow(inject_failures={"Check README": True})

    def on_node_start(node_name: str):
        print(f"  {GEAR} node [{node_name}] started...")

    def on_node_end(node_name: str, result, next_node: str):
        icon = CHECK if result.status == StepStatus.SUCCESS else CROSS
        print(f"     {icon} complete -> next node: {next_node}")

    input("  text Enter startedexecute Graph（text README textfailed)...")
    print()

    result = graph.run(
        on_node_start=on_node_start,
        on_node_end=on_node_end,
    )

    print()
    print("─" * 60)
    print(f"  Execution path: {' → '.join(result.path)}")
    print_result_summary("Graph (with failure branch)", result.status, len(result.path))

    print()
    print('  💡 Note：README textfailedtext，Graph text「fix README」node。')
    print("     This is something Chain cannot do——Chain has a fixed step order.")
    print("     This is also Plan-Execute a different approach——Graph textfailedpathtext。")


# ═══════════════════════════════════════════════════════════════════════════
# Comparison mode
# ═══════════════════════════════════════════════════════════════════════════

def demo_compare():
    """text"""
    print()
    print("━" * 60)
    print("  Summary comparison of four patterns")
    print("━" * 60)
    print()

    comparisons = [
        ("Dimension", "Chain", "Router", "Plan-Execute", "Graph"),
        ("Decision style", "fixed order", "classifier decides", "plan + replan", "conditional-edge transition"),
        ("Flexibility", "lowest", "medium (path selectable)", "high (dynamic planning)", "highest (arbitrary transitions)"),
        ("failure handling", "stop on error", "stop on error", "retry+replan", "jump to error node"),
        ("user confirmation", "none", "none", "supported", "node-level confirmation"),
        ("parallel support", "none", "none", "limited", "limited"),
        ("Debug difficulty", "low", "low", "medium", "high"),
        ("Modelingcost", "low", "low", "medium", "high"),
        ("Use case", "stepfixed、text", "multi-type entry", "mediumtext、text", "Statuscomplex、text"),
    ]

    # Print the table
    col_widths = [14, 16, 18, 18, 18]
    for row in comparisons:
        print("  ", end="")
        for i, cell in enumerate(row):
            print(f"{cell:<{col_widths[i]}}", end="")
        print()

    print()
    print("  💡 Selection guide:")
    print("     stepfully fixed → Chain")
    print("     multi-type entry   → Router")
    print("     needs global planning   → Plan-Execute")
    print("     complexStatustext   → Graph")
    print()
    print("  ⚠️  do notMove simple tasks into Graph——node、text、Statustexterrortextcost。")


# ═══════════════════════════════════════════════════════════════════════════
# REPL main menu
# ═══════════════════════════════════════════════════════════════════════════

def main():
    print_header()

    menu_items = [
        ("1", "Chain normal execution", demo_chain),
        ("1b", "Chain encountersfailed", demo_chain_with_failure),
        ("2", "Router classificationroute", demo_router),
        ("3", "Plan-Execute normal execution", demo_plan_execute),
        ("3b", "Plan-Execute failed→replan", demo_plan_execute_with_failure),
        ("4", "Graph normal execution", demo_graph),
        ("4b", "Graph failure-branch transition", demo_graph_with_failure),
        ("5", "Summary comparison of four patterns", demo_compare),
        ("0", "Exit", None),
    ]

    while True:
        print()
        print("=" * 60)
        print("  Choose demo:")
        for key, desc, _ in menu_items:
            if key == "0":
                print(f"  [{key}] {desc}")
            else:
                print(f"  [{key}] {desc}")
        print("=" * 60)

        choice = input("  pleaseInputchoose > ").strip()

        if choice == "0":
            print("\n  Goodbye!\n")
            break

        for key, desc, fn in menu_items:
            if choice == key and fn:
                fn()
                break
        else:
            # Check whether it is a number
            try:
                idx = int(choice) - 1
                menu_items[idx][2]()
            except (ValueError, IndexError):
                print(f"\n  {CROSS} nonetext: {choice}")

if __name__ == "__main__":
    main()
