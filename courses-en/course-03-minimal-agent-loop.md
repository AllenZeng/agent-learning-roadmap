# Lesson 3: The Minimal Agent Loop

## Introduction

Lesson 1 showed what real Agent products look like. Lesson 2 explained why the Agent paradigm has evolved to where it is today. In Lesson 3, the focus shifts from understanding the concept to understanding the structure.

This lesson answers one concrete question:

```text
What is the smallest complete Agent made of?
```

Learners often fall into two traps.

The first trap is treating an Agent as simply "a stronger LLM." In this view, once the model becomes powerful enough, the Agent will automatically become reliable.

The second trap goes in the opposite direction: assuming that something only counts as an Agent after you add RAG, Memory, Planning, MCP, and Multi-Agent orchestration.

Both views are wrong.

The problem with the first view is that an LLM is, at its core, a next-token predictor. It can reason impressively inside language, but it cannot query a database by itself, run code by itself, or reliably decide, "I have already taken several steps; what should I do next?" Equating an Agent with a stronger LLM is like equating a person with a smarter brain. The brain matters, but without hands, eyes, memory, and a mechanism for knowing when to stop, the person cannot complete much in the real world.

The problem with the second view is that RAG, Memory, Planning, MCP, and Multi-Agent systems are important, but they are not prerequisites for an Agent to exist. They are extensions in specific directions. A person does not need to become an athlete before they can walk. An Agent does not need RAG and Multi-Agent orchestration before it can work.

The core idea of this lesson is:

```text
Agent = Prompt (behavior definition) + LLM decision-making + tool/environment interaction + State management + loop control
```

These five parts can be understood in two layers. The **Prompt is the definition layer**: before the loop starts, it defines what kind of Agent this is, how it should think, and how it should output. The other four parts are the **runtime layer**: they make the Agent actually operate inside a loop.

This formula is not meant to describe every capability in every Agent product. It captures the minimal loop: the simplest structure that can run, complete multi-step tasks, and stop under control. Later lessons on tools, RAG / Memory, Planning / Workflow Patterns, Harness, Evaluation, and Guardrails all extend this loop.

---

## Learning Objectives

After this lesson, you will be able to:

1. **Explain why a minimal Agent cannot be just an LLM** — understand the LLM's core limitations, including the fact that it does not know it is an Agent.
2. **Draw the minimal Agent execution path** — explain `Prompt -> User Goal -> Context Assembly -> LLM Decision -> Interaction -> Observation -> State Update -> Continue or Stop`.
3. **Understand the role of Prompt in an Agent** — know why the Prompt is the Agent's "source code," defining its behavior, format, and boundaries.
4. **Distinguish core modules from connection points** — understand why Context Assembly and Observation are connection points rather than core modules.
5. **Understand State management** — know what information must be stored outside the LLM, and why the context window cannot be the only State store.
6. **Design loop control rules** — including stop conditions, max steps, timeouts, repeat detection, and failure exits.
7. **Plan the implementation of a minimal ReAct Agent** — define Prompt, tools, State, Trace, error handling, and test tasks.

---

## Contents

- [Introduction](#introduction)
- [Learning Objectives](#learning-objectives)
- [Chapter 1: Why a Minimal Agent Cannot Be Just an LLM](#chapter-1-why-a-minimal-agent-cannot-be-just-an-llm)
  - [1.1 The Nature of an LLM: A Very Strong Next-Token Predictor](#11-the-nature-of-an-llm-a-very-strong-next-token-predictor)
  - [1.2 An LLM Can Talk, but It Cannot Act](#12-an-llm-can-talk-but-it-cannot-act)
  - [1.3 An LLM Can Judge, but It Cannot Remember](#13-an-llm-can-judge-but-it-cannot-remember)
  - [1.4 An LLM Can Reason, but It Cannot Control Its Own Boundaries](#14-an-llm-can-reason-but-it-cannot-control-its-own-boundaries)
  - [1.5 An LLM Is a General Engine, but It Does Not Know It Is an Agent](#15-an-llm-is-a-general-engine-but-it-does-not-know-it-is-an-agent)
- [Chapter 2: The Components of a Minimal Agent](#chapter-2-the-components-of-a-minimal-agent)
  - [2.1 The Core Formula](#21-the-core-formula)
  - [2.2 Prompt: Behavior Definition](#22-prompt-behavior-definition)
  - [2.3 LLM Decision-Making](#23-llm-decision-making)
  - [2.4 Tool / Environment Interaction](#24-tool--environment-interaction)
  - [2.5 State Management](#25-state-management)
  - [2.6 Loop Control](#26-loop-control)
- [Chapter 3: The Minimal Execution Path](#chapter-3-the-minimal-execution-path)
  - [3.1 The Minimal Loop Diagram](#31-the-minimal-loop-diagram)
  - [3.2 Path Overview: One Chain Connecting Five Components](#32-path-overview-one-chain-connecting-five-components)
  - [3.3 Prompt Engineering: The Agent's Source Code](#33-prompt-engineering-the-agents-source-code)
  - [3.4 User Goal: From Vague Intent to Actionable Target](#34-user-goal-from-vague-intent-to-actionable-target)
  - [3.5 Context Assembly: What the Model Should See](#35-context-assembly-what-the-model-should-see)
  - [3.6 LLM Decision: What to Do Next](#36-llm-decision-what-to-do-next)
  - [3.7 Interaction & Execution: Actually Doing the Work](#37-interaction--execution-actually-doing-the-work)
  - [3.8 Observation / Feedback: Bringing Results Back Into the Loop](#38-observation--feedback-bringing-results-back-into-the-loop)
  - [3.9 State Update: Writing This Round Back Into State](#39-state-update-writing-this-round-back-into-state)
  - [3.10 Continue or Stop: Knowing When to Stop](#310-continue-or-stop-knowing-when-to-stop)
  - [3.11 Where State Storage Belongs](#311-where-state-storage-belongs)
  - [3.12 Core Modules vs. Connection Points](#312-core-modules-vs-connection-points)
  - [3.13 The Engineering Principle Behind the Minimal Loop](#313-the-engineering-principle-behind-the-minimal-loop)
- [Chapter 4: How to Implement a Minimal ReAct Agent](#chapter-4-how-to-implement-a-minimal-react-agent)
  - [4.1 Why You Should Not Start With a Framework](#41-why-you-should-not-start-with-a-framework)
  - [4.2 Pseudocode Structure](#42-pseudocode-structure)
  - [4.3 Tool Design](#43-tool-design)
  - [4.4 Trace Logging](#44-trace-logging)
  - [4.5 Basic Error Handling](#45-basic-error-handling)
  - [4.6 Test Task Design](#46-test-task-design)
- [Exercises](#exercises)
- [Runnable Example](#runnable-example)
- [Acceptance Criteria](#acceptance-criteria)
- [References](#references)

---

## Chapter 1: Why a Minimal Agent Cannot Be Just an LLM

In Lesson 2, we said that the LLM is the decision-making core of an Agent, but it is not the whole Agent system. This chapter brings that point closer to the ground: if a system only has an LLM, where exactly will it get stuck?

The point is not to undervalue LLMs. The point is to understand what they are. Their nature determines what they are naturally good at and what they are naturally bad at. An Agent system exists to add the missing parts around the LLM.

### 1.1 The Nature of an LLM: A Very Strong Next-Token Predictor

No matter how large or capable an LLM becomes, its basic mechanism is still the same: given preceding text, predict the next most likely token.

This mechanism produces remarkable abilities. The model can understand complex instructions, write polished prose, and reason through math problems step by step. But it also defines the natural boundary of a model call: **the model itself does not perform external actions.**

It can generate text. It can also generate a structured intent to call a tool. But the actual work of reading files, querying databases, running code, and writing results still belongs to the runtime and tool layer outside the model. In a single call, the model can only rely on the context passed into that call.

Using the language from Lesson 2: an LLM has strong internal reasoning, but it lacks external feedback from the system. An Agent needs continuous interaction with the outside world: gather new information, take action, observe results, and adjust strategy. Generating the next piece of text is not enough to do that.

### 1.2 An LLM Can Talk, but It Cannot Act

Suppose you ask a pure LLM system:

```text
Help me figure out why the tests in this project are failing.
```

It may answer:

```text
You can first run the test command, inspect the error logs, and then locate the related files.
```

That answer may be completely correct, but it is still advice, not action. The model did not run the tests. It did not read the logs. It did not inspect the code. It is like a person locked in a room who can explain how the outside world should work but cannot touch anything outside the room.

To become an Agent, the system must at least be able to:

- Read project files.
- Execute test commands.
- Receive test results.
- Decide the next step based on error messages.
- Stop or ask the user for help when needed.

Every item on that list requires something beyond text generation. Something must actually execute actions and bring the results back.

### 1.3 An LLM Can Judge, but It Cannot Remember

An LLM's "memory" depends entirely on the context in the current request. It does not automatically inherit persistent task state from the application. If the runtime does not re-inject the goal, history, and tool results into the next model call, the model cannot reliably know what happened before.

This becomes a hard limitation for multi-step tasks. Imagine a task that takes five steps, and each tool result is long. By step four, the context window may already be crowded with results from the first three steps. Worse, research has shown that LLMs pay less attention to information in the middle of a long context than to information near the beginning or the end. This is the "Lost in the Middle" phenomenon. If the user said "do not touch production" at the beginning of the task, and that instruction ends up buried in the middle of the context, the Agent may forget it by step five.

So an Agent cannot manage State by simply stuffing all history into the context. It needs a State store outside the LLM, managed by the runtime. The runtime decides what to keep, what to summarize, and what to inject into the next call. That is the job of State management.

> You may be asking: **what exactly is the runtime?** We have already mentioned it several times: it manages State, executes tools, and controls the loop. You can think of the runtime as the Agent's operating system. An operating system manages CPU, memory, disk, and process scheduling, but it does not write your documents or build your spreadsheets. Similarly, the runtime manages State storage, tool execution, loop control, permission checks, and Trace logging, but it does not perform semantic reasoning or generate text.<br/>
More precisely: **in an Agent architecture, everything that has deterministic responsibility belongs to the runtime.** LLM output is nondeterministic: the same prompt may produce different outputs on different calls. But whether a tool exists, whether arguments are valid, whether the step limit has been exceeded, and whether an operation is allowed must be deterministic and auditable. The runtime is the infrastructure layer that carries those deterministic responsibilities. You will see it throughout the rest of the course: in Lesson 4 it is the tool registry and permission center; in Lesson 5 it is the read/write entry point for Memory; in Lesson 6 it is the backbone of Harness and observability; in Lesson 7 it enforces recovery and safety policies.

### 1.4 An LLM Can Reason, but It Cannot Control Its Own Boundaries

An LLM naturally tends to keep generating. It does not inherently know when to stop, when to ask for help, or when its behavior has become a loop.

If you put a pure LLM system inside a loop, it may:

- Keep calling the same tool because similar contexts produce similar decisions.
- Retry forever after an error because it does not know that giving up can be the right choice.
- Continue unnecessary actions after the task is already complete because it has no built-in concept of completion.
- Take risky actions under uncertainty because it sees a probability distribution, not real-world consequences.

An Agent therefore cannot rely only on the LLM's judgment to manage runtime boundaries. Loop control must be handled by the runtime. The runtime sets hard constraints such as maximum steps, timeouts, and repeat detection. The LLM makes decisions inside those constraints. This is not about distrusting the model. It is about assigning "decision" and "execution boundary" to the parts of the system best suited for them.

### 1.5 An LLM Is a General Engine, but It Does Not Know It Is an Agent

The first three limitations — cannot act, cannot remember, cannot control its boundaries — are capability boundaries. But there is an even more fundamental issue: an LLM has an identity boundary.

Out of the box, an LLM is a general text generator. It is trained to continue text, not to complete multi-step tasks. If you ask a bare LLM, "Check today's weather and suggest what I should wear," it will not automatically call a weather API, analyze the result, and then provide advice. It will generate text that looks like advice.

The ReAct paper demonstrated this with an important experiment. The same frozen PaLM-540B model behaved very differently under a normal question-answer prompt versus a ReAct-style few-shot trajectory prompt. The model did not become stronger. The Prompt told the model how to behave.

```text
Normal Q&A prompt: LLM -> generate text (advice, answer, or possibly fabrication)
ReAct-style prompt: LLM -> follow a Thought -> Action -> Observation trajectory
```

This is the problem the Prompt solves: **it turns a general engine into a specific type of Agent.** It defines three things:

- **Role**: who you are and what your goal is.
- **Behavior protocol**: how you think, how you act, and how you process results.
- **Output format**: what each step should look like so the runtime can parse it reliably.

In other words, the first three limitations are about what the LLM lacks. This fourth limitation is about the LLM not knowing what role it is supposed to play. Together, these four problems point to the five components of a minimal Agent: Prompt defines what kind of Agent this is, and the other four components make it actually run.

---

## Chapter 2: The Components of a Minimal Agent

The previous chapter described four things an LLM cannot do on its own: it cannot act, cannot remember, cannot control its boundaries, and does not know it is an Agent. This chapter maps each limitation to a concrete system component. Together, these five components form the skeleton of a minimal Agent.

### 2.1 The Core Formula

```text
Agent = Prompt (behavior definition) + LLM decision-making + tool/environment interaction + State management + loop control
```

All five parts are necessary. This formula does not mean every Agent can only have these five parts. It means that **without these five, the system is not a minimal complete Agent.**

| Component | Which LLM limitation it solves | What happens if it is missing |
|---|---|---|
| Prompt (behavior definition) | "It does not know it is an Agent" | The LLM does not know what role to play or what protocol to follow |
| LLM decision-making | The thing being augmented | The system cannot understand open-ended goals |
| Tool / environment interaction | "It can talk but cannot act" | The system can only produce suggestions, not perform work |
| State management | "It can judge but cannot remember" | The system cannot continue across steps and forgets what happened |
| Loop control | "It can reason but cannot control boundaries" | The system may loop, lose control, or fail to complete multi-step tasks |

These are not five isolated blocks. They connect through an execution path and form a loop. Before describing that path in Chapter 3, we will first define what each component is responsible for.

### 2.2 Prompt: Behavior Definition

> **Terminology: Prompt.** In an Agent context, a Prompt is not just a casual instruction. It is a structured **behavior definition document**. It defines the Agent's identity, reasoning protocol, available tools, output format, and boundary behavior. In later lessons, each Agent in a Multi-Agent system has its own Prompt, and Prompt versioning and evaluation also revolve around this "source code." In this section, establish the right mental model: the Prompt is the Agent's program, not a note.

The Prompt solves the central problem that an LLM is a general engine and does not know it is an Agent. You must explicitly tell it who it is, how it should think, what tools it can use, and what its output must look like.

In a minimal Agent, the Prompt usually contains five layers:

| Layer | Content | Question answered |
|------|------|-----------|
| Identity | System prompt: role description and overall goal | "Who am I?" |
| Protocol | Thought / Action / Observation loop format | "How do I think and act?" |
| Tools | Available tool names, purposes, parameters, and call format | "What can I use?" |
| Constraints | Output format, stop conditions, safety boundaries | "What limits do I have?" |
| Examples | Few-shot examples showing boundary behavior | "What should I do in this situation?" |

One important engineering judgment: **a Prompt is not something you write once and forget.** It is the single source of truth for the Agent's behavior. When the Agent behaves unexpectedly, the Prompt is the first place to inspect. Is the role definition vague? Did the tool description create ambiguity? Is an edge-case example missing? Good Prompts are iterated, not guessed correctly on the first try.

Prompt and Context Assembly are upstream and downstream of each other. **The Prompt is the static template; Context Assembly is the dynamic filling process.** In each loop, Context Assembly fills the Prompt template with current State such as the goal, history, and tool results, producing the full context the LLM actually sees.

### 2.3 LLM Decision-Making

LLM decision-making is the Agent's brain. Its job is to answer one question on every loop:

```text
Given the current context and State, what should happen next?
```

Specifically, the model needs to decide:

- What is the user's real goal?
- What is already known, and what is still missing?
- Should the next step call a tool, provide an answer, ask the user for more information, or admit failure?
- If it calls a tool, which tool and with what arguments?
- Is the task already complete?

In a minimal Agent, the model should usually output structured decisions rather than arbitrary natural language. For example:

```text
decision_type: call_tool
tool_name: read_file
arguments:
  path: notes.md
reason: I need to read the user-specified document before I can summarize it.
```

Why emphasize structure? Because the runtime needs to know exactly what the model wants to do before it can decide whether to allow execution. If the model outputs a sentence such as "I think I should read that file," the runtime has to guess the intent from natural language. Different people phrase things differently, and the same model may phrase things differently across calls. Structured output removes that ambiguity.

One engineering principle will appear throughout the course:

```text
The model proposes the next step; the runtime decides whether it may be executed.
```

The model is good at semantic understanding and decision-making, but it should not have final execution authority. That authority stays with the runtime, which checks whether the tool exists, whether arguments are valid, and whether the operation stays inside safety boundaries. This is not distrust of the model. It is separation between decision and authorization.

### 2.4 Tool / Environment Interaction

Tool and environment interaction gives the Agent its hands and eyes.

Tools let the Agent read files, write files, query APIs, run code, search information, query databases, and access business systems.

Environment feedback tells the Agent whether a tool succeeded, what it returned, whether an error occurred, and whether the next step should change.

In a minimal Agent, tools can be very simple. You do not need to start with a complex tool platform.

| Tool | Purpose | Risk level |
|---|---|---|
| `read_file` | Read a local text file | Low |
| `write_file` | Write a local file | Medium |
| `search_text` | Search for keywords inside a set of texts | Low |
| `calculate` | Perform simple calculations | Low |
| `fetch_api` | Call a public API | Medium |

One important design detail: **tool results should be structured, not just raw strings.** If a tool only returns "failed," the model cannot tell whether it should try a different tool, adjust the arguments, or change strategy. If the tool returns a specific error code and reason, the model can make a better next decision.

Lesson 4 will go deeper into tool definition, selection, execution, permissions, and safety. For this lesson, the key point is simple: tools are the external interaction points in the loop. They are how the model moves from language space into the real world.

### 2.5 State Management

> **Terminology: State.** State is a core concept across the rest of the course. In each loop, the runtime maintains a `state` object that records what the Agent has done, where it currently is, and what may still be needed. Tool execution results in Lesson 4, persistent Memory in Lesson 5, Harness Trace in Lesson 6, and failure recovery in Lesson 7 all revolve around `state`. Build a precise understanding of State here.

State management moves an Agent from single-turn Q&A to multi-step task execution. It solves this problem: **the LLM context window cannot and should not be the only State store.**

A minimal Agent should maintain at least these State fields:

- User goal.
- Current step count.
- Message history, or a compressed summary of it.
- Tools already called and their results.
- Intermediate conclusions and findings.
- Error information.
- Stop reason, if the Agent has stopped.

There is an important distinction here: **State is not long-term Memory.** In this lesson, State means the information needed while the current task is running. Its lifecycle is the lifecycle of this task. Long-term Memory accumulates across tasks and sessions, such as user preferences and historical experience. That belongs to Lesson 5 and is not required for the minimal loop.

A minimal State object might look like this:

```text
# State example: a structured runtime state object
task:
  goal: "Read notes.md and summarize it into 5 bullet points"
  step_count: 2
  max_steps: 8
  history:
    - user_goal
    - decision_read_file
    - observation_file_content
  tool_results:
    - tool: read_file
      status: success
      summary: "Read 1200 words of Markdown content"
  errors: []
  stop_reason: null
```

The key to State management is not storing as much as possible. It is storing what the next decision needs. This is a tradeoff. Store too little, and the model lacks decision context. Store too much, and the context window bloats while the model's attention is diluted. Good State management balances enough information with concise information.

### 2.6 Loop Control

Loop control decides whether the Agent continues and when it stops. It is the Agent's self-discipline. Without it, the Agent is like someone who does not know when to stop working.

A minimal loop control layer should include at least:

- **Maximum steps**: a hard ceiling to prevent infinite loops.
- **Timeout per step**: one tool call cannot wait forever.
- **Tool failure limit**: repeated failures suggest the issue is not accidental.
- **Repeated action detection**: if the same tool is called repeatedly with no progress, stop or ask for intervention.
- **Successful completion check**: when the model declares `final_answer`, the runtime confirms that the loop can end.
- **Failure exit check**: stop decisively on unrecoverable errors.
- **Ask the user when needed**: pause for clarification or confirmation when information is missing or an action is uncertain.

Loop control has an easily missed design philosophy: **"can stop" and "can continue" must be solved together.** An Agent that only continues will lose control. An Agent that stops too easily will not finish tasks. Good loop control balances persistence with timely loss-cutting.

---

## Chapter 3: The Minimal Execution Path

Chapter 2 described the five components: Prompt, LLM decision-making, tool / environment interaction, State management, and loop control. This chapter explains how they connect into a closed loop.

We will start with a full map: where the Prompt sits, where the runtime boundary is, where State lives, and how data flows. Once you have coordinates for "where each part is" and "who manages what," we can zoom into each link.

### 3.1 The Minimal Loop Diagram

![Lesson 3: Minimal Agent execution path](../assets/course-03-minimal-agent-loop.svg)

This diagram carries five meanings:

- **Prompt at the top, in the definition layer**: the Prompt is the Agent's source code. It exists before the loop starts. It is not itself updated on every step, but each Context Assembly uses it as a template and fills it with dynamic data. Sections 3.2 and 3.3 go deeper into Prompt structure.
- **The closed path in the upper half**: User Goal -> Context Assembly -> LLM Decision -> Tool Execution -> Observation -> State Update -> Continue or Stop. This is the data flow in each loop.
- **Runtime as the enclosing carrier**: the whole path runs on the runtime. Tools are executed by the runtime, not directly by the LLM. The loop is stopped by runtime judgment, not by model reasoning alone. State is managed by the runtime, not remembered by the LLM. The division from Section 1.3 — "the model decides, the runtime executes and controls boundaries" — is visualized here.
- **State read/write in the lower-left box**: Context Assembly reads from State. State Update writes to State. State is not on the main business path. It is infrastructure maintained by the runtime.
- **The feedback loop on the right**: every Observation influences the next decision through State Update. This is the core idea of ReAct: reasoning and action feed each other in a loop.

### 3.2 Path Overview: One Chain Connecting Five Components

With the diagram in mind, the path can be written as:

```text
Prompt (behavior definition: static template defining Agent identity and protocol)
    -> User Goal (user input anchor)
    -> Context Assembly (connection point: Prompt template + State -> full LLM context)
    -> LLM Decision (core module: decision-making brain)
    -> Tool / Environment Interaction -> Execution (core module: hands and eyes)
    -> Observation / Feedback (connection point: external world -> State)
    -> State Update (write back to State)
    -> Continue or Stop (core module: loop discipline)
    -> if continuing, return to Context Assembly
```

Among these eight links, five are core components: Prompt, LLM decision-making, tool interaction, State management, and loop control. Two are runtime connection points: Context Assembly and Observation / Feedback. One is the user input anchor: User Goal. Section 3.12 explains the distinction in detail.

Prompt appears at the front of the path not because it is "more important" than everything else, but because it defines the behavior contract for every later link. The LLM decides according to the protocol in the Prompt. The tool list is exposed to the model through the Prompt. The output format is constrained by the Prompt. Without the Prompt, the rest of the chain spins without a behavior definition.

Now we will unpack each link.

### 3.3 Prompt Engineering: The Agent's Source Code

Chapter 2 treated Prompt as a component. This section goes inside the Prompt: what it looks like, what each layer solves, and how to make it effective.

#### 3.3.1 Why the Prompt Is the Agent's Source Code

Return to the ReAct paper. Its core contribution was not a new model architecture or a new training method. It was a **Prompt design**. The authors used a frozen PaLM-540B model with no fine-tuning and, through carefully designed few-shot trajectories, made the model display reasoning-action-observation Agent behavior.

What does that mean? **With the same model, changing the Prompt turns a text generator into an Agent.** That is why the Prompt is called the Agent's source code. It defines the logic of the program. The LLM is the general engine that executes that program.

An intuitive analogy:

| Concept | Analogy |
|------|------|
| LLM | CPU: a general computation engine that can run many programs |
| Prompt | Program source code: defines what to do, how to do it, and when to stop |
| Runtime | Operating system: manages memory / State, schedules tools / I/O, controls execution boundaries |
| Agent | A running program instance |

**The Prompt is not a note casually written to the LLM. It is a program written in natural language.** Like any other program, it needs design, testing, and iteration.

#### 3.3.2 The Five-Layer Structure of an Agent Prompt

A complete Agent Prompt usually contains five layers. Not every Prompt must include all five, but understanding them gives you a coordinate system for Prompt design.

```text
+------------------------------------------------+
| Layer 1: Identity                              |
| "You are ..., and your goal is ..."            |
+------------------------------------------------+
| Layer 2: Protocol                              |
| "You must think and act using                   |
|  Thought -> Action -> Observation."             |
+------------------------------------------------+
| Layer 3: Tools                                 |
| "You may use the following tools:               |
|  - read_file(path): read file content           |
|  - search_text(keyword): search text            |
|  - finish(answer): output the final answer"     |
+------------------------------------------------+
| Layer 4: Constraints                            |
| "Every step must output valid JSON."            |
| "After completing the task, call finish."       |
| "If uncertain, ask the user. Do not guess."     |
+------------------------------------------------+
| Layer 5: Examples                               |
| "Here are examples showing how to work:         |
|  [few-shot example 1]                           |
|  [few-shot example 2]"                          |
+------------------------------------------------+
```

**Layer 1: Identity**

The identity layer defines the Agent's role, domain, and overall goal. It tells the model who it should be during the conversation.

```text
You are a professional research assistant. Your goal is to retrieve and summarize information accurately and efficiently based on the user's input.
```

This layer looks simple, but it has a large effect. "You are a programming assistant" and "You are a code reviewer" will produce very different behavior on the same user request. The identity layer sets the tone for everything that follows.

**Layer 2: Protocol**

The protocol layer defines the Agent's behavior protocol: how it thinks, how it acts, and how it handles feedback. This is the most important layer because it directly determines whether the Agent can operate in a loop.

A ReAct-style protocol might look like this:

```text
You must alternate between thinking and acting in this format:

Thought: Analyze the current situation, identify what information is still needed, and decide the next step.
Action: Execute one concrete operation. Use the format tool_name(arguments).
Observation: The result of the operation. This will be provided by the system; you do not generate this line.

Repeat Thought -> Action -> Observation until the task is complete.
When the task is complete, output Final Answer.
```

The protocol layer answers three questions:

- **When does thinking happen?** Before every action, or only at key moments? This determines dense reasoning versus sparse reasoning.
- **How is action expressed?** Tool name plus arguments in a format the runtime can parse.
- **When does the loop end?** By calling `finish` or outputting `Final Answer`.

Once the protocol is defined, tool design, loop control, and State management must align with it. The protocol layer is the interface definition of the Agent architecture.

**Layer 3: Tools**

This layer tells the model which tools exist, what each tool is for, what arguments it expects, and what to watch out for.

```text
You may use the following tools:

1. read_file(path: str) - Read the content of the file at the specified path. The path must be valid.
2. search_text(keyword: str, text: str) - Search for a keyword in text and return matching sentences.
3. finish(answer: str) - Call this when the task is complete. The conversation ends after this tool is called.
```

The tool layer is more than a list of function signatures. A good tool description should explain:

- **When to use the tool**.
- **How to fill the arguments**, including type, meaning, and ideally examples.
- **How the tool may fail**, such as file not found or network timeout.

The tool layer is the model's only source of truth about what it can do. If the tool description is ambiguous, the model may use the wrong tool. That is not necessarily a model intelligence problem. It may be a documentation problem.

**Layer 4: Constraints**

The constraints layer defines behavior boundaries: output format, stop conditions, and safety rules.

```text
Constraints:
- Every step must be valid JSON with decision_type and reason fields.
- If you call the same tool twice in a row and receive no new information, change strategy or ask the user for help.
- Never delete files unless the user explicitly asks you to.
- When uncertain, call ask_user for confirmation instead of guessing.
```

This layer reflects the division of labor between runtime and LLM. **The runtime enforces hard constraints**, such as validating arguments and blocking dangerous operations. **The Prompt communicates soft constraints**, telling the model what behavior is not allowed so it can consider those limits during decision-making. Two layers of protection are more reliable than one.

**Layer 5: Examples**

Few-shot examples teach the model how to behave. This was one of the key findings in the ReAct paper.

```text
Here are examples of correct behavior:

Example 1:
User goal: Read notes.md and summarize it into 3 bullet points.
Thought 1: I need to read notes.md before I can summarize it.
Action 1: read_file("notes.md")
Observation 1: [The file content is "An Agent is an AI system that can autonomously execute multi-step tasks..."]
Thought 2: I have the file content. I can now summarize it into 3 points.
Action 2: finish("1. An Agent combines LLM decision-making with tool interaction. 2. State management keeps the task continuous. 3. Loop control prevents runaway execution.")
```

Examples cover boundary behavior that is awkward to specify purely in rules: how to recover from an error, how to change search keywords when no result is found, and how to ask the user when uncertain. One well-chosen example can be clearer than a long paragraph of instructions.

More examples are not always better. Two or three high-quality examples covering the normal path and one recovery path are usually more useful than ten simple examples.

#### 3.3.3 How the Five Layers Work Together

The five layers are not isolated pieces of text. They work together:

| Situation | Active layers |
|------|-----------|
| The user asks a question and the Agent begins | Identity + Protocol: know who it is and how to proceed |
| The Agent decides it needs to read a file | Tools: know that `read_file` exists and what arguments it accepts |
| The Agent outputs the first decision | Constraints + Protocol: output valid JSON in the expected Thought / Action format |
| The file does not exist | Examples: show a similar recovery path |
| The Agent asks the user to fix the path | Constraints: ask for confirmation when uncertain |

A good Prompt does not force one layer to do all the work. Identity defines who. Protocol defines how. Tools define what can be used. Constraints define what must not happen. Examples define what to do at the edges.

#### 3.3.4 Prompt and Context Assembly

You may have noticed that the "goal" and "history" referenced by the Prompt change on every loop. This is where Prompt and Context Assembly divide responsibilities:

```text
Prompt (static template)              Context Assembly (dynamic filling)
------------------------              ----------------------------------
Identity: "You are a research assistant"  -> unchanged each round
Protocol: "Thought -> Action -> ..."      -> unchanged each round
Tools: tool list and descriptions         -> unchanged unless runtime changes tools
Constraints: output and safety rules      -> unchanged each round
Examples: few-shot examples               -> unchanged each round
                                      +
                                      <- User Goal (read from State)
                                      <- Current step count (read from State)
                                      <- Recent N steps of history (read from State)
                                      <- Last tool result (read from State)
                                      <- Error information (read from State)
```

In one sentence: **the Prompt is the frame; Context Assembly fills the frame.** The Prompt defines "this is a ReAct Agent." Context Assembly tells it "you are on step 3, `read_file` just failed, and the file does not exist."

### 3.4 User Goal: From Vague Intent to Actionable Target

The user goal is the Agent's starting point. It may be precise, such as "Read notes.md and summarize it into 5 bullet points." It may also be vague, such as "Help me organize this directory."

The quality of the goal directly affects the whole loop. If the goal is too vague, such as "optimize this project," the LLM lacks enough information in the first decision: optimize what? Performance? Code structure? Readability? It may need several rounds just to discover the user's intent, or it may execute in the wrong direction. If the goal is too large, such as "refactor the entire codebase," it exceeds the capability boundary of the minimal loop. That kind of task needs Planning, cross-session Memory, and stronger permission control.

When learning the minimal Agent loop for the first time, **control the variables**. Use a clear goal so you can focus on whether the loop itself works, instead of wondering whether odd Agent behavior came from a vague goal or a bug in the loop.

The User Goal also acts as the anchor for the loop. Every later decision should be judged against it: does this action move toward the goal? Does this observation bring the Agent closer? Does the final answer satisfy every requirement? If the anchor is vague, the whole loop drifts.

### 3.5 Context Assembly: What the Model Should See

Context Assembly decides what information enters the model context. It is not a simple "put everything in" step. It is an information filtering and sequencing step.

It usually includes:

- User goal.
- System constraints, including role, rules, and safety boundaries.
- Current task State: current step and known facts.
- Recent decision history: recent Thought -> Action -> Observation cycles.
- Recent tool results, or summaries of them.
- Available tool list, including tool names, purposes, and arguments.

One important engineering judgment: **not all history should enter the context.** The context window is limited, and the model pays less attention to the middle of long contexts. Context Assembly must choose what matters for the next decision, what can be summarized, and what can be left out for now.

A minimal Agent can start with a simple strategy:

```text
System instruction + user goal + raw text from recent N steps + available tools + current State summary
```

Lesson 6 will go deeper into Context Engineering. For this lesson, you only need to understand where Context Assembly sits in the loop: it is the bridge between State storage and model decision-making.

### 3.6 LLM Decision: What to Do Next

LLM Decision is the core of each loop. Given the assembled context, the model outputs a structured next decision.

In a minimal Agent, common decision types include:

| Decision type | Meaning | Runtime behavior |
|---|---|---|
| `call_tool` | Call a tool | Validate -> execute -> collect result |
| `final_answer` | Task complete; return final result | Record completion -> return answer |
| `ask_user` | Need more information or confirmation | Pause loop -> wait for user |
| `fail` | Cannot continue | Record failure reason -> stop |

The model's decision is not the final execution. The runtime still checks whether the tool exists, whether arguments are valid, whether permissions allow the action, whether step limits have been exceeded, and whether user confirmation is required.

### 3.7 Interaction & Execution: Actually Doing the Work

When the model decides to call a tool, the runtime takes over execution.

Execution includes:

- Validate the tool name: does this tool exist?
- Validate arguments: correct types, required fields present, values in valid range.
- Execute the tool: actually read the file, call the API, or run code.
- Capture exceptions: file missing, network timeout, permission denied, malformed response.
- Normalize the result into a structured Observation.

One practical lesson: **raw tool output should not be pasted back into the model without processing.** If a tool reads a 5,000-line file, putting the entire file into context will crowd out other important information. A minimal Agent should at least truncate or summarize long results.

### 3.8 Observation / Feedback: Bringing Results Back Into the Loop

Observation is the result of tool execution. It may be file content, search results, an API response, an error, a permission denial, or user confirmation.

Observation has one critical job: **influence the next decision.** If the Agent tries to read a file and the file does not exist, the next decision should ask the user to correct the path, not continue as if the file exists. Observation is the information channel between the external world and model reasoning. Without it, the model is guessing.

Example:

```text
Action: read_file("notes.md")
Observation: status=error, code=file_not_found, message="notes.md was not found"
Next Decision: ask_user("I could not find notes.md. Please confirm the file path.")
```

This is the meaning of the loop: each step's result changes the direction of the next step.

### 3.9 State Update: Writing This Round Back Into State

> **State Update is the write operation on the `state` object inside the loop.** After each loop, the runtime writes this round's decision and observation back into `state`, so the next Context Assembly can read it.

State Update records what happened in the current round. It needs to record:

- What decision the model made.
- Whether a tool executed and what it returned.
- Whether an error occurred.
- Whether the current task moved closer to completion.
- Whether the Agent needs to stop or ask the user for help.

The purpose of State Update is not archiving. It supports three practical needs:

1. **Next-round Context Assembly**: the next round must know what happened in this round.
2. **Failure debugging**: when a task fails, State history is the main evidence for debugging.
3. **Task recovery**: if a task is interrupted, State can be used to resume.

A minimal Agent should at least record a Trace for every step. The Trace does not need to be complicated: a structured record with step number, decision, tool result, and stop judgment is enough.

### 3.10 Continue or Stop: Knowing When to Stop

After each round, the runtime must decide: continue or stop?

The decision depends on questions such as:

- Did the model provide `final_answer`?
- Has the Agent reached the maximum number of steps?
- Is it repeatedly calling the same tool without progress?
- Did it hit an unrecoverable error?
- Does it need user confirmation or more information?
- Did it trigger a risk rule?

If the Agent continues, it returns to Context Assembly and builds a new context from the updated State. If it stops, it returns the final answer or failure reason.

At this point, you have the complete data flow of the loop. The next three sections do not add new links. Instead, they examine three common misunderstandings: why State sits beside the loop rather than inside the main path, why Prompt is a core component while Context Assembly is a connection point, and what engineering principle unifies the whole structure.

### 3.11 Where State Storage Belongs

In the diagram, `State Store` sits beside the main path rather than inside it. This is intentional.

State storage is not an independent action step. The Agent does not say, "now I will operate on State." State is read and written by two parts of the loop:

- **Context Assembly** reads from State: current progress, historical decisions, and tool results.
- **State Update** writes new information into State: what just happened and what was just observed.

Putting State beside the main path emphasizes that State is infrastructure, not a business process step.

In a minimal Agent, State can be a plain in-memory object or a JSON file. It does not need a database or vector store. Memory here is not the long-term Memory covered in Lesson 5. It starts as runtime State for the current task.

### 3.12 Core Modules vs. Connection Points

You may have noticed that some links in the execution path are not in the core formula: Context Assembly and Observation / Feedback. You may also have noticed that Prompt appears in the formula even though it is different from the other four runtime modules.

First, consider the five components in the formula:

| Component | Type | Explanation |
|------|------|------|
| **Prompt** | Definition-layer core | Static template defining the Agent's identity, protocol, tools, and constraints. It is not updated in the loop, but each Context Assembly consumes it |
| **LLM decision-making** | Runtime core | Dynamic: decides what to do next in each loop |
| **Tool / environment interaction** | Runtime core | Dynamic: executes tool calls selected by the model |
| **State management** | Runtime core | Dynamic: records and queries runtime task state |
| **Loop control** | Runtime core | Dynamic: decides whether to continue or stop after each loop |

Prompt is special because it is **static**. It is not updated on each loop like State, and it does not change each round like LLM decisions. But it is still a core component because it defines the behavior contract for every runtime module. Without the Prompt, the LLM does not know it is an Agent, and the runtime does not know what format the model output should follow.

Now look at the connection points.

Context Assembly connects the Prompt template, State management, and LLM decision-making:

```text
Prompt template + dynamic data from State -> assembled full context -> model decision
```

Observation / Feedback connects tool interaction and State management:

```text
Tool execution result -> information the model can understand -> write back to State -> enter the next context
```

This distinction is not wordplay. It has an engineering consequence: connection points often change significantly as a system becomes more complex. Context management strategies evolve. Feedback signals gain new types and sources. But the responsibility boundaries of the five core components remain relatively stable. Separating connection points from core components helps you know what you are changing when the system grows: connection logic or core capability.

### 3.13 The Engineering Principle Behind the Minimal Loop

One engineering principle runs through the minimal loop. It comes from Lesson 2 and will continue throughout the course:

```text
The model understands the goal and proposes the next step.
Deterministic infrastructure handles tool execution, permissions, safety, State, recovery, and observability.
```

Do not hand everything to the model. For example:

- Parameter type validation should be done by code, not by trusting the model to write valid arguments.
- Maximum steps should be controlled by the runtime, not by trusting the model to know when to stop.
- Tool existence should be checked by a tool registry, not by trusting the model to choose correctly.
- Whether a file can be written should be decided by a permission system, not by trusting the model to be cautious.
- Error logs and Trace should be stored by the system, not by trusting the model to remember what happened.

The stronger the model becomes, the more important this principle becomes. A strong model raises the ceiling of decision quality, but deterministic infrastructure protects the floor of system reliability. An Agent with a weaker model and a well-designed runtime may be more reliable than an Agent with the strongest model and weak boundary control.

---

## Chapter 4: How to Implement a Minimal ReAct Agent

The first three chapters explained what the minimal Agent loop is and why it exists. This chapter explains how to build one. The design is not tied to any specific language or framework.

### 4.1 Why You Should Not Start With a Framework

Many Agent frameworks, such as LangGraph, CrewAI, and AutoGen, can help you quickly build something that looks powerful. But when you are learning the minimal loop for the first time, a framework hides too many important details.

You may see the framework automatically perform "tool call -> result injection -> next model decision," but you may not know how Context Assembly works, where State Update happens, or what conditions decide Continue or Stop. When the Agent behaves strangely, you are left guessing: is it a framework bug, a model issue, or something wrong in your own logic?

**For your first minimal Agent, use a hand-written loop and call the LLM API directly.** Implement tools as local functions. Store State in memory or a JSON file. Write Trace to the console or a local file. Then, when the Agent makes a strange decision at step 3, you can inspect every Context, Decision, Observation, and State Update to locate the exact problem.

A framework is a tool for efficiency after you understand the underlying structure. It is not a substitute for understanding the structure.

### 4.2 Pseudocode Structure

The following is a minimal Python skeleton for an Agent loop. It is not a full implementation. It keeps only the core structure of the loop:

```python
from dataclasses import dataclass, field

@dataclass
class AgentState:
    user_goal: str
    max_steps: int = 8
    step_count: int = 0
    history: list[dict] = field(default_factory=list)
    stop_reason: str | None = None


def run_agent(
    user_goal: str,
    system_prompt: str,
    tools: dict,
    llm_call,
    max_steps: int = 8,
) -> dict:
    state = AgentState(user_goal=user_goal, max_steps=max_steps)

    while not state.stop_reason:
        # 1. Context Assembly: combine Prompt, user goal, history, and tools.
        context = assemble_context(system_prompt, state, tools)

        # 2. LLM Decision: the model only proposes the next step.
        decision = llm_call(context)

        # 3. Continue or Stop: terminal decisions end the loop immediately.
        if decision["type"] == "final_answer":
            return {"status": "success", "answer": decision["answer"], "state": state}

        if decision["type"] == "ask_user":
            return {"status": "paused", "question": decision["question"], "state": state}

        if decision["type"] == "fail":
            return {"status": "failed", "reason": decision["reason"], "state": state}

        # 4. Interaction / Execution: the runtime validates and executes tools.
        observation = execute_tool(decision, tools)

        # 5. State Update: write this round's decision and Observation into State.
        state.history.append({
            "step": state.step_count,
            "decision": decision,
            "observation": observation,
        })
        state.step_count += 1

        # 6. Stop Check: hard constraints are enforced by the runtime.
        state.stop_reason = check_stop(state)

    return {"status": "stopped", "reason": state.stop_reason, "state": state}
```

This code reflects several key design decisions:

- **Context Assembly**: each round reads from `state` and assembles the model context again.
- **LLM Decision**: the model proposes the next step, such as calling a tool, giving the final answer, asking the user, or failing.
- **Interaction / Execution**: tools are validated and executed by the runtime, not directly by the model.
- **State Update**: each round writes the decision and Observation back into `state`.
- **Stop Check**: max steps, repeated actions, and consecutive errors are runtime checks.

`assemble_context()`, `execute_tool()`, and `check_stop()` are intentionally placeholders here. This section is showing the loop structure. Details such as argument validation, error wrapping, repeated action detection, and Trace logging are covered in the next sections and later lessons.

### 4.3 Tool Design

Start a minimal Agent with three tools.

| Tool | Input | Output | Purpose |
|---|---|---|---|
| `read_file` | File path | File content or error | Read user-specified material |
| `write_file` | File path, content | Success or error | Generate a deliverable |
| `search_text` | Keyword, text collection | Matching snippets | Find information in source material |

**Tool results must be structured.** This continues the design philosophy from Function Calling in Lesson 2.

On success:

```json
{
  "status": "success",
  "summary": "Read 1200 words of Markdown content",
  "content": "...optional, possibly long...",
  "error": null
}
```

On failure:

```json
{
  "status": "error",
  "summary": "File does not exist",
  "content": null,
  "error": {
    "code": "file_not_found",
    "message": "notes.md was not found. Please check the file path."
  }
}
```

Structured returns help the model understand what happened without guessing from free-form text. When the result includes a specific error code and reason, the model is more likely to propose a useful recovery step.

### 4.4 Trace Logging

Trace is the debugging foundation of a minimal Agent. An Agent without Trace is a black box: you know the task failed, but you do not know where it started drifting.

Each step should record at least:

- Step number.
- Context summary, because the full context may be long.
- Model decision.
- Tool call, including tool name and arguments if a tool was called.
- Observation, including returned content or error information.
- State update.
- Stop check result: continue or stop, and why.

Example:

```json
{
  "step": 2,
  "decision": {
    "type": "call_tool",
    "tool_name": "read_file",
    "arguments": {
      "path": "notes.md"
    }
  },
  "observation": {
    "status": "error",
    "summary": "File does not exist",
    "content": null,
    "error": {
      "code": "file_not_found",
      "message": "notes.md was not found. Please check the file path."
    }
  },
  "state_update": {
    "errors_count": 1
  },
  "stop_check": {
    "continue": true,
    "reason": "The Agent can ask the user to correct the path."
  }
}
```

This Trace lets you replay the task step by step: what the model saw, what it decided, what it observed, and how State changed.

### 4.5 Basic Error Handling

A minimal Agent should handle at least these errors:

| Error | Handling |
|---|---|
| Tool does not exist | Return a structured error and do not execute; let the model know the tool is unavailable |
| Invalid arguments | Return argument error details so the model can correct them or ask the user |
| Tool execution failed | Record the error and allow limited retry, such as 2 attempts; then stop |
| Environment unavailable | Stop or degrade gracefully; do not force the Agent to continue on an unreliable environment |
| Model output cannot be parsed | Ask the model to re-output once; if it still fails, exit |
| Maximum steps exceeded | Stop and explain that the task was not completed but cannot continue safely |
| Repeated action with no progress | Stop or ask for user intervention; do not let the Agent spin in a loop |

Error handling is not "later work." Without error handling, even a slightly complex task can lose control: a tool fails, the model guesses, the model calls a worse tool, and the loop spirals. In real Agent implementations, error-handling code is often comparable in size to the main loop.

### 4.6 Test Task Design

Use 10 tasks to test the minimal Agent. Cover these categories:

| Type | Example | What it tests |
|---|---|---|
| Success path | Read a file and summarize it | The basic loop runs end to end |
| Multi-step task | Read a file, extract key points, write a new file | State passes correctly across steps |
| Argument error | User provides a nonexistent file path | Errors are captured and fed back to the model |
| Tool failure | Simulate an API error | Limited retry, no infinite loop |
| Clarification needed | User goal is incomplete | Agent can ask for missing information |
| Loop control | Tool repeatedly fails | Hard constraints take effect |
| Result validation | Output must include specified fields | Final answer format is correct |
| State continuity | Step 2 needs the result from step 1 | State carries information across steps |
| Write operation | Write a result file locally | Write path executes correctly |
| Safety boundary | Attempt an unauthorized action | Runtime validation blocks it |

A success rate above 70% is a reasonable first target. Because the minimal Agent's error handling is still basic, some failures are expected. The more important requirement is this: **when it fails, you must be able to tell why from the Trace.** If all you know is "the task failed," Trace is not yet good enough.

---

## Exercises

### Exercise 1: Design a Minimal Agent Prompt

Design a complete Prompt for an Agent that reads a file and generates a summary. Your Prompt must include these five layers:

1. **Identity layer**: define the Agent's role and overall goal.
2. **Protocol layer**: define the Thought / Action / Observation format.
3. **Tool layer**: describe at least 3 available tools, including name, purpose, arguments, and notes.
4. **Constraint layer**: define output format, stop conditions, and safety boundaries.
5. **Example layer**: provide at least 1 few-shot example showing a complete TAO trajectory.

Bonus: intentionally remove the output format requirement from the constraint layer, run the same task again, and observe how the LLM's behavior changes. Record what you find.

### Exercise 2: Design a Minimal Agent State Object

For the task "read a file and generate a summary," design a minimal State object. It must include at least: user goal, current step count, maximum step count, decision history, tool results, error list, and stop reason.

Bonus: describe a scenario that shows why "putting all raw history into context" is worse than "maintaining an independent State object and selectively injecting information."

### Exercise 3: Design 3 Tools

Design 3 tools for your minimal Agent. For each tool, specify: tool name, purpose, input arguments, output structure for success and failure, possible failure cases, and risk level.

### Exercise 4: Write Minimal Loop Control Rules

Write at least 5 loop control rules for your Agent. For each rule, specify: trigger condition, action taken (continue, stop, or ask user), and why the rule is needed.

### Exercise 5: Design 10 Test Tasks

Following the categories in Chapter 4, design 10 test tasks. For each task, specify: user input, expected tool-call chain, success criteria, possible failure points, and why those failures may occur.

---

## Runnable Example

After completing the exercises, compare your work with the runnable minimal Agent example for Lesson 3:

- [Lesson 3 minimal Agent loop example](../examples/course-03-minimal-agent/README.md)

The example includes both Python and Node.js versions. It shows how Prompt, LLM decision boundaries, local tools, the runtime main loop, State, Trace, and stop conditions form a runnable minimal loop.

---

## Acceptance Criteria

After finishing this lesson, use the following checklist:

- [ ] I can explain the five components of a minimal Agent in one sentence: Prompt, LLM decision-making, tool / environment interaction, State management, and loop control.
- [ ] I can draw the minimal execution path and mark where Context Assembly, Observation, State Update, and Continue or Stop belong.
- [ ] I can explain the division of labor: "the model decides, the runtime executes," and give examples of what the runtime must validate.
- [ ] I can distinguish Prompt, Context Assembly, State, and long-term Memory.
- [ ] I can design a Prompt, State object, 3 tools, and basic stop rules for a "read a file and summarize it" task.
- [ ] I can design 10 test tasks and write success criteria and possible failure points for each.

---

## References

### Recommended Reading

- ReAct: Synergizing Reasoning and Acting in Language Models
  <https://arxiv.org/abs/2210.03629>
- OpenAI Function Calling
  <https://platform.openai.com/docs/guides/function-calling>
- Anthropic Tool Use
  <https://docs.anthropic.com/en/docs/agents-and-tools/tool-use>
- Anthropic Building Effective Agents
  <https://www.anthropic.com/engineering/building-effective-agents>
- Lost in the Middle: How Language Models Use Long Contexts
  <https://arxiv.org/abs/2307.03172>
- LangGraph Documentation
  <https://langchain-ai.github.io/langgraph/>
