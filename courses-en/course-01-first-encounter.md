# Lesson 1: Your First Encounter with Agents

## Course Introduction

If you are reading this, you have probably already used ChatGPT, Claude, or a similar product. You ask a question, it answers. Sometimes the answer is impressive. Sometimes it is confidently wrong. At some point, you may have wondered:

> This thing is smart, but can it actually do work for me?

**That is the question this lesson is about.**

This lesson is not about theory, implementation, or architecture. It has one goal: **help you see what an Agent is and build an initial intuition for it.**

What does "see" mean? Open Claude Code and ask it to refactor a file. Open Cursor and watch how it reads your codebase. Open Kimi and ask it to prepare an industry research brief. You do not need to understand how these systems work internally yet, just as you do not need to understand an engine to feel a car accelerate.

What does "intuition" mean? After using these products, you should be able to judge:

- Is this product actually making decisions, or is it just following a fixed process?
- Which step felt smart? Which step felt clumsy?
- Who decided what happened next: the user, a fixed workflow, or the model?
- If you were designing this product, what would you change?

These intuitions are the fuel for everything that follows. For beginners, principles without experience quickly become empty vocabulary. When you learn the principles after using real products, each idea has a concrete image attached to it.

**This lesson is about firsthand product experience, not implementation details.** It gives you observation samples for Lesson 2, where we discuss the Agent paradigm, and for Lesson 3, where we build a minimal closed loop.

Ready? Let us begin with your first encounter.

---

## Learning Objectives

By the end of this lesson, you will be able to:

1. **Explain what an Agent is** by distinguishing it from a Chatbot and a Workflow, instead of being misled by the fact that all three may use an LLM.
2. **Judge an Agent by asking "who decides the next step?"** so you can tell whether the model is actually making decisions or a preset process is driving the interaction.
3. **Analyze any Agent product with a 7-dimension template** and move beyond vague impressions like "good" or "bad."
4. **Explain why users trust or distrust Agents** by connecting surprise, loss of control, and reliability to concrete design choices.

---

## Contents

- [Course Introduction](#course-introduction)
- [Learning Objectives](#learning-objectives)
- [Chapter 1: What Is an Agent?](#chapter-1-what-is-an-agent)
  - [1.1 Start with a Real Scenario](#11-start-with-a-real-scenario)
  - [1.2 An Agent Is Not Just a Smarter Chatbot](#12-an-agent-is-not-just-a-smarter-chatbot)
  - [1.3 Agent vs Chatbot vs Workflow](#13-agent-vs-chatbot-vs-workflow)
  - [1.4 The Core Question: Who Decides the Next Step?](#14-the-core-question-who-decides-the-next-step)
  - [1.5 A Practical Diagnostic Framework](#15-a-practical-diagnostic-framework)
- [Chapter 2: Build Task Intuition First](#chapter-2-build-task-intuition-first)
  - [2.1 What Tasks Are Suitable for Agents?](#21-what-tasks-are-suitable-for-agents)
  - [2.2 What Tasks Are Not Suitable for Agents?](#22-what-tasks-are-not-suitable-for-agents)
  - [2.3 Match the Task to the Product's Capabilities](#23-match-the-task-to-the-products-capabilities)
- [Chapter 3: Try Mainstream Agent Products](#chapter-3-try-mainstream-agent-products)
  - [3.1 Product Categories and What to Observe](#31-product-categories-and-what-to-observe)
  - [3.2 Experience Method: Use Each Product with Questions in Mind](#32-experience-method-use-each-product-with-questions-in-mind)
  - [3.3 Advanced Exercise: Test Different Products with the Same Task](#33-advanced-exercise-test-different-products-with-the-same-task)
- [Chapter 4: Product Breakdown and Analysis](#chapter-4-product-breakdown-and-analysis)
  - [4.1 A 7-Dimension Product Observation Template](#41-a-7-dimension-product-observation-template)
- [Exercises](#exercises)
- [Lesson Recap](#lesson-recap)
- [Acceptance Criteria](#acceptance-criteria)
- [References](#references)

---

## Chapter 1: What Is an Agent?

### 1.1 Start with a Real Scenario

Suppose you type this into a normal question-answering interface:

```text
Book me a flight from Beijing to Shanghai.
```

It will usually answer with something like:

> You can search on Ctrip, airline websites, or other travel platforms. Compare departure times, prices, and refund policies before booking.

Now give the same task to an Agent mode that can operate a browser, search the web, and fill out forms.

If permissions, website compatibility, and login state allow, the Agent can try to open a browser, search for flights, compare prices and departure times, choose a suitable option, and fill in the order page. When it reaches a high-risk step such as payment or final booking, it should stop and ask:

> I found a flight at 3:00 PM for RMB 850. Do you want to continue?

The difference is not the product name. It is the interaction pattern. The first system mainly answers a question. The second system pursues a goal, calls tools, observes results, and decides what to do next.

Here is a more everyday example: imagine you need to write a competitive analysis report. Do not judge only by product name, because the same product may have both a normal chat mode and Agent capabilities such as search, file analysis, or code execution.

**In normal chat mode**, you ask a question and the system gives you competitor names, an analysis framework, and writing suggestions. You still need to open the browser, search, read sources, extract information, and write the report yourself.

**With Agent capabilities**, you can say, "Prepare a competitive analysis for the XX market." The system searches company websites and news articles, extracts key information, compares product differences, writes a structured report, and cites sources. You mainly confirm key steps, such as before the report is finalized or shared.

The real question is not whether the product is called ChatGPT, Claude, or Kimi. The question is: in this interaction, is the system merely telling you what to do, or can it call tools, observe intermediate results, and decide the next step based on what it finds?

### 1.2 An Agent Is Not Just a Smarter Chatbot

This is the first key idea: **the difference between an Agent and a Chatbot is not simply "how smart it is." It is a difference in capability dimensions.**

A normal Chatbot mainly works in one dimension: **language space**. It receives text, processes text, and outputs text. It can understand you, respond to you, and give advice. Even when it has search or a knowledge base, it often just brings external information back into the conversation box.

An Agent works in two dimensions: **language space + action space**. It not only understands your intent, but also acts in tools and environments: searching, reading and writing files, calling APIs, running code, operating a browser, and so on. More importantly, the result of each action affects its next decision.

One concise definition:

> **An Agent is a system that can continuously make decisions and take actions around a goal, rather than merely answer questions.**

Every part of that sentence matters:

- **Around a goal**: an Agent is not just responding to prompts. It keeps moving toward a target and checks whether it is getting closer or drifting away.
- **Continuously make decisions**: it does not make one decision and stop. After each step, it uses new information to decide what should happen next.
- **Take actions**: it does not only suggest what you should do. It actually does things, such as calling tools, retrieving information, processing data, or changing external state when appropriate.

### 1.3 Agent vs Chatbot vs Workflow

Once you have the basic idea, you need to separate three concepts that are often mixed together: **Chatbot**, **Workflow**, and **Agent**.

#### Chatbot: Handles Conversation and Answers

A Chatbot's core capability is understanding and generating language. The user enters a message; the system returns a message. Even if it connects to search or a knowledge base, as long as the pattern is still "you say something, it answers," and it does not plan or decide what to do next, it is closer to a Chatbot.

**Core feature**: the next step is usually "wait for the user."

#### Workflow: Executes a Fixed Process

A Workflow is a predefined execution chain. What each step does, how data moves, and which condition triggers which branch are all decided during design. Some Workflow nodes may call an LLM, for example to generate copy or classify intent, but in that case the LLM is just a functional module. It is not the decision-maker. The process is.

**Core feature**: the next step is determined by preset rules.

A typical Workflow example is an intelligent customer support system:

1. Classify the user's intent into one of 5 predefined categories.
2. Retrieve the matching knowledge base article.
3. Use an LLM to polish the response.
4. If the issue is not resolved, escalate to a human agent.

The LLM participates in steps 1 and 3, but it does not control the process. When to escalate and which knowledge base to use are determined by preset rules.

#### Agent: Dynamically Decides the Next Step Based on Goal, State, and Feedback

The fundamental difference is this:

**For an Agent, the next step is not decided by the user or a preset rule. It is dynamically decided by the model based on the current goal, task state, and environmental feedback.**

**Core feature**: the next step is decided by the model.

A typical example is Claude Code. If you ask it:

```text
Find all bugs in this project and fix them.
```

It may decide which files to inspect first, which diagnostic command to run, whether a test failure is a real bug, how to verify a fix, and whether to retry or change strategy after verification fails.

In that chain, the model is making decisions at each step. It is not simply executing a fixed script.

#### The Core Differences

| Dimension | Chatbot | Workflow | Agent |
|---|---|---|---|
| Who decides the next step? | User | Preset rules | Model, dynamically |
| Can it call tools? | Usually no, or only limited search | Yes, but timing is rule-driven | Yes, and timing is model-driven |
| Task scope | Single-turn or multi-turn conversation | Tasks inside a fixed process | Open-ended goals |
| How it handles failure | It cannot act, so execution failure is not central | Preset exception branches | Adjusts strategy based on feedback |
| Typical products | Basic ChatGPT-style chat | Traditional customer service bots, RPA flows | Claude Code, Codex, Trae |

#### A Common Enterprise Pattern: Agentic Workflow

In real enterprise systems, many teams do not build a "fully autonomous Agent." They use a more controllable hybrid pattern: **Agentic Workflow**.

The core idea is:

> **The Workflow controls the main process boundary. The Agent handles local task decisions.**

This is not the same as simply calling an LLM once inside a process. In a normal Workflow, an LLM node usually performs a fixed action, such as classification, summarization, or rewriting. The input, output, and next step are still governed by process rules.

In an Agentic Workflow, some nodes contain a controlled mini-loop. Inside that loop, the model can choose tools, observe results, adjust strategy, and return a judgment to the main process.

This pattern is common in enterprise AI adoption. The reason is straightforward: enterprise systems need permissions, audit logs, compliance, stable delivery, and human confirmation. You usually cannot let a model freely control the entire business process. But in local tasks such as understanding information, screening materials, detecting anomalies, or recommending next steps, the model can be more adaptive than fixed rules.

For example, consider a content moderation system:

- The overall process is a Workflow: receive content -> automatic rule check -> model screening -> human review.
- But the "model screening" step can be a controlled Agent subtask: the model decides which review angles to use, whether to retrieve relevant policies, whether to request more context when evidence is insufficient, and finally outputs a risk level, evidence, and a recommended action.

The engineering wisdom here is not to treat certainty and flexibility as opposites. Use different decision mechanisms at different levels. Let the Workflow handle the main process, permissions, audit, and human confirmation. Let the Agent handle local understanding, tool selection, anomaly judgment, and strategy adjustment.

### 1.4 The Core Question: Who Decides the Next Step?

If you remember only one question for distinguishing Agents from other products, remember this:

> **Who decides the next step?**

- Chatbot: the user decides the next step. If the user does not type, the system waits.
- Workflow: the preset process decides the next step. Step A always leads to Step B unless a predefined branch applies.
- Agent: the model decides the next step based on the goal, state, and feedback.

This is why "does it use an LLM?" is not a good test. Many Workflows use LLMs, but the LLM only performs one task inside the process. It does not control the process.

**Judgment exercise:**

> A data analysis tool lets the user upload an Excel file. The system automatically generates charts and an insight report. When writing the report, it calls an LLM to generate the analysis text.

Is this an Agent? **No.** It uses an LLM, but when to call the LLM and what to do afterward are predefined by the process. The LLM is a writing module, not the decision-maker.

Now compare it with this version:

> The user enters, "Find unusual trends in this sales data and analyze possible causes." The system decides to split the data by time, check seasonal patterns, compare the same period last year, and search industry news to explain anomalies.

This is Agent behavior: **the model is deciding what to investigate next.**

### 1.5 A Practical Diagnostic Framework

Based on the question "who decides the next step?", you can evaluate any product that claims to be an Agent by asking three questions.

1. **Goal source**: Is the user providing an open-ended goal, or giving step-by-step instructions?
   - Open-ended goal, with the system planning the path -> stronger Agent signal.
   - Step-by-step user instructions -> closer to Chatbot or Workflow.

2. **Action initiation**: Are actions initiated by the model, the user, or preset rules?
   - Initiated by the model -> Agent signal.
   - Triggered by user instruction -> Chatbot signal.
   - Triggered by preset rules -> Workflow signal.

3. **Strategy adjustment**: When something unexpected happens, can the system change strategy by itself?
   - Switches tools, keywords, or paths -> strong Agent signal.
   - Uses only preset exception branches -> Workflow signal.
   - Fails or asks the user to start over -> Chatbot signal.

Together, these questions give you a practical spectrum for judging how "agentic" a product really is.

---

## Chapter 2: Build Task Intuition First

When you first encounter Agents, do not begin with "what technology does it use?" Ask a question that is closer to actual experience:

```text
Is this a task that should be given to a system that decides its own next step?
```

The same product can behave very differently across tasks. An Agent may be strong at coding but limited when booking flights because of permissions and payment risk. A search Agent may be excellent at research, but not suitable for editing your local files. The point of Lesson 1 is not to rank products. It is to train your judgment about whether a task and a product fit each other.

### 2.1 What Tasks Are Suitable for Agents?

Agent-suitable tasks usually share these traits:

| Task trait | Meaning | Example |
|---|---|---|
| Clear goal, flexible path | You know the outcome you want, but not the exact steps | "Find out why this project's tests are failing." |
| Multi-step progress | The task requires decomposition, execution, checking, and adjustment | "Prepare a competitive analysis brief." |
| External capabilities required | The system needs to search the web, read files, run code, query data, or call tools | "Read these PDFs, extract the key points, and produce a table." |
| Unexpected events may occur | Search fails, file formats are wrong, tests fail, or sources conflict | "Fix the code based on this error and verify that tests pass." |
| Results can be checked | You can judge whether the output is useful, complete, and reliable | "Generate meeting notes and list action items." |

One-line rule:

> **If a task requires deciding what to do next based on what happens, it is worth trying with an Agent.**

### 2.2 What Tasks Are Not Suitable for Agents?

Not every task needs an Agent. Many tasks are better handled by a normal Chatbot, a fixed Workflow, or even manual work.

| Less suitable task | Why it is less suitable | Better option |
|---|---|---|
| Single question-answer task | No multi-step decision or tool execution is needed | Chatbot |
| Very fixed rules | Every step is clear, branches are limited, and stability matters most | Workflow or automation script |
| High-risk, irreversible action | A mistake is costly, such as transferring money, deleting production data, or sending mass email | Human confirmation + strict process |
| Fully subjective judgment | There is no verifiable result, so the output may only "sound good" | Human judgment, with Agent as assistant |
| Unclear task boundary | The user has not clarified the goal, so the Agent may drift | Clarify the goal before using an Agent |

This does not mean Agents cannot participate in these tasks. It means they should not have too much autonomy. For high-risk tasks, an Agent can gather information, draft options, or prepare a plan, but the final action should stay with a human.

### 2.3 Match the Task to the Product's Capabilities

When evaluating an Agent product, do not only ask whether it is smart. Ask whether the task falls inside its capability boundary.

The same task can produce very different experiences depending on the product type:

| Task type | Better product form | What happens when they do not match |
|---|---|---|
| Research, synthesis, briefing | Research or search Agent | A coding Agent may manage it, but the search experience may be weak |
| Code changes, test runs, error diagnosis | Coding Agent | A general assistant may only suggest fixes, without reading files or verifying results |
| Fixed business process | Agentic Workflow or builder platform | A pure chat Agent may be flexible but lack stable process, permissions, and audit |
| Long document analysis and structured extraction | General assistant or document analysis Agent | A search product may find public information well, but struggle with private files |
| Preparation before high-risk operations | General assistant, research Agent, or Workflow platform | An Agent should not directly execute irreversible actions |

When trying an Agent, observe two things at the same time:

- **Is the task suitable for an Agent?** Does it require multi-step judgment, tool use, and feedback-based adjustment?
- **Is this product suitable for the task?** Does it have the tools, permissions, context, and confirmation mechanisms needed to finish the task?

If the task and product do not match, do not rush to say "this Agent is bad." First ask whether the Agent is weak, or whether you gave the task to the wrong product form.

---

## Chapter 3: Try Mainstream Agent Products

Now comes the most important learning activity in this lesson: **use the products yourself.**

You do not need to install every product. Choose 3 products, spend at least 30 minutes with each, and use them with a clear purpose. **Reading documentation or watching demos does not count as firsthand experience.**

### 3.1 Product Categories and What to Observe

Do not evaluate products only by whether they are domestic or international. A better approach is to classify Agent products by type, then compare products in the same category by capability boundary, process transparency, and user control.

The table below is not a complete ranking. It is a representative list for beginner exploration. Product capabilities change quickly. This list reflects the product landscape around June 2026; when you do the exercise, rely on the current versions you can access.

| Agent product category | International examples | China-market examples | What to observe |
|---|---|---|---|
| General assistant Agent | ChatGPT, Claude | Kimi, Tongyi Qianwen, Doubao | When does it merely answer, and when does it search, analyze files, call tools, or switch modes? |
| Research / search Agent | ChatGPT Deep Research, Perplexity | Kimi, Tencent Yuanbao, Tongyi Qianwen | How does it break down research questions, choose search keywords, filter sources, and produce evidence-backed conclusions? |
| Coding Agent | Claude Code, Codex | Trae, Tongyi Lingma | Can it understand a codebase, edit across files, run commands, verify results, and ask before high-risk actions? |
| Agentic Workflow / builder platform | Zapier Agents, Lindy | Coze, Dify | How does it combine fixed processes, plugins, knowledge bases, and local Agent decisions? |

Do not only record "what features it supports." Record these observations:

- **Task entry**: Did you provide an open-ended goal, a specific instruction, or a normal question?
- **Tool calling**: Did you select tools manually, or did the model decide which tools to call?
- **Process visibility**: Could you see plans, searches, file reads, code execution, or intermediate results?
- **User control**: Which actions required your confirmation, and which actions did it execute directly?
- **Failure recovery**: When search failed, code broke, or sources conflicted, did it retry, change path, or simply fail?

### 3.2 Experience Method: Use Each Product with Questions in Mind

Many people try a new product by clicking around and relying on a vague feeling. Do not do that here.

When you use each Agent, keep asking these four questions:

1. **When does it make decisions by itself?**
   - Which actions did it perform without asking you?
   - Did those autonomous actions feel reasonable?
   - Which actions should it have done by itself, but instead asked you?

2. **When does it ask me?**
   - Before what kinds of actions does it stop for confirmation?
   - Are those stopping points reasonable?
   - Are they too frequent and annoying, or too loose and risky?

3. **When does it make mistakes?**
   - Record one specific mistake.
   - How did the mistake happen?
   - Did the system notice it? If not, how did you notice?
   - What did it do after the mistake?

4. **When does it surprise me?**
   - Record one moment when you thought, "I did not expect it could do that."
   - Why did that moment stand out?
   - Was the surprise a one-time accident or something reproducible?

These four questions correspond to four core dimensions of Agent design: **autonomy, controllability, fault tolerance, and capability boundary**. You do not need to memorize those terms yet. Just use the products with these questions in mind. In Chapter 4, we will turn your experience into a structured analysis.

### 3.3 Advanced Exercise: Test Different Products with the Same Task

One of the most useful ways to learn is to give **the exact same task** to different Agents. This reveals how differently products "think" when facing the same goal.

Choose a suitable test task, for example:

```text
Research the most important changes in AI coding tools over the last three months and organize them into a brief.
```

A good test task has four traits:

- **Requires multi-step reasoning**: it cannot be solved with one answer.
- **Requires tool use**: it needs external information or external system operations.
- **Has some openness**: there is no single correct path, and multiple strategies are possible.
- **Is verifiable**: you have a way to judge whether the result is good.

Give the same task to 2 or 3 products, then compare their strategies:

- What did each product search first? Were the search keywords good?
- Which product spent more time planning?
- Whose result was broader? Whose was more precise?
- Which product was more efficient, using fewer steps to reach a similar result?
- Which product handled dead links or insufficient information more flexibly?

Record the comparison. That record itself is already high-quality product analysis material.

---

## Chapter 4: Product Breakdown and Analysis

After trying the products, you need a framework to organize your impressions. The purpose of this chapter is to help you move from "it feels useful" or "it feels bad" to "I can explain why it is useful or bad."

### 4.1 A 7-Dimension Product Observation Template

Use the following 7-dimension framework to analyze Agent products. The rightmost column shows an example using Claude Code so you can see the expected level of detail.

| Dimension | Observation question | How to record it | Example: Claude Code |
|---|---|---|---|
| **Task entry** | Did the user provide an open-ended goal, a specific instruction, or a normal question? | Write the original user task | "Add error handling to the utility functions under src/utils." This is a specific instruction with some openness. |
| **Next-step decision authority** | Who decided the next step? | User / fixed process / model | Mostly model-led. It listed directories, read files one by one, and proposed an update plan. It asked for confirmation only for higher-risk actions such as Git operations. |
| **Action capability** | What tools or external capabilities can the product use? | List tools, data sources, or workflow nodes | File read/write, shell commands, code search, Git operations, web search |
| **Process visibility** | What steps can the user see? | Plan, tool calls, progress, intermediate results | High. The user can see plans, status updates, and tool call records. Tool names and parameters are visible, and execution results are shown. |
| **User control** | Can the user confirm, interrupt, modify, or take over? | Mark intervention points | Tool calls can be allowed, denied, or always allowed. The user can intervene in natural language. High-risk actions require confirmation by default. |
| **Failure and recovery** | What happens after an error? | Retry, fallback, clarification, or fail-and-exit | When a test file is missing, it searches the directory, checks configuration, tries another framework path, and asks the user for clarification after repeated failure. |
| **Agentic quality judgment** | Is it closer to Chatbot, Workflow, or Agent? | Give a judgment and explain why | Strong Agent. It chooses tools and execution order autonomously, adjusts based on unexpected feedback, and uses high-risk confirmation as a safety design rather than a capability limit. |

All seven dimensions revolve around one core question:

> **How much decision-making responsibility does the model actually carry while completing the task?**

When making your judgment, use three levels:

1. **What drives most of the product's behavior?** User input, preset rules, or dynamic model decisions?
2. **In which concrete scenarios does it show Agent behavior?** Search planning, tool selection, code verification, or feedback-based retry?
3. **Where does it reveal Chatbot or Workflow limits?** Does it only choose from preset options? Does it apologize and stop when something fails?

One bottom line:

> Do not call a product an Agent just because it uses an LLM. The test is always: **who has the authority to decide the next step?**

---

## Exercises

### Exercise 1: Product Experience and Breakdown (Core)

1. Choose **at least 3** Agent products from the product list in Chapter 3.
2. Use each product for at least 30 minutes.
3. For each product, write a complete breakdown report using the 7-dimension template in Chapter 4.

### Exercise 2: Find Agents in Everyday Tools (Supplementary)

Pay attention to the tools you already use every day. Which ones have begun to show Agent-like behavior? Do they decide "what to do next" in certain moments?

Record 1 or 2 examples and describe:

- In what scenario did the tool show Agent-like behavior?
- Why do you think that was Agent behavior rather than a preset rule?
- Did its autonomous decision-making feel comfortable or unsettling?

### Exercise 3: Same-Task Comparison Test (Optional)

Choose a test task that satisfies these conditions:

- It requires multi-step reasoning.
- It requires tool use.
- It has some openness.
- Its result can be evaluated.

Use the same task to test 2 or 3 products. Write a comparison analysis of at least 500 words, focusing on this question: when different products face the same task, how do their "ways of thinking" differ?

### Deliverables

1. **Three product breakdown reports**: each report must cover all 7 observation dimensions, contain at least 300 words, and include concrete interaction details.
2. **One reflection essay: "My First Experience with Agents"** of at least 500 words:
   - Which moment made you feel, "This is different"? Describe the concrete scenario.
   - Which moment disappointed you? Describe the concrete scenario.
   - If you had to summarize your first impression of Agents in one sentence, what would you say?
3. Optional: one same-task comparison analysis.

---

## Lesson Recap

The key to understanding Agents is not whether a product "uses an LLM." The key is whether it can continuously decide the next step around a goal and revise its actions through tool or environment feedback. When distinguishing Agent, Chatbot, and Workflow, the most useful question is: **who decides the next step?** Normal question-answering is mainly driven by the user. Workflow is mainly driven by preset rules. Agent behavior is driven by the model's dynamic decisions based on goal, state, and feedback. Tasks suited for Agents usually have flexible paths, require multiple execution steps, rely on external tools, and produce results that can be checked. High-risk or irreversible actions must keep human confirmation in the loop.

---

## Acceptance Criteria

After completing this lesson, use the following checklist to evaluate yourself:

- [ ] I can explain the key difference between an Agent and a Chatbot in one sentence without looking at notes.
- [ ] I can name three key differences between an Agent and a Workflow.
- [ ] I understand why "who decides the next step" is the core observation question for Agents.
- [ ] My breakdown reports cover all 7 dimensions, and each dimension contains concrete observations instead of vague impressions.
- [ ] My reflection essay includes specific product interaction details, such as "when I did XXX, the Agent did YYY," rather than abstract comments like "it is smart."
- [ ] I can explain in my own words why "using an LLM" does not automatically mean "being an Agent."
- [ ] I can give at least one example of when an Agent's autonomous decision-making might make users feel out of control.

---

## References

### Recommended Reading

- **[Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)** - An Anthropic engineering post on Agent design principles. Its focus on when to use Agents and when not to use them complements this lesson's judgment framework.
- **[OpenAI Agents SDK documentation](https://platform.openai.com/docs/guides/agents)** - OpenAI's official documentation for how it defines Agents, tools, and handoffs.
- **[What is an AI Agent?](https://blog.google/technology/ai/ai-agents/)** - Google's explanation of AI Agents, useful as a complementary perspective to Anthropic's.
- **[The Agentic AI Landscape](https://a16z.com/ai-agent-landscape/)** - a16z's analysis of the Agent market, useful for understanding the industry view.
