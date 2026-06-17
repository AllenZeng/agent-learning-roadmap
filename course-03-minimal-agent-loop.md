# 课程三：最小 Agent 闭环

## 课程导言

课程一让你看见 Agent 产品的真实形态，课程二解释了 Agent 范式为什么会演进到今天。到了课程三，学习的重心从"理解概念"转入"掌握结构"。

这一课要回答一个非常具体的问题：

```text
一个最小但完整的 Agent，到底由什么组成？
```

很多学习者会掉进两个误区。第一个误区是把 Agent 想成"一个更强的 LLM"——以为只要模型足够强，Agent 就会自动可靠。第二个误区是反过来——以为必须把 RAG、Memory、Planning、MCP、Multi-Agent 全部加上才算 Agent。

这两个判断都不准确。

第一个误区的问题在于：LLM 本质上是一个"下一个 Token 预测器"。它可以在语言空间内做惊人的推理，但它不能自己查数据库、不能自己运行代码、不能自己判断"我已经做了几步、下一步该做什么"。把 Agent 等同于更强的 LLM，就像把一个人等同于更聪明的大脑——大脑是核心，但没有手、没有眼睛、没有记忆、没有判断什么时候该停的机制，这个人什么也完成不了。

第二个误区的问题在于：那些能力确实重要，但它们不是 Agent 存在的**前提**，而是 Agent 在特定方向上的**扩展**。就像一个人不需要先成为运动员才能走路，一个 Agent 不需要先接入 RAG 和 Multi-Agent 才能工作。

本课的核心观点是：

```text
Agent = Prompt（行为定义） + LLM 决策 + 工具/环境交互 + State（状态管理） + 循环控制
```

这个公式有五项，可以分成两层来看：**Prompt 是定义层**——它在循环启动前就决定了"这是个什么样的 Agent、它怎么思考、它怎么输出"；后面四项是**运行时层**——它们让 Agent 在循环中真正运转起来。

这个公式不是要定义所有 Agent 产品的全部能力，而是要抓住"最小闭环"——能跑起来、能完成多步任务、能受控停止的最简结构。后续课程中的工具机制、RAG / Memory、Planning / Workflow Patterns、Harness、Evaluation、Guardrails，都是围绕这个闭环继续扩展。

课程三只解决一件事：**让你真正理解并能实现一个最小可运行 Agent**。

---

## 学习目标

学完本课，你将能够：

1. **解释最小 Agent 为什么不能只有 LLM** — 理解 LLM 的本质局限，包括它不知道自己是一个 Agent
2. **画出最小 Agent 运行链路** — 说清 `Prompt → User Goal → Context Assembly → LLM Decision → Interaction → Observation → State Update → Continue or Stop`
3. **理解 Prompt 在 Agent 中的角色** — 知道为什么 Prompt 是 Agent 的"源代码"，它定义了 Agent 的行为、格式和边界
4. **区分核心模块与连接点** — 明白为什么 Context Assembly、Observation 是连接环节而非核心模块
5. **理解 State（状态）管理的角色** — 知道哪些信息需要独立于 LLM 存储，以及为什么上下文窗口不能作为唯一的 State 存储
6. **设计循环控制规则** — 包括停止条件、最大步数、超时、重复检测和失败退出
7. **规划最小 ReAct Agent 的实现** — 能定义 Prompt、工具、状态、Trace、错误处理和测试任务

本课围绕的核心问题：

- 一个最小 Agent 为什么不能只有 LLM？
- Prompt、LLM 决策、工具交互、状态管理、循环控制各自解决什么？
- 运行链路如何把它们串成闭环？
- 从最小闭环出发，后续课程会向什么方向扩展？

---

## 目录

- [课程导言](#课程导言)
- [学习目标](#学习目标)
- [第一章：为什么最小 Agent 不能只有 LLM](#第一章为什么最小-agent-不能只有-llm)
  - [1.1 LLM 的本质：一个极强的"下一个 Token 预测器"](#11-llm-的本质一个极强的下一个-token-预测器)
  - [1.2 LLM 会说，但不会做](#12-llm-会说但不会做)
  - [1.3 LLM 会判断，但不会记住](#13-llm-会判断但不会记住)
  - [1.4 LLM 能推理，但不能控制自己的边界](#14-llm-能推理但不能控制自己的边界)
  - [1.5 LLM 是通用引擎，但不知道自己是 Agent](#15-llm-是通用引擎但不知道自己是-agent)
- [第二章：最小 Agent 组成](#第二章最小-agent-组成)
  - [2.1 核心公式](#21-核心公式)
  - [2.2 Prompt：行为定义](#22-prompt行为定义)
  - [2.3 LLM 决策](#23-llm-决策)
  - [2.4 工具/环境交互](#24-工具环境交互)
  - [2.5 状态管理](#25-状态管理)
  - [2.6 循环控制](#26-循环控制)
- [第三章：最小运行链路](#第三章最小运行链路)
  - [3.1 最小闭环图](#31-最小闭环图)
  - [3.2 环节总览：一条链路串起五个组成部分](#32-环节总览一条链路串起五个组成部分)
  - [3.3 Prompt Engineering：Agent 的"源代码"](#33-prompt-engineeringagent-的源代码)
  - [3.4 User Goal：从模糊意图到可操作目标](#34-user-goal从模糊意图到可操作目标)
  - [3.5 Context Assembly：模型应该看到什么](#35-context-assembly模型应该看到什么)
  - [3.6 LLM Decision：下一步做什么](#36-llm-decision下一步做什么)
  - [3.7 Interaction & Execution：真的去做](#37-interaction--execution真的去做)
  - [3.8 Observation / Feedback：让结果回到循环](#38-observation--feedback让结果回到循环)
  - [3.9 State Update：把本轮发生的事写进 State](#39-state-update把本轮发生的事写进-state)
  - [3.10 Continue or Stop：知道什么时候该停](#310-continue-or-stop知道什么时候该停)
  - [3.11 State 存储的正确位置](#311-state-存储的正确位置)
  - [3.12 核心模块与连接点的区别](#312-核心模块与连接点的区别)
  - [3.13 最小闭环背后的工程原则](#313-最小闭环背后的工程原则)
- [第四章：从最小闭环看扩展方向](#第四章从最小闭环看扩展方向)
  - [4.1 每个环节分别会被什么能力增强](#41-每个环节分别会被什么能力增强)
  - [4.2 最小 Agent 不必一开始包含哪些能力](#42-最小-agent-不必一开始包含哪些能力)
  - [4.3 从最小闭环走向后续课程](#43-从最小闭环走向后续课程)
- [第五章：最小 ReAct Agent 的实现思路](#第五章最小-react-agent-的实现思路)
  - [5.1 为什么第一次实现不建议用框架](#51-为什么第一次实现不建议用框架)
  - [5.2 伪代码结构](#52-伪代码结构)
  - [5.3 工具设计](#53-工具设计)
  - [5.4 Trace 记录](#54-trace-记录)
  - [5.5 基础错误处理](#55-基础错误处理)
  - [5.6 测试任务设计](#56-测试任务设计)
- [课后练习](#课后练习)
- [验收标准](#验收标准)
- [参考资料](#参考资料)

---

## 第一章：为什么最小 Agent 不能只有 LLM

在课程二中，我们讲过 LLM 是 Agent 的决策核心，但不是完整 Agent 系统。这一章把这个结论拉到更近的距离，让你具体看到：**如果只靠 LLM，一个看起来像 Agent 的系统会在哪里卡住。**

理解这个问题的关键，不是贬低 LLM 的能力，而是准确认识 LLM 的本质。它的本质决定了它天然擅长什么、天然不擅长什么——而 Agent 系统就是在不擅长的方向上给 LLM 装上"假肢"。

### 1.1 LLM 的本质：一个极强的"下一个 Token 预测器"

LLM 无论规模多大、推理多强，它的基本工作机制没有变：根据前面的文本，预测下一个最可能的 Token。

这个机制造就了它惊人的能力——它能理解复杂指令、写出优美的文章、在数学题上一步步推导。但它也划定了 LLM 能力的天然边界：**它只能在语言空间内活动。** 它输出的永远是文本，它"知道"的永远来自训练数据，它"记住"的永远只是当前上下文窗口里的内容。

用课程二的语言来说：LLM 的内部推理很强，但它缺乏系统外部反馈。而 Agent 恰恰需要持续地和外部世界交互——获取新信息、执行动作、观察结果、调整策略。这些都是"生成下一段文本"这个动作本身做不到的。

### 1.2 LLM 会说，但不会做

假设你对一个纯 LLM 系统说：

```text
帮我检查这个项目为什么测试失败。
```

它可能回答：

```text
你可以先运行测试命令，查看错误日志，再定位相关文件。
```

这段回答可能完全正确，但它只是**建议**，不是**行动**。模型没有真的运行测试，没有读取日志，没有检查代码。它就像一个被困在房间里的人，可以告诉你外面的世界应该怎么运作，但无法伸手去触碰任何东西。

如果要成为 Agent，系统至少要能：
- 读取项目文件。
- 执行测试命令。
- 接收测试结果。
- 根据错误信息决定下一步。
- 在必要时停止或请求用户介入。

每一项都需要"生成文本"之外的机制——需要有人去真正执行动作，并把结果拿回来。

### 1.3 LLM 会判断，但不会记住

LLM 的"记忆"完全依赖上下文窗口中的文本。它本身没有任何持久化的内部状态——每次调用都是"第一次见面"。

这对多步任务来说是个硬伤。假设一个任务需要 5 步完成，每一步的工具返回结果都挺长。到第 4 步时，上下文窗口可能已经被前 3 步的结果塞得差不多了。更糟的是，研究已经发现 LLM 对上下文中间位置的信息关注度显著低于开头和结尾——这就是"Lost in the Middle"现象。用户在任务开始时说的"所有操作都不要动生产环境"，如果恰好落在上下文的"中间地带"，Agent 可能会在执行到第 5 步时忘记它。

所以 Agent 不能只靠"把历史塞进上下文"来管理状态。它需要一个独立于 LLM 的状态存储，由 Runtime 管理——该保留的保留，该压缩的压缩，该注入的注入。这就是状态管理要做的事。

> 读到这你可能会问——**Runtime 到底是什么？** 前面反复提到它：状态要它管、工具要它执行、循环要靠它控制。你可以把 Runtime 理解为 Agent 的**操作系统**。就像操作系统管理 CPU、内存、磁盘、进程调度——但它不帮你写文档、做表格；Runtime 管理状态存储、工具执行、循环控制、权限校验、Trace 记录——但它不做语义推理、不生成文本。

> 更准确地说：**Agent 架构中，所有承担"确定性职责"的部分都属于 Runtime。** LLM 的输出是不确定的（同样的 prompt 两次调用结果可能不同），但工具是否执行、参数是否合法、步数是否超限——这些判断必须是确定的、可审计的。Runtime 就是承担这些确定性职责的那层基础设施。你会在后续每一课中反复看到它——课程四中它是工具的注册和权限中心，课程五中它是 Memory 的读写入口，课程六中它是 Harness / 可观测性的骨架，课程七中它是故障恢复和安全策略的执行点。

### 1.4 LLM 能推理，但不能控制自己的边界

LLM 天然倾向于"继续生成"。它不知道什么时候该停，不知道什么时候该请求帮助，不知道什么时候自己的行为已经变成了死循环。

如果你让一个纯 LLM 系统在循环中工作，它可能：
- 一直重复调用同一个工具，因为每次看到类似的上下文，它就做出类似的决策。
- 遇到错误后无限重试，因为它不知道"放弃"也是一个合理选择。
- 在任务已经完成后继续多余操作，因为它没有"完成"的概念——它只是在生成下一个 Token。
- 在不确定时仍然执行高风险动作，因为它没有"风险判断"能力——它看到的是一个概率分布，而不是后果。

所以 Agent 不能只依赖 LLM 的"判断"来管理自己的运行边界。循环控制必须由 Runtime 负责——Runtime 设定硬约束（最大步数、超时、重复检测），LLM 在约束内做决策。这不是不信任模型，而是把"决策"和"执行边界"分给最适合它们的角色。

### 1.5 LLM 是通用引擎，但不知道自己是 Agent

前面三个局限——不能做、不能记、不能控——讲的都是 LLM 的**能力边界**。但还有一个更根本的问题：LLM 的**身份边界**。

LLM 出厂时是一个通用文本生成器。它被训练来"续写文本"，不是"完成多步任务"。如果你直接对一个裸 LLM 说"帮我查一下今天天气，然后根据天气建议穿什么"，它不会自动去调用天气 API、分析结果、再给出建议——它只会生成一段看起来像建议的文本。

ReAct 论文的作者做了一个关键实验来证明这一点：同一个 frozen PaLM-540B 模型，**不写 Prompt 直接问问题和用 ReAct Prompt 格式化后再问，表现天差地别**。不是模型变强了——是 Prompt 告诉了模型它应该怎么表现。

```text
没有 Prompt：LLM → 生成一段文本（可能是建议、可能是答案、可能是胡编）
有 Prompt：  LLM → 知道自己要 Thought → Action → Observation 循环
```

Prompt 解决的正是这个问题：**把通用引擎变成一个特定类型的 Agent。** 它定义了三件事：

- **角色**：你是谁、你的目标是什么
- **行为协议**：你怎么思考（Thought）、怎么行动（Action）、怎么处理结果（Observation）
- **输出格式**：你的每一步输出应该长什么样，以便 Runtime 能可靠解析

换句话说，前三个局限是"LLM 缺了什么能力"的问题，这个局限是"LLM 不知道自己该扮演什么角色"的问题。四个问题合在一起，指向了最小 Agent 的五个组件——Prompt 定义"做什么样的 Agent"，后面四个组件让 Agent 真正运转起来。

---

## 第二章：最小 Agent 组成

上一章讲了 LLM 四个"不能"——不能做、不能记、不能控、不知道自己是 Agent。这一章把每个"不能"对应到一个具体的系统组件上。这五个组件合在一起，就是最小 Agent 的骨架。

### 2.1 核心公式

```text
Agent = Prompt（行为定义） + LLM 决策 + 工具/环境交互 + State（状态管理） + 循环控制
```

五个部分缺一不可。这个公式不是说所有 Agent 只能有这五个部分，而是说：**如果连这五个都没有，就不能算一个最小完整 Agent。**

这五项可以分成两层来看：

| 层次 | 组件 | 角色 |
|------|------|------|
| **定义层**（静态） | Prompt | 定义 Agent 的身份、行为规则和输出格式——"这是个什么样的 Agent" |
| **运行时层**（动态） | LLM 决策 | Agent 的"大脑"——每轮判断下一步做什么 |
| | 工具/环境交互 | Agent 的"手和眼"——真正去执行动作、获取外部信息 |
| | State 管理 | Agent 的"记忆"——记录已经做了什么、现在在哪一步 |
| | 循环控制 | Agent 的"自律"——判断继续还是停止 |

Prompt 排在第一位，不是因为最重要，而是因为因果顺序：**先定义 Agent 是什么，它才能开始运转。** Prompt 是循环启动的前提——就像程序必须先写出来，CPU 才能执行。

| 组成 | 解决 LLM 的哪个局限 | 如果缺失会怎样 |
|---|---|---|
| Prompt（行为定义） | "不知道自己是 Agent" | LLM 不知道自己该扮演什么角色、遵循什么协议 |
| LLM 决策 | —（这是被增强的对象） | 系统无法理解开放目标 |
| 工具/环境交互 | "会说不会做" | 系统只能说，不能做 |
| 状态管理（State） | "会判断不会记" | 系统无法连续工作，忘记前面做了什么 |
| 循环控制 | "能推理不能控边界" | 系统容易失控、死循环、或无法完成多步任务 |

这五个组成部分不是五块独立的积木。它们通过运行链路连接在一起，形成闭环。在讲运行链路之前（第三章），我们先逐个理解每个组成部分负责什么。

### 2.2 Prompt：行为定义

> **术语标注：Prompt** 在 Agent 语境下不是"随便写一段提示词"。它是一份结构化的**行为定义文档**——定义了 Agent 的身份、推理协议、可用工具、输出格式和边界行为。后续课程中，多 Agent 系统（课程五）的每个 Agent 有各自的 Prompt（角色定义），Prompt 的版本管理和评测（课程六）也是围绕这份"源代码"展开的。**请在本节建立对 Prompt 的准确理解：它是 Agent 的"程序"，不是"备注"。**

Prompt 解决的核心问题是：**LLM 是通用引擎，不知道自己是 Agent。** 你必须明确告诉它——你是谁、你要怎么思考、你能用什么工具、你的输出必须长什么样。

在最小 Agent 中，Prompt 通常包含以下几个层次（3.3 节会逐一展开）：

| 层次 | 内容 | 回答的问题 |
|------|------|-----------|
| 身份层 | System prompt：角色描述、总体目标 | "我是谁？" |
| 协议层 | Thought/Action/Observation 循环格式 | "我怎么思考和行动？" |
| 工具层 | 可用工具的名称、用途、参数、调用格式 | "我能用什么？" |
| 约束层 | 输出格式要求、停止条件、安全边界 | "我有什么限制？" |
| 示例层 | Few-shot 示例，教会模型边界行为 | "遇到这种情况怎么办？" |

一个关键的工程判断：**Prompt 不是"写一次就忘了"的东西。** 它是 Agent 行为的唯一定义来源。当 Agent 表现不符合预期时，第一个要排查的就是 Prompt——是不是角色定义模糊？是不是工具描述让模型产生了歧义？是不是缺少了某个边界情况的示例？好的 Prompt 是迭代出来的，不是一次性写对的。

Prompt 和后面要讲的 Context Assembly（3.5 节）是上下游关系：**Prompt 是静态模板（框架），Context Assembly 是动态填充（数据）。** 每轮循环中，Context Assembly 把当前 State（目标、历史、工具结果）填入 Prompt 模板，生成 LLM 实际看到的完整上下文。

### 2.3 LLM 决策

LLM 决策是 Agent 的"大脑"。它的职责是回答一个每次循环都要面对的问题：

```text
基于当前上下文和状态，下一步应该做什么？
```

具体来说，模型需要判断：
- 用户目标到底是什么？（可能需要从模糊描述中提炼）
- 当前已经知道什么？还缺什么？
- 下一步是调用工具、给出答案、请求用户补充、还是承认失败？
- 如果调用工具，是哪个工具？参数是什么？
- 当前任务是否已经完成？

在最小 Agent 中，LLM 决策通常应该输出结构化结果，而不是任意自然语言。例如：

```text
decision_type: call_tool
tool_name: read_file
arguments:
  path: notes.md
reason: 需要读取用户指定文档才能完成总结任务
```

为什么强调结构化？因为 Runtime 需要明确知道模型想做什么，才能决定是否允许执行。如果模型输出的是自然语言"我觉得应该读一下那个文件"，Runtime 很难可靠地解析意图——每个人的表达方式不同，同一个模型在不同时间也可能换一种说法。结构化输出把这个模糊性消除了。

这里有一条重要的工程原则，它会贯穿整个课程：

```text
模型负责提出下一步，Runtime 负责判断能不能执行。
```

模型擅长理解语义和做决策，但它不应该有最终执行权。执行权留在 Runtime 手中，Runtime 可以校验工具是否存在、参数是否合法、操作是否在安全边界内。这不是不信任模型——这是把"决策"和"授权"分开。

### 2.4 工具/环境交互

工具/环境交互是 Agent 的"手"和"眼"。

工具让 Agent 可以：读取文件、写入文件、查询 API、执行代码、搜索资料、查询数据库、访问业务系统。

环境反馈让 Agent 可以知道：工具是否成功、返回了什么结果、是否发生错误、下一步是否需要调整。

在最小 Agent 中，工具可以非常简单。你不需要一开始接入复杂工具平台。最小工具示例：

| 工具 | 用途 | 风险等级 |
|---|---|---|
| `read_file` | 读取本地文本文件 | 低 |
| `write_file` | 写入本地文件 | 中 |
| `search_text` | 在一组文本里搜索关键词 | 低 |
| `calculate` | 执行简单计算 | 低 |
| `fetch_api` | 调用一个公开 API | 中 |

一个关键的设计细节：**工具返回结果应该结构化，不能只是一个原始字符串。** 如果工具只返回"失败了"，模型无从判断应该换一个工具、调整参数、还是改变策略。如果工具返回了完整的错误码和原因，模型就可能做出更聪明的下一步决策。

课程四会深入讨论工具定义、选择、执行、权限和安全。本课只要求理解：工具是闭环中的外部交互点——它是模型从"语言空间"进入"真实世界"的唯一通道。

### 2.5 状态管理

> **术语标注：State（状态）** 是贯穿后续课程的核心概念。每次循环中，Runtime 维护的 `state` 对象记录了 Agent "已经做了什么、现在在哪一步、接下来还需要什么"。课程四的工具执行结果、课程五的 Memory 持久化、课程六的 Harness Trace、课程七的故障恢复，全部围绕 `state` 展开。**请在本节建立对 State 的准确理解。**

状态管理让 Agent 从"单轮问答"走向"多步任务执行"。它解决的核心问题是：**LLM 的上下文窗口不能也不应该成为唯一的 State（状态）存储。**

一个最小 Agent 至少要维护的 State 字段：
- 用户目标。
- 当前步骤数。
- 历史消息（或压缩后的摘要）。
- 已调用的工具及其结果。
- 中间结论和发现。
- 错误信息。
- 停止原因（如果已停止）。

这里有一个重要的概念区分：**State（状态）不等于长期 Memory。** 在本课中，State 主要指当前任务运行时需要保存的信息——它的生命周期是这个任务。长期 Memory 是跨任务、跨会话的信息积累（用户偏好、历史经验），是课程五的内容，不是最小闭环的必选项。

最小 State 对象可以长这样：

```text
# State 示例：一个结构化的运行时状态对象
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

State 管理的关键不是"存得多"，而是"下一轮决策需要什么就保存什么"。这是一个权衡——存少了，模型缺少决策依据；存多了，上下文窗口膨胀，模型注意力分散。好的 State 管理是在"信息充分"和"信息精简"之间找到平衡。

### 2.6 循环控制

循环控制决定 Agent 是否继续、何时停止。它是 Agent 的"自律"——没有它，Agent 就像一个不知道什么时候该收手的人。

最小循环控制至少包括：
- **最大步数**：硬上限，防止无限循环。
- **每步超时**：单次工具调用不能无限等待。
- **工具失败次数上限**：连续失败说明可能不是偶然问题。
- **重复动作检测**：连续调用同一工具且无新进展，应该停止或请求介入。
- **成功完成判断**：模型声明 final_answer 后，Runtime 确认可以结束。
- **失败退出判断**：遇到不可恢复错误时果断停止。
- **必要时请求用户**：不确定的动作、需要补充信息时，停下来问。

常见停止原因：
| 停止原因 | 说明 |
|---|---|
| `completed` | 任务已完成 |
| `max_steps_exceeded` | 超过最大步骤 |
| `tool_error_limit` | 工具连续失败 |
| `invalid_decision` | 模型输出无法解析或不合法 |
| `need_user_input` | 需要用户确认、补充信息或接管 |
| `unsafe_action` | 动作风险过高，不能自动执行 |

循环控制有一个容易被忽视的设计哲学：**"能停止"和"能继续"是一对必须同时解决的能力。** 一个只会继续不会停止的 Agent 会失控，一个太容易停止的 Agent 完不成任务。好的循环控制是在"不轻易放弃"和"及时止损"之间找到平衡。

---

## 第三章：最小运行链路

第二章讲了五个组成部分分别是什么——Prompt、LLM 决策、工具/环境交互、State 管理、循环控制。这一章回答它们怎么串成一条闭环。

我们换个讲法。先给你一张全景图——把整条链路画出来，标注 Prompt 的位置、Runtime 的边界、State 的位置、数据流动的方向。你对"每个环节在哪、谁管谁"建立起坐标系之后，再逐个环节深入。

### 3.1 最小闭环图

```text
┌────────────────────── Runtime（确定性基础设施）──────────────────────────────────┐
│                                                                               │
│  Prompt（行为定义：角色、规则、输出格式）                                          │
│      |                                                                        │
│      v                                                                        │
│  User Goal → Context Assembly → LLM Decision → Interaction → Execution        │
│                  ↑                                                 |          │
│                  │ read                                            v          │
│         +-----------------------+                      Observation / Feedback │
│         | State / Memory Store  |                                  |          │
│         | task state, history,  |                                  |          │
│         | optional persistence  | <-----------------------   State Update     │
│         +-----------------------+     write                        |          │
│                                                                    v          │
│                                                            Continue or Stop   │
│                                                                               │
│  Runtime 职责：工具执行 · 权限校验 · State 管理 · 循环控制 · Trace 记录             │
└───────────────────────────────────────────────────────────────────────────────┘
```

这张图有五层含义：
- **Prompt 在顶部（定义层）**：Prompt 是 Agent 的"源代码"，它在循环启动前就存在。它不在循环链路中——它不参与每步更新——但每轮 Context Assembly 都以它为模板，把动态数据填入其中。3.2 和 3.3 节会深入 Prompt 的结构设计。
- **闭合链路（上半部分）**：User Goal → Context Assembly → LLM Decision → Tool Execution → Observation → State Update → Continue or Stop ——这是每轮循环中数据流动的路径。
- **Runtime 承载（外框）**：整条链路运行在 Runtime 之上。工具不是 LLM 直接执行的，是 Runtime 执行的；循环不是在模型推理中停止的，是 Runtime 判断的；State 不是 LLM 自己记住的，是 Runtime 管理的。1.3 节中讲到的 LLM 和 Runtime 的分工——"模型做决策，Runtime 管执行和边界"——这张图就是它的可视化。
- **State 读写（左下框）**：Context Assembly 从 State 中读取，State Update 向 State 中写入。State 不在主链路上——它不是业务流程中的一步，而是 Runtime 维护的基础设施。
- **反馈闭环（右侧回路）**：每轮 Observation 都会通过 State Update 影响下一轮决策——这正是 ReAct 的核心思想：推理和行动在循环中互相喂给对方。

### 3.2 环节总览：一条链路串起五个组成部分

有了全景图，下面把链路按文字展开：

```text
Prompt（行为定义：静态模板，定义 Agent 的身份和协议）
    → User Goal（用户输入锚点）
    → Context Assembly（连接点：Prompt 模板 + State → LLM 的完整上下文）
    → LLM Decision（核心模块：决策大脑）
    → Tool / Environment Interaction → Execution（核心模块：手和眼）
    → Observation / Feedback（连接点：外部世界 → State 的桥梁）
    → State Update（写回 State）
    → Continue or Stop（核心模块：循环自律）
    → 如果继续，回到 Context Assembly
```

八个环节中，五个是核心组件（Prompt、LLM 决策、工具交互、State 管理、循环控制），两个是运行时连接点（Context Assembly、Observation / Feedback），一个是用户输入锚点（User Goal）。3.12 节会详细解释核心模块和连接点的区分。

Prompt 之所以放在链路的最前面，不是因为它"最重要"，而是因为它**定义了后面所有环节的行为规范**——LLM 根据 Prompt 中定义的协议来决策，工具列表通过 Prompt 告知模型，输出格式由 Prompt 约束。没有 Prompt，后面的链路只是空转。

下面逐个环节展开。

### 3.3 Prompt Engineering：Agent 的"源代码"

在第二章中，我们把 Prompt 定义为一个组件。这一节深入到 Prompt 的内部结构——它到底长什么样、每一层解决什么问题、怎么写才有效。

#### 3.3.1 为什么 Prompt 是 Agent 的"源代码"

回到 ReAct 论文。论文的核心贡献不是一个新模型架构，不是一个新训练方法，而是一个 **Prompt 设计**。作者用 frozen PaLM-540B（参数完全冻结，不做任何微调），通过精心设计的 few-shot Prompt，让模型展现出了"推理—行动—观察"的 Agent 行为。

```text
ReAct 的本质：Prompt Engineering 方法
  输入：用户问题 + 精心设计的 Prompt（含系统指令 + 6 个 few-shot 示例）
  模型：frozen PaLM-540B（没有微调、没有 RLHF、没有架构改动）
  输出：Thought → Action → Observation 交替轨迹
```

这意味着什么？**同一个模型，换一个 Prompt，就从"文本生成器"变成了"Agent"。** 这就是为什么把 Prompt 叫做 Agent 的"源代码"——它定义了程序的全部逻辑。LLM 是执行这个程序的通用引擎。

一个直觉类比：

| 概念 | 类比 |
|------|------|
| LLM | CPU（通用计算引擎，什么程序都能跑） |
| Prompt | 程序源代码（定义了做什么、怎么做、什么时候停） |
| Runtime | 操作系统（管理内存/State、调度工具/IO、控制执行边界） |
| Agent | 一个正在运行的程序实例 |

这个类比不是为了精确，而是为了建立直觉：**Prompt 不是你随手写给 LLM 的一段备注——它是你用自然语言写的"程序"。** 和其他程序一样，它需要设计、需要测试、需要迭代。

#### 3.3.2 Agent Prompt 的五层结构

一份完整的 Agent Prompt 通常包含五个层次。不是每份 Prompt 都必须五层齐全，但理解这五层能帮你建立 Prompt 设计的坐标系。

```
┌─────────────────────────────────────────────┐
│ 第一层：身份层（Identity）                    │
│ "你是一个……，你的目标是……"                    │
├─────────────────────────────────────────────┤
│ 第二层：协议层（Protocol）                    │
│ "你必须按照 Thought → Action → Observation  │
│  的格式来思考和行动"                          │
├─────────────────────────────────────────────┤
│ 第三层：工具层（Tools）                       │
│ "你可以使用以下工具：                          │
│  - read_file(path): 读取文件内容              │
│  - search_text(keyword): 搜索文本             │
│  - finish(answer): 输出最终答案"              │
├─────────────────────────────────────────────┤
│ 第四层：约束层（Constraints）                  │
│ "每步输出必须是合法 JSON"                      │
│ "任务完成后必须调用 finish"                    │
│ "不确定时请求用户确认，不要猜测"                 │
├─────────────────────────────────────────────┤
│ 第五层：示例层（Examples）                     │
│ "以下是一些示例，展示你应该如何工作：            │
│  [few-shot 示例 1]                           │
│  [few-shot 示例 2]"                          │
└─────────────────────────────────────────────┘
```

逐层展开：

**第一层：身份层（Identity）**

定义 Agent 的角色、专业领域和总体目标。这是 Prompt 的"入口"——它告诉模型在接下来的对话中应该扮演谁。

```text
你是一个专业的研究助手。你的目标是根据用户提供的信息，准确、高效地完成信息检索和总结任务。
```

身份层看似简单，但影响深远。如果你写"你是一个编程助手"vs"你是一个代码审查员"，模型在同样的问题面前会给出完全不同的回答风格和侧重点。身份层为后续所有行为提供了基调。

**第二层：协议层（Protocol）**

定义 Agent 的**行为协议**——它怎么思考、怎么行动、怎么处理反馈。这是 Prompt 中最关键的一层，因为它直接决定了 Agent 会不会"循环"。

```text
你必须按照以下格式交替进行思考和行动：

Thought: 分析当前情况，判断还需要什么信息，决定下一步做什么。
Action: 执行一个具体操作。格式为 tool_name(arguments)。
Observation: 操作的结果（由系统提供，你不需要生成这一行）。

重复 Thought → Action → Observation 直到任务完成。
任务完成后，输出 Final Answer。
```

协议层回答三个问题：
- **思考什么时候发生？** 每步行动之前。（还是只在关键节点？这决定了是 dense reasoning 还是 sparse reasoning）
- **行动怎么表达？** 工具名 + 参数，放在特定格式中，方便 Runtime 解析。
- **什么时候结束？** 调用 finish / 输出 Final Answer。

协议层一旦定了，后面的工具设计、循环控制、State 管理都要围绕它来配合。协议层是 Agent 架构的"接口定义"。

**第三层：工具层（Tools）**

告诉模型它有哪些工具可以用、每个工具的用途、参数和注意事项。

```text
你可以使用以下工具：

1. read_file(path: str) — 读取指定路径的文件内容。path 必须是合法文件路径。
2. search_text(keyword: str, text: str) — 在文本中搜索关键词，返回匹配的句子。
3. finish(answer: str) — 任务完成时调用，输出最终答案。调用此工具后对话结束。
```

工具层不只是"列出函数签名"。好的工具描述应该：
- 写清楚**什么时候该用这个工具**（用途说明）
- 写清楚**参数怎么填**（类型 + 含义 + 示例更好）
- 写清楚**可能的失败情况**（文件不存在、网络超时等），让模型有心理准备

工具层是 LLM 了解自己能做什么的唯一渠道。如果工具描述有歧义，模型就可能用错工具——不是模型不够聪明，是你的"文档"没写清楚。

**第四层：约束层（Constraints）**

定义 Agent 的行为边界——输出格式、停止条件、安全约束。

```text
约束：
- 每一步的输出必须是合法的 JSON 格式，包含 decision_type 和 reason 字段。
- 如果连续两次调用同一工具且结果无新信息，必须改变策略或请求用户帮助。
- 绝对不要删除文件，除非用户明确要求。
- 遇到不确定的情况，调用 ask_user 请求用户确认，不要猜测。
```

约束层体现了 Runtime 和 LLM 的分工原则：**Runtime 负责硬约束的执行（校验参数、阻断危险操作），Prompt 负责软约束的传达（告诉模型哪些行为是不被允许的，让它在决策时自觉遵守）。** 两层防护比单靠一层更可靠。

**第五层：示例层（Examples）**

通过 few-shot 示例教会模型它应该怎么表现。这是 ReAct 论文中最关键的发现之一。

```text
以下是一些正确工作的示例：

示例 1：
用户目标：读取 notes.md 并总结为 3 个要点
Thought 1: 我需要先读取 notes.md 的内容，然后根据内容生成总结。
Action 1: read_file("notes.md")
Observation 1: [文件内容为 "Agent 是一种能够自主执行多步任务的 AI 系统……"]
Thought 2: 我已经获得了文件内容。现在可以总结为 3 个要点。
Action 2: finish("1. Agent 的核心是 LLM 决策 + 工具交互…… 2. 状态管理…… 3. 循环控制……")
```

示例层解决的是协议层描述不到的边界行为——比如遇到错误时怎么重试、搜不到结果时怎么换关键词、不确定时怎么请求用户。这些边界行为用自然语言描述很啰嗦，用一个例子展示则非常直观。

示例不是越多越好。2-3 个高质量示例（覆盖正常路径 + 一个错误恢复场景）通常比 10 个简单示例更有效。

#### 3.3.3 五层的协作关系

五层不是五段孤立的文字。它们共同作用时，会产生"整体大于部分之和"的效果：

| 场景 | 起作用的层 |
|------|-----------|
| 用户提问，Agent 开始思考 | 身份层 + 协议层：知道自己是谁、应该按什么模式思考 |
| Agent 判断需要读取文件 | 工具层：知道 read_file 存在、知道它接受什么参数 |
| Agent 输出第一步决策 | 约束层 + 协议层：输出合法 JSON、符合 Thought/Action 格式 |
| 文件不存在，Agent 收到错误 | 示例层：few-shot 中展示了类似的错误恢复方式 |
| Agent 请求用户修正路径 | 约束层："不确定时请求用户确认" |

一个好的 Prompt 不会让某一层承担所有责任。身份层定义"谁"，协议层定义"怎么做"，工具层定义"用什么做"，约束层定义"不能做什么"，示例层定义"遇到边界情况怎么办"。

#### 3.3.4 Prompt 与 Context Assembly 的关系

你可能注意到，Prompt 中提到的"目标"和"历史"会在每次循环中变化。这就引出了 Prompt 和 Context Assembly 的分工：

```text
Prompt（静态模板）              Context Assembly（动态填充）
─────────────────────          ─────────────────────────
身份层："你是一个研究助手"        → 不变，每轮都一样
协议层："Thought → Action → …"  → 不变，每轮都一样
工具层：工具列表和描述             → 不变（除非运行时增减工具）
约束层：输出格式和安全规则          → 不变，每轮都一样
示例层：few-shot 示例              → 不变，每轮都一样
                                +
                                ← User Goal（从 State 读取）
                                ← 当前步骤数（从 State 读取）
                                ← 最近 N 步历史（从 State 读取）
                                ← 上轮工具结果（从 State 读取）
                                ← 错误信息（从 State 读取）
```

一句话总结：**Prompt 是框架，Context Assembly 是填充工。** Prompt 定义了"这是一个 ReAct Agent"，Context Assembly 告诉它"你现在做到第 3 步了，刚才 read_file 失败了，文件不存在"。

---

### 3.4 User Goal：从模糊意图到可操作目标

用户目标是 Agent 的起点。它可能是明确的（"读取 notes.md，总结成 5 个要点"），也可能是模糊的（"帮我整理一下这个目录"）。

目标的质量直接影响整个闭环的表现。一个过于模糊的目标（如"帮我优化这个项目"），LLM 在第一步决策时就没有足够的信息来判断"优化"指什么——性能？代码结构？可读性？它可能需要多轮试探才能搞清楚用户真正想要什么，甚至可能一路朝着错误的方向执行。一个过于宏大的目标（如"帮我重构整个代码库"），会超出最小闭环的能力边界——这种任务需要 Planning 拆解、需要 Memory 跨会话追踪、需要更完善的权限控制。

最小 Agent 的定位决定了它适合处理的目标类型：目标明确、边界清晰、验证标准可判断。这不是说 Agent 不能处理模糊目标，而是说**在第一次学习闭环时，先让变量可控**——当你知道目标是明确的，你就能把注意力集中在观察链路本身是否正常运转，而不是纠结"Agent 的行为到底是目标太模糊导致的，还是链路有 bug 导致的"。

换句话说，User Goal 在闭环中的角色是**锚点**——后续每一步决策都以它为参照：当前的动作是否在朝着目标推进？当前的结果是否离目标更近了？最终答案是否覆盖了目标的所有要求？如果这个锚点是模糊的，整个循环就会在不确定中漂移。

### 3.5 Context Assembly：模型应该看到什么

Context Assembly 决定哪些信息进入模型上下文。这不是一个简单的"把所有东西都塞进去"的操作——它是一个关键的**信息筛选和编排环节**。

它通常包含：
- 用户目标。
- 系统约束（角色、规则、安全边界）。
- 当前任务状态（到哪一步了、已经知道了什么）。
- 历史决策（最近的几个 Thought → Action → Observation 循环）。
- 最近工具结果（或压缩后的摘要）。
- 可用工具列表（工具名、用途、参数）。

这里有一个重要的工程判断：**不是所有历史信息都应该进入上下文。** 上下文窗口有限，且模型对中间位置的信息关注度更低。Context Assembly 需要做取舍——哪些信息对下一步决策至关重要、哪些可以摘要、哪些可以暂时省略。

最小 Agent 中可以先使用简单策略：

```text
系统指令 + 用户目标 + 最近 N 步历史原文 + 可用工具列表 + 当前状态摘要
```

课程六会进一步深入 Context Engineering。本课只要求理解 Context Assembly 在闭环中的位置：它是"状态存储"和"模型决策"之间的桥梁。

### 3.6 LLM Decision：下一步做什么

LLM Decision 是每轮循环的核心。模型根据组装好的上下文，输出一个结构化的"下一步决策"。

在最小 Agent 中，决策通常有以下几种类型：

| 决策类型 | 含义 | Runtime 行为 |
|---|---|---|
| `call_tool` | 调用工具 | 校验 → 执行 → 收集结果 |
| `final_answer` | 任务完成，输出最终结果 | 记录完成 → 返回答案 |
| `ask_user` | 需要用户补充信息或确认 | 暂停循环 → 等待用户 |
| `fail` | 无法继续，承认失败 | 记录失败原因 → 停止 |

模型决策不是最终执行。Runtime 仍然需要校验：工具是否存在、参数是否合法、是否超过权限、是否超过步数、是否应该请求用户确认。

### 3.7 Interaction & Execution：真的去做

当模型决定调用工具时，Runtime 接手执行。

执行环节包括：
- 校验工具名（这个工具存在吗？）。
- 校验参数（类型对吗？必填项都有吗？值在合法范围吗？）。
- 执行工具（真正去读文件、调 API、跑代码）。
- 捕获异常（文件不存在、网络超时、权限不足、返回格式异常）。
- 规范化返回结果（把原始结果整理成结构化的 Observation）。

一条实操经验：工具调用后的原始结果，**不应该不经处理就塞回模型**。尤其是结果很长时——比如读取了一个 5000 行的文件——直接把全文塞进上下文会挤占其他重要信息。最小 Agent 至少要做一个简单的截断或摘要。

### 3.8 Observation / Feedback：让结果回到循环

Observation 是工具执行的结果——它可能是文件内容、搜索结果、API 响应、错误信息、权限拒绝、或者用户确认。

Observation 的作用只有一个，但非常关键：**影响下一轮决策。** 如果 Agent 读取了一个文件但发现文件不存在，下一轮它应该请求用户修正路径，而不是继续假装文件存在。Observation 是"外部世界"和"模型推理"之间的信息通道——没有它，模型就是在盲猜。

一个真实的例子：

```text
Action: read_file("notes.md")
Observation: status=error, code=file_not_found, message="未找到 notes.md"
Next Decision: ask_user("没有找到 notes.md，请确认文件路径是否正确")
```

这就是闭环的意义：每一步的结果改变下一步的方向。

### 3.9 State Update：把本轮发生的事写进 State

> **State Update 是闭环中对 `state` 对象的写入操作**——每轮循环结束后，Runtime 将本轮决策和观察结果写回 `state`，供下一轮 Context Assembly 读取。

State Update 把本轮发生的事情记录到 State 中。它需要记录：
- 模型做了什么决策。
- 工具是否执行、结果是什么。
- 是否发生错误。
- 当前任务是否更接近完成。
- 是否需要停止或请求用户介入。

State Update 的目的不是"存档"，而是支持三个关键需求：
1. **下一轮 Context Assembly**：下一轮需要知道本轮发生了什么（从 State 中读取）。
2. **失败调试**：任务失败时，State 历史是唯一的问题排查依据。
3. **任务恢复**：如果任务中断，State 可以用于恢复。

最小 Agent 至少要能记录每一步的 Trace。Trace 不需要很复杂——一个包含步骤号、决策内容、工具结果、停止判断的结构化记录就足够了。

### 3.10 Continue or Stop：知道什么时候该停

每轮结束后，Runtime 必须判断：继续还是停止？

判断依据包括：
- 模型是否给出 final_answer？
- 是否达到最大步数？
- 是否重复调用同一工具且没有新进展？
- 是否遇到不可恢复错误？
- 是否需要用户确认或补充信息？
- 是否命中风险规则？

如果继续，就重新进入 Context Assembly——用更新后的状态组装新的上下文，开始下一轮循环。如果停止，就输出最终答案或失败原因。

以上八个环节走完，你对闭环的"数据流动"已经有了完整的认知。下面三节（3.11-3.13）不再引入新环节，而是对闭环中三个最容易被误解的点做更深的分析：State 为什么放在图旁边而不是链路中？Prompt 和 Context Assembly 为什么一个算核心组件一个算连接点？整条链路背后统一的工程原则是什么？

### 3.11 State 存储的正确位置

图里的 `State / Memory Store` 不在主链路上，而在旁边。这是有意设计的。

State 存储不是一个"独立行动步骤"——Agent 不会在某一步说"现在我要操作 State"。State 被两个环节读写：
- **Context Assembly** 从 State 中**读取**信息（当前进度、历史决策、工具结果）。
- **State Update** 把新信息**写入** State（刚刚发生的事、刚刚得到的结果）。

把 State 放在主链路旁边而不是其中，是为了强调：State 是基础设施，不是业务流程中的一步。

在最小 Agent 中，State 可以只是一个内存对象或 JSON 文件。不需要数据库，不需要向量存储。这里的 Memory 不等于课程五要讲的长期 Memory——它首先是当前任务的运行时 State。

### 3.12 核心模块与连接点的区别

你可能已经注意到，运行链路中有几个环节没有出现在核心公式里：Context Assembly、Observation / Feedback。而 Prompt 虽然出现在核心公式中，但它的性质和其他四个运行时模块不同。

先看核心公式中的五个组件：

| 组件 | 类型 | 说明 |
|------|------|------|
| **Prompt** | 定义层核心 | 静态模板：定义 Agent 的身份、协议、工具、约束。不在循环中更新，但每轮被 Context Assembly 消费 |
| **LLM 决策** | 运行时核心 | 动态：每轮根据上下文判断下一步做什么 |
| **工具/环境交互** | 运行时核心 | 动态：执行模型决定的工具调用 |
| **State 管理** | 运行时核心 | 动态：记录和查询任务运行时的状态信息 |
| **循环控制** | 运行时核心 | 动态：每轮结束后判断继续还是停止 |

Prompt 的特殊之处在于：它是**静态的**——它不在循环中更新，不像 State 每轮追加、不像 LLM 决策每轮变化。但它仍然是核心组件，因为它定义了所有运行时模块的行为规范。没有 Prompt，LLM 不知道自己是 Agent，Runtime 不知道模型输出应该是什么格式。

再看连接点：

Context Assembly 是 Prompt 模板、State 管理和 LLM 决策之间的连接点：

```text
Prompt 模板 + State 里的动态数据 → 组装成完整上下文 → 模型据此决策
```

Observation / Feedback 是工具交互和 State 管理之间的连接点：

```text
工具执行结果 → 转成模型可理解的信息 → 写回 State → 进入下一轮上下文
```

这个区分不是咬文嚼字。它的工程含义是：这些连接点会随着系统复杂度增长而显著变化（上下文管理策略会变、反馈信号的种类和来源会变），但五个核心组件的职责边界相对稳定。把连接点和核心组件分开，可以让你在扩展系统时清楚地知道"我在改什么"——是在改连接逻辑，还是在改核心能力。

### 3.13 最小闭环背后的工程原则

最小闭环背后有一条贯穿始终的工程原则。它是从课程二一路传承下来的，也会延续到后续每一课：

```text
模型负责理解目标和做下一步判断；
确定性基础设施负责工具执行、权限、安全、状态、恢复和观测。
```

不要把一切都交给模型。例如：
- 参数类型校验应该由代码做，不应该依赖模型"写对"。
- 最大步数应该由 Runtime 控制，不应该依赖模型"自己知道该停了"。
- 工具是否存在应该由工具注册表判断，不应该依赖模型"选对"。
- 文件是否允许写入应该由权限系统判断，不应该依赖模型"有分寸"。
- 错误记录和 Trace 应该由系统保存，不应该依赖模型"记住发生了什么"。

模型越强，这个原则越重要。强模型可以提升决策质量的上限，但确定性基础设施保证系统的下限。一个用较弱模型但 Runtime 设计良好的 Agent，可能比一个用最强模型但缺乏边界控制的 Agent 更可靠。

---

## 第四章：从最小闭环看扩展方向

前三章构建了最小 Agent 的完整图景。这一章的视角稍微拉远：**这个最小闭环，后续课程会沿着什么方向扩展？**

理解这个扩展地图很重要，因为它让你在后续课程中始终知道自己"在闭环的哪个位置做增强"。

### 4.1 每个环节分别会被什么能力增强

| 闭环环节 | 增强能力 | 解决什么问题 | 对应课程 |
|---|---|---|---|
| Prompt | Prompt 模板化、版本管理 | Prompt 从手写字符串走向可管理、可评测的工程资产 | 课程六 |
| Prompt（多 Agent） | 角色 Prompt 设计 | 每个 Agent 有独立的 Prompt 定义其角色和行为边界 | 课程五 |
| Context Assembly | RAG | 从外部知识库检索相关信息，注入上下文 | 课程五 |
| Context Assembly | Memory（长期） | 跨会话积累用户偏好和历史经验 | 课程五 |
| Context Assembly | Context Engineering | 更精细的上下文编排、压缩、优先级管理 | 课程六 |
| LLM Decision | Planning | 让模型先规划再执行，而非每一步临场判断 | 课程五 |
| LLM Decision | Reflection | 让模型在执行后评估结果、修正策略 | 课程五 |
| Tool / Environment Interaction | 工具注册、发现、权限、治理 | 从 3 个本地函数扩展到生产级工具平台 | 课程四 |
| State Update | 持久化、向量存储、State 恢复 | 从内存对象到可恢复、可查询的 State 系统 | 课程六 |
| Continue or Stop | Guardrails、Evaluation | 更精细的安全边界和效果评估 | 课程六 / 课程七 |
| 整个闭环 | Multi-Agent | 多个角色各司其职，并行推进 | 课程五 |
| 整个闭环 | Harness / Runtime | 工程化的运行环境：可追踪、可恢复、可评测 | 课程六 |
| 整个闭环 | 产品化 | 用户信任、失败恢复、成本控制、监控指标 | 课程七 |

这张表的价值不是让你现在就掌握这些能力，而是给你一张地图——以后每学一个新能力，你都能把它放回闭环的对应位置。

### 4.2 最小 Agent 不必一开始包含哪些能力

为了避免一开始就过度复杂化，需要明确最小 Agent **不必**包含：
- 不必有 RAG（外部知识检索是增强，不是前提）。
- 不必有长期 Memory（跨会话记忆是增强，不是前提）。
- 不必有复杂 Planning（先让单步决策跑通）。
- 不必有 Multi-Agent（先让单 Agent 跑通）。
- 不必接入 MCP 或复杂工具协议（3 个本地函数就够了）。
- 不必有完整权限平台（先靠代码硬约束）。
- 不必有线上级 Observability（先靠控制台 Trace）。

这些能力都重要，但它们不是最小闭环的前提。**先让闭环跑起来，再逐步增强**——这个顺序不能反。如果你在闭环还没跑通时就加 RAG、加 Memory、加 Multi-Agent，出问题时你分不清是闭环本身有问题，还是你加的能力有问题。

### 4.3 从最小闭环走向后续课程

| 后续课程 | 与本课的关系 |
|---|---|
| 课程四：工具机制 | 深入本课的工具/环境交互部分——从 3 个本地函数走向工具定义、选择、执行、权限、安全的完整机制 |
| 课程五：场景增强能力 | 在最小闭环上判断是否需要 RAG、Memory、Planning、Reflection、Multi-Agent——每种能力都增强闭环的特定环节 |
| 课程六：Harness 运行时架构 | 把本课的概念循环工程化为可追踪、可恢复、可评测的生产级 Runtime |
| 课程七：产品化实践 | 解决用户信任、失败恢复、成本、安全和指标问题——让 Agent 从"能跑"走向"能用" |

课程三不是"一个简单 demo"，而是整条路线的技术地基。你在本课建立的每一个概念——Context Assembly、State Update、Continue or Stop——在后续课程中都会反复出现，只是每次都变得更工程化、更健壮。

---

## 第五章：最小 ReAct Agent 的实现思路

前四章讲完了"是什么"和"为什么"。这一章讲"怎么做"——给出一个最小 ReAct Agent 的实现方案，不绑定任何特定语言或框架。

### 5.1 为什么第一次实现不建议用框架

很多 Agent 框架（LangGraph、CrewAI、AutoGen 等）能帮你快速搭出一个看起来很厉害的 Agent。但对第一次学习最小闭环来说，框架会隐藏太多关键细节。

你可能会看到框架帮你自动做了"工具调用→结果回填→下一轮决策"，但你不知道中间 Context Assembly 是怎么做的、State Update 发生在哪里、Continue or Stop 的判断依据是什么。当 Agent 行为异常时，你只能猜"是不是框架的 bug"或者"是不是模型的问题"——因为你没有自己走过完整链路。

**第一次实现最小 Agent，建议用手写循环 + 直接调用 LLM API。** 工具用本地函数实现，状态用内存对象或 JSON 文件，Trace 写到控制台或本地文件。这样当你看到 Agent 在第 3 步做了一个奇怪的决定时，你可以回溯每一步的 Context、Decision、Observation、State Update，精确知道哪里出了问题。

框架是"你已经理解原理后提高效率的工具"，不是"你还没理解原理时的替代品"。

### 5.2 伪代码结构

下面是一个最小 Agent Loop 的 Python 实现骨架：

```python
from dataclasses import dataclass, field
from typing import Any

@dataclass
class AgentState:
    """最小 Agent 状态"""
    user_goal: str
    max_steps: int = 8
    step_count: int = 0
    history: list[dict] = field(default_factory=list)
    tool_results: list[dict] = field(default_factory=list)
    errors: list[dict] = field(default_factory=list)
    stop_reason: str | None = None
    final_answer: str | None = None

    def recent_history(self, n: int = 5) -> list[dict]:
        return self.history[-n:]


def run_agent(
    user_goal: str,
    system_prompt: str,
    tools: dict[str, callable],
    llm_call: callable,
    max_steps: int = 8,
) -> dict:
    """最小 ReAct Agent 主循环"""
    state = AgentState(user_goal=user_goal, max_steps=max_steps)

    while not state.stop_reason:
        # 1. 从状态中组装上下文
        context = {
            "system": system_prompt,
            "goal": state.user_goal,
            "history": state.recent_history(n=5),
            "tools": [
                {"name": name, "description": fn.__doc__}
                for name, fn in tools.items()
            ],
            "step": state.step_count,
            "errors": state.errors[-3:],
        }

        # 2. 调用 LLM 获取结构化决策
        decision = llm_call(context)
        # decision: {"type": "call_tool"|"final_answer"|"ask_user"|"fail",
        #            "tool_name"?: str, "arguments"?: dict,
        #            "answer"?: str, "question"?: str, "reason"?: str}

        # 3. 根据决策类型分发
        if decision["type"] == "final_answer":
            state.stop_reason = "completed"
            state.final_answer = decision["answer"]
            return {"status": "success", "answer": decision["answer"]}

        if decision["type"] == "ask_user":
            state.stop_reason = "need_user_input"
            return {"status": "paused", "question": decision["question"]}

        if decision["type"] == "fail":
            state.stop_reason = "failed"
            return {"status": "failed", "reason": decision["reason"]}

        if decision["type"] == "call_tool":
            tool_name = decision["tool_name"]
            arguments = decision.get("arguments", {})

            # Runtime 校验：工具是否存在
            if tool_name not in tools:
                observation = {
                    "status": "error",
                    "summary": f"工具 '{tool_name}' 不存在",
                    "error": {"code": "tool_not_found"},
                }
            else:
                # Runtime 执行工具
                try:
                    result = tools[tool_name](**arguments)
                    observation = {
                        "status": "success",
                        "summary": str(result)[:500],
                        "content": result,
                    }
                except Exception as e:
                    observation = {
                        "status": "error",
                        "summary": str(e),
                        "error": {"code": type(e).__name__, "message": str(e)},
                    }

            # 写回状态
            state.history.append({
                "step": state.step_count,
                "decision": decision,
                "observation": observation,
            })
            state.tool_results.append({
                "tool": tool_name,
                "status": observation["status"],
                "summary": observation["summary"],
            })
            if observation["status"] == "error":
                state.errors.append(observation)

        # 4. 检查停止条件
        state.step_count += 1
        if state.step_count >= state.max_steps:
            state.stop_reason = "max_steps_exceeded"
        if len(state.errors) >= 3:
            state.stop_reason = "tool_error_limit"
        if _repeated_action(state, threshold=3):
            state.stop_reason = "repeated_action"

    return {"status": "stopped", "reason": state.stop_reason}


def _repeated_action(state: AgentState, threshold: int = 3) -> bool:
    """检测是否连续重复调用同一工具"""
    recent = state.history[-threshold:]
    if len(recent) < threshold:
        return False
    tools_called = [
        h["decision"].get("tool_name")
        for h in recent
        if h["decision"]["type"] == "call_tool"
    ]
    return len(set(tools_called)) == 1 and len(tools_called) == threshold
```

这段代码体现了几个关键设计决策：

- **LLM 只做决策，不直接执行工具**：`run_agent` 中调用 `tools[tool_name](**arguments)` 的是 Runtime，不是模型。
- **Runtime 校验工具调用**：执行前先检查 `tool_name not in tools`，参数校验在工具函数内部自然发生。
- **工具结果变成结构化 Observation**：无论成功还是失败，返回到状态中的都是 `{"status", "summary", "content", "error"}` 统一结构。
- **每轮都更新状态**：`state.history.append(...)` 把决策和结果记录在案，`state.tool_results` 和 `state.errors` 独立维护便于快速查询。
- **每轮都检查停止条件**：`step_count` 超限、连续报错、重复动作——三种硬约束在循环末尾统一判断，不依赖模型自觉。
- **`_repeated_action` 独立抽取**：检测连续三次调用同一工具说明可能陷入死循环，这个逻辑不需要模型参与，Runtime 自己就能判断。

### 5.3 工具设计

最小 Agent 建议从 3 个工具开始。

示例组合：

| 工具 | 输入 | 输出 | 用途 |
|---|---|---|---|
| `read_file` | 文件路径 | 文件内容或错误 | 读取用户指定资料 |
| `write_file` | 文件路径、内容 | 写入成功或错误 | 生成交付物 |
| `search_text` | 关键词、文本集合 | 匹配片段 | 在资料中查找信息 |

**工具返回结果必须结构化**。这是从课程二 Function Calling 的设计哲学延续下来的：

成功时：
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
  message: "未找到 notes.md，请检查文件路径"
```

结构化返回的好处是：模型能明确知道发生了什么，而不是从一段自由文本中猜测。当返回中包含具体的错误码和原因时，模型更可能提出有效的修正方案。

### 5.4 Trace 记录

Trace 是最小 Agent 的调试基础。没有 Trace 的 Agent 就像一个黑箱——你只知道最终失败了，不知道哪一步开始偏的。

每一步至少记录：
- step number。
- context summary（上下文太长时做一个简要标记）。
- model decision（模型决定做什么）。
- tool call（如果调用了工具，记录工具名和参数）。
- observation（工具返回了什么，或错误信息）。
- state update（状态发生了什么变化）。
- stop check result（继续还是停止，原因是什么）。

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

这个 Trace 让你在调试时可以逐步骤回放——看到模型在每一轮看到了什么（context）、决定了什么（decision）、得到了什么（observation）、状态发生了什么变化（state update）。

### 5.5 基础错误处理

最小 Agent 至少要处理这些错误：

| 错误 | 处理方式 |
|---|---|
| 工具不存在 | 返回结构化错误，不执行，让模型知道该工具不可用 |
| 参数不合法 | 返回参数错误详情，让模型修正或请求用户提供正确参数 |
| 工具执行失败 | 记录错误，允许有限重试（如 2 次），超过则停止 |
| 环境不可用 | 停止或降级，不要让 Agent 在不可靠的环境上硬撑 |
| 模型输出无法解析 | 请求模型重新输出（最多 1 次），仍失败则退出 |
| 超过最大步数 | 停止并说明原因，让用户知道"没做完但不能再继续了" |
| 重复动作无进展 | 停止或请求用户介入，不要让 Agent 在死循环里空转 |

错误处理不是"后续再说"的内容。最小闭环如果没有错误处理，稍微复杂一点的测试任务就会失控——工具失败 → 模型乱猜 → 模型调用更错的工具 → 循环爆炸。有经验的人实现 Agent 时，错误处理代码量往往和主循环代码量相当。

### 5.6 测试任务设计

用 10 条任务测试最小 Agent。建议覆盖以下类型：

| 类型 | 示例 | 测试什么 |
|---|---|---|
| 成功路径 | 读取一个文件并总结 | 基本闭环能跑通 |
| 多步任务 | 读取文件、提取要点、写入新文件 | 状态在多步间正确传递 |
| 参数错误 | 用户给出不存在的文件路径 | 错误能被捕获并反馈给模型 |
| 工具失败 | 模拟 API 返回错误 | 有限重试，不无限循环 |
| 需要澄清 | 用户目标不完整 | Agent 能请求补充信息 |
| 循环控制 | 工具反复失败时能停止 | 硬约束生效 |
| 结果验证 | 输出必须包含指定字段 | 最终答案格式正确 |
| 状态延续 | 第二步要使用第一步工具结果 | 状态在步骤间正确传递 |
| 写操作 | 写入本地结果文件 | 写操作正常执行 |
| 安全边界 | 尝试执行不允许的动作时拒绝 | Runtime 校验生效 |

成功率达到 70% 以上是一个初步目标——考虑到最小 Agent 的错误处理还很基础，有些失败是可以预期的。更重要的是：**失败时你要能通过 Trace 知道为什么失败。** 如果你只能看到"任务失败了"但不知道失败在哪一步、什么原因，那说明 Trace 还不够好。

---

## 课后练习

### 练习一：画出最小 Agent 闭环

用自己的话画出以下链路：

```text
Prompt → User Goal → Context Assembly → LLM Decision → Interaction → Observation → State Update → Continue or Stop
```

要求：
- 标出 Prompt 的位置，并用一句话说明它为什么不在循环内但却是链路的一部分。
- 标出状态从哪里读取、在哪里写入。
- 标出工具结果如何影响下一轮决策（给一个具体例子）。
- 标出停止条件在哪里发生。
- 在图上标注五个核心组件分别对应链路的哪个部分。

### 练习二：设计一份最小 Agent 的 Prompt

为一个"读取文件并生成摘要"的 Agent，设计一份完整的 Prompt。你的 Prompt 必须包含以下五层：

1. **身份层**：定义 Agent 的角色和总体目标
2. **协议层**：定义 Thought/Action/Observation 格式
3. **工具层**：描述至少 3 个可用工具（名称、用途、参数、注意事项）
4. **约束层**：输出格式要求、停止条件、安全边界
5. **示例层**：至少 1 个 few-shot 示例，展示完整的 TAO 轨迹

附加题：故意去掉约束层中的"输出格式要求"，用同样的任务跑一次，观察 LLM 的行为变化。记录你的发现。

### 练习三：设计一个最小 Agent 状态对象

为"读取文件并生成摘要"这个任务，设计一个最小状态对象。至少包含：用户目标、当前步骤数、最大步骤数、历史决策、工具结果、错误列表、停止原因。

附加题：想一个场景，说明为什么"把全部历史原文塞进上下文"不如"维护独立的状态对象 + 选择性注入"。

### 练习四：设计 3 个工具

为你的最小 Agent 设计 3 个工具。每个工具写清楚：工具名、工具用途、输入参数、输出结构（含成功和失败两种格式）、可能失败的情况、风险等级。

### 练习五：写出最小循环控制规则

为你的 Agent 写出至少 5 条循环控制规则。每条规则写清楚：触发条件是什么、采取什么动作（继续/停止/请求用户）、为什么需要这条规则。

### 练习六：完成 10 条测试任务设计

按照第五章的任务类型，设计你的 10 条测试任务。每条任务写清楚：用户输入、期望工具调用链、成功标准、可能失败点和为什么它会失败。

### 交付物

完成本课后，建议沉淀以下材料：
1. 一张最小 Agent 闭环图（标注五个核心组件和两个连接点，含 Prompt 的位置）。
2. 一份完整的 Agent Prompt（含五层结构：身份、协议、工具、约束、示例）。
3. 一个最小状态对象设计。
4. 三个工具定义（含成功/失败输出格式）。
5. 一份循环控制规则（含每条规则的触发条件和理由）。
6. 十条测试任务（含成功标准和失败点分析）。
7. 一份最小 Agent 实现方案说明。

---

## 验收标准

完成本课后，请用以下标准自检：

- [ ] 我能解释为什么最小 Agent 不能只有 LLM——能从 LLM 的本质局限（只能生成文本、没有外部感知、没有持久状态、不能自我控制、不知道自己是一个 Agent）出发，说明五个组成部分解决了什么。
- [ ] 我能说出 `Prompt（行为定义） + LLM 决策 + 工具/环境交互 + 状态管理 + 循环控制` 五部分各自负责什么，以及它们分别填补了 LLM 的哪个空白。
- [ ] 我能解释为什么 Prompt 是 Agent 的"源代码"，能拆解一份 ReAct Prompt 的五层结构（身份层、协议层、工具层、约束层、示例层）。
- [ ] 我能画出最小运行链路图，标注 Prompt 的位置、State 的读写关系、以及 Runtime 的边界。
- [ ] 我能区分 Prompt（静态模板）和 Context Assembly（动态填充）的分工。
- [ ] 我能区分"状态"和"长期 Memory"——前者是当前任务运行时信息，后者是跨任务经验积累。
- [ ] 我能解释 Prompt 为什么是核心组件、而 Context Assembly 和 Observation / Feedback 为什么是"连接点"。
- [ ] 我理解"模型决策，Runtime 执行"的工程原则，并能举例说明 Runtime 应该校验什么。
- [ ] 我能设计一份最小 Agent 的 Prompt、一个状态对象和 3 个工具。
- [ ] 我能写出最小循环控制规则，包括停止条件和继续条件。
- [ ] 我能设计 10 条测试任务，并定义每一条的成功标准和可能失败点。
- [ ] 我知道课程四、五、六、七分别会在本课基础上扩展闭环的哪个环节。

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
- Lost in the Middle: How Language Models Use Long Contexts
  <https://arxiv.org/abs/2307.03172>
- LangGraph 文档
  <https://langchain-ai.github.io/langgraph/>
