# 课程三：最小 Agent 闭环

## 课程导言

课程一让你看见 Agent 产品的真实形态，课程二解释了 Agent 范式为什么会演进到今天。到了课程三，学习重点从“理解概念”进入“掌握结构”。

这一课要回答一个非常具体的问题：

```text
一个最小但完整的 Agent，到底由什么组成？
```

很多学习者一开始会把 Agent 想成“一个更强的 LLM”。这会导致两个误区：

- 以为只要模型足够强，Agent 就会自动可靠。
- 以为只要加上 RAG、Memory、Planning、MCP、Multi-Agent，就能成为完整 Agent。

这两个判断都不准确。

本课的核心观点是：

```text
Agent = LLM 决策 + 工具/环境交互 + 状态管理 + 循环控制
```

这个公式不是为了定义所有 Agent 产品的全部能力，而是为了抓住“最小闭环”。后续课程中的工具机制、RAG / Memory、Planning / Workflow Patterns、Harness、Evaluation、Guardrails，都是围绕这个闭环继续扩展。

课程三只解决一件事：**让你真正理解并能实现一个最小可运行 Agent**。

---

## 学习目标

学完本课，你将能够：

1. **解释最小 Agent 为什么不能只有 LLM** — 理解模型决策、工具交互、状态管理和循环控制各自承担什么职责
2. **画出最小 Agent 运行链路** — 说清 `User Goal -> Context Assembly -> LLM Decision -> Interaction -> Observation -> State Update -> Continue or Stop`
3. **区分核心组成和运行连接点** — 明白 Context Assembly、Observation / Feedback 不是额外“核心模块”，而是运行时连接环节
4. **理解状态管理为什么是多步任务的基础** — 知道任务状态、历史消息、工具结果、错误信息如何支撑下一轮决策
5. **设计最小循环控制规则** — 包括停止条件、最大步数、超时、重复动作检测和失败退出
6. **规划一个最小 ReAct Agent 的实现方案** — 能定义工具、状态、Trace、错误处理和测试任务

本课围绕以下核心问题展开：

- 一个最小 Agent 为什么不能只有 LLM？
- LLM 如何根据上下文和状态做下一步决策？
- 工具/环境交互如何产生反馈，并影响下一轮决策？
- 状态管理如何支撑多步任务，而不是只处理单轮问答？
- 循环控制如何判断继续、停止、重试或失败退出？

---

## 目录

- [课程导言](#课程导言)
- [学习目标](#学习目标)
- [第一章：为什么最小 Agent 不能只有 LLM](#第一章为什么最小-agent-不能只有-llm)
  - [1.1 LLM 只能生成下一段文本](#11-llm-只能生成下一段文本)
  - [1.2 Agent 必须能影响外部世界](#12-agent-必须能影响外部世界)
  - [1.3 Agent 必须能持续工作](#13-agent-必须能持续工作)
  - [1.4 Agent 必须能受控停止](#14-agent-必须能受控停止)
- [第二章：最小 Agent 组成](#第二章最小-agent-组成)
  - [2.1 核心公式](#21-核心公式)
  - [2.2 LLM 决策](#22-llm-决策)
  - [2.3 工具/环境交互](#23-工具环境交互)
  - [2.4 状态管理](#24-状态管理)
  - [2.5 循环控制](#25-循环控制)
- [第三章：最小运行链路](#第三章最小运行链路)
  - [3.1 User Goal：用户目标](#31-user-goal用户目标)
  - [3.2 Context Assembly：上下文组装](#32-context-assembly上下文组装)
  - [3.3 LLM Decision：模型决策](#33-llm-decision模型决策)
  - [3.4 Tool / Environment Interaction：工具或环境交互](#34-tool--environment-interaction工具或环境交互)
  - [3.5 Observation / Feedback：观察和反馈](#35-observation--feedback观察和反馈)
  - [3.6 State Update：状态更新](#36-state-update状态更新)
  - [3.7 Continue or Stop：继续或停止](#37-continue-or-stop继续或停止)
- [第四章：运行时循环总览](#第四章运行时循环总览)
  - [4.1 最小闭环图](#41-最小闭环图)
  - [4.2 State / Memory Store 的位置](#42-state--memory-store-的位置)
  - [4.3 Context Assembly 和 Observation 为什么不是额外核心模块](#43-context-assembly-和-observation-为什么不是额外核心模块)
  - [4.4 最小闭环背后的工程原则](#44-最小闭环背后的工程原则)
- [第五章：沿运行链路展开学习](#第五章沿运行链路展开学习)
  - [5.1 每个运行环节要解决的问题](#51-每个运行环节要解决的问题)
  - [5.2 最小 Agent 不必包含哪些能力](#52-最小-agent-不必包含哪些能力)
  - [5.3 从最小闭环走向后续课程](#53-从最小闭环走向后续课程)
- [第六章：最小 ReAct Agent 的实现思路](#第六章最小-react-agent-的实现思路)
  - [6.1 推荐最小技术栈](#61-推荐最小技术栈)
  - [6.2 伪代码结构](#62-伪代码结构)
  - [6.3 工具设计](#63-工具设计)
  - [6.4 Trace 记录](#64-trace-记录)
  - [6.5 基础错误处理](#65-基础错误处理)
  - [6.6 测试任务设计](#66-测试任务设计)
- [课后练习](#课后练习)
- [验收标准](#验收标准)
- [参考资料](#参考资料)
- [下一课衔接](#下一课衔接)

---

## 第一章：为什么最小 Agent 不能只有 LLM

### 1.1 LLM 只能生成下一段文本

LLM 的直接能力是根据输入上下文生成输出。它可以理解用户目标，也可以推理下一步应该做什么，但它本身并不会真的执行外部动作。

例如你问：

```text
帮我检查这个项目为什么测试失败。
```

一个只包含 LLM 的系统最多会回答：

```text
你可以先运行测试命令，查看错误日志，再定位相关文件。
```

这不是 Agent，它只是给建议。

如果要成为 Agent，系统至少要能：

- 读取项目文件。
- 执行测试命令。
- 接收测试结果。
- 根据错误信息决定下一步。
- 在必要时停止或请求用户介入。

这就超出了“只生成文本”的范围。

### 1.2 Agent 必须能影响外部世界

Agent 和 Chatbot 的关键差异之一，是 Agent 能通过工具或环境动作影响外部世界。

这里的“外部世界”可以很简单，不一定是浏览器或真实业务系统。它可以是：

- 一个本地文件。
- 一个 API。
- 一个数据库查询。
- 一段代码执行结果。
- 一个搜索结果。
- 一个任务状态对象。

只要模型的决策能触发外部动作，并拿到外部反馈，它就开始进入 Agent 的范围。

### 1.3 Agent 必须能持续工作

单次工具调用还不够。

一个最小 Agent 必须能多轮推进任务：

```text
理解目标 -> 判断下一步 -> 执行动作 -> 观察结果 -> 更新状态 -> 再判断下一步
```

这就是“闭环”。

如果系统只做一次判断、一次工具调用、一次回答，它更像工具增强问答。真正的 Agent 需要在任务没有完成时继续推进。

### 1.4 Agent 必须能受控停止

循环带来能力，也带来风险。

如果没有循环控制，Agent 可能：

- 一直重复调用同一个工具。
- 遇到错误后无限重试。
- 在任务已经完成后继续多余操作。
- 在不确定时仍然执行高风险动作。
- 花费过多 token、时间或 API 成本。

所以最小 Agent 不只是“能继续”，还必须“能停止”。

循环控制是最小闭环的一部分，不是上线前再补的保护逻辑。

---

## 第二章：最小 Agent 组成

### 2.1 核心公式

课程三使用这个公式理解最小 Agent：

```text
Agent = LLM 决策 + 工具/环境交互 + 状态管理 + 循环控制
```

四个部分缺一不可。

| 组成 | 负责什么 | 如果缺失会怎样 |
|---|---|---|
| LLM 决策 | 理解目标、判断下一步、选择动作 | 系统无法处理开放目标 |
| 工具/环境交互 | 获取外部信息或影响外部环境 | 系统只能说，不能做 |
| 状态管理 | 保存任务、历史、结果、错误和中间信息 | 系统无法连续工作 |
| 循环控制 | 判断继续、停止、重试或失败退出 | 系统容易失控或无法完成多步任务 |

这个公式不是说所有 Agent 只能有这四个部分，而是说：**如果连这四个都没有，就不能算一个最小完整 Agent。**

### 2.2 LLM 决策

LLM 决策是 Agent 的“大脑”。

它负责回答：

- 用户目标是什么？
- 当前已经知道什么？
- 下一步应该做什么？
- 是否需要调用工具？
- 应该调用哪个工具？
- 工具参数应该是什么？
- 当前任务是否已经完成？

LLM 决策需要依赖上下文。上下文质量越差，决策越容易错。

最小 Agent 中，LLM 决策通常输出结构化结果，而不是任意自然语言。例如：

```text
decision_type: call_tool
tool_name: read_file
arguments:
  path: notes.md
reason: 需要读取用户指定文档才能完成总结任务
```

结构化输出的好处是：Runtime 可以明确知道模型想做什么，并决定是否允许执行。

### 2.3 工具/环境交互

工具/环境交互是 Agent 的“手”和“眼”。

工具让 Agent 可以：

- 读取文件。
- 写入文件。
- 查询 API。
- 执行代码。
- 搜索资料。
- 查询数据库。
- 访问业务系统。

环境反馈让 Agent 可以知道：

- 工具是否成功。
- 返回了什么结果。
- 是否发生错误。
- 下一步是否需要调整。

在最小 Agent 中，工具可以非常简单。你不需要一开始接入复杂工具平台。

最小工具示例：

| 工具 | 用途 | 风险等级 |
|---|---|---|
| `read_file` | 读取本地文本文件 | 低 |
| `write_file` | 写入本地文件 | 中 |
| `search_notes` | 在一组文本里搜索关键词 | 低 |
| `calculate` | 执行简单计算 | 低 |
| `fetch_api` | 调用一个公开 API | 中 |

课程四会深入讨论工具定义、选择、执行、权限和安全。本课只要求理解：工具是闭环中的外部交互点。

### 2.4 状态管理

状态管理让 Agent 从“单轮问答”变成“多步任务执行”。

一个最小 Agent 至少要维护：

- 用户目标。
- 当前步骤数。
- 历史消息。
- 已调用的工具。
- 工具返回结果。
- 中间结论。
- 错误信息。
- 停止原因。

状态不等于长期 Memory。

在本课中，状态主要指当前任务运行时需要保存的信息。长期 Memory 是后续课程五的内容，不是最小闭环的必选项。

最小状态可以长这样：

```text
task:
  goal: "读取 notes.md，并总结为 5 个要点"
  step_count: 2
  max_steps: 8
  history:
    - user_goal
    - decision_read_file
    - observation_file_content
  tool_results:
    - tool: read_file
      status: success
      summary: "读取到 1200 字 Markdown 内容"
  errors: []
  stop_reason: null
```

状态管理的关键不是“存得多”，而是“下一轮决策需要什么就保存什么”。

### 2.5 循环控制

循环控制决定 Agent 是否继续执行。

最小循环控制至少包括：

- 最大步数。
- 每步超时。
- 工具失败次数上限。
- 重复动作检测。
- 成功完成判断。
- 失败退出判断。
- 必要时请求用户介入。

常见停止原因包括：

| 停止原因 | 说明 |
|---|---|
| `completed` | 任务已完成 |
| `max_steps_exceeded` | 超过最大步骤 |
| `tool_error_limit` | 工具连续失败 |
| `invalid_decision` | 模型输出无法解析或不合法 |
| `need_user_input` | 需要用户确认、补充信息或接管 |
| `unsafe_action` | 动作风险过高，不能自动执行 |

没有循环控制的 Agent，很难从 demo 走向可靠系统。

---

## 第三章：最小运行链路

最小 Agent 不只是四个组成部分，还需要一条运行链路把它们连接起来。

```text
User Goal
    -> Context Assembly
    -> LLM Decision
    -> Tool / Environment Interaction
    -> Observation / Feedback
    -> State Update
    -> Continue or Stop
```

核心公式描述的是组成能力，运行链路描述的是这些能力如何协作。

### 3.1 User Goal：用户目标

用户目标是 Agent 的起点。

目标可以很简单：

```text
读取 notes.md，总结成 5 个要点。
```

也可以稍微开放：

```text
帮我整理这个目录下的学习笔记，生成一份 Agent 工具调用主题的文章草稿。
```

最小 Agent 适合先从简单目标开始。目标过大时，容易同时涉及 Planning、文件系统、Memory、权限、安全等后续能力。

一个好的最小目标应该满足：

- 需要至少两步完成。
- 需要至少一次工具或环境交互。
- 结果可以验证。
- 风险较低。

### 3.2 Context Assembly：上下文组装

Context Assembly 决定哪些信息进入模型上下文。

它通常包含：

- 用户目标。
- 系统约束。
- 当前任务状态。
- 历史决策。
- 最近工具结果。
- 错误信息。
- 可用工具列表。

上下文组装不是简单把所有东西都塞给模型。

你需要问：

- 模型下一步决策需要哪些信息？
- 哪些历史结果已经可以摘要？
- 哪些工具结果太长，应该压缩？
- 哪些信息是约束，必须保留？

最小 Agent 中可以先使用简单策略：

```text
系统指令 + 用户目标 + 最近 N 步历史 + 可用工具列表 + 当前状态摘要
```

课程六会进一步深入 Context Engineering。本课只要求理解上下文组装在闭环中的位置。

### 3.3 LLM Decision：模型决策

LLM Decision 是每轮循环的核心。

模型需要根据上下文输出下一步：

- 继续调用工具。
- 生成最终答案。
- 请求用户补充信息。
- 停止并说明失败原因。

最小 Agent 可以要求模型输出以下决策类型：

| 决策类型 | 含义 |
|---|---|
| `call_tool` | 调用工具 |
| `final_answer` | 输出最终结果 |
| `ask_user` | 请求用户补充信息或确认 |
| `fail` | 无法继续，失败退出 |

这样 Runtime 可以根据决策类型执行不同逻辑。

模型决策不是最终执行。Runtime 仍然需要校验：

- 工具是否存在。
- 参数是否合法。
- 是否超过权限。
- 是否超过步数。
- 是否应该请求用户确认。

这体现了一个重要原则：

```text
模型负责提出下一步，Runtime 负责判断能不能执行。
```

### 3.4 Tool / Environment Interaction：工具或环境交互

当模型决定调用工具时，Runtime 会执行工具或环境动作。

工具执行包括：

- 校验工具名。
- 校验参数。
- 执行工具。
- 捕获异常。
- 规范化返回结果。

工具结果不应该直接无处理地塞回模型，尤其是结果很长或包含错误时。

最小 Agent 至少要把工具结果整理成：

```text
tool_name:
status:
result_summary:
raw_result_reference:
error:
```

如果工具失败，也要返回结构化 Observation，而不是让程序直接崩溃。

### 3.5 Observation / Feedback：观察和反馈

Observation 是工具或环境动作的结果。

它可能是：

- 文件内容。
- 搜索结果。
- API 响应。
- 代码执行输出。
- 错误信息。
- 权限拒绝。
- 用户确认或驳回。

Observation 的作用是影响下一轮决策。

例如：

```text
Action: read_file("notes.md")
Observation: 文件不存在
Next Decision: ask_user("没有找到 notes.md，请确认文件路径")
```

如果没有 Observation，Agent 就无法根据外部反馈调整行为。

### 3.6 State Update：状态更新

State Update 把本轮发生的事情写回状态。

需要记录：

- 模型做了什么决策。
- 工具是否执行。
- 工具结果是什么。
- 是否发生错误。
- 当前任务是否更接近完成。
- 是否需要停止或请求用户介入。

状态更新不是为了“保存所有东西”，而是为了支持：

- 下一轮上下文组装。
- 失败调试。
- 任务恢复。
- 成功率评估。

最小 Agent 至少要能记录每一步的 trace。

### 3.7 Continue or Stop：继续或停止

每轮结束后，Runtime 都要判断是否继续。

常见判断包括：

- 模型是否给出最终答案？
- 是否达到最大步数？
- 是否重复调用同一工具且没有新进展？
- 是否遇到不可恢复错误？
- 是否需要用户确认？
- 是否命中风险规则？

如果继续，就重新进入 Context Assembly。

如果停止，就输出最终答案或失败原因。

---

## 第四章：运行时循环总览

### 4.1 最小闭环图

可以把最小 Agent 看成一个不断推进的控制循环：

```text
User Goal -> Context Assembly -> LLM Decision -> Interaction -> Execution
                ^                                               |
                | read                                          v
       +-----------------------+                    Observation / Feedback
       | State / Memory Store  |                                |
       | task state, history,  |                                v
       | optional persistence  | <----------------------   State Update
       +-----------------------+          write                 |
                                                                v
                                                         Continue or Stop
```

这张图有三层含义：

- 主链路：目标如何一步步推进到执行和反馈。
- 状态读写：上下文从状态中读取，执行结果写回状态。
- 反馈闭环：每轮 Observation 都会影响下一轮决策。

### 4.2 State / Memory Store 的位置

图里的 `State / Memory Store` 不在主链路上，而在旁边。

这是有意设计的。

状态存储不是一个“独立行动步骤”，而是被两个环节读写：

- Context Assembly 从状态中读取信息。
- State Update 把新信息写回状态。

在最小 Agent 中，State / Memory Store 可以只是一个内存对象、JSON 文件或数据库记录。

这里的 Memory 不等于课程五要讲的长期 Memory。它首先表示任务运行状态和历史记录。

### 4.3 Context Assembly 和 Observation 为什么不是额外核心模块

前面公式是：

```text
Agent = LLM 决策 + 工具/环境交互 + 状态管理 + 循环控制
```

你可能会问：

```text
那 Context Assembly 和 Observation / Feedback 算不算核心模块？
```

它们非常重要，但它们更像运行时连接点。

Context Assembly 是状态管理和 LLM 决策之间的连接点：

```text
状态里有什么 -> 选择什么进入上下文 -> 模型据此决策
```

Observation / Feedback 是工具交互和状态管理之间的连接点：

```text
工具执行结果 -> 转成模型可理解的信息 -> 写回状态 -> 进入下一轮上下文
```

所以它们和核心公式并不冲突。

### 4.4 最小闭环背后的工程原则

最小闭环背后有一个重要工程原则：

```text
模型负责理解目标和做下一步判断；
确定性基础设施负责工具执行、权限、安全、状态、恢复和观测。
```

不要把所有问题都交给模型。

例如：

- 参数类型校验应该由代码做。
- 最大步数应该由 Runtime 控制。
- 工具是否存在应该由工具注册表判断。
- 文件是否允许写入应该由权限系统判断。
- 错误记录和 trace 应该由系统保存。

模型越强，这个原则越重要。强模型可以提升上限，确定性基础设施保证下限。

---

## 第五章：沿运行链路展开学习

### 5.1 每个运行环节要解决的问题

| 运行环节 | 作用 | 本课要掌握的问题 |
|---|---|---|
| State / Memory Store | 保存任务状态和历史 | 保存什么、何时读取、何时写入 |
| Context Assembly | 组装模型输入 | 哪些信息进入上下文，哪些不进入 |
| LLM Decision | 判断下一步 | 输出什么结构，如何表达工具调用或停止 |
| Tool / Environment Interaction | 选择工具或环境动作 | 工具名和参数如何被表达 |
| Execution | 执行工具或动作 | 如何校验、超时、捕获错误 |
| Observation / Feedback | 整理执行结果 | 如何把结果转成下一轮可用信息 |
| State Update | 写回状态 | 如何记录历史、错误、中间结果 |
| Continue or Stop | 控制循环 | 如何继续、停止、重试或失败退出 |

这些环节会在后续课程中继续深化。

### 5.2 最小 Agent 不必包含哪些能力

为了避免一开始就过度复杂化，需要明确最小 Agent 不必包含：

- 不必有 RAG。
- 不必有长期 Memory。
- 不必有复杂 Planning。
- 不必有 Multi-Agent。
- 不必接入 MCP。
- 不必有完整权限平台。
- 不必有线上级 Observability。

这些能力都重要，但不是最小闭环的前提。

最小 Agent 的目标是先让闭环跑起来，再逐步增强。

### 5.3 从最小闭环走向后续课程

课程三和后续课程的关系如下：

| 后续课程 | 与本课的关系 |
|---|---|
| 课程四：工具机制 | 深入本课的工具/环境交互部分 |
| 课程五：场景增强能力 | 在最小闭环上判断是否需要 RAG、Memory、Planning、Reflection、Multi-Agent |
| 课程六：Harness 运行时架构 | 把本课的概念循环工程化为可追踪、可恢复、可评测的 Runtime |
| 课程七：产品化实践 | 解决用户信任、失败恢复、成本、安全和指标问题 |

所以课程三不是“一个简单 demo”，而是整条路线的技术地基。

---

## 第六章：最小 ReAct Agent 的实现思路

### 6.1 推荐最小技术栈

本课不绑定具体框架。

推荐原则是：

- 使用自己熟悉的语言，例如 Python、TypeScript 或 JavaScript。
- 直接调用任意 LLM API。
- 工具先用本地函数实现。
- 状态先用内存对象或 JSON 文件。
- Trace 先写到控制台或本地文件。
- 不要一开始引入复杂 Agent 框架。

框架可以提高效率，但会隐藏关键结构。第一次学习最小闭环时，最好先亲手理解每个环节。

### 6.2 伪代码结构

下面是一个最小 Agent Loop 的伪代码，不绑定任何语言或 SDK。

```text
initialize state with user_goal

while not stopped:
    context = assemble_context(state, tools)

    decision = call_llm(context)

    if decision.type == "final_answer":
        state.stop_reason = "completed"
        return decision.answer

    if decision.type == "ask_user":
        state.stop_reason = "need_user_input"
        return decision.question

    if decision.type == "fail":
        state.stop_reason = "failed"
        return decision.reason

    if decision.type == "call_tool":
        validation = validate_tool_call(decision.tool_name, decision.arguments)

        if validation.failed:
            observation = make_error_observation(validation.error)
        else:
            observation = execute_tool(decision.tool_name, decision.arguments)

        update_state(state, decision, observation)

    if should_stop(state):
        return make_stop_response(state)
```

这段伪代码体现了几个关键点：

- LLM 只做决策，不直接执行工具。
- Runtime 校验工具调用。
- 工具结果变成 Observation。
- 每轮都更新状态。
- 每轮都检查停止条件。

### 6.3 工具设计

最小 Agent 建议从 3 个工具开始。

示例组合：

| 工具 | 输入 | 输出 | 用途 |
|---|---|---|---|
| `read_file` | 文件路径 | 文件内容或错误 | 读取用户指定资料 |
| `write_file` | 文件路径、内容 | 写入成功或错误 | 生成交付物 |
| `search_text` | 关键词、文本集合 | 匹配片段 | 在资料中查找信息 |

工具返回结果应该结构化。

例如：

```text
status: success
summary: "读取到 1200 字 Markdown 内容"
content: "...可选，可能较长..."
error: null
```

失败时：

```text
status: error
summary: "文件不存在"
content: null
error:
  code: file_not_found
  message: "未找到 notes.md"
```

这样模型能在下一轮明确知道发生了什么。

### 6.4 Trace 记录

Trace 是最小 Agent 的调试基础。

每一步至少记录：

- step number。
- context summary。
- model decision。
- tool call。
- observation。
- state update。
- stop check result。

示例：

```text
step: 2
decision:
  type: call_tool
  tool: read_file
  arguments:
    path: notes.md
observation:
  status: error
  summary: "文件不存在"
state_update:
  errors_count: 1
stop_check:
  continue: true
  reason: "可以请求用户修正路径"
```

没有 Trace 的 Agent 很难调试。你只会看到最终失败，却不知道是哪一步错了。

### 6.5 基础错误处理

最小 Agent 至少要处理这些错误：

| 错误 | 处理方式 |
|---|---|
| 工具不存在 | 返回结构化错误，不执行 |
| 参数不合法 | 返回参数错误，让模型修正或请求用户 |
| 工具执行失败 | 记录错误，允许有限重试 |
| 环境不可用 | 停止或降级 |
| 模型输出无法解析 | 请求模型重新输出或失败退出 |
| 超过最大步数 | 停止并说明原因 |
| 重复动作无进展 | 停止或请求用户介入 |

错误处理不是后续才需要。最小闭环如果没有错误处理，测试任务稍微复杂就会失控。

### 6.6 测试任务设计

用 10 条任务测试最小 Agent。

建议任务集包含：

| 类型 | 示例 |
|---|---|
| 成功路径 | 读取一个文件并总结 |
| 多步任务 | 读取文件、提取要点、写入新文件 |
| 参数错误 | 用户给出不存在的文件路径 |
| 工具失败 | 模拟 API 返回错误 |
| 需要澄清 | 用户目标不完整 |
| 循环控制 | 工具反复失败时能停止 |
| 结果验证 | 输出必须包含指定字段 |
| 状态延续 | 第二步要使用第一步工具结果 |
| 写操作 | 写入本地结果文件 |
| 安全边界 | 尝试执行不允许的动作时拒绝 |

成功率达到 70% 以上是一个初步目标。更重要的是：失败时要知道为什么失败。

---

## 课后练习

### 练习一：画出最小 Agent 闭环

用自己的话画出以下链路：

```text
User Goal -> Context Assembly -> LLM Decision -> Tool / Environment Interaction -> Observation / Feedback -> State Update -> Continue or Stop
```

要求：

- 标出状态从哪里读取。
- 标出状态在哪里写入。
- 标出工具结果如何影响下一轮决策。
- 标出停止条件在哪里发生。

### 练习二：设计一个最小 Agent 状态对象

为“读取文件并生成摘要”这个任务，设计一个最小状态对象。

至少包含：

- 用户目标。
- 当前步骤数。
- 最大步骤数。
- 历史决策。
- 工具结果。
- 错误列表。
- 停止原因。

### 练习三：设计 3 个工具

为你的最小 Agent 设计 3 个工具。

每个工具写清楚：

- 工具名。
- 工具用途。
- 输入参数。
- 输出结构。
- 可能失败的情况。
- 风险等级。

### 练习四：写出最小循环控制规则

为你的 Agent 写出至少 5 条循环控制规则，例如：

- 最大步数为 8。
- 同一个工具连续失败 2 次后停止。
- 模型输出无法解析时最多重试 1 次。
- 写文件前需要确认。
- 最终答案必须包含任务完成说明和停止原因。

### 练习五：完成 10 条测试任务设计

按照第六章的任务类型，设计你的 10 条测试任务。

每条任务写清楚：

- 用户输入。
- 期望工具调用。
- 成功标准。
- 可能失败点。

### 交付物

完成本课后，建议沉淀以下材料：

1. 一张最小 Agent 闭环图。
2. 一个最小状态对象设计。
3. 三个工具定义。
4. 一份循环控制规则。
5. 十条测试任务。
6. 一份最小 Agent 实现方案说明。

---

## 验收标准

完成本课后，请用以下标准自检：

- [ ] 我能解释为什么最小 Agent 不能只有 LLM。
- [ ] 我能说出 `LLM 决策 + 工具/环境交互 + 状态管理 + 循环控制` 四部分各自负责什么。
- [ ] 我能画出最小运行链路，并解释每个环节的作用。
- [ ] 我能区分状态管理和长期 Memory。
- [ ] 我能解释 Context Assembly 和 Observation / Feedback 为什么不是额外核心模块。
- [ ] 我能设计一个最小状态对象和 3 个工具。
- [ ] 我能写出最小循环控制规则。
- [ ] 我能设计 10 条测试任务，并定义成功标准。
- [ ] 我知道课程四、五、六分别会在本课基础上扩展什么。

---

## 参考资料

### 推荐阅读

- ReAct: Synergizing Reasoning and Acting in Language Models  
  <https://arxiv.org/abs/2210.03629>
- OpenAI Function Calling  
  <https://platform.openai.com/docs/guides/function-calling>
- Anthropic Tool Use  
  <https://docs.anthropic.com/en/docs/agents-and-tools/tool-use>
- Anthropic Building Effective Agents  
  <https://www.anthropic.com/engineering/building-effective-agents>
- LangGraph 文档  
  <https://langchain-ai.github.io/langgraph/>

