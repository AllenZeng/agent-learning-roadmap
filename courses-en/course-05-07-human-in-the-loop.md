# Chapter 7: Human-in-the-loop - When an Agent Should Not Decide on Its Own

[Back to Course Five](./course-05-01-scenario-enhancement.md) | [Previous Chapter](./course-05-06-reflection.md) | [Next Chapter](./course-05-08-multi-agent.md)

## Chapter Outline

- [7.1 "It made the decision for me, and I was not there"](#71-it-made-the-decision-for-me-and-i-was-not-there)
- [7.2 "Can do" is not "should do": the gap between capability and permission](#72-can-do-is-not-should-do-the-gap-between-capability-and-permission)
- [7.3 Five HITL patterns](#73-five-hitl-patterns)
  - [7.3.1 Confirmation](#731-confirmation)
  - [7.3.2 Clarification](#732-clarification)
  - [7.3.3 Takeover](#733-takeover)
  - [7.3.4 Review](#734-review)
  - [7.3.5 Teaching Feedback](#735-teaching-feedback)
  - [7.3.6 Comparing the five patterns](#736-comparing-the-five-patterns)
- [7.4 Design decisions: what to ask, how often to ask, and how to present it](#74-design-decisions-what-to-ask-how-often-to-ask-and-how-to-present-it)
  - [7.4.1 Risk levels: which actions need human involvement](#741-risk-levels-which-actions-need-human-involvement)
  - [7.4.2 Frequency control: neither annoying nor careless](#742-frequency-control-neither-annoying-nor-careless)
  - [7.4.3 Context presentation: helping humans decide quickly](#743-context-presentation-helping-humans-decide-quickly)
- [7.5 Learning from feedback](#75-learning-from-feedback)
- [7.6 The evolution path: from "confirm everything" to precise intervention](#76-the-evolution-path-from-confirm-everything-to-precise-intervention)
- [7.7 Five HITL anti-patterns](#77-five-hitl-anti-patterns)
- [7.8 When HITL is not needed](#78-when-hitl-is-not-needed)
- [Chapter Summary](#chapter-summary)
- [Runnable Example](#runnable-example)

---

## 7.1 "It made the decision for me, and I was not there"

Your knowledge-assistant Agent is now connected to RAG, Memory, Context Engineering, Planning, and Reflection. It can search your notes, remember your preferences, manage context, break down tasks, and recover from mistakes. You begin to trust it.

Then one day, you ask it to clean up some files.

```text
You: "Clean up log files older than 30 days under /tmp/logs."
Agent: "Sure." -> calls delete_file -> starts deleting
```

Suddenly, you notice a filename flash by: `.env.backup`. That was a backup file you manually placed there last week. It was not a log file. Before you can stop the Agent, the file is gone.

The Agent did not "turn bad." It followed your instruction. The problem is that "clean up log files" carried hidden constraints you did not spell out. The `.env` backup must not be deleted, but the Agent did not know that.

Here is another scene. You are testing a customer-support Agent. A user says, "I want a refund."

```text
User: "This product does not work for me. I want a refund."
Agent: "I am sorry for the poor experience. I have submitted a full refund request for you.
The money will be returned within 3-5 business days."
```

You stare at the screen and feel your palms sweat. The refund policy has not been defined yet. There is no amount limit, no eligibility rule, and no approval flow. The Agent just made a business decision on your behalf.

Both examples point to the same issue: **an Agent may be able to perform an action, but that does not mean it should perform the action autonomously.** There is a gap between capability and permission. It is not a technical gap. It is a judgment gap. The model does not fully know your business rules, your tolerance for risk, or the hidden constraints that even you may not remember to state.

Human-in-the-loop, or HITL, exists to solve this problem: **insert human judgment at the right points in the Agent's decision chain.**

## 7.2 "Can do" is not "should do": the gap between capability and permission

First, define three terms in the HITL context:

```text
Capability: what the Agent can technically do.
  Example: it can call delete_file, call refund_api, or send an email.

Permission: what the system allows the Agent to do autonomously.
  Example: delete_file is allowed, but requires human confirmation.
  refund_api is never allowed to run autonomously.

Judgment: whether this specific action is appropriate right now.
  Example: deleting /tmp/logs/access_2026.log is fine.
  deleting /tmp/logs/.env.backup is not.
```

The essence of HITL is this: **when an Agent has the capability to perform an action, but the system cannot exhaustively encode every judgment rule in code, return the judgment to a human.**

Why not just write rules in code?

- Is `.env.backup` a log file? The name says no, but the file is inside `/tmp/logs`. The Agent missed the hidden constraint.
- Is a full refund appropriate? That depends on refund policy, user history, order amount, delivery status, and more. A few `if` statements will not cover the real decision space.

HITL is not a complete safety mechanism. It does not replace permission checks, input validation, tool isolation, audit logs, or Guardrails, which are covered in Course Six, Chapter 7. HITL is better understood as a **decision-enhancement layer** in the defense stack. When the Agent's autonomous judgment is not enough for the risk involved, human judgment becomes part of the workflow.

## 7.3 Five HITL patterns

HITL is not just "show a confirmation dialog." Depending on when and how deeply the human participates, HITL usually falls into five patterns.

### 7.3.1 Confirmation

**Use this when** the Agent has already decided what it wants to do, but the action is risky enough to require human approval.

```text
Agent: "I will delete the following 12 files:
  - /tmp/logs/access_20260501.log (32MB, last modified 45 days ago)
  - /tmp/logs/error_20260515.log (8MB, last modified 31 days ago)
  - ...
  [Confirm] [Cancel] [Change scope]"
```

Confirmation has three design requirements.

**1. Show the consequence, not just the operation**

```text
Poor: "Confirm delete_file?"
The human cannot tell what will be deleted, how much will be deleted, or what the impact is.

Better: "12 files will be deleted, freeing 156MB. All files were last modified more than
30 days ago. Note: there are 3 non-log files under /tmp/logs (.env.backup, config.json,
README). They will not be deleted."
```

**2. Offer middle options, not only yes or no**

```text
[Delete all] [Only delete .log files] [Let me review one by one] [Cancel]
```

Binary confirmation pushes people toward "yes" because of decision fatigue. Middle options improve decision quality.

**3. Provide complete but concise context**

The human needs to see what will happen, why the Agent thinks it should happen, what the risks are, and what happens if the action is not taken.

### 7.3.2 Clarification

**Use this when** the Agent is unsure what the user means and needs the human to define the intent.

```text
You: "Organize the recent articles."
Agent: "'Recent articles' could mean:
  A. Articles written in the last 7 days (3 articles)
  B. Articles modified recently (8 articles)
  C. Articles opened recently (5 articles)
  Which one do you mean?"
```

The difference between clarification and confirmation is simple. Confirmation says, "I have decided, please approve." Clarification says, "I need you to help me decide."

Design requirements for clarification:

- **Offer concrete choices instead of throwing back an open-ended question.** Do not say, "Please clarify your request." Say, "Do you mean A, B, or C?"
- **Attach counts or examples to each option** so the human can choose based on information rather than guesswork.
- **Include an "Other" path** so the human can provide an answer the Agent did not consider.

### 7.3.3 Takeover

**Use this when** the action is too complex or too sensitive for the Agent to execute. The Agent should hand control back to the human.

```text
Agent: "The database migration script includes the following operations:
  - Change the type of the email field in the users table
  - Drop the deprecated_records table

  This type of operation requires manual execution. I have prepared the migration script:
  /tmp/migration_20260629.sql

  After you run it, reply 'done' and I will continue with the next steps."
```

The core difference between confirmation and takeover is this: in confirmation, the Agent executes and the human permits. In takeover, **the human executes and the Agent waits**. The Agent moves into a supporting role. It prepares, explains, and waits, but does not perform the action.

Takeover fits situations such as:

- Database schema changes
- Production deployments
- Operations that require compliance approval
- Any action that cannot be easily rolled back if it goes wrong

### 7.3.4 Review

**Use this when** the Agent has produced an output, but a human needs to inspect quality or choose among alternatives.

```text
Agent: "The technical proposal is ready and has 4 sections:
  1. Architecture overview (generated)
  2. API design (generated)
  3. Database design (generated)
  4. Security considerations (generated, with 3 open questions marked)

  [View full proposal] [Review section by section] [Edit a section] [Approve]"
```

The point of review mode is to help the human **find the parts that deserve attention quickly**. The Agent should proactively mark:

- Areas where it is uncertain
- Places where multiple reasonable options exist
- Recommendations that still need human judgment

Do not force the human to read the entire output just to make a decision. **Surfacing uncertainty is the most valuable part of review mode.**

### 7.3.5 Teaching Feedback

**Use this when** the Agent made a mistake or produced something inadequate, and the human correction should help it improve.

```text
Agent: "I generated the release checklist for you."
You: "Item 3 is missing the database backup step. The check command in item 6 is wrong:
use pytest, not unittest."
Agent: "Updated. I noticed this project consistently uses pytest. I will update Memory with:
  'Project test runner preference: pytest, not unittest.'
  Future release checklists will also include the database backup step."
```

Teaching feedback is where HITL meets Memory. Every correction from the human can become reusable knowledge. There are three levels:

| Level | What is learned | Scope |
|---|---|---|
| **Immediate correction** | The current task is fixed | Current task only |
| **Preference update** | The user prefers pytest | Future tasks in this project |
| **Pattern learning** | "A release checklist must include database backup" | Release-related tasks across projects |

Teaching feedback should not overpromise "automatic learning." For V0, immediate correction is enough. Preference updates and pattern learning require a Memory system, as discussed in Chapter 3.

### 7.3.6 Comparing the five patterns

| Pattern | Human role | Agent role | Intervention timing | Typical use case |
|---|---|---|---|---|
| **Confirmation** | Approver | Executor | Before execution | Deleting files, sending emails, Git push |
| **Clarification** | Definer | Executor | After understanding is incomplete | Ambiguous requests, multi-meaning instructions |
| **Takeover** | Executor | Assistant | During execution | Database migration, production deployment |
| **Review** | Reviewer | Creator | After output | Code review, proposal review |
| **Teaching Feedback** | Coach | Learner | After an error | Output mismatch, preference changes |

## 7.4 Design decisions: what to ask, how often to ask, and how to present it

### 7.4.1 Risk levels: which actions need human involvement

Not every action needs HITL. The core classification criteria are **irreversibility** and **severity of consequence**.

| Risk level | Action characteristics | HITL pattern | Examples |
|---|---|---|---|
| **Low** | Read-only, no side effects, repeatable | No intervention | Reading files, searching code, generating text |
| **Medium** | Writes are reversible and limited in scope | Confirmation, often batched | Creating or editing files, sending drafts |
| **High** | Writes are hard to roll back or affect external systems | Item-by-item confirmation | Deleting files, Git commit, API writes |
| **Critical** | Irreversible, or involves compliance, money, or security | Takeover, or item-by-item confirmation plus audit | Database migration, refund, deployment, permission changes |

Risk level is not fixed forever. The same action can move between levels depending on context:

- `delete_file` on a temporary file -> medium risk
- `delete_file` under `~/.ssh/` -> critical risk
- `send_email` of a draft to a teammate -> medium risk
- `send_email` to 1,000 customers -> high risk

So risk classification cannot depend only on the tool name. It must consider parameters and context.

### 7.4.2 Frequency control: neither annoying nor careless

The hardest part of HITL design is not "what should we ask?" It is "how often should we ask?"

**If you ask too often**, the human becomes a confirmation machine. Every step asks for approval, and the user quickly builds muscle memory: click "confirm" without reading. HITL becomes meaningless.

**If you ask too rarely**, the human loses awareness of what the Agent is doing. By the time a problem is noticed, the Agent may have already performed ten irreversible actions.

Several strategies help control frequency.

**Strategy 1: batch confirmation**

```text
Poor individual confirmations:
  "Confirm deleting access_20260501.log?" [Confirm]
  "Confirm deleting error_20260515.log?" [Confirm]
  "Confirm deleting debug_20260520.log?" [Confirm]
  ... 12 times

Better batch confirmation:
  "12 files will be deleted, freeing 156MB. 11 are .log files and 1 is .txt.
   [Delete all] [Only delete .log files] [Review one by one] [Cancel]"
```

**Strategy 2: trust accumulation**

If the user approves the same type of action five times in a row, ask: "Do you want to trust me with similar file operations and stop confirming them one by one?"

**Strategy 3: summary-based checkpointing**

Instead of confirming every step before execution, provide a summary checkpoint after a phase:

```text
"Previous phase complete: collected 8 relevant documents, 32KB total.
Ready to move into the writing phase.
 [Continue] [View document list] [Adjust direction]"
```

**Strategy 4: session-based trust decay**

Within one session, the Agent's understanding of user preferences usually becomes more accurate. Across sessions, trust should decay or reset because the task may have changed.

### 7.4.3 Context presentation: helping humans decide quickly

Humans also suffer from missing information when making HITL decisions. If a dialog only says, "Agent wants to execute refund. Confirm?" the human has no real basis for judgment.

A good HITL design gives a **concise but complete decision context**:

```text
Agent requests permission to issue a refund:

> User: Zhang San (ID: 12847)
> Order: ORD-20260629-0042
> Amount: ¥299.00 (full refund)
> Reason: User says "product functionality does not match the description"
> User history: registered for 2 years, 0 previous refund requests
> Order status: paid, not shipped

Agent judgment: eligible for refund under the 7-day no-reason policy because the order has not shipped.

[Approve refund] [Reject and provide reason] [Escalate to human support]
```

Key design principles:

1. **Highlight anomalies.** If "0 previous refund requests" becomes "5 previous refund requests," the UI should make that stand out.
2. **Make the Agent's reasoning visible.** Do not only tell the human what the Agent wants to do. Explain why the Agent reached that judgment.
3. **Offer context-aware actions.** Do not limit the decision to yes or no. Include options such as "escalate to human support."

## 7.5 Learning from feedback

Every HITL intervention is also a label. The human says "yes" or "no." If that signal is used only for the current decision, most of its value is wasted.

There are three levels of learning.

**Level 1: immediate application (always)**

The human decision changes the current task. "Reject refund" means the Agent stops the refund flow and tells the user accordingly.

**Level 2: preference update (with Memory)**

When the human repeatedly approves or rejects similar actions, update Memory:

```text
"User preference update: for cleanup operations under /tmp/logs, the user has approved
similar actions 3 times in a row. Next time, reduce confirmation frequency and use
batch confirmation."
```

**Level 3: policy adjustment (requires human review)**

Analyze HITL data: Which actions have low approval rates, suggesting the Agent's judgment is weak? Which actions are never rejected, suggesting HITL may no longer be needed?

```text
HITL data analysis (last 30 days):
- read_file confirmations: 120, approval rate 100% -> consider removing confirmation
- delete_file confirmations: 45, approval rate 89% -> keep confirmation
- refund confirmations: 8, approval rate 50% -> confirmation is not enough; consider takeover
- send_email confirmations: 30, approval rate 97% -> may downgrade to medium risk
```

This analysis should not change policy automatically. Humans should review the data and decide whether to adjust the strategy. The value of HITL data is that it gives policy changes evidence, not that it lets the system rewrite its own rules.

## 7.6 The evolution path: from "confirm everything" to precise intervention

| Phase | What it does | Best fit |
|---|---|---|
| **V0: fully manual** | High-risk actions are hard-coded as forbidden. The human performs them manually, then the Agent continues. | Prototypes, internal tools |
| **V1: confirmation for key actions** | All write actions show a simple yes/no confirmation dialog. | First version with real users |
| **V2: risk levels plus batch confirmation** | Different HITL patterns are used by risk level. Similar actions can be confirmed in batches. | Users start using the product frequently |
| **V3: context presentation plus learning** | Confirmation dialogs show decision context. Rejected preferences are written into Memory. | Trust-building stage |
| **V4: data-driven policy adjustment** | HITL approval data is used to tune risk levels and intervention patterns. | Mature products with ongoing optimization |

Most projects can start at V1. V0 is usually too conservative because the Agent cannot do anything useful. V4 only makes sense once there is enough usage data.

## 7.7 Five HITL anti-patterns

**Anti-pattern 1: confirming every step**

Every tool call shows a confirmation dialog. The result: the user clicks "confirm" 15 times in 30 seconds and reads none of them. HITL becomes meaningless.

**Better approach**: intervene only for high-risk and critical actions. Let low-risk actions run automatically.

**Anti-pattern 2: confirmation without enough information**

```text
"Agent wants to execute write_file. Confirm?"
```

The user does not know what will be written, where it will be written, why it will be written, or what the impact is. This dialog gives no basis for judgment.

**Better approach**: show the file path, a change summary, and the Agent's reasoning.

**Anti-pattern 3: treating HITL as the security mechanism**

Using HITL to prevent prompt injection or unauthorized operations: "A human will confirm it anyway, so we do not need validation."

**Better approach**: HITL is a decision-enhancement layer, not a complete security system. Security requires permissions, validation, isolation, audit logs, and Guardrails working together. Humans can also be tricked. An attacker can design context that makes "confirm" feel natural.

**Anti-pattern 4: no timeout handling**

The Agent waits for human confirmation. The human goes into a meeting. The Agent waits forever.

**Better approach**: define timeouts. The timeout behavior depends on risk. Low-risk actions may continue automatically; high-risk actions should stop safely.

**Anti-pattern 5: treating all users the same**

New users and experienced users see the same confirmation frequency.

**Better approach**: let users adjust their HITL level. "Developer mode" can reduce confirmations. "Safe mode" can increase them. Users should control how much autonomy they are willing to grant.

## 7.8 When HITL is not needed

1. **Low-risk informational Agents**: an Agent that only answers questions and does not execute tools with side effects usually does not need HITL before every response. But if the output affects high-risk decisions in medicine, law, finance, security, or compliance, human review or a clear disclaimer is still needed.
2. **Read-only operations**: if all tools are read-only, such as reading files, searching, or querying, there are no side effects. HITL adds almost no value.
3. **Reversible, low-impact personal actions**: for a personal Agent where actions are reversible and do not touch secrets, privacy, production systems, or external communication, HITL frequency can be reduced. But "personal use" should not mean every action is automatically allowed.
4. **Strong automated validation**: if actions are followed by automated tests, linting, or type checks, HITL frequency can be reduced significantly. Automated validation is more stable than human confirmation for properties that can be checked mechanically. It still cannot replace judgment about business intent, compliance, or user impact.

## Chapter Summary

HITL is not about making the Agent ask for permission at every step. It is about returning judgment to humans at the points where capability exceeds safe autonomous permission. The five core patterns are confirmation, clarification, takeover, review, and teaching feedback. Good HITL design depends on risk classification, frequency control, and context presentation. As the system matures, HITL should evolve from broad confirmations to precise interventions supported by feedback data.

## Runnable Example

After finishing this chapter, run the local Human-in-the-loop example for Course Five 05-07:

- [Course Five 05-07 Human-in-the-loop Example](../examples/course-05-07-human-in-the-loop/README.md)

The example covers three scenarios: file cleanup, refund handling, and release-document generation. It provides both Python and Node.js versions and demonstrates the five HITL patterns: confirmation, clarification, takeover, review, and teaching feedback. You will see how the same `delete_file` action can be classified as medium, high, or critical risk depending on path, reversibility, and impact. You will also see how an Agent should present consequences, anomalies, reasoning, and middle options when asking for human judgment.

The example also generates `hitl_audit.jsonl` and `hitl_memory.json`. These files demonstrate two ideas. First, HITL decisions should be audited instead of existing only as transient dialogs. Second, human review and correction can become reusable Memory, such as "release checklists must include a database backup step." This maps to the risk classification and context-presentation ideas in 7.4, and to feedback learning in 7.5.

The example is a teaching implementation, not a full production safety framework. Risk assessment is rule-based. Refunds and database migrations do not call external systems. The scripts only print decision context, subsequent workflow branches, and audit records. You must manually choose HITL decisions while running the example; pressing Enter uses the default option so you can observe the full flow continuously. A real system still needs permission checks, tool isolation, input validation, audit logs, and Guardrails working together.

```bash
# Python version
cd examples/course-05-07-human-in-the-loop/python
python3 hitl_demo.py
python3 -m unittest test_hitl_demo.py

# Node.js version
cd examples/course-05-07-human-in-the-loop/nodejs
npm start
```
