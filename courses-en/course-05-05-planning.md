# Chapter 5: Planning / Workflow Pattersons

[Return Course Five Document](./course-05-01-scenario-enhancement.md) | [Previous Chapter](./course-05-04-context-engineering.md) | [Next chapter](./course-05-06-reflection.md)

## Table of contents of this chapter

- [5.1 Agent starts drifting after a longer mission](#51-agent-starts-drifting-after-a-longer-mission)
- [5.2 Why is it only react not enough: from the incipient to the visible process?](#52-why-is-it-only-react-not-enough-from-the-incipient-to-the-visible-process)
- [5.3 Mission organization is more important than one-step decision-making](#53-mission-organization-is-more-important-than-one-step-decision-making)
- [5.4 Choose how to organize and then talk about Agent capabilities](#54-choose-how-to-organize-and-then-talk-about-agent-capabilities)
  - [5.4.1 Chain: Fixed sequence change for certainty at the expense of resilience](#541-chain-fixed-sequence-change-for-certainty-at-the-expense-of-resilience)
  - [5.4.2 Router: Disaggregat the task type before choosing the execution path](#542-router-disaggregat-the-task-type-before-choosing-the-execution-path)
  - [5.4.3 Plan-Execute: Make the plan visible before allowing failure and re-planning](#543-plan-execute-make-the-plan-visible-before-allowing-failure-and-re-planning)
  - [5.4.4 Graph: Advance drawing of abnormal paths into the status machine](#544-graph-advance-drawing-of-abnormal-paths-into-the-status-machine)
  - [5.4.5 Normal paths run and patterns differ when failure](#545-normal-paths-run-and-patterns-differ-when-failure)
  - [5.4.6 Not only four models: parallel, organization of workers, assessment of optimization of borders](#546-not-only-four-models-parallel-organization-of-workers-assessment-of-optimization-of-borders)
- [5.5 Don't just come up and draw a picture: Upgrade with failure and evaluation.](#55-dont-just-come-up-and-draw-a-picture-upgrade-with-failure-and-evaluation)
- [5.6 Planning failure usually dies in an abnormal path Let's go.](#56-planning-failure-usually-dies-in-an-abnormal-path-lets-go)
  - [5.6.1 Location at first glance: Planning Failed Mode Quick Checklist](#561-location-at-first-glance-planning-failed-mode-quick-checklist)
  - [5.6.2 Three failure stories: dead cycle, undetected branches, bad plans](#562-three-failure-stories-dead-cycle-undetected-branches-bad-plans)
- [5.7 Not every multistep is worth Planning.](#57-not-every-multistep-is-worth-planning)
- [5.8 From drift to removable: One Planning Life Cycle](#58-from-drift-to-removable-one-planning-life-cycle)
- [Runable Example](#runable-example)

---

## 5.1 Agent starts drifting after a longer mission

Return to 1.1 intellectual assistants. You gave it a multistep mission:

```text
帮我做发布准备：检查 README 完整性、跑一遍测试、整理 changelog、生成 release checklist。
```

Agent started work. The first step, it read the README, wrote a comment. Step two, it... started going over the source code to verify one of the details mentioned in the README. In the third step, it searched the relevant GitHub issue. Five minutes later you come back and check it out and find it detached from the original target, and you don't know what you're doing. You flipped the trace and found out that it had never touched anything about "publishing" since step 4.

The reason is: **Naked Rect Cycle does not have the concept of "global mission structure".** It is doing local best decision-making at every step, but local best sum may not reach the target. Like a driver without navigation, every intersection chooses the direction that looks right, but it may never reach its destination.

The longer the task, the more a mechanism is needed to answer:

- What steps are to be taken? What is the dependency between steps?
- What steps can be implemented in parallel?
- What steps are required for user confirmation before implementation?
- When a step fails, is it retrying, skipping, reprogramming or stopping?

This is the core issue that Planning/Workflow Pattersons is going to solve. **In this chapter, we will present specific presentations using a chapter-wide "publishing assistant" scene.** This scenario is defined as follows:

```text
场景：发布助手 Agent

用户：一位维护着开源项目的开发者
典型任务：软件版本发布准备（检查 README、运行测试、整理 changelog、生成 checklist）
复杂度：4 个步骤，步骤间存在依赖关系（changelog 必须在测试通过后生成，
        checklist 依赖所有前置步骤完成）
挑战：
  - 步骤不是完全独立的——有先后依赖
  - 测试可能失败——需要决定重试还是跳过
  - README 可能缺少必要章节——需要决定是否阻塞发布
  - 初次使用者可能说不清楚所有步骤——需要 Agent 自己补全

Planning 需求：
  - 步骤之间的依赖关系需要被明确建模
  - 某一步失败后需要明确的处理策略
  - 执行前用户可能需要确认计划
```

And every Planning model that follows, we're going to use this scenario -- the same mission, different organizational approaches, completely different effects.

## 5.2 Why is it only react not enough: from the incipient to the visible process?

Planning was not in the beginning of the Agent field. Retrospect the evolution: **October 2022, rect paper (Yao et al.).** The core finding of the paper is that allowing LLM to rotate between "debate" and "action" can significantly increase the completion rate of complex missions. But the React model is "every step of the way" -- the model sees the current operation and decides the next action. This is effective for a three-to-five-step mission, but more than one step exposes the problem: the model does not have a global vision and can easily drift. **At the beginning of 2023, the Plan-and-Execute model emerged.** The idea is straightforward: to have the model break down the entire mission into an implementation plan before it is progressively implemented after user confirmation. This solves the Rect's "no global view" problem, but introduces a new problem... - The plan may not be implemented (the steps outlined in the model cannot be completed in the physical environment) or the original plan will no longer be applicable after the environmental changes. **In the second half of 2023, the structure (Graph) was created.** Frames like LangGraph and CrewAI begin to model tasks into nodes and edges - Each node is an action or judgement, and the border representation status is moved, and if it fails, it can jump back to a particular node and try again. The chart structure is not the only direction in which Plan-and-Execute evolves, but expands the one-dimensional step list to a visible control stream: it can express branches, tracers, parallel paths, artificial confirmation points, or can carry models such as React, Router or Plan-Execute.**2024 to date, the WorldFlow Pattersons became a consensus.** The "Building Employment Acts" article in Anthropic summarizes Prompt Chaining, Routing, Parallelization, Orchestra-Workers, Evaluator-Optimizer, OpenAgents SDK puts handoff, guardrail, Tracing, evals in the basic toolbox of Agent; LangGraph emphasizes durable expertise, human-in-the-loop, personal and time travel. Together, they point to the same principle: most scenes do not need to be complex at the outset. Graph, the key is to choose the least adequate organization based on the mission pattern, and to test whether complexity actually brings benefits by using a track and eval.

## 5.3 Mission organization is more important than one-step decision-making

Rect Loop is good at dynamic decision-making, but not at natural assurance global structures.

Complex tasks usually take several forms:

| Task Form | Examples | Fit Mode |
|---|---|---|
| Step Fixed | Read File - > Summary - > Output | Chain |
| Significant differences in type of input | Questions and answers, writing, code review, different paths | Router |
| Submissions are independent of each other. | Check also README, test, rely on loopholes | Parallelization |
| The number of sub-tasks is uncertain. | Code migration, cross-document reconstruction, competition research | Orchestrator-Workers |
| The output needs to be sharpened. | Document optimization, code restoration, planned quality review | Evaluator-Optimizer |
| Tool selection dynamics | We need to check and decide on the next step. | ReAct Loop |
| The mission can be dismantled. | Release preparation, research reports, code migration | Plan-Execute |
| State and branch complex | Worksheet processing, approval stream, multi-stage tasks | Graph |

But looking at the tables alone is not intuitive. We use the release of the assistant scene for a different pattern of the same mission:

```text
任务："准备 v1.2.0 版本发布"

┌─────────────────────────────────────────────────────────────────────────┐
│ Chain 模式处理：                                                         │
│   检查 README → 运行测试 → 整理 changelog → 生成 checklist               │
│   遇错即停。测试失败 → 后面全跳过。                                      │
│                                                                         │
│ Plan-Execute 模式处理：                                                   │
│   1. 生成计划（同上 4 步）                                               │
│   2. 用户确认                                                            │
│   3. 逐步执行。测试失败 → 重试 2 次 → 仍失败 → 重规划                    │
│      "测试失败原因是 test_memory_cleanup 断言错误，                      │
│       新的后续步骤：分析失败原因 → 修复 → 重新测试 → 继续"                │
│                                                                         │
│ Graph 模式处理：                                                          │
│   检查 README ──success──▶ 运行测试 ──success──▶ changelog ──▶ checklist │
│        │                      │                                         │
│        error                  error                                      │
│        ▼                      ▼                                         │
│   修复 README            重试测试                                        │
│   (修复后终止，         (重试成功→changelog                               │
│    人工检查)             重试失败→终止)                                   │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Insight**: The difference between the three models is not "do it" — it can be done under normal processes. The difference is **when the anomaly occurs**:
- Chain, just give up.
- Plan-Execute Dynamic Adjustment
- Graph jumps by predefined branch

So don't ask "Planning OK," but ask:

- Is the task sufficiently complex to be dismantled first?
- Are the steps stable and can be consolidated into processes?
- Is there a need for mid-course re-planning?
- Do users need to confirm the plan?
- Do you need to go back to one node after failure?

## 5.4 Choose how to organize and then talk about Agent capabilities

Next, we're going to launch the assistant scenes, each model of interface skeletons, execution behaviour and the applicable boundary. For example items at the end of this chapter, there are complete operational codes; the code segments in the body are meant to describe the control stream and some details of the project are omitted.

### 5.4.1 Chain: Fixed sequence change for certainty at the expense of resilience

Chain is the "one way to the black" -- like a water line in a factory, and each position is processed in a regular order, waiting behind the first stop. Release the four steps for preparation to be carried out in a fixed order - first check README, then run the test, then organize changelog, and then generate checklist. There's no branch, there's no "if..."

```python
class ChainExecutor:
    """按固定顺序依次执行步骤。遇错即停，无分支，无重试。"""

    def execute(self, on_step_start=None, on_step_end=None):
        for i, step_name in enumerate(self.steps):
            tool = TOOL_REGISTRY.get(step_name)
            if not tool:
                return ChainResult(status="failed", failed_at=i,
                                   error=f"未找到工具: {step_name}")

            result = tool()  # 执行步骤
            if result.status == StepStatus.ERROR:
                return ChainResult(status="failed", failed_at=i,
                                   error=result.error)
            # 成功，继续下一步

        return ChainResult(status="completed", results=all_results)
```

**Chain's problem is not on the normal path** — normal, four steps go by, everything OK. But on the abnormal path:

```text
场景：运行测试失败

Chain 执行过程：
  ✅ 检查 README → 通过（缺少 Contributing 章节，但不算失败）
  ❌ 运行测试 → 失败！1 个测试用例未通过
  ⏭️ 整理 changelog → 跳过
  ⏭️ 生成 checklist → 跳过

最终报告："发布准备失败，第 2 步运行测试出错。"

用户的感受：我就因为一个测试失败，整个发布流程就停了？
而且那个失败的测试跟这次发布改动无关，是之前的遗留问题。
Chain 不会说"这个测试失败不阻塞发布，可以跳过"——它只会停止。
```

**Chain's applicable boundary is narrow and clear**: steps are fully defined, no surprises, no dynamic decision-making is required. Like, "Read profiles, poach, poach, poach, poach, poach, write in the cache," These four steps will not fail under normal circumstances, and failure means that the system is in trouble, and stop is right.

Chain seems simple, but its failure is often underestimated - because "if you're wrong, stop" is in itself a design decision, not always right:

| Failed performance | Typical cause | Method of amendment |
|---|---|---|
| Failure of non-critical steps leads to disruption of the entire process | Chain doesn't distinguish between "imprisonmental error" and "non-obstructive warning" -- README missing a non-critical chapter and testing all red, and "failure" in Chain's eyes. | If it's really necessary, Chain, separate the steps from the next steps. |
| The sequence of steps is dead, but it's different. | Changelog relies on "test pass", but Chain's step list is flat and does not depend on modelling -- it depends on sequence. | Chain is not suitable if there is a complex dependency between steps; upgrade to Plan-Execute or Graph |
| The same failure always runs from the top. | Step 3 failed. Next time we start from step 1 -- Chain doesn't have the concept of "continue from failure" | If the task is time-consuming, consider Graph's sustainability |
| High cost of user intervention | Half the users want to skip a certain step, Chain doesn't support it -- it's only going to have to be remixed from the middle step after it's run or manually terminated. | If the user interacts more frequently, at least add an inter-step confirmation point (not pure Chain, but functional) |

### 5.4.2 Router: Disaggregat the task type before choosing the execution path

Chain's "One Way to the Black" is good when steps are fixed, but when users move from "pull ready" to "do me a bug" -- you can't do the same thing. Agent needs to judge "what kind of mission this is" before taking the corresponding path. That's Router.

Router is basically "Classer + Multiple Chain". Different tasks follow different paths:

```python
class RouterExecutor:
    ROUTES = {
        "release": ["检查 README", "运行测试", "整理 changelog", "生成 checklist"],
        "bugfix":  ["运行测试", "整理 changelog"],
        "docs":    ["检查 README"],
    }

    def classify(self, query: str) -> str:
        # 实际项目中这里是 LLM 调用，这里简化为关键词匹配
        if "发布" in query or "release" in query.lower():
            return "release"
        if "bug" in query.lower() or "修复" in query:
            return "bugfix"
        if "文档" in query or "readme" in query.lower():
            return "docs"
        return "release"  # 兜底

    def execute(self, query: str):
        category = self.classify(query)
        steps = self.ROUTES.get(category, self.ROUTES["release"])
        return ChainExecutor(steps).execute()
```

Router's key design points:

- **The classification accuracy**: the classification is wrong, the follow-up is all wrong. In the production environment, we don't just look at the "accuracy rate" as a percentage, but at the cost of a single error. The misallocation of the client's FAQ may have been simply an incorrect answer; a refund, a copy, a misallocation of production operations could have resulted in a real loss. High-risk pathways require identification, denial or manual takeover.
- **Bottom path**: Difault path must be available when classification fails. The bottom should not default on the "most complete" path, but the "most secure" path: an explanation that cannot be judged, collects more information, or performs only read-only inspections.
- **In the path or Chain**: Router only solves the "choice the road" and doesn't solve the "what about the pit on the road." Inside the path, it's still stopped by mistake.

Router's failure is usually not when it's right, but when it's wrong and there's no way:

| Failed performance | Typical cause | Method of amendment |
|---|---|---|
| The classification error resulted in the wrong path being executed | The user said, "Check the code for me." Router classified it as a bugfix path. | Catalogs do not rely only on keyword matching; Image classification with LLM few-shot, adding a layer of "confirming route" interaction for vague input |
| The bottom path becomes the "Box of Everything." | All unsettled inputs take the path, causing the path to be over-launched, and users wonder why writing a document for me triggers the release process. | The bottom path should be the safest path (e.g. only information presentation), not the full path; the trigger frequency of the bottom path Monitor |
| Path definition outdated | The bugfix path that was defined last month only contains "run the test + sort the bagelog", but the team's now bugfix process needs an "updated version" | Path definition needs to follow actual workflow; frequency of usage and user feedback for each path is reviewed periodically |
| There are no shared steps between paths | Release path and bugfix path have "run test" but separate definition -- Change the test name twice. | Ripping public steps for reusable step definition, Router path reference step name instead of repeating definition |

### 5.4.3 Plan-Execute: Make the plan visible before allowing failure and re-planning

Router solved the "choice which way," but the inside of the path is Chain -- stop in case of a mistake. What if you fail to release the prep running test? Users would be dissatisfied if they stopped altogether simply because of a failure of a legacy test unrelated to the current release. What you need is not a solid path, but the ability to "adapt to the dynamics of implementation" — to plan first, to implement wrongly and to re-strategize.

This is Planning's most classic realization. Core process in four steps:

```text
1. 生成计划：分析目标 → 拆解为结构化步骤（每步包含：名称、工具、描述、依赖、重试次数）
2. 用户确认：展示计划 → 用户修改或确认
3. 逐步执行：按依赖顺序执行 → 记录每步结果
4. 失败重规划：某步重试耗尽 → 基于当前状态生成新的后续步骤
```

```python
class PlanExecuteExecutor:
    def execute(self, goal, inject_failures=None):
        # 1. 生成计划
        plan = self.generate_plan(goal)
        # plan.steps = [
        #   PlanStep("检查 README", tool="检查 README", depends_on=[]),
        #   PlanStep("运行测试", tool="运行测试", depends_on=[]),
        #   PlanStep("整理 changelog", tool="整理 changelog", depends_on=["运行测试"]),
        #   PlanStep("生成 checklist", tool="生成 checklist",
        #            depends_on=["检查 README", "运行测试", "整理 changelog"]),
        # ]

        # 2. 逐步执行
        for step in plan.steps:
            # 检查依赖是否满足
            unmet = [d for d in step.depends_on if d not in plan.completed_steps]
            if unmet:
                # 依赖未满足 → 先插入依赖步骤
                continue

            result = execute_step(step, inject_failures)

            # 3. 失败处理
            if result.status == "error":
                step.retries += 1
                if step.retries < step.max_retries:
                    continue  # 重试
                else:
                    # 重试耗尽 → 触发重规划
                    new_steps = self.replan(goal, plan.completed_steps,
                                            step.name, result.error)
                    plan.replace_remaining(new_steps)

        return plan.final_output
```

**Replan is the core difference between Plan-Execute and Chain.** Its logic is to generate a new set of next steps based on completed steps + the cause of failure + the tools available. It's not "re-plan from zero" -- the steps that have been completed will not be repeated.

```text
重规划示例（运行测试失败）：
  输入：
    已完成：["检查 README"]
    失败步骤："运行测试"
    错误信息："1 个测试失败: test_memory_cleanup_on_session_end"

  重规划输出（新步骤替换原计划的后续步骤）：
    步骤 3. 分析运行测试失败原因 — 重新运行测试以确认失败原因
    步骤 4. 整理 changelog — 继续执行
    步骤 5. 生成 checklist — 继续执行
```

**The common trap of Plan-Execute**: Replanning itself may fail. If the new steps generated by replan are not enforceable, you need an exit condition-- – Usually the maximum number of heavy plans (e.g., up to 2 re-plannings) are reported later. The Plan-Execute Executor in the Example Project also achieved this layer of protection: `max_replan_count` Or when a duplicate planning step is generated, implementation will be suspended and a cycle avoided.

Plan-Execute is the most flexible of the four models, but flexibility also leads to a unique pattern of failure:

| Failed performance | Typical cause | Method of amendment |
|---|---|---|
| Reschedule the dead cycle | Replan does not distinguish between "recoverable error" (net timeout) and "non-recoverable error" (not in the guit warehouse), reprogrammes all failures equally, and the new plan is the same as the old plan. | Error classification: Retrievable retry, non-recoverable skipping and notification to users; set max replan count=2; test whether new steps are the same as the previous one |
| The plan is too vague to be implemented. | Model-generated steps like "Ensure Everything Normal" - no specific tools, no acceptance standards, no input output. | Plan generation requires specific tools and acceptance standards to be bound at each step; regeneration of steps without a tool name |
| The plan was tampered with after user confirmation | In the course of implementation, Agent detected environmental anomalies and inserted additional steps on its own. Users did not know the plan had changed. | The confirmed plan locks to immutable; any deviation (including insertion steps) requires a new request for user confirmation |
| The plan is too slow. Users can't wait. | The plan generation for complex tasks is multiple LLMs, 30 seconds or more, and the user has cut to another window | Plan generation timeout limit (e. g. 10 seconds); pre-empt a rough plan to allow the user to confirm direction and then refine |
| Relationship Modelling Error | Changelog announces that it relies on the Run Test, but the Run Test is not finished when it's actually done. | The implementation engine needs to check the completion of the dependent step, not only the existence of the step name |

### 5.4.4 Graph: Advance drawing of abnormal paths into the status machine

Plan-Execute's dynamic re-engineering is flexible, but it also has a cost — the LLM is called back every failure to generate new steps, delays are high and results are uncertain. If your release process is implemented once a week and the failure pattern is stable, you don't have to ask LLM to rethink "what now." You can draw the answers into a map in advance -- this is Graph.

Graph modeled the mission into a directional map. Unlike Plan-Execute's One-D List + Dynamic Reordering, all possible paths **are defined at the time of construction**:

```text
发布准备的 Graph 结构：

              ┌────────────┐
              │ 检查 README │
              └─────┬──────┘
                    │ success         error
                    ▼                 ▼
              ┌────────────┐    ┌──────────────┐
              │  运行测试   │    │ 修复 README   │
              └─────┬──────┘    └──────┬───────┘
                    │                  │ success
             success│ error            ▼
                    ▼     ▼       (终止: 人工检查)
              ┌─────────────┐
              │整理 changelog│
              └─────┬───────┘
                    │ success/error → (终止)
                    ▼
              ┌─────────────┐
              │生成 checklist│
              └─────┬───────┘
                    ▼
                  (完成!)
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
                    current = current  # 重试
                else:
                    current = node.on_error  # 走失败分支
            else:
                current = node.on_success  # 走成功分支
```

Graph's real power in the failed branch. The path for normal running is `check_readme → run_tests → changelog → checklist` - Same as Chain. Distinction in an anomaly:

```text
Graph 错误处理（README 检查失败）：
  check_readme → 失败 → on_error 跳转 → fix_readme
  路径：check_readme → fix_readme → (终止)

  Chain 做不到：Chain 的步骤顺序是 ["检查 README", "运行测试", ...]，
  失败后只能停在第一步。

  Plan-Execute 也可以通过 replan 生成"修复 README"这类步骤，
  但它是运行时动态生成；Graph 的修复路径是预定义的——
  更可预测，也更依赖事先设计和测试。
```

**Graph 's modelling costs**: You need to think ahead of time about the jump target for each node in all cases. Graph needs to define 6 nodes (including error processing nodes) for the release of this 4-step task. For a more complex worksheet processing process, the number of nodes could reach dozens -- at which point the maintenance costs of Graph became significant.

Graph's power lies in the predefined branch, but its failure is precisely due to the "predefined" -- you can only deal with the anomalies you've thought about:

| Failed performance | Typical cause | Method of amendment |
|---|---|---|
| The wrong branch code was never tested. | The main path is almost the wrong branch. Crash at first trigger | Regular injection of failure force trigger error branch (chaos test); unit testing for each error branch separately |
| Unforeseen anomalies have no branches. | Graph only defined branches for "test failure" and "reADME missing" but no nodes can be handled when "disk space is insufficient". | Each Graph keeps one `on_unexpected` Bottom-of-the-pipe - Defaults are pauses and notifications to users, not silent failures |
| It's hard to maintain. | In the first six nodes, six months later, 30 nodes, 50 sides, no one can tell the whole picture. | Subchart wrap (contain multiple nodes of "test-related" as a subchart); periodic review of dead nodes (three months without triggering nodes considered for removal) |
| Unable to recover due to the lack of permanence | Crash, reboot, do not know where to proceed and what to do. | Endurance after implementation of each node (current node, completed steps, intermediate results); support for recovery from failure node |
| Over-engineering | A three-line script for reading profile printout is modelled as 5 Node Graph | 5.4.5 Decision tree self-censorship: are the steps fully fixed and without abnormal branches? All right, Chain, that's enough. |

### 5.4.5 Normal paths run and patterns differ when failure

All four models are finished. You may wonder: How different are they? Here's to run the same launch preparation in four different modes — a normal situation, a test failure — so you can see the difference.

Run each of the four modes of launching a preparatory mission against the actual performance:

```text
═══════════════════════════════════════════════════════════════════
任务："准备 v1.2.0 版本发布"（所有步骤正常）
═══════════════════════════════════════════════════════════════════

Chain:           ✅ 4/4 完成。路径: 检查README→运行测试→changelog→checklist
Router(发布):     ✅ 4/4 完成。路径同上。
Plan-Execute:    ✅ 4/4 完成。先展示计划，用户确认后执行。
Graph:           ✅ 4 个节点。路径: check_readme→run_tests→changelog→checklist

所有模式都能完成。此时看不出差异。

═══════════════════════════════════════════════════════════════════
任务："准备 v1.2.0 版本发布"（运行测试失败）
═══════════════════════════════════════════════════════════════════

Chain:           ❌ 第 1 步完成，第 2 步失败，第 3-4 步跳过。
                 最终输出: "发布准备失败"。

Plan-Execute:    ⚠️ 第 1 步完成，第 2 步失败 → 重试 1 次 → 仍失败
                 → 触发重规划 → 插入"分析失败原因"步骤
                 → 判断为非阻塞且用户确认跳过后，继续执行 changelog 和 checklist。
                 最终输出: "发布准备完成（测试失败已记录，待修复）。"

Graph:           ✅ check_readme✓ → run_tests✗ → 重试 → 仍失败
                 → on_error 跳转 → retry_tests✓ → changelog✓ → checklist✓
                 最终输出: "发布准备完成"。

三种模式对同一异常的处理完全不同：
- Chain 直接放弃
- Plan-Execute 动态生成应对策略
- Graph 执行预定义的失败恢复路径
```

**Mode selection decision tree**(practical judgement process):

```text
你的任务步骤是完全固定的吗？
  ├─ 是 → 步骤会有异常需要分支处理吗？
  │      ├─ 不会 → Chain
  │      └─ 会 → 异常分支可以提前穷举吗？
  │             ├─ 可以 → Graph
  │             └─ 不可以 → Plan-Execute
  └─ 否 → 需要根据输入类型选不同路径吗？
         ├─ 是 → Router
         └─ 否 → Plan-Execute 或 ReAct Loop
```

> **Remember**: Do not push a simple task into Graph. Graph's problem is not "too powerful," but you have to maintain node, side, state, wrong branch, recovery strategy and test coverage; if the mission had only a three-step fixed process, these costs would not automatically yield benefits.

### 5.4.6 Not only four models: parallel, organization of workers, assessment of optimization of borders

The first four models are sufficient to explain the release of the assistant scene for this chapter, but three high frequency variants will be encountered in the real project. They are not necessarily higher than Chain, Router, Plan-Execute, Graph, but they are different.

| Mode | Issues addressed | Publish examples of assistants | Boundary application |
|---|---|---|---|
| Parallelization | It's not dependent on each other. | README, relying on gap scans, format checks can run in parallel and eventually aggregate the results | Only when there is no conflict between sub-tasks, little sharing, and failure results can be interpreted independently |
| Orchestrator-Workers | Uncertainty about the number and type of subtasks before running, requiring a organizer ' s dynamic assignment | When moving a project document, the organizer scans the list of files and then distributes different files to multiple worker processes | Fits to an open task; higher cost, needs to workr output uniform, organisers can combine conflicts |
| Evaluator-Optimizer | Output quality requires repeated checking and correction | After generating releasing checklist, check if version numbers are missing, rollback programs, release permissions, and let optimizer modify | Fits qualitatively determinable products; if the evaluation criteria themselves are vague, they can easily become meaningless cycles |

Put them back in the release of the assistant's scene, as you can see:

```text
用户："帮我做 v1.2.0 发布准备。"

Parallelization:
  同时执行 README 检查、测试、依赖漏洞扫描。
  等所有只读检查完成后，再决定是否生成 changelog。

Orchestrator-Workers:
  编排者发现项目里有 Python、Node.js、Docker 三类发布材料。
  分别派发给三个 worker 检查，再汇总为统一 checklist。

Evaluator-Optimizer:
  先生成 checklist。
  evaluator 检查 checklist 是否覆盖测试、版本号、文档、回滚、权限。
  如果缺项，optimizer 修订 checklist，最多迭代 2 次。
```

These three models are often used in combination with previous models: Router can judge the type of task before entering Parallelization; Plan-Execute can break a step into Orchestra-Workers; and Graph can fix Evaluator-Optimizer into a subgraph. The premise of a combination is still the same: to prove simple models first with track and eval, then to add complexity.

## 5.5 Don't just come up and draw a picture: Upgrade with failure and evaluation.

Planning / Workflow Pattersons

| Phase | Do what? | Fit to target. | Don't do anything too early. |
|---|---|---|---|
| V0: Naked | Model step-by-step decision tool, step-by-step judgement | See if the mission really takes more steps. | Don't introduce Planning Frames too early. |
| V1：Checklist | Make the model list the steps, but not enforce them | We'll reduce the leaks and verify if there's a regular step pattern. | Don't ask too early for a structured plan. |
| V2: User confirmation plan | Allow users to modify the plan before execution, confirm and execute | Enhancing controllability and involving users in decision-making | Don't automate too early. If the user can't clear the steps, keep moving. |
| V3: Structured Plan | Targeting, tools, input, acceptance standards per step | Support for traceable implementation and failure positioning | Do not seek form integrity too early - 5 steps enough to generate 15 steps |
| V4: Dynamic re-planning | Automatically adjust plans in case of failure or environmental change | Supporting the adaptation of complex missions | Don't be too early to trust re-engineering -- check the validity of "misclass" and "exit conditions". |
| V5：Graph | Solidize task nodes, states and branches into graphic structures | Support status sustainability, implementation recovery, path back Fire! | Don't fix it too early. |

**The upgrade signal at each stage is specific and visible**, not the vague feeling that the system should be better:

- V0V1: Users say, "You're missing another step" or "You should check X and then do Y" -- that the mission has a fixed pattern and is worth listing.
- V1VV2: Users frequently interrupt Agent during implementation ( "No, don't do that first") — indicating that users want to participate in decision-making.
- V2→V3: Similar tasks are performed more than five times, with a similar feedback from each user ( "What is the acceptance criterion for this step") - a description of the need to structure.
- V3→V4: The failure of "Agent continues hard after a step has failed or abandons it all" - indicates the need for re-planning capability.
- V4VV5: The mission is carried out at least once a week, and there are new people in the team who need to take over — at which point the reversible and recoverable value of Graph can be realized.

It is recommended to be V2 or V3 at the initial stage. Graph waits until the state and branch is really complicated. The cost is not the abstract "complicated" but the need to maintain the node definition, border conditions, permanence, recovery strategy, wrong branch testing and debugging tools. **Rather than relying solely on a perceived mode of upgrading, it will be judged by a closed loop.** Prepare a set of real missions and failed injections, run one in different modes and compare the results:

| Evaluation items | Record what? | Why does it matter? |
|---|---|---|
| Mission completion rate | Ultimately meeting user targets | Preventing complicated patterns is just "looks more complete." |
| Ratio of missing critical steps | Whether necessary steps such as README, Testing, Changelog, Checklist are missing | Validate whether Planning really reduces the missing steps |
| Failed recovery rate | Injection test failed, file missing, permission error given correct treatment | The value of Planning is mainly in abnormal paths. |
| User confirmations | Number of user confirmations required before and during implementation Minor | Too little to lose control. Too much to interrupt the work flow. |
| Average time and cost | LLM calls, time-consuming tools, total delay | Plan-Execute and Graph returns must cover costs |
| Number of planned deviations | Whether actual execution inserts, deletes, skips confirmed steps | Validate whether the confirmation lock is in effect. |
| Relayability | Can you see input, output, status and error per step from the track | Deciding whether the system can be debugged, audited and handed over |

A simple comparison template:

```text
任务集：发布准备 10 条，其中 3 条注入失败

模式              完成率  失败恢复率  平均耗时  用户确认次数  计划偏离次数  是否升级
Chain             70%     20%         低        0             0             否：异常路径太弱
Plan-Execute      90%     80%         中        1.4           0             是：收益覆盖成本
Graph             92%     90%         中        1.1           0             暂缓：建模成本高，任务还不稳定
```

**Production level Planning at least records this information**. Otherwise, the plan would appear to be clear, effectively unrecoverable, unauditable and unmodified:

| Fields | Meaning |
|---|---|
| `goal` | Original user target, avoid drifting from active target |
| `plan_version` | planned version; new version generated for each structural change |
| `steps` | Name, tool, input, output, dependence, acceptance standards per step |
| `state ` | ` pending ` / ` running ` / ` completed ` / ` failed ` / ` skipped` |
| `approval` | Who confirmed which version of the plan and what the scope was? |
| `risk_level ` | ` read_only ` / ` modifies_files ` / ` external_side_effect ` / ` irreversible` |
| `requires_approval` | Need for manual validation for execution, in particular for writing, submitting, publishing, deleting, paying, etc. |
| `trace` | Call, time-consuming, error, number of retests and observations per step |
| `recovery` | Rule(s) for retrying, skipping, reprogramming, manual takeover or termination after failure |

**Designing the order of decision-making for Planning (in the case of publishing assistants):**

1. **To confirm whether the task really requires Planning**: Self-censorship using 5.7 criteria — a task that can be accomplished in one step? Two or three steps of fixed process is enough? If the answer is yes, stop here and don't introduce Planning. Naked Rect ran five missions to see if there were signs of "missing steps, bias, inability to recover".
2. **Observe the natural pattern of the mission**: are the mission steps fixed or subject to input changes? Do you need to try again, skip or reprogramme after you fail? Do users need to be involved in decision-making? These observations determine which direction you're going in -- instead of choosing an "advanced" model.
3. **Start with the simplest mode**: first Chain (if steps are fixed and no anomalies) or Router (if diversion by type of input). Upgrade to Plan-Execute or Graph only when you do encounter an anomaly that Chain/Router cannot handle. **The only reasonable reason for the mode upgrade is that you have a specific malfunction, not "this model is higher."**4. **Define exit conditions for each mode**: Chain stopped when it failed? How many times does Plan-Execute plan? Which part of the unforeseeable abnormality goes to? Planning without exit conditions is not Planning, it's "Agent can't get out of the loop."
5. **The wrong path is the same as the main path**: the failed branches of Graph are the last time you want to face them when they're triggered for the first time. Regular injection of failure force triggers, and each error branch is tested separately.
6. **The plan is locked as soon as it is confirmed**: the user confirms the 4-step plan, and the implementation cannot be 5-step. Any deviation — whether by inserting new steps or skipping — needs to be reconfirmed. Distinguishing between "light adjustment" (retry delay), which is automatic, and "structural change" (insert/delete steps), which is confirmed.
7. **Comparative assessment with real missions**: preparation of 3 missions — one perfectly normal, one intermediate step failed, one required re-planning. Run in different modes, comparing: step completion rate, failure recovery rate, number of user interventions, final output quality, cost and track readability. Don't make decisions by feeling Chain enough.

## 5.6 Planning failure usually dies in an abnormal path Let's go.

### 5.6.1 Location at first glance: Planning Failed Mode Quick Checklist

| Failed Mode | Performance | Possible causes | Revision Direction |
|---|---|---|---|
| The plan is not implemented. | The steps seem reasonable but impossible to land. | No tools and no environmental constraints | Planned binding tools and acceptance standards |
| It's too detailed. | Generating a lot of meaningless steps. | Seek form integrity | Limit the number of steps and the size of particles |
| Implementation of deviation plan | Forget the plan when it's implemented | Status does not record current steps | Update status after each step of implementation |
| No re-planning. | Continue hard when tools fail | No failures. | Adding planning triggers |
| Over-engineering | Small task, Graph. | Technology driven | Start with Chain / Router |
| Users don't buy. | The plan doesn't match the user's real goal. | Missing confirmation node | Confirm the plan before it is implemented |

### 5.6.2 Three failure stories: dead cycle, undetected branches, bad plans

The quick check sheet tells you "what may be the problem," but there are often layers between symptoms and root causes when actually debugging. The following is a display of how symptoms can be traced to the root causes and repaired by the failure of the three release assistant scenarios.

- -- **Debug story one: Plan-Execute reprogrammed into a dead cycle**

```text
症状：
用户说"帮我做发布准备"。Agent 生成计划，执行到"整理 changelog"时失败
（错误：GitError: 不在 git 仓库中）。重规划生成的新步骤中又有"整理 changelog"，
再次失败，再次重规划……用户等了 3 分钟，Agent 还在循环。

排查过程：
1. 查看 trace → changelog 步骤失败了 8 次，重规划了 6 次
2. 每次重规划都生成了相同的步骤："整理 changelog" + "生成 checklist"
3. 错误信息一直是 "GitError: 不在 git 仓库中"——环境问题，重试不可能解决
4. 重规划逻辑没有判断"失败原因是否可恢复"——对所有错误都一视同仁

根因：
- replan() 函数只看了"失败步骤名"，没分析"失败原因类型"
- GitError 是环境问题（不可恢复），但被当作可重试的错误处理
- 缺少最大重规划次数限制

修复：
1. 错误分类：可恢复错误（网络超时、资源暂时不可用）→ 重试；
   不可恢复错误（配置错误、环境问题、权限不足）→ 跳过并通知用户
2. 增加 max_replan_count=2：最多重规划 2 次，超过后终止并上报
3. 重规划时检查"新步骤是否与前次相同"——如果相同，说明 replan 没有
   产生有效替代方案，应该终止而不是继续
```

- -- **Debug Story II: The wrong branch of Graph was never tested**

```text
症状：
"修复 README"节点在生产环境中第一次被触发时，
执行了 30 秒后 crash——它尝试写入一个不存在的目录。
但这个节点在图中已经存在了 3 个月。

排查过程：
1. 查看 Graph 定义 → fix_readme 节点的 action 是 lambda 写的临时代码
2. 这个节点从未在正常流程中被触发（因为"检查 README"几乎不会失败）
3. 开发时只测试了主路径（happy path），错误分支只在代码中存在，
   从未被集成测试覆盖

根因：
- Graph 的失败分支在构建时定义，但测试时几乎只覆盖主路径
- 错误分支代码是"写完就忘了"的代码——没有监控、没有告警
- 正常情况下这些节点永远不会被访问，但一旦被访问就是紧急情况

修复：
1. 注入测试：定期向 Graph 中注入错误，强制触发所有错误分支
   （例如：每周跑一次 chaos test，故意让 README 检查失败）
2. 错误分支节点也必须有完整的日志和监控
3. 每个错误分支节点单独做单元测试
```

- -- **Debug story three: After user confirmation, Agent changed the plan without permission**

```text
症状：
用户确认了 Agent 生成的 4 步发布计划。执行到第 3 步（"整理 changelog"）时，
Agent 发现 git log 中有一些未提交的改动，它自行插入了一个
"先提交未保存的改动"步骤，导致 changelog 内容包含了不该包含的改动。

排查过程：
1. 查看执行 trace → 第 3 步执行前，Agent 检测到 dirty working tree
2. Plan-Execute 的 execute() 方法中有一段逻辑：
   "如果检测到环境异常，自动插入修复步骤"
3. 用户确认的是 4 步计划，但实际执行了 5 步——用户不知道第 5 步的存在

根因：
- 计划确认后没有锁定：用户确认的是一个"快照"，但执行器把它当
  "参考模板"来用
- "自动插入步骤"的权限太高——它不应该在用户确认后还能修改计划

修复：
1. 计划确认后锁定：confirmed_plan 是 immutable 的，
   任何偏离都需要重新请求用户确认
2. 如果执行过程中发现需要额外步骤，暂停执行并通知用户：
   "发现环境异常（working tree 有未提交改动），
   建议先提交再继续。是否允许我插入这个步骤？"
3. 区分"微小调整"（如重试延迟时间）和"结构变更"（如插入新步骤）——
   前者自动处理，后者必须确认
```

---

**The three stories in common**:

- **Reprogramming is not silver** — it needs to be accompanied by an erroneous classification (recoverable vs non-recoverable) and exit conditions (maximum planning times).
- **The wrong path deserves to be as serious as the main path.** -**Plan should be locked as soon as it is confirmed.** The user confirms that the 4-step plan cannot be implemented in 5 steps. Any deviation would need to be reconfirmed.

## 5.7 Not every multistep is worth Planning.

Planning:

- The mission can be accomplished in one step.
- Two or three steps of a fixed process are sufficient.
- Users are more interested in quick results than in plans.
- The plan cannot be validated, only an intermediate text is generated.
- The tasks are carried out by a firm business process stabilization.
- There has been a marked increase in costs and delays since the introduction of the plan, but the quality has not improved.
- There is no trace or evaluation data to prove that Planning really reduces the slippage, failure and return to work.

Practical judgement:

```text
如果问题主要是"漏步骤、走偏、无法恢复"，考虑 Planning。
如果问题只是"某一步工具调用错了"，先修工具机制。
```

## 5.8 From drift to removable: One Planning Life Cycle

The following is a series of key differences in the four models, replaying them with a continuous cross-sky story. This is the three iterative versions of the release assistant, from the beginner to the reliable tool.

```text
═══════════════════════════════════════════════════════════════════
V1：裸 ReAct — 周一 14:00
═══════════════════════════════════════════════════════════════════
│
│  [14:00] 用户："帮我做 v1.2.0 发布准备。"
│
│  Agent 的 ReAct 循环：
│    思考：用户要做发布准备，先看看项目结构。
│    行动：ls -la（列出文件）
│    观察：看到 README.md, src/, tests/, CHANGELOG.md
│
│    思考：有 CHANGELOG.md，让我看看内容。
│    行动：cat CHANGELOG.md
│    观察：（读取了 200 行 changelog 历史）
│
│    思考：changelog 最后更新在 3 个月前。让我看看最近的 git log。
│    行动：git log --oneline -20
│    观察：（输出了 20 条 commit）
│
│    思考：最近的 commit 有 feat 和 fix，需要整理到 changelog。
│    行动：（开始编辑 CHANGELOG.md……）
│
│    思考：应该也检查一下测试。
│    行动：npm test
│    观察：42 passed, 0 failed
│
│    思考：测试通过。用户还提到要检查 README……
│    行动：cat README.md
│    （此时已经过去了 8 分钟，用户已经不耐烦了）
│
│  问题：Agent 在第 1 步就偏离了。它没有先理解"发布准备"需要哪些步骤，
│        而是每步临场决策，被文件内容吸引，在 changelog 编辑上花了
│        大量时间，最后才想起来还有 README 和 checklist。
│        用户要的是一个清单，Agent 却开始改文件了。
│
│  用户反馈："我只是想让你生成一个 checklist，你怎么开始改 changelog 了？
│             而且 changelog 内容也不对，包含了未完成的 commit。"
│
═══════════════════════════════════════════════════════════════════
V2：Plan-Execute — 周二 10:00（基于用户反馈改进）
═══════════════════════════════════════════════════════════════════
│
│  [10:00] 用户："帮我做 v1.2.0 发布准备。"
│
│  1. 生成计划：
│     Agent 不再直接动手，而是先生成计划：
│
│     ┌─────────────────────────────────────────────────────────┐
│     │ 发布准备计划 - v1.2.0                                    │
│     │                                                         │
│     │ 步骤 1. 检查 README 完整性                               │
│     │   工具: 文件读取 + 章节校验                               │
│     │   验收: 确认 Installation, Quick Start, API,             │
│     │         Contributing 四个章节都存在                       │
│     │                                                         │
│     │ 步骤 2. 运行测试                                         │
│     │   工具: npm test                                        │
│     │   验收: 所有测试用例通过                                  │
│     │                                                         │
│     │ 步骤 3. 整理 changelog                                   │
│     │   工具: git log + changelog 模板                         │
│     │   依赖: 步骤 2 通过（确保改动已测试）                     │
│     │   验收: changelog 覆盖本次发布的所有 commit               │
│     │                                                         │
│     │ 步骤 4. 生成 release checklist                           │
│     │   工具: checklist 模板                                   │
│     │   依赖: 步骤 1, 2, 3 全部完成                            │
│     │   验收: checklist 覆盖所有发布检查项                      │
│     └─────────────────────────────────────────────────────────┘
│
│  [10:01] 用户确认："计划看起来不错，执行吧。但测试如果失败不要
│           硬停——告诉我哪个失败了，我决定是否继续。"
│
│  2. 执行：
│     步骤 1 ✅ — README 缺少 Contributing 章节，但不算阻塞
│     步骤 2 ❌ — 1 个测试失败: test_memory_cleanup
│
│     重试步骤 2 — 仍然失败。
│
│     根据用户的指示，Agent 不硬停，而是报告：
│     "步骤 2 运行测试：1 个测试失败（test_memory_cleanup_on_session_end）。
│      这个失败的测试与本次发布改动无关。是否跳过继续？"
│
│     用户："跳过，继续。"
│
│     步骤 3 ✅ — changelog 已生成，覆盖 5 个 commit
│     步骤 4 ✅ — checklist 已生成
│
│  3. 最终输出：
│     ✅ 发布准备完成
│     ⚠️ 测试：1 个已知失败（非阻塞，已记录）
│     📋 Checklist 包含 7 个检查项
│
│  用户反馈："这次好多了！计划清晰，遇到问题有选择，不是一刀切。"
│
═══════════════════════════════════════════════════════════════════
V3：Graph — 周三 15:00（流程固化为可复用工作流）
═══════════════════════════════════════════════════════════════════
│
│  经过一周的稳定运行，团队决定把发布流程固化为 Graph：
│
│  原因：
│  - 发布流程每周至少执行一次，步骤和分支已经稳定
│  - 需要支持"恢复执行"——如果执行到一半出问题，生产系统应能从失败节点继续
│  - 需要可回放——新人接手发布时可以重放上一次的执行路径
│
│  [15:00] 新人第一次执行发布："帮我做 v1.3.0 发布准备。"
│
│  Graph 执行路径（自动记录每一步）：
│    check_readme   ✅ → "README 完整"
│    run_tests      ✅ → "42/42 passed"
│    changelog      ✅ → "Changelog 已生成"
│    checklist      ✅ → "7/7 检查项"
│
│  执行路径: check_readme → run_tests → changelog → checklist
│
│  [15:30] 第二次发布（README 有问题）：
│    check_readme   ❌ → FileNotFoundError
│    fix_readme     ✅ → "README 已补充"（自动跳转到修复节点）
│    （终止，等待人工检查）
│
│  执行路径: check_readme → fix_readme
│
│  用户反馈："我不用每次都说'如果失败怎么办'——分支逻辑已经
│             写在 Graph 里了。而且执行路径可追溯，很放心。"
│
│  但代价是：构建这个 Graph 花了一个下午。团队需要定义 6 个节点、
│  8 条边、3 个重试策略——这些都是 Chain 和 Plan-Execute 不需要的。
│
═══════════════════════════════════════════════════════════════════
```

**Several key behaviours exposed in playback**:

1. **Naked Rect is not Planning**: it does not have a global task view and is prone to partial bias by local information — Agent is attracted to changelog content at step 1 and deviates from the goal of generating checklist.
2. **Plan-Execute's core value lies in "Plan Visualization + Failed Decision Point"**: Users can see steps ahead of time, make choices when they fail -- skipping this non-stop test is not possible for Chain.
3. **Graph's value lies in "reliability of solidification"**: normal and unusual processes are predefined and each execution is predictable and releasable. But the construction costs -- this release of Graph took the team one afternoon -- should not be the default option.
4. **The iterative order is important**: nudity React validates feasibility plus Plan-Execute improves reliability and stabilizes before considering solidification to Graph. Don't skip the middle step. If you jump, you'll find the wrong branch in Graph that was never tested when the first trigger in the production environment. **Core decision review of four models:**

| Mode | Core decision-making | Wrong behavior. |
|---|---|---|
| Chain（5.4.1） | Are the steps fully fixed and without abnormal branches? | Non-critical step failure leads to complete process interruption; users want to skip a step but Chain does not support |
| Router（5.4.2） | Is the classification accurate enough? Is the bottom path secure? | The cataloguing error led to the wrong path being executed; the bottom path became a "massive bin". |
| Plan-Execute（5.4.3） | Are reprogrammed exit conditions reliable? Are you locked after plan confirmation? | Reschedule dead loops;Agent inserts new steps without permission after user confirmation |
| Graph（5.4.4） | Are modelling costs worth paying? Is the error branch tested the same as the main path? | 30 nodes no one can tell the whole story; wrong branch 3 months without trigger, crash |

**Three main lines through the entire link:**

1. **Mode selection is driven by scenes, not by "high sense"**: Chain is not "lower mode", and Graph is not "high mode". If the steps of a mission are fully fixed and not unexpected, Chain is the best solution — it is simple, predictable and cost-free. A complex model is only worth introducing if it proves that it can reduce leakages, increase failure recovery rates or improve handover audits.
2. **The abnormal path deserves to be as serious as the main path**: Most Planning malfunctions are not on the main path — normal processes can be completed in four modes. The failure occurred when Chain gave up, Plan-Execute fell into a re-planning cycle, and the error branch of Graph was never tested. When evaluating the Planning system, don't just look at "can we run out of normal time" or "what to do with abnormal times."
3. **Plan is locked as soon as it is confirmed and deviation needs to be reconfirmed**: Planning ' s credibility is based on user confirmation of the plan. The user confirmed the 4-step plan that Agent could not implement 5-step -- whatever the "good faith" reasons. Any deviation required the knowledge and confirmation of the user.

Turning back to the question at the beginning of this chapter - Agent started drifting in the face of multistep tasks. Take the example of the release assistant: the user gave the release task of four steps, and the naked Reform Agent started to explore the details of the changelog in step 1, departing from the original target. The essence of Planning is not to let Agent "softly choose the next step", but **to establish a global mission structure** — which steps, what dependencies are, what happens after failure — before doing so. The more defined the structure (Chain), the less flexible it is, the more predictable it is; the more dynamic it is (Plan-Execute), the more flexible it is and the more necessary it is to exit the conditions.

> **The story is not over.** Planning gives Agent a global task view and release is ready not to miss steps. But there's a new problem: Agent's test failed at the point of running the test, and TypeError clearly hit it in the log -- Agent saw it, but kept writing about changelog, and didn't stop to decide whether to try again, process, downgrade or stop. It lacks the closed loop of "responding to sorting decision-making or stopping". This is what the next chapter is about.

---

### Summary of this chapter

The essence of Planning is not to let Agent "softly choose the next step" but to establish a global task structure before he does it — which steps, what dependencies are, what happens when he fails — and then to implement it under its constraints. Three main lines running through the chapter: **Mode selection is driven by scenes, not by "high senses".** Chain is not a low-level model, Graph is not an advanced model. Chain is the best — simple, predictable, zero maintenance costs — if the steps of a mission are completely fixed and not unexpected. 5.4.5 Decision tree self-censorship: steps fixed and non-abnormal? Yeah, Chain. Need input diversion? Router. Anomalous patterns can be exhaustive? Otherwise, Plan-Execute. The upgrade mode is preceded by track and eval proving that complexity can be replaced by higher completion, failure recovery or releasability. **Anomalous path deserves as much serious as the main path.** Most Planning malfunctions do not occur on the main path - normal processes can be completed in four modes. The failure occurred when Chain gave up, Plan-Execute fell into a re-planning cycle, and the error branch of Graph was never tested. When evaluating the Planning system, don't just look at "can we run out of normal time" or "what to do with abnormal times." Regular injections force trigger error branches, and each error branch is tested separately. **Plan locked once confirmed.** User confirmed the 4-step plan that Agent could not implement 5-step -- for whatever "good faith" reasons. Any deviation (inserting, deleting, skipping steps) requires a new request for user confirmation. Distinguishing between "small adjustments" (retry delay) and "structural changes" (inserting/deleting steps) — the former are automatically processed and the latter must be confirmed.

---

## Runable Example

Once this chapter is completed, you can compare the local Planning example of running course 5 05-05 with:

- [Course 5 05-05 Planning / Worklow Pattersons](../examples/course-05-05-planning/README.md)

This example revolves around the "publishing assistant" scene, where four Planning models are shown in two versions: Chain (fixed order), Router (classification route), Plan-Execute (planned implementation of re-engineering), Graph (nodal chart + condition margin + status machine). Examples include an interactive REPL in which you can perform the same task in a different mode, inject failure-watching re-planning behaviour, and compare the four models with different treatments of the same anomaly.

Examples are teaching achievement, not a complete production framework: It is confirmed by pressing the Enter simulation user that the Graph logs replayable path without lasting recovery; Plan-Execute already contains the maximum number of heavy plans and repeats the reprogramming test to avoid the failure path in the example.

```bash
# Python 版本
cd examples/course-05-05-planning/python
python3 planning_demo.py

# Node.js 版本
cd examples/course-05-05-planning/nodejs
node planning_demo.mjs
```

> **Chapter IV Review.** You now have four perspectives on Agent: scene enhancement (Chapter 1) defines what additional capabilities Agent needs in multiple rounds of interaction; RAG (Chapter 2) solves "what the model doesn't know to look for information"; Memory (Chapter 3) solves "state continuity of cross-session"; and Planning (Chapter) solves "organization and execution of multi-step tasks". But, Agent, there's one more problem that we haven't solved in the face of a complicated mission. **It sees feedback signals, but continues the path down and does not stop to decide on the next step**. This is the next chapter of the question to be answered.

---
