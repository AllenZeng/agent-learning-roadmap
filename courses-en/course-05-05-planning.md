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
Help me get ready for release: check README's integrity, run the tests, organize changelogs, generate release checklist.
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
Scene: Release Assistant Agent

User: A developer maintaining open source projects
Typical task: Software release preparation (check README, run tests, organize changelog, generate checklist)
Complexity: 4 steps, with a dependency between the steps (changelog must be created after the test is passed).
        checklist Reliance on all pre-steps)
Challenges:
  - Step is not completely independent.——He's dependent on you.
  - Tests may fail.——You need to decide whether to try again or skip.
  - README The necessary chapters may be missing——Need to decide whether to block the release
  - First users may not be clear about all the steps.——Could not close temporary folder: %s

Planning Needs:
  - Dependency between steps needs to be clearly modelled
  - When a step fails, a clear approach is required.
  - Pre-implementation users may need to confirm the plan
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
Other Organiser

┌─────────────────────────────────────────────────────────────────────────┐
│ Chain Mode processing:│
│   Check README → Run Test → Collate Changelog → Generate checklist│
│   Stop in case of a mistake. Test failed → All in the back.│
│                                                                         │
│ Plan-Execute Mode processing:│
│   1. Generation plan (ibid., step 4)│
│   2. User confirmation│
│   3. Progressive implementation. Test failed → Try again 2 times → Still failed. → Replanning│
│      "The reason for the failure of the test was that the test was wrong, and that the test was wrong.│
│       New next steps: analysis of causes of failure → Rehabilitation → Retest → Go on."│
│                                                                         │
│ Graph Mode processing:│
│   Check README──success──▶ Run Test──success──▶ changelog ──▶ checklist │
│        │                      │                                         │
│        error                  error                                      │
│        ▼                      ▼                                         │
│   Fix README Retest│
│   (Ended after repair, (successful retest) → changelog                               │
│    Manual check) → Terminated)│
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
    """Execute steps in a fixed order. Stop on error; no branches or retries."""

    def execute(self, on_step_start=None, on_step_end=None):
        for i, step_name in enumerate(self.steps):
            tool = TOOL_REGISTRY.get(step_name)
            if not tool:
                return ChainResult(status="failed", failed_at=i,
                                   error=f"No tool found:{step_name}")

            result = tool()  # Implementation steps
            if result.status == StepStatus.ERROR:
                return ChainResult(status="failed", failed_at=i,
                                   error=result.error)
            # Success. Go on.

        return ChainResult(status="completed", results=all_results)
```

**Chain's problem is not on the normal path** — normal, four steps go by, everything OK. But on the abnormal path:

```text
scene: run test failed

Chain Implementation process:
  ✅ Check README → Passed (lack of Contributing Chapter but not a failure)
  ❌ Run Test → Failed！1 One test example failed
  ⏭️ Collate Changelog → Skip
  ⏭️ Generate checklist → Skip

Final report: "Performance failure, error in step 2 running test."

User's perception: I stopped the entire release process because a test failed.?
And that failed test had nothing to do with the release of the change. It was a legacy.
Chain Not to say, "This test fails without blocking the release. You can skip."——It'll just stop.
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
        "release": ["Check README, Run Test, Collapse Changelog, Generate Checklist],
        "bugfix":  ["Run test, "Check up changelog."],
        "docs":    ["Check README"],
    }

    def classify(self, query: str) -> str:
        # This is the LLM call in the actual project, which is simplified to match the keyword
        if "In query or "release" in query.lower (:
            return "release"
        if "bug" in query.lower() or "In repair:
            return "bugfix"
        if "Document in query or "readme" in query.lower():
            return "docs"
        return "release"  # Bottom

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
1. Generating plan: analytical objective → Dismantling to a structured step (each step includes: name, tool, description, dependence, number of retries)
2. User confirmation: presentation plan → User modify or confirm
3. Progressive implementation: implementation in the order of reliance → Record the results of each step
4. Failed to re-strategize: a step to exhaust → Generate new next steps based on current status
```

```python
class PlanExecuteExecutor:
    def execute(self, goal, inject_failures=None):
        # 1. Generation schedule
        plan = self.generate_plan(goal)
        # plan.steps = [
        #   PlanStep("Check README', tool="Check README, inspections on=[]),
        #   PlanStep("Run Tests, tool="Run Tests, depends on=[]),
        #   PlanStep("Cleaning up changelog, tool="Collapse changelog, depends on=["Run the test."]),
        #   PlanStep("Generate checklist, tool="Generate checklist."
        #            depends_on=["Check README, Run Test, Collapse Changelog]),
        # ]

        # 2. Progressive implementation
        for step in plan.steps:
            # Check if dependency is satisfied
            unmet = [d for d in step.depends_on if d not in plan.completed_steps]
            if unmet:
                # Reliance Unsatisfied → Insert dependency step first
                continue

            result = execute_step(step, inject_failures)

            # 3. Failed to process
            if result.status == "error":
                step.retries += 1
                if step.retries < step.max_retries:
                    continue  # Try again
                else:
                    # It's exhausting. → Trigger replanning
                    new_steps = self.replan(goal, plan.completed_steps,
                                            step.name, result.error)
                    plan.replace_remaining(new_steps)

        return plan.final_output
```

**Replan is the core difference between Plan-Execute and Chain.** Its logic is to generate a new set of next steps based on completed steps + the cause of failure + the tools available. It's not "re-plan from zero" -- the steps that have been completed will not be repeated.

```text
Reprogramming example (run test failed):
  Input:
    Completed:["Check README"]
    Failed step: Run test
    return a tool_not_found error

  Reprogramming output (new steps replace planned next steps):
    Step 3. Analysis of reasons for failure in running tests— Rerun test to confirm cause of failure
    Step 4. Collapse changelog— Continue
    Step 5. Generate checklist— Continue
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
Launching the proposed Graph structure:

              ┌────────────┐
              │ Check README│
              └─────┬──────┘
                    │ success         error
                    ▼                 ▼
              ┌────────────┐    ┌──────────────┐
              │  Run Test│    │ Fix README│
              └─────┬──────┘    └──────┬───────┘
                    │                  │ success
             success│ error            ▼
                    ▼     ▼       (Termination: manual check)
              ┌─────────────┐
              │Collate Changelog│
              └─────┬───────┘
                    │ success/error → (Terminated)
                    ▼
              ┌─────────────┐
              │Generate checklist│
              └─────┬───────┘
                    ▼
                  (Completed!)
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
                    current = current  # Try again
                else:
                    current = node.on_error  # Go to the failed branch.
            else:
                current = node.on_success  # Take the successful branch.
```

Graph's real power in the failed branch. The path for normal running is `check_readme → run_tests → changelog → checklist` - Same as Chain. Distinction in an anomaly:

```text
Graph Error processing (README check failed):
  check_readme → Failed → on_error Jump → fix_readme
  Path: check readme → fix_readme → (Terminated)

  Chain Can't do it: Chain's sequence is["Check Readme, Run Test,...],
  Failure can only be stopped at the first step.

  Plan-Execute You can also create "rehabilitating README" through replans.
  But it's run-time dynamic.;Graph The path to repair is predefined.——
  More predictable and dependent on prior design and testing.
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
Mission: "Prepar for v1.2.0 release" (all steps are normal)
═══════════════════════════════════════════════════════════════════

Chain:           ✅ 4/4 Done. Path: Check README → Run Test → changelog → checklist
Router(Published:✅ 4/4 Done. The path is the same.
Plan-Execute:    ✅ 4/4 Done. Show the plan first, user confirmation and implementation.
Graph:           ✅ 4 Node. Path: check readme → run_tests → changelog → checklist

All models can be completed. There is no difference at this time.

═══════════════════════════════════════════════════════════════════
Other Organiser
═══════════════════════════════════════════════════════════════════

Chain:           ❌ Step 1, step 2, failed, step 3-4 jumped.
                 Final output: "Dispatch ready failed".

Plan-Execute:    ⚠️ Step 1, step 2, failed → Try again 1 time → Still failed.
 → Trigger replanning → Insert "Analyse the causes of failure" step
 → Continue the changelog and checklist when judged unblocked and confirmed by the user.
                 Final output: "Issuing ready for completion (the test failure has been recorded, pending repair). "

Graph:           ✅ check_readme✓ → run_tests✗ → Try again → Still failed.
 → on_error Jump → retry_tests✓ → changelog✓ → checklist✓
                 Final output: "Release ready."

The treatment of the same anomaly is completely different in three models:
- Chain Just give up.
- Plan-Execute Dynamic generation responses
- Graph Executing predefined failed recovery path
```

**Mode selection decision tree**(practical judgement process):

```text
Are your mission steps completely fixed??
  ├─ Yes. → Is there an anomaly in the procedure that requires a branch??
  │      ├─ Nope. → Chain
  │      └─ Yes. → Can an abnormal branch run ahead??
  │             ├─ Yeah. → Graph
  │             └─ No way. → Plan-Execute
  └─ Yes → Do you need to select different paths according to type of input??
         ├─ Yes. → Router
         └─ Yes → Plan-Execute Or Reform Loop
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
User: "Help me do v1.2.0 release preparation."

Parallelization:
  Also perform README checks, tests, and rely on gap scanning.
  When all read-only checks are completed, the decision is made to generate changelog.

Orchestrator-Workers:
  The organizers found three types of release material for Python, Node.js and Docker.
  Sending three worker checks each to be aggregated into a unified checklist.

Evaluator-Optimizer:
  Mr. Checklist.
  evaluator Checks whether checklist covers tests, version numbers, documents, rollbacks, permissions.
  If missing, optimizer revises checklist up to two times.
```

These three models are often used in combination with previous models: Router can judge the type of task before entering Parallelization; Plan-Execute can break a step into Orchestra-Workers; and Graph can fix Evaluator-Optimizer into a subgraph. The premise of a combination is still the same: to prove simple models first with track and eval, then to add complexity.

## 5.5 Don't just come up and draw a picture: Upgrade with failure and evaluation.

Planning / Workflow Pattersons

| Phase | Do what? | Fit to target. | Don't do anything too early. |
|---|---|---|---|
| V0: Naked | Model step-by-step decision tool, step-by-step judgement | See if the mission really takes more steps. | Don't introduce Planning Frames too early. |
| V1:Checklist | Make the model list the steps, but not enforce them | We'll reduce the leaks and verify if there's a regular step pattern. | Don't ask too early for a structured plan. |
| V2: User confirmation plan | Allow users to modify the plan before execution, confirm and execute | Enhancing controllability and involving users in decision-making | Don't automate too early. If the user can't clear the steps, keep moving. |
| V3: Structured Plan | Targeting, tools, input, acceptance standards per step | Support for traceable implementation and failure positioning | Do not seek form integrity too early - 5 steps enough to generate 15 steps |
| V4: Dynamic re-planning | Automatically adjust plans in case of failure or environmental change | Supporting the adaptation of complex missions | Don't be too early to trust re-engineering -- check the validity of "misclass" and "exit conditions". |
| V5:Graph | Solidize task nodes, states and branches into graphic structures | Support status sustainability, implementation recovery, path back Fire! | Don't fix it too early. |

**The upgrade signal at each stage is specific and visible**, not the vague feeling that the system should be better:

- V0V1: Users say, "You're missing another step" or "You should check X and then do Y" -- that the mission has a fixed pattern and is worth listing.
- V1VV2: Users frequently interrupt Agent during implementation ( "No, don't do that first") — indicating that users want to participate in decision-making.
- V2 → V3: Similar tasks are performed more than five times, with a similar feedback from each user ( "What is the acceptance criterion for this step") - a description of the need to structure.
- V3 → V4: The failure of "Agent continues hard after a step has failed or abandons it all" - indicates the need for re-planning capability.
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
Job set: 10 articles published, 3 of which failed to inject

Mode, completion rate, failure recovery rate, average time, number of user confirmations, number of planned deviations, whether or not to upgrade
Chain             70%     20%         Low 0 No: abnormal path weak
Plan-Execute      90%     80%         1.4 0 Yes: Cost of revenue cover
Graph             92%     90%         1.10 Suspension: high modelling costs and unstable tasks
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
Symptoms
The user said, "Help me get ready for the release." Agent Generation Program failed when it was implemented until "Check changelog"
(Error: GitError: Not in guit repository. In the new steps generated by the reprogramming, there is also the "changelog" that has been created.
Again, again, again.……The user waited three minutes, and Agent is still revolving.

Queries:
1. View Trace → changelog Step failed eight times, reprogrammed six times.
2. Every reprogramming has generated the same step: "Collating Changelog."+ "Generate checklist"
3. The wrong message has been "GitError: Not in the guit warehouse."——Environmental problems. It's impossible to try again.
4. The reprogramming logic does not judge whether the cause of failure can be restored.——All mistakes are equal.

GEN:
- replan() The function only looks at the "failure step name" and does not analyze the "causes of failure."
- GitError It is an environmental issue (non-recoverable), but it is treated as a re-testable error
- Lack of maximum planning limit

Restoration:
1. Error classification: recoverable error (network timeout, resources temporarily unavailable) → Try again;
   Unrecoverable error (assembly error, environmental problem, inadequate authority) → Skip and notify users
2. Add max replan count=2:Maximum multiple planning 2 times, terminated and reported after
3. Check if the new step is the same as the previous one during reprogramming.——If it's the same, it means no.
   The creation of effective alternatives should be discontinued rather than continued
```

- -- **Debug Story II: The wrong branch of Graph was never tested**

```text
Symptoms
"When the README node was first triggered in the production environment,
30 seconds to crash——It tries to write a non-existent directory.
But this node has been in the picture for three months.

Queries:
1. View Graph Definition → fix_readme The action for node is a temporary code written by lmbda
2. This node was never triggered in the normal process.
3. Only primary path (happy path) was tested at the time of development, and the error branch only exists in the code.
   Never covered by integration tests

GEN:
- Graph Failed branch defined at build, but tested with almost only main path
- The wrong branch code is the code for writing and forgetting.——No surveillance, no police.
- Under normal circumstances, these nodes will never be visited, but once visited, they will be an emergency.

Restoration:
1. Injection test: regularly inject errors into the Graph and force all error branches to trigger
   (For example: once a week, Chaos test, deliberately failed the README inspection)
2. The error branch must also have a complete log and monitor
3. Unit testing for each error branch
```

- -- **Debug story three: After user confirmation, Agent changed the plan without permission**

```text
Symptoms
User confirms the 4-step release plan generated by Agent. As we move to step 3 ( "Cleaning Changelog" ),
Agent Found some unsubmitted changes in the guit log, which inserted one of its own.
"Submit unsaved changes first'step, resulting in changelog content containing changes that should not be included.

Queries:
1. View execution track → Before step 3, Agent detected dirty working tree
2. Plan-Execute There is a logic in the method:
   "If an abnormal environment is detected, automatically insert the restoration step."
3. User confirmed 4-step plan, but 5-step implementation——User does not know step 5 exists

GEN:
- There's no lock after plan confirmation: the user identified a "scatter" but the implementer used it as a "scatter"
  "Reference Templates
- "Automatically insert steps with too much permission.——It shouldn't be able to change the plan after the user has confirmed it.

Restoration:
1. The program confirmed locking: confirmed plan is immutable.
   Any deviation requires a new request for confirmation
2. If additional steps are found necessary in the course of implementation, suspend and inform users:
   "In the past few years, environmental anomalies have been detected (working changes have not been submitted).
   Recommendation submitted before continuation. Will you allow me to insert this step??"
3. Distinguishing between "small adjustments" (e.g., delay in retry) and "structure changes" (e.g., insertion of new steps)——
   The former are automatically treated, and the latter must be confirmed.
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
If the problem is mostly "missing, falling, not recovering," consider Planning.
If the problem is just "a step tool is wrong," fix the tool mechanism.
```

## 5.8 From drift to removable: One Planning Life Cycle

The following is a series of key differences in the four models, replaying them with a continuous cross-sky story. This is the three iterative versions of the release assistant, from the beginner to the reliable tool.

```text
═══════════════════════════════════════════════════════════════════
V1:Red— Monday 14:00
═══════════════════════════════════════════════════════════════════
│
│  [14:00] User: "Help me do v1.2.0 release preparation."
│
│  Agent Other Organiser
│    Thinking: Users need to prepare for the launch and look at the project structure.
│    Action: ls-la (file listing)
│    Observation: README.md, src/, tests/, CHANGELOG.md
│
│    Think: There's CHANGELOG.md, let me see the content.
│    Action: Cat Changelog.md
│    Observation: (read 200 row changelog history)
│
│    Thinking: Changelog was last updated three months ago. Let me see the latest guit log.
│    Action: Git log-oneline-20
│    Observation: (20 articles exported)
│
│    Thinking: Recently, the committee has feat and fix, which needs to be sorted into changelog.
│    Action: (start editing CHANGELOG.md)……)
│
│    Think: We should check the tests too.
│    Action: npm test
│    Observation: 42 passed, 0 covered
│
│    Think: Test passed. User also mentioned checking README……
│    Action: cat README.md
│    (It's been eight minutes and the user's been impatient.
│
│  Question: Agent deviated at step 1. It didn't understand what steps were needed to make the release ready.
│        It's every step of decision-making, attracted to the content of the document, spent on the changelog editing.
│        A lot of time, and finally there's README and checklist.
│        The user wanted a list, and Agent started changing the file.
│
│  User feedback: "I just want you to create a checklist. How did you start changing changelog??
│             And changelog is not right, it contains unfinished content."
│
═══════════════════════════════════════════════════════════════════
V2:Plan-Execute — Tuesday 10 a.m. (based on user feedback improvements)
═══════════════════════════════════════════════════════════════════
│
│  [10:00] User: "Help me do v1.2.0 release preparation."
│
│  1. Generation plan:
│     Agent No more direct action, but rather a plan.
│
│     ┌─────────────────────────────────────────────────────────┐
│     │ Release Preparation Plan - v1.2.0│
│     │                                                         │
│     │ Step 1. Check README integrity│
│     │   Tools: File Read+ Chapter Validation│
│     │   Acceptance, Quick Start, API,│
│     │         Contributing All four chapters exist.│
│     │                                                         │
│     │ Step 2. Run tests│
│     │   Tools: npm test│
│     │   Accepted and accepted: all test examples passed│
│     │                                                         │
│     │ Step 3. Collapse changelog│
│     │   Tools: guit log+ changelog Templates│
│     │   Dependence: Step 2 Pass (ensure that changes are tested)│
│     │   Receiving and Inspection: Changelog covers all members of this release│
│     │                                                         │
│     │ Step 4. Generate based checklist│
│     │   Tools: checklist templates│
│     │   Dependence: Step 1, 2, 3│
│     │   Receiving and Inspection: checklist overwrite all published entries│
│     └─────────────────────────────────────────────────────────┘
│
│  [10:01] User confirmed: "The plan looks good. But not if it fails.
│           Stop hard.——Tell me which failed, and I'll decide whether to continue."
│
│  2. Implementation:
│     Step 1✅ — README Missing Contributing Chapter but not blocked
│     Step 2❌ — 1 Could not close temporary folder: %s
│
│     Retry Step 2— Still failed.
│
│     According to the user's instructions, Agent does not stop, but reports:
│     "Step 2 Run test: 1 test failed (test memory cleanup on session end).
│      This failed test has nothing to do with this release change. Skip Continue?"
│
│     User: " Skip, continue."
│
│     Step 3✅ — changelog Generated, over 5 committees
│     Step 4✅ — checklist Generated
│
│  3. Final output:
│     ✅ Release ready.
│     ⚠️ Test: 1 known failure (not blocked, recorded)
│     📋 Checklist Include 7 Checkpoints
│
│  User feedback: "This is much better.！The plan is clear, the problem is selective, not one size fits all."
│
═══════════════════════════════════════════════════════════════════
V3:Graph — Wednesday, 15:00 (process solidifiably reusable workflow)
═══════════════════════════════════════════════════════════════════
│
│  After a week of steady operation, the team decided to anchor the release process into a Graph:
│
│  Reason:
│  - Processes issued are implemented at least once a week and steps and branches have stabilized
│  - We need to support the resumption of implementation.——If there is a problem with implementation, the production system should continue from the failure nodes.
│  - Replayable if needed——You can reset the last execution path when the newcomer takes over for release.
│
│  [15:00] Newman's first execution release: "Help me do v1.3.0 release preparation."
│
│  Graph Execution path (automatically record every step):
│    check_readme   ✅ → "README Full."
│    run_tests      ✅ → "42/42 passed"
│    changelog      ✅ → "Changelog Generated
│    checklist      ✅ → "7/7 "Check Item."
│
│  Execution path: check readme → run_tests → changelog → checklist
│
│  [15:30] Second release (REDME has a problem):
│    check_readme   ❌ → FileNotFoundError
│    fix_readme     ✅ → "README Added" (automated jump to fixed node)
│    (Stop, wait for manual inspection)
│
│  Execution path: check readme → fix_readme
│
│  User feedback: "I don't have to say "What if I fail?"——Branch logic is already in place.
│             It's written in Graph. And the execution path can be traced, very reassuring."
│
│  But the price is: it took Graph an afternoon to build this. Team needs to define 6 nodes,
│  8 Side, 3 retry policies——These are not needed by Chain and Plan-Execute.
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
| Chain(5.4.1) | Are the steps fully fixed and without abnormal branches? | Non-critical step failure leads to complete process interruption; users want to skip a step but Chain does not support |
| Router(5.4.2) | Is the classification accurate enough? Is the bottom path secure? | The cataloguing error led to the wrong path being executed; the bottom path became a "massive bin". |
| Plan-Execute(5.4.3) | Are reprogrammed exit conditions reliable? Are you locked after plan confirmation? | Reschedule dead loops;Agent inserts new steps without permission after user confirmation |
| Graph(5.4.4) | Are modelling costs worth paying? Is the error branch tested the same as the main path? | 30 nodes no one can tell the whole story; wrong branch 3 months without trigger, crash |

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
# Python Version
cd examples/course-05-05-planning/python
python3 planning_demo.py

# Node.js Version
cd examples/course-05-05-planning/nodejs
node planning_demo.mjs
```

> **Chapter IV Review.** You now have four perspectives on Agent: scene enhancement (Chapter 1) defines what additional capabilities Agent needs in multiple rounds of interaction; RAG (Chapter 2) solves "what the model doesn't know to look for information"; Memory (Chapter 3) solves "state continuity of cross-session"; and Planning (Chapter) solves "organization and execution of multi-step tasks". But, Agent, there's one more problem that we haven't solved in the face of a complicated mission. **It sees feedback signals, but continues the path down and does not stop to decide on the next step**. This is the next chapter of the question to be answered.

---
