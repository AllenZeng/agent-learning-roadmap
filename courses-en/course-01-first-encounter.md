# Lesson I: Introduction

## Introduction to the curriculum

If you're reading this, you're probably already using ChatGPT, Claude or something. You ask it questions, and it answers you — sometimes amazing, sometimes nonsense. You might feel like, "This thing is smart, but can it really do something for me?" **This is the subject of this course.** This course is not theoretical, practical or structured. It has only one goal: **to show you Agent, to build intuition.** What's "see"? Open Claude Code to help you rebuild a file; open Cursor to see how it understands your code library; open Kimi to do an industry study. You don't need to understand how it works inside -- like you don't need to understand engine principles to feel the acceleration of a car.

What's "intuitive"? When you're done, you can naturally judge:

- Is this product really making decisions, or is it just following a regular process?
- Which steps does it make you think you're smart? Which steps does it make you think you're stupid?
- Who's going to decide — users, fixed processes, models?
- What would you change if you were to design it?

These instincts, they're all the fuel behind the study. For beginners, it is easy to change principles without experience to empty terms; to learn them with intuition, you can think of a specific picture in every sentence. **This course is a sensory and cognitive level, with no details of achievement.** It provides a sample of product observations for the model understanding for course II and the minimum closed circle for course III.

Ready? Let's get in touch for the first time.

---

## Learning objectives

After this lesson, you will be able to:

1. **Says what Agent is** — Distinguishing between it and the nature of Chatbot, WorldFlow, instead of being fascinated by the image of using LLM Muse.
2. **judge by "who decides the next step"** — whether the product is a model or a preset rule is driving
3. **Dismantling any Agent product from a 7-dimensional template** -- from sensory experience to structured analysis, no longer in "good use / bad use"
4. **Explains why the user trusts or does not trust Agent** -- understand the reasons behind the design of surprise, loss of control, reliability

---

## Contents

- [Introduction to the curriculum](#introduction-to-the-curriculum)
- [Learning objectives](#learning-objectives)
- [Chapter 1: What is Agent?](#chapter-1-what-is-agent)
  - [1.1 First look at a scene.](#11-first-look-at-a-scene)
  - [1.2 Agent isn't the smartest chat robot.](#12-agent-isnt-the-smartest-chat-robot)
  - [1.3 Agent vs Chatbot vs Workflow](#13-agent-vs-chatbot-vs-workflow)
  - [1.4 Core Observatory: Who decides on the next step?](#14-core-observatory-who-decides-on-the-next-step)
  - [1.5 An operational diagnostic framework](#15-an-operational-diagnostic-framework)
- [Chapter 2: Creating mission instincts](#chapter-ii-establishment-of-mission-intuition)
  - [2.1 What's appropriate for Agent?](#21-whats-appropriate-for-agent)
  - [2.2 What's not appropriate for Agent?](#22-whats-not-appropriate-for-agent)
  - [2.3 Match mission and product capabilities](#23-match-mission-and-product-capabilities)
- [Chapter 3: Experience Mainstream Products](#chapter-3-experience-mainstream-products)
  - [3.1 List of products and elements of experience](#31-list-of-products-and-elements-of-experience)
  - [3.2 Empirical methodology: with problems](#32-empirical-methodology-with-problems)
  - [3.3 Progress: Testing different products with the same mission](#33-progress-testing-different-products-with-the-same-mission)
- [Chapter 4: Product dismantling and analysis](#chapter-4-product-dismantling-and-analysis)
  - [4.1 Product Experience Observation Framework and Dismantling Templates](#41-product-experience-observation-framework-and-dismantling-templates)
- [After-school exercises](#after-school-exercises)
- [Acceptance and inspection standards](#acceptance-and-inspection-standards)
- [References](#references)

---

## Chapter 1: What is Agent?

### 1.1 First look at a scene.

You entered in a regular question and answer mode: "Call me a flight from Beijing to Shanghai."

It can usually only tell you: "You can check flights with the airline network or other platforms, taking care of the timing, the price and the de-signing rules."

You have an Agent mode with browser operations, searches and forms.

Agent can try to open his own browser, search for flight information, compare prices and times of different airlines, and fill out order pages after finding a suitable flight, provided that access, site compatibility and login status allow. When it comes to high-risk steps such as payment, billing, it should stop and ask you: "A flight at 3 p.m. with a fare of 850 dollars, do you want to continue?"

The difference between these two reactions is not a difference between product names, but rather a difference in the pattern of interaction: the former answer primarily to questions, while the latter call tools around targets, observe results and continue to decide on the next step.

And one more day-to-day scene -- assuming you're writing a competition analysis. Note that not just the name of the product here, because the same product may have both a regular question-and-answer mode and an Agent capability such as search, file, code execution: **The usual question-and-answer format**: you ask it, it gives you competitive names, analytical frameworks, writing suggestions. You need to open your browser to search, read articles, extract information, organize and document. **Agent Capability Practice**: You told it "Do me a competition analysis in the XX field" and it searchs its own official networks and news stories, extracts key information, compares product differences, and produces a structured report with information sources. You just have to confirm the key nodes (e.g. before the final release).

It's not called ChatGPT, Claude or Kimi, it's just telling you what to do in this interaction, it's able to call tools, observe results and continue to decide on the next step based on intermediate information.

### 1.2 Agent isn't the smartest chat robot.

This is the first key understanding of Agent: **Agent and Chatbot are not the difference between intelligence, but the difference between capacity dimensions.** Normal Chatbot works mainly on one dimension: **language space**. It receives text, processes text, output text. It understands you, responds to you, advises you. Even if you have access to a search or a knowledge base, it's often only to bring back external information to answer you in the dialogue box.

Agent works on two dimensions: **language space + action space**. It doesn't just understand your intentions, it can generate action in tools and environments - search, read and write files, call API, execute codes, operate browsers, etc. More critically, the outcome of the operation will in turn influence its next decision-making.

In summary:

> **Agent is a system that can sustain decision-making and implementation around objectives, not simply answer questions.** Every word in this sentence matters:

- **Around the goal**: Agent is not "a question-and-answer" but is always moving towards a goal. It will determine how far away it is from the target and whether it has gone astray.
- **Ongoing decision-making**: Not once, but after every step, re-judge "what happens next" based on new information.
- **Enforcement**: Not just "recommended you do" but really do it — call tools to access external information, process data, or change the state of the outside world when needed.

### 1.3 Agent vs Chatbot vs Workflow

After understanding what Agent is, you need to distinguish between three often confused concepts: **Chatbot**, **Workflow**, **Agent**.

#### Chatbot: Responsible for dialogue and answers

Chatbot's core competence is to understand and generate language. The user enters a statement, and it returns a statement. Even with access to the search engine or the knowledge base, as long as it's still "What you say, I answer," without making plans and without deciding "three things to do next," it's closer to Chatbot. **Core feature**: the next step is usually "waiting user input".

#### Workflow: execution by fixed process

Workflow is a predefined enforcement chain. What each step does, how the data is transmitted and what triggers what branch is determined at the design stage. Although some of the points in Workflow may call LLM (e.g. creating a file, categorizing intent), LLM here is only a "functional module", not a "decision maker." Decision-making is the process that was designed. **Core feature**: the next step will be determined by "pre-established rules".

Typical example of a workflow: smart customer service system

1. Recognize user intent (5 predefined types)
2. Call the corresponding knowledge base according to intent
3. LLM Colour Generation Answers
4. If it doesn't work out, turn around.

Throughout the process, LLM is involved in steps 1 and 3, but it has no decision-making power - when to transfer people and which knowledge base is determined by default rules.

#### Agent: Decide on the next step based on the development of objectives, status and feedback

The fundamental difference between Agent and the preceding is that: **The next step is not for the user to decide, not for the default rules, but for the model to determine according to current objectives, mission status and environmental feedback dynamics.**

**Core feature**: the next step is "model dynamics".

Typical Agent example: Claude Code. "Help me find all the bugs of this project and fix it."

- It decides which files to read first.
- When you read the code, you decide what diagnostic order to run.
- When you see the diagnosis, you decide if it's a phenomenon.
- After repair, decide how to verify
- After verification failed, it's decided whether to try again or change strategy.

Each step in the chain is the model itself, not the preset process.

#### Three core differences

| Relative dimensions | Chatbot | Workflow | Agent |
|---------|---------|----------|-------|
| Who will decide the next step? | User | Pre-set rules | Model dynamics decisions |
| Could Call Tool | Usually not, or only search-enhanced | Yes, but the call is a rule. | Yes, the call time is determined by the model. |
| Scope of mandate | Single or multiple rounds of dialogue | Tasks in Fixed Processes | Open Targets |
| Wrong way. | I can't do it. I don't care if it's an error. | The anomaly is handled by preset rules. | Adjust the strategy to reflect feedback dynamics |
| Typical products | ChatGPT base Version | Traditional smart customer service, RPA process | Claude Code、Codex、Trae |

#### Common landing pattern of enterprises: Agency Workflow

In reality, many enterprise systems do not go directly into "full autonomy", but rather use a more manageable hybrid — **Agenda Workflow**.

The core idea of Agenic WorkFlow is: **WorkFlow is responsible for the main process boundary and Agent is responsible for local mission decision-making.** It's not simply "call once at a point." The LLM node in the normal WorkFlow usually completes only one fixed action, such as classification, summary, rewrite; input, output and subsequent flow is still determined by process rules. The key difference is that some nodes have a controlled small closed ring inside, and models can select tools around local targets, observe results, adjust strategies and return judgement to the main process.

This is the common course of practice in the current corporate AI transition. The reason for this is simple: the business landscape usually requires authority, audit, compliance, steady delivery and manual validation, and cannot leave the entire business chain freely to the model; but the model can also provide a more adaptive than the fixed rules in local areas such as information understanding, material screening, abnormal judgement, and recommendations for the next step.

For example, a content audit system:

- The overall process is Workflow: Receive content → Automatic rule check → Initial model screening → manual review
- But the "model first screening" step is not a simple classification, but a controlled Agent subtask: the model itself determines the angle from which to review, whether policies need to be retrieved, whether to request more context in case of insufficient evidence, final output risk rating, evidence and recommended treatment.

The engineering wisdom of such a design is that there is no need to put "certainty" and "flexibility" dichotomy, but to use different decision-making mechanisms at different levels. Main processes, competencies, audits and manual confirmations are given to Workflow; local understanding, tool selection, abnormal judgement and tactical adjustments are given to Agent.

### 1.4 Core Observatory: Who decides on the next step?

If you can only remember one concept to distinguish between Agent and other products, remember this:

> **Look who decided the next step.** - Chatbot: User decides the next step (user does not enter, system waits)

- Workflow: Preset process determines the next step (step A is bound to step B)
- Agent: The model determines the next step according to the dynamics of objectives, status and feedback

That's why whether LLM is used is not a good criterion -- a lot of Workflow is also used, but LLM is only responsible for the implementation of a link (e.g. classification, generation) and not for determining the course. **Judgement exercise**: Thinking about the following scenes -

> A data analysis tool, user uploads Excel, system automatically generates charts and insight reports. When generating the report, the system calls LLM to write the analytical text.

Is this Agent? Although LLM has been called, "when and what to do with it" is a predefined process. LLM is just a "file generator", not a "decision maker".

> The same tool, but the user can enter, "Help me find an unusual trend in this sales data and analyze possible causes." The system decides on its own: to split data on a time-dimensional basis, to check seasonal fluctuations, to compare the same period last year and to explain anomalies in the search industry news.

That's Agent's behavior: **The model is deciding what to look for next.**

### 1.5 An operational diagnostic framework

Based on the core perspective of who decides the next step, here is a quick-judgement framework. When you meet any product that claims to be Agent, you ask three questions:

1. **Target source**: Does the user enter an open target (Agent self-dismantling) or a step-by-step directive (user-led every step)?
   - User input open target, Agent autonomously plan execution path stronger Agent features
   - User step by step to give specific instructions more than Chatbot or WorkFlow
2. **Initiation of action**: whether the action was initiated by the model itself or triggered by a user directive or preset rule?
   - Autostart model → Agent feature
   - User command trigger → Chatbot feature
   - Preset rules trigger → Workflow feature
3. **Strategy adjustment**: Can the system change its strategy independently in the event of an accident?
   - Free to change tools, keywords, paths
   - Only preset abnormal branch can be used to process → Workflow feature
   - Directly failed or requested to re-enter Chatbot feature

These three problems are stacked together, and it's a product of the Agent Colour Spectra.

---

## Chapter II: Establishment of mission intuition

Don't ask first, "What technology does it use?" Let's start with the question of a closer experience:

```text
It's not an appropriate task to give to a system that will decide on its own next move.?
```

The same product may present a completely different picture in different missions. An Agent is very strong in writing codes, and may be subject to privileges and payment restrictions when ordering tickets; a search type Agent is well suited for sorting, but not necessarily for modifying your local files. So course one is not about ranking the product, but training you to judge whether the mission and product competencies match.

### 2.1 What's appropriate for Agent?

These features usually apply to jobs suitable for Agent:

| Task characteristics | Annotations | Examples |
|---|---|---|
| Target is clear, but the path is not fixed. | You know what you want, but you don't know what to do in the middle. | Help me find out why this project failed. |
| We need more pace. | It's not the end of an answer. It's decomposition, execution, inspection, adjustment. | Help me organize a competition analysis brief. |
| Need to use external capacity | Need to search_web pages, read_files, run codes, query data or call tools | "Read these PDFs, extract core views and generate forms." |
| There could be an accident. | Unable to search, incorrect file format, error test, information conflict, need to change strategy | "Recover the code based on error reporting and verify whether the test passed." |
| The results can be checked. | You can judge whether the output is useful, complete, reliable. | "to generate minutes and list to-dos." |

One sentence: **If the mission needs to "determine the next step", it deserves to experience it.**

### 2.2 What's not appropriate for Agent?

Not all missions need Agent. Many missions are more appropriate with ordinary Chatbot, fixed workwork, or even manual operations.

| Not a suitable assignment. | Why not? | A more appropriate way. |
|---|---|---|
| Single questions and answers | There is no need for multi-step decision-making and no need for tools to implement | Chatbot |
| The rules are very fixed. | Every step is clear, there are few branches, and the search for stability is consistent. | Workflow/ Automation Script |
| High-risk and irreversible. | Mistakes are costly, such as transfers, removal of production data, mass e-mail | Manual confirmation + strict process |
| The test of judgment is entirely subjective. | There's no way to verify the results. It's easy to turn into "sounds good." | Human judgment, Agent. |
| Mission boundaries are unclear. | Users don't know what they're after either, Agent. | Clarify the target and then give it to Agent. |

This is not to say that Agent cannot be involved in these tasks, but that it should not have too much autonomy. High-risk missions allow Agent to collate information, propose programmes, generate drafts, but the key actions are to be confirmed.

### 2.3 Match mission and product capabilities

It's not just about whether it's smart or not, it's about whether the task falls within its capacity.

The same mission, assigned to different types of Agent, will have a completely different experience:

| Task Type | More suitable product forms | What happens when it doesn't match? |
|---|---|---|
| Information checks, syntheses and briefings | Research / Search TypeAgent | Programming Agent may be able to do it, but the search experience may not be. Okay. |
| Change code, run tests, check errors | Programming | The General Assistant may only be able to advise, not read and write directly to the project and verify the results |
| Processing of fixed business processes | Agency Workflow / Build Platform | Agent may be flexible but lacks stable processes, authority and audit |
| Analyse long documents, extract structured information | General Assistant or Document Analysis | Search-type products may be better at finding information than at handling your private files. |
| Programme preparation for high-risk operations | General assistant, researcher Agent, workflow platform | Agent should not be allowed to directly execute irreversible actions |

So, you have to look at two things at the same time as Agent:

- **Does the task itself fit Agent**: Does it require multistep judgement, tool use and feedback adjustments?
- **Is this product appropriate for this task**: Does it have the tools, competencies, context and validation mechanisms to fulfil its mandate?

If the mission doesn't match the product, don't rush to the conclusion that this Agent can't. You have to judge whether Agent's incompetent or you've given the task to inappropriate product patterns.

---

## Chapter 3: Experience Mainstream Products

This is followed by the core learning activities of the course: **in person.** You don't need to install all the products. Select three paragraphs, each of which takes at least 30 minutes to experience with purpose. **Documents and presentation videos are not an experience.**

### 3.1 List of products and elements of experience

Don't look at products in isolation by "domestic/foreign". A better way to do this would be to classify them by Agent product type before comparing the differences in capacity boundaries, process transparency and user control of the same product category.

The following is not a complete list, but a list of delegates suitable for an introductory experience. Product capacity is changing rapidly, and this list is based on the June 2026 product pattern and is based on the current version of the experience.

| Agent Product Classification | Foreign representation products | Domestic representative product | For what? |
|---|---|---|---|
| General Assistant | ChatGPT、Claude | Kimi, Tunyuji / Bean bag | When does it just answer questions? When does it search, analyze, call tools or switch modes? |
| Research / Search TypeAgent | ChatGPT Deep Research、Perplexity | Kimi, Tun Tsing Yuanbao / Tsang Yi | How it dismantles research issues, selects search keywords, screens sources, generates evidence-based conclusions |
| Programming | Claude Code、Codex | Trae, Viola. | Does it understand the code library, cross-file modifications, running commands, validation results and request confirmation prior to high-risk operations |
| Agency Workflow / Build Platform | Zapier Agents、Lindy | Buttons, Coze, Diffy. | How it combines fixed processes, plugins, knowledge banks and local Agent decision-making |

The experience is not just about "what it supports," but about:

- **Mission entrance**: did you enter an open target, a specific directive, or an ordinary question and answer?
- **Tool call**: Did you choose the tool manually or did the model use it?
- **Process Visibility**: Can you see plans, searches, file reading, code execution or intermediate results?
- **User control**: What actions do you need to confirm that they will be executed directly?
- **Failed to recover**: Unable to search, wrong code, conflicting information, will it try again, change paths, or simply fail?

### 3.2 Empirical methodology: with problems

A lot of people experience the new product as "just a little bit, just a sense." We don't do that.

In the experience of each of the Agents, please always carry these four questions:

1. **When will it make its own decision?** -- Which operations it carried out without asking your opinion?
   - Do you think these claims are reasonable?
   - What kind of operation do you think it should be done on its own?
2. **When will it ask me?** -- What kind of operation would it stop for confirmation?
   - Does this stop point make sense? Is it too frequent (obstinate) or too loose (dangerous)?
3. **When did it go wrong?** -- Record a specific error. How did it go wrong?
   - Did it find out? If not, how did you find out?
   - What did it do after the mistake?
4. **When does it surprise me?** -- Record a moment that makes you think "Wow, it can do this."
   - Why does this moment impress you?
   - Is the surprise "one-off" or "renewable"?

These four questions correspond to the four core dimensions designed by Agent: **autonomy, controlability, tolerance, capability boundaries.** You don't need to remember these terms now — just use them with problems. In chapter IV, we will systematize these experiences.

### 3.3 Progress: Testing different products with the same mission

One of the most enlightening ways to learn is to test different Agent with the same mission. It shows you how different the "thinking" of different products is in the face of the same goal. Choose a suitable test assignment like "Help me study the important changes in the field of the AI programming tool for the last three months and make a brief."

A good test mission meets four conditions:

- **Need for multi-step reasoning**: Not a single answer.
- **Tools needed**: external information needed or external systems operated
- **There is some openness**: there is no only correct answer, allowing for multiple strategies
- **Verifiable**: There is a way to judge the results for good or bad

The task is assigned to two to three products and then to observe their differences in strategy:

- Who's gonna search for what first?
- Who spends more time planning?
- Who has more comprehensive results? Who has more accurate results?
- Who is more efficient (with fewer steps to achieve comparable results)?
- Who is more flexible when faced with dead links or insufficient information?

The results of the comparison are recorded — it is in itself a high-quality product analysis material.

---

## Chapter 4: Product dismantling and analysis

After the product, you need a framework to systematize your feelings. That's what this chapter is about.

### 4.1 Product Experience Observation Framework and Dismantling Templates

Here's the 7-dimensional observation frame reference. On the right side is a complete demonstration of Claude Code to help you understand how each dimension is recorded.

| Dimensions | Observation issues | Recording mode | Claude Code |
|------|---------|---------|-------------------|
| **Mission entrance** | Did the user enter an open target, a specific command, or a regular question and answer? | Write Original User Job | "Help me add the tool function under src/utils to the error processing" -- specific instructions, with some openness |
| **The next decision-making authority** | Who decides the next step? | User / Fixed Process / Model | Models dominate. It was decided to list the directories first, to read the documents individually and to propose changes. Just ask for confirmation for high-risk actions. |
| **Activities** | What tools or external capabilities can products use? | List tools, data sources or workflow sections Points | File reading and writing, Shell command, code search, Git operation, Web search |
| **Process visibility** | What steps can users see? | Plans, tool calls, progress, intermediate results | High. Visible plan, milestones and tool call logs; tool caller pre-marked names and parameters; implementation results visible |
| **User control** | Can users identify, interrupt, modify or take over? | Mark Intervention Node | Any tool calling optional permission/rejection/always allowed; real-time intervention in natural languages; default confirmation for high-risk operations |
| **Failed and recovered** | What happens when something goes wrong? | Retry, downgrade, clarify, fail to exit | Active search directory, check configuration, change frame attempts when the test file does not exist and clarify to the user after successive failure |
| **Agent Color Decision** | It's more like Chatbot, Workflow, or Agent? | Give your judgment and give your reasons. | Strong Agen. Auto-decision tools and sequencing of implementation; dynamic adjustments in unexpected feedback; high-risk recognition as security design, non-capacity constraints |

The seven dimensions revolve around the same core issue: **How much "decision" responsibility does the model have in dealing with the task?** --- **Three levels of judgement**:

1. **What drives most behaviour in this product?** -- User input, preset rules, or model dynamic decision making?
2. **In what specific scenario did it show the Agent character?** — Is it "search planning" autonomy, or is it a feedback loop when "code generation automatically runs test validation"?
3. **Which scenes showed it to the bottom of Chatbot or WorkFlow?** — Is it a "selecting only from preset options" or is it a "failure without an apology" error? **A bottom line in judgement**: Don't call it Agent because a product "used LLM". The test is always **"Who's got the decision-making power next."** ---

## After-school exercises

### Practice I: Product experience and dismantling (core)

1. Select from the list of products in Chapter III **at least 3** Agent products for experience at least 30 minutes each
2. For each product, a complete dismantling report is prepared using the 7-dimensional dismantling template of chapter 4.

### Practice II: Daily Age Discovery (Auxiliary)

Keep an eye on which of the tools you use in your day-to-day life are already Agent features -- Do they decide at some point what to do next?

Record 1-2 discoveries, describing:

- In what scenario did it show the Agent character?
- Why do you think that's Agent's behavior instead of pre-set rules?
- Does its autonomous decision make you comfortable or uneasy?

### Practice III: Same job comparison test (chosen)

Select a test task that meets the following conditions:

- It's a multi-step theory.
- Need tool use
- There's a certain openness.
- Results can be validated

Using this task to test 2-3 products separately, write a comparative analysis (500 words or more) and focus on: What is the difference between "thinking" when different products face the same task?

### Delivery

1. **Three product dismantling reports**: 7 observation dimensions per copy, more than 300 words per copy, with specific interactive details
2. **A copy of "my first experience"** (500 words above):
   - Which moment did you think it was different? — describing specific scenarios
   - When did it disappoint you?
   - What would you say if you had your first impression of Agent in one sentence?
3. (selected) A mission-specific analysis

---

## Stenograph

The key to Agent is not "using LLM", but whether it can continue to decide on the next step around the goal and amend action through tools or environmental feedback. In judging Agent, Chatbot and Workflow, the most useful question is: **Who decides the next step?** General questions and answers are driven mainly by users, WorldFlow is driven mainly by pre-set rules, and Agent allows the model to advance dynamically according to objectives, status and feedback. Tasks suitable for Agent usually have irregular paths, require multiple steps of execution, rely on external tools, and the results can be checked; high-risk or irreversible actions must retain human recognition.

---

## Acceptance and inspection standards

Upon completion of this course, use the following criteria for self-examination:

- [ ] I can say the key difference between Agent and Chatbot without looking at it.
- [ ] I can tell you three key differences between Agent and WorldFlow.
- [ ] I understand why "who decides the next step" is the core observation point for Agent.
- [ ] My decomposition report covers all 7 dimensions, each with specific observations rather than general perceptions.
- [ ] I have specific product interaction details in my pen ("Agent did YYY in XXX Operations"), not abstract evaluation ("It's smart")
- [ ] I can explain in my own words why using LLM doesn't mean it's Agent.
- [ ] I can at least give one example of when Agent's autonomous decision-making can make users feel out of control.

---

## References

### Recommended reading

- **[Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)** -- Anthropic team blog post on Agent design principles. Focusing on "When to use Agent, when not" is highly complementary to the framework of this course.
- **[OpenAI Agents SDK Document](https://platform.openai.com/docs/guides/agents)** -- OpenAI official Ages SDK document shows how they define Agent, tools and hand-over mechanisms.
- **[What is an AI Agent?](https://blog.google/technology/ai/ai-agents/)** The interpretation of AI Agent by Google official blog complements the Anthropic perspective.
- **[The Agentic AI Landscape](https://a16z.com/ai-agent-landscape/)** — a16z for analysis of Agent market patterns, suitable for an industry perspective.
