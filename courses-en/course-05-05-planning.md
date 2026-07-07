# Chapter 5: Planning / Workflow Patterns

[Back to Course 5](./course-05-01-scenario-enhancement.md) | [Previous Chapter](./course-05-04-context-engineering.md) | [Next Chapter](./course-05-06-reflection.md)

## Chapter Contents

- [5.1 Long Tasks Make Agents Drift](#51-long-tasks-make-agents-drift)
- [5.2 Why ReAct Alone Is Not Enough: From In-the-Moment Decisions to Explicit Workflows](#52-why-react-alone-is-not-enough-from-in-the-moment-decisions-to-explicit-workflows)
- [5.3 Task Organization Matters More Than Single-Step Decisions](#53-task-organization-matters-more-than-single-step-decisions)
- [5.4 Choose the Organization Pattern Before Discussing Agent Capability](#54-choose-the-organization-pattern-before-discussing-agent-capability)
  - [5.4.1 Chain: Determinism From a Fixed Order, at the Cost of Recovery](#541-chain-determinism-from-a-fixed-order-at-the-cost-of-recovery)
  - [5.4.2 Router: Classify the Task Before Choosing the Execution Path](#542-router-classify-the-task-before-choosing-the-execution-path)
  - [5.4.3 Plan-Execute: Make the Plan Visible, Then Replan After Failure](#543-plan-execute-make-the-plan-visible-then-replan-after-failure)
  - [5.4.4 Graph: Put Exception Paths Into the State Machine Up Front](#544-graph-put-exception-paths-into-the-state-machine-up-front)
  - [5.4.5 The Happy Path Looks Similar; Failure Reveals the Difference](#545-the-happy-path-looks-similar-failure-reveals-the-difference)
  - [5.4.6 Beyond the Four Patterns: Parallelization, Orchestrator-Workers, and Evaluator-Optimizer](#546-beyond-the-four-patterns-parallelization-orchestrator-workers-and-evaluator-optimizer)
- [5.5 Do Not Start by Drawing a Graph: Let Failures and Evals Drive the Upgrade](#55-do-not-start-by-drawing-a-graph-let-failures-and-evals-drive-the-upgrade)
- [5.6 Planning Usually Fails on Exception Paths](#56-planning-usually-fails-on-exception-paths)
  - [5.6.1 Quick Reference: Common Planning Failure Modes](#561-quick-reference-common-planning-failure-modes)
  - [5.6.2 Three Debugging Stories: Infinite Replanning, Untested Branches, and Unauthorized Plan Changes](#562-three-debugging-stories-infinite-replanning-untested-branches-and-unauthorized-plan-changes)
- [5.7 Not Every Multi-Step Task Deserves Planning](#57-not-every-multi-step-task-deserves-planning)
- [5.8 From Drift to Replayability: A Planning Lifecycle](#58-from-drift-to-replayability-a-planning-lifecycle)
- [Runnable Example](#runnable-example)

---

## 5.1 Long Tasks Make Agents Drift

Return to the knowledge assistant from 1.1. You give it a multi-step task:

```text
Help me prepare for a release: check whether the README is complete,
run the tests, organize the changelog, and generate a release checklist.
```

The agent starts working. First, it reads the README and writes a short comment. Then it starts browsing the source code to verify one detail mentioned in the README. After that, it searches related GitHub issues. Five minutes later, you come back and find that it has drifted away from the original goal. You inspect the trace and realize that after step 4, it never touched anything related to the release again.

The reason is simple: **a raw ReAct loop has no concept of global task structure.** It makes a locally reasonable decision at each step, but a sequence of locally reasonable decisions does not necessarily reach the goal. It is like a driver without navigation: every turn may look plausible, yet the car may never arrive.

The longer the task, the more you need a mechanism that can answer:

- What steps should be done? What dependencies exist between them?
- Which steps can run in parallel?
- Which steps require user approval before execution?
- If one step fails, should the agent retry, skip, replan, or stop?

These are the core questions addressed by Planning / Workflow Patterns.

**This chapter uses a single running example: a release assistant.** The scenario is:

```text
Scenario: Release Assistant Agent

User: A developer maintaining an open-source project
Typical task: Prepare a software release
              (check README, run tests, organize changelog, generate checklist)
Complexity: 4 steps with dependencies
            (the changelog should be generated after tests pass;
             the checklist depends on all previous steps)
Challenges:
  - Steps are not fully independent; some must happen before others.
  - Tests may fail; the agent must decide whether to retry or skip.
  - The README may miss required sections; the agent must decide whether this blocks release.
  - First-time users may not know every required step; the agent may need to fill gaps.

Planning requirements:
  - Dependencies between steps must be explicitly modeled.
  - Each failure needs a clear handling strategy.
  - The user may need to approve the plan before execution.
```

Every pattern in this chapter will use the same release assistant scenario. The task is the same, but different organization patterns lead to very different behavior.

## 5.2 Why ReAct Alone Is Not Enough: From In-the-Moment Decisions to Explicit Workflows

Planning was not part of agent systems from the beginning. The field evolved in stages.

**October 2022: the ReAct paper by Yao et al.** The paper showed that alternating between reasoning and acting can significantly improve performance on complex tasks. But ReAct is still an in-the-moment loop: the model sees the current observation and chooses the next action. This works well for tasks with three to five steps. Once the task becomes longer, the weakness appears: the model lacks a global view and can drift.

**Early 2023: Plan-and-Execute became common.** The idea is direct: ask the model to break the task into an execution plan first, let the user confirm it, and then execute the steps. This solves ReAct's lack of a global view, but introduces new problems. The plan may be impossible to execute in the real environment, or the environment may change after the plan is created.

**Late 2023: graph-based workflows became popular.** Frameworks such as LangGraph and CrewAI began modeling tasks as nodes and edges. Each node represents an action or decision, and each edge represents a state transition. On failure, the workflow can jump back to a specific node and retry. Graphs are not the only evolution of Plan-and-Execute. Their real contribution is turning a one-dimensional step list into explicit control flow: branches, rollback, parallel paths, human approval points, and even patterns such as ReAct, Router, and Plan-Execute can all be represented inside a graph.

**Since 2024: Workflow Patterns have become a shared vocabulary.** Anthropic's "Building Effective Agents" article summarizes common patterns such as Prompt Chaining, Routing, Parallelization, Orchestrator-Workers, and Evaluator-Optimizer. The OpenAI Agents SDK puts handoffs, guardrails, tracing, and evals into the basic agent orchestration toolbox. LangGraph emphasizes durable execution, human-in-the-loop, persistence, and time travel. Together, these practices point to the same principle: most systems should not start with a complex graph. Choose the smallest organization pattern that fits the task shape, then use traces and evals to verify whether more complexity is actually useful.

## 5.3 Task Organization Matters More Than Single-Step Decisions

A ReAct loop is good at dynamic decision-making, but it does not naturally guarantee global structure.

Complex tasks usually fall into several shapes:

| Task shape | Example | Suitable pattern |
|---|---|---|
| Fixed steps | Read file -> summarize -> output | Chain |
| Inputs differ by type | Q&A, writing, and code review each need different paths | Router |
| Subtasks are independent | Check README, tests, and dependency vulnerabilities at the same time | Parallelization |
| Number of subtasks is unknown | Code migration, cross-file refactoring, competitor research | Orchestrator-Workers |
| Output needs repeated refinement | Copy editing, code repair, plan review | Evaluator-Optimizer |
| Tool choice is dynamic | The agent must inspect and decide what to do next | ReAct Loop |
| Task can be decomposed first | Release preparation, research report, code migration | Plan-Execute |
| State and branches are complex | Ticket handling, approval flow, multi-stage task | Graph |

A table is useful, but the difference becomes clearer when we run the same release task through different patterns:

```text
Task: "Prepare the v1.2.0 release"

┌─────────────────────────────────────────────────────────────────────────┐
│ Chain pattern:                                                           │
│   Check README → run tests → organize changelog → generate checklist     │
│   Stop on error. Test failure → all later steps are skipped.             │
│                                                                         │
│ Plan-Execute pattern:                                                    │
│   1. Generate a plan (the same 4 steps)                                  │
│   2. Ask the user to confirm                                             │
│   3. Execute step by step. Test failure → retry twice → still failing    │
│      → replan: "The failure is an assertion error in                     │
│      test_memory_cleanup. New next steps: analyze failure → fix          │
│      → rerun tests → continue."                                          │
│                                                                         │
│ Graph pattern:                                                           │
│   Check README ──success──▶ run tests ──success──▶ changelog ──▶ checklist│
│        │                      │                                         │
│        error                  error                                      │
│        ▼                      ▼                                         │
│   fix README              retry tests                                    │
│   (then stop for          (retry succeeds→changelog;                     │
│    human review)           retry fails→stop)                             │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key insight:** the difference between these patterns is not whether they can finish the happy path. They all can. The difference appears when something goes wrong:

- Chain gives up.
- Plan-Execute adapts dynamically.
- Graph follows a predefined branch.

So the useful question is not "Is Planning good?" The useful questions are:

- Is the task complex enough that it should be decomposed first?
- Are the steps stable enough to become a fixed workflow?
- Does execution need mid-course replanning?
- Should the user approve the plan?
- After failure, does the workflow need to return to a specific node?

## 5.4 Choose the Organization Pattern Before Discussing Agent Capability

The following sections use the release assistant to compare each pattern's interface shape, execution behavior, and boundaries. The runnable example at the end of this chapter contains full code. The code snippets in the text focus on control flow and omit some engineering details.

### 5.4.1 Chain: Determinism From a Fixed Order, at the Cost of Recovery

A Chain means "follow this road to the end." It is like an assembly line: each station processes the item in a fixed order, and later stations wait for earlier stations. In the release assistant, the four steps are fixed: check README, run tests, organize changelog, generate checklist. There are no branches and no "if this, then that."

```python
class ChainExecutor:
    """Execute steps in a fixed order. Stop on error; no branches or retries."""

    def execute(self, on_step_start=None, on_step_end=None):
        for i, step_name in enumerate(self.steps):
            tool = TOOL_REGISTRY.get(step_name)
            if not tool:
                return ChainResult(status="failed", failed_at=i,
                                   error=f"Tool not found: {step_name}")

            result = tool()  # Execute the step
            if result.status == StepStatus.ERROR:
                return ChainResult(status="failed", failed_at=i,
                                   error=result.error)
            # Success; continue to the next step.

        return ChainResult(status="completed", results=all_results)
```

**The problem with Chain is not the happy path.** If everything succeeds, all four steps run in order and the output is fine. The problem appears on exception paths:

```text
Scenario: tests fail

Chain execution:
  ✅ Check README → passed
     (Contributing section is missing, but this is treated as non-fatal)
  ❌ Run tests → failed! 1 test failed
  ⏭️ Organize changelog → skipped
  ⏭️ Generate checklist → skipped

Final report: "Release preparation failed at step 2: run tests."

User reaction: Why did one failing test stop the whole release flow?
That test is a legacy failure and unrelated to this release.
Chain cannot say, "This test does not block release; we can continue."
It can only stop.
```

**Chain has a narrow but clear boundary:** the steps must be fully known, unlikely to surprise you, and not require dynamic decisions. For example: "read config -> parse -> validate -> write to cache." If one of these steps fails, stopping is probably the right behavior.

Chain looks simple, but its failures are often underestimated. "Stop on error" is itself a design decision, and it is not always correct.

| Failure symptom | Typical cause | Fix |
|---|---|---|
| A non-critical step interrupts the whole workflow | Chain does not distinguish blocking errors from non-blocking warnings. A missing optional README section and a fully failing test suite both look like "failure." | If Chain is required, classify results inside each step as `error` or `warning`; warnings should not block later steps. |
| Step order is fixed, but real dependencies differ | The changelog depends on tests passing, but the Chain is just a flat list; dependencies are only implied by order. | If dependencies are complex, Chain is the wrong abstraction. Use Plan-Execute or Graph. |
| The same failure forces the workflow to start over | Step 3 fails, and the next run starts again from step 1. Chain has no concept of resuming from a failed step. | If the task takes time, consider Graph-style state persistence. |
| User intervention is expensive | A user wants to skip one step midway, but Chain cannot support that without manual interruption. | If interaction is common, at least add confirmation points between steps. That is no longer a pure Chain, but it is more practical. |

### 5.4.2 Router: Classify the Task Before Choosing the Execution Path

Chain's fixed road is useful when the steps are stable. But if the user changes the request from "prepare a release" to "help me fix a bug," the same four steps no longer make sense. The agent first needs to decide what kind of task it is handling, then choose the matching path. That is Router.

Router is essentially "classifier + multiple Chains." Different tasks follow different paths:

```python
class RouterExecutor:
    ROUTES = {
        "release": ["check_readme", "run_tests", "organize_changelog", "generate_checklist"],
        "bugfix":  ["run_tests", "organize_changelog"],
        "docs":    ["check_readme"],
    }

    def classify(self, query: str) -> str:
        # In a real project this would usually be an LLM call.
        # Here it is simplified to keyword matching.
        if "release" in query.lower():
            return "release"
        if "bug" in query.lower() or "fix" in query.lower():
            return "bugfix"
        if "docs" in query.lower() or "readme" in query.lower():
            return "docs"
        return "release"  # fallback

    def execute(self, query: str):
        category = self.classify(query)
        steps = self.ROUTES.get(category, self.ROUTES["release"])
        return ChainExecutor(steps).execute()
```

Router has three important design points:

- **Classification accuracy:** if routing is wrong, everything downstream is wrong. In production, do not look only at aggregate accuracy. Look at the cost of one bad route. A wrong FAQ answer may be tolerable; a wrong refund, release, or production operation may not be. High-risk routes need confirmation, refusal, or human handoff.
- **Fallback path:** classification failure needs a default behavior. The fallback should not be the "most complete" path. It should be the safest path: explain uncertainty, ask for more information, or perform read-only checks.
- **The selected path is still a Chain:** Router chooses the road. It does not solve what happens when the road has a hole. Inside each route, execution still stops on error unless you add another pattern.

Router usually fails not when it chooses the right path, but when it chooses the wrong one or has no appropriate path.

| Failure symptom | Typical cause | Fix |
|---|---|---|
| Wrong route executes the wrong workflow | The user says "check this code," and Router classifies it as `bugfix`, so it runs tests and writes a changelog, even though the user wanted code review. | Do not rely only on keyword matching. Use LLM few-shot intent classification and add route confirmation for ambiguous inputs. |
| The fallback becomes a catch-all trash bin | Unclear requests all fall into the default release path, so users are confused when "help me write docs" triggers release preparation. | Make fallback the safest path, not the fullest path. Monitor how often fallback is triggered. |
| Route definitions become stale | Last month's `bugfix` route had only "run tests + organize changelog," but the team now also requires a version bump. | Review route definitions against the real workflow and user feedback. |
| Routes duplicate shared steps | Both `release` and `bugfix` define "run tests" separately, so changing the test tool requires edits in multiple places. | Extract reusable step definitions and let routes reference step names. |

### 5.4.3 Plan-Execute: Make the Plan Visible, Then Replan After Failure

Router answers "which path should this task take," but the selected path is still usually a Chain. If tests fail during release preparation, should the whole task stop? If the failure is a known legacy test unrelated to the release, users may expect the agent to continue after recording the risk. What you need is not a fixed path, but the ability to adjust execution based on what happens: plan first, execute, and replan after failure.

This is the classic Planning implementation. The core flow has four steps:

```text
1. Generate a plan:
   analyze the goal → break it into structured steps
   (each step has a name, tool, description, dependencies, and retry count)
2. Ask for user approval:
   show the plan → let the user modify or confirm it
3. Execute step by step:
   follow dependency order → record each result
4. Replan on failure:
   when retries are exhausted → generate new remaining steps from current state
```

```python
class PlanExecuteExecutor:
    def execute(self, goal, inject_failures=None):
        # 1. Generate the plan
        plan = self.generate_plan(goal)
        # plan.steps = [
        #   PlanStep("check_readme", tool="check_readme", depends_on=[]),
        #   PlanStep("run_tests", tool="run_tests", depends_on=[]),
        #   PlanStep("organize_changelog", tool="organize_changelog",
        #            depends_on=["run_tests"]),
        #   PlanStep("generate_checklist", tool="generate_checklist",
        #            depends_on=["check_readme", "run_tests", "organize_changelog"]),
        # ]

        # 2. Execute step by step
        for step in plan.steps:
            unmet = [d for d in step.depends_on if d not in plan.completed_steps]
            if unmet:
                # Dependencies are not satisfied; insert or run dependency steps first.
                continue

            result = execute_step(step, inject_failures)

            # 3. Failure handling
            if result.status == "error":
                step.retries += 1
                if step.retries < step.max_retries:
                    continue  # retry
                else:
                    # Retries exhausted; trigger replanning.
                    new_steps = self.replan(goal, plan.completed_steps,
                                            step.name, result.error)
                    plan.replace_remaining(new_steps)

        return plan.final_output
```

**Replanning is the core difference between Plan-Execute and Chain.** Replanning means: given the completed steps, the failure reason, and the available tools, generate a new set of remaining steps. This is not planning from scratch. Completed steps should not be repeated.

```text
Replanning example: tests fail

Input:
  Completed: ["check_readme"]
  Failed step: "run_tests"
  Error: "1 test failed: test_memory_cleanup_on_session_end"

Replanning output:
  Step 3. Analyze the test failure — rerun the test to confirm the cause
  Step 4. Organize changelog — continue execution
  Step 5. Generate checklist — continue execution
```

**The common trap:** replanning itself can fail. If the new plan is also impossible to execute, the system needs an exit condition. A typical guardrail is a maximum replan count, such as two attempts. The runnable example in this chapter includes this protection: when `max_replan_count` is reached, or when replanning produces the same steps again, execution stops instead of looping forever.

Plan-Execute is the most flexible of the four main patterns, but flexibility brings its own failure modes.

| Failure symptom | Typical cause | Fix |
|---|---|---|
| Infinite replanning loop | `replan` treats every error the same. It does not distinguish recoverable errors, such as network timeout, from unrecoverable errors, such as "not a git repository." The new plan repeats the old one. | Classify errors: recoverable → retry; unrecoverable → skip with user notice or stop. Set `max_replan_count=2`. Detect whether the new steps are identical to previous attempts. |
| Plan is too vague to execute | The model produces steps like "make sure everything is fine" with no tool, acceptance criteria, input, or output. | Require every step to bind to a concrete tool and acceptance criteria. Reject steps without tool names. |
| Plan changes after user approval | During execution, the agent detects an environment issue and inserts extra steps without telling the user. | Treat confirmed plans as immutable. Any structural change, including inserted steps, must be approved again. |
| Planning is too slow | Complex planning calls the LLM many times and takes more than 30 seconds. | Set a planning timeout, such as 10 seconds. Show a rough plan first, confirm direction, then refine. |
| Dependencies are modeled incorrectly | The changelog claims to depend on tests, but execution starts it before tests complete. | The executor must check completed dependency state, not just whether a step name exists. |

### 5.4.4 Graph: Put Exception Paths Into the State Machine Up Front

Dynamic replanning is flexible, but it has a cost. Every failure may require another LLM call, which adds latency and uncertainty. If your release workflow runs every week and the failure modes are already stable, you do not need the model to rethink the response every time. You can draw the response as a map in advance. That is Graph.

Graph models the task as a directed graph. Unlike Plan-Execute's "linear list + dynamic replanning," **all possible paths in a Graph are defined when the workflow is built**.

```text
Release preparation graph:

              ┌─────────────┐
              │ check README│
              └──────┬──────┘
                     │ success         error
                     ▼                 ▼
              ┌─────────────┐    ┌────────────┐
              │  run tests  │    │ fix README │
              └──────┬──────┘    └─────┬──────┘
                     │                 │ success
              success│ error           ▼
                     ▼     ▼      (stop: human review)
              ┌───────────────┐
              │organize changelog│
              └──────┬────────┘
                     │ success/error → (stop)
                     ▼
              ┌───────────────┐
              │generate checklist│
              └──────┬────────┘
                     ▼
                  (done!)
```

```python
class WorkflowGraph:
    def __init__(self):
        self.nodes: dict[str, Node] = {}

    def add_node(self, name, action, on_success=None, on_error=None,
                 max_retries=1):
        self.nodes[name] = Node(name, action, on_success, on_error, max_retries)

    def run(self, entry, context):
        current = entry
        while current:
            node = self.nodes[current]
            result = node.action(context)

            if result.status == "error":
                node.retry_count += 1
                if node.retry_count < node.max_retries:
                    current = current  # retry the same node
                else:
                    current = node.on_error  # follow failure edge
            else:
                current = node.on_success  # follow success edge
```

Graph's real strength is failure handling. On the happy path, it runs `check_readme → run_tests → changelog → checklist`, which looks much like Chain. The difference appears when a node fails:

```text
Graph error handling: README check fails

  check_readme → failure → on_error jump → fix_readme
  Path: check_readme → fix_readme → stop

  Chain cannot do this. Its steps are ["check README", "run tests", ...],
  so it can only stop at the first step.

  Plan-Execute can also generate a "fix README" step through replanning,
  but that is generated at runtime.
  In Graph, the repair path is predefined:
  more predictable, but more dependent on up-front design and testing.
```

**The modeling cost of Graph:** you must decide every node's target under every relevant condition. For a 4-step release task, the graph may need 6 nodes when error handling nodes are included. For a more complex ticket workflow, the graph may grow to dozens of nodes. At that point, maintenance cost becomes significant.

Graph's power comes from predefined branches, and its failures come from the same source: it can only handle exceptions you thought about in advance.

| Failure symptom | Typical cause | Fix |
|---|---|---|
| Error branch was never tested | The happy path almost never fails, so an error branch sits untouched for three months. The first real trigger crashes because it writes to a missing directory. | Inject failures regularly to force error branches to run. Unit-test every error branch. |
| Unexpected exception has no path | The graph has branches for "test failure" and "README missing," but nothing for "disk full." | Add an `on_unexpected` fallback node. The default behavior should pause and notify the user, not fail silently. |
| Graph becomes impossible to maintain | A graph starts with 6 nodes and grows into 30 nodes and 50 edges. No one can explain the whole workflow. | Encapsulate subgraphs, such as all test-related nodes. Review dead nodes; remove nodes unused for months. |
| Missing state persistence prevents recovery | The process crashes at step 3. After restart, the system does not know the current node or intermediate results. | Persist state after every node: current node, completed steps, intermediate output, and errors. Support resume from the failed node. |
| Over-engineering | A three-line script, "read config -> print output," becomes a 5-node graph. | Use the decision tree in 5.4.5. If steps are fixed and have no exception branches, Chain is enough. |

### 5.4.5 The Happy Path Looks Similar; Failure Reveals the Difference

Now that the four main patterns have been introduced, compare them by running the same release task twice: once where everything works, and once where tests fail.

```text
═══════════════════════════════════════════════════════════════════
Task: "Prepare the v1.2.0 release" (all steps succeed)
═══════════════════════════════════════════════════════════════════

Chain:           ✅ 4/4 complete.
                 Path: check README → run tests → changelog → checklist
Router(release): ✅ 4/4 complete. Same path.
Plan-Execute:    ✅ 4/4 complete. Shows plan first, then executes after approval.
Graph:           ✅ 4 nodes. Path: check_readme → run_tests → changelog → checklist

All patterns complete the task. The difference is not visible yet.

═══════════════════════════════════════════════════════════════════
Task: "Prepare the v1.2.0 release" (tests fail)
═══════════════════════════════════════════════════════════════════

Chain:           ❌ Step 1 completes, step 2 fails, steps 3-4 are skipped.
                 Final output: "Release preparation failed."

Plan-Execute:    ⚠️ Step 1 completes, step 2 fails → retry once → still fails
                 → trigger replanning → insert "analyze failure cause"
                 → classify as non-blocking after user confirmation
                 → continue changelog and checklist.
                 Final output: "Release preparation complete
                 (test failure recorded, fix pending)."

Graph:           ✅ check_readme✓ → run_tests✗ → retry → still fails
                 → on_error jump → retry_tests✓ → changelog✓ → checklist✓
                 Final output: "Release preparation complete."

The same exception leads to different behavior:
- Chain gives up.
- Plan-Execute dynamically creates a recovery strategy.
- Graph follows a predefined failure recovery path.
```

**Pattern selection decision tree:**

```text
Are the task steps fully fixed?
  ├─ Yes → Do failures require branch handling?
  │      ├─ No → Chain
  │      └─ Yes → Can the exception paths be enumerated up front?
  │             ├─ Yes → Graph
  │             └─ No → Plan-Execute
  └─ No → Do you need different paths for different input types?
         ├─ Yes → Router
         └─ No → Plan-Execute or ReAct Loop
```

> **Remember:** do not force a simple task into a Graph. The problem with Graph is not that it is too powerful. The problem is that you must maintain nodes, edges, state, error branches, recovery rules, and tests. If the task is a three-step fixed workflow, those costs do not automatically produce value.

### 5.4.6 Beyond the Four Patterns: Parallelization, Orchestrator-Workers, and Evaluator-Optimizer

The four patterns above are enough to explain the release assistant, but real systems often need three additional variants. They are not necessarily more advanced than Chain, Router, Plan-Execute, or Graph. They solve different problems.

| Pattern | Problem solved | Example in the release assistant | Boundary |
|---|---|---|---|
| Parallelization | Independent subtasks can run at the same time | README check, dependency vulnerability scan, and formatting check can run in parallel before results are merged | Use only when subtasks have no write conflicts, little shared state, and independently explainable failures. |
| Orchestrator-Workers | The number and type of subtasks are unknown before execution | During documentation migration, the orchestrator scans files first, then assigns different files to workers | Good for open-ended tasks. Higher cost; worker outputs must share a format, and the orchestrator must merge conflicts. |
| Evaluator-Optimizer | Output quality must be checked and improved repeatedly | After generating the release checklist, an evaluator checks whether it covers version number, rollback plan, and permissions; an optimizer revises it | Good when quality can be judged. If the evaluation criteria are vague, it may become a meaningless loop. |

In the release assistant, they look like this:

```text
User: "Help me prepare the v1.2.0 release."

Parallelization:
  Run README check, tests, and dependency vulnerability scan at the same time.
  After all read-only checks finish, decide whether to generate the changelog.

Orchestrator-Workers:
  The orchestrator finds Python, Node.js, and Docker release materials.
  It assigns each category to a separate worker, then merges results into one checklist.

Evaluator-Optimizer:
  Generate the checklist first.
  The evaluator checks whether it covers tests, version number, docs, rollback, and permissions.
  If anything is missing, the optimizer revises the checklist, up to 2 iterations.
```

These variants are often combined with the earlier patterns. Router can classify the task first and then enter Parallelization. Plan-Execute can expand one step into Orchestrator-Workers. Graph can turn Evaluator-Optimizer into a fixed subgraph. The rule is still the same: use traces and evals to prove that a simpler pattern is insufficient before adding complexity.

## 5.5 Do Not Start by Drawing a Graph: Let Failures and Evals Drive the Upgrade

Planning / Workflow Patterns can evolve in stages:

| Stage | What it does | Good target | What not to do too early |
|---|---|---|---|
| V0: Raw ReAct | The model chooses tools step by step | Explore whether the task really needs multiple steps | Do not introduce a Planning framework before raw ReAct has proven insufficient. |
| V1: Checklist | The model lists steps first, but execution is not enforced | Reduce missed steps; test whether a stable step pattern exists | Do not require a structured plan too early. First confirm that a checklist helps. |
| V2: User-approved plan | The user can edit and approve the plan before execution | Improve control and involve the user in decisions | Do not automate too early. If users cannot state the steps yet, keep it manual. |
| V3: Structured plan | Each step binds goal, tool, input, and acceptance criteria | Make execution traceable and failures diagnosable | Do not chase formal completeness. If 5 steps are enough, do not generate 15. |
| V4: Dynamic replanning | Adjust the plan after failure or environment changes | Support adaptive execution for complex tasks | Do not trust replanning before error classification and exit conditions are validated. |
| V5: Graph | Freeze tasks, states, and branches into a graph | Support persistence, recovery, and replay | Do not freeze into Graph too early. Wait until the process has been stable for at least a month. |

**Upgrade signals should be concrete and observable**, not vague wishes that "the system should be better":

- V0→V1: users say "you missed a step again" or "you should check X before Y." The task has a stable pattern, so a checklist is useful.
- V1→V2: users frequently interrupt execution with "no, don't do that yet." They want to participate in the decision.
- V2→V3: the same task has been run more than five times, and users repeatedly ask questions such as "what is the acceptance criterion for this step?" The plan needs structure.
- V3→V4: you have seen a failure where the agent either blindly continued or gave up entirely. Replanning is needed.
- V4→V5: the task runs at least weekly, and new team members need to execute or inspect it. Graph's replay and recovery value can now pay off.

For early learning, V2 or V3 is usually enough. Bring in Graph only when state and branches are genuinely complex. Its cost is not an abstract "complexity." You must maintain node definitions, edge conditions, state persistence, recovery strategy, error branch tests, and debugging tools.

**Do not upgrade based on taste. Use evals.** Prepare real tasks and failure-injected tasks, run multiple patterns, then compare results:

| Eval item | What to record | Why it matters |
|---|---|---|
| Task completion rate | Whether the final user goal was achieved | Prevent complex patterns from only looking more complete. |
| Missed critical steps | Whether README, tests, changelog, checklist, and other required steps were missed | Verify that Planning actually reduces omissions. |
| Failure recovery rate | Whether injected test failures, missing files, and permission errors were handled correctly | Planning's value mainly appears on exception paths. |
| User confirmation count | How many confirmations are needed before and during execution | Too few confirmations reduce control; too many interrupt flow. |
| Average time and cost | LLM calls, tool time, and total latency | Plan-Execute and Graph must earn back their cost. |
| Plan deviation count | Whether execution inserted, deleted, or skipped confirmed steps | Verify that "locked after approval" actually works. |
| Replayability | Whether the trace shows each step's input, output, state, and errors | Determines whether the system can be debugged, audited, and handed off. |

A simple comparison template:

```text
Task set: 10 release-preparation tasks, 3 with injected failures

Pattern           Completion  Recovery  Avg time  Confirmations  Deviations  Upgrade?
Chain             70%         20%       low       0              0           No: weak exception paths
Plan-Execute      90%         80%       medium    1.4            0           Yes: benefit covers cost
Graph             92%         90%       medium    1.1            0           Wait: modeling cost is high; workflow not stable yet
```

**Production-grade Planning should at least record the following fields.** Without them, a plan may look clear, but the system cannot recover, audit, or debug it.

| Field | Meaning |
|---|---|
| `goal` | Original user goal; prevents goal drift during execution |
| `plan_version` | Plan version; every structural change creates a new version |
| `steps` | Name, tool, input, output, dependency, and acceptance criteria for each step |
| `state` | `pending` / `running` / `completed` / `failed` / `skipped` |
| `approval` | Who approved which plan version, and what scope was approved |
| `risk_level` | `read_only` / `modifies_files` / `external_side_effect` / `irreversible` |
| `requires_approval` | Whether human approval is required before execution, especially for writing files, committing, publishing, deleting, payments, and other side effects |
| `trace` | Tool calls, duration, errors, retry count, and observations for each step |
| `recovery` | Rules for retry, skip, replan, human handoff, or stop after failure |

**Decision order for designing Planning, using the release assistant as an example:**

1. **Confirm whether the task needs Planning at all.** Use the criteria in 5.7. If the task can be done in one step, or two to three fixed steps are enough, stop here. Run raw ReAct five times and observe whether it misses steps, drifts, or fails to recover.
2. **Observe the task's natural shape.** Are the steps fixed or input-dependent? After failure, should the agent retry, skip, or replan? Does the user need to participate? These observations determine the pattern.
3. **Start with the simplest pattern.** Use Chain if steps are fixed and have no exception branches. Use Router if input type determines the path. Upgrade to Plan-Execute or Graph only when you see failures that Chain or Router cannot handle. The only good reason to upgrade is a concrete failure, not that another pattern sounds more advanced.
4. **Define exit conditions for every pattern.** When should Chain stop? How many times may Plan-Execute replan? Where should Graph route unexpected exceptions? Planning without exit conditions is just an agent stuck in a loop.
5. **Treat error paths as seriously as the main path.** A Graph branch that was written and forgotten will fail at the worst possible time. Inject failures regularly and test each error branch separately.
6. **Lock the plan after confirmation.** If the user approved a 4-step plan, the agent must not execute 5 steps. Any structural deviation, whether inserting or skipping a step, requires approval. Distinguish small adjustments, such as retry delay, from structural changes, such as adding or deleting steps.
7. **Compare patterns with real tasks.** Prepare three tasks: one fully successful, one with a middle-step failure, and one that requires replanning. Run different patterns and compare completion rate, recovery rate, user intervention count, final output quality, cost, and trace readability.

## 5.6 Planning Usually Fails on Exception Paths

### 5.6.1 Quick Reference: Common Planning Failure Modes

| Failure mode | Symptom | Possible cause | Fix direction |
|---|---|---|---|
| Plan is not executable | Steps sound reasonable but cannot be carried out | Tools and environment constraints are missing | Bind tools and acceptance criteria in the plan |
| Plan is too granular | Many meaningless steps are generated | Chasing formal completeness | Limit step count and granularity |
| Execution drifts away from plan | The agent forgets the original plan during execution | State does not record the current step | Update state after every step |
| No replanning | The agent keeps going after a tool fails | No failure branch | Add replanning triggers |
| Over-engineering | Small tasks use Graph | Technology-driven design | Start from Chain / Router |
| User rejects the plan | The plan does not match the real user goal | Missing approval point | Ask the user to approve before execution |

### 5.6.2 Three Debugging Stories: Infinite Replanning, Untested Branches, and Unauthorized Plan Changes

The table above tells you what the problem might be. In real debugging, symptoms and root causes are often several layers apart. The following three release-assistant stories show how to move from symptom to root cause to fix.

---

**Debugging story 1: Plan-Execute falls into an infinite replanning loop**

```text
Symptom:
The user says, "Help me prepare the release."
The agent generates a plan and reaches "organize changelog."
That step fails with: GitError: not a git repository.
Replanning creates a new plan that again contains "organize changelog."
It fails again, replans again, and repeats.
After 3 minutes, the agent is still looping.

Investigation:
1. Inspect the trace → the changelog step failed 8 times and replanned 6 times.
2. Each replan generated the same steps: "organize changelog" + "generate checklist."
3. The error stayed the same: "GitError: not a git repository."
   This is an environment problem; retrying cannot fix it.
4. The replanning logic did not classify whether the failure was recoverable.

Root cause:
- replan() only looked at the failed step name, not the failure type.
- GitError is an unrecoverable environment problem, but it was treated as retryable.
- There was no maximum replan count.

Fix:
1. Classify errors:
   recoverable errors (network timeout, temporarily unavailable resource) → retry;
   unrecoverable errors (configuration error, environment issue, permission denial)
   → skip with user notice or stop.
2. Add max_replan_count=2.
3. During replanning, check whether the new steps match the previous steps.
   If they match, replanning produced no useful alternative and should stop.
```

---

**Debugging story 2: A Graph error branch was never tested**

```text
Symptom:
The "fix README" node is triggered in production for the first time.
After 30 seconds, it crashes because it tries to write to a missing directory.
The node has existed in the graph for 3 months.

Investigation:
1. Inspect the Graph definition → the fix_readme node action is a temporary lambda.
2. The node was never triggered in the normal flow because README checks almost never fail.
3. Development only tested the happy path.
   The error branch existed in code, but never ran in integration tests.

Root cause:
- Graph failure branches were defined during construction, but testing focused on the main path.
- The error branch was "write and forget" code: no monitoring, no alerting.
- These nodes are rarely visited, but when they are visited it is usually urgent.

Fix:
1. Add failure injection:
   regularly inject errors into the Graph to force every error branch to run
   (for example, run a weekly chaos test that makes README check fail).
2. Give error-branch nodes complete logging and monitoring.
3. Unit-test every error-branch node separately.
```

---

**Debugging story 3: The agent changes the plan after user approval**

```text
Symptom:
The user approves a 4-step release plan.
At step 3, "organize changelog," the agent detects uncommitted changes
in git log and inserts a new step:
"commit unsaved changes first."
The changelog now includes changes that should not be part of the release.

Investigation:
1. Inspect the trace → before step 3, the agent detected a dirty working tree.
2. PlanExecuteExecutor.execute() contains logic:
   "if an environment issue is detected, automatically insert a repair step."
3. The user approved a 4-step plan, but execution ran 5 steps.
   The user never saw or approved the extra step.

Root cause:
- The plan was not locked after approval.
  The executor treated the approved plan as a reference template, not a snapshot.
- The "auto-insert step" behavior had too much authority.
  It should not modify an approved plan without asking.

Fix:
1. Lock the confirmed plan. confirmed_plan is immutable.
   Any deviation must request user approval again.
2. If execution discovers that an extra step is needed, pause and notify the user:
   "I found an environment issue: the working tree has uncommitted changes.
   I recommend committing before continuing. May I insert this step?"
3. Separate small adjustments from structural changes:
   retry delay can be automatic;
   inserted or deleted steps require approval.
```

---

The three stories share the same lessons:

- **Replanning is not a silver bullet.** It needs error classification and exit conditions.
- **Error paths deserve the same attention as the happy path.** A forgotten Graph branch will fail at the worst moment.
- **Once a plan is confirmed, it should be locked.** If the user approved 4 steps, execution must not silently become 5 steps.

## 5.7 Not Every Multi-Step Task Deserves Planning

The following situations do not need complex Planning:

- The task can be completed in one step.
- A fixed two- or three-step process is already enough.
- The user wants a fast result more than a visible plan.
- The plan cannot be verified and is only intermediate text.
- A deterministic business workflow already handles the task well.
- Planning clearly increases cost and latency without improving quality.
- You have no trace or eval data proving that Planning reduces missed steps, failures, or rework.

Practical rule:

```text
If the main problem is "missed steps, drift, or inability to recover," consider Planning.
If the problem is "one tool call failed," fix the tool mechanism first.
```

## 5.8 From Drift to Replayability: A Planning Lifecycle

Now connect the key differences across patterns through one continuous story. This is the release assistant evolving from a beginner tool into a reliable workflow over three versions.

```text
═══════════════════════════════════════════════════════════════════
V1: Raw ReAct — Monday 14:00
═══════════════════════════════════════════════════════════════════
│
│  [14:00] User: "Help me prepare the v1.2.0 release."
│
│  Agent's ReAct loop:
│    Thought: The user wants release preparation. First inspect the project.
│    Action: ls -la
│    Observation: README.md, src/, tests/, CHANGELOG.md
│
│    Thought: There is a CHANGELOG.md. Let me read it.
│    Action: cat CHANGELOG.md
│    Observation: 200 lines of changelog history
│
│    Thought: The changelog was last updated 3 months ago.
│             Let me inspect recent git commits.
│    Action: git log --oneline -20
│    Observation: 20 commits
│
│    Thought: Recent commits include feat and fix.
│             I should organize them into the changelog.
│    Action: starts editing CHANGELOG.md...
│
│    Thought: I should also check tests.
│    Action: npm test
│    Observation: 42 passed, 0 failed
│
│    Thought: Tests passed. The user also mentioned README...
│    Action: cat README.md
│    (8 minutes have passed; the user is already impatient.)
│
│  Problem:
│    The agent drifted from the first step.
│    It did not first understand what "release preparation" requires.
│    Instead, it made local decisions, got attracted by changelog details,
│    spent too much time editing, and only later remembered README and checklist.
│    The user wanted a checklist; the agent started modifying files.
│
│  User feedback:
│    "I only wanted a checklist. Why did you start editing the changelog?
│     Also, the changelog includes unfinished commits."
│
═══════════════════════════════════════════════════════════════════
V2: Plan-Execute — Tuesday 10:00
═══════════════════════════════════════════════════════════════════
│
│  [10:00] User: "Help me prepare the v1.2.0 release."
│
│  1. Generate plan:
│     The agent no longer acts immediately. It first produces a plan:
│
│     ┌─────────────────────────────────────────────────────────┐
│     │ Release preparation plan - v1.2.0                       │
│     │                                                         │
│     │ Step 1. Check README completeness                       │
│     │   Tool: file read + section validation                  │
│     │   Acceptance: Installation, Quick Start, API,           │
│     │               and Contributing sections all exist       │
│     │                                                         │
│     │ Step 2. Run tests                                       │
│     │   Tool: npm test                                        │
│     │   Acceptance: all tests pass                            │
│     │                                                         │
│     │ Step 3. Organize changelog                              │
│     │   Tool: git log + changelog template                    │
│     │   Dependency: step 2 passes                             │
│     │   Acceptance: changelog covers all release commits      │
│     │                                                         │
│     │ Step 4. Generate release checklist                      │
│     │   Tool: checklist template                              │
│     │   Dependency: steps 1, 2, and 3 complete                │
│     │   Acceptance: checklist covers all release checks       │
│     └─────────────────────────────────────────────────────────┘
│
│  [10:01] User confirms:
│    "The plan looks good. Execute it.
│     But if tests fail, don't just stop.
│     Tell me which test failed and I'll decide whether to continue."
│
│  2. Execute:
│     Step 1 ✅ — README lacks Contributing, but this is non-blocking
│     Step 2 ❌ — 1 test failed: test_memory_cleanup
│
│     Retry step 2 — still failing.
│
│     Following the user's instruction, the agent does not stop blindly:
│     "Step 2 run tests: 1 test failed
│      (test_memory_cleanup_on_session_end).
│      This failure appears unrelated to this release.
│      Should I skip it and continue?"
│
│     User: "Skip it and continue."
│
│     Step 3 ✅ — changelog generated, covering 5 commits
│     Step 4 ✅ — checklist generated
│
│  3. Final output:
│     ✅ Release preparation complete
│     ⚠️ Tests: 1 known failure, recorded as non-blocking
│     📋 Checklist contains 7 items
│
│  User feedback:
│    "This is much better. The plan is clear, and I get a choice when something fails."
│
═══════════════════════════════════════════════════════════════════
V3: Graph — Wednesday 15:00
═══════════════════════════════════════════════════════════════════
│
│  After a week of stable operation, the team freezes the release flow as a Graph.
│
│  Reasons:
│  - The release process runs at least once a week, and the branches are stable.
│  - It needs execution recovery: if the process fails midway,
│    production should resume from the failed node.
│  - It needs replayability: a new maintainer can replay the previous release path.
│
│  [15:00] New maintainer: "Help me prepare the v1.3.0 release."
│
│  Graph execution path, with every step recorded:
│    check_readme   ✅ → "README complete"
│    run_tests      ✅ → "42/42 passed"
│    changelog      ✅ → "Changelog generated"
│    checklist      ✅ → "7/7 checks"
│
│  Path: check_readme → run_tests → changelog → checklist
│
│  [15:30] Second release, README has a problem:
│    check_readme   ❌ → FileNotFoundError
│    fix_readme     ✅ → "README supplemented"
│    (stop and wait for human review)
│
│  Path: check_readme → fix_readme
│
│  User feedback:
│    "I no longer need to say what to do on failure every time.
│     The branch logic is in the Graph, and the path is auditable."
│
│  Cost:
│    Building this Graph took an afternoon.
│    The team had to define 6 nodes, 8 edges, and 3 retry policies.
│    Chain and Plan-Execute did not require that up-front work.
│
═══════════════════════════════════════════════════════════════════
```

Several key behaviors are visible in the replay:

1. **Raw ReAct is not Planning.** It has no global task view and can be pulled off course by local information. In V1, the agent was attracted by the changelog and drifted away from the checklist goal.
2. **Plan-Execute's core value is "visible plan + failure decision points."** The user sees the steps first and can decide what to do when a step fails. Chain cannot offer that choice.
3. **Graph's value is fixed reliability.** Happy paths and exception paths are predefined, so execution is predictable and replayable. But the modeling cost is real; the release Graph took an afternoon and should not be the default for every task.
4. **The iteration order matters.** Start with raw ReAct to verify feasibility, add Plan-Execute to improve reliability, and only freeze into Graph after the workflow stabilizes. If you skip the middle stages, you may discover untested error branches only when they fail in production.

**Core decision review for the four patterns:**

| Pattern | Core decision | What it looks like when wrong |
|---|---|---|
| Chain (5.4.1) | Are steps fully fixed with no exception branches? | A non-critical failure stops the whole workflow; users cannot skip a step. |
| Router (5.4.2) | Is classification accurate enough, and is fallback safe? | Wrong route executes the wrong workflow; fallback becomes a catch-all path. |
| Plan-Execute (5.4.3) | Are replanning exit conditions reliable, and is the confirmed plan locked? | Infinite replanning; the agent inserts steps after approval. |
| Graph (5.4.4) | Is the modeling cost justified, and are error branches tested like the main path? | No one can explain the 30-node graph; an error branch crashes the first time it is triggered. |

**Three themes run through the whole chapter:**

1. **Pattern choice is driven by the scenario, not by sophistication.** Chain is not "low-level," and Graph is not "advanced." If the steps are fixed and surprises are unlikely, Chain is optimal: simple, predictable, and cheap to maintain. Complex patterns are justified only when traces and evals show that they reduce missed steps, improve recovery, or support handoff and audit.
2. **Exception paths deserve the same attention as the happy path.** Most Planning failures do not happen on the normal flow; all four patterns can complete the normal flow. Failures happen when something goes wrong: Chain gives up, Plan-Execute loops while replanning, Graph enters an untested branch. When evaluating Planning, do not only ask whether the workflow finishes when everything works. Ask what happens when it fails.
3. **Once a plan is confirmed, deviations require confirmation.** Planning earns trust because the user approved the plan. If the user approved 4 steps, the agent must not execute 5, even for a "helpful" reason such as fixing an environment issue. Any inserted, removed, or skipped step needs user awareness and approval.

Return to the opening problem: an agent begins to drift on a multi-step task. In the release assistant example, the user gave a 4-step release task, but raw ReAct dove into changelog details at the first opportunity and lost the original goal. Planning is not about making the agent "smarter at choosing the next step." Planning is about **building a global task structure before execution**: what the steps are, how they depend on each other, and what should happen after failure. The more fixed the structure is, the more predictable but less flexible it becomes. The more dynamic the structure is, the more flexible it becomes, but the more it needs exit conditions.

> **The story is not over.** Planning gives the agent a global task view, so release preparation no longer misses steps. But a new problem appears: the agent reaches "run tests," sees a clear `TypeError` in the logs, and still keeps writing the changelog without deciding whether to retry, handle, degrade, or stop. It lacks a closed loop of "feedback → classification → decision → handling or stop." That is the topic of the next chapter: Reflection.

---

### Chapter Recap

Planning is not about making an agent "smarter at choosing the next step." It is about building a global task structure before execution: what the steps are, how they depend on each other, and what should happen after failure. Three ideas matter most:

**Choose patterns by scenario, not by sophistication.** Chain is not primitive, and Graph is not automatically better. If a task has fixed steps and no meaningful exception branches, Chain is the best choice: simple, predictable, and cheap. Use the decision tree in 5.4.5: fixed steps and no exception branches → Chain; input-based paths → Router; enumerable exception paths → Graph; otherwise → Plan-Execute. Before upgrading, use traces and evals to prove that extra complexity improves completion rate, recovery rate, or replayability.

**Treat exception paths as seriously as the happy path.** Most Planning failures appear when something goes wrong: Chain gives up, Plan-Execute enters an infinite replan loop, and Graph reaches a branch that was never tested. Do not only evaluate whether the workflow finishes under normal conditions. Evaluate how it handles failures. Inject failures regularly and test each error branch separately.

**Lock the plan after confirmation.** If the user approved a 4-step plan, the agent must not execute 5 steps, regardless of intent. Any deviation, including inserted, deleted, or skipped steps, requires renewed confirmation. Small adjustments such as retry delay can be automatic; structural changes require approval.

---

## Runnable Example

After finishing this chapter, run the local Course 5 05-05 Planning example:

- [Course 5 05-05 Planning / Workflow Patterns Example](../examples/course-05-05-planning/README.md)

The example uses the release assistant scenario and provides both Python and Node.js versions. It demonstrates four Planning patterns: Chain (fixed order), Router (classification-based routing), Plan-Execute (plan → execute → replan), and Graph (node graph + conditional edges + state machine). It includes an interactive REPL where you can switch patterns, run the same task, inject failures, observe replanning behavior, and compare how the four patterns handle the same exception.

The example is a teaching implementation, not a complete production framework. It uses Enter key presses to simulate user approval. Graph records a replayable path but does not implement durable recovery. Plan-Execute includes a maximum replan count and repeated-replan detection so the failure path does not loop forever.

```bash
# Python version
cd examples/course-05-05-planning/python
python3 planning_demo.py

# Node.js version
cd examples/course-05-05-planning/nodejs
node planning_demo.mjs
```

> **Review of the last four chapters.** You now have four ways to look at agents: Scenario Enhancement (Chapter 1) defines the extra capabilities an agent needs in multi-turn interaction; RAG (Chapter 2) solves "the model does not know, so it should retrieve"; Memory (Chapter 3) solves cross-session state continuity; Planning (this chapter) solves the organization and execution of multi-step tasks. But one major problem remains: when an agent sees feedback, it may still continue down the same path instead of stopping to decide what to do next. That is the question Reflection answers in the next chapter.

---
