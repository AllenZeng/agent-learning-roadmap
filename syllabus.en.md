# Agent Learning Roadmap Syllabus

This syllabus explains the learning structure behind the Agent Learning Roadmap. The course is not ordered by concept popularity. It is ordered by the cognitive layers a learner usually needs when moving from "I have heard of Agents" to "I can design and ship an Agent product."

> English status: lessons 01-05 are available in English. Lessons 06-08 are currently available in Chinese and linked as such below.

## Learning Layers

| Layer | Lessons | Core Question |
| --- | --- | --- |
| Product intuition | Lesson 01 | What does an Agent product look like, and how is it different from a Chatbot or Workflow? |
| Paradigm understanding | Lesson 02 | Why did LLM Agents, tool use, ReAct, planning, reflection, and multi-agent patterns appear? |
| Minimal loop | Lesson 03 | What is the smallest working Agent loop? |
| Tool mechanism | Lesson 04 | How does tool calling become selectable, executable, controllable, reusable, and auditable? |
| Scenario enhancement | Lesson 05 | When should RAG, Memory, Context Engineering, Planning, Reflection, Human-in-the-loop, or Multi-Agent patterns be introduced? |
| Runtime engineering | Lesson 06 | How does a minimal Agent become a traceable, recoverable, evaluable, governable runtime harness? |
| Productization | Lesson 07 | How do Agent capabilities become trusted product experiences? |
| Integrated practice | Lesson 08 | How do the course concepts come together in a real project? |

```text
Foundation path: product intuition -> paradigm evolution -> minimal Agent loop
Capability path: tool mechanism -> scenario enhancement capabilities
Shipping path: runtime engineering -> productization -> project practice
```

The goal is to avoid treating RAG, Memory, MCP, Skills, Evaluation, and Guardrails as a flat list of "core modules." Learners first build the minimal loop, then learn which capabilities solve which scenario and engineering problems.

## Table of Contents

- [Learning Layers](#learning-layers)
- [Lesson 01: First Encounter with Agents](#lesson-01-first-encounter-with-agents)
- [Lesson 02: Agent Paradigm Evolution](#lesson-02-agent-paradigm-evolution)
- [Lesson 03: Minimal Agent Loop](#lesson-03-minimal-agent-loop)
- [Lesson 04: Tool Mechanism](#lesson-04-tool-mechanism)
- [Lesson 05: Scenario Enhancement Capabilities](#lesson-05-scenario-enhancement-capabilities)
- [Lesson 06: Harness Runtime Architecture](#lesson-06-harness-runtime-architecture)
- [Lesson 07: Agent Productization](#lesson-07-agent-productization)
- [Lesson 08: Project Practice and Ecosystem Tracking](#lesson-08-project-practice-and-ecosystem-tracking)
- [Recommended Learning Order](#recommended-learning-order)

## Lesson 01: First Encounter with Agents

Build product intuition before implementation details. The learner first observes real Agent products and learns to distinguish Chatbots, Workflows, and Agents.

### Core Questions

- What is an Agent?
- How is it different from a Chatbot or Workflow?
- Where does a product show Agent-like behavior?
- Why do users experience Agents as useful, surprising, unreliable, or hard to control?

### Core Content

- Agent vs Chatbot vs Workflow: the key question is "who decides the next step?"
- Product observation framework: task entry, decision authority, action capability, process visibility, user control, and failure recovery.

English lesson: [First Encounter with Agents](courses-en/course-01-first-encounter.md)

## Lesson 02: Agent Paradigm Evolution

Understand the Agent paradigm through problem evolution. Each new pattern appears because the previous stage exposes a limitation.

### Core Questions

- Why did traditional Agents rarely enter everyday user products?
- What changed when LLMs became the decision core?
- What problems did Function Calling, Toolformer, Plugins, and MCP solve?
- Why is ReAct a useful mental model for the Agent loop?
- Why do Planning, Reflection, and Multi-Agent patterns appear?

### Core Content

- Traditional Agent -> LLM Agent: from hand-written rules to model-driven goal understanding and dynamic decisions.
- Key paradigm shifts: Tool Use, ReAct, Planning, Reflection, Multi-Agent, MCP, and Skills.

English lesson: [Agent Paradigm Evolution](courses-en/course-02-evolution.md)

## Lesson 03: Minimal Agent Loop

The minimal loop is the foundation. Later capabilities extend this loop rather than replace it.

### Core Questions

- Why is an Agent more than an LLM call?
- How does the LLM decide the next step from context and state?
- How do tool and environment interactions feed back into later decisions?
- How does state management support multi-step work?
- How does loop control decide whether to continue, stop, retry, or fail?

### Core Content

```text
Agent = Prompt + LLM Decision + Tool / Environment Interaction + State + Loop Control
```

English lesson: [Minimal Agent Loop](courses-en/course-03-minimal-agent-loop.md)

## Lesson 04: Tool Mechanism

Tool calling is not just function execution. It is a full mechanism for definition, selection, execution, feedback, permission, audit, and reuse.

### Core Questions

- How does an Agent decide whether to call a tool?
- Why do tool calls fail?
- How should tools be described so the model knows when to use them?
- How should tool results return to the next decision?
- How should high-risk tools be controlled?
- How can repeated tool workflows become reusable capabilities?

### Core Content

| Stage | Common Problem | Mechanism |
| --- | --- | --- |
| Tool definition | The model does not know what tools exist or when to use them | Name, description, parameter schema, usage boundary |
| Tool selection | Wrong tool or invalid arguments | Routing, validation, `tool_choice` control |
| Execution and feedback | Failed execution or overly long results | Timeout, retry, structured errors, result summarization |
| Permission and safety | Tools may have real-world impact | Risk level, least privilege, approval, audit |
| Human-in-the-loop | High-risk decisions should not be automated | Confirm, reject, take over, roll back |
| MCP | Tool integration is fragmented | Protocol-based client/server integration |
| Skill | Repeated tool combinations need reuse | Procedural knowledge, default flow, failure handling |

English lesson: [Tool Mechanism](courses-en/course-04-tool-mechanism.md)

## Lesson 05: Scenario Enhancement Capabilities

Lesson 05 focuses on when to introduce extra capabilities and what complexity each one adds.

### Core Content

Context enhancement:

| Capability | Use When | Learn |
| --- | --- | --- |
| RAG / external knowledge | The Agent needs private documents, sources, or fast-changing knowledge | Embedding, chunking, hybrid search, rerank, citation, factuality |
| Memory | The Agent needs continuity across turns or sessions | Short-term memory, long-term memory, user preference, update and forgetting |
| Context Engineering | Multiple sources make context noisy or long | Context layering, token budget, priority, compression, structure |

Behavior enhancement:

| Capability | Use When | Learn |
| --- | --- | --- |
| Planning / Workflow | The task has multiple steps and dependencies | Chain, Router, ReAct Loop, Plan-Execute, Graph |
| Reflection | External feedback requires changing path | Feedback classification, handling strategy, stop condition |
| Human-in-the-loop | High-risk steps need human judgment | Confirmation, clarification, takeover, review |
| Multi-Agent | The task benefits from role separation or parallel work | Isolated context, structured communication, arbitration, cost boundary |

English lessons:

- [05-01 Scenario Enhancement Capabilities](courses-en/course-05-01-scenario-enhancement.md)
- [05-02 RAG / External Knowledge Access](courses-en/course-05-02-rag.md)
- [05-03 Memory](courses-en/course-05-03-memory.md)
- [05-04 Context Engineering](courses-en/course-05-04-context-engineering.md)
- [05-05 Planning / Workflow Patterns](courses-en/course-05-05-planning.md)
- [05-06 Reflection](courses-en/course-05-06-reflection.md)
- [05-07 Human-in-the-loop](courses-en/course-05-07-human-in-the-loop.md)
- [05-08 Multi-Agent](courses-en/course-05-08-multi-agent.md)
- [05-09 Capability Composition](courses-en/course-05-09-composition.md)

## Lesson 06: Harness Runtime Architecture

Move from "writing an Agent" to "designing an Agent runtime."

### Core Questions

- What engineering stages make up an Agent runtime?
- Where do Agent systems most often fail?
- How do Context Engineering, Orchestration, Checkpoint, Evaluation, Guardrails, and Observability help?
- What is the boundary between Harness and Orchestration?
- How should systems handle context compression, session recovery, delegation, and debugging?

Chinese lesson: [Harness Runtime Architecture](courses/course-06-runtime-architecture.md)

## Lesson 07: Agent Productization

Turn Agent capability into a product experience that users can trust and operate.

### Core Questions

- How should an Agent product expose uncertainty and process state?
- How should failure recovery, confirmation, and takeover be designed?
- How should cost, latency, safety, and evaluation be visible in product decisions?
- How should metrics drive continued iteration?

Chinese lesson: [Agent Productization](courses/course-07-productization.md)

## Lesson 08: Project Practice and Ecosystem Tracking

Use an integrated project to connect knowledge-based, tool-based, and task-execution Agent patterns.

### Core Questions

- How should a learner scope a realistic Agent project?
- Which capabilities should be included first?
- What should be validated before adding more complexity?
- How should the project keep up with a fast-moving ecosystem?

Chinese lesson: [Project Practice and Ecosystem Tracking](courses/course-08-project-practice.md)

## Recommended Learning Order

For systematic learning:

1. Lesson 01 -> Lesson 02 -> Lesson 03
2. Lesson 04
3. Lesson 05, section by section according to scenario needs
4. Lesson 06 -> Lesson 07
5. Lesson 08 as an integrated project

For hands-on-first learners:

1. Start with Lesson 03 and build the minimal Agent loop.
2. Read Lesson 04 when tool calling becomes necessary.
3. Return to Lesson 02 to understand why the patterns exist.
4. Add Lesson 05 capabilities only when your project exposes the matching problem.
5. Use Lessons 06-08 when moving from demo to product.
