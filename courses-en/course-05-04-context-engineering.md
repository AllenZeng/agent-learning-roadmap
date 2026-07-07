# Chapter 4: Context Engineering -- Don't let Agent drown in his own context

[Return Course Five Document](./course-05-01-scenario-enhancement.md) | [Previous Chapter](./course-05-03-memory.md) | [Next chapter](./course-05-05-planning.md)

## Table of contents of this chapter

- [4.1 The more the power, the more the power, the more Agent is not missing, but the context is out of control](#41-the-more-the-power-the-more-the-power-the-more-agent-is-not-missing-but-the-context-is-out-of-control)
- [4.2 Context Engineering core: deciding what to see in the current step](#42-context-engineering-core-deciding-what-to-see-in-the-current-step)
- [4.3 Agent, where does the context come from? — Eight categories of sources and panorama](#43-agent-where-does-the-context-come-from-eight-categories-of-sources-and-panorama)
- [4.4 Three introductory packages: first layering of information, limits, filtering](#44-three-introductory-packages-first-layering-of-information-limits-filtering)
  - [4.4.1 Layers: Why not mix RAG, Memory, tool results?](#441-layers-why-not-mix-rag-memory-tool-results)
  - [4.4.2 Budget: Long context is not a free warehouse](#442-budget-long-context-is-not-a-free-warehouse)
  - [4.4.3 Choice: Who should be left behind when the context is overstretched?](#443-choice-who-should-be-left-behind-when-the-context-is-overstretched)
- [4.5 Five types of means of production: writing, selection, compression, isolation, cache](#45-five-types-of-means-of-production-writing-selection-compression-isolation-cache)
  - [4.5.1 Writing context: not just reading, but taking notes](#451-writing-context-not-just-reading-but-taking-notes)
  - [4.5.2 Selection of context: Selected from mass information what the current steps need](#452-selection-of-context-selected-from-mass-information-what-the-current-steps-need)
  - [4.5.3 Compressed context: from chat stream to task status summary](#453-compressed-context-from-chat-stream-to-task-status-summary)
  - [4.5.4 Context of isolation: When should Agent see everything himself?](#454-context-of-isolation-when-should-agent-see-everything-himself)
  - [4.5.5 Cache and Company: Long sessions are not just handwritten summaries](#455-cache-and-company-long-sessions-are-not-just-handwritten-summaries)
- [4.6 Tool Output: Why does the tool result most easily deflect Agent?](#46-tool-output-why-does-the-tool-result-most-easily-deflect-agent)
  - [4.6.1 Why tool output is the easiest to explode](#461-why-tool-output-is-the-easiest-to-explode)
  - [4.6.2 Resulting in thinness](#462-resulting-in-thinness)
  - [4.6.3 Tool return is not just short, but actionable.](#463-tool-return-is-not-just-short-but-actionable)
  - [4.6.4 The tool itself also needs](#464-the-tool-itself-also-needs)
  - [4.6.5 Clean-up, not just compression: Move context after use](#465-clean-up-not-just-compression-move-context-after-use)
  - [4.6.6 Code skeletons: adjectable result processing Device](#466-code-skeletons-adjectable-result-processing-device)
  - [4.6.7 Contextal credibility: information is not an instruction](#467-contextal-credibility-information-is-not-an-instruction)
- [4.7 How does the context strategy really work?](#47-how-does-the-context-strategy-really-work)
- [4.8 Evolutionary route: from "all in" to "the context control system"](#48-evolutionary-route-from-all-in-to-the-context-control-system)
- [4.9 Common failure symptoms and treatment: from context to context attack](#49-common-failure-symptoms-and-treatment-from-context-to-context-attack)
- [4.10 When does context work not be required?](#410-when-does-context-work-not-be-required)
- [Summary of this chapter](#summary-of-this-chapter)
- [Runable Example](#runable-example)

---

## 4.1 The more the power, the more the power, the more Agent is not missing, but the context is out of control

You made a knowledge base, Agent.

First week, it's good. You put it on the Notion file (RAG), it can retrieve your notes and answer questions. You added it to memory, and it remembers your preference for simple answers and code examples for Python. You've given it a few tools -- reading files, searching code libraries, executing shell commands -- and it's able to check its own data and run scripts.

You're satisfied. It's getting "dry."

The second week, the problem began to arise. At first it was just a little problem. You thought it was an accident:

- You wrote "Always replying in Chinese" in System Prompt, but it occasionally appeared in English. You're like, "Photo-spill, just refresh."
- It found the correct document and in its reply quoted the old conclusions three days earlier. You think it's possible that memory recalled the expired.
- One time after reading a 2,000-line log file, the next five rounds of conversations revolve around a unrelated Warning, you ask about code structure, and it's analyzing the root causes of that Warning.

You're on alert.

In the third week, the problem became normal:

- The output format of System Prompt, the security rules, often "forget." You have to repeat the rules at the end of every message.
- It had the tools to check up on the latest files, but it started to speculate -- because the context was too long, and it was too lazy to adjust the tools.
- Each round of answers is slower and token is becoming more exhausting, but the quality of the answers is not improving. You look at the bill and you start to wonder, "Are these powers helping or hurting it?"

You looked over the track one time. In step 3, these things are inserted in the context:

- System hint (1200 tokens)
- User Target (50 tokens)
- 3 document clips retrieved by RAG (total 4200 tokens)
- Memory recalled 2 preferences (300 tokens)
- A tool call result for step 1 - a log file for row 1500 (8000 tokens)
- Step 2 tool call results — code library search results (2,500 tokens)
- Historical Message 1800 tokens

The total is about 18,000 tokens. When the model makes its decisions in such a long context, the probability that key information will be ignored increases markedly, especially when it is buried in the middle of a large number of tool results and historical news. The directive "Reaction in Chinese" is still in the context, but it does not necessarily gain sufficient weight in current decision-making. **It's not like the model suddenly gets stupid. Not the RAG problem. It's not about memory. It's not about tools.**

**You turned Agent's context into a dump.** Every time you introduce a new capability -- RAG, Memoory, Tool -- you add something to the context. But no one has stopped thinking: is it reasonable to organize these things? How many signals and noises in the context?

That's what Context Engineering is about to solve.

## 4.2 Context Engineering core: deciding what to see in the current step

Take a step back and figure out a fundamental question: **What can the model see?** The model has no eyes. No ears. It can't see your code warehouse, it can't see your database, it can't see your file system. The only thing it can "see" every time it reasons is the pile of text you put in when you call API -- the context.

```text
模型当前一步的"直接视野" = 你传进去的上下文

模型不知道上下文之外有任何东西。
模型不会"想起来"你上次说过什么（除非在上下文里）。
模型不会"主动去查"什么（除非它决定调用工具，而工具结果又回到上下文里）。
```

But there's a key distinction, and many beginners will ignore: **The current step of the model can only see the context directly, but the full view of the Agent system is much more than the context.** Agent can also expand its indirect vision by:

- Tools: Read files, search databases, search code libraries on demand - information is not in context but is readily available through tools
- External status: scratchpad file, runtime state, database cursor - task progress and intermediate results outside context
- Memoory store: Long-term memory is not in the context, but only when required Back
- File system: large files, logs, configuration files are not context-specific, only index maintained
- Agent: Take the big mission out, and Agent digs deep in his own context and returns to the enrichment. **Context Engineering's mission is not to "plug all horizons into models," but to decide "what to see at this stage."** More precisely:

> Context Engineering is not writing Prompt. It is an engineering system that dynamically manages "what information enters the model, which information remains external, which information is compressed, which information is sent to the subAgent for quarantine, which information can be cached and which information needs to be evaluated" before every step of Agent's decision.

Prompt Engineering is concerned with "How to write the instructions clearly"; RAG is concerned with "What to look at from the knowledge base"; Memoory is concerned with "What to write across the wheel"; **Context Engineering is concerned with "What to see in models before every decision is made."** The four relationships are:

```text
RAG 负责"查什么"   ──→ 信息生产者
Memory 负责"记什么" ──→ 信息生产者
工具负责"执行什么"  ──→ 信息生产者（工具结果也是上下文的一部分）

Context Engineering 负责"怎么组织这些生产者的产出" ──→ 信息组织者
```

Without the organizers, the more the producers, the more messy they are. It's not an issue of efficiency, it's a question of correctness — the model will really “not see” the key information in the context.

As the capacity to introduce courses 2 to 4 grows, so does the context:

```text
V0（最小闭环）：
  上下文 = System Prompt + 用户消息 + 历史消息 + 工具结果

V1（接入 RAG）：
  上下文 = System Prompt + RAG 片段 + 用户消息 + 历史消息 + 工具结果

V2（接入 Memory）：
  上下文 = System Prompt + Memory 召回 + RAG 片段 + 用户消息 + 历史消息 + 工具结果

V3（接入 Planning）：
  上下文 = System Prompt + 执行计划 + Memory 召回 + RAG 片段 + 用户消息 + 历史消息 + 工具结果

每一步都在往上下文里加东西。如果不加组织，V3 不是更强的 Agent，而是更混乱的 Agent。
```

So the core theme of Context Engineering is not "Whether or not to put something in the context," but: **At this stage, what information has to go in, what information has to go back, what information has to go back, what information has to be left outside on demand, what information should be cleaned up, what information should be put back on a cache in a stable prefix — and how these decisions are verified.**

## 4.3 Agent, where does the context come from? — Eight categories of sources and panorama

Before we talk about "how to manage," let's see what to manage. At each step of the line of reasoning, Agent has eight possible sources of context:

```text
用户目标
  ↓
┌─────────────────────────────────────────────────────┐
│                  Context Sources                    │
│                                                     │
│  ① System Instructions     角色、约束、安全规则        │
│  ② User Message            当前用户输入               │
│  ③ Conversation History    历史对话（原文或摘要）      │
│  ④ RAG Knowledge           检索到的外部知识片段        │
│  ⑤ Memory                  召回的用户偏好和长期记忆    │
│  ⑥ Tool Definitions        可用工具的 schema 和描述   │
│  ⑦ Tool Results            工具调用的返回结果          │
│  ⑧ Runtime State           当前计划、进度、scratchpad │
│                                                     │
└─────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────┐
│               Context Operations                    │
│                                                     │
│  Write     → 把计划、笔记、中间状态写入外部状态           │
│  Select    → 从知识、记忆、工具、历史中选相关内容         │
│  Compress  → 压缩历史、工具结果、长文档、推理轨迹         │
│  Isolate   → 用子 Agent / sandbox 隔离大上下文         │
│  Assemble  → 按分层和预算组装最终 prompt               │
│  Evaluate  → 评测不同策略对成功率、成本、延迟的影响       │
│                                                     │
└─────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────┐
│                   Model Call                        │
│                                                     │
│  模型基于组装好的上下文，决定下一步：                     │
│  → 回答问题                                          │
│  → 调用工具                                          │
│  → 写入外部状态                                       │
│  → 启动子 Agent                                      │
│                                                     │
└─────────────────────────────────────────────────────┘
```

The core message of this picture is: **Context Engineering is not "how token" but Agent's running information dispatch system.** You're not managing a static Prompt template, you're managing a dynamic flow of information... Each source is producing information on a continuous basis and you need a movement control layer to determine which enters the model, which stays outside and which needs to be compressed or cached.

The structure of this chapter follows this landscape:

- **.4 Three introductory packages**: starting with layering, budget, selection - a basic version of Context Engineering
- **4.5 Production level five means**: write, select, compress, isolate, cache - complete production level toolbox
- **4.6 Tool output**: single deep tool output, the most explosive source
- **4.7 Assessment**: How to verify that your context strategy is working

## 4.4 Three introductory packages: first layering of information, limits, filtering

For starters, Context Engineering can start with three things: **layering, budget, choice.** These three cover 80% of the prototype to the V1 scene.

But let me be clear: **These three are introductory versions, not complete methodology.** Production class Agent will also continue to introduce compression, external state, contextual isolation and evaluation (Sections 4.5-4.7).

### 4.4.1 Layers: Why not mix RAG, Memory, tool results?

Do not mix different types of information into models. To structure the context so that models can distinguish between "this is the rule," "this is the reference," "this is the state" and "this is history". **Bad practice:**

```text
把所有信息平铺在 messages 数组里：
message[0]: system prompt
message[1]: user message
message[2]: RAG 结果 1
message[3]: RAG 结果 2
message[4]: Memory 召回
message[5]: 工具输出 1
message[6]: 历史消息 1
……
模型看到的是一大坨文本，无法区分哪些是指令、哪些是参考、哪些是历史。
当上下文变长，"Lost in the Middle"效应会让中间的信息被严重忽略。
```

**Better practice:**
```text
┌─────────────────────────────────────────────────────────┐
│ Layer 0: 系统指令（System / Developer Instructions）      │  ← 最高优先级，永不裁剪
│ - 角色定义、行为约束、输出格式、安全规则                      │
├─────────────────────────────────────────────────────────┤
│ Layer 1: 用户目标 + 当前任务                               │  ← 高优先级
│ - 用户原始消息、确认后的计划、当前子任务                       │
├─────────────────────────────────────────────────────────┤
│ Layer 2: 当前计划 / Scratchpad 摘要                       │  ← 高优先级，动态更新
│ - 当前目标、已完成步骤、待办事项、已验证事实                   │
├─────────────────────────────────────────────────────────┤
│ Layer 3: 任务相关知识（RAG）                               │  ← 中优先级，按相关性过滤
│ - 检索到的文档片段、去重后的知识                             │
├─────────────────────────────────────────────────────────┤
│ Layer 4: 用户相关知识（Memory）                            │  ← 中优先级，按相关性和时效性过滤
│ - 用户偏好、历史决策、项目约定                               │
├─────────────────────────────────────────────────────────┤
│ Layer 5: 工具可用性（Tool Definitions）                    │  ← 中优先级，按当前任务筛选
│ - 当前步骤可能用到的工具 schema 和描述                       │
├─────────────────────────────────────────────────────────┤
│ Layer 6: 最近工具结果（Tool Results）                      │  ← 中优先级，动态变化
│ - 最近 N 步的工具调用与处理后的结果                          │
├─────────────────────────────────────────────────────────┤
│ Layer 7: 历史对话摘要                                     │  ← 低优先级，摘要化
│ - 更早的消息用摘要代替原文                                  │
├─────────────────────────────────────────────────────────┤
│ Layer 8: 外部状态索引（不进入上下文，但模型知道可以获取）       │  ← 不注入
│ - 完整文件路径、数据库行 ID、日志文件位置                     │
└─────────────────────────────────────────────────────────┘
```

Each layer is separated by clear markers to help the model's attention mechanism locate information:

```text
<system>
## 角色定义
你是个人知识助手……
## 行为约束
- 使用中文回复
- 不确定时明确说"不确定"
- 回答末尾标注信息来源
</system>

<user_goal>
帮我写一篇关于 Agent Context Engineering 的技术文章
</user_goal>

<current_plan>
## 当前进度
- 步骤 1/4：收集资料 ✅ 已完成
- 步骤 2/4：写大纲 ⏳ 等待用户确认
- 步骤 3/4：写正文 🔜
- 步骤 4/4：review 和修改 🔜

## 已验证事实
- 用户偏好技术文章先给大纲确认
- 目标读者是有 Agent 开发经验的工程师
- 字数要求 3000-5000 字
</current_plan>

<reference_knowledge>
## 相关笔记
[检索到的 3 篇笔记内容……]
</reference_knowledge>

<user_memory>
## 用户偏好
- 技术文章先给大纲确认
- 语气直接，不要营销化
- 代码示例使用 Python
</user_memory>

<tool_results>
## 文件搜索结果
文件搜索 "context window" 返回 12 个结果，其中 3 个与当前任务相关：
1. context_engineering_notes.md - 上下文分层策略 (2.3K tokens)
2. llm_attention_mechanism.md - 注意力机制与上下文位置 (1.8K tokens)
3. production_context_pipeline.py - 上下文管线代码 (0.9K tokens)

其余 9 个结果涉及测试和配置文件，已保存到索引，可通过 read_file 按需读取。
</tool_results>

<history_summary>
用户之前讨论了 Context Engineering 和 RAG 的区别。结论：RAG 负责查，CE 负责组织。
</history_summary>

<external_index>
以下内容未注入上下文，模型可通过工具按需获取：
- 完整日志文件：/tmp/task-log-20260629.txt (8500 tokens)
- 完整检索结果：12 条匹配的完整内容
</external_index>
```

The core value of this tiered approach is **to reduce the probability that key information will be inundated by noise.** Research and practice have shown that intermediate information in the context is more likely to be overlooked, which is often referred to as the "lost in the Middle" effect. Placing behavioral restraints at the beginning, following the current task, at the end of the external index is not always the best formula, but rather a sound engineering inspiration: let the model see the rules and objectives first, and finally see the entry point where information can continue to be obtained.

Key design decisions: **RAG and Memory to separate.** RAG is mission-related knowledge -- "What's the structure of this project?" Memory is user-related knowledge -- "What's this guy prefer to answer?" Combining makes it difficult to distinguish between "fact" and "preference". Tool Defenses and Tool Resources are also separated. **Tool definition tells the model what you can do, tool results tells the model what happened last time.** One is a capacity statement and the other is implementation feedback. When separated, the result of the historical tool can be trimmed when the context is overstretched without affecting the model ' s understanding of the tools available.

### 4.4.2 Budget: Long context is not a free warehouse

The layer solves the "where" problem, the budget solves the "how much". The context solves the problem of "letting down" and does not solve the problem of "good, fast, good". There are four reasons for this:

1. **Sensitivity**: The longer the context, the easier the model is to ignore key information buried in the middle. 100K token doesn't mean "100K is equally valid". The context capabilities of different models vary widely, but the judgement that "a long window is not an unlimited working memory" still holds true.
2. **Delays and costs**: the longer the context, the slower and more expensive each call. Every more 1000 token input, delay and cost are online or even more linear.
3. **Containment dilution**: System Prompt constraints may be diluted in the long context by a large number of intermediate elements. Your carefully written response in Chinese still exists, but the current steps of the model may have focused more on recent tool results, RAG clips or historical news.
4. **Cache failure**: production systems often rely on prompt caping to reduce costs and delays. If dynamic content is inserted in the prefix on each round, the system hints, tool definitions and stabilization norms will not allow for a stable reuse cache.

Set the Token budget for each layer:

| Layer | Budget scope (token) | Annotations |
|---|---|---|
| System Instructions | 1000-2000 | Core constraints, not participating in cropping |
| User Target + Current Plan | 500-1000 | Keep whole. |
| RAG Results | 2000-4000 | Intercept by relevance, mark cut points |
| Memoory, call back. | 500-1000 | Recall only the most relevant articles 3-5 |
| Tool Definitions | 500-1500 | Filter tools for current tasks |
| Tool results (nearest N step) | 3000-5000 | After a summary of the long results, we put it in. |
| History | 2000-3000 | Early messages are replaced by summaries |
| Cache Friendly Prefix | Depending on models and platforms | Stable system instructions, tool definitions, format specifications remain as sequence and content as possible |
| Total | Approx. 10000-16000 | Far below the model ceiling, but with high information density |

> **Important tip: This is not a fixed template.** The budget is the engineering parameter for task type, modelling capacity, cost constraints, delay requirement and common determination. The rational budget for different scenarios varies widely:

| scene | Context Policy Points |
|---|---|
| Customer service, Agent. | Short Context + Strong Rules + Small order information. Total budget 3000-5000 token |
| Code Review | Larger tool results budget (code segment required), but documents read without advance Load |
| Research, Agent. | SubAgent explores parallel + summation returns. Main Agent context is strictly controlled |
| Personal Assistant | Memoory self-management is more important - the cost of false memories is far greater than the cost token |
| Enterprise Knowledge Bank | Permission filter + Reference trace over token optimization |

Core principles for budget allocation: **The model is given whatever is needed for decision-making in this round. Models may later be needed, not necessarily now, to be converted into external indices and then acquired through tools when needed.** This explains why context cannot directly replace RAG. The long context is suitable for reading a small number of high-level materials at once, and the RAG is suitable for screening evidence from a large, complex and continuously changing knowledge base. The production system is not usually one-size-fits-all, but a combination: first by searching, filtering and reranking, then by putting a small number of high-value segments into the context; and then by using tools to read them as needed, if the model so requires.

### 4.4.3 Choice: Who should be left behind when the context is overstretched?

The budget was set, but it was still running well. The tool returns a 10000 line log, RAG recalls 20 clips. A choice must be made.

Core principles selected: **Sorted according to "Model decision-making dependency on this information" rather than "Is the information itself important?"** A memory may be important, but if it is not needed at this stage, it should not be at the expense of the budget.

```text
裁剪优先级（从先裁到后裁）：

1. 最早的工具输出 → 用摘要替代原文
   "步骤 2 的文件读取返回了 config.py，内容已记录在状态中"

2. 相关性低的 RAG 片段 → 丢弃
   保留 score > 阈值的片段，标注已丢弃数量和原因

3. 早期历史消息 → 用摘要替代
   "前 5 轮对话讨论了 X，结论是 Y"

4. Memory 召回 → 只保留用户明确设定的偏好
   丢弃自动推断的、置信度低的、与当前任务无关的记忆

5. 历史工具结果 → 只保留摘要 + 索引
   完整结果保存到外部文件，模型需要时可再次通过工具读取

永远不裁：
- System Prompt 的核心约束（安全规则、输出格式、角色定义）
- 用户当前消息
- 当前任务的执行计划和进度
```

There is an important design option here: **cropping logic should be placed "before the context is inserted" rather than "after the model has read the context".** Once the context has entered the attention window of the model, costing and attention dilution have already occurred. The choice before injection is a proactive management of the Token budget, not an ex post passivity.

## 4.5 Five types of means of production: writing, selection, compression, isolation, cache

The three introductory packages (stratification, budget, selection) address the question of how to organize the information available. But there are five deeper problems that Agent needs to solve:

- **In**: where does the middle state that has emerged from the implementation of Agent go? It can't be all over the news history.
- **Option**: selection of relevant elements from a large candidate (4.4.3 step)
- **Compressed**: how can long conversations, long tool results, long implementation trajectory be summarized as functional?
- **Segregation**: Lord Agent read himself or a pie?
- **Cache**: What stable elements should remain and what dynamic elements should be put back so as to avoid destroying the caches on each round?

### 4.5.1 Writing context: not just reading, but taking notes

Agent cannot rely only on chat history. The history of chat is a flow of books — each round of conversations is recorded, sequenced and not structured. When the task exceeds 10 paces, spans hours or even days, the flowbook history can get the model lost. **External status required:**

- Dismantling current target and subtask
- Completed steps and key outputs
- To-dos and dependency
- Verified facts and conclusions
- Excluded programmes and causes
- Document modification plan and progress
- User clearly identified constraints and decision-making
- Tool call result index (where is the complete result, what is the key finding)

This information does not need to be fully contextualized in each round, but needs to be systematically retained and selectively injected when appropriate. **Bad practice:**

```text
每轮都把完整的历史工具结果和消息塞回上下文：
message[0]: system prompt
message[1]: 用户：帮我发布一个新版本
message[2]: 助手：[工具调用] 读取 README，返回 3000 tokens……
message[3]: 助手：[工具调用] 检查课程 1，返回 5000 tokens……
message[4]: 助手：[工具调用] 检查课程 2，返回 4500 tokens……
……
message[20]: 用户：确认发布
message[21]: 助手：[工具调用] 执行发布脚本……

到第 20 轮，上下文已经超过 50000 tokens。
模型开始"忘记"用户的发布要求，忽略 README 的约束，甚至重复已完成的步骤。
```

**Better practice:**
```text
维护一个外部 Scratchpad / Runtime State：

{
  "goal": "发布 GitHub 阶段性版本 v0.5.0",
  "constraints": [
    "README 必须说明未完成章节",
    "license 使用 CC BY-SA 4.0",
    "发布前必须人工确认"
  ],
  "completed": [
    {"step": "检查 README", "result": "已更新，标注了未完成章节", "time": "2026-06-29 10:23"},
    {"step": "review 课程 1-4", "result": "通过，无需修改", "time": "2026-06-29 10:45"}
  ],
  "pending": [
    {"step": "review 课程 5-6", "depends_on": []},
    {"step": "补 examples 目录", "depends_on": ["review 课程 5-6"]},
    {"step": "生成 changelog", "depends_on": ["review 课程 5-6", "补 examples 目录"]}
  ],
  "evidence_index": {
    "README.md": "lines 1-80, 已确认包含未完成章节说明",
    "syllabus.md": "课程 5 章节索引已更新"
  },
  "decisions": [
    {"decision": "使用 CC BY-SA 4.0 而非 MIT", "reason": "用户明确要求", "confirmed_by": "user"}
  ]
}
```

For each round of reasoning, the part of Scratchpad relating to the current steps is selectively inserted into the context. Not all of the injections -- the models just need to know "where we are now, what we're going to do next, what we're going to have to do," without seeing a complete history of implementation.

Scratchpad can be written to a file by tool or saved by runningtime state scheme. Key design principles: **Only fields relevant to current decision-making are exposed to the model, while the remaining fields remain in the external state.**

### 4.5.2 Selection of context: Selected from mass information what the current steps need

Select to use the most frequent operation in Context Engineering. Its core questions are: **pick out what is really needed in terms of RAG results, Memory recall, tool definition, historical news.** This is different from "crop" in Section 4.4.3. Cutting is passive — the context is too limited. The choice is proactive — screening before injecting context.

Select the core strategy: **RAG Option** (see chapter II for further details):

- Relevance score threshold filter
- Heavy: Only one of the same contents is kept
- Conflict detection: when two clips give contradictory information, the priority time stamp is updated or the source is more authoritative **Memory Option** (see chapter III for further details):
- Only recall memories related to the semantics of the current task
- Time decay: the longer the memory, the higher the relevance score to be recalled
- User clearly set memory ( "Remember, I prefer X") above automatically extrapolated memory **Tool selection**:
- Not all tools are defined per round. The current step is probably not a tool that can't be used.
- When there are too many tools, group them by category, first let the model select the category and then inject the specific tool under the category
- When tools describe overlap, merge or remove redundancy tools - vague tool descriptions are themselves context noise **History Choice** - Last 3-5 rounds of original retention
- Keep only summary earlier
- A branch of history that has nothing to do with the current job can be cut.

### 4.5.3 Compressed context: from chat stream to task status summary

The budget was limited and it was not possible to retain all the original texts. Compression is a short summary of long content while retaining information useful for decision-making.

Three compression types:

| Compression Type | Compress objects | Keep what? | Drop what? | Main risks |
|---|---|---|---|---|
| **History compression** | Multi-round original | User objectives, confirmed conclusions, constraints, key decisions | Processive dialogue, exploratory tool calls, abandoned programs | Loss of detail leads to repeated questions and conflicting decisions by models |
| **Tool compression** | Long Tool Results | Key findings, evidence index, recommendations for next steps | Complete original text, intermediate process, redundant information | The summary error led the model to judge based on incomplete information |
| **Task compression** | Execute Track | Current plan, completed/to-do, blocking points, verified facts | Specific implementation process, retreat operation, resolved branch | Mission status drift - summary and actual inconsistent |

**History compression example:**
```text
原始历史（1500 tokens，5 轮对话）：
用户：查一下 context engineering 的论文
助手：[搜索工具] 找到了 8 篇……
用户：只看 2024 年以后的
助手：[过滤] 还剩 3 篇……
用户：第一篇讲了什么
助手：[读取] 这篇讨论了上下文窗口的注意力衰减……
用户：和我们的项目有什么关系
助手：[分析] 你们的上下文管线可以在组装阶段……

压缩后摘要（200 tokens）：
用户在研究 context engineering 相关论文，筛选到 2024 年后的 3 篇。
已讨论第 1 篇关于注意力衰减的内容，用户正在评估如何应用到自己的上下文管线。
关键决策：用户关注组装阶段的优化，暂不关注训练阶段的改进。
待确认：是否继续讨论剩余 2 篇。
```

**Example of tool compression:**
```text
原始工具结果（3000 tokens，grep 返回 120 行匹配）：
[120 行 grep 输出……]

压缩后（500 tokens）：
搜索 "rate_limiter" 在 8 个文件中找到 120 处匹配：
1. src/api/middleware.py - 23 处（限流器主实现）
   L45: class RateLimiter
   L78: def check_limit(self, key: str) -> bool
2. src/api/handlers.py - 15 处（使用限流器）
3-8. 其余 6 个文件共 82 处（测试、配置、文档）
完整结果索引：/tmp/grep-rate-limiter-20260629.txt
```

Compression is not an LLM you imagine calling out. The compression itself makes mistakes — the summary may omit key information, may misinterpret the intent, may not synchronize with the current mission state. It is therefore important that the index of the original information be maintained after the compression so that the model can be traced back to the original language, as needed.

### 4.5.4 Context of isolation: When should Agent see everything himself?

This is a relatively new engineering practice. Core idea: **Don't let a master Agent eat all the context. The Jean-Agent digs locally in his own context and returns only the results of the compression to the main Agent.** Agent can consume a large amount of token to dig up a problem -- reading dozens of files, analyzing complete logs, retrieving a large number of documents -- but returns only the sum of 1000-2000 tokens to master Agent. The context of the main Agent remains light.

| scene | Bad practice. | Better practices |
|---|---|---|
| Code library analysis | Master Agent reads dozens of files and the context expands rapidly to 50K+ | SubAgent submodule analysis, return structural summary and risk point for each module |
| Market research | Main Agent read all the information, and information on different topics interferes with each other | Multiple studies Agent sub-themes (competition, user needs, technology trends) are independently retrieved and each returns its structured summary |
| Bug, check. | Master Agent keeps all logs and stacks, and the context is flooded with technical detail | Log analysis |
| Document Review | Main Agent read complete 50 page document, distraction | Document Agent extracts structure, risks, inconsistencies, suggestions; main Agent sees only structured review reports |
| Extensive data exploration | Main Agent executes 20 SQL queries with all results in context | Data analysis Agent explores independently, returning only to critical insight and visualization suggestions |

The context isolation of subAgent is essentially part of Context Engineering -- you're deciding "what information is not given to the Lord Agent, but is left to another execution unit with its own context." This intersects with the subsequent Multi-Agent chapter (chap. VIII), but it is different: Context Engineering is concerned with "the budget allocation strategy in context" and Multi-Agent is concerned with "the organizational model of multi-role collaboration".

### 4.5.5 Cache and Company: Long sessions are not just handwritten summaries

Context management in the production environment also takes into account two issues that are easily overlooked by beginners: **cache** and **automatic compression**. **Cache concerns stabilization prefix.** Many model platforms will cache duplicate prompt prefixes to reduce delays and costs. The context must be assembled in such a way as to stabilize the stable content:

```text
适合放在稳定前缀：
- System / Developer Instructions
- 输出格式规范
- 稳定的工具定义
- 固定 few-shot 示例
- 长期不变的安全规则

适合放在动态后缀：
- 当前用户消息
- 当前计划和进度
- 本轮 RAG 片段
- 本轮 Memory 召回
- 最近工具结果
```

If the results of the latest tool are inserted in each round between the system command and the definition of the tool, the prefix changes frequently and the benefit of the cache disappears. Cacheful and friendly context layouts are usually: **stabilization rules preceded by dynamic tasks; stabilization content less changed and dynamic content less.**

**Compaction is concerned that long sessions continue to run.** When dialogue or mission trajectory becomes longer, the old message, the results of the tool and the implementation process can be summarized in a shorter state. There are two different floors:

| Type | Strengths | Risk |
|---|---|---|
| Handwritten Structured | Field clarity, auditability, alignment of performance and operations | Need you to design schema and update logic |
| Model/API AutoComposition | Access speed. It's good for long sessions. | The summary may be unexplainable, may lose details and need to retain the original index |

The practical approach is not one: critical mission status is written in Scratchpad, where historical dialogue and low-value tool results can be handed over to submission; all compressed content is indexed with original evidence, avoiding a model continuing its reasoning based on a non-retroactive summary.

## 4.6 Tool Output: Why does the tool result most easily deflect Agent?

### 4.6.1 Why tool output is the easiest to explode

Tool output is the most destructive of all context sources of pollution. The reason is simple: **You can't completely control the size of the tool output.** - System Prompt was written by you, the length is controlled.

- RAG turns out you search, you can just take top-K.
- Memoory recall is under your control and you can set a numerical ceiling.

But the tool output -- you let Agent read a file that could be 50 rows or 5,000 lines. You make it search the code library, possibly return 3 results, or 300. You let it run an order, stdout could be just one line or tens of thousands of lines.

And once the tool output enters the context, it becomes the next LLM call input. The model is based on these (possibly useless, possibly obsolete, potentially misleading) information for decision-making next. A bloated tool output is not only wasted, Token, but even more dangerous — it can lead models to drill the horns on irrelevant information.

Back to the 4.1 scene: After reading a technical detail in README, Agent deviated from the goal of "publishing readiness". This is the classic example of the context in which tools are exported.

### 4.6.2 Resulting in thinness

Different tools require different thin tactics: **Strategy I: Cut + Mark (suitable for file reading, log view)**

```text
原始输出：1500 行日志
处理后：
[前 50 行]
……
[日志中间 1350 行已省略，包含 23 条 INFO、5 条 WARNING]
……
[后 50 行]
总计 1500 行，已显示首尾各 50 行。如需查看完整日志，请指定行号范围。
```

Key: Interception must be marked with "what to cut" and "how to get what's left." Otherwise, the model may make an erroneous inference based on incomplete information. **Strategy II: Extract + Summary (suitable for code search, document retrieval)**

```text
原始输出：grep 返回 120 个匹配结果
处理后：
搜索 "context window" 在 8 个文件中找到 120 处匹配。按文件分组：

1. src/context/builder.py - 15 处匹配（上下文构建主文件）
   L42: def build_context(layers: List[ContextLayer]) -> str:
   L78: window_budget = self.calculate_budget(model_max_tokens)
   L156: truncated = self.truncate_by_priority(layers, remaining)

2. src/context/compressor.py - 8 处匹配（上下文压缩）
   L23: class ContextCompressor:
   L45: def compress_tool_output(self, output: str, max_tokens: int):

3-8. [其他 6 个文件共 97 处匹配，涉及测试和配置文件]
   使用 "grep -n 'context window' <file>" 查看具体行
```

Key: Structure the search results so that the model can quickly locate the most relevant files, rather than get lost in the 120 line grep output. **Strategy III: Structure + Filter (suitable for API calls, database queries)**

```text
原始输出：API 返回 200 条用户记录（JSON，每条 20 个字段）
处理后：
查询返回 200 条记录。按状态分组：
- active: 142 条
- inactive: 43 条
- suspended: 15 条

最近 5 条 active 记录的关键字段：
| id | name | email | last_login |
|----|------|-------|------------|
| 1  | ...  | ...   | ...        |

完整数据已写入临时文件 /tmp/query_result_20260629.json
需要进一步分析时，使用 read_file 工具读取指定字段。
```

Key: Don't let the model "remember" a lot of structured data. Keep summary and index and place the complete data where the model can be accessed again with tools.

### 4.6.3 Tool return is not just short, but actionable.

Skinnyness is the first step. But the good instrument output is not only short — it should directly serve the next decision. **Bad tool returns:**

```text
搜索 "rate_limiter" 返回 120 行匹配结果：
src/api/middleware.py:45: class RateLimiter:
src/api/middleware.py:78:     def check_limit(self, key: str) -> bool:
src/api/middleware.py:102:    def reset_limit(self, key: str) -> None:
src/api/handlers.py:23:       limiter = RateLimiter(redis_client)
src/api/handlers.py:56:       if not limiter.check_limit(user_id):
……
[115 more lines]
```

The model needs to solve 120 lines, figure out the focus, decide which document to read next. Each step represents an additional cost of reasoning and opportunity for error. **Better tool returns:**

```json
{
  "query": "rate_limiter",
  "total_matches": 120,
  "key_files": [
    {
      "file": "src/api/middleware.py",
      "role": "限流器主实现",
      "key_lines": [45, 78, 102, 156],
      "match_count": 23,
      "relevance": "核心"
    },
    {
      "file": "src/api/handlers.py",
      "role": "限流器使用方",
      "key_lines": [23, 56, 89],
      "match_count": 15,
      "relevance": "高"
    }
  ],
  "other_matches": "其余 6 个文件共 82 处匹配（测试、配置、文档）",
  "suggested_next_action": "read_file('src/api/middleware.py', start_line=40, end_line=160)"
}
```

When the model gets this result, it doesn't have to focus in 120 lines. It knows firsthand where the core is, what the key line is, what the next step is. This reduces the second judgement burden of the model and reduces the probability of error.

### 4.6.4 The tool itself also needs

Contact Engineering not only manages the results of the tool, but also the definition of the tool itself.

Tool description, parameter schema, return field description - these all consume context. An Agent with 50 tools, the definition of tools alone could account for 5000+tokens. If only five of the current tasks are required, then the other 45 tools are defined as pure context noise.

Also, when tools are defined as overlapping or vague, the model presents a tool selection error - both tools appear to be able to do this, and the model chooses an inappropriate one.

**Context management strategy for tool definition:**

1. **Task-based screening tool**: not all tools are injected per round. Based on the intent of the current step, only the definition of the instrument may be used.
2. **The tool description needs to be accurately distinguished**: if the two tools overlap, either merge or clearly distinguish in the description, "What is the scenario with A without B?"
3. **System model for too many tools**: e.g. "File Operating Class", "Code Search Class", "External API Class". The model selection tool group is first used to inject specific tools into the group.
4. **Budget set for tool definition**: as with tool results, tool definition consumes token. Sets a separate token budget for the tool definition area.

### 4.6.5 Clean-up, not just compression: Move context after use

Compression is to make long content shorter. But there are tools whose results should not be reduced and retained — they should be cleaned up.

The following types of tools are suitable for clean-up rather than compression:

- **One-time query result**: 500 line results of a SQL query. The current steps are useful, but no further 20 rounds are required.
- **Full original**: read a 5,000 line HTML page. The summary is sufficient and the original text should not be in the context.
- **Duplicate results**: same grep ran three times (different parameters), last time only.
- **Large binary/log**: full log file line 20000. Only the abnormal summary + file path index is kept in the context. **Clean-up strategy:**

```text
1. 工具结果只在接下来 N 轮可见（如 N=3），超出的自动清理
2. 同类工具结果只保留最后一次（新的 grep 结果替换旧的）
3. 大型结果不进入 message history，而是保存到外部 store，上下文中只保留结果 ID / 文件路径
4. 跨轮仍然需要的结果——如用户确认过的决策——应该提取到 Scratchpad，而不是留在工具结果里
```

**Clean vs compression option:**
| Situation | Compression | Clean up. |
|---|---|---|
| Results may be cited in subsequent steps | ✅ | ❌ |
| Results include user-identified decision-making | Scratchpad | ❌ |
| The result is a one-time query. | ❌ | ✅ |
| The result is over 5000 tokens and low information density. | ❌ | ✅ |
| Updated version of similar results | ❌ | ✅ (cleaning old versions) |

A practical rule of practice: **if the results of the tool are useful for subsequent decision-making, they are kept in a condensed form. If it's just an intermediate process, then clean it up.**

### 4.6.6 Code skeletons: adjectable result processing Device

Do not write dead logic for each tool. Register different treatment strategies by tool using a plug-in result processor:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ProcessedResult:
    """处理后的工具输出"""
    content: str                # 注入上下文的内容
    original_size: int          # 原始大小（tokens）
    processed_size: int         # 处理后大小（tokens）
    truncated: bool             # 是否被截断
    truncation_note: Optional[str] = None  # 截断说明（供模型理解）
    external_ref: Optional[str] = None     # 完整结果的外部存储路径

class ResultProcessor(ABC):
    """工具输出处理器基类"""
    @abstractmethod
    def process(self, raw_output: str, max_tokens: int) -> ProcessedResult:
        ...

class FileReadProcessor(ResultProcessor):
    """文件读取：保留首尾，中间截断"""
    def process(self, raw_output: str, max_tokens: int) -> ProcessedResult:
        lines = raw_output.split("\n")
        if len(lines) <= 100:
            return ProcessedResult(
                content=raw_output,
                original_size=len(raw_output),
                processed_size=len(raw_output),
                truncated=False
            )
        head = "\n".join(lines[:50])
        tail = "\n".join(lines[-50:])
        omitted = len(lines) - 100
        content = (
            f"{head}\n\n……\n[中间 {omitted} 行已省略]\n……\n\n{tail}\n\n"
            f"[文件共 {len(lines)} 行，已显示首尾各 50 行。"
            f"如需查看完整文件，请指定行号范围调用 read_file。]"
        )
        return ProcessedResult(
            content=content,
            original_size=len(raw_output),
            processed_size=len(content),
            truncated=True,
            truncation_note=f"文件共 {len(lines)} 行，已显示首尾各 50 行"
        )

class SearchResultProcessor(ResultProcessor):
    """搜索结果：结构化分组摘要"""
    def process(self, raw_output: str, max_tokens: int) -> ProcessedResult:
        # 分组、去重、按文件聚合……
        # 返回结构化的搜索结果摘要
        ...

class APIResultProcessor(ResultProcessor):
    """API 结果：统计摘要 + 关键样本 + 外部存储"""
    def process(self, raw_output: str, max_tokens: int) -> ProcessedResult:
        # 解析 JSON，提取统计信息，保留少量关键记录
        # 完整数据写入临时文件，返回文件路径作为 external_ref
        ...

class GenericProcessor(ResultProcessor):
    """通用处理器：简单截断"""
    def process(self, raw_output: str, max_tokens: int) -> ProcessedResult:
        char_limit = max_tokens * 4  # 粗略估算 1 token ≈ 4 chars
        if len(raw_output) <= char_limit:
            return ProcessedResult(
                content=raw_output,
                original_size=len(raw_output),
                processed_size=len(raw_output),
                truncated=False
            )
        truncated = raw_output[:char_limit]
        return ProcessedResult(
            content=(
                f"{truncated}\n\n"
                f"[输出已截断，原始长度 {len(raw_output)} 字符，"
                f"已截断至约 {max_tokens} tokens。如需完整内容，请使用更精确的查询参数。]"
            ),
            original_size=len(raw_output),
            processed_size=len(truncated),
            truncated=True,
            truncation_note=f"输出超出限制，已截断至约 {max_tokens} tokens"
        )

# 注册处理器
result_processors = {
    "read_file": FileReadProcessor(),
    "search_codebase": SearchResultProcessor(),
    "call_api": APIResultProcessor(),
    # 未注册的工具使用 GenericProcessor
}
default_processor = GenericProcessor()

def process_tool_output(tool_name: str, raw_output: str, max_tokens: int) -> ProcessedResult:
    """对工具输出进行处理后再注入上下文"""
    processor = result_processors.get(tool_name, default_processor)
    return processor.process(raw_output, max_tokens)
```

The core design of this skeleton:

1. **The logic of the independent processing of each tool**: the output patterns of file reading and code search are completely different and cannot be one-size-fits-all
2. **Process results are transparent**: Tell the model "Preliminary size, processing size, cut-off, complete results, where" and the model needs this meta-information to judge.
3. **The cut-off is for the model**: `"文件共 1500 行，已显示首尾各 50 行"` — Models know that information is incomplete and they decide whether to continue to base their reasoning on existing information or to use tools to get more content
4. **external ref supports cleanup semantics**: full results are saved externally and only summarized in context. The next round can remove the tool result from the cleanup mechanism and keep only the external ref index

### 4.6.7 Contextal credibility: information is not an instruction

Context work is not only a matter of length but also of credibility. The text that enters the context does not all have the same weight: System Studies is the rule, user message is the target, RAG footage is the evidence, web content and tool results are only external observations. The most dangerous error is to use the instructions in the external information as a system directive.

Typical risks include:

- The RAG section is mixed with a malicious message:
- The main text of the web page contains hidden instructions for reptiles or models
- Forgery recommendations in logs, README, issue reviews
- Memoory saved obsolete or contaminated preferences
- Tool returned unauthorized filtered data

So every information that enters the context should have metadata, not just text:

```json
{
  "content": "检索到的片段正文……",
  "source": "docs/security.md",
  "source_type": "rag",
  "timestamp": "2026-06-29T10:30:00+08:00",
  "trust_level": "reference_only",
  "permission_scope": "project:agent-learning-roadmap",
  "freshness": "current",
  "instruction_authority": "none"
}
```

Key principles: **External information can provide facts that do not cover the rules of the system; tool results can provide observations and do not authorize subsequent operations on their own; Memory can provide preferences that do not bypass current user goals and permission boundaries.** When conflicts occur from different sources, the system will indicate the conflict in a visible manner, rather than allowing the model itself to guess in a series of conflicting texts.

## 4.7 How does the context strategy really work?

Context Engineering can't just feel -- "I think the answer is better after the layering" is not engineering language. You need indicators and data to verify that the strategy is actually working. **Core assessment indicators:**

| Indicators | Annotations | How? |
|---|---|---|
| Task Success Rate | Task Completion Rate - Does Agent Set User Target | Manual labelling or LLM-as-Judge assessment |
| Constraint Following Rate | Output format, security constraints, language bound compliance rate | Autodetection (reforms, format validation) or manual labelling |
| Tool Call Accuracy | Whether the tool selection is correct or reasonable | Compare old tool call or manual assessment |
| Retrieval Usefulness | Whether RAG/Memory content is used effectively | Check if model answers refer to injection (citiation match) |
| Context Utilization | How much of the infusion really affected the answer? | Compare output differences with/without the content |
| Token Cost | Enter token, output token, total cost | API returned usage field |
| Latency | Model response delay (including context time of assembly) | End-to-end timing |
| Context Drift Rate | Multi-cycle target deviation ratio - Does Agent still do the original thing? | Per N round to compare current behaviour with initial target |
| Recovery Rate | Recovery after error — ratio re-matched after context-related problems | Mark "deviation" event, statistical recovery rate |
| Injection Resistance | Whether to continue to comply with the rules of the system in the event of malicious instructions in the external context | Construct RAG/webpage/tool output injection sample |
| Context Ablation Sensitivity | Whether the result after deleting a category of context is significantly degraded | Remove RAG, Memoory, Tool Digest, ScratchPad |

**A simple A/B assessment design:** It does not need to be fully automated from the outset. Fixed 30 representative mission samples, hand-run four sets:

```text
A 组：全量上下文（V0 baseline）
  所有信息原封不动注入，不做分层、不做预算、不做压缩

B 组：分层 + 预算（V3）
  上下文按 4.4.1 的分层结构组织，每层有预算上限

C 组：分层 + 预算 + 工具压缩（V4）
  在 B 组基础上，为高频工具注册结果处理器

D 组：分层 + 预算 + 工具压缩 + Scratchpad（V4+）
  在 C 组基础上，引入外部 Scratchpad 管理任务状态

比较维度：
- 完成率（任务是否成功完成）
- 平均输入 token 数
- 平均耗时
- 约束遵守率（如输出格式、语言要求）
- 注入攻击通过率（恶意上下文是否被当成资料而不是指令）
- 上下文消融结果（移除某类信息后质量是否下降）
- 人工评分（1-5 分，由你或同事评估回答质量）
```

After 30 samples x 4 groups = 120 assessments, you'll have data support for "what strategy really works in your scene," rather than sensory involvement.

The core value of the assessment is not "prove that my strategy is the best" but what strategies are really useful to your type of mission and what strategies are overdesigned. You may find that Group B (Strategic + Budget) has already mentioned the completion rate from 70% to 90%, Group C (plus tool compression) to 93%, but Group D (plus Scratchpad) does not rise or fall -- because your task is rarely more than five steps, and the additional complexity of Scratchpad has introduced a new pattern of failure.

That's the point of the assessment: **from "I think I should add" to "data needs added."**

## 4.8 Evolutionary route: from "all in" to "the context control system"

Context Engineering does not need a step in place. As with all enhancements, it should start with the smallest version:

| Phase | What did you do? | Added Capability Dimension | Apply scene |
|---|---|---|---|
| **V0: All in** | All messages remain unmoved into context and cut with tokenizer | None | Prototype validation, one-step simple task |
| **V1: plus budget** | Set a maximum number of tokens for each type of information, which is simply cut when exceeded | Budget | Prototype with no more than 3 sources |
| **V2: Tool-output processing** | Registration of results processor for HF tools, long output compression/cleaning | Budget + tool compression | Tool calls frequently, output easily explodes |
| **V3: Layer + Priority** | Context structured layers, cut by priority rather than simply cut over time | Layer + Budget + Selection | Source 3+, multi-step task |
| **V4：Scratchpad + Compaction** | Introduction of external status to manage task progress; structured compression of historical and tool results | + Write + Compress | A single task exceeding 10 steps, or crossing multiple rounds |
| **V5: Child isolation** | The context submission was assigned to the child Agent independently and returned only to the enrichment results | + Segregation | Complex tasks requiring in-depth analysis of a large number of documents |
| **V6: Cache friendly + Trustworthiness layer** | Stable prefix reuse cache; indicating source, permission and credibility for external context | +Cache + Secure Border | Cost-sensitive or access to external web pages, enterprise knowledge base, user memory systems |
| **V7：Eval-driven Optimization** | Establish an evaluation system for context strategies, using data-driven policy selection and parameter optimization | + Evaluation | Production systems that continuously optimize the quality of context |

The logical goal for most projects is **V3 (Strategic + Priority)**. V4-V7 applies to:

- Single tasks often exceed 10 steps
- There is often a need for in-depth analysis of a large number of codes/documents.
- Costs and delays have become bottlenecks, or external information is at risk of injection
- • Consider V7

An important rule of experience: **Every time you add a new source of information to your context, add a paragraph dealing with logic.** Not just producers, unorganized.

## 4.9 Common failure symptoms and treatment: from context to context attack

These symptoms will not occur at the same time, but almost every Agent project that has evolved from the prototype to production will encounter 2-3:

| Problem performance | Common statements in industry | Bottom Interpretation | Treatment direction |
|---|---|---|---|
| **Constraint oblivion**: the model violates the explicit constraints in System Prompt | Instruction Dilution | Constraint is "drowned" in the long context and attention is diverted to a lot of irrelevant token. | Repeat key constraints at the end of the context; shorten the total length of the context; and place constraints at the beginning of the focus |
| **Lost in the middle**: the model ignores information on the middle of the context | Lost in the Middle | The attention mechanisms are significantly less focused on the middle of the sequence than on the beginning and end. | Place key information at the beginning or end; summarize intermediate content and move forward; avoid burying important information in the middle of context |
| **Tool result poisoning**: The model is running away from a non-relevant tool output and subsequent multiple wheels are spinning around irrelevant content | Context Poisoning | Tool output is injected without filtering, and large unrelateds dominate attention. | Register processor for tool output; set Token ceiling for single tool output; use "Summary + External Index" mode for large results; implement tool-result clearing |
| **Infoconflict**: RAG clips and Memoory recall give conflicting preferences or facts | Context Clash | Different sources of information lacked mechanisms for heavy and conflict resolution, and models were randomly selected or stitched in the face of conflicting information | Add cross-source-by-source logic; prioritize time-stamp updates or more authoritative sources when information conflicts occur; highlight "controversial" when conflicts are detected |
| **Context inflation**: tool results added per round, context approaching window ceilings | Context Rot / Bloat | Historic tool output has not been compressed or cleaned up, the context is growing like snowball, and each round is slower and more expensive | Summary replacement for tool output exceeding N steps; setting the context usage alarm threshold (e. g. 70 per cent); introducing tool-result clearing; moving task status out to Scratchpad |
| **Repeat injection**: The same knowledge appears in the RAG results and Memoory | Context Redundancy | There is a lack of coordination between the sources of information, and repeat content is valuable token budget without increasing the amount of information | Cross-source heavy at the Context Assembly stage; priority is given to the same content using a higher quality version of the source; the label for duplicate content "has appeared in [source]" |
| **Context Injecting**: external web pages, RAG clips or tool results require models to ignore old rules | Context Injection | The system doesn't distinguish between "information text" and "directive text". | Identification of sources and credibility for external context; clear reference-only; high-risk actions must be authorized and manually identified |

## 4.10 When does context work not be required?

Context Engineering is also following the "on demand" principle. A complex design is not required for:

1. **One-step simple task**: a user asks, a model answer, no tools to call, no multiple rounds of history. Just send System Prompt+ user message.
2. **Single source**: only System Prompt and user messages, no RAG, Memory, tool output. No need for Division.
3. **The context is far below the ceiling of the model**: the total number of Tokens is less than 30 per cent of the ceiling of the model, with simple tasks and few steps. Excessive design of the context line is a waste of engineering resources.
4. **Prototype validation phase**: still checking if "this direction works". V0 is completely acceptable. Context Engineering is a means of optimization, not a precondition.
5. **Short life cycle Agent**: This Agent was abandoned only a few times — for example, one-time data migration script. It's not worth setting up a context line.

A judgement signal: **When you find yourself beginning to write "Please follow Rule X" in System Prompt, indicate that the context is long enough to be bound by the model. This is the signal that introduced Context Engineering.** In turn, if your Agent is running well now — the restraints are being complied with, the tools are not being missed, the users are not complaining about the quality of the answer being reduced — then continue with the current context strategy. **Contex Engineering is a cure, not a healthcare. Don't eat when there's no problem.**

### Summary of this chapter

The context is the immediate vision of the current phase of the model ' s decision-making, while the full vision of Agent consists of context, external state, tools, long-term memory.

Context Engineering is the dynamic management of which information enters the model, which remains external, which is compressed, which is handed over to the sub-Agent for quarantine, which stable content should cache, and which needs to be evaluated and validated before each step of the decision is made.

The introduction starts with three things: a hierarchy (each type of information is in place and does not mix RAG, Memory, tool results), a budget (the long context is not simply filled because of locational sensitivity, delayed costs, thinning of constraints and cache lapses), and a choice (when overstretching is based on model dependence on that information, not important first exit).

Production levels also require five types of means: writing (Scratchpad management task), choice (involved extraction of current steps from mass information), compression (historical compression, tool compression, task compression and control), isolation (the son Agent digs deep in his own context and returns enrichment to the master Agent only), cache (stable pre-fixing, dynamic content after).

The output of tools is the most explosive context — not just thinness, but also "actionable", the definition of management tools themselves, the distinction between injection and externalization, the clean-up of one-time results, not just compression.

The external context must be sourced, competent and credible, and the information cannot cover the rules of the system. The assessment data (completion rate, binding compliance rate, context utilization, delayed costs, injection of resistance and digestion results) rather than the perceived effectiveness of the strategy are used to test the effectiveness.

When you start writing "Serve Rule X" in Prompt, it's time to introduce Context Engineering.

## Runable Example

Once this chapter has been completed, you can compare the local Context Engineering example of running course 5 05-04:

- [Course 5 05-04 Context Engineering/ Context Project Example](../examples/course-05-04-context-engineering/README.md)

This example revolves around the "publishing assistant" scene, with Python and Node.js versions demonstrating the difference between the same context sources under the Naive policy and the Engineering strategy: the Naive policy injects all the information in its original form, and the Engineering strategy starts with the context layering, then the Token budget, priority cutting, tool output thinness, Scratchpad injection, pre-stability prefixing and credibility labels. The examples also include A/B assessment, injection of attack samples and context digestion to observe the impact of different context strategies on cost, signal retention and safety.

The example is teaching realization, which is not a complete production framework: Token estimates are light-supplied and tool output compression and injection testing rules are achieved; real systems should be replaced with models tokenizer, task-related compressors and more complete safety strategies. The Python and Node.js versions are not dependent on external services or API Key.

```bash
# Python 版本
cd examples/course-05-04-context-engineering/python
python3 context_engineering_demo.py
python3 -m unittest test_context_engineering.py

# Node.js 版本
cd examples/course-05-04-context-engineering/nodejs
npm start
```

---

> **Chapter IV Review.** You now have four perspectives on Agent: RAG that allows it to access external knowledge, Memoory that allows it to remember user and task status, Context Engineering that allows multi-source information to be organized in the context rather than flood each other. These three together make up Agent's context-enhanced capacity-- It's a question of "where the information for decision-making comes from and how."
>
> Agent, however, faced with a complex task, had another problem that remained unresolved: **information was available, but the sequence of implementation between multiple steps, dependency, failure to restore how to organize?** Naked Rect Cycle has no mission structure, multi-step tasks are easily driftable and do not know where to recover from.
>
> That's the next chapter Planning to answer.
