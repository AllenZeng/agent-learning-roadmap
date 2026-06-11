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
Agent = LLM 决策 + 工具/环境交互 + 状态管理 + 循环控制
```

这个公式不是要定义所有 Agent 产品的全部能力，而是要抓住"最小闭环"——能跑起来、能完成多步任务、能受控停止的最简结构。后续课程中的工具机制、RAG / Memory、Planning / Workflow Patterns、Harness、Evaluation、Guardrails，都是围绕这个闭环继续扩展。

为什么这个顺序很重要？因为如果你不理解这个闭环本身，直接跳到"加 RAG""加 Memory""加 Multi-Agent"，你加的每一层都是在你不理解的地基上盖楼。反过来，如果你先把闭环跑通了，再看那些扩展能力，你会立刻知道它们分别增强了闭环的哪个环节——RAG 增强的是 Context Assembly 的信息来源，Memory 增强的是 State 的跨会话持久化，Planning 增强的是 LLM Decision 的结构化程度。

课程三只解决一件事：**让你真正理解并能实现一个最小可运行 Agent**。

---

## 学习目标

学完本课，你将能够：

1. **解释最小 Agent 为什么不能只有 LLM** — 理解 LLM 的本质局限
2. **画出最小 Agent 运行链路** — 说清 `User Goal → Context Assembly → LLM Decision → Interaction → Observation → State Update → Continue or Stop`
3. **区分核心模块与连接点** — 明白为什么 Context Assembly、Observation 是连接环节而非额外核心模块
4. **理解状态管理的角色** — 知道哪些信息需要独立于 LLM 存储，以及为什么上下文窗口不能作为唯一的状态存储
5. **设计循环控制规则** — 包括停止条件、最大步数、超时、重复检测和失败退出
6. **规划最小 ReAct Agent 的实现** — 能定义工具、状态、Trace、错误处理和测试任务

本课围绕的核心问题：

- 一个最小 Agent 为什么不能只有 LLM？
- LLM 决策、工具交互、状态管理、循环控制各自解决什么？
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
- [第二章：最小 Agent 组成](#第二章最小-agent-组成)
  - [2.1 核心公式](#21-核心公式)
  - [2.2 LLM 决策](#22-llm-决策)
  - [2.3 工具/环境交互](#23-工具环境交互)
  - [2.4 状态管理](#24-状态管理)
  - [2.5 循环控制](#25-循环控制)
- [第三章：最小运行链路](#第三章最小运行链路)
  - [3.1 User Goal：从模糊意图到可操作目标](#31-user-goal从模糊意图到可操作目标)
  - [3.2 Context Assembly：模型应该看到什么](#32-context-assembly模型应该看到什么)
  - [3.3 LLM Decision：下一步做什么](#33-llm-decision下一步做什么)
  - [3.4 Interaction & Execution：真的去做](#34-interaction--execution真的去做)
  - [3.5 Observation / Feedback：让结果回到循环](#35-observation--feedback让结果回到循环)
  - [3.6 State Update：把经验写下来](#36-state-update把经验写下来)
  - [3.7 Continue or Stop：知道什么时候该停](#37-continue-or-stop知道什么时候该停)
- [第四章：运行时循环总览](#第四章运行时循环总览)
  - [4.1 最小闭环图](#41-最小闭环图)
  - [4.2 状态存储的正确位置](#42-状态存储的正确位置)
  - [4.3 核心模块与连接点的区别](#43-核心模块与连接点的区别)
  - [4.4 最小闭环背后的工程原则](#44-最小闭环背后的工程原则)
- [第五章：从最小闭环看扩展方向](#第五章从最小闭环看扩展方向)
  - [5.1 每个环节分别会被什么能力增强](#51-每个环节分别会被什么能力增强)
  - [5.2 最小 Agent 不必一开始包含哪些能力](#52-最小-agent-不必一开始包含哪些能力)
  - [5.3 从最小闭环走向后续课程](#53-从最小闭环走向后续课程)
- [第六章：最小 ReAct Agent 的实现思路](#第六章最小-react-agent-的实现思路)
  - [6.1 为什么第一次实现不建议用框架](#61-为什么第一次实现不建议用框架)
  - [6.2 伪代码结构](#62-伪代码结构)
  - [6.3 工具设计](#63-工具设计)
  - [6.4 Trace 记录](#64-trace-记录)
  - [6.5 基础错误处理](#65-基础错误处理)
  - [6.6 测试任务设计](#66-测试任务设计)
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

这里先停一下：**Runtime 是什么？** 在本课中，Runtime 指的是包裹在 LLM 外面的那层确定性系统代码。它不生成文本，不做语义推理，但它负责：管理状态（记住前面发生了什么）、执行工具（真的去读文件、调 API）、控制循环（判断继续还是停止）、校验权限（这个操作允许吗）、记录 Trace（每一步发生了什么）。简单说：**Agent 系统中所有不是 LLM 的部分，都属于 Runtime 的职责范围。** 理解了 Runtime 和 LLM 的分工——LLM 做决策，Runtime 管执行和边界——你就抓住了 Agent 架构最核心的设计原则。

### 1.4 LLM 能推理，但不能控制自己的边界

LLM 天然倾向于"继续生成"。它不知道什么时候该停，不知道什么时候该请求帮助，不知道什么时候自己的行为已经变成了死循环。

如果你让一个纯 LLM 系统在循环中工作，它可能：
- 一直重复调用同一个工具，因为每次看到类似的上下文，它就做出类似的决策。
- 遇到错误后无限重试，因为它不知道"放弃"也是一个合理选择。
- 在任务已经完成后继续多余操作，因为它没有"完成"的概念——它只是在生成下一个 Token。
- 在不确定时仍然执行高风险动作，因为它没有"风险判断"能力——它看到的是一个概率分布，而不是后果。

所以 Agent 不能只依赖 LLM 的"判断"来管理自己的运行边界。循环控制必须由 Runtime 负责——Runtime 设定硬约束（最大步数、超时、重复检测），LLM 在约束内做决策。这不是不信任模型，而是把"决策"和"执行边界"分给最适合它们的角色。

---

## 第二章：最小 Agent 组成

上一章讲了 LLM 四个"不能"——不能做、不能记、不能控、不能止。这一章把每个"不能"对应到一个具体的系统组件上。这四个组件合在一起，就是最小 Agent 的骨架。

### 2.1 核心公式

```text
Agent = LLM 决策 + 工具/环境交互 + 状态管理 + 循环控制
```

四个部分缺一不可。这个公式不是说所有 Agent 只能有这四个部分，而是说：**如果连这四个都没有，就不能算一个最小完整 Agent。** 就像一个最小的人体需要大脑、手、记忆和自律——少了任何一样，都不能算一个完整的人。

| 组成 | 解决 LLM 的哪个局限 | 如果缺失会怎样 |
|---|---|---|
| LLM 决策 | —（这是被增强的对象） | 系统无法理解开放目标 |
| 工具/环境交互 | "会说不会做" | 系统只能说，不能做 |
| 状态管理 | "会判断不会记" | 系统无法连续工作，忘记前面做了什么 |
| 循环控制 | "能推理不能控边界" | 系统容易失控、死循环、或无法完成多步任务 |

这四个组成部分不是四块独立的积木。它们通过运行链路连接在一起，形成闭环。在讲运行链路之前（第三章），我们先逐个理解每个组成部分负责什么。

### 2.2 LLM 决策

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

### 2.3 工具/环境交互

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

### 2.4 状态管理

状态管理让 Agent 从"单轮问答"走向"多步任务执行"。它解决的核心问题是：**LLM 的上下文窗口不能也不应该成为唯一的状态存储。**

一个最小 Agent 至少要维护：
- 用户目标。
- 当前步骤数。
- 历史消息（或压缩后的摘要）。
- 已调用的工具及其结果。
- 中间结论和发现。
- 错误信息。
- 停止原因（如果已停止）。

这里有一个重要的概念区分：**状态不等于长期 Memory。** 在本课中，状态主要指当前任务运行时需要保存的信息——它的生命周期是这个任务。长期 Memory 是跨任务、跨会话的信息积累（用户偏好、历史经验），是课程五的内容，不是最小闭环的必选项。

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

状态管理的关键不是"存得多"，而是"下一轮决策需要什么就保存什么"。这是一个权衡——存少了，模型缺少决策依据；存多了，上下文窗口膨胀，模型注意力分散。好的状态管理是在"信息充分"和"信息精简"之间找到平衡。

### 2.5 循环控制

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

第二章讲了"四个组成部分"，这一章讲"它们怎么协作"。

四个组成部分不是四块积木拼在一起就能工作。它们需要通过一条运行链路串联起来，形成真正的闭环：

```text
User Goal
    → Context Assembly
    → LLM Decision
    → Tool / Environment Interaction → Execution
    → Observation / Feedback
    → State Update
    → Continue or Stop（如果继续，回到 Context Assembly）
```

核心公式描述的是"有什么"，运行链路描述的是"怎么运转"。下面逐个环节展开。

### 3.1 User Goal：从模糊意图到可操作目标

用户目标是 Agent 的起点。它可能是明确的（"读取 notes.md，总结成 5 个要点"），也可能是模糊的（"帮我整理一下这个目录"）。

目标的质量直接影响整个闭环的表现。一个过于模糊的目标（如"帮我优化这个项目"），LLM 在第一步决策时就没有足够的信息来判断"优化"指什么——性能？代码结构？可读性？它可能需要多轮试探才能搞清楚用户真正想要什么，甚至可能一路朝着错误的方向执行。一个过于宏大的目标（如"帮我重构整个代码库"），会超出最小闭环的能力边界——这种任务需要 Planning 拆解、需要 Memory 跨会话追踪、需要更完善的权限控制。

最小 Agent 的定位决定了它适合处理的目标类型：目标明确、边界清晰、验证标准可判断。这不是说 Agent 不能处理模糊目标，而是说**在第一次学习闭环时，先让变量可控**——当你知道目标是明确的，你就能把注意力集中在观察链路本身是否正常运转，而不是纠结"Agent 的行为到底是目标太模糊导致的，还是链路有 bug 导致的"。

换句话说，User Goal 在闭环中的角色是**锚点**——后续每一步决策都以它为参照：当前的动作是否在朝着目标推进？当前的结果是否离目标更近了？最终答案是否覆盖了目标的所有要求？如果这个锚点是模糊的，整个循环就会在不确定中漂移。

### 3.2 Context Assembly：模型应该看到什么

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

### 3.3 LLM Decision：下一步做什么

LLM Decision 是每轮循环的核心。模型根据组装好的上下文，输出一个结构化的"下一步决策"。

在最小 Agent 中，决策通常有以下几种类型：

| 决策类型 | 含义 | Runtime 行为 |
|---|---|---|
| `call_tool` | 调用工具 | 校验 → 执行 → 收集结果 |
| `final_answer` | 任务完成，输出最终结果 | 记录完成 → 返回答案 |
| `ask_user` | 需要用户补充信息或确认 | 暂停循环 → 等待用户 |
| `fail` | 无法继续，承认失败 | 记录失败原因 → 停止 |

模型决策不是最终执行。Runtime 仍然需要校验：工具是否存在、参数是否合法、是否超过权限、是否超过步数、是否应该请求用户确认。

### 3.4 Interaction & Execution：真的去做

当模型决定调用工具时，Runtime 接手执行。

执行环节包括：
- 校验工具名（这个工具存在吗？）。
- 校验参数（类型对吗？必填项都有吗？值在合法范围吗？）。
- 执行工具（真正去读文件、调 API、跑代码）。
- 捕获异常（文件不存在、网络超时、权限不足、返回格式异常）。
- 规范化返回结果（把原始结果整理成结构化的 Observation）。

一条实操经验：工具调用后的原始结果，**不应该不经处理就塞回模型**。尤其是结果很长时——比如读取了一个 5000 行的文件——直接把全文塞进上下文会挤占其他重要信息。最小 Agent 至少要做一个简单的截断或摘要。

### 3.5 Observation / Feedback：让结果回到循环

Observation 是工具执行的结果——它可能是文件内容、搜索结果、API 响应、错误信息、权限拒绝、或者用户确认。

Observation 的作用只有一个，但非常关键：**影响下一轮决策。** 如果 Agent 读取了一个文件但发现文件不存在，下一轮它应该请求用户修正路径，而不是继续假装文件存在。Observation 是"外部世界"和"模型推理"之间的信息通道——没有它，模型就是在盲猜。

一个真实的例子：

```text
Action: read_file("notes.md")
Observation: status=error, code=file_not_found, message="未找到 notes.md"
Next Decision: ask_user("没有找到 notes.md，请确认文件路径是否正确")
```

这就是闭环的意义：每一步的结果改变下一步的方向。

### 3.6 State Update：把经验写下来

State Update 把本轮发生的事情记录到状态中。它需要记录：
- 模型做了什么决策。
- 工具是否执行、结果是什么。
- 是否发生错误。
- 当前任务是否更接近完成。
- 是否需要停止或请求用户介入。

状态更新的目的不是"存档"，而是支持三个关键需求：
1. **下一轮 Context Assembly**：下一轮需要知道本轮发生了什么。
2. **失败调试**：任务失败时，状态历史是唯一的问题排查依据。
3. **任务恢复**：如果任务中断，状态可以用于恢复。

最小 Agent 至少要能记录每一步的 Trace。Trace 不需要很复杂——一个包含步骤号、决策内容、工具结果、停止判断的结构化记录就足够了。

### 3.7 Continue or Stop：知道什么时候该停

每轮结束后，Runtime 必须判断：继续还是停止？

判断依据包括：
- 模型是否给出 final_answer？
- 是否达到最大步数？
- 是否重复调用同一工具且没有新进展？
- 是否遇到不可恢复错误？
- 是否需要用户确认或补充信息？
- 是否命中风险规则？

如果继续，就重新进入 Context Assembly——用更新后的状态组装新的上下文，开始下一轮循环。如果停止，就输出最终答案或失败原因。

---

## 第四章：运行时循环总览

前三章分别讲了"为什么需要四个组成部分""每个部分负责什么""它们怎么串成链路"。这一章把这些放在一起，从整体视角看最小闭环。

### 4.1 最小闭环图

```text
User Goal → Context Assembly → LLM Decision → Interaction → Execution
                ↑                                               |
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
- **主链路**：目标如何一步步推进到执行和反馈——从左到右，再从右回到左。
- **状态读写**：上下文从状态中读取，执行结果写回状态——状态不在主链路上，但在两侧支撑着主链路的每一次循环。
- **反馈闭环**：每轮 Observation 都会影响下一轮决策——这正是 ReAct 的核心思想：推理和行动在循环中互相喂给对方。

### 4.2 状态存储的正确位置

图里的 `State / Memory Store` 不在主链路上，而在旁边。这是有意设计的。

状态存储不是一个"独立行动步骤"——Agent 不会在某一步说"现在我要操作状态"。状态被两个环节读写：
- **Context Assembly** 从状态中**读取**信息（当前进度、历史决策、工具结果）。
- **State Update** 把新信息**写入**状态（刚刚发生的事、刚刚得到的结果）。

把状态放在主链路旁边而不是其中，是为了强调：状态是基础设施，不是业务流程中的一步。

在最小 Agent 中，State / Memory Store 可以只是一个内存对象或 JSON 文件。不需要数据库，不需要向量存储。这里的 Memory 不等于课程五要讲的长期 Memory——它首先是当前任务的运行时状态。

### 4.3 核心模块与连接点的区别

你可能已经注意到，运行链路中有几个环节没有出现在核心公式里：Context Assembly、Observation / Feedback。

它们非常重要，但它们不是"核心模块"，而是**运行时连接点**。

Context Assembly 是状态管理和 LLM 决策之间的连接点：

```text
状态里有什么 → 选择什么进入上下文 → 模型据此决策
```

Observation / Feedback 是工具交互和状态管理之间的连接点：

```text
工具执行结果 → 转成模型可理解的信息 → 写回状态 → 进入下一轮上下文
```

这个区分不是咬文嚼字。它的工程含义是：这些连接点会随着系统复杂度增长而显著变化（上下文管理策略会变、反馈信号的种类和来源会变），但四个核心模块的职责边界相对稳定。把连接点和核心模块分开，可以让你在扩展系统时清楚地知道"我在改什么"——是在改连接逻辑，还是在改核心能力。

### 4.4 最小闭环背后的工程原则

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

## 第五章：从最小闭环看扩展方向

前四章构建了最小 Agent 的完整图景。这一章的视角稍微拉远：**这个最小闭环，后续课程会沿着什么方向扩展？**

理解这个扩展地图很重要，因为它让你在后续课程中始终知道自己"在闭环的哪个位置做增强"。

### 5.1 每个环节分别会被什么能力增强

| 闭环环节 | 增强能力 | 解决什么问题 | 对应课程 |
|---|---|---|---|
| Context Assembly | RAG | 从外部知识库检索相关信息，注入上下文 | 课程五 |
| Context Assembly | Memory（长期） | 跨会话积累用户偏好和历史经验 | 课程五 |
| Context Assembly | Context Engineering | 更精细的上下文编排、压缩、优先级管理 | 课程六 |
| LLM Decision | Planning | 让模型先规划再执行，而非每一步临场判断 | 课程五 |
| LLM Decision | Reflection | 让模型在执行后评估结果、修正策略 | 课程五 |
| Tool / Environment Interaction | 工具注册、发现、权限、治理 | 从 3 个本地函数扩展到生产级工具平台 | 课程四 |
| State Update | 持久化、向量存储、状态恢复 | 从内存对象到可恢复、可查询的状态系统 | 课程六 |
| Continue or Stop | Guardrails、Evaluation | 更精细的安全边界和效果评估 | 课程六 / 课程七 |
| 整个闭环 | Multi-Agent | 多个角色各司其职，并行推进 | 课程五 |
| 整个闭环 | Harness / Runtime | 工程化的运行环境：可追踪、可恢复、可评测 | 课程六 |
| 整个闭环 | 产品化 | 用户信任、失败恢复、成本控制、监控指标 | 课程七 |

这张表的价值不是让你现在就掌握这些能力，而是给你一张地图——以后每学一个新能力，你都能把它放回闭环的对应位置。

### 5.2 最小 Agent 不必一开始包含哪些能力

为了避免一开始就过度复杂化，需要明确最小 Agent **不必**包含：
- 不必有 RAG（外部知识检索是增强，不是前提）。
- 不必有长期 Memory（跨会话记忆是增强，不是前提）。
- 不必有复杂 Planning（先让单步决策跑通）。
- 不必有 Multi-Agent（先让单 Agent 跑通）。
- 不必接入 MCP 或复杂工具协议（3 个本地函数就够了）。
- 不必有完整权限平台（先靠代码硬约束）。
- 不必有线上级 Observability（先靠控制台 Trace）。

这些能力都重要，但它们不是最小闭环的前提。**先让闭环跑起来，再逐步增强**——这个顺序不能反。如果你在闭环还没跑通时就加 RAG、加 Memory、加 Multi-Agent，出问题时你分不清是闭环本身有问题，还是你加的能力有问题。

### 5.3 从最小闭环走向后续课程

| 后续课程 | 与本课的关系 |
|---|---|
| 课程四：工具机制 | 深入本课的工具/环境交互部分——从 3 个本地函数走向工具定义、选择、执行、权限、安全的完整机制 |
| 课程五：场景增强能力 | 在最小闭环上判断是否需要 RAG、Memory、Planning、Reflection、Multi-Agent——每种能力都增强闭环的特定环节 |
| 课程六：Harness 运行时架构 | 把本课的概念循环工程化为可追踪、可恢复、可评测的生产级 Runtime |
| 课程七：产品化实践 | 解决用户信任、失败恢复、成本、安全和指标问题——让 Agent 从"能跑"走向"能用" |

课程三不是"一个简单 demo"，而是整条路线的技术地基。你在本课建立的每一个概念——Context Assembly、State Update、Continue or Stop——在后续课程中都会反复出现，只是每次都变得更工程化、更健壮。

---

## 第六章：最小 ReAct Agent 的实现思路

前五章讲完了"是什么"和"为什么"。这一章讲"怎么做"——给出一个最小 ReAct Agent 的实现方案，不绑定任何特定语言或框架。

### 6.1 为什么第一次实现不建议用框架

很多 Agent 框架（LangGraph、CrewAI、AutoGen 等）能帮你快速搭出一个看起来很厉害的 Agent。但对第一次学习最小闭环来说，框架会隐藏太多关键细节。

你可能会看到框架帮你自动做了"工具调用→结果回填→下一轮决策"，但你不知道中间 Context Assembly 是怎么做的、State Update 发生在哪里、Continue or Stop 的判断依据是什么。当 Agent 行为异常时，你只能猜"是不是框架的 bug"或者"是不是模型的问题"——因为你没有自己走过完整链路。

**第一次实现最小 Agent，建议用手写循环 + 直接调用 LLM API。** 工具用本地函数实现，状态用内存对象或 JSON 文件，Trace 写到控制台或本地文件。这样当你看到 Agent 在第 3 步做了一个奇怪的决定时，你可以回溯每一步的 Context、Decision、Observation、State Update，精确知道哪里出了问题。

框架是"你已经理解原理后提高效率的工具"，不是"你还没理解原理时的替代品"。

### 6.2 伪代码结构

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

### 6.3 工具设计

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

### 6.4 Trace 记录

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

### 6.5 基础错误处理

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

### 6.6 测试任务设计

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
User Goal → Context Assembly → LLM Decision → Interaction → Observation → State Update → Continue or Stop
```

要求：
- 标出状态从哪里读取、在哪里写入。
- 标出工具结果如何影响下一轮决策（给一个具体例子）。
- 标出停止条件在哪里发生。
- 在图上标注四个核心模块分别对应链路的哪个部分。

### 练习二：设计一个最小 Agent 状态对象

为"读取文件并生成摘要"这个任务，设计一个最小状态对象。至少包含：用户目标、当前步骤数、最大步骤数、历史决策、工具结果、错误列表、停止原因。

附加题：想一个场景，说明为什么"把全部历史原文塞进上下文"不如"维护独立的状态对象 + 选择性注入"。

### 练习三：设计 3 个工具

为你的最小 Agent 设计 3 个工具。每个工具写清楚：工具名、工具用途、输入参数、输出结构（含成功和失败两种格式）、可能失败的情况、风险等级。

### 练习四：写出最小循环控制规则

为你的 Agent 写出至少 5 条循环控制规则。每条规则写清楚：触发条件是什么、采取什么动作（继续/停止/请求用户）、为什么需要这条规则。

### 练习五：完成 10 条测试任务设计

按照第六章的任务类型，设计你的 10 条测试任务。每条任务写清楚：用户输入、期望工具调用链、成功标准、可能失败点和为什么它会失败。

### 交付物

完成本课后，建议沉淀以下材料：
1. 一张最小 Agent 闭环图（标注核心模块和连接点）。
2. 一个最小状态对象设计。
3. 三个工具定义（含成功/失败输出格式）。
4. 一份循环控制规则（含每条规则的触发条件和理由）。
5. 十条测试任务（含成功标准和失败点分析）。
6. 一份最小 Agent 实现方案说明。

---

## 验收标准

完成本课后，请用以下标准自检：

- [ ] 我能解释为什么最小 Agent 不能只有 LLM——能从 LLM 的本质局限（只能生成文本、没有外部感知、没有持久状态、不能自我控制）出发，说明四个组成部分解决了什么。
- [ ] 我能说出 `LLM 决策 + 工具/环境交互 + 状态管理 + 循环控制` 四部分各自负责什么，以及它们分别填补了 LLM 的哪个空白。
- [ ] 我能画出最小运行链路，并解释每个环节的作用。
- [ ] 我能区分"状态"和"长期 Memory"——前者是当前任务运行时信息，后者是跨任务经验积累。
- [ ] 我能解释 Context Assembly 和 Observation / Feedback 为什么是"连接点"而非"核心模块"。
- [ ] 我理解"模型决策，Runtime 执行"的工程原则，并能举例说明 Runtime 应该校验什么。
- [ ] 我能设计一个最小状态对象和 3 个工具。
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
