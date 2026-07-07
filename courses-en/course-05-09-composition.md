# Chapter IX: Portfolio of capacities and sequence of introduction

[Return Course Five Document](./course-05-01-scenario-enhancement.md) | [Previous Chapter](./course-05-08-multi-agent.md) | [Next part: after-school exercises](./course-05-01-scenario-enhancement.md#课后练习)

## Table of contents of this chapter

- [9.1 No one-time capacity stacked](#91-no-one-time-capacity-stacked)
  - [9.1.1 Anti-curricular materials: disasters introduced by the Big Bang](#911-anti-curricular-materials-disasters-introduced-by-the-big-bang)
  - [9.1.2 Hidden costs of capabilities](#912-hidden-costs-of-capabilities)
  - [9.1.3 Levels of capacity complexity](#913-levels-of-capacity-complexity)
  - [9.1.4 Correct problem-driven rhythm](#914-correct-problem-driven-rhythm)
  - [9.1.5 What's the "minimal circle"?](#915-whats-the-minimal-circle)
- [9.2 Capacity portfolio cases](#92-capacity-portfolio-cases)
  - [Case I: Personal Knowledge Assistant](#case-i-personal-knowledge-assistant)
  - [Case II: Code Review](#case-ii-code-review)
  - [Case III: Individual assignments](#case-iii-individual-assignments)
  - [Case four: Smart customer service, Agent.](#case-four-smart-customer-service-agent)
  - [Case V: Data Analysis Assistant](#case-v-data-analysis-assistant)
  - [Case VI: Writing Collaboration](#case-vi-writing-collaboration)
  - Cross-case comparison overview
- [9.3 Counter-model of capacity mix](#93-counter-model-of-capacity-mix)
- [9.4 Gradual introduction of rhythms and signals](#94-gradual-introduction-of-rhythms-and-signals)
- [9.5 Degradation and removal of capabilities](#95-degradation-and-removal-of-capabilities)
- [9.6 Field exercise: capacity to make decisions for new scenes](#96-field-exercise-capacity-to-make-decisions-for-new-scenes)

---

## 9.1 No one-time capacity stacked

Agent, a knowledge assistant in Ri, eventually brought together seven capacities. But this is not an end in itself — it has been used for months, and one problem after another has been pushed out.

In real projects, empowerment does occur frequently. Personal Knowledge Assistant needs RAG + Memory; Code ReviewAgent needs Tool Use + Reflection + Reviewer. However, a combination does not amount to a one-time drawing of the architecture in the design document.

The better order is - let the problem drive into the rhythm:

```text
Let's get the smallest ring running.
  -> Watch the first clear problem pattern.
  -> We'll fix it with a minimum of capacity.
  -> Is the evaluation really getting better?
  -> Watch the next bottleneck.
  -> Loop
```

Do not join the system because a certain ability is popular in the community. Each capability should be supported by problematic evidence and evaluation methods before entering the system. If you can't say "What problem the user has at what point when there is no RAG," then RAG should not be your first priority.

### 9.1.1 Anti-curricular materials: disasters introduced by the Big Bang

Look at a scene. A team decided to be an "Agent" all-powerful code assistant, introducing seven capabilities simultaneously in a sprint:

```
Sprint Target: Build SuperCodeAgent v1.0

First week:
- Access RAG: All code repository documents within index company
- Access memory: Save all user code habits and preferences
- Accessing Planning: Supporting multi-step reshuffle plan self-dismantling

Week two:
- Access: Automatically review and correct code generation
- Access Multi-Agent: one writing code, one review code, one writing test

Sprint Online after completion, results:
```

**User feedback on first day:**
| Problem | Gene. | User perception |
|------|------|----------|
| Agent's response was too slow (25 seconds average) | Five superpowers lead to an extremely long single request chain. | "Not as fast as I can write." |
| The results are often irrelevant. | RAG Index quality was not polished in time | "It's not about what I asked." |
| Memoory remembers a lot of useless preferences. | No memory screening strategy. | "It recorded the configuration of my temporary test, and it was officially completely out of order." |
| Plan, the steps are always off track. | Planning didn't match the scene. | "Step 10, step 3 begins to do irrelevant things." |
| Two Agents. | Multi-Agent does not define conflict resolution rules | "The guy who writes the code says it's okay. The guy who reviews the code says it's rewrite." |

**Core lesson:** Not that these capabilities are bad, but that one-time introduction leads to:

1. **Debugging dilemma**: When a problem arises, you cannot quickly locate what caused it.
2. **Evaluation difficulty**: you do not have a "pre-inclusion" baseline to compare
3. **User trust overdraft**: first experience poor and users may not give you a second chance
4. **Team perception overload**: maintainers need to understand five complex subsystems simultaneously

> **Remember one sentence: one capacity, one problem, one assessment. The three principles of "one" are the bottom line for introducing rhythm.**

### 9.1.2 Hidden costs of capabilities

Every capacity also has a quiet cost in solving problems. Before the decision is taken, the bill is clear:

| Capacity | Solve what? | The cost. |
|------|-------------|-----------|
| **RAG / External Knowledge Access** | Model does not know private/real time information | Index maintenance, search delay (+500ms-2s), reference verification, document update synchronization |
| **Memory** | Cross-session/cross-wheel extension | Storage expansion, forgotten tactics, privacy compliance, perpetuation of false memories |
| **Context Engineering** | Multiple information sources cause context confusion | Layer design costs, Token budget need to be continuously aligned, over-compression leads to information distortion |
| **Planning / Workflow** | Multistep Tasks Organization | Prompt length surge, step drift, error cascade, interruption recovery |
| **Reflection** | Automatically detect and correct errors | Multi-rotation cost (x2-3 token), endless cycle, overcorrection |
| **Human-in-the-loop** | High-risk operations require human identification. | Block waiting, UX interruption, confirmation of fatigue, process delay |
| **Multi-Agent** | Conflict of roles, parallel implementation | Coordinated spending, Agent conflict decisions, Trade complexity multiplying, and cost linear growth |
| **Tool Use** | Interaction with the outside world | Tool Call Failed, Timeout Control, Permission Security, Results Validation |

**Cost amplification effect:** When multiple combinations of capacities, the cost is not simply added up, but is interactively amplified:

```text
Single capacity delay:
  RAG Search: 800 ms
  Planning Dismantling: 1.2s
  Reflection Amendments: + 1 round LLM Call (1.5s)
  Multi-Agent Coordination:+500ms

Delay after grouping:
  RAG + Planning + Reflection + Multi-Agent
  = 800ms + 1.2s + (1.5s × number of Agents)+ 500ms + Coordination waiting
  ≈ 5-8 seconds (user-perceived lag)
```

That is why the introduction of capabilities requires restraint — the waiting time of users, your debugging time, the probability of system error is growing every step.

### 9.1.3 Levels of capacity complexity

Instead of using capability as a binary switch, let's see how complicated they are. The following figure is not the route of upgrading that all Agent must follow, but is an incremental reference: the higher the system, the higher the delay, debugging, state consistency and evaluation costs.

```text
                        ┌─────────────────────────┐
                        │  High complexity: self-adaptation synergy│
                        │  More Agent Auto by Task│
                        │  Teaming, division of labour, mutual review│
                        ├─────────────────────────┤
                        │  High complexity: decision-making boundaries│
                        │  Has Human-in-the-loop│
                        │  High-risk operational human confirmation│
                        ├─────────────────────────┤
                        │  Medium high complexity: self-correction│
                        │  Single Agent has Reflection│
                        │  Test failed and automatically retry/correct│
                        ├─────────────────────────┤
                        │  Medium and high complexity: complex tasking│
                        │  Single Agent with Planning│
                        │  Multistep tasks automatically split│
                        ├─────────────────────────┤
                        │  Medium complexity: Context management│
                        │  Available Context Engineering│
                        │  Layers, budgets, priority management│
                        ├─────────────────────────┤
                        │  Medium complexity: state perception│
                        │  Single Agent with RAG+Memory │
                        │  Access to external knowledge, remember preferences│
                        ├─────────────────────────┤
                        │  Baseline: minimum closed ring│
                        │  LLM + Tool Use + Loop    │
                        │  Dealing with simple, independent mandates│
                        └─────────────────────────┘
```

**The correct way to use this ladder:**

- **Do not use it as a road map**: not first RAG, then Memory, then Planning, then Multi-Agent. The true order is determined by the question.
- **There is evidence for each addition**: confirmation that current problems cannot be solved in a simpler way and that more complex capabilities are introduced.
- **Allowing a combination of low complexity**: Not all scenarios need to climb to high complexity. A lot of scenes at RAG + Light Memory is the best solution.
- **Revertable**: If high-complexity capacity causes more problems, a more simple combination is a mature decision. **Self-examination:**
- What kind of capability does the current scene have?
- Is there data or user feedback support for this ability to address issues?
- Are the indicators of capacity in place stable?
- Is it worth adding complexity, delay and maintenance costs?

### 9.1.4 Correct problem-driven rhythm

The following is the actual introduction of the rhythm (simplified) within three months by Agent:

```text
┌─────────────────────────────────────────────────────────┐
│  Week 0: Minimum closed loop on line│
│  - LLM + Basic dialogue│
│  - User manually paste information content│
│  - Core indicator: Reasonable answers (manual judgement)│
├─────────────────────────────────────────────────────────┤
│  Week 2: Problem finding— RAG Introduction│
│  User feedback: "It's too much trouble to post notes manually every time."│
│  Ask yourself, "How often is this question?"?" → 70% All the conversations need information.│
│  Introduction: Markdown Document Index+ Vector Search+ Reference Output│
│  Assessment: 20 fixed questions, check recall rate, answer accuracy, quote correctness│
│  Result: recall rate 78% → Optimizing the segment policy → 89%                   │
├─────────────────────────────────────────────────────────┤
│  Week 6: Problem finding— Memory Introduction│
│  User feedback: "Every time a new conversation starts, it forgets what I'm working on."│
│  Ask yourself, "How much does cross-session context affect experience?"?" → Average of 3-5 meetings for users│
│  Introduction: Session Summary+ Sustainability of key information│
│  Evaluation: Cross-session queries 10 scenes to check context connection accuracy│
│  Result: Connection accuracy rate 82% → After adjusting the summary policy → 91%               │
├─────────────────────────────────────────────────────────┤
│  Week 8: Problem finding— Context Engineering Introduction│
│  User feedback: "After receiving RAG and Memory, the context is often overstretched.│
│           "Sometimes I ignore the rules I set."│
│  Ask yourself, "Some sources.?Is the organization reasonable??" → 3 information sources│
│  Introduction: Context Layer+ Token Budget+ Tool Output Compression│
│  Assessment: 10 binding forgotten test scenarios, check binding compliance rates│
│  Result: binding compliance rate from 72% Raise to 94%                          │
├─────────────────────────────────────────────────────────┤
│  Week 12: Problem finding— Planning Introduction│
│  User feedback: "Let it help me organize my notes for a week. It always leaves out some folders."│
│  Ask yourself: "The mission is linear or needs dynamic planning."?" → We need a branch.│
│  Introduction: Simple Rect mode, allowing Agent to decide next step by itself│
│  Assessment: 10 multi-step tasking, check step coverage and missing rates│
│  Result: missed rate from 20% Down to 5%                                │
├─────────────────────────────────────────────────────────┤
│  Week 16: Problem finding— HITL Introduction│
│  User feedback: "It deletes a document that I'm not sure I should, not asking me."│
│  Ask yourself, "What operational risks are high enough to be identified?"?" → Delete files, configure changes│
│  Introduction: Risk classification+ Confirm Mode+ Batch confirmation│
│  Assessment: high-risk operational recognition rate 100%,User error recognition rate< 5%             │
│  Result: No unexpected file deletion event, enhanced user trust│
├─────────────────────────────────────────────────────────┤
│  Week 18: No new capabilities introduced│
│  Reason: Current five capabilities are stable and no clear problem signals│
│  Reflection And Multi-Agent stays until there's evidence.│
└─────────────────────────────────────────────────────────┘
```

**Key observations:**

1. **Every capacity is introduced with a specific problem trigger** not because "others are using it"
2. **Every time it's introduced, it's a quantitative assessment.** It's not like it's getting better.
3. **There are enough observation periods between the two introductions** (2-4 weeks) and the pattern of issues is really clear
4. **Week 18 has chosen not to be introduced**, which is the easiest but equally important decision to ignore

### 9.1.5 What's the "minimal circle"?

Before we talk about the power mix, we need to figure out what the "minimal closure" is -- because you need to have something to run before you can introduce anything.

```text
Minimum Closed Ring= prompt + LLM Decision-making+ Tool Call+ Cycle control+ Status Management
```

**What can the smallest closed ring do:**

- Receive user commands
- Call tool to get information/ execute operations
- Results-based decision-making for the next steps
- Loop until the job is finished
- Return final result **Minimum closed circle boundary:**

```text
✅ is the smallest closed ring:
  - "Search this folder for all .md files."
  - "Replace the foo in this code with a bar."
  - "Read this CSV file. Count the number of each category."

❌ Capacity needs to be strengthened:
  - "Answer the question according to my notes." → Require RAG
  - "Remember what I said last time." → Yes, memory.
  - "It's a lot of information. It's a lot of context. → Needs Context Engineering
  - "Disassembly this need, one by one." → Require Planning
  - "Check your code for any bugs." → Request
  - ""This operation is too important for it to decide." → Could not initialise Bonobo
  - "Find someone to review your program." → Require Multi-Agent
```

**Importance of the minimum closed ring as a baseline:** Answer these questions with a minimum closed loop before introducing any enhancements:

1. **Can this task be done with a minimum closed ring?** → If so, why do we have to do it?
2. **Where's the card when it's done?** This is the only legitimate reason for introducing new capabilities.
3. **How much better is the new capability compared to the minimum closed ring?** → This is the baseline for evaluation

---

## 9.2 Capacity portfolio cases

The following six cases cover the most common Agent scene. Each case starts with a "start-up problem" and introduces capacity sequentially, with a clear indication that "not for the time being" — the latter is as important as the former.

#### Case I: Personal Knowledge Assistant

**Scene description:** Users have a large number of local notes (Markdown, PDF, Web Clip) and hope that Agent will be able to answer questions based on this information and give sources of reference. **Start question:**

- User information is extensive and the model does not know what the information is.
- User needs to cite the source. **Priority capacity:**
- **RAG / External knowledge access**. That's core competence -- without it, Agent can only give a generic answer, and it can't meet the core requirement of "my notes."**Minimal version achieved:**

```text
Document Directory → Document parsing (Markdown/PDF) → Plain Text)
 → Text split (500 to 1000 tokens per block by paragraph/heading)
 → Quantification to Embedding Mode
 → Deposit vector database (Chroma / Milvus / Pinecone)

User Ask → Query Quantification → Search Top-K (K)=5-10)
 → Collapse Retrieval Results to Prompt
 → LLM Generate answers (with reference tags)
```

**Assessment of dimensions:**

- Recall rate: Retrieving relevant documents found Blocks
- Accuracy of answer: Whether the resulting answers correctly use the information retrieved
- Quoting correctness: whether the reference mark points to the correct source
- Refusal rate: When the information is not relevant, Agent honestly indicates that he does not know **Follow-up questions:**
- Users would like to remember the current research theme and the next dialogue could continue.
- Multicycle queries need to be followed by context.
- There is a lack of correlation between the multiple questions and answers on the same subject. **Reintroduced:**
- **Summaries of sessions and lightweight Memoory**. Note that this is not the introduction of a complete long-term memory system, but a light solution to the specific issue of "Remembering the current research theme". **Memory Minimum:**

```text
End of each session:
 → Generate session summaries with LLM (research themes, key findings, pending issues)
 → Enduring storage (JSON file or light database)

Other Organiser
 → Load Recent Session Summary
 → Attach to system Prompt as context
 → Users can always ask "forget about the past."
```

**Not introduced:**

- **Multi-Agent** unless there is a clear need for parallel research or review. If the user is just a person, single Agent is totally enough.
- **Reflection**, unless there are clear systemic problems with the quality of search results. RAG's search quality issues should be addressed as a matter of priority by optimizing the segmenting strategy and adjusting the search parameters, rather than introducing Reflection so that it "checks itself".
- **Planning** unless the user's assignment becomes clearly multi-step (e.g. "Help me cross-check between the three sources"). **Introduction of path overview:**

```text
Minimum Closed Ring
 → RAG
 → Retrieving Quality
 → Memory
 → Steady running.
 → Planning?(Waiting for problem signals)
```

---

#### Case II: Code Review

**Scene description:** Team needs an Agent to review Pull Request, not only on the surface of diff, but also to understand the context of the code and perform test validation judgement. **Start question:**

- Agent, read diff only and output general recommendations (e.g., "Consider adding notes", "check empty pointers").
- I can't verify my judgment -- I can say, "there may be a performance problem," but I can't actually verify it.
- The absence of context is suggested - there is no understanding of the caller or caller for this function. **Priority capacity:**
- **Tool calls: reading files, searching codes, running tests**. It's the key to moving from "prisal censorship" to "in-depth censorship".
- **Reflection: modified judgement after test failure**. Agent needs to correct its own conclusions when the tool calls results that contradict the initial judgement. **Minimal version achieved:**

```text
Received PR diff
 → Analyse changes in diff
 → For every suspicious point, call tools:
      - read_file: Read full content of relevant documents
      - search_code: Search for all references for functions/ variables
      - run_test: Run relevant tests
 → Review based on the results of the tool
 → If the test fails, Reflect:
      - Analysis of causes of failure
      - Whether it's your judgment or the code is wrong.
      - Amendment review
 → Final output review report
```

**Key design decisions: why first introduce Reflect rather than Multi-Agent?** For the code review scene, the first response is "introducing Multi-Agent, writing one review." But if you examine Agent without the tools to call, the other Agent just says, "Read it again and diff give general advice" -- two blind people can't see it together.

The correct sequence is: **Let individual Agent call "see" through the tool, then "Correct" through the Reflection, and finally consider Multi-Agent's division of labour.**

**Follow-up questions:**
- After the review has reached a certain stage, Agent will need to conduct a second review of the revised code (to examine whether the revised code introduces new issues).
- There is a conflict between the role of a single Agent, who also plays the role of "reviewer" and "reviser" -- it may be too tolerant of its own proposals.

**Reintroduced:**

- **Multi-Agent**: One Agent reviews and makes recommendations and the other Agent reviews the revised code. Note that this is not a complete Multi-Agent system, but the "Reviewer Model" -- two Agent serial work, not complex coordination. **Multi-Agent Minimum:**
```text
Reviewer Agent(Reviewer:
  Input: PR diff
  Output: List of review comments
  Tools: Reading files, searching codes, running tests

Verifier Agent(Authenticator:
  Enter: Modified Code+ Reviewer Reviews
  Output: Validation report
  Conduct: an article-by-article examination of whether Reviewer ' s recommendations are correctly implemented
       Check if changes have introduced new questions

Conflict resolution rules (simple version):
  - If Reviewer and Verifier agree → Accepted
  - If there is disagreement → Mark it as "a manual review required."
  - Ban two Agents calling each other into a loop
```

**Not introduced:**

- **Long-term memory** unless it is necessary to remember project engagements, test habits or user preferences. If project specifications and testing strategies have been defined in the project document, the marginal benefits of Memoory are low.
- **Planning**, unless the review mission becomes clearly multi-step (e.g. "Censorship safety first, performance later, readability last"). **Introduction of path overview:**

```text
Minimum Closed Ring
 → Tool Use(In-depth analysis with tools)
 → Reflection(We can't fix it without an external signal.
 → Multi-Agent Reviewer(In the event of conflict of roles)
 → Steady running.
 → Memory?(Waiting for proof of need)
```

---

#### Case III: Individual assignments

**Scene description:** User hopes that Agent can help with complex multi-step tasks (e.g., "Appointing CI/CD for this open-source project"), to continue after the critical nodes have been suspended and support has been interrupted. **Start question:**

- The task is multi-step and easy to miss.
- The user wishes to confirm the key node (e.g. before creating GitHub Security).
- Manual tracking of the mission is cumbersome. **Priority capacity:**
- **Planning / Worklow Pattersons**. Multi-step missions naturally require structured organizations.
- **Human-in-the-loop**. Critical operations require manual validation, which is a safety requirement rather than an experiential optimization. **Minimal version achieved:**

```text
User task: "Setting repository CI/CD"
 → Planning Agent Dismantling:
      Step 1: Analyse project structure and define CI/CD scheme
      Step 2: Write CI Profiles
      Step 3: Generate a list of required Secrets
      Step 4: [HITL] Waiting for user confirmation of the Secrets list
      Step 5: Configure GitHub Securitys
      Step 6: Trigger First CI Run
      Step 7: [HITL] Check run results until user confirmation
 → Update status after implementation of each step
 → Users can view progress at any time
```

**Human-in-the-loop design elements:**
```text
✅ HITL Design:
  - Pause pending irreversible operation (delete, publish, change of authority)
  - Give clear options on pause: "Confirm execution / Skip / Modify parameters"
  - The default after time is "no execution"

❌ Bad HITL design:
  - Every step is suspended (recognised fatigue)
  - Not enough information to judge when paused
  - Automatically perform high-risk operations after timeout
```

**Follow-up questions:**

- This will continue after a long break.
- The history of mandate implementation requires traceability. **Reintroduced:**
- **Task status and Checkpoint**, part of which will go into six courses. The core idea is to perpetuate the mandate and support recovery from the point of interruption. **Checkpoint Minimum:**

```text
Task status structure:
{
  "task_id": "xxx",
  "goal": "Configure the warehouse with CI/CD."
  "steps": [
    {"id": 1, "desc": "Analysis of project structure, "status": "done"},
    {"id": 2, "desc": "Write CI Configuration, "status": "done"},
    {"id": 3, "desc": "Generate the Secrets List, "status": "in process"},
    ...
  ],
  "checkpoint_data": {
    "branch": "feature/ci-setup",
    "ci_file": ".github/workflows/ci.yml",
    ...
  },
  "last_updated": "2024-03-15T10:30:00Z"
}

Restore process:
  User Reconnection → Test not completed → Load Checkpoint → Continue from Breakpoint
```

**Not introduced:**
- Automatically long term, unless the user clearly requires a cross-mission preference. Independence between mandates is a feature rather than a flaw.
- **RAG**, unless task execution requires frequent access to external documents.
- **Multi-Agent** does not need parallels in a single user scenario. **Introduction of path overview:**

```text
Minimum Closed Ring
 → Planning + HITL(Mission structure and security requirements)
 → Checkpoint(Interrupted recovery needs)
 → Steady running.
 → Memory?(whether cross-mission preferences need to be sustained)
```

---

#### Case four: Smart customer service, Agent.

**Scene description:** Smart customer service for the electrician platform, which needs to answer product questions, process refunds, query the order status. Some of the issues can be dealt with automatically, sensitive operations (e.g. refunds) need to be manually identified and complex issues need to be transferred to manual passenger service. **Start question:**

- User consulting product information, Agent needs a product bank-based response.
- User query order status, Agent needs access to order system.
- Refund/exchange operations involve funds and inventories and cannot be implemented automatically. **Priority capacity:**
- **RAG / External knowledge access**: Product information, policy documents, FAQ etc. require real-time retrieval.
- **Tool Use**: Call an internal system of order query API, Logistics query API etc.
- **Human-in-the-loop**: sensitive operations such as refunds, exchange clearances require manual confirmation. **Why are these three capacities introduced simultaneously?** The special features of the guest scene are that RAG, Tool Use, HITL are not solving the "several deepening of the same problem" but are addressing the "three independent and simultaneous hard demands":
- No RAG → Product Information Unable to answer
- Unable to query purchase order without Tool Use
- There's no HITL. There's a financial risk of refund.

This is "the scenario itself requires multiple capabilities to produce the least available product". But even so, step-by-step verification is recommended - make sure the RAG is retrieved correctly, then access Tool Use, and finally add HITL. **Minimal version achieved:**

```text
User Message
 → Intent classification (product consulting / order query / after-sale processing / chat)
 → Route to corresponding process:

Product consultation process:
 → RAG Retrieving product knowledge base
 → Spelling results to generate answers
 → Additional product links

Order query process:
 → Authentication of user identity
 → Call order API
 → Format Order Information Return

Post-sale process:
 → Query order status
 → Determination of whether the condition for return of goods is met
 → [HITL] Refund if required → Generate refund requests → Pending manual clearance
 → [HITL] Approval approved → Execution refunds → Organisation
```

**Follow-up questions:**

- Users contact the client ' s service several times and are rejustified each time.
- Returners ' preferences and historical issues need to be remembered.
- When complex issues are transferred manually, artificial passenger service needs to see the context of the dialogue. **Reintroduced:**
- **Session Memory**: Remember the context of the current session and the recent history of contact. Attention is given to "talk-level" rather than "user-level long-term archives" — the former addressing the problem of repetitive statements, the latter involving privacy compliance. **Memory Design (Customs Special):**

```text
Sessional memory (7 days valid):
  - History of Dialogue in this Session
  - Products/orders covered by this session
  - Unsolved issues for this session

User-level memory (user authorization required):
  - Common receiving address
  - Recent 3 purchase records
  - Language preference

Memory cleanup strategy:
  - Session-level memory: 7 days to clear automatically after session
  - User-level memory: user ready to view and remove
  - Sensitive information (payment, password) never recorded
```

**Not introduced:**

- **Planning**: client dialogue is usually linear (if-else route) and does not require dynamic planning
- **Reflection**: feedback from the guest scene is from user satisfaction rating instead of Agent self-correction
- **Multi-Agent**: Unless two different roles, pre-sale and post-sale, need to be addressed simultaneously, but usually by route **Introduction of path overview:**

```text
Minimum Closed Ring
 → RAG + Tool Use + HITL(Scene needs, but in steps)
 → Memory(Reduced repetition of statements and attention to privacy boundaries)
 → Steady running.
 → Next steps based on user satisfaction data
```

---

#### Case V: Data Analysis Assistant

**Scene description:** Data analyst needs Agent to help write SQL, analyze data, and generate visualized reports. The task is usually multi-step: understand the need to write a query → validates the results → explains the finding → produces a chart. **Start question:**

- Users describe needs in natural languages, and Agent needs to be translated into SQL.
- After SQL execution, Agent needs to check whether the results match expectations.
- If the result is not correct, Agent needs to fix the query itself. **Priority capacity:**
- **Tool Use**: Implementation of SQL, reading table structure, query data dictionary.
- **Reflection**: SQL automatically check and amends when performance fails or results are abnormal. **Why first?**

For single-form queries and one-time indicators to calculate such tasks, the user ' s natural language has given the main analytical objectives - "Look at sales trends last month, split by region, and find the three fastest growing categories." The first thing to do at this point is not "will it plan" but "can it read Schema correctly, generate SQLs, perform queries and fix them when the wrong information appears."

But it's not that data analysis doesn't need Planning. Planning is of clear value only when the task is upgraded to cross-table exploration, staged validation assumptions, first checking A, then results-based B, and final consolidation visualization. The sequence should be to stabilize the implementation and validation loops and then introduce a multi-step analysis of needs into Planning. **Minimal version achieved:**

```text
User Needs → Agent Analysis:
  1. Read database Schema, understand table structure and fields
  2. Generate SQL queries
  3. Execute SQL
  4. Inspection results:
     - Successful implementation? → If failed, Refile: parsing error information, fixes SQL
     - Is the result reasonable?? → If the number of lines is 0 or the value is abnormal, Reflection: Check the query logic
     - The result is consistent with user intent? → Reasonable examination of results
  5. Explain the discovery.
  6. Optional: Generate visual codes (matpllotlib / eCharts)
```

**Reflection for specific applications in the data analysis scene:**
```text
Reflection Trigger condition:
  ✅ SQL Syntax Error → Read error information, correct syntax
  ✅ The results are empty. → Check if the WEREE conditions are too strict
  ✅ The values are clearly abnormal. → Check that JOIN is correct
  ✅ The result is a contradiction with common sense. → Remind users of possible data quality problems

Reflection Conditions for discontinuation:
  ❌ Amendment 3 failed → Informing users and requesting guidance
  ❌ I'm not sure it's right. → The label "needs manual verification."
  ❌ We found a problem with the data source itself. → Reporting problem. No further attempts at repair.
```

**Follow-up questions:**

- Complex analysis requires multiple steps (see table A, based on table B, combined analysis).
- User wants Agent to remember the usual analytical templates and preferences.
- The analysis across multiple data sources requires structured steps. **Reintroduced:**
- **Planning**: introduced when analytical tasks are upgraded from "one query" to "multi-step analysis process".
- **Memory**: Remember user analytical habits (commonly used indicators, preferred chart type, naming norm). **Not introduced:**
- **RAG**: unless analysis requires frequent reference to external methods for documentation or industry standards
- **Multi-Agent**: Single-person analysis scenario, no role conflicts **Introduction of path overview:**

```text
Minimum Closed Ring
 → Tool Use + Reflection(Translation+Amended, analyze the scene core)
 → Planning(After the need for multi-step analysis is identified)
 → Memory((Analysis of customary reuse needs identified)
 → Steady running.
```

---

#### Case VI: Writing Collaboration

**Scene description:** Users and Agent collaborate on technical blogs. Agent needs to understand the user style of writing, remember the points discussed earlier, retrieve references and perform quality checks based on external evidence after each change. **Start question:**

- User wants Agent consistent writing style.
- User needs Agent reference technology.
- After Agent has finished a paragraph, the user hopes that it will be able to check the problem (retroactivity of the reference, operation of the code example, compliance of terms with the agreement and whether user feedback has been processed). **Priority capacity:**
- **RAG**: Retrieving technical references, related articles, API documents.
- **Memory**: Remember user writing style preferences, terminology choices, structure habits. **Why is this scene being introduced at the same time by RAG+Memory?** In writing scenes, RAG and Memory solve different dimensions:
- RAG solves "What to write" - providing accurate technical content.
- Memoory solves "How to write" -- consistent style and terminology.

They are independent of each other but cannot be separated. There's no RAG inaccuracies, there's no memory incoherence. **Minimal version achieved:**

```text
Collaborative writing process:
  1. User proposes a writing theme
  2. Agent Search for Reference (RAG)
  3. Agent Memoory
  4. Agent Generate first draft
  5. [HITL] User review to propose changes
  6. Agent Based on feedback
  7. Agent Quality check:
     - Reference Validation (retribution original, confirmation of presence)
     - Code Example Test (run or static)
     - Check of terminologies/style lists (in contrast to explicit preference in Memoory)
     - User feedback check (article-by-article confirmation that changes have been processed)
  8. Output Final

Memory Storage structure (writing scene):
{
  "style_preferences": {
    "tone": "Professional but friendly."
    "sentence_length": ""The middle sentence is " ,
    "code_style": "Python, type hints "and shall add."
    "preferred_terms": {
      "use": ["Database, Query],
      "avoid": ["DB", "query"]
    }
  },
  "structural_habits": {
    "opening": "Story/problem introduction."
    "body": "Concept → Rationale → Example: → Attention."
    "closing": "Summary+ Extend reading."
  },
  "common_mistakes_to_avoid": [
    "Don't overdo passive speech."
    "Code examples need to be runable."
    "For the first time a technical term has appeared.
  ]
}
```

**Follow-up questions:**

- After changing multiple rounds, Agent needs to verify the quality of articles based on a clear check (not relying on user-by-user identification).
- The long articles are complex in structure and require section management. **Reintroduced:**
- **Reflection**: Quality check only for external feedback signals — can references be found in the original text, can code examples run, whether user changes are article-by-article covered, and if terms are consistent with the established style list.
- **Planning**: Structural planning and outline management. **Reflection in the design of the writing scene:**

```text
Trigger signal:
  1. Quote verification failed: source of generated content cannot be found in RAG original
  2. Code check failed: the code example cannot run, type check failed or output did not match expectations
  3. Inconsistencies in the list of terms: use of terms that users explicitly request to avoid
  4. User feedback not covered: there are still pending items in the list of changes

Amendments:
  - Auto run every chapter completed
  - When a problem is identified, only the corresponding problem will be corrected and the whole text will not be rewritten
  - Over two corrections of the same kind still failed → Mark and request user intervention
  - Purely subjective expression quality ( "Whether it's good enough" or "high-temperature") to the user or Reviewer list, without modeling self-assessment as Reflection
```

**Not introduced:**

- **Multi-Agent**: Writing is creative work, and an Agent co-reads enough. The introduction of the Multi-Agent "A Writing One Review" could lead to a lack of consistency in style.
- **Human-in-the-loop** enhanced version: Writing collaboration is naturally a HITL mode (HITL for each user review) and no additional system-level HITL mechanism is required. **Introduction of path overview:**

```text
Minimum Closed Ring
 → RAG + Memory(Exact content+ The same style)
 → Reflection(Quality check based on external signals)
 → Planning(Longform structure management)
 → Steady running.
```

---

## 9.3 Counter-model of capacity mix

I said, "Do what." This subsection says, "Don't do it."

#### Counter-model I: Capability Hoarding

**Symptoms:**

```text
"Our Agent used RAG.+ Memory + Planning + Reflection + Multi-Agent,
  And Tool Use, Guardrails, Human-in-the-loop..."
```

**Problem diagnosis:** Says "what" but says "why." Each ability is added to "if it works." As a result, the system was so complicated that no one could fully understand and no one could be held responsible for it. **The antidote:**

- Each ability must have a corresponding "issue/ticket" to record the reasons for its introduction.
- Regular "Capacity Inventory": Is it still working? Still solve the problem?
- If no one can explain why a power exists, consider removing it.

---

#### Counter-model two: "Online when it's perfect."

**Symptoms:**

```text
"RAG The rate of recall is 78.%,Wait till we optimize to 90.% Go back online."
"Memory "The strategy of oblivion is not ready.
"Planning "Sometimes it'll drift until we're done."
```

**Diagnosis of the problem:** Waiting for a perfect minimum is equal to never being published. Users prefer a flawed Assistant to wait for a non-existent Assistant. Furthermore, real use feedback is not available without publication and no real optimization without feedback. **The antidote:**

- Define "good enough" threshold, not "perfect".
- The ability below the threshold can be online but labelled as "experimental function".
- Set up a user feedback channel for real use driver optimization **Criteria for judgement:**

```text
Minimum standards for access:
☐ Availability of core functions?(Can't block it.
☐ Whether or not security issues are addressed?(No data leak, no hazardous operations.
☐ Is the failure pattern elegant??(Tell the user when there's a problem, instead of making a mistake
☐ Whether user can choose not to use?(Capability should be optional)

No standards to wait:
☐ Is performance optimal??(It'll be fine.
☐ Is the border fully covered??(♪ Some borders are only to be found ♪
☐ All assessment indicators met?(Real data may differ from evaluation data)
```

---

#### Anti-model three: blind and wind.

**Symptoms:**

```text
"Hacker News According to that article, Multi-Agent was the most important trend in 2024."
"We're all using LangGraph to do the Agent workflow. We should use it."
"XXX The company's technical blog says that Agent used Reflection. It worked well."
```

**Problem diagnosis:** The scene, data, constraints, users are different from you. The solutions that suit them don't necessarily suit you. The replacement of community hot spots with their own problem analysis is the fastest way to introduce unnecessary complexity. **The antidote:**

- When reading other people's programs, you focus on "what's wrong with them," not "what's the technology they use?"
- If you can't spell it out in one sentence, you can't introduce it.
- Think of community articles as "menu of options" instead of "list of necessity." **Conversion exercise:**

```text
Read: "We improved code review with Multi-Agent."
Don't think, "I should add Multi-Agent."
Think, "What's wrong with their code review?"?Do I have that too??
        What did they solve with Multi-Agent??Why isn't the single Agent enough??
        What's the bottleneck in my code review process??"
```

---

#### Counter-module IV: No assessment, no overlap after introduction

**Symptoms:**

```text
"We added it two weeks ago.
"Memory Plus, it doesn't work. It should work."
"Planning Sometimes the steps aren't right, but most of them are okay."
```

**Diagnosis of the problem:** Introduction capacity is only the beginning, not the end. The introduction of non-assessed capabilities is tantamount to adding "no impact" variables to the system. Over time, you don't know whether the quality of the system is rising or falling. **The antidote:**

- Each capability must be predefined when introduced
- Weekly/monthly access to assessment indicators to confirm no degradation
- Re-engineer all available capabilities when new capabilities are introduced and check if they affect each other **Evaluation of rhythm recommendations:**

```text
Pre-introduction: establishment of baseline assessments (current system performance on these indicators)
Week 1 after introduction: daily assessment (quick confirmation of correct direction)
Week 2-4 after introduction: weekly assessment (observation of performance after stable usage)
2nd month after introduction: monthly assessment (continuous monitoring to prevent degradation)
```

---

#### Counter-model V: Lack of coordination between capacities

**Symptoms:**

```text
RAG Retrieved, Memoory also wrote a copy.
Planning Generated a 5-step plan, but Reflect considers step 2 completed (inconsistent information)
Multi-Agent In which Agent A modified the file, Agent B does not know (state is not synchronized)
```

**Problem diagnosis:** Capabilities are not stand-alone plugins that share status and influence each other ' s behaviour. System behaviour is unpredictable when multiple capacities have different understandings of the same data. **The antidote:**

- Defining the boundaries of competence: who is responsible for what data
- Unified state management: all capabilities read through the same State layer Write
- Clear compacts (schema/format) for transmission of information between competencies
- Consistency between periodic checks **CAPACITY COORDINATION LIST:**

```text
☐ RAG Whether the search results are entered into the Memoory system?If so, is it necessary?
☐ Memory Whether the information in is affecting Planning step generation?
☐ Reflection Whether the amendments update the Planning status?
☐ Multi-Agent Whether or not the various Agness share the same Memoory view?
☐ An input assumption that an output change in one capability will destroy another capability?
```

When a combination of capabilities begins, they should not be matched by a Prompt ad hoc agreement, but should be carried at the time of operation: a unified State, Trade, Checkpoint, Eval regression and permission boundaries will be carried out in the Harness structure of Course 6. This chapter deals with "shouldn't it be a combination" and course six with "how to stabilize after a combination."

---

## 9.4 Gradual introduction of rhythms and signals

#### When should we speed up the introduction?

The following signals indicate that the user ' s needs have clearly exceeded the current system ' s capacity boundaries and that accelerated introduction is reasonable:

```text
Speed signal:
✅ User feedback on the same issue appeared within 2 weeks+ Minor
✅ Current capacity indicators continue to decline (reflecting growing demand but capacity not keeping pace)
✅ The competitor has provided this capability, and the users are losing.
✅ The solution to the problem is clear and the risks are manageable
✅ The user made it clear, "I can't continue without X."
```

**Speeding up does not represent a rush.** Even if it accelerates, keep the process of "inclusion of evaluation and observation". The acceleration is the observation cycle (e.g. from 4 weeks to 2 weeks) rather than skipping the evaluation.

#### When should we suspend and consolidate?

The following signals indicate that you need to stop and digest, rather than continue to add new capabilities:

```text
Pause signal:
🛑 Last introduced capacity assessment indicator is still unstable.
🛑 Known bug not fixed (over 3 open issue)
🛑 Team members say, "The system is too complicated for new entrants."
🛑 The percentage of "slow" and "unreliability" in user feedback is rising.
🛑 You find yourself unable to tell how many capabilities the current system has.
```

**The suspension is not a failure; it is responsible.** The suspension may include:
- Fix known bug
- Refine document and Trace
- Optimizing the assessment system
- Capacity no longer required for clean-up (see 9.5)
- Reduce system complexity

#### Three principles of rhythm control

**Principle I: a new variable at a time** Only a new capability is introduced at any given time. If a capacity is not working well when it is introduced, you can only determine that it is. You never know which one works and which brings the problem.

```text
❌ Also introduce RAG+ Memory:
  "Retrieving has improved, but the context of the cross-conference seems to have improved... not sure which reason."

✅ Introduce RAG first, stabilize 2 weeks later introduce Memoory:
  "RAG Include recall Rate from 0% Raise to 85%(It's the effect of RAG."
  "2 Introduction of memory after week, inter-session connection accuracy rate from 28% Raise to 80%(It's the effect of memory."
```

**Principle II: Assessment indicators always precede new capabilities** If you do not have a running evaluation process, do not introduce new capabilities. The introduction without an evaluation is like walking with your eyes closed -- you don't know if you're going right or if you're going further away from the target. **Principle III: Reissued periodically** Regardless of whether the system is stable or not, a capacity reset is regularly performed:

```text
Repetition checklist:
☐ Capacity per introduced: assessment of stability or improvement of indicators?
☐ Capacity not to be introduced: whether the reason for not being introduced is still valid?
☐ Is there a new problem pattern??
☐ Capability to be downgraded or removed?
☐ Can the overall complexity of the system be reduced??
☐ Is the system well understood by the team? (Can new members quickly start)?
```

## 9.5 Degradation and removal of capabilities

Most of the classes only say "how" and don't say "how." But mature system design and mature engineers must be able to judge when a capability should be removed.

#### When should we consider removing them?

| Signal | Annotations | Example: |
|------|------|------|
| **Problem disappeared** | The problem that was introduced to this ability no longer exists. | User changed workflow, no more cross-conferences, memory |
| **Capacity has never been used** | Plus consistently useless and very low usage rate (< 5%) | The Planning system is perfect, but 95% of the tasks are one step. |
| **Cost is greater than gain** | Capacity maintenance costs/delayed/mistakes exceed its value | Memoory often misreading causes user trouble, maintaining forgotten strategies takes longer than saving time. |
| **There are simpler options** | I found out I didn't need that ability to solve the problem. | Prompt Optimize + Better Tool Description achieves effects close to Planning |
| **Conflict with other capabilities** | The behavior of both abilities is contradictory, and users are confused. | Memoory remembers one style, but RAG retrieves examples of another style |
| **Evaluation indicators continue to decline** | Quality of capacity continues to deteriorate and optimizes costs High | RAG index updates are slower and recall rates continue to decline |

#### How to safely downgrade or remove

Removal capacity needs to be more cautious than introducing capacity, as users may already have relied on certain behaviours. **Downgrade removal process:**

```text
Step 1: Identification of impacts
  - Statistics of the frequency of use of the capacity
  - List user scenes that depend on this ability
  - Assessing changes in user experience after removal

Step 2: Finding alternatives
  - Whether core needs can be covered in a simpler way?
  - Can we get the power changed from "automated" to "activated on demand"??
  - Can we limit our capabilities to a smaller range??

Step 3: Gradual downgrading
  Option A: from Automatic to Manual
    Original: Momory Summary is automatically implemented for each dialogue
    Change: Only when user input/summarize

  Option B: Downsizing
    Original: Memoory
    Change: Memoory only records conversations that users clearly mark as "important"

  Option C: Replace with lighter
    Original: Complete Reforming
    Change: Fixed Chain process (if most tasks are standardized)

Step 4: Grayscale removal
  - Yes, 10.% Users turn off the capability and observe feedback
  - If no negative feedback, extend to 50%
  - If continuous, remove completely

Step 5: Recording decision-making
  - Why is it removed??Why was it introduced??What have you learned??
  - How does this experience help to introduce future capabilities to decision-making??
```

**Degraded better than direct removal:** In many cases, reducing capacity from "active" to "passive" is a better option:

```text
Current status: Memoory autorecords each session
After downgrade: Memoory only recorded when specified by the user

Current status: RAG auto-research every query
After demotion: RAG only triggers when the user mentions "check"

Current status: Planning Autodismantling all tasks
After downgrade: Planning only touches when the task exceeds 5 steps Fire!

Current status: Multi-Agent parallel processing
After downgrade: Default list Agent processing, start Reviewer when users add --review tags
```

#### Validation of effects after removal

After removing a capability, need to be confirmed:

- Has the problem previously addressed by that capacity re-emerged?
- Has the system delay improved?
- Has the user feedback changed?
- Has the maintenance burden been reduced?

If one capacity is removed, none of the above indicators change — that means that it is unnecessary and that the removal is correct.

---

## 9.6 Field exercise: capacity to make decisions for new scenes

Here are three new scenarios. For each scene:

1. To determine which capacities should be prioritized
2. Indicate which competencies are not introduced and why
3. Draw capability introduction path

#### Practice I: Review of legal instrumentsAgent

**Scene:** The law firm needs an Agent to assist the solicitor in reviewing the contract. Agent needed to check whether the contract terms were in compliance, whether there were risk clauses and whether key clauses were missing. The results of the review require final confirmation by a manual lawyer. **Binding:**

- The contract contents are highly sensitive and cannot be uploaded to external services
- Different contract templates for different industries (technology, finance, real estate)
- Possible legal risk of an error being reviewed
- All internal knowledge base (past case, contract template library) **Please judge:**
- Priority capacity:
- Not included:
- Entry path:

<details > <summary > </summary > **Priority capacity:**

- **RAG**: Need to retrieve the Institute ' s internal knowledge base (past case, contract template) and have to be locally deployed (privileged)
- **human-in-the-loop**: final decision on legal review must be confirmed by a human lawyer, which is a hard demand **Not introduced:**
- **Memory**: each contract is independent and cross-contract memory may lead to confusion of information
- **Planning**: contract review is structured (article-by-article) and a fixed review list is sufficient without dynamic planning
- **Reflection**: Agent self-inspects contracts of less quality than human lawyers and self-checks for external signals of lack of legal judgement
- **Multi-Agent**: Single-person review of scenes, an Agent + human lawyer confirmed sufficient **Introduction path:**

```text
Minimum Closed Ring (LLM)+ (contract reading tool)
 → RAG(Retrieval of knowledge base, comparison of contract terms)
 → HITL(Manually confirm nodes)
 → Steady running.
```

</details>

---

#### Practice II: Smart Home Control Agent

**scene:** Users interact with Agent by voice/text. Agent needs to control the lighting, air conditioning, curtains, sound, etc., to understand the user's daily habits and to adjust automatically to the scene (e.g. "I'm going to sleep" to trigger lights, close curtains, lower air conditioning). **Binding:**

- Low delay required for equipment control (<500ms)
- User habits vary from person to person.
- The scene trigger requires user confirmation (prevent error)
- Support multiple users (family members have preferences) **Please judge:**
- Priority capacity:
- Not included:
- Entry path:

<details > <summary > </summary >**Priority capacity:**

- **Tool Use**: Base capacity of control equipment (calling equipment API)
- **Memory**: Remember user preferences (temperature, light, common scenes)
- **Human-in-the-load**: confirmation to users when scene triggers (security requirements) **Not introduced:**
- **RAG**: Smart home control does not depend on external knowledge
- **Planning**: scenes are usually predefined ("Sleep" + Lights + Curtains + Temperature) without dynamic planning
- **Reflection**: Device control results can be confirmed by sensor feedback (lights turned off), no Agent reflection is required
- **Multi-Agent**: single-user service, no parallel **Introduction path:**

```text
Minimum Closed Ring+ Tool Use(equipment)
 → Memory(Remember user preferences)
 → HITL(Image confirmed)
 → Steady running.
```

</details>

---

#### Practice III: Auto-maintenance of technical documents

**scene:** Open-source project maintainer needs an Agent auto-maintenance technical document. When the code changes, Agent needs to detect which documents need to be updated, automatically generate the document PR and explain the changes in the PR. **Binding:**

- Consistency between documents and codes is essential.
- Need to understand the impact of changes across multiple documents
- Document quality influences the onboarding experience of new users
- Document changes require final approval by human defenders **Please judge:**
- Priority capacity:
- Not included:
- Entry path:

<details > <summary > </summary > **Priority capacity:**

- **Tool Use**: Read replacement code diff, search affected documents, create PR
- **Reflection**: Compare code and document consistency after document generation (e.g. check for API parameter names)
- **Planning**: complex changes may affect multiple documents and require structured processing **Not introduced:**
- **RAG**: document content is derived from the code itself and does not require external knowledge Library
- **Memory**: no cross-session status required for independent processing of each document update
- **Multi-Agent**: Single Agent can complete the full process of reading changes → updating documents → verifying consistency. PR Approval is done by human defenders, no need for Agent Reviewer.

Introduction path:

```text
Minimum Closed Ring+ Tool Use(Read codes, search documents, create PR)
 → Reflection(Validate document-code consistency)
 → Planning(Documents updated for multi-file changes)
 → Steady running.
```

</details>
