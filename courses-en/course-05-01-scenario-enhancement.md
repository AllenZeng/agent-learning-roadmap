# Course V: Scenario-Driven Agent Enhancement

## Course Introduction

After Course III and Course IV, you already have a working Agent: LLM decision-making, tool calls, state management, and loop control. It can handle simple tasks reliably: reading files, summarizing content, searching, and replacing text.

But once you run that Agent in real scenarios for a few weeks, two very different kinds of problems start to appear.

**The first kind is a context problem: where does the information behind the Agent's decisions come from, and how is it managed?** Private knowledge is not stored in the model's parameters. External data does not enter the decision process by itself. User preferences and task progress disappear once the session ends. After you connect external knowledge and historical state, another problem appears: many sources start pouring information into the same context window, and the context changes from a carefully designed input into an expanding pile of mixed signals. This kind of problem is handled through **context enhancement**: RAG for retrieving external data, Memory for carrying state across time, and Context Engineering for organizing multiple information sources.

**The second kind is a behavior problem: when the task becomes complex, how should the Agent organize execution, collaborate, and respond to feedback?** A bare ReAct loop has no task structure, so multi-step work can drift. When tool calls fail or intermediate results look wrong, the Agent needs a way to classify the feedback, decide what to do next, and know when to stop. High-risk actions need clear decision boundaries. A single role is often not enough to review its own work from multiple perspectives. This kind of problem is handled through **behavior-pattern enhancement**: Planning for task decomposition and orchestration, Reflection for feedback-driven decision loops, Human-in-the-loop for decision boundaries, and Multi-Agent for role-based collaboration.

These two groups of capabilities answer two fundamental questions. They also share one important property: **none of them is required for a minimal Agent loop to run**. They are scenario-driven enhancements. You introduce them only when the problem in front of you justifies the extra complexity.

This course does not start from a list of concepts. It starts from the problems that force those concepts to exist. Each chapter follows the same path:

```text
Problem in context -> Technical background -> Design reasoning
-> Solution path (core flow + code skeleton)
-> Iteration path (from minimal version to production-ready version)
-> Boundary check (when not to use it)
```

By the end of this course, you do not need to master all seven enhancement capabilities in equal depth. What matters is that, when you face a new scenario, you can judge:

- Is this mainly a context problem or a behavior problem?
- Does this scenario really need an enhancement capability?
- What engineering complexity will the capability introduce?
- If you decide to introduce it, what is the smallest useful version?
- Under what conditions should you explicitly avoid introducing it?

---

## Learning Objectives

After this course, you will be able to:

1. **Choose enhancements from scenario problems**: treat RAG, Memory, Context Engineering, Planning, Reflection, Human-in-the-loop, and Multi-Agent as problem-driven options rather than a fixed checklist of modules.
2. **Distinguish the two major enhancement categories**: decide whether the problem is about "where decision-relevant information comes from and how it is managed" (context enhancement) or "how complex work is organized, coordinated, and recovered" (behavior-pattern enhancement).
3. **Make scenario-level judgments for each capability**: know when RAG is needed, what Memory should and should not store, how context should be layered, which organization pattern fits a complex task, why Reflection needs external feedback, which operations require human confirmation, and why Multi-Agent should be introduced only when role conflict or parallel work justifies it.
4. **Start from the smallest viable version**: understand the path from V0 to production for each capability, instead of stacking a full architecture from the beginning.
5. **Write a capability-introduction note**: explain why you are introducing, or not introducing, a capability using the structure "problem, solution, cost, iteration path, boundary."

---

## Contents

- [Course Introduction](#course-introduction)
- [Learning Objectives](#learning-objectives)
- [Chapter 1: Why Enhancement Should Start From Scenario Problems](#chapter-1-why-enhancement-should-start-from-scenario-problems)
  - [1.1 The Two Ceilings of a Minimal Agent](#11-the-two-ceilings-of-a-minimal-agent)
  - [1.2 Two Enhancement Categories: Context vs Behavior Patterns](#12-two-enhancement-categories-context-vs-behavior-patterns)
  - [1.3 A General Decision Process for Introducing Enhancements](#13-a-general-decision-process-for-introducing-enhancements)
- [Follow-up Chapters](#follow-up-chapters)
  - [Part I: Context Enhancement](#part-i-context-enhancement)
  - [Part II: Behavior-Pattern Enhancement](#part-ii-behavior-pattern-enhancement)
  - [Final Chapter: Capability Composition and Introduction Order](#final-chapter-capability-composition-and-introduction-order)
- [References](#references)
- [Connection to the Next Course](#connection-to-the-next-course)

---

## Chapter 1: Why Enhancement Should Start From Scenario Problems

### 1.1 The Two Ceilings of a Minimal Agent

Imagine you spent two weeks building a personal knowledge assistant Agent. It runs on the minimal loop from Course III: LLM decision-making, tool calls, state management, and loop control. During the first month, it feels smooth. In the second month, problems start showing up one after another.

At first, those problems look unrelated. But if you look closely, they hit two different ceilings.

**The first ceiling is context. Where does the information behind the Agent's decisions come from, and how is it managed?**

In a minimal loop, "context" usually means the system prompt, the user message, and tool results. Everything lives inside the current session. When the session ends, the information disappears. That creates three concrete problems:

- Private knowledge and real-time data outside the model's training data are unavailable. The Agent can only guess from parameter memory.
- User preferences, project conventions, and progress from the previous task do not survive across sessions. The user has to explain the same things again.
- After you connect external knowledge through RAG and historical state through Memory, a new problem appears: system prompts, retrieved snippets, recalled memories, tool outputs, and chat history all enter the same context. What used to be a designed input becomes an expanding information pile. The model starts ignoring key constraints, and different pieces of information conflict with each other.

These three layers -- **retrieving external data, preserving historical state, and organizing multiple information sources** -- determine the quality of the information available for Agent decisions. The corresponding enhancement capabilities are RAG (Chapter 2), Memory (Chapter 3), and Context Engineering (Chapter 4).

**The second ceiling is behavior. When the task becomes complex, how does the Agent organize execution, collaborate, and recover?**

A minimal loop usually has only a bare ReAct pattern: at each step, the Agent decides what to do next based on the current context. That works for tasks like "look up what X means." It is not enough for more complex work:

- The task has multiple steps and dependencies. The real question is not just "what is the next action?" but "how should the whole task be decomposed, ordered, and verified?"
- Execution can fail. Tool calls may fail, results may be abnormal, and intermediate outputs may not meet expectations. Without a recovery mechanism, errors silently travel into later steps.
- Some actions are irreversible or high impact: deleting files, sending messages, making payments. The Agent may be technically able to execute them, but deciding whether it should execute them requires human business judgment and risk awareness.
- Some tasks need multiple viewpoints. When the same Agent plays creator and reviewer at the same time, self-review has natural blind spots.

These four layers -- **task decomposition and orchestration, feedback-driven next-step decisions, decision-boundary control, and role-based collaboration** -- determine whether an Agent can handle complex work. The corresponding enhancement capabilities are Planning (Chapter 5), Reflection (Chapter 6), Human-in-the-loop (Chapter 7), and Multi-Agent (Chapter 8).

These two ceilings answer the two core questions of Agent enhancement: **where does decision-relevant information come from and how is it managed? How is complex execution organized, coordinated, and recovered?** Course III and Course IV gave you a working skeleton. Course V explains where to strengthen that skeleton when real scenarios become messy.

### 1.2 Two Enhancement Categories: Context vs Behavior Patterns

The seven capabilities above naturally form two groups. The difference is not just what they manage; the deeper difference is the question they answer.

```text
┌─────────────────────────────────────────────────────────────┐
│              Context Enhancement (Information)              │
│  Core question: What is inside the Agent's field of view?    │
│                                                             │
│  RAG          -> What should it retrieve?                    │
│                  How does external knowledge enter context?  │
│  Memory       -> What should it remember?                    │
│                  How does state continue across sessions?    │
│  Context Eng  -> How should context be managed?              │
│                  How do multiple sources become usable input?│
│                                                             │
│  Relationship: RAG and Memory produce information.           │
│  Context Engineering organizes information. Without an       │
│  organizer, more producers usually create more confusion.    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│           Behavior-Pattern Enhancement (Action)             │
│  Core question: How does the Agent get work done?            │
│                                                             │
│  Planning     -> How should the task be decomposed?          │
│  Reflection   -> After feedback appears, should it retry,    │
│                  repair, escalate, or stop?                  │
│  HITL         -> When should the Agent not decide alone?     │
│  Multi-Agent  -> When one role is not enough, how should     │
│                  work be divided and coordinated?            │
│                                                             │
│  Relationship: Planning structures action. Reflection adjusts│
│  action based on feedback. HITL constrains action boundaries.│
│  Multi-Agent expands action capacity and perspective.        │
└─────────────────────────────────────────────────────────────┘
```

Why make this distinction? There are two practical reasons.

**First, introduction order.** In real projects, you usually solve information problems before behavior problems. If an Agent cannot see the right information, adding a sophisticated Planning pattern will not help much. It will simply make a well-structured plan on top of bad inputs. Wrong RAG snippets, outdated memories, and disorganized context are information-layer problems; Planning and Multi-Agent orchestration can amplify those problems instead of fixing them.

**Second, problem diagnosis.** When an Agent behaves badly, first decide whether the failure is mainly about information or behavior. If the answer is inaccurate, is the retrieval result wrong, or is the task decomposition wrong? If the Agent deletes a file it should not delete, is the missing piece Human-in-the-loop confirmation, or did Memory store an incorrect classification for that file? Putting the failure in the right category points you toward the right enhancement.

The table below is the navigation map for later chapters. You do not need to finish the whole course before applying it. When a problem appears, jump to the matching capability.

| Dimension | Problem Scenario | Root Cause | Enhancement | Added Complexity |
|---|---|---|---|---|
| **Context enhancement** | External knowledge cannot enter the answer | The answer is not in model parameters | RAG (Ch2) | Index maintenance, retrieval latency, citation verification |
| **Context enhancement** | The Agent forgets once the session closes | State evaporates with the session | Memory (Ch3) | Write policy, privacy, memory pollution |
| **Context enhancement** | More information sources turn context into a junk drawer | Multiple sources are injected without structure | Context Engineering (Ch4) | Layer design, token-budget tuning, over-compression |
| **Behavior-pattern enhancement** | Multi-step tasks drift or miss steps | Bare ReAct has no task structure | Planning (Ch5) | Plan executability, replanning cost |
| **Behavior-pattern enhancement** | The Agent sees feedback but keeps going down the same path | Missing decision loop | Reflection (Ch6) | Extra rounds, clear stop conditions |
| **Behavior-pattern enhancement** | The Agent decides things it should not decide alone | The model cannot distinguish "can do" from "should do" | Human-in-the-loop (Ch7) | Blocking latency, confirmation fatigue |
| **Behavior-pattern enhancement** | The Agent reviews its own work and misses obvious issues | One Agent is carrying too many roles | Multi-Agent (Ch8) | Coordination overhead, 2-5x cost increase |

### 1.3 A General Decision Process for Introducing Enhancements

Before you introduce any enhancement capability, ask five questions.

1. **What is the current problem?**

   Is the problem missing knowledge, broken state continuity, messy context, poor task organization, lack of recovery, unsafe autonomy, or role overload?

2. **Is there a simpler solution?**

   Would it be enough for the user to provide context directly, for the system to use a fixed workflow, for a tool to add validation, for the prompt to become clearer, or for one confirmation step to be added?

3. **What complexity does this capability introduce?**

   RAG introduces index maintenance and citation problems. Memory introduces privacy and contamination problems. Context Engineering adds information-layering work. Human-in-the-loop adds latency and interaction-design complexity. Multi-Agent adds communication and debugging overhead.

4. **What is the smallest useful version?**

   Build a minimal enhancement that can be evaluated. Do not start by implementing the full architecture.

5. **How will you know it actually improved the system?**

   You need a task set, comparison metric, or human acceptance standard. Without evaluation, an enhancement is only architectural decoration.

---

## Follow-up Chapters

Starting from Chapter 2, each chapter is split into a separate file so it can be read, maintained, and expanded independently. The course is organized in the order "information first, behavior second."

### Part I: Context Enhancement

| Chapter | File | Topic |
|---|---|---|
| Chapter 2: RAG / External Knowledge Access | [course-05-02-rag.md](./course-05-02-rag.md) | External knowledge access flow, RAG iteration path, and boundaries |
| Chapter 3: Memory: State Continuity | [course-05-03-memory.md](./course-05-03-memory.md) | Session state, long-term memory, write and recall strategies |
| Chapter 4: Context Engineering | [course-05-04-context-engineering.md](./course-05-04-context-engineering.md) | Context layers, token budgets, priority, compression, and structure |

### Part II: Behavior-Pattern Enhancement

| Chapter | File | Topic |
|---|---|---|
| Chapter 5: Planning / Workflow Patterns | [course-05-05-planning.md](./course-05-05-planning.md) | Chain, Router, ReAct, Plan-Execute, and Graph patterns |
| Chapter 6: Reflection: A Feedback-Driven Decision Loop | [course-05-06-reflection.md](./course-05-06-reflection.md) | Feedback signals, handling strategies, and stop conditions |
| Chapter 7: Human-in-the-loop -- When an Agent Should Not Decide Alone | [course-05-07-human-in-the-loop.md](./course-05-07-human-in-the-loop.md) | Confirmation, clarification, takeover modes, frequency control, and feedback learning |
| Chapter 8: Multi-Agent Collaboration | [course-05-08-multi-agent.md](./course-05-08-multi-agent.md) | Independent context, structured communication, role division, arbitration, and cost boundaries |

### Final Chapter: Capability Composition and Introduction Order

| Chapter | File | Topic |
|---|---|---|
| Chapter 9: Capability Composition and Introduction Order | [course-05-09-composition.md](./course-05-09-composition.md) | Composition cases, introduction decision table, and capability-introduction template |

---

## References

### Recommended Reading

- Lewis et al., Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks: https://arxiv.org/abs/2005.11401
- Shinn et al., Reflexion: Language Agents with Verbal Reinforcement Learning: https://arxiv.org/abs/2303.11366
- Yao et al., Tree of Thoughts: Deliberate Problem Solving with Large Language Models: https://arxiv.org/abs/2305.10601
- Microsoft AutoGen: https://microsoft.github.io/autogen/
- Anthropic, Building Effective Agents: https://www.anthropic.com/engineering/building-effective-agents
- OpenAI, A Practical Guide to Building Agents: https://cdn.openai.com/building-agents/practical-guide-to-building-agents.pdf

### Terminology Quick Reference

| Term | Brief Explanation | Role in This Course |
|---|---|---|
| RAG | Retrieval-Augmented Generation | Context enhancement: one way to bring external knowledge into the Agent |
| External knowledge access | Bringing information outside the model into the decision context | Context enhancement |
| Memory | Preserving state across turns, sessions, or tasks | Context enhancement |
| Context Engineering | Engineering principles for layering, budgeting, prioritizing, and structuring context | Context enhancement: the information-organization layer |
| Planning | Task decomposition and plan execution | Behavior-pattern enhancement: complex task organization |
| Workflow Pattern | A reusable task-organization pattern | Behavior-pattern enhancement: Chain, Router, Graph, and related patterns |
| Reflection | A feedback-driven decision loop: detect feedback, classify it, decide, handle, verify, or stop | Behavior-pattern enhancement: a runtime mechanism, not a natural model ability |
| Human-in-the-loop | Adding human judgment at key points in the Agent decision chain | Behavior-pattern enhancement: decision-boundary control |
| Multi-Agent | Multiple Agents dividing work, working in parallel, or reviewing each other | Behavior-pattern enhancement: a high-complexity capability |

---

## Connection to the Next Course

Course VI will go deeper into Harness runtime architecture. Course V answers "when should we introduce which enhancement capability?" Course VI answers the engineering question that follows: "after these capabilities are introduced, how does the runtime carry them reliably?" That includes Context Pipeline implementation, Orchestration runtime control, Checkpoint recovery, Evaluation, Guardrails, and Observability.
