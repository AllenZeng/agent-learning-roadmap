# Chapter 9: Combining Capabilities and Choosing the Right Order

[Return to Course 5](./course-05-01-scenario-enhancement.md) | [Previous Chapter](./course-05-08-multi-agent.md) | [Next: Course 6](./course-05-01-scenario-enhancement.md#connection-to-the-next-course)

## Chapter Outline

- [9.1 Do Not Add Every Capability at Once](#91-do-not-add-every-capability-at-once)
  - [9.1.1 A cautionary story: the big-bang rollout](#911-a-cautionary-story-the-big-bang-rollout)
  - [9.1.2 The hidden cost of every capability](#912-the-hidden-cost-of-every-capability)
  - [9.1.3 A ladder of capability complexity](#913-a-ladder-of-capability-complexity)
  - [9.1.4 The right rhythm is problem-driven](#914-the-right-rhythm-is-problem-driven)
  - [9.1.5 What counts as a minimal closed loop?](#915-what-counts-as-a-minimal-closed-loop)
- [9.2 Capability Combination Patterns](#92-capability-combination-patterns)
  - [Case 1: Personal knowledge assistant](#case-1-personal-knowledge-assistant)
  - [Case 2: Code review agent](#case-2-code-review-agent)
  - [Case 3: Personal task execution agent](#case-3-personal-task-execution-agent)
  - [Case 4: Customer support agent](#case-4-customer-support-agent)
  - [Case 5: Data analysis assistant](#case-5-data-analysis-assistant)
  - [Case 6: Writing collaboration agent](#case-6-writing-collaboration-agent)
- [9.3 Anti-Patterns in Capability Combination](#93-anti-patterns-in-capability-combination)
- [9.4 Timing and Signals for Gradual Adoption](#94-timing-and-signals-for-gradual-adoption)
- [9.5 Downgrading and Removing Capabilities](#95-downgrading-and-removing-capabilities)
- [9.6 Practice: Decide the Capability Roadmap for a New Scenario](#96-practice-decide-the-capability-roadmap-for-a-new-scenario)

---

## 9.1 Do Not Add Every Capability at Once

The knowledge assistant from Chapter 1.1 eventually accumulated seven different capabilities. But it did not start that way. Those capabilities appeared over several months of real use, one problem at a time.

In real projects, enhanced agent capabilities often do appear together. A personal knowledge assistant may need RAG plus Memory. A code review agent may need Tool Use, Reflection, and a reviewer role. But "these capabilities can work together" does not mean "draw the full architecture in the design doc on day one."

A healthier sequence is to let real problems drive the rhythm:

```text
Get the smallest closed loop running
  -> Observe the first clear problem pattern
  -> Fix it with the smallest useful version of one capability
  -> Evaluate whether the system actually improved
  -> Observe the next bottleneck
  -> Repeat
```

Do not add a capability just because it is popular in the community. Before a capability enters the system, it should have both problem evidence and an evaluation method. If you cannot say, "without RAG, users fail at this specific step in this specific way," then RAG should not be your first priority.

### 9.1.1 A cautionary story: the big-bang rollout

Consider this scenario. A team decides to build an "all-purpose code assistant agent" and introduces seven capabilities in a single sprint:

```text
Sprint goal: build SuperCodeAgent v1.0

Week 1:
- Add RAG: index all internal repository documentation
- Add Memory: store every user's coding habits and preferences
- Add Planning: automatically break down multi-step refactoring tasks

Week 2:
- Add Reflection: automatically review and fix generated code
- Add Multi-Agent: one agent writes code, one reviews code, one writes tests

The sprint ends. The system goes live. Then the feedback arrives.
```

**User feedback on day one:**

| Problem | Root cause | User reaction |
|------|------|----------|
| The agent is too slow, averaging 25 seconds per reply | Five capabilities make each request path extremely long | "I can write it faster myself." |
| Retrieved results are often irrelevant | The RAG index quality was not tuned before launch | "The search results have nothing to do with my question." |
| Memory stores many useless preferences | There is no filtering strategy for what should become memory | "It remembered a temporary test config and messed up my real workflow." |
| Plans often drift | Planning was not constrained for this scenario | "It created 10 steps, and by step 3 it was doing something unrelated." |
| Agents contradict each other | Multi-Agent has no conflict resolution rule | "The coding agent says it is fine; the review agent says rewrite it." |

**Core lesson:** the problem is not that these capabilities are bad. The problem is that introducing them all at once creates four failures:

1. **Debugging becomes unclear**: when something breaks, you cannot quickly locate which capability caused it.
2. **Evaluation becomes weak**: there is no "before" baseline to compare against.
3. **User trust gets spent too early**: a bad first experience may be the only chance users give you.
4. **The team is overloaded**: maintainers must understand several complex subsystems at the same time.

> **Remember this rule: one capability, one problem, one evaluation. These three ones are the baseline for capability rollout.**

### 9.1.2 The hidden cost of every capability

Every capability solves a problem, but it also adds a bill. Before introducing one, look at that bill clearly:

| Capability | Problem it solves | Cost it introduces |
|------|-------------|-----------|
| **RAG / external knowledge access** | The model does not know private or real-time information | Index maintenance, retrieval latency (+500 ms to 2 s), citation validation, document update sync |
| **Memory** | State continuity across turns or sessions | Storage growth, forgetting policy tuning, privacy compliance, persistence of incorrect memories |
| **Context Engineering** | Context becomes chaotic across many information sources | Layering design cost, continuous token-budget tuning, information loss from over-compression |
| **Planning / Workflow** | Multi-step task organization | Longer prompts, step drift, cascading errors, interruption recovery |
| **Reflection** | Automatic error detection and correction | Extra LLM calls (2-3x token use), endless self-revision loops, overcorrection |
| **Human-in-the-loop** | Human confirmation for high-risk actions | Blocking waits, UX interruption, confirmation fatigue, slower flows |
| **Multi-Agent** | Role separation and parallel work | Coordination overhead, conflict arbitration, more complex traces, roughly linear cost growth |
| **Tool Use** | Interaction with external systems | Tool failure handling, timeout control, permission safety, result validation |

**Cost amplification:** when capabilities are combined, the cost is not simply additive. It can compound:

```text
Single-capability latency:
  RAG retrieval: 800 ms
  Planning decomposition: 1.2 s
  Reflection fix: +1 LLM call (1.5 s)
  Multi-Agent coordination: +500 ms

Combined latency:
  RAG + Planning + Reflection + Multi-Agent
  = 800 ms + 1.2 s + (1.5 s x number of agents) + 500 ms + coordination wait
  ~= 5-8 seconds of user-visible lag
```

This is why capability rollout needs restraint. Every layer increases user wait time, your debugging time, and the probability of system failure.

### 9.1.3 A ladder of capability complexity

Instead of treating a capability as an on/off switch, look at the complexity it introduces. The ladder below is not a roadmap every agent must follow. It is a cost reference: the higher you go, the more the system must handle latency, debugging difficulty, state consistency, and evaluation cost.

```text
                        ┌─────────────────────────┐
                        │  High: adaptive teamwork │
                        │  Multiple agents form    │
                        │  teams, split work,      │
                        │  and review each other   │
                        ├─────────────────────────┤
                        │  High: decision boundary │
                        │  Human-in-the-loop for   │
                        │  high-risk operations    │
                        ├─────────────────────────┤
                        │  Medium-high: correction │
                        │  A single agent uses     │
                        │  Reflection to detect    │
                        │  failures and retry/fix  │
                        ├─────────────────────────┤
                        │  Medium-high: workflow   │
                        │  A single agent plans    │
                        │  and executes multi-step │
                        │  tasks                   │
                        ├─────────────────────────┤
                        │  Medium: context control │
                        │  Context Engineering for │
                        │  layers, budgets, and    │
                        │  priority management     │
                        ├─────────────────────────┤
                        │  Medium: state awareness │
                        │  A single agent uses     │
                        │  RAG + Memory            │
                        ├─────────────────────────┤
                        │  Baseline: closed loop   │
                        │  LLM + Tool Use + Loop   │
                        │  for simple independent  │
                        │  tasks                   │
                        └─────────────────────────┘
```

**How to use this ladder correctly:**

- **Do not treat it as a roadmap**: the real order is not "RAG, then Memory, then Planning, then Multi-Agent." The order depends on the problem.
- **Require evidence for each layer**: only add complexity after confirming the current problem cannot be solved in a simpler way.
- **Allow low-complexity systems to stay low-complexity**: many scenarios are best served by RAG plus lightweight Memory.
- **Be willing to roll back**: if a high-complexity capability creates more problems than it solves, stepping back is a mature engineering decision.

**Self-check questions:**

- Which capability category matches the current pain point?
- Is that pain point backed by data or user feedback?
- Are the evaluation metrics for existing capabilities stable?
- Is the added complexity, latency, and maintenance cost worth it?

### 9.1.4 The right rhythm is problem-driven

Here is a simplified version of how a knowledge assistant introduced capabilities over three months:

```text
┌─────────────────────────────────────────────────────────┐
│  Week 0: minimal closed loop goes live                  │
│  - LLM + basic conversation                             │
│  - Users paste source material manually                 │
│  - Core metric: answer quality, judged manually         │
├─────────────────────────────────────────────────────────┤
│  Week 2: problem discovered -> add RAG                  │
│  User feedback: "Pasting notes every time is too much." │
│  Ask: "How frequent is this?" -> 70% of conversations   │
│  require looking up source material                     │
│  Add: Markdown index + vector search + cited answers    │
│  Evaluate: 20 fixed questions for recall, answer        │
│  accuracy, and citation correctness                     │
│  Result: recall 78% -> after chunk tuning -> 89%        │
├─────────────────────────────────────────────────────────┤
│  Week 6: problem discovered -> add Memory               │
│  User feedback: "Every new chat forgets what I study."  │
│  Ask: "How much does cross-session context matter?"     │
│  Users average 3-5 sessions per research topic          │
│  Add: session summary + persistent key facts            │
│  Evaluate: 10 cross-session follow-up scenarios         │
│  Result: continuity accuracy 82% -> after summary       │
│  tuning -> 91%                                          │
├─────────────────────────────────────────────────────────┤
│  Week 8: problem discovered -> add Context Engineering  │
│  User feedback: "After RAG and Memory, context often    │
│  exceeds the limit, and sometimes it ignores my rules." │
│  Ask: "How many information sources exist? Are they     │
│  organized well?" -> 3 sources                          │
│  Add: context layers + token budget + compressed tool   │
│  outputs                                                │
│  Evaluate: 10 rule-retention tests                      │
│  Result: rule compliance improves from 72% to 94%       │
├─────────────────────────────────────────────────────────┤
│  Week 12: problem discovered -> add Planning            │
│  User feedback: "When it organizes a week of notes, it  │
│  often misses folders."                                 │
│  Ask: "Is this linear, or does it require branching?"   │
│  It requires branching                                  │
│  Add: a simple ReAct pattern so the agent can choose    │
│  the next step                                          │
│  Evaluate: 10 multi-step organization tasks             │
│  Result: omission rate drops from 20% to 5%             │
├─────────────────────────────────────────────────────────┤
│  Week 16: problem discovered -> add HITL                │
│  User feedback: "It deleted a file without asking me."  │
│  Ask: "Which actions are risky enough to require        │
│  confirmation?" -> file deletion, config changes        │
│  Add: risk levels + confirmation mode + batch confirm   │
│  Evaluate: 100% confirmation for high-risk operations,  │
│  mistaken user confirmation below 5%                    │
│  Result: no accidental deletions; user trust improves   │
├─────────────────────────────────────────────────────────┤
│  Week 18: no new capability                             │
│  Reason: the current five capabilities are stable and   │
│  there is no clear problem signal                       │
│  Reflection and Multi-Agent wait for evidence           │
└─────────────────────────────────────────────────────────┘
```

**Key observations:**

1. **Every capability has a concrete problem trigger**, not "everyone else is using it."
2. **Every introduction has a quantitative evaluation**, not "it feels better."
3. **There is enough observation time between changes**: two to four weeks for the problem pattern to become clear.
4. **Week 18 chooses not to add anything**, which is easy to overlook but equally important.

### 9.1.5 What counts as a minimal closed loop?

Before discussing capability combinations, first define the minimal closed loop. You need something runnable before you can decide what to enhance.

```text
Minimal closed loop = prompt + LLM decision + tool call + loop control + state management
```

**What the minimal closed loop can do:**

- Receive a user instruction
- Call tools to fetch information or perform actions
- Decide the next step from the tool result
- Continue until the task is complete
- Return the final result

**Boundaries of the minimal closed loop:**

```text
Included in the minimal closed loop:
  - "Search this folder for all .md files."
  - "Replace foo with bar in this code."
  - "Read this CSV and count rows by category."

Requires an enhanced capability:
  - "Answer this based on my notes." -> requires RAG
  - "Remember what I said last time." -> requires Memory
  - "There are too many information sources and the context is messy." -> requires Context Engineering
  - "Break this requirement into subtasks and finish them one by one." -> requires Planning
  - "Check whether the code you generated has bugs." -> requires Reflection
  - "This operation is too important for the agent to decide alone." -> requires Human-in-the-loop
  - "Have another role review your plan." -> requires Multi-Agent
```

**Why the minimal closed loop matters as a baseline:**

Before adding any enhancement, answer these questions with the minimal closed loop:

1. **Can the minimal closed loop handle this task?** If yes, why add anything?
2. **Where exactly does it get stuck?** This is the only legitimate reason to introduce a new capability.
3. **After the new capability is added, how much better is it than the baseline?** This is the evaluation baseline.

---

## 9.2 Capability Combination Patterns

The following six cases cover the most common agent scenarios. Each case starts from the initial problem, introduces capabilities in order, and explicitly states what should not be introduced yet. The latter is as important as the former.

#### Case 1: Personal knowledge assistant

**Scenario:** A user has many local notes, including Markdown files, PDFs, and web clippings. They want the agent to answer questions from those materials and cite sources.

**Initial problems:**

- The user has a large amount of material, and the model does not know its contents.
- The user needs source citations.

**Priority capability:**

- **RAG / external knowledge access**. This is the core capability. Without it, the agent can only give generic answers and cannot satisfy the requirement of "based on my notes."

**Minimal implementation:**

```text
Document folder -> document parsing (Markdown/PDF -> plain text)
                -> text chunking (by paragraph/heading, 500-1000 tokens per chunk)
                -> embedding
                -> vector database (Chroma / Milvus / Pinecone)

User question -> query embedding -> retrieve Top-K chunks (K=5-10)
              -> add retrieved chunks to the prompt
              -> LLM generates an answer with citation markers
```

**Evaluation dimensions:**

- Recall: did retrieval find the relevant document chunks?
- Answer accuracy: did the generated answer correctly use retrieved information?
- Citation correctness: do citation markers point to the right sources?
- Refusal rate: when the material does not contain relevant information, does the agent honestly say it does not know?

**Follow-up problems:**

- The user wants the assistant to remember the current research topic and continue next time.
- Multi-turn follow-up questions need context continuity.
- Multiple Q&A sessions on the same topic are not connected.

**Add next:**

- **Session summary and lightweight Memory**. This is not a full long-term memory system. It is a targeted solution for remembering the current research topic.

**Minimal Memory implementation:**

```text
At the end of each session:
  -> Use the LLM to generate a session summary
     (research topic, key findings, unresolved questions)
  -> Persist it in a JSON file or lightweight database

When the next session starts:
  -> Load recent session summaries
  -> Add them to the system prompt as context
  -> Let the user request "forget previous context" at any time
```

**Do not introduce yet:**

- **Multi-Agent**, unless there is a clear need for parallel research or review. If this is for one user's personal use, a single agent is enough.
- **Reflection**, unless retrieval quality shows a clear systemic issue. RAG quality should first be improved through chunking strategy and retrieval parameter tuning, not by asking the agent to "check itself."
- **Planning**, unless the user's tasks become clearly multi-step, such as "cross-check this across three sources."

**Rollout path:**

```text
Minimal closed loop
  -> RAG
    -> retrieval quality iteration
      -> Memory
        -> stable operation
          -> Planning? (wait for problem signal)
```

---

#### Case 2: Code review agent

**Scenario:** A team needs an agent to review pull requests. It should not only read the surface diff, but also understand code context and run tests to validate its judgment.

**Initial problems:**

- After reading only the diff, the agent gives generic suggestions such as "consider adding comments" or "check for null pointers."
- It cannot validate its own claims. It may say "there might be a performance problem" without actually testing it.
- Its suggestions lack context. It does not understand callers and callees around the changed function.

**Priority capabilities:**

- **Tool Use: read files, search code, run tests**. This is what turns a surface-level review into a deeper review.
- **Reflection: revise judgment after test failures or contradictory evidence**. When tool results conflict with the initial judgment, the agent needs to correct its conclusion.

**Minimal implementation:**

```text
Receive PR diff
  -> Analyze changed areas
  -> For each suspicious point, call tools:
      - read_file: read the full relevant file
      - search_code: find all references to a function or variable
      - run_test: run relevant tests
  -> Form review comments from tool results
  -> If a test fails, use Reflection:
      - analyze the failure
      - decide whether the agent's judgment was wrong or the code is actually faulty
      - revise the review comment
  -> Output the final review report
```

**Key design decision: why Reflection before Multi-Agent?**

In code review, the first impulse is often "use Multi-Agent: one writes, one reviews." But if the reviewing agent cannot call tools, the second agent is just reading the diff again and producing another generic opinion. Two blind reviewers do not suddenly gain sight.

The right order is: **first let a single agent see through tool calls, then let it correct itself through Reflection, and only then consider Multi-Agent role separation.**

**Follow-up problems:**

- After the code is modified, the agent needs to review the updated code again and check whether new issues were introduced.
- A single agent playing both "reviewer" and "suggestion author" can create role conflict. It may become too lenient toward its own suggestion.

**Add next:**

- **A lightweight Multi-Agent reviewer mode**: one agent reviews and suggests changes; another verifies the modified code. This is not a full Multi-Agent system. It is a reviewer pattern: two agents work in sequence without complex coordination.

**Minimal Multi-Agent implementation:**

```text
Reviewer Agent:
  Input: PR diff
  Output: review comments
  Tools: read files, search code, run tests

Verifier Agent:
  Input: modified code + Reviewer comments
  Output: verification report
  Behavior:
    - check each Reviewer suggestion was implemented correctly
    - check the modification did not introduce new issues

Simple conflict resolution:
  - If Reviewer and Verifier agree -> accept
  - If they disagree -> mark as "requires human review"
  - Do not allow the two agents to call each other in a loop
```

**Do not introduce yet:**

- **Long-term Memory**, unless the agent must remember project conventions, test habits, or user preferences. If project rules and test strategy already live in repository files, Memory adds little value.
- **Planning**, unless the review becomes clearly multi-step, such as "review security first, then performance, then readability."

**Rollout path:**

```text
Minimal closed loop
  -> Tool Use (deep analysis requires tools)
    -> Reflection (correction requires external signals)
      -> Multi-Agent Reviewer (role split only after role conflict appears)
        -> stable operation
          -> Memory? (wait for demand evidence)
```

---

#### Case 3: Personal task execution agent

**Scenario:** A user wants an agent to execute complex multi-step tasks, such as "configure CI/CD for this open-source project." The agent should pause for confirmation at key points and resume after interruption.

**Initial problems:**

- The task has many steps, and missing a step is easy.
- The user wants confirmation at critical points, such as before creating GitHub Secrets.
- Manually tracking task progress is tedious.

**Priority capabilities:**

- **Planning / Workflow Patterns**. Multi-step tasks naturally need structure.
- **Human-in-the-loop**. Critical operations need human confirmation. This is a safety requirement, not a UX enhancement.

**Minimal implementation:**

```text
User task: "Configure CI/CD for this repository"
  -> Planning Agent breaks it down:
      Step 1: analyze project structure and choose CI/CD approach
      Step 2: write CI configuration file
      Step 3: generate required Secrets list
      Step 4: [HITL] wait for user confirmation of the Secrets list
      Step 5: configure GitHub Secrets
      Step 6: trigger the first CI run
      Step 7: [HITL] inspect run result and wait for user confirmation
  -> Update state after each step
  -> Let the user inspect progress at any time
```

**Human-in-the-loop design points:**

```text
Good HITL design:
  - Pause before irreversible actions: delete, publish, permission changes
  - Provide clear options while paused: "confirm / skip / change parameters"
  - Default to "do not execute" after timeout

Bad HITL design:
  - Pause at every step, causing confirmation fatigue
  - Pause without enough information for the user to decide
  - Automatically execute high-risk operations after timeout
```

**Follow-up problems:**

- Long tasks need to continue after interruption.
- Execution history needs to be traceable.

**Add next:**

- **Task state and Checkpoint**. Course 6 will cover this in depth. The core idea is to persist task state and resume from the interruption point.

**Minimal Checkpoint implementation:**

```text
Task state:
{
  "task_id": "xxx",
  "goal": "Configure CI/CD for this repository",
  "steps": [
    {"id": 1, "desc": "Analyze project structure", "status": "done"},
    {"id": 2, "desc": "Write CI configuration", "status": "done"},
    {"id": 3, "desc": "Generate Secrets list", "status": "in_progress"},
    ...
  ],
  "checkpoint_data": {
    "branch": "feature/ci-setup",
    "ci_file": ".github/workflows/ci.yml",
    ...
  },
  "last_updated": "2024-03-15T10:30:00Z"
}

Resume flow:
  User reconnects -> detect unfinished task -> load Checkpoint -> continue from the saved point
```

**Do not introduce yet:**

- **Automatic long-term Memory**, unless the user explicitly needs preferences to carry across tasks. Task independence is a feature, not a defect.
- **RAG**, unless task execution frequently needs external documentation.
- **Multi-Agent**, because a single-user scenario usually does not need parallel roles.

**Rollout path:**

```text
Minimal closed loop
  -> Planning + HITL (task structure and safety)
    -> Checkpoint (interruption recovery)
      -> stable operation
        -> Memory? (only if cross-task preferences matter)
```

---

#### Case 4: Customer support agent

**Scenario:** An e-commerce platform needs a customer support agent that answers product questions, handles returns and exchanges, and checks order status. Some issues can be automated. Sensitive operations, such as refunds, require human approval. Complex issues should be handed off to a human support agent.

**Initial problems:**

- Product questions must be answered from the product catalog.
- Order status questions require access to the order system.
- Refund and exchange operations affect money and inventory, so they cannot be executed automatically.

**Priority capabilities:**

- **RAG / external knowledge access**: product information, policy documents, and FAQ need real-time retrieval.
- **Tool Use**: internal systems must be called, such as order lookup and logistics APIs.
- **Human-in-the-loop**: sensitive operations such as refund approval and exchange approval require human confirmation.

**Why introduce these three together?**

Customer support is special because RAG, Tool Use, and HITL are not three layers for the same problem. They solve three separate hard requirements that exist at the same time:

- Without RAG -> product information cannot be answered.
- Without Tool Use -> orders cannot be queried.
- Without HITL -> refunds create financial risk.

This is a case where the scenario itself requires multiple capabilities for a minimally useful product. Even then, validate them step by step: first make sure RAG retrieval is correct, then connect Tool Use, then add HITL.

**Minimal implementation:**

```text
User message
  -> Intent classification:
     product question / order lookup / after-sales request / small talk
  -> Route to the corresponding flow:

Product question flow:
  -> RAG retrieves from the product knowledge base
  -> Generate an answer from retrieved results
  -> Include product links

Order lookup flow:
  -> Verify user identity
  -> Call order API
  -> Format and return order information

After-sales flow:
  -> Query order status
  -> Determine whether the order qualifies for return/exchange
  -> [HITL] If refund is needed, create a refund request and wait for human approval
  -> [HITL] After approval, execute refund and notify user
```

**Follow-up problems:**

- Returning users must explain the same issue again every time.
- Returning customers' preferences and recent issues may need to be remembered.
- When a complex issue is handed off to a human, the human agent needs conversation context.

**Add next:**

- **Session Memory**: remember the current conversation and recent contact history. This should be session-level, not a full user-level long-term profile. The former reduces repetition; the latter raises privacy and compliance concerns.

**Memory design for customer support:**

```text
Session-level memory (valid for 7 days):
  - Conversation history in this session
  - Products/orders involved in this session
  - Unresolved issues in this session

User-level memory (requires user authorization):
  - Common shipping address
  - Last 3 purchases
  - Language preference

Cleanup policy:
  - Session-level memory: automatically delete 7 days after the session ends
  - User-level memory: users can view and delete it at any time
  - Sensitive information such as payment data and passwords is never stored
```

**Do not introduce yet:**

- **Planning**: customer support conversations are usually linear flows with routing rules, not dynamic planning problems.
- **Reflection**: feedback in support comes from user satisfaction and operational outcomes, not from the agent judging itself.
- **Multi-Agent**: unless pre-sales and post-sales roles truly need to be handled simultaneously. In most cases, routing is enough.

**Rollout path:**

```text
Minimal closed loop
  -> RAG + Tool Use + HITL (hard scenario requirements, validated step by step)
    -> Memory (reduce repeated explanations while respecting privacy boundaries)
      -> stable operation
        -> decide next step from user satisfaction data
```

---

#### Case 5: Data analysis assistant

**Scenario:** A data analyst needs an agent to write SQL, analyze data, and generate visual reports. The task is often multi-step: understand the request, write a query, validate the result, explain the finding, and generate a chart.

**Initial problems:**

- The user describes an analysis request in natural language, and the agent must translate it into SQL.
- After SQL runs, the agent must check whether the result is plausible.
- If the result is wrong, the agent must correct the query.

**Priority capabilities:**

- **Tool Use**: execute SQL, read table schemas, query the data dictionary.
- **Reflection**: automatically inspect and fix SQL failures or abnormal results.

**Why Tool Use + Reflection before Planning?**

For single-table queries or one-off metric calculations, the user's natural language already contains the main analysis goal: "Show last month's sales trend by region and find the three fastest-growing categories." The first problem is not whether the agent can plan. The first problem is whether it can read the schema, generate SQL, execute the query, and fix itself when the database returns an error.

This does not mean data analysis never needs Planning. When the task becomes cross-table exploration, staged hypothesis testing, "query A first, then query B based on A's result, then combine and visualize," Planning becomes valuable. The order should be: first stabilize execution and validation, then add Planning when multi-step analysis clearly appears.

**Minimal implementation:**

```text
User request -> Agent analyzes:
  1. Read database schema and understand tables/fields
  2. Generate SQL
  3. Execute SQL
  4. Inspect result:
     - Did execution succeed?
       -> if not, Reflection analyzes the error and fixes SQL
     - Is the result plausible?
       -> if row count is 0 or values are abnormal, Reflection checks query logic
     - Does the result match the user's intent?
       -> run a plausibility check against the request
  5. Explain findings
  6. Optionally generate visualization code (matplotlib / eCharts)
```

**Reflection in data analysis:**

```text
Reflection triggers:
  - SQL syntax error -> read the error and fix syntax
  - Empty result set -> check whether WHERE conditions are too strict
  - Obviously abnormal values -> check JOIN logic
  - Result contradicts common sense -> warn the user about possible data quality issues

Reflection stop conditions:
  - Still failing after 3 fixes -> explain the situation and ask the user for guidance
  - Unsure whether the result is correct -> mark "requires human verification"
  - Data source itself appears faulty -> report the issue and stop trying to patch around it
```

**Follow-up problems:**

- Complex analysis requires multiple steps: query table A, use A's result to query table B, then merge analysis.
- The user wants the agent to remember common analysis templates and preferred metrics.
- Analysis across multiple data sources needs organized step management.

**Add next:**

- **Planning**: introduce it when analysis evolves from a single query into a multi-step analysis process.
- **Memory**: remember the user's analysis habits, such as common metrics, preferred chart types, and naming conventions.

**Do not introduce yet:**

- **RAG**, unless analysis frequently needs external methodology documents or industry standards.
- **Multi-Agent**, because a single analyst scenario usually has no role conflict.

**Rollout path:**

```text
Minimal closed loop
  -> Tool Use + Reflection (translation + correction are core to analysis)
    -> Planning (after clear multi-step analysis demand appears)
      -> Memory (after reuse of analysis habits becomes valuable)
        -> stable operation
```

---

#### Case 6: Writing collaboration agent

**Scenario:** A user and an agent collaborate on technical blog posts. The agent needs to understand the user's writing style, remember previously discussed points, retrieve reference material, and run quality checks after each revision based on external evidence.

**Initial problems:**

- The user wants a consistent writing style.
- The user needs the agent to cite technical references.
- After the agent writes a section, the user wants it to check concrete issues: whether citations are traceable, code examples run, terminology follows conventions, and user feedback has been handled.

**Priority capabilities:**

- **RAG**: retrieve technical references, related articles, and API documentation.
- **Memory**: remember the user's style preferences, terminology choices, and structural habits.

**Why RAG + Memory together?**

In writing, RAG and Memory solve different dimensions:

- RAG answers "what to write" by providing accurate technical content.
- Memory answers "how to write it" by preserving consistent style and terminology.

They are independent, but both are important. Without RAG, the content may be inaccurate. Without Memory, the style becomes inconsistent.

**Minimal implementation:**

```text
Writing collaboration flow:
  1. User proposes a topic
  2. Agent retrieves references (RAG)
  3. Agent recalls user style preferences (Memory)
  4. Agent drafts the first version
  5. [HITL] User reviews and gives revision feedback
  6. Agent revises from feedback
  7. Agent runs quality checks:
     - citation validation: retrieve source text and confirm the citation exists
     - code example check: run or statically inspect code
     - terminology/style checklist: compare against explicit preferences in Memory
     - feedback coverage: confirm each user comment was handled
  8. Output the final draft

Memory structure for writing:
{
  "style_preferences": {
    "tone": "professional but approachable",
    "sentence_length": "mostly short to medium sentences",
    "code_style": "Python with required type hints",
    "preferred_terms": {
      "use": ["database", "query"],
      "avoid": ["DB", "SQL magic"]
    }
  },
  "structural_habits": {
    "opening": "start from a story or problem",
    "body": "concept -> mechanism -> example -> caveats",
    "closing": "summary + further reading"
  },
  "common_mistakes_to_avoid": [
    "avoid overusing passive voice",
    "code examples must be runnable",
    "explain technical terms the first time they appear"
  ]
}
```

**Follow-up problems:**

- After multiple revision rounds, the agent needs to verify article quality against explicit checks instead of waiting for the user to point out every issue.
- Long articles need structure and section management.

**Add next:**

- **Reflection**: use it only for quality checks backed by external signals, such as whether a citation appears in the source, whether code runs, whether user feedback was covered, and whether terminology matches the confirmed style list.
- **Planning**: use it for long-form structure planning and outline management.

**Reflection design for writing:**

```text
Trigger signals:
  1. Citation validation fails: a generated source cannot be found in the RAG material
  2. Code check fails: code does not run, type check fails, or output is unexpected
  3. Terminology checklist mismatch: the draft uses terms the user explicitly asked to avoid
  4. User feedback not covered: some revision request remains unresolved

Correction rules:
  - Run after each section is completed
  - Fix only the specific issue found; do not rewrite the entire article
  - If the same issue fails more than 2 times, mark it and ask the user to intervene
  - Do not treat subjective writing taste, such as "is this elegant enough," as model self-evaluation.
    Use user review or a reviewer checklist instead.
```

**Do not introduce yet:**

- **Multi-Agent**: writing is creative work. One agent plus user review is usually enough. Adding "one writes, one reviews" can make style less consistent.
- **A stronger system-level Human-in-the-loop mechanism**: writing collaboration is already naturally HITL, because the user reviews every draft.

**Rollout path:**

```text
Minimal closed loop
  -> RAG + Memory (accurate content + consistent style)
    -> Reflection (quality checks based on external signals)
      -> Planning (long-form structure management)
        -> stable operation
```

---

## 9.3 Anti-Patterns in Capability Combination

The previous section showed what to do. This section shows what to avoid.

#### Anti-pattern 1: Capability Hoarding

**Symptom:**

```text
"Our agent uses RAG + Memory + Planning + Reflection + Multi-Agent,
 plus Tool Use, Guardrails, Human-in-the-loop..."
```

**Diagnosis:** The team can say what the system has, but not why each part exists. Each capability was added because "it might be useful someday." The result is a system so complex that nobody fully understands it, and nobody knows who owns a failure.

**Remedy:**

- Every capability must have a corresponding issue or ticket that records why it was introduced.
- Run regular capability inventories: is this capability still used? Does it still solve the original problem?
- If nobody can explain why a capability exists, consider removing it.

---

#### Anti-pattern 2: Waiting for perfection before launch

**Symptom:**

```text
"RAG recall is only 78%; let's wait until it reaches 90%."
"The forgetting policy for Memory is not tuned yet; let's not ship."
"Planning still drifts sometimes; let's release after that is solved."
```

**Diagnosis:** Waiting for a perfect minimum version often means never launching. Users would rather have an imperfect assistant than wait for a perfect assistant that does not exist. More importantly, without release you get no real usage feedback, and without feedback you cannot truly improve.

**Remedy:**

- Define a "good enough" threshold instead of a "perfect" standard.
- Capabilities below the long-term target can ship as experimental features if they pass the minimum threshold.
- Create a feedback channel so real use drives iteration.

**Launch threshold:**

```text
Minimum standard for launch:
[ ] Is the core function usable? No blocking bugs.
[ ] Are safety issues handled? No data leakage or dangerous actions.
[ ] Are failure modes graceful? The user is told when something goes wrong.
[ ] Can the user choose not to use the capability?

Standards that do not need to be perfect:
[ ] Is performance optimal? It can be optimized later.
[ ] Are all edge cases covered? Some only appear in real use.
[ ] Do all evaluation metrics reach the ideal target? Real data may differ from the test set.
```

---

#### Anti-pattern 3: Blindly following trends

**Symptom:**

```text
"That Hacker News post says Multi-Agent is the most important trend of 2024."
"Everyone is using LangGraph for agent workflows, so we should too."
"A big company's blog says Reflection worked well for their agent."
```

**Diagnosis:** Their scenario, data, constraints, and users are not yours. A solution that fits them may not fit you. Replacing your own problem analysis with community trends is the fastest path to unnecessary complexity.

**Remedy:**

- When reading other teams' designs, focus on the problem they had, not the technology they used.
- If you cannot explain in one sentence why your scenario needs this capability, do not add it yet.
- Treat community articles as a menu of options, not a checklist.

**Conversion exercise:**

```text
When you read:
"We improved code review quality with Multi-Agent."

Do not think:
"We should add Multi-Agent too."

Think:
"What code review problem did they have?
 Do we have the same problem?
 What exactly did Multi-Agent solve for them?
 Why was a single agent insufficient?
 What is the bottleneck in our own code review flow?"
```

---

#### Anti-pattern 4: Adding a capability without evaluation or iteration

**Symptom:**

```text
"We added RAG two weeks ago. Users say it seems better... I am not sure."
"Memory is enabled now. We have not measured it, but it should help."
"Planning steps are sometimes off, but it mostly works, probably."
```

**Diagnosis:** Introducing a capability is the beginning, not the end. A capability without evaluation adds an unknown variable to the system. Over time, you no longer know whether quality is improving or degrading.

**Remedy:**

- Define the evaluation method before introducing each capability.
- Review metrics weekly or monthly to confirm there is no regression.
- When adding a new capability, rerun the evaluations for existing capabilities to check for interaction effects.

**Suggested evaluation rhythm:**

```text
Before introduction: establish baseline evaluation
Week 1 after introduction: evaluate daily to confirm direction
Weeks 2-4 after introduction: evaluate weekly as usage stabilizes
Month 2 onward: evaluate monthly to monitor for regression
```

---

#### Anti-pattern 5: Capabilities that do not coordinate

**Symptom:**

```text
RAG retrieves content, and Memory stores another copy of the same content.
Planning creates a 5-step plan, but Reflection believes step 2 is already done.
Agent A in a Multi-Agent system modifies a file, but Agent B does not know.
```

**Diagnosis:** Capabilities are not independent plugins. They share state and influence each other's behavior. When multiple capabilities have different understandings of the same data, system behavior becomes unpredictable.

**Remedy:**

- Define responsibility boundaries: who owns which data?
- Use unified state management: all capabilities read and write through the same State layer.
- Define explicit contracts for information passed between capabilities, such as schema and format.
- Regularly check consistency across capabilities.

**Coordination checklist:**

```text
[ ] Do RAG results enter Memory? If yes, is that necessary?
[ ] Does Memory influence Planning step generation?
[ ] Does Reflection update Planning state after a correction?
[ ] Do all agents in Multi-Agent share the same Memory view?
[ ] Could one capability's output change break another capability's input assumptions?
```

Once capabilities are combined, coordination should not rely on ad hoc prompt agreements. It should be handled by the runtime: unified State, Trace, Checkpoint, evaluation regression sets, and permission boundaries. Course 6 will cover this Harness architecture. This chapter focuses on whether capabilities should be combined at all; Course 6 focuses on how to keep them stable after combination.

---

## 9.4 Timing and Signals for Gradual Adoption

#### When to speed up adoption

The following signals suggest that user needs have clearly exceeded the current system boundary, so accelerating adoption is reasonable:

```text
Acceleration signals:
[+] The same issue appears in user feedback 5+ times within 2 weeks
[+] Evaluation metrics for the current capability keep declining
    because demand is growing beyond what the system can handle
[+] Competitors already provide this capability, and users are leaving
[+] The solution is clear and the risk is controllable
[+] Users explicitly say, "I cannot continue using this unless X is supported"
```

**Acceleration does not mean rushing blindly.** Even when you speed up, keep the "introduce -> evaluate -> observe" process. Acceleration shortens the observation window, for example from four weeks to two, but it does not skip evaluation.

#### When to pause and consolidate

The following signals mean you should stop and digest the previous change instead of adding another capability:

```text
Pause signals:
[!] Evaluation metrics for the last capability are still unstable
[!] Known bugs remain unresolved, especially more than 3 open issues
[!] Team members say, "The system is too complex; new people cannot understand it"
[!] User feedback mentioning "slow" and "unreliable" is increasing
[!] You cannot clearly explain how many capabilities are currently active
```

**Pausing is not failure. It is responsible engineering.** During a pause, you can:

- Fix known bugs
- Improve documentation and traces
- Strengthen the evaluation system
- Remove capabilities that are no longer needed, as discussed in 9.5
- Reduce overall system complexity

#### Three principles for controlling rhythm

**Principle 1: one new variable at a time**

Introduce only one new capability at a time. If the result is poor, you can identify the cause. If you introduce two capabilities together, you may never know which one helped and which one caused problems.

```text
Bad: introduce RAG + Memory at the same time
  "Retrieval improved, and cross-session context also seems better...
   but we are not sure why."

Good: introduce RAG first, then Memory after two stable weeks
  "After RAG, recall improved from 0% to 85%. We know RAG caused that."
  "Two weeks later, after Memory, cross-session continuity improved from 28% to 80%.
   We know Memory caused that."
```

**Principle 2: evaluation metrics come before the new capability**

If you do not have a runnable evaluation process, do not add a new capability. Adding a capability without evaluation is like walking with your eyes closed. You do not know whether you are moving toward the goal or away from it.

**Principle 3: review regularly**

Whether the system feels stable or not, run a regular capability review:

```text
Review checklist:
[ ] For every introduced capability: are metrics stable or improving?
[ ] For every capability not yet introduced: is the reason for not introducing it still valid?
[ ] Have new problem patterns appeared?
[ ] Can any capability be downgraded or removed?
[ ] Can overall system complexity be reduced?
[ ] Does the team understand the system well enough for new members to ramp up?
```

---

## 9.5 Downgrading and Removing Capabilities

Most tutorials explain how to add capabilities, but not how to remove them. Mature system design and mature engineering both require knowing when a capability should be removed.

#### When to consider removal

| Signal | Meaning | Example |
|------|------|------|
| **The problem disappeared** | The original problem no longer exists | The user changed workflow and no longer needs cross-session Memory |
| **The capability is not used** | It was added but usage is near zero, such as below 5% | Planning is elaborate, but 95% of tasks are single-step |
| **Cost exceeds benefit** | Maintenance cost, latency, or error rate outweighs value | Memory often remembers wrong information and costs more time than it saves |
| **A simpler solution exists** | The problem can be solved without this capability | Prompt tuning plus better tool descriptions performs almost as well as Planning |
| **It conflicts with another capability** | Two capabilities produce contradictory behavior | Memory stores one writing style, while RAG retrieves examples in another style |
| **Metrics keep declining** | Quality keeps degrading and optimization cost is too high | RAG index updates become slower and recall keeps dropping |

#### How to downgrade or remove safely

Removal must be more careful than introduction, because users may already rely on the behavior.

**Downgrade/removal process:**

```text
Step 1: confirm impact scope
  - Measure how often the capability is used
  - List user scenarios that depend on it
  - Estimate the user experience after removal

Step 2: find alternatives
  - Can a simpler mechanism cover the core need?
  - Can the capability move from automatic to on-demand?
  - Can the capability be restricted to a smaller scope?

Step 3: downgrade gradually
  Option A: automatic -> manual
    Before: Memory summarizes every conversation automatically
    After: Memory summarizes only when the user enters /summarize

  Option B: shrink scope
    Before: Memory records every conversation
    After: Memory records only conversations the user marks as important

  Option C: replace with a lighter mechanism
    Before: full ReAct Planning
    After: fixed Chain flow, if most tasks are already standardized

Step 4: gradual removal
  - Disable the capability for 10% of users and watch feedback
  - If there is no negative signal, expand to 50%
  - If still stable, remove it fully

Step 5: record the decision
  - Why remove it? Why was it introduced originally? What did we learn?
  - How should this experience guide future capability decisions?
```

**Downgrading is often better than direct removal:**

In many cases, changing a capability from active to passive is the better choice:

```text
Before: Memory automatically records every session
After: Memory records only when the user explicitly asks

Before: RAG retrieves for every query
After: RAG triggers only when the user says "look this up"

Before: Planning decomposes every task
After: Planning triggers only when the task exceeds 5 steps

Before: Multi-Agent runs in parallel by default
After: single-agent by default; start Reviewer only when the user adds --review
```

#### Verify after removal

After removing a capability, confirm:

- Did the old problem reappear?
- Did system latency improve?
- Did user feedback change?
- Did maintenance burden decrease?

If none of these metrics change after removal, that capability was probably unnecessary, and removal was the right decision.

---

## 9.6 Practice: Decide the Capability Roadmap for a New Scenario

Below are three new scenarios. For each one:

1. Decide which capabilities should be introduced first.
2. Explain which capabilities should not be introduced yet and why.
3. Draw the capability rollout path.

#### Exercise 1: Legal document review agent

**Scenario:** A law firm needs an agent to help junior lawyers review contracts. The agent must check whether clauses are compliant, whether risky clauses exist, and whether key clauses are missing. A human lawyer must make the final confirmation.

**Constraints:**

- Contract content is highly sensitive and cannot be uploaded to external services.
- Contract templates differ by industry, such as technology, finance, and real estate.
- Review mistakes can create legal risk.
- The firm has an internal knowledge base with past cases and contract templates.

**Make your decision:**

- Priority capabilities: _______
- Do not introduce yet: _______
- Rollout path: _______

<details>
<summary>Reference answer (click to expand)</summary>

**Priority capabilities:**

- **RAG**: the agent needs to retrieve the firm's internal knowledge base, including past cases and contract templates. It must run locally because of privacy constraints.
- **Human-in-the-loop**: final legal judgment must be confirmed by a human lawyer. This is a hard requirement.

**Do not introduce yet:**

- **Memory**: each contract is independent, and cross-contract memory can create confusion.
- **Planning**: contract review is structured clause-by-clause work. A fixed review checklist is enough; dynamic planning is unnecessary.
- **Reflection**: agent self-review is weaker than lawyer review here, and legal judgment lacks a reliable external self-correction signal.
- **Multi-Agent**: for a single review flow, one agent plus human lawyer confirmation is enough.

**Rollout path:**

```text
Minimal closed loop (LLM + contract reading tool)
  -> RAG (retrieve knowledge base and compare clauses)
    -> HITL (human confirmation point)
      -> stable operation
```

</details>

---

#### Exercise 2: Smart home control agent

**Scenario:** A user interacts with a smart home control agent through voice or text. The agent controls lights, air conditioners, curtains, speakers, and other devices. It understands daily habits and automatically adjusts scenes, such as "I am going to sleep" triggering lights off, curtains closed, and air conditioning lowered.

**Constraints:**

- Device control needs low latency, under 500 ms.
- Habits vary by user: one person sleeps with AC at 26°C, another at 24°C.
- Scene triggers require user confirmation to prevent accidental actions.
- Multiple users are supported, and family members have different preferences.

**Make your decision:**

- Priority capabilities: _______
- Do not introduce yet: _______
- Rollout path: _______

<details>
<summary>Reference answer (click to expand)</summary>

**Priority capabilities:**

- **Tool Use**: controlling devices through device APIs is the foundation.
- **Memory**: remember each user's preferences, such as temperature, light brightness, and common scenes.
- **Human-in-the-loop**: confirm scene triggers for safety.

**Do not introduce yet:**

- **RAG**: smart home control does not depend on external knowledge.
- **Planning**: scenes are usually predefined, such as "sleep" -> lights off + curtains closed + temperature adjustment. Dynamic planning is unnecessary.
- **Reflection**: device results can be confirmed through sensor feedback, such as whether the light is off. The agent does not need to reflect on itself.
- **Multi-Agent**: a single service flow does not need parallel roles.

**Rollout path:**

```text
Minimal closed loop + Tool Use (device control)
  -> Memory (remember user preferences)
    -> HITL (confirm scenes)
      -> stable operation
```

</details>

---

#### Exercise 3: Technical documentation maintenance agent

**Scenario:** An open-source maintainer needs an agent to automatically maintain technical documentation. When code changes, the agent detects which docs need updates, generates a documentation PR, and explains the change inside the PR.

**Constraints:**

- Consistency between code and documentation is critical.
- The agent needs to understand the impact of changes across multiple files.
- Documentation quality affects onboarding for new users.
- A human maintainer must approve documentation changes.

**Make your decision:**

- Priority capabilities: _______
- Do not introduce yet: _______
- Rollout path: _______

<details>
<summary>Reference answer (click to expand)</summary>

**Priority capabilities:**

- **Tool Use**: read code diffs, search affected docs, and create PRs.
- **Reflection**: after generating documentation, compare code and docs for consistency, such as matching API parameter names.
- **Planning**: complex changes may affect multiple documents and need organized handling.

**Do not introduce yet:**

- **RAG**: the source of truth is the code itself, not an external knowledge base.
- **Memory**: each documentation update can be handled independently and does not need cross-session state.
- **Multi-Agent**: a single agent can complete the flow of reading changes, updating docs, and validating consistency. Final PR approval is done by a human maintainer, so an agent reviewer is unnecessary.

**Rollout path:**

```text
Minimal closed loop + Tool Use (read code, search docs, create PR)
  -> Reflection (verify code-documentation consistency)
    -> Planning (coordinate multi-file documentation updates)
      -> stable operation
```

</details>
