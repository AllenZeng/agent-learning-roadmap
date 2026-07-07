# Chapter 8: Multi-Agent -- from "one person doing the work" to "a team working together"

[Back to Course 5 main document](./course-05-01-scenario-enhancement.md) | [Previous chapter](./course-05-07-human-in-the-loop.md) | [Next chapter](./course-05-09-composition.md)

## Chapter outline

- [8.1 Three hard ceilings of a single Agent](#81-three-hard-ceilings-of-a-single-agent)
  - [8.1.1 Role conflict: creators cannot reliably review their own work](#811-role-conflict-creators-cannot-reliably-review-their-own-work)
  - [8.1.2 Context pressure: too much intermediate reasoning turns into noise](#812-context-pressure-too-much-intermediate-reasoning-turns-into-noise)
  - [8.1.3 Serial bottleneck: independent tasks still have to wait in line](#813-serial-bottleneck-independent-tasks-still-have-to-wait-in-line)
  - [8.1.4 Why "use a stronger model" is not the answer](#814-why-use-a-stronger-model-is-not-the-answer)
- [8.2 What exactly gets split -- the "four differences" in Multi-Agent](#82-what-exactly-gets-split----the-four-differences-in-multi-agent)
  - [8.2.1 Changing the Prompt is not Multi-Agent](#821-changing-the-prompt-is-not-multi-agent)
  - [8.2.2 Four differences: input, tools, goals, and acceptance criteria](#822-four-differences-input-tools-goals-and-acceptance-criteria)
  - [8.2.3 Self-check: how many conditions does your scenario satisfy](#823-self-check-how-many-conditions-does-your-scenario-satisfy)
- [8.3 Reviewer pattern: the simplest entry point into Multi-Agent](#83-reviewer-pattern-the-simplest-entry-point-into-multi-agent)
  - [8.3.1 Pattern skeleton: one executor, one reviewer](#831-pattern-skeleton-one-executor-one-reviewer)
  - [8.3.2 Why independent context works better than "switching roles" in a Prompt](#832-why-independent-context-works-better-than-switching-roles-in-a-prompt)
  - [8.3.3 Replay: single-Agent self-review vs Reviewer review](#833-replay-single-agent-self-review-vs-reviewer-review)
  - [8.3.4 Where the Reviewer pattern fails](#834-where-the-reviewer-pattern-fails)
- [8.4 Supervisor pattern: decompose, dispatch, synthesize](#84-supervisor-pattern-decompose-dispatch-synthesize)
  - [8.4.1 Pattern skeleton: one dispatcher plus multiple workers](#841-pattern-skeleton-one-dispatcher-plus-multiple-workers)
  - [8.4.2 Decomposition quality determines the value of the whole pattern](#842-decomposition-quality-determines-the-value-of-the-whole-pattern)
  - [8.4.3 The cost of merging -- "three Workers finished quickly, then the Supervisor spent longer merging"](#843-the-cost-of-merging----three-workers-finished-quickly-then-the-supervisor-spent-longer-merging)
  - [8.4.4 Where the Supervisor pattern fails](#844-where-the-supervisor-pattern-fails)
- [8.5 Parallel Specialists: one task, multiple pairs of eyes](#85-parallel-specialists-one-task-multiple-pairs-of-eyes)
  - [8.5.1 How it differs from Supervisor: same input, different dimensions](#851-how-it-differs-from-supervisor-same-input-different-dimensions)
  - [8.5.2 Mutually exclusive dimensions are the premise of parallel review](#852-mutually-exclusive-dimensions-are-the-premise-of-parallel-review)
  - [8.5.3 Merge rule: conflicts are not resolved automatically](#853-merge-rule-conflicts-are-not-resolved-automatically)
- [8.6 Agent definition and configuration -- how "different" becomes real](#86-agent-definition-and-configuration----how-different-becomes-real)
  - [8.6.1 Write an Agent definition card before writing the Prompt](#861-write-an-agent-definition-card-before-writing-the-prompt)
  - [8.6.2 Mapping configuration to the four dimensions](#862-mapping-configuration-to-the-four-dimensions)
  - [8.6.3 System Prompt design -- not just "give it a different name"](#863-system-prompt-design----not-just-give-it-a-different-name)
  - [8.6.4 Tool assignment -- whitelists, not "please do not use this"](#864-tool-assignment----whitelists-not-please-do-not-use-this)
  - [8.6.5 Model selection -- not every role needs the strongest model](#865-model-selection----not-every-role-needs-the-strongest-model)
  - [8.6.6 Parameter tuning -- different roles, different parameters](#866-parameter-tuning----different-roles-different-parameters)
  - [8.6.7 Configuration management -- from scattered settings to "configuration as code"](#867-configuration-management----from-scattered-settings-to-configuration-as-code)
- [8.7 Communication protocols -- Agents cannot just ask "what do you think?"](#87-communication-protocols----agents-cannot-just-ask-what-do-you-think)
  - [8.7.1 Why free-form conversation is a disaster](#871-why-free-form-conversation-is-a-disaster)
  - [8.7.2 Design the message format around the collaboration pattern](#872-design-the-message-format-around-the-collaboration-pattern)
  - [8.7.3 From internal message conventions to Agent protocols](#873-from-internal-message-conventions-to-agent-protocols)
- [8.8 Adjudication, stopping, and fallback -- the "traffic rules" of Multi-Agent](#88-adjudication-stopping-and-fallback----the-traffic-rules-of-multi-agent)
  - [8.8.1 Adjudication: who decides when Agents disagree](#881-adjudication-who-decides-when-agents-disagree)
  - [8.8.2 Stopping conditions: no infinite back-and-forth](#882-stopping-conditions-no-infinite-back-and-forth)
  - [8.8.3 Fallback strategy: what if a Worker fails](#883-fallback-strategy-what-if-a-worker-fails)
- [8.9 The real cost -- not just the Token bill](#89-the-real-cost----not-just-the-token-bill)
  - [8.9.1 A sample cost comparison](#891-a-sample-cost-comparison)
  - [8.9.2 Latency amplification: the real cost of message round trips](#892-latency-amplification-the-real-cost-of-message-round-trips)
  - [8.9.3 Long-term cost: trace complexity and handoff difficulty](#893-long-term-cost-trace-complexity-and-handoff-difficulty)
- [8.10 Exercise: make a Supervisor decomposition executable](#810-exercise-make-a-supervisor-decomposition-executable)

---

## 8.1 Three hard ceilings of a single Agent

Before discussing how to design Multi-Agent systems, we need to answer a more basic question: **where exactly does a single Agent get stuck?** If you cannot answer that question clearly, adding Multi-Agent is probably just "architecture for architecture's sake."

The bottleneck of a single Agent is not simply "the model is not smart enough." It is structural. There are three hard ceilings, each corresponding to a different failure mode.

### 8.1.1 Role conflict: creators cannot reliably review their own work

Return to the opening scenario of this chapter. A knowledge assistant finishes an API technical design, and you ask it to review the design from a security perspective. It says "no obvious issues" -- while you immediately spot three security risks.

This is not an attitude problem. It is a mechanism problem. The same Agent produced a large amount of intermediate reasoning while it was in "creation mode": "store the key in plaintext for local development first," "simplify the permission model for now and refine it later." Those thoughts were reasonable trade-offs during creation, but they stayed in the context. When you ask the Agent to switch into "review mode," those thoughts become prior explanations. When it sees a plaintext key, it thinks "this was for developer convenience," instead of "this is a security vulnerability."

Use a human analogy. You spend two hours writing a 3,000-word technical proposal, then someone immediately asks you to "review this proposal strictly from a security perspective." Even if you have security experience, you will instinctively defend your own design. In the same brain, prior commitment is not an attitude problem; it is a cognitive mechanism. Agents behave similarly, except their "prior commitment" appears as tokens already present in the context.

**The structural root cause of role conflict**: the creator optimizes for "complete the design," while the reviewer optimizes for "find the problems." These two goals naturally conflict. If the same context and the same objective function must serve both conflicting goals, the goals compromise with each other, and review turns into a formality.

### 8.1.2 Context pressure: too much intermediate reasoning turns into noise

When a single Agent handles a complex task, the context window accumulates many intermediate artifacts: the first draft, traces of failed attempts, exploratory search results, and temporary notes such as "save this for later."

These artifacts were useful at the moment they were created. But when the Agent needs to judge the final output, the intermediate reasoning becomes **noise**. It consumes context space, distracts attention, and introduces outdated assumptions.

A typical context-pressure scenario looks like this:

```text
Agent context window (simplified):
┌────────────────────────────────────────────────────────────┐
│ System Prompt (500 tokens)                                 │
│ Task: write technical design + security review              │
├────────────────────────────────────────────────────────────┤
│ User message (100 tokens)                                  │
├────────────────────────────────────────────────────────────┤
│ Round 1: tries design A, finds it unsuitable, abandons it    │  ← noise
│          (800 tokens)                                      │
│ Round 2: tries design B and writes part of it (1200 tokens) │  ← partial noise
│ Round 3: completes the first draft of design B (2000 tokens)│  ← useful
│ Search notes: 5 summarized notes about API design           │  ← partial noise
│          (1500 tokens)                                     │
│ Round 4: polishes the design (800 tokens)                   │  ← noise
├────────────────────────────────────────────────────────────┤
│ User: "Now review it from a security perspective."          │
│ Agent must make a security judgment using all the context   │
│ above.                                                     │
│                                                            │
│ Problem: it sees the Round 1 reasoning that said "use       │
│ plaintext for simplicity." During review, that reasoning    │
│ becomes "this was intentional, so it is not a problem."      │
└────────────────────────────────────────────────────────────┘
```

**The structural root cause of context pressure**: a single Agent's context window is a shared pool for all information. Intermediate artifacts from the creation process are mixed with the final output. The Agent cannot reliably distinguish "this is the final decision" from "this was an abandoned attempt." During review, historical information pollutes judgment.

### 8.1.3 Serial bottleneck: independent tasks still have to wait in line

The first two ceilings are quality problems. The third is a speed problem.

Suppose the knowledge assistant receives a research task: "Research the latest practices in four major Agent architecture directions -- Tool Use, Memory, Planning, and Multi-Agent -- and summarize each direction." A single Agent handles it like this:

```text
Timeline (serial execution):
├─ [0:00-1:30] Research Tool Use: retrieve notes + search latest sources + prepare output
├─ [1:30-3:00] Research Memory: retrieve notes + search latest sources + prepare output
├─ [3:00-4:30] Research Planning: retrieve notes + search latest sources + prepare output
├─ [4:30-6:00] Research Multi-Agent: retrieve notes + search latest sources + prepare output
└─ [6:00-7:00] Synthesize the four research outputs into a final report

Total time: about 7 minutes
```

But look closely at those four research tasks. They do not depend on one another. Researching Memory does not require waiting for the Tool Use result. They could run at the same time.

**The structural root cause of the serial bottleneck**: a single Agent has one execution thread. Even when tasks have no dependency on each other, they still run one after another. This is not a model-speed problem. Even if the model reasons faster, the total time for four queued tasks is still the sum of the four tasks.

### 8.1.4 Why "use a stronger model" is not the answer

A natural thought is: when stronger models arrive, will these problems disappear automatically?

No. These three ceilings are **structural problems**, not **capability problems**.

- **Role conflict** is not "the model is not smart enough to review." It is conflicting goals inside the same context. A stronger model may be better at switching between goals, but as long as creation and review share one context, prior explanations will soften the review standard.
- **Context pressure** is not "the model's context window is too small." It is an information-structure problem. A larger context window can hold more noise; it does not solve the structural flaw that intermediate reasoning can contaminate final judgment.
- **Serial bottleneck** has even less to do with model capability. A single thread is still a single thread.

That is the fundamental reason Multi-Agent exists: when the **structure** of a single Agent, rather than its raw capability, becomes the bottleneck, we need multiple instances, multiple contexts, and multiple tool sets to break through those structural limits.

---

## 8.2 What exactly gets split -- the "four differences" in Multi-Agent

Once we understand the ceilings of a single Agent, the next step is not "define Agent roles." The next step is to clarify: **what does Multi-Agent actually split?**

### 8.2.1 Changing the Prompt is not Multi-Agent

The easiest mistake is to treat "writing System Prompts" as "creating Agents." You define three roles -- researcher, engineer, reviewer -- write a System Prompt for each role, and ask the same model to play them in sequence. That is not Multi-Agent. That is **role-playing**.

The essential difference between role-playing and Multi-Agent:

```text
"Fake" Multi-Agent (changing the Prompt):
┌─────────────────────────────────────────────────────┐
│ Same LLM instance                                   │
│ Same context window                                 │
│ Same tool set                                       │
│                                                     │
│ Round 1: System = "You are a researcher"            │
│          → produces research report                 │
│ Round 2: System = "You are an engineer"             │
│          → sees research report + all intermediate   │
│            reasoning → produces technical design     │
│ Round 3: System = "You are a reviewer"              │
│          → sees technical design + research report   │
│            + all intermediate reasoning              │
│          → "no obvious issues"                      │
│                                                     │
│ The three roles share the same brain, the same       │
│ memory, and the same tools. The "reviewer" sees all  │
│ thoughts from the "researcher" and "engineer,"       │
│ including compromises such as "simplify this for     │
│ now and refine it later."                            │
└─────────────────────────────────────────────────────┘

"Real" Multi-Agent (independent instances):
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Agent A:         │  │ Agent B:         │  │ Agent C:         │
│ Researcher       │  │ Engineer         │  │ Reviewer         │
│                 │  │                 │  │                 │
│ Context:         │  │ Context:         │  │ Context:         │
│ - research task  │  │ - design task    │  │ - review criteria│
│ - search results │  │ - final research │  │ - final design   │
│                 │  │   report         │  │ - original reqs  │
│ Tools:           │  │                 │  │                 │
│ - search         │  │ Tools:           │  │ Tools:           │
│ - retrieve notes │  │ - write files    │  │ - read files     │
│                 │  │ - read files     │  │   (read-only)    │
│ Cannot see:      │  │                 │  │ - security scan  │
│ - engineer trace │  │ Cannot see:      │  │                 │
│ - reviewer       │  │ - researcher's   │  │ Cannot see:      │
│   judgment       │  │   intermediate   │  │ - researcher     │
│                 │  │   reasoning      │  │   reasoning      │
│                 │  │ - reviewer       │  │ - engineer       │
│                 │  │   judgment       │  │   compromises    │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

The key difference is not how beautifully the Prompt is written. The key difference is that **each Agent sees different things and can do different things**.

### 8.2.2 Four differences: input, tools, goals, and acceptance criteria

Real Multi-Agent splits work across four dimensions. Take the knowledge assistant scenario "write a technical design + perform a security review" as an example:

| Dimension | Single Agent self-review | Multi-Agent: Author + Reviewer |
|---|---|---|
| **Different input** | Author and Reviewer are the same context. Reviewer "sees" the Author's intermediate reasoning and compromises. | Author context contains requirements, retrieved notes, and writing tools. Reviewer context contains **only** the final design + review criteria. It cannot see the Author's drafts or "simplify now, refine later" reasoning. |
| **Different tools** | Same tool set: it can both write files and run security scans. | Author can write files and retrieve notes. Reviewer can only read files and run security scans. It **cannot write**, so the reviewer cannot quietly "fix it and approve it." |
| **Different goals** | "Complete the user's task" -- vague, with subgoals compromising each other. | Author goal: produce a technical design that satisfies the requirements. Reviewer goal: find every issue that violates the security standard. **The goals do not compromise with each other.** |
| **Different acceptance criteria** | "If the user thinks it is okay, it is okay" -- no objective standard. | Author standard: the design covers the requirements. Reviewer standard: every checklist item passes; any FAIL means the whole review is REJECT. |

**At least two of these four dimensions must differ for Multi-Agent to be worth using.** If two Agents have the same input, the same tools, the same goal, and the same acceptance criteria, then no matter what names you give them, they are essentially the same Agent. You are only wasting tokens and latency.

A minimal decision rule: **if you cannot explain what the two Agents see differently, you probably do not need two Agents.**

### 8.2.3 Self-check: how many conditions does your scenario satisfy

Before introducing Multi-Agent, answer these questions one by one:

```text
□ Role conflict: are there two roles whose goals naturally conflict?
   Examples: creator vs reviewer, optimizer vs security assessor,
   salesperson vs risk analyst.
   If there is no natural conflict, a single Agent with a clearer Prompt
   is usually enough.

□ Need for independent context: is one role's intermediate reasoning noise
   or necessary information for another role?
   Examples: debugging traces from implementation are noise for security
   review; compromises made during design discussion are noise for final
   acceptance.
   If intermediate reasoning is useful to every role, you do not need to
   split context.

□ Tool permission separation: are there operations that should not be
   handled by the same Agent?
   Examples: approving deployment vs executing deployment, writing code vs
   merging to main, generating invoices vs approving invoices.
   If one Agent can safely perform every operation, you do not need to split.

□ Parallelism: are there independent subtasks that can run at the same time?
   Examples: researching four independent directions, analyzing three
   independent modules, pulling data from five sources in parallel.
   If the tasks have strict sequential dependencies, parallel value is zero.

□ Perspective diversity: do you need to examine the same problem from
   different positions, assumptions, or risk preferences?
   Example: a technical design needs cost, security, and maintainability
   review at the same time.
   If one perspective covers all concerns, you do not need multiple
   perspectives.
```

**Entry rule**: only seriously consider Multi-Agent when at least two items are true. If only one item is true, there is usually a simpler solution -- a better Prompt, narrower tool permissions, or a predefined checklist -- that can achieve a similar result.

---

## 8.3 Reviewer pattern: the simplest entry point into Multi-Agent

Reviewer is the "Hello World" of Multi-Agent. It only needs two Agents, the communication pattern is simple, and its value is easy to measure. If you cannot make Reviewer work, do not jump to Supervisor, Debate, or Graph Collaboration.

It solves exactly one problem: **the executor cannot impartially review its own output.**

### 8.3.1 Pattern skeleton: one executor, one reviewer

```text
Executor Agent                              Reviewer Agent
┌──────────────────────────┐              ┌──────────────────────────┐
│ System: technical design │              │ System: security reviewer │
│ writer                   │              │                          │
│                          │              │ Tools:                   │
│ Tools:                   │   final      │  - read files only        │
│  - write files           │   output     │  - retrieve security docs │
│  - retrieve notes        │─────────────►│  - checklist verification │
│  - web search            │              │                          │
│                          │   review     │ Context:                 │
│ Context:                 │◄─────────────│  - final output only      │
│  - requirements          │   feedback   │  - review checklist       │
│  - retrieved notes       │              │  - security standards     │
│  - drafts and reasoning  │              │                          │
│    from creation         │              │ Goal: find all security   │
│                          │              │ issues                    │
│ Goal: complete the       │              │ Acceptance: every         │
│ technical design         │              │ checklist item passes     │
│ Acceptance: design       │              │                          │
│ covers requirements      │              │                          │
└──────────────────────────┘              └──────────────────────────┘
```

Core skeleton code:

```python
# Reviewer pattern: minimal Multi-Agent, 2 Agents + structured review
class ReviewerPattern:
    """Executor produces output → Reviewer checks it → fix or escalate."""

    def __init__(self, executor: Agent, reviewer: Agent):
        self.executor = executor
        self.reviewer = reviewer

    def run(self, task: str, criteria: list[dict]) -> dict:
        """
        task: user task description
        criteria: review checklist, where each item is verifiable
          [{"id": "C1", "check": "Are all user inputs length-validated?",
            "how_to_verify": "Inspect parameter declarations in API endpoint definitions"},
           {"id": "C2", "check": "Are API keys stored in environment variables?",
            "how_to_verify": "Search config files for key= or secret= literals"},
           ...]
        """
        # Step 1: Executor produces the draft
        draft = self.executor.run(task)

        for round_num in range(2):  # at most two revision rounds
            # Step 2: Reviewer reviews
            # Key: reviewer only receives the final output and review criteria,
            # not the executor's intermediate reasoning.
            review = self.reviewer.run(
                task="Review the following output against the checklist. "
                     "For each item, return a concrete pass/fail judgment and evidence.",
                context={
                    "original_requirement": task,
                    "artifact": draft.output,
                    "criteria": criteria
                }
            )

            if review.verdict == "approved":
                return {
                    "status": "approved",
                    "output": draft.output,
                    "review_rounds": round_num + 1,
                    "review_trace": review
                }

            # Step 3: Executor fixes the output
            # Key: pass specific issues, not the reviewer's subjective judgment.
            draft = self.executor.run(
                task=task,
                fix_instructions=review.issues  # concrete issue list, not "poor overall quality"
            )

        # Still not approved after two rounds: mark as disputed and escalate to human adjudication.
        return {
            "status": "disputed",
            "output": draft.output,
            "unresolved_issues": review.issues,
            "message": "Still not approved after two revision rounds; human adjudication is required."
        }
```

> **Design point**: Executor and Reviewer use independent LLM instances: different System Prompts, different tool sets, and different context windows. `fix_instructions` passes only the concrete issues found by Reviewer, such as "line 3 lacks input length validation," not subjective evaluation such as "overall quality is poor." Executor should revise based on facts, not be steered by another model's subjective tone. The two-round limit is a protection mechanism. The marginal value of a third revision round usually does not justify the communication cost and decision fatigue.

### 8.3.2 Why independent context works better than "switching roles" in a Prompt

The most important mechanism in the Reviewer pattern is **independent context**. It is not "make the model think from another angle." If the same context is used, the prior information is still there. Independent context means Reviewer **physically cannot see** Executor's intermediate reasoning.

Specifically, Reviewer cannot see these items:

| Information in Executor context that Reviewer does not receive | Why Reviewer should not see it |
|---|---|
| "For local development convenience, store the key in plaintext first." | This sentence makes Reviewer reinterpret "plaintext key" from "security vulnerability" into "intentional temporary design," softening the review. |
| "Simplify the permission model to one admin role first; refine later." | After seeing this explanation, Reviewer may stop marking "lack of least privilege" as FAIL. |
| The first two abandoned drafts out of three drafts | Noise. They are unrelated to the final design but may confuse Reviewer's understanding of the final structure. |
| Executor's uncertainty during writing, such as "not sure here, leave it for now" | This can create unnecessary doubt or cause Reviewer to miss the real defect. |

**Independent context is intentional information asymmetry.** Executor knows more than Reviewer, but some of that information should not be visible to Reviewer because it would bias judgment. This is the same principle as blind review in the real world. Reviewers are blinded to author identity not because of capability limits, but because the system design blocks biasing information and makes judgment more objective.

### 8.3.3 Replay: single-Agent self-review vs Reviewer review

Now compare the knowledge assistant task "write a technical design + security review" end to end.

```text
═══════════════════════════════════════════════════════════════════
Task: write a technical design for an API module and review it from
a security perspective
═══════════════════════════════════════════════════════════════════

Approach 1: single Agent self-review
┌─────────────────────────────────────────────────────────────────┐
│ [10:00] Agent writes the design (35 seconds)                     │
│         Output: API design document with endpoint definitions,    │
│         data flow, and configuration notes                        │
│                                                                 │
│ [10:01] User: "Now review it from a security perspective."        │
│         Agent: "After review, this design has no obvious          │
│         security issues."                                        │
│                                                                 │
│         Four hidden issues missed by the review:                  │
│         ① /api/data endpoint has no input length limit            │
│         ② API key is written in plaintext in config.yaml          │
│         ③ Permission model has only one role, admin; every        │
│           operation requires admin                                │
│         ④ requirements.txt does not pin third-party dependency    │
│           versions                                               │
│                                                                 │
│         Why were they missed? The Agent's intermediate reasoning  │
│         while writing included:                                  │
│         - "Use plaintext for local development convenience."      │
│         - "Refine the permission model later."                    │
│         During review, these thoughts became "explanations" and   │
│         weakened the review standard.                             │
└─────────────────────────────────────────────────────────────────┘

Approach 2: Reviewer pattern
┌─────────────────────────────────────────────────────────────────┐
│ [10:00] Author Agent writes the design (35 seconds)              │
│         Output: same as above                                    │
│                                                                 │
│ [10:01] Reviewer Agent receives:                                 │
│         - final design text (without Author's intermediate        │
│           reasoning)                                             │
│         - review checklist (4 items, each with a concrete verify  │
│           method)                                                │
│         - security standard document (as reference)               │
│         - tools: read files, retrieve standards, check item by    │
│           item                                                   │
│                                                                 │
│         Reviewer checks item by item:                            │
│         ┌─────────────────────────────────────────────────────┐  │
│         │ C1: Input validation                                │  │
│         │   verify: inspect parameter declarations in API      │  │
│         │   endpoint definitions                              │  │
│         │   result: /api/data input has no length limit → FAIL │  │
│         │   evidence: api_schema.yaml line 12                  │  │
│         │                                                     │  │
│         │ C2: Key management                                  │  │
│         │   verify: search config files for key=/secret=       │  │
│         │   literals                                          │  │
│         │   result: config.yaml line 8 api_key: "sk-abc123"    │  │
│         │   → FAIL                                            │  │
│         │   evidence: config.yaml line 8                       │  │
│         │                                                     │  │
│         │ C3: Permission model                                │  │
│         │   verify: check for non-admin role definitions       │  │
│         │   result: only admin exists; no read/write split     │  │
│         │   → FAIL                                            │  │
│         │   evidence: permissions.py lines 3-5                 │  │
│         │                                                     │  │
│         │ C4: Dependency security                             │  │
│         │   verify: check whether requirements.txt pins        │  │
│         │   versions                                          │  │
│         │   result: dependencies use >= instead of ==          │  │
│         │   → FAIL                                            │  │
│         │   evidence: full requirements.txt                    │  │
│         └─────────────────────────────────────────────────────┘  │
│                                                                 │
│         verdict: rejected (4/4 FAIL)                            │
│         issues: [                                               │
│           {id:"C1", desc:"/api/data lacks input length limit",   │
│            location:"api_schema.yaml:12", suggestion:"add        │
│            max_length"},                                        │
│           {id:"C2", desc:"API key stored in plaintext",          │
│            location:"config.yaml:8", suggestion:"use an          │
│            environment variable"},                              │
│           ...                                                   │
│         ]                                                       │
│                                                                 │
│ [10:02] Author receives review feedback and fixes each item      │
│         (25 seconds)                                            │
│                                                                 │
│ [10:03] Reviewer runs second review:                             │
│         C1: PASS  C2: PASS  C3: PASS  C4: PASS                  │
│         verdict: approved                                       │
│                                                                 │
│ Comparison:                                                     │
│ Single-Agent self-review: missed 4 security risks and claimed    │
│ "no obvious issues"                                             │
│ Reviewer pattern: found and fixed all 4 issues                   │
│ Extra cost: +1 minute (Reviewer review + Author revision)        │
│ + $0.04 token cost                                              │
│ Benefit: from "shipping with security holes" to "passed the      │
│ security checklist"                                             │
═══════════════════════════════════════════════════════════════════
```

### 8.3.4 Where the Reviewer pattern fails

The Reviewer pattern is useful, but only under specific conditions. It has four failure boundaries:

**Boundary 1: it fails when the checklist is vague.** If the review standard is just "check whether the design is secure," Reviewer will produce the same kind of output as single-Agent self-review: "no obvious issues." The checklist must be concrete, itemized, and tied to explicit verification methods.

```text
Vague review criterion:
  "Check whether the design is secure"
  → Reviewer output: "Overall secure, no obvious issues"

Concrete review criteria:
  "1. Does every user input have length and type validation?
      Verification method: inspect every parameter declaration in the API schema.
   2. Are secrets stored in environment variables or a secret-management service?
      Verification method: grep config files for key= patterns.
   3. Are there roles other than admin?
      Verification method: inspect the role list in the permission module.
   4. Are third-party dependencies pinned?
      Verification method: inspect version declarations in requirements.txt."
```

**Boundary 2: it fails when Reviewer has no independent verification tools.** If Reviewer can only "read the design and judge it," it is not fundamentally different from single-Agent self-review. Reviewer needs verification tools independent of Executor: read original config files rather than Executor's description of them, run linters, retrieve original security standards. Core principle: **Reviewer verifies what is real, not what Executor claims.**

**Boundary 3: it can deadlock when Reviewer is too strict.** If every review suggestion is treated as "must fix," Executor fixes one round, Reviewer discovers new issues -- new issues, not old issues left unfixed -- then Executor fixes again, Reviewer discovers more, and approval never happens. The correction is to separate "must fix" from "should improve"; keep must-fix items under five; recommendations should not block approval.

**Boundary 4: Executor learns to anticipate the checklist.** This is the most subtle failure mode. After many reviews, Executor learns to add statements that look like security measures: "this module follows security best practices," "all inputs are fully validated." But those statements do not correspond to actual implementation. Reviewer sees the statements and marks "security measures mentioned" as PASS. In reality, nothing was implemented. The fix is to change the checklist from "is it mentioned" to "is it implemented." Do not check "does the design discuss key management"; check "are keys actually stored in environment variables, verified by grep."

---

## 8.4 Supervisor pattern: decompose, dispatch, synthesize

Reviewer solves a **quality** problem: the executor needs independent review. But when the task itself can naturally be split into independent subtasks, a single Agent runs into a **speed** problem: the serial bottleneck.

The Supervisor pattern uses one scheduling Agent to decompose and synthesize, while multiple Worker Agents execute in parallel.

### 8.4.1 Pattern skeleton: one dispatcher plus multiple workers

```text
Supervisor Agent                             Worker Agents
┌─────────────────────────┐       ┌─────────────────────────────────┐
│ Receives user task       │       │ Worker 1: research Tool Use      │
│                         │       │  - independent context            │
│ Decomposes into N        │       │  - independent retrieval tools    │
│ subtasks:               │───┬───│  - output: structured findings    │
│  - define boundaries     │   │   │                                 │
│  - specify output format │   │   │ Worker 2: research Memory        │
│  - assign Worker         │   │   │  - independent context            │
│                         │   │   │  - independent retrieval tools    │
│ Synthesizes N results:   │   │   │  - output: structured findings    │
│  - deduplicate           │   │   │                                 │
│  - identify conflicts    │◄──┴──│ Worker 3: research Planning       │
│  - mark missing data     │       │  ...                            │
│  - produce final output  │       │ Worker 4: research Multi-Agent   │
└─────────────────────────┘       └─────────────────────────────────┘
```

Core skeleton code:

```python
class SupervisorPattern:
    """Supervisor decomposes task → Workers run in parallel → Supervisor synthesizes."""

    def __init__(self, supervisor: Agent, workers: dict[str, Agent]):
        self.supervisor = supervisor
        self.workers = workers

    def run(self, task: str) -> dict:
        # Step 1: Supervisor decomposes the task.
        # The decomposition must include boundaries, output template, and Worker assignment.
        plan = self.supervisor.decompose(task)
        # plan.subtasks = [
        #   {"id": "T1", "topic": "Latest practices in Tool Use",
        #    "worker": "researcher_1",
        #    "scope": "design patterns, failure modes, framework comparison",
        #    "exclude": "do not cover Tool Use inside Multi-Agent collaboration; Worker 4 covers that",
        #    "output_template": "## Tool Use\n### Key findings\n- ...\n### Failure modes\n- ...\n### Sources\n- ..."},
        #   ...
        # ]

        # Step 2: Execute in parallel.
        results = parallel_execute(
            plan.subtasks,
            lambda st: self.workers[st.worker].execute(
                task=f"Research {st.topic}. Scope: {st.scope}. Exclude: {st.exclude}. "
                     f"Output format: {st.output_template}",
                tools=["search_notes", "web_search"]
            )
        )
        # A Worker that fails or times out returns None and does not block other Workers.

        # Step 3: Supervisor synthesizes.
        # Key operations: deduplicate, identify conflicts, mark missing data, synthesize.
        final = self.supervisor.synthesize(
            task=task,
            worker_results=results,
            instructions="""
            Synthesis rules:
            1. If two Workers give conflicting conclusions on the same topic,
               mark "conflict exists" instead of choosing automatically.
            2. If a Worker times out or fails, mark that direction as "data missing"
               in the report.
            3. Deduplicate: merge identical findings and note which Workers supplied them.
            4. Organize the final output into a unified structure; do not paste Worker
               outputs directly.
            """
        )
        return final
```

### 8.4.2 Decomposition quality determines the value of the whole pattern

The most underestimated step in the Supervisor pattern is **decomposition**. Many implementations simplify it to "ask the LLM to split the task into several parts" and then discover that Worker outputs overlap heavily, use inconsistent formats, and cannot be merged.

Good decomposition needs four things:

**1. Clear boundaries, including `exclude`**

It is not enough to say "you research A, you research B." You also need to say "do not touch this part."

```text
Poor decomposition:
  Worker 1: research Tool Use
  Worker 2: research Multi-Agent
  → Both Workers write about "Tool Use inside Multi-Agent"
  → 30% content overlap

Good decomposition:
  Worker 1: research Tool Use design patterns, failure modes, and framework implementations
            exclude: do not cover the role of Tool Use in Multi-Agent collaboration
            (covered by Worker 4)
  Worker 2: research Multi-Agent collaboration patterns, communication protocols,
            and failure modes
            exclude: do not cover Tool Use mechanisms inside a single Agent
            (covered by Worker 1)
```

**2. A unified output template**

Every Worker must output in the same structure; otherwise Supervisor cannot merge automatically.

```text
Output template (shared by all Workers):
## {Research direction}
### Key findings
- Finding 1 (1-2 sentences + source citation)
- Finding 2
### Failure modes
- Common failure 1 (symptom + cause + correction direction)
### Recommended practices
- Practice 1 (applicable scenarios + non-applicable scenarios)
### Source citations
- [Source 1](link or note path)
```

**3. Worker capability fit**

Not every Worker should use the same model. Research Workers may need strong retrieval capability, such as web search and long context. Analysis Workers may need stronger reasoning. Assign the right task to the right Worker.

**4. Granularity control**

If you split too finely, such as 10 subtasks, communication and synthesis cost can exceed execution benefit. If you split too coarsely, such as 2 subtasks, parallelism is too weak. A practical rule: **number of subtasks = min(number of independent parallel dimensions, number of available Workers, 5)**. Beyond five subtasks, marginal gains usually do not cover coordination cost.

### 8.4.3 The cost of merging -- "three Workers finished quickly, then the Supervisor spent longer merging"

This is the classic failure scene for the Supervisor pattern:

```text
Scenario: user asks, "Research the latest practices in Agent Memory."
Supervisor decomposes into 3 subtasks → 3 Workers run in parallel

Timeline:
├─ Worker 1 researches "short-term memory" (45 seconds)
├─ Worker 2 researches "long-term memory" (50 seconds)
├─ Worker 3 researches "Memory frameworks" (40 seconds)
│  Parallel time: 50 seconds ✓ faster than serial execution
│
├─ Supervisor starts merging (60 seconds) ← the problem is here
│  Why? Because the three Worker outputs look like this:
│  - Worker 1 outputs 3 pages of Markdown (overview + detailed analysis + code examples)
│  - Worker 2 outputs 5 bullet points + 1 table
│  - Worker 3 outputs a list of 8 frameworks with no analysis
│  The formats are different, the structures are different, and the coverage overlaps heavily.
│  Supervisor cannot "merge automatically." It is effectively asking the LLM to
│  re-synthesize three reports. If one Agent had done this integration from the
│  start, it might have taken only 70 seconds.
│
├─ Total time: 50 seconds (parallel execution) + 60 seconds (merge) = 110 seconds
│  Serial time: about 120 seconds (3 directions × 40 seconds + natural synthesis 10 seconds)
│  Parallel benefit: almost zero. Complexity tripled to save 10 seconds.
└─

Root cause: no output template was specified during decomposition. Each Worker output
according to its own interpretation, so merge cost erased the parallel benefit.

Fix:
1. Force a unified output template during decomposition: structure, fields, length limit.
2. Limit each Worker output to 300 words; forbid "overview" and "background" sections.
3. Worker outputs only extracted information, not synthesis or summary. Synthesis belongs to Supervisor.
```

**The core lesson**: the value of parallelism is not "Workers run fast." It is **"Worker outputs can be directly composed without asking the LLM to understand and rewrite everything."** If the merge step requires the LLM to read all Worker outputs and "write the report again," you may as well let one Agent write it from the beginning.

### 8.4.4 Where the Supervisor pattern fails

| Failure mode | Symptom | Root cause | Fix |
|---|---|---|---|
| Ambiguous decomposition boundaries | Worker outputs overlap by 30% | No `exclude` scope defined during decomposition | Attach a clear `exclude` statement to every subtask |
| Inconsistent formats | Worker outputs cannot be merged automatically; Supervisor must re-synthesize | No output template | Force an output template during decomposition, while allowing Workers to fill the template flexibly |
| Worker failure causes incomplete report | Worker 2 times out, but Supervisor pretends all four directions are complete | Synthesis rules do not mark "data missing" | Force synthesis rule: failed Worker's direction is marked "data missing; reason: {timeout/error}" |
| Parallelism becomes serial | Decomposition itself takes 30 seconds because LLM is repeatedly asked to adjust the plan | Decomposition depends too heavily on LLM decisions | Use predefined decomposition templates for common tasks; ask LLM to adjust only for unusual cases |
| Supervisor becomes the bottleneck | Five Workers all wait for Supervisor's decomposition before starting | Decomposition and dispatch are serial | For standard tasks, use a predefined cached decomposition plan and skip LLM decomposition |

---

## 8.5 Parallel Specialists: one task, multiple pairs of eyes

In Supervisor, each Worker handles a different task. Parallel Specialists is a variation: **the same task is analyzed by multiple experts from different dimensions at the same time, then merged.**

### 8.5.1 How it differs from Supervisor: same input, different dimensions

```text
Supervisor pattern:                    Parallel Specialists pattern:

Task A → Worker 1                      Same task
Task B → Worker 2                           │
Task C → Worker 3                 ┌─────────┼─────────┐
                                  ▼         ▼         ▼
Different tasks, different        Specialist A  Specialist B  Specialist C
Workers                           (correctness) (security)    (performance)
                                      │         │         │
                                      └─────────┼─────────┘
                                                ▼
                                            merged result

Different dimensions, same input
```

Suitable scenarios: a piece of code needs correctness, security, and performance review at the same time. A design needs evaluation from technical feasibility, cost, and maintainability perspectives. An answer needs simultaneous checks for factual accuracy, logical completeness, and clarity.

### 8.5.2 Mutually exclusive dimensions are the premise of parallel review

The core premise of this pattern is that **dimensions do not depend on each other**. If performance analysis first needs the conclusion from correctness analysis, it cannot run in parallel; correctness must run before performance.

Dimension design must satisfy two conditions:

1. **Mutual exclusivity**: each dimension has a non-overlapping focus. If both "correctness" and "security" analyze input validation, 60% of their output will repeat.
2. **Independence**: each dimension can reach a conclusion from the input plus its own focus, without waiting for other dimensions.

```python
class ParallelSpecialists:
    """Multiple experts analyze different dimensions of the same task in parallel."""

    def __init__(self, specialists: dict[str, Agent]):
        self.specialists = specialists

    def run(self, task: str, dimensions: list[dict]) -> dict:
        """
        dimensions = [
          {"name": "correctness", "agent": "code_reviewer",
           "focus": "logic errors, boundary conditions, exception handling, state consistency",
           "exclude": "do not analyze security vulnerabilities or performance bottlenecks"},
          {"name": "security", "agent": "security_auditor",
           "focus": "injection risk, secret leakage, permission bypass, sensitive data exposure",
           "exclude": "do not analyze logic errors, even if they may cause undefined behavior"},
          {"name": "performance", "agent": "perf_analyzer",
           "focus": "time complexity, memory usage, I/O bottlenecks, caching strategy",
           "exclude": "do not analyze correctness or security impact"},
        ]
        """
        # Run in parallel.
        results = parallel_execute(
            dimensions,
            lambda d: self.specialists[d["agent"]].analyze(
                task=task,
                focus=d["focus"],
                exclude=d["exclude"]
            )
        )

        # Merge: deduplicate + mark sources + detect conflicts.
        return self.merge(results, dimensions)

    def merge(self, results: list[dict], dimensions: list[dict]) -> dict:
        """Merge multi-dimensional analysis results."""
        all_findings = []
        conflicts = []

        for i, result in enumerate(results):
            for finding in result.findings:
                finding["source_dimension"] = dimensions[i]["name"]
                all_findings.append(finding)

        # Deduplicate: same location + same issue description → merge into one finding,
        # while marking that it came from multiple dimensions.
        deduped = self._deduplicate(all_findings)

        # Conflict detection: if two dimensions give contradictory judgments
        # about the same location.
        # Example: Specialist A says "this design is safe."
        #          Specialist B says "this has injection risk."
        # → Do not resolve automatically; mark as a conflict.
        conflicts = self._detect_conflicts(deduped)

        return {
            "findings": deduped,
            "conflicts": conflicts,  # marked, not automatically resolved
            "dimension_summary": {
                d["name"]: len(r.findings) for d, r in zip(dimensions, results)
            }
        }
```

### 8.5.3 Merge rule: conflicts are not resolved automatically

The most dangerous moment in Parallel Specialists is **merging**. When two experts make contradictory judgments, the easiest mistake is to let an LLM choose automatically -- for example, "take the majority opinion" or "let Supervisor decide."

But automatic resolution hides the real issue. If one expert says "safe" and another says "vulnerable," at least one expert's analysis is wrong. Maybe one focus definition is not clear enough. Maybe one expert lacks key context. Automatically choosing the "majority" only covers up the problem.

**Merge rules**:

1. **Identical findings are deduplicated automatically**: if two experts point to the same issue, with the same location and issue type, merge it into one finding and note both source dimensions.
2. **Contradictory judgments are not resolved automatically**: mark "security-dimension conflict; human review required" and include the concrete reasoning from both experts.
3. **Every finding records its source**: each finding says which dimension produced it, so the reader knows the perspective behind the finding.

Common failures in this pattern:

| Failure mode | Symptom | Fix |
|---|---|---|
| Dimensions are not mutually exclusive | "Correctness" and "security" experts produce 60% overlapping output | Define a clear `focus` and `exclude` scope for each dimension |
| Conflict is lost during merge | Expert A says safe, Expert B says risky, and merge keeps A | Merge rule must say: mark conflicts, do not resolve them |
| Too many parallel experts | 8 experts are launched and API concurrency limits are triggered | Keep dimension count <= 5; group dimensions when there are more than 5 |
| One expert is too "soft" | Performance expert always outputs "no obvious performance issue" | Check whether that expert's `focus` contains concrete enough checklist items |

---

## 8.6 Agent definition and configuration -- how "different" becomes real

Section 8.2 explained the four dimensions that Multi-Agent splits: different input, tools, goals, and acceptance criteria. Sections 8.3 to 8.5 covered the structure of three collaboration patterns. But structural design only answers "how Agents are organized." It does not answer the earlier question: **how should each Agent itself be configured so that they are truly different?**

### 8.6.1 Write an Agent definition card before writing the Prompt

Many teams start Multi-Agent design by opening an editor and writing Prompts:

```text
You are a researcher.
You are an engineer.
You are a reviewer.
```

That is too early. Prompt is part of Agent configuration, but it is not the Agent definition itself. What you should write first is an **Agent definition card**. It is like a job description and also like a runtime configuration checklist. It keeps responsibility, input, tools, model, parameters, output protocol, and failure handling in one place, so you can judge whether this Agent is truly different from other Agents.

Here is an example definition card for a Reviewer Agent:

```yaml
agent: security_reviewer
responsibility: review security risks only; do not modify artifacts
input:
  - final_artifact
  - original_requirement
  - security_checklist
excluded_input:
  - author_private_trace
  - draft_history
  - author_self_justification
tools:
  - read_file
  - run_security_scan
model:
  capability: instruction_following
  reason: needs stable checklist execution and structured output; does not need high creativity
parameters:
  temperature: 0
  max_tokens: 1000
output_schema: ReviewResponse
acceptance:
  - every FAIL must include location and evidence
  - when uncertain, do not guess pass; mark insufficient_information
fallback:
  - after two failed revision rounds, enter human_review
```

The most important part of this card is not the `agent` name. It is the set of constraints:

- **Responsibility boundary**: what it owns and what it does not own. Reviewer reviews only; it does not modify. Supervisor decomposes and synthesizes only; it does not do Worker research.
- **Input boundary**: what it can see and what it cannot see. Reviewer cannot see Author drafts or self-justification. That is the premise of independent review.
- **Tool boundary**: which tools it can call. A Reviewer without `write_file` permission cannot quietly edit while reviewing.
- **Model boundary**: what capability it needs. Not every Agent should use the strongest model; model capability should match responsibility.
- **Output boundary**: what schema it must use. Without structured output, the next Agent has to re-interpret a natural-language paragraph.
- **Failure boundary**: what happens when it fails. Retry, downgrade, switch model, hand off to a human -- all must be defined in advance.

If you cannot write an Agent definition card, the Agent has not been designed clearly enough. Continuing to write Prompts at that point only creates a text actor that looks like a role but has no real boundaries.

### 8.6.2 Mapping configuration to the four dimensions

| Dimension | Engineering configuration method | Author + Reviewer example |
|---|---|---|
| **Different input** | Context-scope declaration in System Prompt + runtime information filtering | Author context contains retrieved notes, creation history, and drafts. Reviewer context receives only the final design + review criteria; all Author intermediate reasoning is filtered out. |
| **Different tools** | Agent-level whitelist in the tool registry | Author registers `write_file`, `search_notes`, `web_search`. Reviewer only registers `read_file`, `run_security_scan`; no write permission. |
| **Different goals** | Task definition in System Prompt + success-criteria wording | Author: "produce a technical design that satisfies requirements and covers every requirement point." Reviewer: "find every issue that violates the security standard and provide location and evidence item by item." |
| **Different acceptance criteria** | Output Schema constraints + stopping conditions | Author output has no mandatory schema. Reviewer output must be `{verdict, checks[], issues[]}`, and `verdict` only has `approved` or `rejected`. |

The table is a quick mapping. Next we will unpack each configuration dimension and common mistake.

### 8.6.3 System Prompt design -- not just "give it a different name"

The most common weak version looks like this:

```text
# Author
"You are a technical design writer. Write a complete technical design based on the requirements."

# Reviewer
"You are a security reviewer. Review the security of this technical design."
```

These two Prompts differ only in role name and verb. They do not define what Reviewer should focus on, what criteria it should use, what the output must contain, or what to do when uncertain. The result is that Reviewer is no different from single-Agent self-review. It only knows it is called "reviewer"; it does not know how a reviewer should behave.

**An effective System Prompt must define five elements.** Here is a Reviewer Agent example:

```text
# Reviewer Agent — System Prompt structure

## 1. Identity and responsibility scope: what you own and what you do not own
"You are a security reviewer. You only review technical designs from a security perspective.

You focus on: input validation, key management, permission model, dependency security,
and data protection.
You do not focus on: technical feasibility, code quality, architecture design,
or performance optimization.
Those are owned by other roles. Do not mention them in your review report."

## 2. Input description: what you can see and what you cannot see
"You will receive the final version of a technical design.

You will not see: drafts, discussion records, or reasoning about compromises made
during authoring.
You must judge only from the final design text and the review criteria.
If the design says something like 'for development convenience, use plaintext here
for now,' do not treat it as a 'reasonable temporary solution.' Treat it as a
security vulnerability.
Your judgment must not be softened by the author's intention."

## 3. Review criteria: itemized and verifiable
"You must check the following criteria item by item. Each criterion includes a
verification method. You must actually perform the verification, not judge only
from wording in the design.

C1: Input validation
    Standard: does every user input point declare length and type validation?
    Verification: inspect the input schema in the API definition and confirm that
    every parameter has type and max_length.

C2: Key management
    Standard: are all secrets and sensitive configurations stored in environment
    variables or a secret-management service?
    Verification: search the design text and config files for key=, secret=,
    and password= literals.
    If a hardcoded value is found → FAIL. If an environment variable is referenced → PASS.

C3: Permission model
    Standard: are there non-admin roles? Does the design follow least privilege?
    Verification: check whether the design defines multiple roles, such as
    read/write/admin, and whether every operation declares the minimum required permission.

C4: Dependency security
    Standard: are third-party dependencies pinned?
    Verification: inspect requirements.txt or equivalent files and check whether
    versions use == or >=."

## 4. Output format: mandatory structure
"Your output must be a JSON object and must contain no other text:
{
  "verdict": "approved" | "rejected",
  "checks": [
    {
      "id": "C1",
      "passed": true | false,
      "evidence": "where in the design you found supporting evidence, such as file:line.
                   If there is not enough information, use 'insufficient_information'."
    }
  ],
  "issues": [
    {
      "id": "I1",
      "description": "specific issue description; factual, not subjective",
      "location": "file:line",
      "severity": "must_fix" | "should_fix",
      "suggestion": "fix suggestion, no more than 2 sentences"
    }
  ]
}

Do not output 'overall evaluation', 'summary', or 'suggest further discussion'.
If a check is uncertain, set passed=false and explain why in evidence.
That is better than incorrectly setting passed=true."

## 5. Boundary behavior: what to do when uncertain
"Handle the following cases by rule. Do not improvise:

- If the design does not contain enough information to judge a check item:
  passed=false, evidence='insufficient_information'
- If the design says 'follows security best practices' without specifics:
  that is not PASS. You verify what was actually done, not what was claimed.
- If an issue severity is unclear between must_fix and should_fix:
  treat it as must_fix; only human review may downgrade it.
- If you find a security issue outside the checklist:
  still report it, mark severity as should_fix, and note in description that it is
  outside the checklist but worth attention."
```

**Design principles for the five elements**:

- **"What you do not own" is more important than "what you own."** It prevents the Agent from crossing boundaries, such as Reviewer commenting on code quality, and narrows the Agent's attention to its own responsibility.
- **Review criteria should move from "evaluate" to "check existence."** "Check whether the design is secure" is an evaluation: vague, subjective, and easily biased by overall impression. "Search for `key=` literals in the design text" is an existence check: concrete, objective, and less dependent on judgment.
- **Boundary behavior defines the Agent's character.** When uncertain, does it guess or admit uncertainty? When it sees a vague claim, does it treat it as evidence or ask for proof? These are not model parameters, but they determine reliability. A Reviewer that guesses is more dangerous than no Reviewer, because its wrong judgment will be treated as "reviewed and approved."

### 8.6.4 Tool assignment -- whitelists, not "please do not use this"

The most common mistake in Multi-Agent tool assignment is to register the full tool set for every Agent, then rely on the System Prompt to say "please only use the tools you need."

That is like giving every employee every access card, then putting up a note saying "please only enter the rooms you should enter." System Prompt is a suggestion. Tool registration is a hard constraint. Suggestions can be ignored by the model, especially when the model believes "using this tool will help complete the task." Hard constraints cannot be ignored.

**Correct approach: whitelist.** Each Agent only receives the tools it needs. Tools outside the whitelist do not exist for that Agent. Runtime rejects calls at the tool-call layer, and the model may not even know those tools exist.

```python
# Tool registration: whitelist
# When creating each Agent, pass only the tools it needs.
# Do not pass the full tool set and rely on Prompt constraints.

AGENT_TOOL_WHITELIST = {
    "author": {
        "search_notes",      # retrieve notes: needs reference material
        "web_search",        # web search: needs current information
        "read_file",         # read files: needs existing docs
        "write_file",        # write files ← Author only; artifact must persist
    },
    "reviewer": {
        "read_file",         # read Author's output
        "search_notes",      # retrieve security standards
        "run_security_scan", # security scan ← Reviewer only; Author does not have it
        # note: no write_file — Reviewer cannot modify Author's output
        # note: no web_search — Reviewer does not need external information
    },
    "supervisor": {
        "read_file",         # read Worker outputs
        # note: no write_file — Supervisor only produces synthesis, not edits source files
        # note: no search — Supervisor does not research; Workers do
    },
    "worker_researcher": {
        "search_notes",      # retrieve notes
        "web_search",        # web search
        "read_file",         # read files
        # note: no write_file — Worker outputs analysis into context,
        #       not directly into the filesystem
    },
}
```

**Iron rules for tool assignment**:

1. **An Agent that can perform a dangerous action must not also approve that action.** `write_file` and `approve_deploy` should never be on the same Agent. `merge_pr` and `code_review` should never be on the same Agent. This is not only about security. When the same Agent can both "do" and "approve," it takes shortcuts: write then approve, approve then merge.
2. **Output tools should only be registered on Agents that truly need them.** In a 3-Agent system, usually only 1 Agent needs `write_file`. Other Agents return outputs through the communication protocol, and the caller decides whether to persist them.
3. **If you are unsure whether an Agent should receive a tool, do not give it the tool.** Adding a tool later is easy: add one line to configuration. Taking it back later is hard: the Agent may already have developed behavior that depends on the tool.

### 8.6.5 Model selection -- not every role needs the strongest model

Not every Agent needs the strongest and most expensive model. Different roles need different model capabilities. If every Agent uses the same model, you are wasting money and may even reduce system reliability.

| Agent role | Core capability needed | Model recommendation | Reason |
|---|---|---|---|
| **Executor / Author** | Long-form generation, creative expression, synthesis across sources | Strongest model | Output quality directly affects the final result; this is where the return on model quality is highest. |
| **Reviewer** | Detail comparison, item-by-item checking, structured output compliance | Mid-to-strong model focused on instruction following and structured output | It does not need creativity. It needs to avoid missing checklist items and avoid fabricating evidence. Temperature should be 0. |
| **Supervisor (decomposition)** | Task analysis, structure design, boundary definition | Strongest model | Decomposition quality determines all Worker quality and the total task cost. Spending $0.02 more here may save $0.20 of wasted Worker work. |
| **Supervisor (synthesis)** | Deduplication, format stitching, conflict marking | Mid model | Mostly structural work: compare fields, merge lists, check format. It needs not to omit or fabricate, not deep creativity. |
| **Worker (research)** | Retrieval + summary + template-based output | Mid model with good retrieval tools | Speed matters; many Workers may run in parallel; cost matters. Output quality should be constrained by templates, not only by model power. |
| **Worker (analysis)** | Deep reasoning, multi-step analysis | Strong model | Analysis quality determines decision quality. If Supervisor depends on Worker analysis to decide, do not underinvest here. |
| **Debate participant** | Argumentation, rebuttal, multi-angle thinking | Strong model | Weak models are easily led astray or trapped in word games. If the role is only "play devil's advocate," a mid model can be enough. |

The table above selects models by Agent role. In real engineering, you also need another view: **what is the underlying model actually strong at?** "Strong model" is not one dimension. A model may be strong at reasoning but weak at code, have long context but unstable instruction following, or be cheap and fast but unsuitable for final adjudication.

Breaking model choice down by capability makes the decision clearer:

| Model capability type | Better fit | Poor fit | Why |
|---|---|---|---|
| **Strong reasoning model** | Supervisor decomposition, Planner, Risk Analyst, complex Code Reviewer | Many simple Workers, format-conversion Agents | Good for task decomposition, trade-offs, conflict judgment, and hidden-risk detection; expensive and should not be used for mechanical extraction. |
| **Strong coding model** | Code Worker, Test Fixer, Code Reviewer | Copywriting Worker, simple summary Agent | Understands project structure, language APIs, test failures, and edge cases; using it for non-code tasks wastes capability. |
| **Long-context model** | Research Worker, Document Analyst, Migration Planner | Short checklist Reviewer, single-step tool-calling Agent | Good for reading large amounts of material and long files; but long context does not guarantee stricter judgment, and it also carries more noise. |
| **Strong instruction-following model** | Reviewer, Schema Extractor, Policy Checker | Creative Author, open-ended Brainstorm Agent | Good for fixed workflow, fixed schema, itemized checks; use low temperature and prioritize stability over novelty. |
| **Low-latency / low-cost model** | Batch classification Worker, format normalization, first-pass screening Agent | Final adjudicator, complex planner | Good for high-concurrency, low-risk tasks; errors must be catchable by later strong models or rules. |
| **Multimodal model** | UI Reviewer, chart-parsing Worker, screenshot QA Agent | Plain-text protocol merge Agent | Valuable when input contains screenshots, PDF pages, or design comps; should not be the default for every Agent. |

A practical rule: **put the strongest model where error propagation is most severe, not everywhere.** If Supervisor decomposes the task badly, every Worker may waste effort. If Reviewer misses a high-risk issue, the user may trust a false "approved" signal. If the final synthesizer fabricates a conclusion, the final deliverable is polluted. These positions deserve stronger, steadier models. By contrast, batch field extraction, template filling, and format conversion can usually use cheaper models because schema checks or downstream Reviewers can catch errors.

**A common failure scene**: every Agent uses the same model and the same temperature. Reviewer runs at temperature 0.7 and "creatively" fabricates plausible-looking evidence. The checklist appears to PASS every item, but two evidence fields are fictional. The entire review becomes useless and more dangerous than no review, because the user trusts the "reviewed" label.

**The special role of Reviewer**: Reviewer is the role that must be least wrong in Multi-Agent. Its judgment is the system's quality gate. Reviewer does not need to be "smart" in a creative sense. It needs to be rigorous: temperature 0, enforced structured output, evidence fields specific to file:line. If Executor writes an imperfect design, the user may fix it. If Reviewer misses a security check, the user may trust the "approved" label and ship an incident.

### 8.6.6 Parameter tuning -- different roles, different parameters

The same model can behave very differently under different parameter settings. Different Multi-Agent roles need different parameter configurations:

| Parameter | Executor / Author | Reviewer | Supervisor | Worker (research) |
|---|---|---|---|---|
| **Temperature** | 0.3-0.7 | **0-0.1** | decomposition 0.2-0.3 / synthesis 0-0.1 | 0.1-0.3 |
| **Max Tokens** | estimated output × 1.3 | **estimated structured output** (usually 500-1000; stop when enough) | decomposition 1024 / synthesis 2048 | template-based estimate (usually 500-800) |
| **Stop Sequences** | none special | stop after JSON closing `}` | same as Reviewer | same as Reviewer |
| **Top P** | 0.9-0.95 | **1.0** (determinism) | 0.95-1.0 | 0.95 |

**Key parameter decisions**:

- **Reviewer's temperature must be 0 or close to 0.** This is one of the most neglected and highest-impact settings. When temperature is not 0, the same design may receive different evidence text across two runs. For a quality gate, determinism matters far more than creativity.
- **Max Tokens is not just a ceiling; it is a budget.** Giving Reviewer too many max tokens will not make it review more carefully. After producing the structured result, it may start adding explanations, advice, or summaries. Setting just enough max tokens tells the model: "once the required structure is complete, stop."
- **Supervisor decomposition and synthesis should use different temperatures.** Decomposition needs some flexibility because each task may split differently. Synthesis needs determinism because the same Worker outputs should produce the same synthesized result.

### 8.6.7 Configuration management -- from scattered settings to "configuration as code"

Managing three Agents manually is tolerable. With five Agents, System Prompts, tool whitelists, model choices, and parameters start spreading across multiple files. You update Reviewer's criteria but forget to update Supervisor's synthesis logic, and the system begins to develop subtle inconsistencies.

**Recommended practice: centralize Agent configuration and keep System Prompts in external files.**

```python
# agent_configs.py — single source of truth for all Agent configurations
# To change any Agent configuration, edit this file.
# To add a new Agent, declare its complete configuration in one place.
# During code review, reviewers can immediately see which Agent configurations
# are affected by a change.

AGENT_CONFIGS = {
    "author": {
        "model": "claude-sonnet-4-6",
        "temperature": 0.4,
        "max_tokens": 4096,
        "system_prompt": "prompts/author_system.txt",  # external file, easy to diff
        "tools": ["search_notes", "web_search", "read_file", "write_file"],
        "output_schema": None,  # no forced structured output
    },
    "reviewer": {
        "model": "claude-sonnet-4-6",
        "temperature": 0.0,  # deterministic; quality gates must not be random
        "max_tokens": 1024,  # just enough for structured output; prevents extra commentary
        "system_prompt": "prompts/reviewer_system.txt",
        "tools": ["read_file", "search_notes", "run_security_scan"],
        "output_schema": "schemas/review_result.json",  # enforce structured output
        "max_rounds": 2,  # Reviewer-specific control parameter
    },
    "supervisor": {
        "model": "claude-fable-5",
        "temperature": 0.2,
        "max_tokens": 2048,
        "system_prompt": "prompts/supervisor_system.txt",
        "tools": ["read_file"],
        "decomposition_strategy": "template_first",  # prefer predefined templates
        "merge_conflict_policy": "flag_not_resolve", # flag conflicts, do not resolve them
    },
    "worker_researcher": {
        "model": "claude-haiku-4-5",  # cheaper model for research Workers
        "temperature": 0.2,
        "max_tokens": 800,
        "system_prompt": "prompts/worker_researcher_system.txt",
        "tools": ["search_notes", "web_search", "read_file"],
        "output_template": "templates/research_report.md",  # force output shape
    },
}
```

**Three principles of configuration management**:

1. **Keep System Prompts in external files.** Do not hardcode long strings in code. External files can be diffed ("which Reviewer criterion changed?"), reviewed, and rolled back. When system behavior becomes abnormal, inspect the latest System Prompt diff first. Often the problem is not code; it is a Prompt change.
2. **Declare tool whitelists centrally at the configuration layer.** One file should show all Agent tool permissions. When adding a dangerous tool such as `delete_file`, reviewers can immediately see which Agents receive it instead of grepping ten files.
3. **Configuration changes must go through review.** Changing Reviewer's checklist or Supervisor's decomposition strategy can be as risky as changing business code. A criterion changed from "check whether plaintext secrets exist" to "check whether a secret-management service is referenced" may allow designs that previously failed to pass. That risk is comparable to changing a line of core business logic.

## 8.7 Communication protocols -- Agents cannot just ask "what do you think?"

We have covered the structure of three collaboration patterns and how to configure each Agent so they are truly different. Now we need to answer: how do configured Agents actually pass information to each other? This is one of the most underestimated problems in Multi-Agent. Many systems design the collaboration pattern well and configure Agents differently, then fail at the communication protocol.

### 8.7.1 Why free-form conversation is a disaster

The most intuitive communication style is to let Agents talk freely, like people in a meeting. Everyone says a sentence, responds, and adds comments. Group Chat works this way: multiple Agents speak freely in a shared conversation.

But in Multi-Agent, free-form conversation is **the most expensive, hardest to debug, and easiest to break** communication style. There are three reasons:

**1. Information decay.** Every time information passes from one Agent to another, the original information decays. Agent A's finding is paraphrased by Agent B, then quoted by Agent C. By the time it reaches Supervisor, the concrete judgment has become a vague impression.

```text
Original: "config.yaml line 8 has a plaintext api_key field, creating a leak risk"
↓ Agent B paraphrases:
"A mentioned a key-management issue in the config file"
↓ Agent C quotes:
"The earlier discussion touched on security concerns"
↓ Supervisor receives:
"The team discussed security" ← the original information is gone
```

**2. Intent distortion.** One Agent says "recommended improvement." Another Agent interprets it as "must fix." Humans use context to distinguish "recommended" from "mandatory." In text passed between Agents, that context is easily lost.

**3. Blurry decisions.** Free-form conversation has no "decision point." Agents can keep discussing, agreeing, adding suggestions, and saying "consider further," but no one says "discussion ends here; the decision is below." The final output becomes meeting notes, not a decision.

### 8.7.2 Design the message format around the collaboration pattern

The alternative to free-form conversation is **structured communication**. This is not about defining a layered protocol from low to high. It is about implementing the three collaboration patterns from earlier as concrete message formats: Reviewer needs review tickets, Supervisor needs task assignments and reports, and Parallel Specialists need findings marked by dimension.

**Reviewer pattern: command-response**

Reviewer should not receive "take a look at this design." It should receive a review request that states what to review, which criteria to use, and how to provide evidence when something fails.

```json
{
  "type": "review_request",
  "artifact": "API design v1",
  "context": {
    "user_goal": "Design a query API for an internal knowledge base",
    "constraints": ["Do not expose unauthorized documents", "Response time below 2 seconds"]
  },
  "criteria": [
    {
      "id": "security.authz",
      "check": "Does the design specify document-level authorization checks?",
      "how_to_verify": "The design must state permission source, check location, and failure response",
      "severity": "must_fix"
    },
    {
      "id": "reliability.timeout",
      "check": "Does the design define timeout and fallback strategy?",
      "how_to_verify": "The design must state timeout duration, retry count, and user-visible result",
      "severity": "should_fix"
    }
  ]
}
```

Reviewer's response must be just as rigid. Notice there is no "overall evaluation" field, because "overall it looks fine" is exactly the kind of empty text that hides problems.

```json
{
  "type": "review_response",
  "verdict": "rejected",
  "checks": [
    {
      "check_id": "security.authz",
      "passed": false,
      "evidence": "The design only says 'connect to the permission system later' and does not state check location or failure response",
      "suggestion": "Add permission source, pre-query authorization check, and unauthorized error response."
    },
    {
      "check_id": "reliability.timeout",
      "passed": true,
      "evidence": "Section 4 defines a 2-second timeout and cache fallback",
      "suggestion": null
    }
  ],
  "issues": [
    {
      "id": "issue-001",
      "location": "Section 3: permission model",
      "severity": "must_fix",
      "description": "Authorization remains a promise and is not part of the request path.",
      "suggestion": "Replace 'connect to the permission system later' with an executable authorization flow."
    }
  ]
}
```

This format is suitable for quality gates: security review, pre-launch checks, design acceptance, and code review. Its defining trait is that **both input and output are tightly constrained**, so the Agent cannot dodge judgment through natural language.

**Supervisor pattern: template-fill**

When Supervisor decomposes a task, do not just say "go research vector databases." It should give Worker a filled task assignment: what to do, what not to do, and what format to deliver.

```json
{
  "type": "subtask_assignment",
  "task_id": "research-vector-db",
  "worker": "researcher-1",
  "topic": "Vector database selection in RAG systems",
  "scope": "Compare only the engineering suitability of Milvus, pgvector, and Pinecone",
  "exclude": "Do not explain vector-search algorithms or write market background",
  "output_template": {
    "key_findings": "up to 3 items",
    "failure_modes": "up to 2 items",
    "recommended_use": "one sentence describing the best-fit scenario",
    "sources": "list cited sources"
  },
  "max_length": 300
}
```

When Worker returns, it should not write a free-form essay. It should fill the template:

```json
{
  "type": "worker_report",
  "task_id": "research-vector-db",
  "status": "completed",
  "content": {
    "key_findings": [
      "pgvector fits teams already using Postgres and has the lowest operational cost.",
      "Milvus fits higher-scale vector workloads with stronger retrieval-performance requirements.",
      "Pinecone fits teams that want to reduce self-hosting burden."
    ],
    "failure_modes": [
      "Only comparing retrieval performance while ignoring data synchronization and permission filtering.",
      "Introducing a separate vector database too early and increasing operational complexity."
    ],
    "recommended_use": "If the team already uses Postgres, start with pgvector to establish a baseline.",
    "sources": ["official documentation", "project README", "engineering practice article"]
  },
  "error": null
}
```

This format works for parallel research and information synthesis. It is less rigid than Reviewer, but it still constrains output shape through templates, preventing three Workers from returning three incompatible reports.

**Parallel Specialists pattern: dimension-tagged findings**

The key to Parallel Specialists is not "everyone says whatever they want." It is that every finding carries its source dimension. That allows Supervisor to deduplicate and detect conflicts instead of blending different perspectives into a vague summary.

```json
{
  "type": "dimension_analysis",
  "dimension": "security",
  "findings": [
    {
      "id": "sec-001",
      "location": "/login",
      "severity": "must_fix",
      "description": "The login endpoint does not define failure-count limits.",
      "evidence": "The design describes username/password verification but does not mention rate limiting or lockout."
    }
  ]
}
```

The merge result should also preserve structure. If two dimensions give opposite judgments for the same location, do not automatically "compromise." Expose the conflict explicitly.

```json
{
  "type": "merge_result",
  "findings": [
    {
      "id": "sec-001",
      "dimension": "security",
      "location": "/login",
      "severity": "must_fix",
      "description": "The login endpoint does not define failure-count limits."
    }
  ],
  "conflicts": [
    {
      "location": "/login",
      "finding_a": "security says failure-count limit is missing",
      "finding_b": "performance says additional checks may increase latency",
      "resolution": "needs_human_review"
    }
  ],
  "coverage": {
    "correctness": 2,
    "security": 1,
    "performance": 1
  }
}
```

This format suits multi-perspective review of the same artifact: correctness, security, performance, cost, and user experience. The goal is not to force multiple Agents to agree; the goal is to make judgments from different dimensions traceable, mergeable, and adjudicable.

**Core principles of structured communication**:

- **Do not accept "overall fine."** Review results must be concrete, itemized, and supported by evidence.
- **Free text should appear only at leaf nodes.** Descriptions can be natural language, but the communication skeleton -- status, type, location, severity -- must be structured fields.
- **Missing fields are better than fabricated fields.** If Reviewer cannot find evidence, set `evidence` to `"not_found"` instead of inventing a plausible description.
- **Human-readable trace.** Structured communication naturally produces searchable traces. You can grep `"verdict": "rejected"` to find all rejected reviews and calculate pass rates for each check item.

### 8.7.3 From internal message conventions to Agent protocols

The `review_request`, `worker_report`, and `dimension_analysis` formats in this section are internal message conventions. In early real projects, this is usually enough: clear fields, clear status, clear artifacts, and clear failure reasons.

But once Agents no longer live in the same codebase, framework, or team, the problem grows: how does one Agent discover another Agent? How does it know what the other Agent can do? How does it delegate tasks, track status, receive results, and handle failure? At that point, a more standardized Agent communication protocol becomes useful.

After 2025, the industry has seen several related attempts:

- **MCP (Model Context Protocol)**: mainly solves how Agents connect to tools, data sources, and context in a standardized way.
- **A2A (Agent2Agent Protocol)**: mainly solves how different Agents discover each other, delegate tasks, exchange messages, and return artifacts.
- **ACP / ANP and other protocol explorations**: attempt to solve Agent communication, identity, discovery, multimodal messages, and cross-platform interoperability from different angles.

The common direction of these protocols is not "make Agents chat more freely." It is the opposite: pull vague natural-language parts into verifiable protocol objects, such as capability descriptions, task state, message type, artifact, error, and permission.

For most business projects, you do not need to introduce a complete industry protocol from day one. A more realistic path is:

1. Define clear structured communication formats inside the system first.
2. When Agent count, team boundaries, and tool ecosystems become more complex, then consider standards such as MCP / A2A.
3. Do not treat protocols as a substitute for reliability. Protocols only solve "how to communicate." They do not automatically solve "who is trusted, who adjudicates, when to stop, and what to do when things go wrong."

## 8.8 Adjudication, stopping, and fallback -- the "traffic rules" of Multi-Agent

Collaboration patterns define how Agents divide labor. Communication protocols define how Agents pass information. There is a third layer: **control mechanisms** -- who decides when things do not go as expected, when the system stops, and how it exits.

Without this layer, a Multi-Agent system is not a decision system. It is a discussion group. It may discuss well, but no one makes the call.

### 8.8.1 Adjudication: who decides when Agents disagree

Multi-Agent systems produce three common types of disagreement, and each needs a different adjudication method:

| Disagreement type | Typical scenario | Adjudication method | Why it cannot be resolved automatically |
|---|---|---|---|
| Reviewer vs Executor | Reviewer says FAIL; Executor says "this is not a problem" | If still rejected after two revision rounds, escalate to human adjudication. Executor must not be allowed to overrule Reviewer. | Letting the reviewed party judge the reviewer cancels the review. |
| Worker vs Worker (factual conflict) | Worker 1 says "Framework A supports streaming output"; Worker 2 says "it does not" | Check source citations. If sources are clear, compare authority. If both sources are unclear, mark "factual conflict exists." | Factual questions require source tracing, not voting. |
| Worker vs Worker (judgment conflict) | Specialist A says "safe"; Specialist B says "vulnerable" | Mark conflict and request human review. Do not vote or take the "majority opinion." | Judgment conflict means at least one side missed or misread something; a human must re-examine it. |

**Design principles for adjudication**:

1. **The adjudicator cannot be a party.** Executor cannot decide whether Reviewer's finding is reasonable. Worker cannot decide whether its own output is correct.
2. **Human adjudication is safer than automatic adjudication.** When two Agents give contradictory judgments, it is safer to pause and ask a human than to let a third Agent "vote." The third Agent can also be wrong.
3. **Adjudication needs a deadline.** A task cannot block forever while waiting for human input. Set a timeout: if no human decision arrives within N minutes, use the most conservative choice, such as prioritizing Reviewer's judgment or pausing the task while preserving state.

### 8.8.2 Stopping conditions: no infinite back-and-forth

Multi-Agent stopping conditions are similar to Reflection stopping conditions, but with collaboration-specific dimensions:

| Stopping condition | Suggested threshold | Behavior when triggered |
|---|---|---|
| Reviewer round trips | Still `rejected` after 2 revision rounds | Mark `disputed`, escalate to human adjudication, do not enter a third round |
| Supervisor synthesis count | 1 decomposition-synthesis cycle | If synthesis has missing data, do not decompose again; mark missing data and output |
| Worker timeout | Slowest expected Worker time × 1.5 | Discard timed-out Worker's result and mark "data missing for this direction" in the report |
| Total token consumption | 50K tokens for one task | Stop all Agents and return completed partial results |
| Repeated message loop | 3 consecutive rounds with message similarity > 90% | Mark as "conversation loop," force stop, and output current state |
| Error escalation | Recoverable error becomes unrecoverable, such as network timeout becoming disk full | Stop all Agents, preserve state, notify user |

**Stopping conditions must be hardcoded. They cannot be decided by the Agent itself.** Agents do not have an instinct for "we should stop now." On the sixth back-and-forth, they may confidently start another round. Stopping conditions are runtime-level enforcement and are independent of the Agent's reasoning ability.

### 8.8.3 Fallback strategy: what if a Worker fails

During Multi-Agent execution, Worker Agents can fail for many reasons: API rate limits, network timeouts, unparseable output, or context overflow. The system must define fallback behavior for every failure mode:

```text
Worker failure mode                    Fallback strategy
─────────────────────────────────────────────────────
Single Worker timeout               → Discard that Worker's result
                                      Mark "Direction X: data missing (timeout)"
                                      in the final report
                                      Do not retry; do not block other Worker outputs

Single Worker output unparseable     → Try to regenerate once, and only once
                                      If still unparseable, mark
                                      "data missing (format error)"

Multiple Workers fail at once        → Likely an upstream issue, such as API outage
(≥50% Workers fail)                    Stop all execution and return partial results
                                      + error diagnosis
                                      Do not continue; continuing may only burn tokens

Supervisor decomposition fails       → If the decomposition plan does not meet minimum
                                      requirements, such as boundary overlap > 30%,
                                      downgrade to "single Agent direct execution"
                                      and skip Multi-Agent
                                      Notify the user: "decomposition quality does not
                                      meet parallel-execution conditions; downgraded"

Supervisor synthesis fails           → Return raw Worker outputs, marked "not synthesized"
                                      Do not ask the LLM to synthesize again;
                                      the cause of the first synthesis failure may remain
```

**Core fallback principle: downgrade, but never silently.** The system may downgrade to single-Agent execution when Multi-Agent is unavailable, but it must not pretend Multi-Agent succeeded. Missing data, failed Workers, skipped checks -- all of these must be explicitly marked in the final output.

---

## 8.9 The real cost -- not just the Token bill

The cost of Multi-Agent is often underestimated because the largest part is not the monthly API bill.

### 8.9.1 A sample cost comparison

Use the knowledge assistant task "write a technical design + security review" as an example, comparing typical consumption between single Agent and Reviewer pattern. The numbers below are teaching estimates for practicing cost breakdown; they are not fixed bills for any production system.

```text
═══════════════════════════════════════════════════════════════════
Task: write a technical design for an API module (about 2,000 words)
and review it from a security perspective

Single Agent self-review:
┌─────────────────────────────────────────────────────────────────┐
│ Writing phase:                                                   │
│   System Prompt: 800 tokens                                      │
│   User input + context: 500 tokens                               │
│   Model output (design): 2,500 tokens                            │
│   Subtotal: 3,800 tokens                                         │
│                                                                 │
│ Self-review phase (same context, one additional turn):           │
│   Additional user message: 100 tokens                            │
│   Model output (review): 300 tokens                              │
│   Subtotal: 400 tokens                                           │
│                                                                 │
│ Total: ~4,200 tokens                                             │
│ Latency: ~40 seconds                                             │
│ Cost: ~$0.06 (estimated with Claude Sonnet pricing)              │
│ Result: missed 4 security risks                                  │
└─────────────────────────────────────────────────────────────────┘

Reviewer pattern:
┌─────────────────────────────────────────────────────────────────┐
│ Author Agent (independent instance):                             │
│   System Prompt: 400 tokens (creation only; no review logic)      │
│   User input + context: 500 tokens                               │
│   Model output (design): 2,500 tokens                            │
│   Subtotal: 3,400 tokens                                         │
│                                                                 │
│ Reviewer Agent (independent instance, independent context):       │
│   System Prompt: 300 tokens (review only; no creation logic)      │
│   Input context (design + checklist): 2,800 tokens                │
│   Model output (structured review result): 600 tokens             │
│   Subtotal: 3,700 tokens                                         │
│                                                                 │
│ Author revision phase (independent instance, receives issues      │
│ only):                                                          │
│   Input context (design + issues): 3,300 tokens                   │
│   Model output (revised design): 2,600 tokens                     │
│   Subtotal: 5,900 tokens                                         │
│                                                                 │
│ Reviewer second review:                                          │
│   Input context (revised design + checklist): 2,900 tokens        │
│   Model output (review result): 300 tokens                        │
│   Subtotal: 3,200 tokens                                         │
│                                                                 │
│ Total: ~16,200 tokens (3.9× single Agent)                        │
│ Latency: ~80 seconds (2× single Agent)                           │
│ Cost: ~$0.22 (3.7× single Agent)                                 │
│ Result: found and fixed all 4 security risks                     │
└─────────────────────────────────────────────────────────────────┘

Cost-benefit analysis:
┌─────────────────────────────────────────────────────────────────┐
│ Extra cost: +$0.16, +40 seconds                                 │
│ Benefit: from "4 security vulnerabilities" to "passed security   │
│ checklist"                                                      │
│                                                                 │
│ Judgment: if deployment with this design causes a security       │
│ incident, remediation cost >> $0.16                              │
│ In this scenario, the extra cost is worth it.                    │
│                                                                 │
│ But if the task is a low-risk internal memo?                     │
│ The extra cost may not be worth it. Not every scenario needs     │
│ Multi-Agent.                                                    │
└─────────────────────────────────────────────────────────────────┘
```

**Key insight**: Multi-Agent token consumption is often 2-5× single Agent. The real question is not "is it expensive?" The question is "what did the extra tokens buy?" If they bought "found 4 security vulnerabilities that a single Agent would miss," then $0.16 is cheap. If they bought "three Agents discussed for 12 rounds and produced the same result as one Agent," every cent was wasted.

### 8.9.2 Latency amplification: the real cost of message round trips

Multi-Agent latency is not simply "model inference time × number of Agents." Real latency includes:

```text
Reviewer pattern latency breakdown:
┌──────────────────────────────────────────────────────────────┐
│ Author inference: 30 seconds                                 │
│ +                                                            │
│ Reviewer inference: 25 seconds                               │
│ +                                                            │
│ Context construction and transfer: 5 seconds                  │
│   (package Author output + checklist into Reviewer context)    │
│ +                                                            │
│ Author revision inference: 20 seconds                         │
│ +                                                            │
│ Reviewer second-round inference: 10 seconds                   │
│ =                                                            │
│ Total: ~90 seconds                                           │
│                                                              │
│ User-perceived latency: 90 seconds from request to approved   │
│ result                                                       │
│ Single-Agent self-review: ~40 seconds                        │
│ Latency amplification: 2.25×                                 │
│                                                              │
│ Supervisor pattern latency (4 Workers in parallel):           │
│ Supervisor decomposition: 8 seconds                           │
│ +                                                            │
│ Parallel Workers (slowest one): 45 seconds                    │
│ +                                                            │
│ Supervisor synthesis: 15 seconds                              │
│ =                                                            │
│ Total: ~68 seconds                                           │
│ Serial execution (4 × 40 seconds + 10 seconds synthesis):     │
│ ~170 seconds                                                 │
│ Speedup: 2.5× ✓                                              │
└──────────────────────────────────────────────────────────────┘
```

**Keys to latency optimization**:

- Reviewer pattern is inherently slower than single Agent because every round trip adds another inference. Design for fewer round trips; keep the two-round limit.
- Supervisor pattern gets latency benefit from parallelism. If there are too few Workers or task durations vary heavily, such as one Worker taking 45 seconds and another 10 seconds, the speedup shrinks.
- Context construction and transfer time is easy to ignore, especially when the transferred content is long, such as a full technical design.

### 8.9.3 Long-term cost: trace complexity and handoff difficulty

The most hidden cost of Multi-Agent is not in the bill. It is in **maintenance**.

Three months later, when a new engineer takes over the system, they face:

```text
Single-Agent system:
├─ 1 System Prompt
├─ 1 tool set
├─ 1 trace (linear execution log)
└─ Debugging: find the broken step → fix Prompt or tool

Multi-Agent system:
├─ 3 System Prompts (Author, Reviewer, Supervisor)
├─ 3 tool sets (different permissions)
├─ multiple crossed traces (Agent A's output is Agent B's input;
│   finding who introduced an error requires reading 3 traces and
│   cross-checking them)
├─ Debugging: "Why is the final design missing one security check?"
│   → Reviewer missed it (inspect Reviewer trace)
│   → Author ignored it during revision (inspect Author trace)
│   → Supervisor dropped it during synthesis (inspect Supervisor trace)
│   → a communication-protocol field was parsed incorrectly
└─ Change impact: changing Reviewer's checklist
                → may affect Author's revision strategy
                → may affect Supervisor's judgment logic
```

This does not mean Multi-Agent should not be used. It means: **introduce Multi-Agent only when you are confident that the value it creates covers the additional maintenance cost.** If a single Agent with a good Prompt can reach 90 points, introducing Multi-Agent to chase 95 points may cost 3× the maintenance complexity.

## 8.10 Exercise: make a Supervisor decomposition executable

**Related sections**: 8.4 Supervisor pattern, 8.7 structured communication, 8.8 fallback strategy.

**Scenario**

The user asks: "Research the latest practices in three Agent directions: Memory, Tool Use, and Multi-Agent. For each direction, output key findings, common failure modes, recommended practices, and sources."

**Constraints**

- At most 3 Workers.
- Each Worker output must be no more than 300 words.
- Each Worker must provide at least 2 sources.
- If a Worker times out, the final report must not pretend that direction was completed.

**Output requirement**

Write a Supervisor dispatch plan in the following format:

```json
{
  "subtasks": [
    {
      "id": "T1",
      "worker": "worker_memory",
      "topic": "",
      "scope": "",
      "exclude": "",
      "output_template": "",
      "timeout_seconds": 60
    }
  ],
  "merge_rules": [
    "",
    ""
  ],
  "fallback_rules": [
    "",
    ""
  ]
}
```

**Passing criteria**

- Every subtask has `scope` and `exclude`, and the three Worker scopes must not obviously overlap.
- `output_template` must include four fields: "key findings / failure modes / recommended practices / sources."
- `merge_rules` must explain how to deduplicate, how to handle factual conflicts, and how to mark sources.
- `fallback_rules` must explain what to do for three cases: Worker timeout, unparseable output, and insufficient sources.
