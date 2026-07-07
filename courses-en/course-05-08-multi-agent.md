# Chapter 8: Multi-Agent -- from "one person works" to "one team works."

[Return Course Five Document](./course-05-01-scenario-enhancement.md) | [Previous Chapter](./course-05-07-human-in-the-loop.md) | [Next chapter](./course-05-09-composition.md)

## Table of contents of this chapter

- [8.1 Three types of hard ceiling for single Agent](#81-three-types-of-hard-ceiling-for-single-agent)
  - [8.1.1 Conflict of roles: creators cannot review their work](#811-conflict-of-roles-creators-cannot-review-their-work)
  - [8.1.2 Context squeezing: Too much middle reasoning has become noise](#812-context-squeezing-too-much-middle-reasoning-has-become-noise)
  - [8.1.3 Serial bottlenecks: undependent tasks queuing](#813-serial-bottlenecks-undependent-tasks-queuing)
  - [8.1.4 "More models" why not the answer?](#814-more-models-why-not-the-answer)
- [8.2 What's the split?](#82-whats-the-split)
  - [8.2.1 Prompt not Multi-Agent](#821-prompt-not-multi-agent)
  - [8.2.2 Four different: input, tools, objectives, acceptance standards](#822-four-different-input-tools-objectives-acceptance-standards)
  - [8.2.3 Self-censorship List: Your scenes meet a few](#823-self-censorship-list-your-scenes-meet-a-few)
- [8.3 Reviewer Mode: Simple Multi-Agent Entry](#83-reviewer-mode-simple-multi-agent-mode)
  - [8.3.1 Model skeleton: one execution, one review](#831-model-skeleton-one-execution-one-review)
  - [8.3.2 Why independent context is more effective than changing role Prompt](#832-why-independent-context-is-more-effective-than-changing-role-prompt)
  - [8.3.3 Operational rollback: a single Agent self-review vs Reviewer review](#833-operational-rollback-a-single-agent-self-review-vs-reviewer-review)
  - [8.3.4 Obsolete boundary of Reviewer](#834-obsolete-boundary-of-reviewer)
- [8.4 Supervisor Model: Dismantling, Distribution, Summary](#84-supervisor-model-dismantling-distribution-summary)
  - [8.4.1 Model skeleton: one dispatcher + multiple implementers](#841-model-skeleton-one-dispatcher-multiple-implementers)
  - [8.4.2 Dismantling quality determines the value of the whole model](#842-dismantling-quality-determines-the-value-of-the-whole-model)
  - [8.4.3 Costs of consolidation - "Three Walkers ran out, Supervisor took longer to merge."](#843-costs-of-consolidation---three-walkers-ran-out-supervisor-took-longer-to-merge)
  - [8.4.4 Obsolete boundary of Supervisor](#844-obsolete-boundary-of-supervisor)
- [8.5 Parallel Specialists: same mission, multiple eyes](#85-parallel-specialists-same-mission-multiple-eyes)
  - [8.5.1 Distinction from Supervisor: same input, different dimensions](#851-distinction-from-supervisor-same-input-different-dimensions)
  - [8.5.2 Cross-dimensionalization is a parallel premise](#852-cross-dimensionalization-is-a-parallel-premise)
  - [8.5.3 Consolidation rule: conflict does not automatically abate](#853-consolidation-rule-conflict-does-not-automatically-abate)
- [8.6 Agent's settings and configurations -- how "different" landed.](#86-agents-settings-and-configurations----how-different-landed)
  - [8.6.1 Write Agent settings instead of Prompt](#861-write-agent-settings-instead-of-prompt)
  - [8.6.2 Mapping with four dimensions](#862-mapping-with-four-dimensions)
  - [8.6.3 Systems Prompt Design -- not just "rename."](#863-systems-prompt-design----not-just-rename)
  - [8.6.4 Allocation of tools — white list, not "please don't use"](#864-allocation-of-tools-white-list-not-please-dont-use)
  - [8.6.5 Model selection - not all players need the strongest model](#865-model-selection---not-all-players-need-the-strongest-model)
  - [8.6.6 Easing of parameters — different roles, different parameters](#866-easing-of-parameters-different-roles-different-parameters)
  - [8.6.7 Configuration management - from scattered locations to "configuration or code"](#867-configuration-management---from-scattered-locations-to-configuration-or-code)
- [8.7 Communication protocol-Agent cannot "what do you think?"](#87-communication-protocol-agent-cannot-what-do-you-think)
  - [8.7.1 Why is free dialogue a disaster?](#871-why-is-free-dialogue-a-disaster)
  - [8.7.2 Design communication formats by collaborative mode](#872-design-communication-formats-by-collaborative-mode)
  - [8.7.3 From internal communications engagement to Agent protocol](#873-from-internal-communications-engagement-to-agent-protocol)
- [8.8 award, suspension and background - Multi-Agent 'Rules of Traffic'](#88-award-suspension-and-background---multi-agent-rules-of-traffic)
  - [8.8.1 Adjudication mechanisms: who rules when differences arise](#881-adjudication-mechanisms-who-rules-when-differences-arise)
  - [8.8.2 Conditions for cessation: not unlimited return](#882-conditions-for-cessation-not-unlimited-return)
  - [8.8.3 Bottom strategy: what if Walker dies?](#883-bottom-strategy-what-if-walker-dies)
- [8.9 The truth of the cost - not just Token's bill](#89-the-truth-of-the-cost---not-just-tokens-bill)
  - [8.9.1 An estimated comparative bill](#891-an-estimated-comparative-bill)
  - [8.9.2 Delay magnification: the real cost of communications travel](#892-delay-magnification-the-real-cost-of-communications-travel)
  - [8.9.3 Long-term costs: Trade complexity and difficulty of taking over](#893-long-term-costs-trade-complexity-and-difficulty-of-taking-over)
- [8.10 After-school exercise: write the subvisor dismantling to implementable](#810-after-school-exercise-write-supervisor-dismantling-to-implementable)

---

## 8.1 Three types of hard ceiling for single Agent

Before discussing how Multi-Agent designed it, we need to figure out a more fundamental question: **Where exactly is Agent's card?** If you don't understand the question, then you introduce Multi-Agent probably is "structure for architecture."

The single Agent capacity bottleneck is not "not smart enough" but structural. There are three types of hard ceilings that correspond to three different patterns of failure.

### 8.1.1 Conflict of roles: creators cannot review their work

Back to the scene at the beginning of this chapter. After the knowledge assistant wrote the API technology program, you let it be reviewed from a security perspective. It says "no obvious problem" -- and you look at three security hazards.

This is not an issue of attitude, but of mechanisms. The same Agent created a lot of middle reasoning under the "Creative Mode" - – "In order to facilitate local development, let's simplify the power model first with an explicit key, then refine it later" – these reasonings are a reasonable trade-off at the time of creation, but they remain in the context. And when you switch it to "review mode," these reasonings become preconceived "explains": seeing the explicit key, it's thinking, "This is for the convenience of development," not "This is a security loophole."

For example, it took you two hours to complete a 300-word technical program, and you were immediately asked to "check the program from a safety perspective." Even if you're a person with security experience, you'll defend your design unconsciously. The same brain, preconceived, is not about attitude, is about cognitive mechanisms. Same thing with Agent -- except that its "preliminary" expression is those tokens that already exist in the context. **The structural causes of role conflicts**: The creator's goal is to complete the programme and the examiner's goal is to identify the problem. These two objectives are naturally contradictory. Let the same context and the same target function serve both conflicting objectives - – The result is a compromise between objectives, and the review becomes an exercise.

### 8.1.2 Context squeezing: Too much middle reasoning has become noise

When single Agent handles complex tasks, a large number of intermediates are piled up in context windows: drafts of the first edition, track of failed attempts, results of exploratory searches, provisional records of all kinds "to be written down and used later".

These things were valuable at the moment they were produced. But when Agent needed to judge on the basis of the final output, these intermediate reasoning became **noise** — they took up context space, distracted attention and introduced outdated assumptions.

This is typical of the crowding:

```text
Agent Context window (simplified indicative):
┌────────────────────────────────────────────────────────────┐
│ System Prompt (500 tokens)                                 │
│ Mission: writing technology programme+ Security clearances│
├────────────────────────────────────────────────────────────┤
│ User Message (100 tokens)│
├────────────────────────────────────────────────────────────┤
│ Round 1: Attempting to use option A, finding unreasonable, giving up (800 tokens)│  ← Noise
│ Round 2: try to use option B, written in part (1200 tokens)│  ← Partial Noise
│ Round 3: Completion of the first draft of Option B (2000 tokens)│  ← It works.
│ Retrieving intermediate results: 5 notes summary on API design (1500 tokens)│  ← Partial Noise
│ Round 4: Motion programme (800 tokens)│  ← Noise
├────────────────────────────────────────────────────────────┤
│ User: "Safety review now."│
│ Agent Need to make a security determination in all the above-mentioned contexts│
│                                                             │
│ Question: It saw the "preliminary" reasoning in Round 1 to simplify it.│
│ It's a theory that's going to turn into a review, "It's intentional, it's not a problem."│
└────────────────────────────────────────────────────────────┘
```

**The structural root cause of the squeezing of the context**: The context window for single Agent is the "public pool" of all information. The middle product of the creation process is mixed with the final output, and Agent can't distinguish between "this is the final decision" and "this is an abandoned attempt". At the time of the review, the historical information had polluted the judgement.

### 8.1.3 Serial bottlenecks: undependent tasks queuing

The first two are quality issues and the third is speed.

The knowledge assistant received a research mission: "Help me look into the four main directions of the Agent architecture - Tool Use, Memory, Planning, Multi-Agent - and give me an update on each of them. "Single Agent treatment:

```text
Timeline (string execution):
├─ [0:00-1:30] Research Tool Use: Retrieving Notes+ Search for updates+ Collapse Output
├─ [1:30-3:00] Research Memoory: Retrieving notes+ Search for updates+ Collapse Output
├─ [3:00-4:30] Research Planning: Retrieving notes+ Search for updates+ Collapse Output
├─ [4:30-6:00] Research Multi-Agent: Retrieving Notes+ Search for updates+ Collapse Output
└─ [6:00-7:00] Summarize four studies and produce final reports

Total time taken: about 7 minutes
```

But look closely at these four research missions — they are not dependent on each other. The study Memory does not have to wait for the results of Tool Use. They can be carried out simultaneously. **The structural causes of the serial bottlenecks**: single Agent has only one execution thread. Even if there is no dependency between mandates, there can be only one. This is not a question of the speed of the model — the speed of the model's reasoning, and the total time of queuing four tasks is the sum of four tasks.

### 8.1.4 "More models" why not the answer?

A natural idea is: will these problems be solved automatically when a stronger model comes out?

Nope. As these three types of ceiling are structural problems **, not capacity problems**.

- **Role conflict** is not a model that is not smart enough to read it — it is a conflicting goal in the same context. A stronger model might be better transposed between the two objectives, but a pre-emptive "interpretation" would soften the review criteria as long as creation and review shared the same context.
- **Context squeezing** is not the size of the context window of the model - it is the information structure. The larger window simply plugs in more noise and does not address the structural flaws of the "intermediate reasoning of pollution final judgment".
- **Serial bottlenecks** are more unrelated to modelling capabilities — one-way is one-way.

This is the rationale behind the existence of Multi-Agent: when the single Agent's **structure (rather than capacity)** becomes a bottleneck, these structural limitations need to be broken with more than examples, context, tool sets.

---

## 8.2 What's the split?

The next step is not "defining Agent's Role" but to find out: **Multi-Agent's Distinction?**

### 8.2.1 Prompt not Multi-Agent

The easiest mistake: to write "System Prompt" as "create Argentina." Define three roles — researcher, engineer, examiner — to write to each role a piece of System Prompt, and then rotate the same model. It's not Multi-Agent, it's called role-playing.

The difference between role-playing and the nature of Multi-Agent:

```text
"False "Multi-Agent" (change Prompt):
┌─────────────────────────────────────────────────────┐
│ Same LLM instance│
│ Same Context Window│
│ The same tool set│
│                                                     │
│ Round 1: System = "You're a researcher." → Output research reports│
│ Round 2: System = "You're an engineer." → See the report.+ All│
│          Intermediate reasoning → Outputs technical programme│
│ Round 3: System = "You're the censor." → See the technology.+ Research│
│          Report+ All middle reasoning → "No obvious problem."│
│                                                     │
│ The three players share the same brain, the same memory, the same set of tools.│
│ "The reviewers "see the researcher" and "engineer" all the thinking.——       │
│ Those are the compromises, "Simplify here later."│
└─────────────────────────────────────────────────────┘

"True "Multi-Agent" (independent example):
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Agent A: Researchers│  │ Agent B: Engineer│  │ Agent C: Reviewer│
│                 │  │                 │  │                 │
│ Context:│  │ Context:│  │ Context:│
│ - Research mission│  │ - Technical programme mandate│  │ - Review criteria│
│ - Search Results│  │ - Research report (final)│  │ - Technical programme (final)│
│                 │  │                 │  │ - Original Requirements│
│ Tools:│  │ Tools:│  │                 │
│ - Search│  │ - Write Files│  │ Tools:│
│ - Retrieving notes│  │ - Read Files│  │ - Read files (read-only)│
│                 │  │                 │  │ - Clear scan.│
│ Can not see:│  │ Can not see:│  │                 │
│ - Engineer's reasoning.│  │ - Researcher's middle reasoning│  │ Can not see:│
│ - Reviewer's judgement│  │ - Reviewer's judgement│  │ - Researcher's reasoning│
│                 │  │                 │  │ - Engineer compromise.│
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

The key difference is not how well it is written in Prompt, but in **every Agent sees things differently and can do different things.**

### 8.2.2 Four different: input, tools, objectives, acceptance standards

The real Multi-Agent splits four dimensions. For example, the knowledge assistant's "writing technology program + security clearance" scene:

| Dimensions | Form Agent (self-review) | Multi-Agent(Author + Reviewer) |
|---|---|---|
| **Entered differently** | Author and Reviewer are in the same context. Reviewer "sees" the middle reasoning and compromise of Author. | The Author context requires documentation, notes search results, writing tools. Reviewer context **only** final option + review criteria not available for Author's draft and "simplified later." |
| **Different tools** | The same tool set -- it can write files and make security scans. | Author can write documents and retrieve notes. Reviewer can only read_files, run safety scans -- **can't write** to make sure the examiner doesn't quietly "do it again" |
| **Different goals** | "Full the user's mission" -- the goal is vague and the sub-goals compromise. | Objective: Technical programmes with outputs to meet demand. Objective Reviewer: To find all issues that do not meet safety standards. **Targets do not compromise with each other** |
| **Different acceptance standards** | "As long as the user thinks it's okay," no objective criteria. | Author standard: Programme fully covers needs. Reviewer standard: review list adopted article by article, any one FAIL as a whole REJECT |

**Of these four dimensions, at least two are different, and Multi-Agent is worth it.** If the two Agents have the same input, the same tools, the same goals and the same acceptance criteria - whatever name they are given, they are essentially the same Agent. You're just wasting token and delaying.

Here's one of the simplest criteria: **If you can't say two Agents, "What difference does it make?", then you don't need two Agents.**

### 8.2.3 Self-censorship List: Your scenes meet a few

Before introducing Multi-Agent, answer by article:

```text
□ Role Conflict: Is there a natural contradiction between two objectives?
   (Example: Creator vs examiner, optimist vs security assessor, promoter vs risk analyst)
   If there's no natural contradiction, Agent.+ Clear Prompt usually is enough.

□ Independent context needs: whether the middle reasoning of one role is noise or necessary information for the other?
   (Example: Debugging track during code realization;The compromise in the programme discussion is noise for final acceptance)
   If intermediate reasoning is useful for all roles, there is no need to split the context.

□ Tool permission separation: whether some operations should not be performed by the same Agent?
   (Example: Authorized deployment of vs execute deployment, write code vs merge to main branch, generate invoices vs approve invoices)
   If all operations can be performed safely by the same Agent, no split is required.

□ Parallel possibilities: whether there are non-dependent sub-missions that can be carried out simultaneously?
   (Example: research on four separate directions, analysis of three separate modules, parallel extraction of data from five data sources)
   If mandates are strictly sequentially dependent, the parallel value is zero.

□ Diversity of perspectives: need to look at the same issue from different positions, different assumptions, different risk preferences?
   (Example: Technical programmes need to be assessed from the perspective of cost, safety and maintenance)
   If a single perspective already covered all the concerns, there was no need for more perspectives.
```

**Introductory judgement**: satisfaction of at least two of these is worth serious consideration. When only one is satisfied, there is usually a simpler method (better Prompt, more detailed tool privileges, predefined checklist) to achieve similar results.

---

## 8.3 Reviewer Mode: Simple Multi-Agent Mode

Reviewer is the "Hello World" of Multi-Agent -- it only takes two Agents, the simplest mode of communication and the easiest to assess. If not even the Reviewer can't get away, let's not think about Supervisor, Debate or Graph Collaboization.

It solves only one problem: **implementers cannot review their outputs impartially.**

### 8.3.1 Model skeleton: one execution, one review

```text
Executor Agent(Reviewer
┌──────────────────────────┐              ┌──────────────────────────┐
│ System: You're a tech writer.│              │ System: You're a security inspector.│
│                          │              │                          │
│ Tools:│              │ Tools:│
│  - Write Files│   Final outputs│  - Read files (read only)！)       │
│  - Retrieving notes│─────────────►│  - Search safety code│
│  - Web Search│              │  - Checklist checks│
│                          │   Review observations│                          │
│ Context:│◄─────────────│ Context:│
│  - Required Document│              │  - Final output (only this)！)    │
│  - Note search results│              │  - List of criteria for review│
│  - Drafts and reasoning in the creation process│              │  - Security Code Document│
│                          │              │                          │
│ Objective: To complete the technical programme│              │ Objective: To identify all security issues│
│ Receipt and inspection: programme coverage requirements│              │ Acceptance and inspection: review of the list adopted article by article│
└──────────────────────────┘              └──────────────────────────┘
```

Core skeleton code:

```python
# Reviewer Mode: Shortest Multi-Agent, 2 Agent+ Structural review
class ReviewerPattern:
    """Executor produces output; reviewer checks it; then fix or report."""

    def __init__(self, executor: Agent, reviewer: Agent):
        self.executor = executor
        self.reviewer = reviewer

    def run(self, task: str, criteria: list[dict]) -> dict:
        """
        task: Other Organiser
        criteria: Review lists, each of which is an article-by-article check
          [{"id": "C1", "check": "All user input is verified for length?",
            "how_to_verify": "Check the parameter statements in the API endpoint definition"},
           {"id": "C2", "check": "API Whether the key is stored in an environment variable?",
            "how_to_verify": "Search for whether key is included in the profile=or secret= Literally."},
           ...]
        """
        # Step 1: Executor Outputs
        draft = self.executor.run(task)

        for round_num in range(2):  # Up to two rounds of correction
            # Step 2: Reviewer Review
            # Key: Reviewer only receives final output and review criteria and does not receive intermediate reasoning from execuator
            review = self.reviewer.run(
                task="The following outputs are examined article by article against the review list. Give specific pass/fail judgement and evidence. " I don't know.
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

            # Step 3: Executor Amendments
            # Key: Only specific issues, no subjective evaluation of reviewer
            draft = self.executor.run(
                task=task,
                fix_instructions=review.issues  # A list of specific issues, not "a poor overall quality."
            )

        # Two rounds not passed: marking differences, manual adjudication
        return {
            "status": "disputed",
            "output": draft.output,
            "unresolved_issues": review.issues,
            "message": "Two rounds of amendment are still pending review, requiring manual adjudication."
        }
```

> **Design element**: Exporter and Reviewer uses separate LLM examples - different Systems Prompt, different tool sets, different context windows. `fix_instructions` Only the specific questions found by Reviewer (e.g., "line 3 lacks input length verification") and no subjective evaluation by Reviewer (e.g., "of poor overall quality"). Let Executor modify it on the basis of facts, rather than being influenced by the subjective opinion of another model. The two-round cap is a protective mechanism — the marginal benefits of the third round of amendment are often insufficient to cover communication costs and decision-making fatigue.

### 8.3.2 Why independent context is more effective than changing role Prompt

The most critical mechanism of the Reviewer model is the **independent context**. It's not "let the model think in a different angle" -- it's a different angle in the same context, and the first message is still there. The context of independence is the middle reasoning of Reviewer not physically visible to Executor.

Specifically, Reviewer can't see these things:

| Execuator information in context but not available in Reviewer | Why can't Reviewer see it? |
|---|---|
| "In order to facilitate local development, you can store the key with a clear message." | It'll make Reviewer re-understand the word "security breach" to "intentional ad hoc solution." |
| "The permission model is simplified to an admin, then refined." | Reviewer, seeing this explanation, may no longer mark "the lack of minimal permission" as FAIL |
| First two versions of the three drafts (released) | Noise - not related to the final scenario, but may confuse the Reviewer's understanding of the programme structure |
| Executor's uncertainty and hesitation in writing. | It'll create unnecessary suspicion or let go of real flaws. |

**The very nature of the context of independence is asymmetrical information** - and **the information deliberately designed is incorrect**. Execuator knows more than Reviewer, but some of the messages Reviewer shouldn't know -- it affects judgment. This is one of the reasons for "blindness" in reality: the reviewer does not know who the author is, not the question of competence, but the design of the system — blocking identity information to make judgement more objective.

### 8.3.3 Operational rollback: a single Agent self-review vs Reviewer review

Here's the end-to-end comparison with the Knowledge Assistant, Writing Technology Program + Security Review.

```text
═══════════════════════════════════════════════════════════════════
Mission: Write an API module technical programme and review it from a security perspective
═══════════════════════════════════════════════════════════════════

Mode I: Single Agent (self-review)
┌─────────────────────────────────────────────────────────────────┐
│ [10:00] Agent Writing scheme (35 seconds)│
│         Output: API design document containing endpoint definition, data stream, configuration description│
│                                                                 │
│ [10:01] User: "Safety review now."│
│         Agent:"As a result of the review, the programme has no obvious security problems."│
│                                                                 │
│         Four hidden questions (examining missing):│
│         ① /api/data End does not enter length limit│
│         ② API key Written in config.yaml│
│         ③ Permission model only has one character, all operations need admin permissions│
│         ④ requirements.txt Unlocked third-party dependent version│
│                                                                 │
│         Why did you miss it??Agent The middle line of reasoning in writing the program included:│
│         - "In order to facilitate local development, first, it's clear."│
│         - ""The power model will be refined."│
│         These reasonings became "explaining" at the time of the review, weakening the review criteria.│
└─────────────────────────────────────────────────────────────────┘

Mode 2: Reviewer Mode
┌─────────────────────────────────────────────────────────────────┐
│ [10:00] Author Agent Writing scheme (35 seconds)│
│         Outputs: Idem│
│                                                                 │
│ [10:01] Reviewer Agent Received:│
│         - Final formula text (no middle reasoning for Author)│
│         - Review list (4 items, each with a specific method)│
│         - Safety Code Document (as reference)│
│         - Tools: Reading documents, searching guidelines, article-by-article checks│
│                                                                 │
│         Reviewer Article by article:│
│         ┌─────────────────────────────────────────────────────┐  │
│         │ C1: Enter Validation│  │
│         │   verify: Check the parameter statements in the API endpoint definition│  │
│         │   Result: /api/data endpoint input parameter has no length limit → FAIL    │  │
│         │   Evidence: api schema.yaml row 12│  │
│         │                                                      │  │
│         │ C2: Key Management│  │
│         │   verify: Search for profile key=/secret= Volume│  │
│         │   Result: config.yaml line 8 api key: "sk-abc123" → FAIL│  │
│         │   Evidence: config.yaml line 8│  │
│         │                                                      │  │
│         │ C3: Permission Model│  │
│         │   verify: Check for non-admin role definition│  │
│         │   Result: only admin role missing read/write separation → FAIL  │  │
│         │   Evidence: missions.py Line 3-5│  │
│         │                                                      │  │
│         │ C4: Reliance on security│  │
│         │   verify: Checks whether releases.txt are locked│  │
│         │   Result: All dependent uses>= Not==,Unlocked → FAIL         │  │
│         │   Evidence: requirements.txt full text│  │
│         └─────────────────────────────────────────────────────┘  │
│                                                                 │
│         verdict: rejected (4/4 FAIL)                             │
│         issues: [                                               │
│           {id:"C1", desc:"/api/data Missing input length limit,│
│            location:"api_schema.yaml:12", suggestion:"Add max legth."},│
│           {id:"C2", desc:"API key "Specific storage"│
│            location:"config.yaml:8", suggestion:"Change to an environment variable."},  │
│           ...                                                   │
│         ]                                                       │
│                                                                 │
│ [10:02] Author Review received, amended article by article (25 seconds)│
│                                                                 │
│ [10:03] Reviewer Second round of reviews:│
│         C1: PASS  C2: PASS  C3: PASS  C4: PASS                  │
│         verdict: approved                                        │
│                                                                 │
│ Comparison:│
│ Single Agent self-censorship: four security risks missing, claiming "no obvious problem."│
│ Reviewer Mode: All 4 problems identified and corrected│
│ Additional costs:+1 Minutes (Reviewer review)+ Author Amended)+ $0.04 token    │
│ Proceeds: from "safe breach online" to "security clearance list."│
═══════════════════════════════════════════════════════════════════
```

### 8.3.4 Obsolete boundary of Reviewer

The Reviewer model works, but it works only under certain conditions. Here are its four failed borders: **Boundary I: Expiry when the list is vague.** If the review criterion is "Check if the program is safe" (one sentence), Reviewer's output will be the same as the single Agent self-censorship - "no obvious problem". The review list must be specific, article-by-article, with a clear verify methodology.

```text
Fuzzy review criteria:
  "Check if the program is safe." → Reviewer Output: "All clear. No obvious problem."

Specific review criteria:
  "1. All user input verified for length and type?Validation method: Check the statement of each parameter in API schema.
   2. Whether the key is stored in an environmental variable or key management service Medium?Authentication method: key in grep config file= Mode.
   3. Existence of non-admin role definition?Validation method: Check the list of roles defined in the permission module.
   4. Third party dependent on locking in version number?Validation method: Check the version declaration format in requirements.txt."
```

**Boundary II: Reviewer lapses when no independent authentication tool is available.** If the Reviewer can only read the text of the scheme and then judge it is not different from the individual Agent self-examination. Reviewer must have a validation tool independent of Executor: read the original profile (rather than read the excurator's description in the program), run linter, retrieve the original security code. Core principle: **Reviewer validates "real things", not Executor "proclaimed things."**

**Boundaries III: Reviewer is too harsh to be locked.** If every recommendation of review is "must be modified," when Excelctor finishes the round, Reviewer finds a new problem... - Look, it's a new problem, not a problem that hasn't been fixed -- and then Execuator changes it, Reviewer discovers a new problem and never appears. Method of amendment: Distinguishing between "must modify" and "recommended to optimize"; must not exceed 5 and the recommendation does not block adoption. **Boundaries IV: Execuator learned the "prejudice" review list.** This is the most hidden pattern of failure. After a number of times, Execuator learned to proactively add to the program the description "Looks like a security measure" - "This module follows the best practice of safety" - "All inputs have been fully verified" - but these descriptions do not correspond to actual realization. After seeing these statements, Reviewer marked "Save security measures mentioned" in the check list. In practice, however, security measures have not been implemented. Method of amendment: To review the list from "Whether or not to mention" to "Whether or not to implement" - do not check that "the program discusses key management" but check that "the key in the program is actually stored in the environment variable (grep authentication). "

---

## 8.4 Supervisor Model: Dismantling, Distribution, Summary

Reviewer addresses the issue of "quality" — the implementer needs to be independently reviewed. But when the task itself can naturally be broken down into several non-dependent sub-tasks, the single Agent encounters the problem of **speed** - a chain bottleneck.

The Supervisor model uses a scheduler Agent to dismantle and aggregate, and multiple worker Agents are implemented in parallel.

### 8.4.1 Model skeleton: one dispatcher + multiple implementers

```text
Supervisor Agent                             Worker Agents
┌─────────────────────────┐       ┌─────────────────────────────────┐
│ Receive user assignments│       │ Worker 1: Research Tool Use│
│                         │       │  - Independent Context│
│ Other Organiser│       │  - Independent search tool│
│  - Clarifying borders│───┬───│  - Output: Structured findings│
│  - Specify output format│   │   │                                 │
│  - Assign Worker│   │   │ Worker 2: Research.│
│                         │   │   │  - Independent Context│
│ Summary N Results:│   │   │  - Independent search tool│
│  - Heavy.│   │   │  - Output: Structured findings│
│  - Conflict identification│◄──┴──│                                 │
│  - Note Missing│       │ Worker 3: Research│
│  - Synthetic Final Output│       │  ...                            │
└─────────────────────────┘       │ Worker 4: Research Multi-Agent│
                                  └─────────────────────────────────┘
```

Core skeleton code:

```python
class SupervisorPattern:
    """Supervisor Other Organiser → Workers Parallel → Supervisor Summarize """

    def __init__(self, supervisor: Agent, workers: dict[str, Agent]):
        self.supervisor = supervisor
        self.workers = workers

    def run(self, task: str) -> dict:
        # Step 1: Supervisor Dismantling Tasks
        # Dismantling results must include: boundary, output template, workker assignment
        plan = self.supervisor.decompose(task)
        # plan.subtasks = [
        #   {"id": "T1", "topic": "Tool Use The latest practice."
        #    "worker": "researcher_1",
        #    "scope": "Design mode, fail mode, frame comparison,
        #    "exclude": "It does not contain cross-cutting elements from other directions (which are dealt with in aggregate)"
        #    "output_template": "## Tool Use\n### Key findings\n- ...\n### Failed Mode\n- ...\n### Source\n- ..."},
        #   ...
        # ]

        # Step 2: Parallel implementation
        results = parallel_execute(
            plan.subtasks,
            lambda st: self.workers[st.worker].execute(
                task=f"Research{st.topic}.Scope:{st.scope}.Exclude:{st.exclude}."
                     f"Output format:{st.output_template}",
                tools=["search_notes", "web_search"]
            )
        )
        # results Worker failed or timed out returns None without blocking other Worker

        # Step 3: Supervisor Summary
        # Critical operations: weighting, conflict identification, missing labels, synthesis
        final = self.supervisor.synthesize(
            task=task,
            worker_results=results,
            instructions="""
            Summary rules:
            1. If two Walkers make conflicting conclusions about the same subject, → It's not automatic.
            2. If a Worker overtime or failure → It says, "The data is missing."
            3. Weight: Same found merger, indicating which is from Worker
            4. Final output organized according to a unified structure, do not spell Worker original
            """
        )
        return final
```

### 8.4.2 Dismantling quality determines the value of the whole model

The most easily underestimated step of the Supervisor model is the dismantling. A lot of it has been done to simplify dismantling to "let LLM divide tasks into several" -- and then it's discovered that the worker output is highly overlapping, inconsistent in format and unable to merge.

Good dismantling takes four things: **1. Clear borders (include)** Not only "your research A, your research B," but also to say, "Don't touch anything."

```text
Bad dismantling:
  Worker 1: Research Tool Use
  Worker 2: Research Multi-Agent
 → Both Walkers are writing about "Tool Use's application in Multi-Agent"
 → 30% Overlapping

Good disassembly:
  Worker 1: Research: Design models, failure models and framework realization for Tool Use
            exclude: Not involving Tool Use in Multi-Agent collaboration (covered by Worker 4)
  Worker 2: Research Multi-Agent collaboration model, communication protocol and failure model
            exclude: Tool Use mechanism that does not involve individual Agent (covered by Worker 1)
```

**2. Unified output template** Each Worker must output with the same structure, otherwise Supervisor cannot merge automatically.

```text
Output template (all Worker shared):
## {Research orientation}
### Key findings
- Found 1 (1-2 sentence)+ Source Reference)
- Found 2
### Failed Mode
- Common failure 1 (performance)+ Reason+ Revised direction)
### Recommended practice
- Practice 1 (applying scenes)+ No scene applicable)
### Source Reference
- [Source 1](Link or Note Path)
```

**3. Worker Capability Match** Not all Walkers should be the same model. Research-type Worker may require a strong search capability (networked search, context) and analytical-type Worker may require a strong reasoning capability. assigns the right task to the right workker.**.4. Control of the particle size of dismantling** It was too detailed (10 subtasks) and the cost of communication and aggregation exceeded the implementation benefits. It's too coarse (2 subtasks) and insufficiently parallel. An empirical rule: **Number of sub-tasks = Min (number of separate dimensions that can be used in parallel, number of workr, 5)**. Marginal gains over 5 sub-tasks are generally insufficient to cover coordination costs.

### 8.4.3 Costs of consolidation - "Three Walkers ran out, Supervisor took longer to merge."

This is Supervisor's classic roll-over scene:

```text
Scene: Users ask for "Research, Agent Memoory's Recent Practice."
Supervisor Disassembly into 3 subtasks → 3 Worker in parallel

Timeline:
├─ Worker 1 Research on short-term memory (45 seconds)
├─ Worker 2 Research on Long-Term Memory (50 seconds)
├─ Worker 3 Study "Memory Frame" (40 seconds)
│  Parallel time: 50 seconds✓ Faster than a string.
│
├─ Supervisor Start consolidation (60 seconds)← That's the problem.
│  Why??Because of three worker outputs:
│  - Worker 1 3 pages Markdown+ Detailed analysis+ Code Example)
│  - Worker 2 Five points out.+ 1 Table
│  - Worker 3 Output list of 8 frames (no analysis)
│  The format is completely different, the structure is completely different and the coverage overlaps considerably.
│  Supervisor Unable to "Auto Merge"——It's actually getting LLM to recombine.
│  Three reports, and if this integration is done by one Agent from the beginning,
│  Probably just need 70 seconds.
│
├─ Total time: 50 seconds (in parallel)+ 60 sec (merger)= 110 sec
│  Serial time: about 120 seconds (3 directions)× 40 sec+ Natural summary 10 seconds)
│  Parallel gains: almost zero. Three times the complexity, 10 seconds.
└─

Root: No output template was specified when dismantling. Three Walkers each output according to their own understanding.
      Combined costs offset parallel gains.

Restoration:
1. Force a uniform output template when dismantling (structure, fields, length limits)
2. The output length of each Worker is contained in 300 words (prohibits output "overview" and "background introduction")
3. Worker Just output "post-extract information" without synthesis and summary.——The integration is the responsibility of Supervisor.
```

**The core lesson of the rollover**: The parallel value is not "Worker runs fast", but **"Worker's output can be combined directly, without LLM understanding and synthesis"**. If combining steps requires LLM to read through all Worker outputs and "rewrite them," then let one of the Agent write from the beginning.

### 8.4.4 Obsolete boundary of Supervisor

| Expiry Mode | Performance | Gene. | Amendments |
|---|---|---|---|
| Dismantling border blur | Worker output 30 per cent | No exclude range defined when dismantling | Each submission with a clear exclude statement |
| Format Unharmonized | Worker output cannot be automatically merged, Supervisor needs to be re-integrated | No output template | Force the output template when dismantling (enable Worker to play freely in the template) |
| Worker failed to complete the report | Worker 2 timeout, Supervisor pretended to have completed all four directions. | There was no "data missing" in the summary. | Compulsion of aggregation rules: Failed Worker's corresponding orientation label "Default of data, cause: {overtime/ error} |
| Parallel Shape | Dismantling itself took 30 seconds. | Dismantling logic relies too much on LLM decision-making | Predefined breakup template: common tasks are fixed to break down dimensions and LLM is adjusted only in case of anomalies |
| Supervisor becomes a bottleneck. | Five. Walker's waiting for Supervisor's dismantling. | Dismantling and distribution are a series. | For standard tasks, use predefined dismantling (cachel), skip LLM dismantling |

---

## 8.5 Parallel Specialists: same mission, multiple eyes

Each Worker of Supervisor handles different tasks. Parallel Specialists is a variant: **The same task, with multiple experts analysing it from different dimensions at the same time and then combining it.**

### 8.5.1 Distinction from Supervisor: same input, different dimensions

```text
Supervisor Mode: Parallel Specialists:

Task A → Worker 1                   Same job.
Task B → Worker 2                         │
Task C → Worker 3               ┌─────────┼─────────┐
                                ▼         ▼         ▼
Different Specialist A Specialist B Specialist C
                                (Correctability (security) (performance)
                                    │         │         │
                                    └─────────┼─────────┘
                                              ▼
                                          Merge Results

Different dimensions, same input
```

Application scenario: A code requires both correctness, security and performance. A programme needs to assess both technical feasibility, cost and maintenance. A response requires simultaneous examination of factual accuracy, logical completeness and clarity of presentation.

### 8.5.2 Cross-dimensionalization is a parallel premise

A central prerequisite for the success of this model is the non-dependence of **dimensions.** If performance analysis requires first knowing the conclusions of correctness analysis, then it cannot go in parallel — it has to run correctness before running performance.

The dimensions design requires two conditions:

1. **Overlapping**: no overlap of attention per dimension. If "right" and "safe" both analyze input validation, 60% of the content repeats.
2. **Independent**: the result of each dimension can be concluded by simply entering + its own focus, which does not require other dimensions.

```python
class ParallelSpecialists:
    """Multiple experts handle different dimensions of the same task."""

    def __init__(self, specialists: dict[str, Agent]):
        self.specialists = specialists

    def run(self, task: str, dimensions: list[dict]) -> dict:
        """
        dimensions = [
          {"name": "correctness", "agent": "code_reviewer",
           "focus": ""Logical error, border conditions, anomalies, state consistency."
           "exclude": "No analysis of security gaps and performance bottlenecks."},
          {"name": "security", "agent": "security_auditor",
           "focus": "Injecting risk, leaking key, crossing authority, exposure to sensitive data."
           "exclude": ""do not analyse logical errors (even if it may lead to uncertain behaviour)"},
          {"name": "performance", "agent": "perf_analyzer",
           "focus": "Time complexity, space occupation, I/O bottlenecks, cache strategy,
           "exclude": "No analysis of correctness and safety effects."},
        ]
        """
        # Parallel implementation
        results = parallel_execute(
            dimensions,
            lambda d: self.specialists[d["agent"]].analyze(
                task=task,
                focus=d["focus"],
                exclude=d["exclude"]
            )
        )

        # Merge: Heavy+ Organisation+ Conflict Identification
        return self.merge(results, dimensions)

    def merge(self, results: list[dict], dimensions: list[dict]) -> dict:
        """Merge multi-dimensional analysis results."""
        all_findings = []
        conflicts = []

        for i, result in enumerate(results):
            for finding in result.findings:
                finding["source_dimension"] = dimensions[i]["name"]
                all_findings.append(finding)

        # Heavy: Same position+ Description of the same problem → Merge in one with the label from multiple dimensions
        deduped = self._deduplicate(all_findings)

        # Conflict detection: if two dimensions give conflicting judgements about the same location
        # Example: Specialist A says, "The design here is safe."
        #     Specialist B Say, "There's a risk here."
        # → It's not self-resolved.
        conflicts = self._detect_conflicts(deduped)

        return {
            "findings": deduped,
            "conflicts": conflicts,  # Mark but not solve automatically
            "dimension_summary": {
                d["name"]: len(r.findings) for d, r in zip(dimensions, results)
            }
        }
```

### 8.5.3 Consolidation rule: conflict does not automatically abate

The most dangerous moment for Parallel Specialists is integration. When two experts make conflicting judgements, the easiest mistake is to allow LLM to choose automatically -- for example, "take a majority" or "let Supervisor decide."

But this auto-dissociation will mask the real problem. If one expert says "safe" and the other says "a loophole," that means at least one expert has a problem with analysis -- Maybe one of them's focus definition is not clear enough, maybe one of them lacks the key context. Automatically choosing "majority" just covered up the problem. **Consolidation rules**:

1. **The same finding automatically removes weight**: two experts identified the same problem (the same location + the same type of problem) and merged it into one article, marked from two dimensions.
2. **Contradictory judgement does not automatically abate**: labeled as "Different analysis of security dimensions requires manual review" with the specific basis of two experts.
3. **Source notation**: Each discovery indicates the dimensions from which the discovery was made, so that the reader knows what perspective the discovery was made.

A common failure of this model:

| Expiry Mode | Performance | Amendments |
|---|---|---|
| It's a repetition of dimensions. | "Rightness" and "security" experts, 60 percent of the output overlaps. | Clear range of focus and exclude for each dimension |
| Merge Lost Conflict | Specialist A says safety, specialist B says there's a problem. | The merger rule is clear: conflict labels are not abated |
| Too many parallels. | Eight specialists, API, and a limit to trigger limit. | ≤5 dimensions; grouping in parallel when exceeding 5 dimensions |
| Some expert's too soft. | "Performance" expert output, no apparent performance problem. | Review whether the expert dimension definition of Focus gives enough specificity to the check item |

---

## 8.6 Agent's settings and configurations -- how "different" landed.

8. 2 The four dimensions of Multi-Agent split were described: different inputs, different tools, different targets, and different acceptance standards. 8.3 to 8.5 The structural design of three modes of collaboration is described. But structural design only solves the question of how to organize between Agents, and it doesn't solve a more advanced question: **How each Agent is configured to make them really different?**

### 8.6.1 Write Agent settings instead of Prompt

Multi-Agent's first step is to open the editor to write

```text
You're a researcher.
You're an engineer.
You're the censor.
```

It's too early. Prompt is part of Agent's configuration, but not Agent's setting itself. What really should be written first is an **Agent setup card**: it's like a job description, like a running time configuration list. It places duties, inputs, tools, models, parameters, output protocols and failure processing in the same place so that you can judge whether this Agent is really different from other Agents.

Here is an example of a set card for Reviewer Argentina:

```yaml
agent: security_reviewer
responsibility: Only review of security risks and no modification of products
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
  reason: Need for stable compliance with review lists and structured outputs without high creativity
parameters:
  temperature: 0
  max_tokens: 1000
output_schema: ReviewResponse
acceptance:
  - Each FAIL must contain the localization and evidence
  - Uncertainty cannot be guessed, must be marked
fallback:
  - Enter human review when two rounds of amendment are still pending
```

This one's not the key. `agent` Name, but a few sets of constraints:

- **Boundaries of responsibility**: it is responsible for what, not what. Reviewer only reviews and does not change; Supervisor only dismantles and aggregates and does not replace Worker research.
- **Enter boundary**: it can see anything, it can't see anything. Reviewer could not see Author ' s draft and self-defence, which was a prerequisite for an independent review.
- **Tool boundary**: What tools can it call. Nothing. `write_file` The authority's Reviewer, it's not subject to revision.
- **Model boundary**: what capacity it requires. Not all Agents use the strongest models, but match model capabilities by duty.
- **Export boundary**: it must be delivered by what schema. Without structured output, after that, Agent can only re-understand a natural language.
- **Failed boundary**: What happens when it fails. Retesting, downgrading, changing models, handing over people must be defined in advance.

If an Agent set card can't be written, this Agent is not clearly designed. This is the time to continue writing Prompt, which only creates a text actor who looks like a character and actually has no boundaries.

### 8.6.2 Mapping with four dimensions

| Dimensions | Project Configuration Tool | Take Author + Reviewer, for example |
|---|---|---|
| **Entered differently** | Context range declaration in System Prompt + information filter in Runtime | The context of Author contains the results of the notes search, the history of the creation, the draft. Reviewer context is only injected into the final scenario + review criteria filtering out all middle reasoning of Author |
| **Different tools** | Agent Class White List in Tool Registration Table | Author is registered to write file, search notes, web search. Reviewer registers only read_file, run security scan -- no write permission |
| **Different goals** | Task definition in System Prompt + description of success criteria | Author: "Technology of output to meet demand, covering all demand points". Reviewer: "Find out all problems that do not meet safety standards, give location and evidence by article." |
| **Different acceptance standards** | Output Schema binding + cessation condition | Author's output is not mandatory. Reviewer output must be `{verdict, checks[], issues[]}`,verdict has two values only. |

The above table is a quick look map. Below is an itemized list of specific practices and common errors for each configuration dimension.

### 8.6.3 Systems Prompt Design -- not just "rename."

The most common spelling is:

```text
# Author
"You are a technical programme writer, please write a complete technical programme according to demand."

# Reviewer
"You're a security examiner, please review the security of this technical program."
```

These two Prompt differences are only character names and verbs. They have no definition: what the Reviewer is specifically concerned with, what criteria to judge, what the output must contain, and what to do when it is uncertain. The result is that Reviewer is no different from the individual Agent -- it only knows its name as "censor," but it doesn't know what the censor should do. **Effective Systems Prompt must define five elements.** The following is an example:

```text
# Reviewer Agent — System Prompt Structure

## 1. Identity and terms of reference (whatever, whatever)
"You're a security inspector. You are solely responsible for reviewing technical options from a safety perspective.

You're concerned about input validation, key management, permission model, relying on security, data protection.
You don't care: technical feasibility, code quality, architecture design, performance optimization——
You don't have to mention it in your review."

## 2. Enter instructions (what you can see, nothing you can see)
"You'll get a final version of the technology program.

You will not see the drafts of the programme, the minutes of the discussions, the reasoning of compromise.
You can judge only on the basis of the final programme text and the review criteria.
If you see in the program a description of 'for convenience', here's an explicit description.——
Not as a 'reasonable temporary solution', but as a 'security loophole'.
Your judgment is not softened by the author's intentions."

## 3. Review criteria (article by article, verifiable)
"You must examine the following criteria article by article. Each article is accompanied by a verification method.——You have to actually perform the validation.
It cannot be judged solely by the language of the programme.

C1: Enter Validation
    Standard: Does all user input points declare length and type verification?
    Validation: View the input scheme defined by the API, confirming that each parameter has type and max legth.

C2: Key Management
    Standard: Whether all keys and sensitive configurations are stored in environmental variables or key management services Medium?
    Authentication: search program text and key in profile=、secret=、password= Literally.
          If Hard Encoding Value Found → FAIL.If Reference Environment Variable → PASS.

C3: Permission Model
    Standard: Is there a non-admin role definition?Whether to follow the principle of minimum competence?
    Validation: Check if multiple roles (e.g. read/write/admin) are defined in the program.
          and whether each operation states the minimum powers required.

C4: Reliance on security
    Standard: Third-party reliance on locking in version numbers?
    Validation: Check version declaration formats in requirements.txt or equivalent files (== Still?>=)."

## 4. Output format (compulsory structure)
"Your output must be a JSON object and cannot contain other text:
{
  "verdict": "approved" | "rejected",
  "checks": [
    {
      "id": "C1",
      "passed": true | false,
      "evidence": "What did you find in the program?
                   Support your judgment. If you can't find enough information to fill in 'insufficient information'.
    }
  ],
  "issues": [
    {
      "id": "I1",
      "description": "Description of specific issues (not subjective evaluation, fact statement),
      "location": "File name: Line number,
      "severity": "must_fix" | "should_fix",
      "suggestion": "Proposed amendments, no more than two words."
    }
  ]
}

The output of the `overall evaluation' summary' suggested further discussion is not allowed.
If something's unsure, passed as false, evidence is why it's not.——
It's better than putting it wrongly as true."

## 5. Boundary behaviour (what to do when uncertain)
"The following shall be dealt with in accordance with the rules and shall not be exercised on their own:

- Program does not have sufficient information to judge an inspection item → passed=false,evidence='insufficient_information'
- The program says, "Have followed best safety practices" without specifying → It's not equal to PASS.
  What you need to prove is what you actually did, not what you claim to do.
- If issue severity is unclear between must_fix and should_fix:
  Treat it as must_fix; only manual review may downgrade it.
- If you find a security issue that is not on the checklist:
  Still report it, mark severity as should_fix, and note that it is outside the checklist but worth attention.
```

**Design principles for five elements**:

- **"Whatever" is more important than "whatever."** It not only prevents Agent from crossing the border (Reviewer evaluated the quality of the code), but also narrows the focus of Agent to focus on its own responsibilities.
- **The review criteria have been changed from "assessment" to "inspection availability".** "Check the safety of the programme" is an assessment — vague, subjective and susceptible to general impressions. "The existence of key = volume in the text of the search program" is to check existence — specific, objective and without judgement.
- **Border behavior defines Agent's character**. Do you guess when you're not sure? When you see a vague statement, when you're in evidence or when you're asking questions? These are not technical parameters, but determine the reliability of Agent. A Reviewer that'll guess is more dangerous than no Reviewer -- its miscalculation will be considered "reviewed through".

### 8.6.4 Allocation of tools — white list, not "please don't use"

The most common error in the distribution of tools in Multi-Agent is the registration of the full volume set for each Agent, and then the System Prompt says, "Please use only the tools you need."

It's equivalent to giving every employee access to all lock cards, and then a note says, "Please just go into your room." System Prompt is a suggestion, tool registration is hard. The proposal can be ignored by the model (especially when the model considers that "a better task can be accomplished with this tool"), and not by hard restraints. **Correct practice: white list.** Every Agent only registers the tools it needs, and the tools that are not on the white list don't exist for it -- Runtme directly rejects the tools at the level of their call, and the models don't even know the tools exist.

```python
# Tool registration: white list
# When each Agent is created, only the tools it needs are passed on——Not full load and constraints by Prompt

AGENT_TOOL_WHITELIST = {
    "author": {
        "search_notes",      # Retrieving notes——We need information.
        "web_search",        # Network Search——We need an update.
        "read_file",         # Read Files——Need reference to existing documents
        "write_file",        # Write Files← Author Unique, output needs to be durable
    },
    "reviewer": {
        "read_file",         # Read Files——Read Author output
        "search_notes",      # Search safety code——Safety standards
        "run_security_scan", # Clear scan.← Reviewer It's unique, Author. No.
        # Note: no write file——Reviewer Unable to modify Author output
        # Note: no web search——Reviewer No external information required
    },
    "supervisor": {
        "read_file",         # Worker Output
        # Note: no write file——Supervisor Output summary report only, without modification of original document
        # Note: No search——Supervisor No research. That's Walker's job.
    },
    "worker_researcher": {
        "search_notes",      # Retrieving notes
        "web_search",        # Network Search
        "read_file",         # Read Files
        # Note: no write file——Worker Only output analysis to context.
        #       Do not modify the file system
    },
}
```

**Iron law for the distribution of tools**:

1. **Agent can perform a dangerous operation and can't approve it at the same time.** Write file and approve deploy are never the same Agent. Merge pr and code review will never be the same Agent. It's not just security considerations -- when the same Agent can "do" and "do" it, it takes a shortcut: do it, do it.
2. **The output tool is registered only on the necessary Agent.** In a 3-Agent system, there is usually only one Agent that needs write file privileges. The output of the other Agent is sent back to the caller by a communication protocol, which determines whether or not to last.
3. **When it's not clear whether or not to register a tool for an Agent.** The after-action tool is easy (add a line to the configuration) and it is difficult to recover afterwards (Agent may have relied on that tool to develop a certain pattern of behaviour).

### 8.6.5 Model selection - not all players need the strongest model

Not all Agent needs the strongest and most expensive model. The demand for modelling capacity varies from one actor to another. If all Agents use the same model, you're not only wasting money, but you're also likely to undermine the system's reliability.

| Agent Role | Core competency requirements | Model selection recommendations | Rationale |
|---|---|---|---|
| **Executor / Author** | Long text generation, creative expression, integration of multi-source information | The strongest model | Output quality directly impacts the end result, with the highest returns on inputs |
| **Reviewer** | Detailed comparison, article-by-article check, following structured output format | Medium-power model focusing on command compliance and structured output | No creativity is needed. What is needed is "not to miss the check" and "not to fabricate evidence". temperature should read 0 |
| **Supervisor (dismantling phase)** | Mission analysis, structural design, boundary definition | The strongest model | Dismantling quality determines the quality of all work and the total cost of the task. There's an extra $ 0.02 to save Worker. |
| **Supervisor (consolidation phase)** | Reload, formatting, conflict labels | Medium Model | Mainly structural operations - contrast fields, merge lists, check formats. There's no need for in-depth reasoning. |
| **Worker (research)** | Retrieve + Summary + Output by Template | Medium model, need search tools Okay. | Speed is a priority, requiring multiple running in parallel and cost-sensitive. Output quality is subject to template rather than model capacity |
| **Worker (analytical)** | Deep reasoning, multistep analysis | Strong Model | Quality analysis determines the quality of decision-making. If Worker's analysis is the basis of Supervisor's decision, it's hard to save input here. |
| **Debate Participants** | Arguments, rebuttals, multidimensional thinking | Strong Model | Weak models are easy to miss or get into text games in Debate. But if it's just the "singing back" role, you can use the medium model. |

The above table selects the model by the Agent role. There's a different angle to be taken into account in the actual project: **What is the strength of the bottom model?** "The Strong Model" is not a single dimension. A model may be strong in reasoning but weak in code, may have long context but inconsistent in following instructions, or may be cheap and fast but not suitable for final adjudication.

Dismantling by capacity type makes model selection clearer:

| Model capacity type | More appropriate, Agent. | Not suitable, Agent. | Reason for selection |
|---|---|---|---|
| **Strong reasoning model** | Supervisor Dismantling, Planner, Risk Analyst, Complex Code Reviewer | Lots of simple workker, format conversions Argentina | Suitable for task decomposition, trade-offs, conflict judgement and implied risk identification; high cost, not for mechanical extraction |
| **Code-capable model** | Code Worker、Test Fixer、Code Reviewer | Word, brief summary, Agent. | Understand project structure, language API, test failure and boundary conditions; waste capacity for non-code tasks |
| **Context Model** | Research Worker、Document Analyst、Migration Planner | Shortlist Reviewer, One Step Tool Call | It's appropriate to read a lot of information and long documents; but the context is not the same as a more critical judgement, and the noise gets more. |
| **Strong Command Compliance Model** | Reviewer、Schema Extractor、Policy Checker | Creative Author, Open Brainstom Age | Suitable for fixed processes, fixed schema, article by article; low temperature, emphasis on stability rather than novel |
| **Low delay/low cost model** | Batch classification | Final adjudicators, complex planners | Fits to multiple, low-risk single task; error can be driven by a subsequent strong model or rule Stay. |
| **Multimodular Model** | UI Reviewer, Chart Parsing Worker, Screenshot QA Agent | Plain Text Protocol Merge | Value only when input contains screenshots, PDF pages, drafts; should not be used by default for all Agents |

Here is a practical judgement: **put the strongest model in the worst position of error, not all.** Supervisor debugging the task, leaving all workr running in vain; Reviewer missing the high-risk problem, making the user believe "passed"; and the final merger fabricated the conclusion, contaminating the final delivery. These positions deserve stronger and more stable models. On the contrary, tasks such as batch extraction fields, template filling, format conversions, i.e. error using a cheap model, are usually captured by a schema check or lower Reviewer. **A common rollover scene**: All Agents have created a "creative" version of the edifice under the téperature of 0.7, with the same model + téperature → Reviewer, which appears to be PASS, but two of the ividences are fictional and the whole review is more dangerous than it is without review (because the user trusts the mark that has been reviewed). **Reviewer's specialty**: Reviewer is the most intriguable character in Multi-Agent -- its judgment is the system's "quality gate". The Reviewer model does not need to be "smart." What is needed is "temperature 0", structured output enforcement, and evidence field requires specific filenames: line numbers. There are one or two imperfect solutions that Execut wrote -- users can fix themselves. Reviewer missed a security check -- users trusted the pass mark, which could lead to an online accident.

### 8.6.6 Easing of parameters — different roles, different parameters

The same model, different parameter configurations allow the same model to present completely different behavioural characteristics. Different roles in Multi-Agent need different parameter configurations:

| Parameters | Executor/Author | Reviewer | Supervisor | Worker (research) |
|---|---|---|---|---|
| **Temperature** | 0.3-0.7 | **0-0.1** | Dismantling 0.2-0.3 / Summary 0-0.1 | 0.1-0.3 |
| **Max Tokens** | Estimated by output x 1.3 | **Projected by structured output** (usually 500-1000, stop if sufficient) | Dismantling 1024 / Summary 2048 | Estimated by template (usually 500-800) |
| **Stop Sequences** | No Special | JSON Ender `}` Stop After | Same Reviewer | Same Reviewer |
| **Top P** | 0.9-0.95 | **1.0**(certainty) | 0.95-1.0 | 0.95 |

**Key decision-making for parameter design**:

- **Reviewer's temperature must be zero or close to zero.** This is the most easily neglected but most influential configuration. When temperature is not 0, the Reviewer field runs different text each time it runs -- This means that the two reviews of the same programme may have different results. For "Quality Gate", certainty is much more important than creativity.
- **Max Tokens isn't "ceiling," it's "budget".** Too many max tokens set for Reviewer will not allow it to review more carefully -- it will start "additional" after the output of the structured results, "recommends" "commends". Sets just enough max tokens to tell the model: "Exit the requested structure and stop."
- **Supervisor disassembly and aggregateture should be different.** Dismantling requires some flexibility (the decomposition dimensions of each task are not identical), but aggregation requires certainty (the same worker output should have the same aggregate results).

### 8.6.7 Configuration management - from scattered locations to "configuration or code"

Three Agents managed manually okay. At five Agents, Systems Prompt, White List of Tools, Model Selection, Parameters are scattered in multiple files. Modifys the review criteria for Reviewer, forgetting that the summary logic of Supervisor is being updated simultaneously - the system is beginning to show subtle inconsistencies. **Recommended practice: Agent configuration centralized, Systems Prompt external documentation.**

```python
# agent_configs.py — Single fact source for all Agent configurations
# Modifys the configuration of any Agent only by changing this file.
# When adding an Agent, declare its full configuration in one place.
# When the code is reviewed, you can see "what configurations of Agent are affected by this change."

AGENT_CONFIGS = {
    "author": {
        "model": "claude-sonnet-4-6",
        "temperature": 0.4,
        "max_tokens": 4096,
        "system_prompt": "prompts/author_system.txt",  # External file, easy diff
        "tools": ["search_notes", "web_search", "read_file", "write_file"],
        "output_schema": None,  # Do not force structured output
    },
    "reviewer": {
        "model": "claude-sonnet-4-6",
        "temperature": 0.0,  # Determination——The mass gates can't be random.
        "max_tokens": 1024,  # Just enough to structure the output to prevent "addition"
        "system_prompt": "prompts/reviewer_system.txt",
        "tools": ["read_file", "search_notes", "run_security_scan"],
        "output_schema": "schemas/review_result.json",  # Force structured output
        "max_rounds": 2,  # Reviewer Specific control parameters
    },
    "supervisor": {
        "model": "claude-fable-5",
        "temperature": 0.2,
        "max_tokens": 2048,
        "system_prompt": "prompts/supervisor_system.txt",
        "tools": ["read_file"],
        "decomposition_strategy": "template_first",  # Predefined Template for Priority
        "merge_conflict_policy": "flag_not_resolve", # The conflict labels are overwhelming.
    },
    "worker_researcher": {
        "model": "claude-haiku-4-5",  # Research with cheap models.
        "temperature": 0.2,
        "max_tokens": 800,
        "system_prompt": "prompts/worker_researcher_system.txt",
        "tools": ["search_notes", "web_search", "read_file"],
        "output_template": "templates/research_report.md",  # Force Output Format
    },
}
```

**Three principles of configuration management**:

1. **System Prompt External Documentation.** No long strings to die in code. External files can diff ("What review criteria have been changed this time?"), review, roll back. When the system behaves abnormally, look at the latest System Prompt Diff -- the problem is not code change, it's Prompt change.
2. **The white list of tools is centralized on the configuration level.** A file with all Agent tool privileges. Add a new hazard tool (e.g. `delete_file` At the time, the examiner was able to see at first sight "what this tool has been assigned to Agent" -- not ten files of grep.
3. **Configure Change Walk Report.** Changed the review criteria for Reviewer? Changed Supervisor's dismantling strategy? These changes have no less impact than changes in business codes. One review criterion was changed from "Check if there's a specified key" to "Check if there's a key management service"? - Looks like a change in the sentence, which could actually result in the project being adopted. The risk of this change is comparable to the core business logic of the change.

## 8.7 Communication protocol-Agent cannot "what do you think?"

We've talked about the structure of the three modes of collaboration and how each Agent can be configured to be really different. How exactly do you communicate between the configured Agents? This is the most undervalued issue in Multi-Agent. Many systems are well designed for collaborative models, and Agent configurations are different, but they fall on communication protocols.

### 8.7.1 Why is free dialogue a disaster?

The most intuitive means of communication is to allow Agent to speak freely — as human beings do, you talk to me. This is the Group Chat mode: multiple Agents speak freely in a shared conversation.

However, in Multi-Agent, free dialogue is the most expensive, difficult to debug and the easiest to fail. There are three reasons: **1. Information decay.** The original message declines every time it passes between Agent. AgentA's discovery was repeated by AgentB, and then by AgentC's quote - when it came to Supervisor, the original specific judgment became a vague impression.

```text
Original: "config.yaml 8th row api key field is clear, there is a risk of leakage"
↓ Agent B Repeat:
"A The key management issue was mentioned in the configuration file."
↓ Agent C References:
"The previous discussion involved security considerations."
↓ Supervisor Received:
"The team discussed safety."← Original message completely lost
```

**2. Intentional distortion.** One Agent says "recommended optimization", the other Agent understands "must optimization". The word "recommended" and "must" distinguish between human communication, and the word between Agent is easily lost.**3. Blur decision-making.** Free dialogue has no "decision point". Agent can keep talking about "consent" and "complement" and "advice" and "further consider" -- no one says "discussion is over, and the following is a decision." The final output was not a decision-making exercise, but a summary of the discussions.

### 8.7.2 Design communication formats by collaborative mode

Alternatives to free dialogue are **structured communications**. This is not the definition of a low-to-high protocol hierarchy, but rather the translation of three of the previously mentioned collaboration models into a specific message format: Reviewer needs to review worksheets, Supervisor needs task sheets and reports, and Paallel Specialists needs to show results with dimensions. **Reviewer mode: command-response** Reviewer should not have received a sentence "Look at this program for me," but rather a review sheet. It's clear in the worksheet: what to review, what criteria to review, how to give evidence after failure.

```json
{
  "type": "review_request",
  "artifact": "API Design v1",
  "context": {
    "user_goal": "Design a query API for the internal knowledge base.",
    "constraints": ["Do not expose unauthorized documents.", "Response time must be under 2 seconds."]
  },
  "criteria": [
    {
      "id": "security.authz",
      "check": "Document-level permission verification is specified.",
      "how_to_verify": "The design must state the permission source, check location, and failure response.",
      "severity": "must_fix"
    },
    {
      "id": "reliability.timeout",
      "check": "Timeout and fallback strategies are defined.",
      "how_to_verify": "The design must specify timeout, retry count, and user-visible fallback behavior.",
      "severity": "should_fix"
    }
  ]
}
```

Reviewer's response will be equally rigid. Note that there is no "overview" field, because "overall is okay" is the kind of bullshit that is the easiest to hide.

```json
{
  "type": "review_response",
  "verdict": "rejected",
  "checks": [
    {
      "check_id": "security.authz",
      "passed": false,
      "evidence": "The design only says 'connect to the access system later' and does not specify the check location or failure response.",
      "suggestion": "Add permission sources, pre-check points, and error responses for missing permission."
    },
    {
      "check_id": "reliability.timeout",
      "passed": true,
      "evidence": "Section 4 defines a 2-second timeout and cache fallback.",
      "suggestion": null
    }
  ],
  "issues": [
    {
      "id": "issue-001",
      "location": "Section 3: Permission Model",
      "severity": "must_fix",
      "description": "Permission verification is only promised and is not part of the request chain.",
      "suggestion": "Replace 'connect to the access system later' with an enforceable permission verification process."
    }
  ]
}
```

This format is suitable for quality gates: security clearance, front-line inspection, programme acceptance, code review. It is characterised by the fact that **both input and output are binding** and Agent cannot circumvent judgement in natural languages. **Supervisor Mode: Template - Fill** When Supervisor dismantles the mission, don't just say, "You go to the research vector database." It should give Worker a filled list of tasks: what to do, what to do, what to deliver.

```json
{
  "type": "subtask_assignment",
  "task_id": "research-vector-db",
  "worker": "researcher-1",
  "topic": "Vector database selection in a RAG system",
  "scope": "Only compare applicability of Milvus, pgvector, and Pinecone.",
  "exclude": "Do not cover vector search algorithms or market background.",
  "output_template": {
    "key_findings": "Up to 3",
    "failure_modes": "Up to 2",
    "recommended_use": "One sentence describing the best-fit scenario.",
    "sources": "List Quote Sources"
  },
  "max_length": 300
}
```

Worker, when you return, do not write a long, freely developed text, but complete the template:

```json
{
  "type": "worker_report",
  "task_id": "research-vector-db",
  "status": "completed",
  "content": {
    "key_findings": [
      "pgvector fits teams already using Postgres and has the lowest migration cost.",
      "Milvus fits large-scale vector workloads with high search performance requirements.",
      "Pinecone fits teams that want to reduce self-hosting operational burden."
    ],
    "failure_modes": [
      "Only evaluates search features and ignores data synchronization and permission filters.",
      "The premature introduction of an independent vector database increases the complexity of transport."
    ],
    "recommended_use": "If the team already uses Postgres, first build a baseline with pgvector.",
    "sources": ["Official docs", "Project README", "Engineering practice articles"]
  },
  "error": null
}
```

This format is suitable for parallel research and aggregation. It doesn't have the Reviewer so rigid, but it limits the output shape through templates to avoid three different reports from Walker. **Parallel Specialists Mode: Dimensions - Mark** The key to Parallel Specialists is not "talk to each other", but to each discovery with its source dimension. In this way, Supervisor is able to focus on the conflict, rather than drawing a vague summary of different perspectives.

```json
{
  "type": "dimension_analysis",
  "dimension": "security",
  "findings": [
    {
      "id": "sec-001",
      "location": "/login",
      "severity": "must_fix",
      "description": "The login interface does not specify failure-count limits.",
      "evidence": "The scheme only describes the account password verification, and does not mention the rate limit or lockout."
    }
  ]
}
```

The result of the merger would also be to retain the structure. If two dimensions make the opposite judgement of the same position, not automatically "cut off" but expose the conflict.

```json
{
  "type": "merge_result",
  "findings": [
    {
      "id": "sec-001",
      "dimension": "security",
      "location": "/login",
      "severity": "must_fix",
      "description": "The login interface does not specify failure-count limits."
    }
  ],
  "conflicts": [
    {
      "location": "/login",
      "finding_a": "Security: failure-count limit is missing.",
      "finding_b": "Performance: additional checks may increase latency.",
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

This format is suitable for a multi-perspective review of the same product: correctness, safety, performance, cost, user experience. It does not focus on reaching agreement among multiple Agents, but rather on allowing different dimensions of judgement to be tracked, merged and adjudicated. **Core principles of structured communications**:

- **Not accepted as "comprehensively all right"**: the results of the review must be specific, article-by-article and supported by evidence.
- **Free text only appears at leaf node**: the description may be a natural language, but the "bones" of communication (state, type, location, severity) must be structured fields.
- **Missing field is better than created field**: If Reviewer cannot find evidence, it is not possible to find evidence. `evidence ` Field Filling ` "not_found"` Instead of fabricating a description that sounds reasonable.
- **Human readable track**: Structured communication creates a searchable track -- you can grep `"verdict": "rejected"` All rejected reviews are found and the pass rate for each review item is measured.

### 8.7.3 From internal communications engagement to Agent protocol

Designed in front of this section `review_request ` 、` worker_report ` 、 ` dimension_analysis`, an internal communication agreement. It is usually sufficient for real projects to do so at an early stage: clear fields, clear status, clear product and clear reasons for failure.

But when Agent no longer exists in the same code library, the same frame, the same team, the problem goes up further: how does one Agent find another? How do you know what they can do? How is tasking, tracking status, receiving results, handling failures? This requires a more standardized Agent communication protocol.

After 2025, there have been some related attempts in the industry:

- **MCP (Model subject Protocol)**: mainly addresses how Agent standardizes connectivity tools, data sources and context.
- **A2A (Agent2AgentProtocol)**: mainly addresses how different Agents discover, commission, exchange information and return products.
- **Agreements such as ACP / ANP are explored**: an attempt to address Agent communications, identity, discovery, multi-modular messages and cross-platform interoperability from different perspectives.

The common direction of these agreements is not "to make Agent more free to talk," but the opposite: to tear out the vague parts of the natural language and turn them into verifiable objects of agreement, such as capability descriptions, task status, type of message, product, error and permission.

For most business projects, full industry agreements need not be introduced at the outset. The more realistic path is:

1. Clear definition of structured communication formats within the system;
2. When the number of Agents, team boundaries, tools become more ecologically complex, standard agreements such as MCP/A2A are considered;
3. Don't treat the agreement as a reliable substitute, it only solves "how to communicate", it doesn't automatically solve "who can trust, who decides, when to stop, what to do wrong."

## 8.8 award, suspension and background - Multi-Agent 'Rules of Traffic'

The collaboration model defines how Agent divides, the communication protocol defines how Agent communicates information. But there is a third level: **the control mechanism** — who decides when, when and how?

The Multi-Agent system without this layer is not a "decision-making system" but a "discussion group" -- it's probably a good discussion, but nobody boarded it.

### 8.8.1 Adjudication mechanisms: who rules when differences arise

There are three types of disagreement in the Multi-Agent system, each of which requires different methods of adjudication:

| Type of disagreement | Typical scene | Method of award | Why can't we just digest? |
|---|---|---|---|
| Reviewer vs Executor | Reviewer ruled Fail, Execuator, that "it's not a problem." | After two rounds of amendment, no manual decision was passed. Exportor should not have the power to overrule Reviewer's judgment | Allowing the subject to rule on the examiner is tantamount to cancelling the review |
| Worker vs Worker | Worker 1 says, "Framework A supports current output," and Worker 2 says, "No support." | Checks source references. Quoted confrontation (who is more authoritative). It's not clear from the source that there's a difference of fact. | The facts need to be traced, not voted. |
| Worker vs Worker | Specialist A says "safe," Specialist B says, "a gap." | Mark conflict manual review. No automatic vote or "majority." | To judge conflict means that at least one person has missed or missed it, and it requires a fresh look at it. |

**Principles for the design of adjudication mechanisms**:

1. **The adjudicator cannot be a party**. Exportor cannot rule on the reasonableness of the review by Reviewer. Worker cannot rule on the correctness of his output.
2. **Manual decision superiors automatic decision**. When two Agents make contradictory judgements, it is safer to suspend and request human intervention, rather than to allow the third Agent to "vote" -- the third Agent could also make mistakes.
3. **The award requires a "final deadline".** Tasks cannot be blocked indefinitely by waiting for a manual decision. Set timeout: Manual decision exceeding N minutes does not respond to the most conservative choice (e.g. Reviewer 's judgement gives priority or suspends the mission and keeps the site).

### 8.8.2 Conditions for cessation: not unlimited return

Multi-Agent's suspension conditions are similar to those of Reflect, but there are more dimensions specific to collaboration:

| Conditions for discontinuation | Proposal for thresholds | Conduct at Trigger |
|---|---|---|
| Reviewer Number of round trips | 2 rounds after correction | Mark "disputed", manual ruling, not into Round 3. |
| Number of Supervisor summaries | 1 Dismantling - Summary | If the summary results are missing, do not reopen - label missing and output |
| Worker and timeout. | Maximum Worker time-consuming x 1.5 | The result of Worker's timeout is discarded, and the report indicates that the data is missing. |
| Total token consumption | Single task 50K tokens | Stop all Agents, return partial results completed |
| information sources | 3 consecutive rounds of communications with similar content > 90 per cent | Called "dialogue dead" and forced to stop and output the current state. |
| Error Upgrade | Recoverable error failure (e.g. network overtime becomes disk full) | Stop All Agent, keep the scene and notify the user |

**The conditions for stopping must be coded hard and cannot be decided by Agent itself.** Agent has no instinct to stop -- it'll still start a new round of communications confidently on the sixth round. The condition for cessation is a mandatory check on the Runtme layer, unrelated to Agent 's reasoning ability.

### 8.8.3 Bottom strategy: what if Walker dies?

When the Multi-Agent system is running, Worker Agent may fail for various reasons: API limit, network timeout, output unresolved, context spilling. The system must pre-empt every failure:

```text
Worker Failed mode, bottom strategy.
─────────────────────────────────────────────────────
Individual Worker Timeout → Drop the worker result
                           In the final report, mark "Specific X: Data Missing (over time)"
                           Do not try again, do not block other Worker outputs

Individual Worker Output Not Parsed → Attempt to regenerate once (only once)
                           Still unsolved. → Idem, mark "Default of data."

Multiple Worker also fails → Possible root cause is upstream (e.g. API failure)
(≥50% Worker Stop all implementation and return partial results+ Error diagnosis
                           No more.——It's probably just more token.

Supervisor Dismantling failed → If the dismantling programme does not meet minimum requirements (e.g., overlapping borders)>30%)
                           Decline to "Single Agent Direct Execution", Skip Multi-Agent
                           Notify user: "The quality of the dismantling program does not meet the parallel conditions and is downgraded"

Supervisor Synchronising folder → Returns original output for each Worker (labelled as "uncollected")
                           Do not try to reassemble LLM——Reason for failure in first aggregation
                           Could still be there.
```

**Core principle at the bottom: demotion without silence.** The system can be downgraded to single Agent if Multi-Agent is not available - but cannot pretend Multi-Agent is successful. Missing data, failed worker, skipping check items - all clearly marked in the final output.

---

## 8.9 The truth of the cost - not just Token's bill

Multi-Agent's costs are often underestimated because its head is not on a monthly API bill.

### 8.9.1 An estimated comparative bill

Take the example of the knowledge assistant writing technology program + security clearance mission, comparing typical consumption of the Agent and Reviewer models. The figures below are teaching estimates, which are used to train in cost dismantling methods and do not represent a fixed bill for a production system.

```text
═══════════════════════════════════════════════════════════════════
Mission: Write an API module technology programme (approximately 2000 words), review from a security perspective

Agent (self-review):
┌─────────────────────────────────────────────────────────────────┐
│ Writing phase:│
│   System Prompt: 800 tokens                                     │
│   User Input+ Context: 500 tokens│
│   Model output (programme): 2,500 tokens│
│   Subtotal: 3,800 tokens│
│                                                                 │
│ Self-review phase (same context, additional round):│
│   Could not close temporary folder: %s│
│   Model output (review): 300 tokens│
│   Subtotal: 400 tokens│
│                                                                 │
│ Total:~4,200 tokens                                             │
│ Time consuming:~40 sec│
│ Cost:~$0.06(Estimated with Claude Sonnet)│
│ Result: four security risks missed.│
└─────────────────────────────────────────────────────────────────┘

Reviewer Mode:
┌─────────────────────────────────────────────────────────────────┐
│ Author Agent(Independent examples:│
│   System Prompt: 400 tokens(Just create, without censorship logic)│
│   User Input+ Context: 500 tokens│
│   Model output (programme): 2,500 tokens│
│   Subtotal: 3,400 tokens│
│                                                                 │
│ Reviewer Agent(Independent example, independent context:│
│   System Prompt: 300 tokens(Just censorship, without creative logic)│
│   Write context (programmes)+ Review list: 2,800 tokens│
│   Model output (structured review results): 600 tokens│
│   Subtotal: 3,700 tokens│
│                                                                 │
│ Author Amendment phase (independent examples, only received issues):│
│   Write context (programmes)+ issues): 3,300 tokens                       │
│   Model output (amended scheme): 2,600 tokens│
│   Subtotal: 5,900 tokens│
│                                                                 │
│ Reviewer Second round of reviews:│
│   Writing context (modified scenario)+ Review list: 2,900 tokens│
│   Model output (review results): 300 tokens│
│   Subtotal: 3,200 tokens│
│                                                                 │
│ Total:~16,200 tokens(3.9 times the single Agent)│
│ Time consuming:~80 sec (2 times single Agent)│
│ Cost:~$0.22(3.7 times the single Agent)│
│ Result: All 4 security hazards identified and corrected│
└─────────────────────────────────────────────────────────────────┘

Cost-benefit analysis:
┌─────────────────────────────────────────────────────────────────┐
│ Additional costs:+$0.16, +40 sec│
│ Proceed: from "there are 4 security holes" to "through the security clearance list."│
│                                                                 │
│ If there is a security incident after the programme is deployed, repair costs>> $0.16            │
│       In this scenario, the extra cost is worth it.│
│                                                                 │
│ But if the mission is a low-risk internal memo,?                                │
│ The extra costs may not be worth it.——Not all scenes need Multi-Agent│
└─────────────────────────────────────────────────────────────────┘
```

**Key Insight**: Token consumption of Multi-Agent is usually 2-5 times that of single Agent. It's not "expensive" -- it's "additional token buys what." If it's the "Face Found" Agent's gonna miss four safety holes," then $0.16 is cheap. If it's "three Agents to discuss 12 rounds, but output is the same as single Agent", every penny is wasted.

### 8.9.2 Delay magnification: the real cost of communications travel

Multi-Agent's delay is not a simple "model reasoning time x Agent number". Real delays include:

```text
Reviewer Mode delayed dismantling:
┌──────────────────────────────────────────────────────────────┐
│ Author Argument: 30 seconds│
│ +                                                             │
│ Reviewer Inference: 25 seconds│
│ +                                                             │
│ Context Build and Transfer: 5 seconds│
│   (Output+ Review the checklist as input context for Reviewer)│
│ +                                                             │
│ Author Revised reasoning: 20 seconds│
│ +                                                             │
│ Reviewer Two rounds of reasoning: 10 seconds│
│ =                                                             │
│ Total:~90 sec│
│                                                                │
│ User perception delay: 90 seconds (from launch to accessed results)│
│ Agent self-review:~40 sec│
│ Delay Zooming: 2.25 times│
│                                                                │
│ Supervisor Mode delay (4 Worker parallel):│
│ Supervisor Dismantling: 8 seconds│
│ +                                                             │
│ Parallel Worker (lowest): 45 seconds│
│ +                                                             │
│ Supervisor Summary: 15 seconds│
│ =                                                             │
│ Total:~68 sec│
│ Serial (4)× 40 sec+ 10 Other Organiser~170 sec│
│ Accelerating ratio: 2.5 times✓                                              │
└──────────────────────────────────────────────────────────────┘
```

**Key to delayed optimization**:
- The Reviewer model is inherently slower than the single Agent - one more reasoned delay per round trip. Design to minimize the number of round trips (up to two rounds).
- The delayed benefits of the Supervisor model come from parallel. If the number of workingrs is small or the task is very different (one workingr 45 seconds, another 10 seconds), the acceleration effect is reduced.
- The time-consuming construction and transmission of the context is easily ignored - especially when the content is long (e.g. complete programme text).

### 8.9.3 Long-term costs: Trade complexity and difficulty of taking over

Multi-Agent's most hidden costs are not on the bill, on **maintenance**.

Three months later, when the new guy took over the system, Ta faced:

```text
Single Agent system:
├─ 1 Systems Prompt
├─ 1 Toolset
├─ 1 Track (linear execution record)
└─ Debug: Find the steps that are wrong → Fix Prompt or Tools

Multi-Agent System:
├─ 3 Systems Prompt (Author, Reviewer, Supervisor)
├─ 3 Tool sets (discrepancies)
├─ Multiple Cross-Traces (Agent A's output is Agent B's input), find out who introduced the error.
│   Need to flip 3 tracks and cross-check)
├─ Debugging: "Why is the final solution missing a security check??"
│ → Reviewer It's missing.
│ → Author Ignored during correction (check the track)
│ → Supervisor Missing during aggregation (check Supervisor track)
│ → A field in the communication protocol was misinterpreted.
└─ Change impact: change review list for Reviewer → A revision strategy that may affect Author
 → The logic of judgement that may affect Supervisor
```

It's not that Multi-Agent shouldn't be used. It says: **Should only be introduced if you are convinced that the additional maintenance costs can be covered by the value created by Multi-Agent.** If only Agent + good Prompt could do 90 points, the cost of introducing Multi-Agent for 95 points could be three times the maintenance complexity.

## 8.10 After-school exercise: Write Supervisor dismantling to implementable

**Corresponding section**: 8.4 Supervisor model, 8.7 Structured communications, 8.8 Bottom-up strategy. **scene** User request: "Help me study the latest practices in three Agent directions: Memoory, Tool Use, Multi-Agent. The key findings, common failure patterns, recommended practices and sources are exported in each direction."**Binding** - Up to 3 Walkers.

- Each Worker output does not exceed 300 words.
- Each Worker must give at least two sources.
- If a Worker is out of time, the final report cannot pretend that the direction has been completed. **Exit requirements** Write a Supervisor distribution plan in the following format:

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

**Criteria for eligibility** - Every submission. `scope ` and ` exclude`, and the scope of the three Workers cannot clearly overlap.
- `output_template` Must contain the "Key Discovery / Failed Mode / Recommended Practice / Source" field.
- `merge_rules` It was important to explain how to weigh, how to deal with conflicts of fact and how to identify sources.
- `fallback_rules` It is important to explain how the three scenarios of workingrker's timeout, non-resolveable output and insufficient sources are dealt with.
