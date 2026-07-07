# Course V: Site empowerment

## Introduction to the curriculum

After course 3 and course 4, you have a running Agent-LLM decision-making + Tool Call + State Management + Cycle Control. It deals with simple tasks that are stable: reading documents, making summaries and searching for replacements.

But once you put it in the real scene for weeks, you hit two different kinds of problems:

**Category I: Context — Information on which Agent's decision-making depends, where and how?** Private knowledge is not in the model parameters and external data cannot come in; user preferences and task status evaporates over one session; and when external knowledge and historical status are connected, multiple sources of information are injected into the context, from carefully designed inputs to expanding information piles. Such problems are addressed by **context enhancement**: RAG (access to external data), Memory (continuing historical status), Context Engineering (organizational multi-source information).

**Category II: behaviour issues — how can Agent organize implementation, collaboration, response feedback when faced with complex tasks?** Naked Rect Cycle has no mandate structure and multi-step tasks are prone to drift; classification, processing and discontinuation mechanisms are lacking following unusual feedback from the implementation process; high-risk operations lack decision-making authority boundaries; and single players cannot look at their work from multiple perspectives. Such problems are addressed by the enhanced behaviour patterns: Planning (missions decomposition and organization), Reflection (results-based decision-making closed loop), Human-in-the-loop (decision-making boundaries), Multi-Agent (multi-role division of labour collaboration).

These two sets of capabilities answer two fundamental questions. But they have one thing in common: **none of the mandatory core modules of Agent** — a minimum closed circle does not need them to run. They are selective introduction of empowerment by scene.

This course does not start with conceptual terms but begins with problems. Each chapter follows the same path:

```text
It's a problem. → Technical background. → Thinking.
 → Programme (core links + Code skeleton) → iterative path (from minimum version to production level) → Judge the boundary (when not)
```

After school, you don't have to do all seven types of abilities, but you should be able to judge when you face a new scene:

- Is the current scenario a context or a behavioural issue?
- Does the question really require some kind of empowerment?
- What is the added complexity of the project after its introduction?
- If so, which minimum version should begin?
- Under what circumstances should it be expressly excluded?

---

## Learning objectives

After this lesson, you will be able to:

1. **Scene-based empowerment**: instead of using RAG, Memory, Context Engineering, Planning, Reflecting, Human-in-the-loop, Multi-Agent as a fixed module list, the corresponding enhancements are selected according to the actual problem model
2. **Distinguishing between two types of enablement**: the question is "Where does the information on which decision-making depends come from, how do you manage it?" (better context) or "How do you organize, collaborate, recover from complex tasks"? (better behaviour patterns)
3. **Scenario judgement for each type of capability**: know when RAG, Memoory, what should be remembered, how context is stratified, which organizational model for complex tasks, Reflection must have external feedback signals, what operations must be identified by humans, Multi-Agent is introduced only when roles conflict or need to be parallel
4. **From the smallest version**: each capability has a path from V0 to the production level, without a one-time stacking structure
5. **Develop a capability introduction note**: explain why a capacity is introduced or not introduced with "problems, formulas, costs, trajectories, boundaries"

---

## Contents

- [Introduction to the curriculum](#introduction-to-the-curriculum)
- [Learning objectives](#learning-objectives)
- [Chapter I: Why learn from scenes for empowerment](#chapter-i-why-learn-from-scenes-for-empowerment)
  - [1.1 Two types of ceiling for the smallest Agent](#11-two-types-of-ceiling-for-the-smallest-agent)
  - [1.2 Two types of enhancements: context vs behaviour patterns](#12-two-types-of-enhancements-context-vs-behaviour-patterns)
  - [1.3 Common diagnostic processes introduced by capacity](#13-common-diagnostic-processes-introduced-by-capacity)
- [Follow-up chapter](#follow-up-chapter)
  - [Part I: Context enhancement](#part-i-context-enhancement)
  - [Part II: Enhancement of behaviour patterns](#part-ii-enhancement-of-behaviour-patterns)
  - [Final chapter: Portfolio of capacities and sequence of introduction](#final-chapter-portfolio-of-capacities-and-sequence-of-introduction)
- [References](#references)
- [Next class connect.](#next-class-connect)

---

## Chapter I: Why learn from scenes for empowerment

### 1.1 Two types of ceiling for the smallest Agent

You spent two weeks doing a personal knowledge assistant, Agent. It runs on the smallest closed ring of course three - LLM Decision + Tool Call + State Management + Cycle Control. The first month went smoothly, but the second began with problems coming up one after another.

These questions appear to be varied, but look closely at them and hit two different ceilings. 

**First ceiling: context. Where does it come from and how does it work?**

The least closed circle 'the context' is the System Prompt+User Message + Tool returns. All the information is in the current session, and the session is closed. This means three things:

- Private knowledge, real-time data other than model training data cannot be obtained by Agent. It can only remember "guess" by parameters.
- User preferences, project engagements, progress of the last mission are evaporated through one session. It has to start from scratch every time.
- When you access both the external knowledge (RAG) and the historical state (Memory), the new problem follows: multiple sources of information are simultaneously injected into the context, system hints, retrieval clips, memory recall, tool outputs, history messages are mixed — the context has changed from "detailed input" to "extended information piles". The model begins to ignore key constraints and fights between information.

These three levels - **access to external data, continuity of history, organization multi-source information** - jointly determine the quality of information for Agent decision-making. Corresponding enhancements were RAG (chap. II), Momory (chap. III) and Context Engineering (chap. IV).

**Second ceiling: behavior. How does Agent organize implementation, collaboration and recovery in the face of complex tasks?**

The minimum closed circle has only one naked rect loop: each step determines what to do next according to the current context. This model, "Check out what X" is okay, but it's not enough when it comes to more complex mission patterns:

- The task itself is multi-step, dependent — not "what to do next," but "how to break it down, how to do it in sequence, how to do it."
- There are errors in the implementation process — tools failed to call, returns abnormally and intermediate outputs did not match expectations. In the absence of a correction mechanism, errors are carried silently into subsequent steps.
- Some operations have irreversible effects — deleting files, sending messages, executing payments. Agent is technically capable of implementation, but judging whether it should or not requires human operational knowledge and risk awareness.
- Some tasks require multiple perspectives — creators and reviewers share the same context and consider themselves as naturally blind.

These four levels — **task break-up and organization, feedback-driven decision-making on the next steps, decision-making boundaries, multi-role division of labour** — together determine Agent's ability to handle complex tasks. Corresponding enabling capacities are Planning (chapter V), Reflecting (chapter VI), Human-in-the-loop (chapter VII), Multi-Agent (chapter VIII).

---

These two ceilings answered two fundamental questions about Agent's enhancement: where is the information on which decision-making depends? How can complex missions be organized, coordinated and restored? Course 3 and course 4 give you a run-away skeleton, and course 5 solves the problem of strengthening the skeleton in which direction when it encounters the complexity of the real scene.

### 1.2 Two types of enhancements: context vs behaviour patterns

The seven categories of capacity corresponding to the above seven issues are naturally divided into two groups. Their differences are not just "whatever," but the fundamental questions answered are different:

```text
┌─────────────────────────────────────────────────────────────┐
│                    Context enhancement (information dimension)│
│  Question: What's in Agent's Vision??                             │
│                                                             │
│  RAG → What? How does external knowledge get in the context?│
│  Memory → Remember what? How does it last?│
│  Context Eng → How does it work? How does multiple information sources fit into the context?│
│                                                             │
│  Three relationships: RAG and Memoory are information producers, Context Engineering│
│  Is an information organizer. Without organizers, the more producers, the more the context becomes.│
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   Behavioural enhancement (action dimension)│
│  Question: Agent how to "work"?                                  │
│                                                             │
│  Planning → How to break it down: how to break up a complex mission.│
│  Reflection → How? Should we try again, process it or stop it next time the feedback comes out?│
│  HITL → How? When should we decide?│
│  Multi-Agent → How? How do you work when a single player is not enough?│
│                                                             │
│  Four relationships: Planning Action, Reflecting Action Based on Feedback, HITL│
│  Binding action (border), Multi-Agent extension (scale).│
└─────────────────────────────────────────────────────────────┘
```

Why do you make this distinction? Two reasons:

**First, introduction order.** In real projects, you usually solve problems of information and then behavior. A person who doesn't even have a clear vision, and you've given it a complicated Planning model for nothing. It did the right task on the wrong message, and the result was wrong. The error clips that RAG retrieves, the outdated preferences recalled by Memory, the unorganized confusion context - the problem of these information dimensions will be magnified by the complex layout of Planning and Multi-Agent.

**Second, positioning issues.** When Agent behaves badly, it is a question of information or behaviour. The model answers are inaccurate — are the results of the search not correct (information questions) or are the tasks broken down wrong (behaviour questions)? Agent deletes the document that should not be deleted -- is it without HITL confirmation, or is it the wrong file classification in Memoory? Bringing the problem to the right dimensions will lead to the right direction.

The following table shows the coordinates of the next chapter — which does not require all of the lessons to be done — and turns to the corresponding section whenever the problem arises:

| Dimensions | Problem scene | Gene. | Empowerment | Add complexity after introduction |
|---|---|---|---|---|
| **Context enhancement** | External knowledge doesn't fit. | No answers in model parameters | RAG (Ch2) | Index maintenance, delayed retrieval, reference verification |
| **Context enhancement** | I'm losing my memory when I close my sessions. | Status evaporates with session | Memory (Ch3) | Writing strategy, privacy, memory pollution |
| **Context enhancement** | Information source 1 context to dump | Multi-Info Unordered Injection | Context Engineering (Ch4) | Layer design, budget transfer, overcompression |
| **Behavioural mode enhancement** | Multistep task drifting step | Naked. | Planning (Ch5) | Plan enforceability, reprogramming costs |
| **Behavioural mode enhancement** | I saw the feedback and I kept going. | Lack of decision-making closed loop | Reflection (Ch6) | Multi-wheel cost, condition to stop |
| **Behavioural mode enhancement** | It's up to you. | Models don't know what to do and what to do. | Human-in-the-loop (Ch7) | Block delay, confirm fatigue. |
| **Behavioural mode enhancement** | You'll see. | Single Agent Role Overload | Multi-Agent (Ch8) | Coordinated expenses, costs 2-5 times |

### 1.3 Common diagnostic processes introduced by capacity

Each time you want to introduce an empowerment, you ask five questions:

1. **What is the current problem?** Is it a lack of knowledge, a fractured state, a confused context, a dysfunctional mission, a lack of correction, a lack of autonomy, or an overload of roles?
2. **Is there a simpler solution?** For example, is it sufficient for users to provide context directly, to use fixed processes, to add tools to verify, to optimize the hint, and to add a confirmation step?
3. **What complexity would introduce this capability?** For example, RAG will introduce indexing and citation questions, Memoory will introduce privacy and pollution issues, Context Engineering will increase information layering costs, HITL will increase delay and interactive design complexity, Multi-Agent will introduce communication and debugging issues.
4. **How to make the smallest version?** First, a minimum assessable enhancement, rather than an initial complete architecture.
5. **How does it really get better?** There must be task sets, comparative indicators or manual acceptance criteria.

---

## Follow-up chapter

Starting with chapter II, each chapter is split into separate documents to facilitate separate reading, maintenance and subsequent expansion. Chapters are organized in the order of "information, behavior after behaviour":

### Part I: Context enhancement

| Chapter | Documentation | Theme |
|---|---|---|
| Chapter 2: RAG / External knowledge access | [course-05-02-rag.md](./course-05-02-rag.md) | External knowledge access links, RAGs and borders |
| Chapter III: Memory: Status sustainability | [course-05-03-memory.md](./course-05-03-memory.md) | Session status, long-term memory, writing and recall strategy |
| Chapter 4: Context Engineering / Context Project | [course-05-04-context-engineering.md](./course-05-04-context-engineering.md) | Context layer, Token budget, priority, compression and structure |

### Part II: Enhancement of behaviour patterns

| Chapter | Documentation | Theme |
|---|---|---|
| Chapter 5: Planning / Workflow Pattersons | [course-05-05-planning.md](./course-05-05-planning.md) | Chain、Router、ReAct、Plan-Execute、Graph |
| Chapter 6: Reflection: A closed loop for feedback-based decision-making | [course-05-06-reflection.md](./course-05-06-reflection.md) | Feedback signal, processing strategy, cessation conditions |
| Chapter 7: Human-in-the-loop - When Agent should not decide for himself | [course-05-07-human-in-the-loop.md](./course-05-07-human-in-the-loop.md) | Identification/ clarification/takeover model, frequency control, feedback learning |
| Chapter 8: Multi-Agent/ Multi-Intelligence Collaboration | [course-05-08-multi-agent.md](./course-05-08-multi-agent.md) | Independent context, structured communications, division of labour decisions, cost boundaries |

### Final chapter: Portfolio of capacities and sequence of introduction

| Chapter | Documentation | Theme |
|---|---|---|
| Chapter IX: Portfolio of capacities and sequence of introduction | [course-05-09-composition.md](./course-05-09-composition.md) | Capacity portfolio cases, introduction of decision sheets, competency description templates |

---

## References

### Recommended reading

- Lewis et al., Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks: https://arxiv.org/abs/2005.11401
- Shinn et al., Reflexion: Language Agents with Verbal Reinforcement Learning: https://arxiv.org/abs/2303.11366
- Yao et al., Tree of Thoughts: Deliberate Problem Solving with Large Language Models: https://arxiv.org/abs/2305.10601
- Microsoft AutoGen: https://microsoft.github.io/autogen/
- Anthropic, Building Effective Agents: https://www.anthropic.com/engineering/building-effective-agents
- OpenAI, A Practical Guide to Building Agents: https://cdn.openai.com/building-agents/practical-guide-to-building-agents.pdf

### Quick check on terminology

| Terminology | Brief explanation | This class is located. |
|---|---|---|
| RAG | Retrieval enhanced generation | Context enhancement: one of the means of external knowledge access |
| External knowledge access | Access to decision-making context for external information on models | Context Enhancement |
| Memory | Cross-cycle, cross-session or cross-mission continuity | Context Enhancement |
| Context Engineering | Project principles for hierarchical, budgetary, priority and structured management of the types of information in the context | Context enhancement: information organization layer |
| Planning | Dismantling and plan implementation | Improved behaviour patterns: complex mission organization |
| Workflow Pattern | Reusable Task Organizing Mode | Behavioural enhancement: Chain, Router, Graph, etc. |
| Reflection | Feedback-based decision-making closed loops: testing feedback for classification decision-making validation or discontinuation | Behavioural enhancement: Runtme Engineering Mechanism, not Natural Model Capacity |
| Human-in-the-loop | Introduction of human judgment at the critical nodes of the Agent decision-making chain | Improved behaviour patterns: decision-making boundaries |
| Multi-Agent | MultiAgent Division, Parallel, Mutual Review | Behavioural enhancement: high complexity enhancement |

---

## Next class connect.

Course six will enter the Harness running time structure. Course 5 addresses the issue of "When to introduce what enhances" and course 6 addresses the engineering question of "How to stabilize the carrying of these capabilities when they are introduced" — including the realization of the Context Pipeline project, the operational time control of Orchestra, the re-establishment of the Checkpoint, the Evaluation evaluation system, the Guardrails security protection and the Observancy observation debugging.
