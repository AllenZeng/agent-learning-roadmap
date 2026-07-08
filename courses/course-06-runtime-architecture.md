# 第 6 章：Harness：让 Agent 稳定、可靠、持续运行

## 这门课为什么从“能力”转向“运行秩序”

前面几章已经把 Agent 的能力零件装起来了：

- 第 3 章讲最小 Agent 循环：Agent 如何观察、思考、行动。
- 第 4 章讲工具机制：Agent 如何调用外部工具，连接真实世界。
- 第 5 章讲能力增强：Memory、Context Engineering、Planning、Reflection、RAG、Multi-Agent、Human-in-the-loop 如何补足复杂任务场景。

到了第 6 章，问题变了。

你不再只是问“Agent 能不能调用工具”“能不能检索知识”“能不能规划任务”。你要问的是：

> 当 Agent 已经具备多种增强能力之后，如何通过一套运行架构，把这些能力组织成稳定、可控、可恢复、可观测、可持续演进的系统？

本章的核心不是继续增强 Agent 能力，而是管理 Agent 能力的运行秩序。这个负责承载、编排、约束、恢复和观测 Agent 运行过程的系统层，我们称为 **Harness**。

Harness 这个词原本指马具。马本身有力量，但没有马具，力量就可能乱跑；马具不增加马的力量，却让力量可以被引导、约束和交付。Agent Harness 也是如此：它不制造新的智能，而是让已有的智能能在真实系统里稳定工作。

## 能力越多，越需要一套运行秩序

一个 Agent 系统能力越多，表面上越强，但运行复杂度也越高：

- Memory 可能污染上下文。
- RAG 可能引入不可靠证据。
- Planning 可能产生过长、不可恢复的任务链。
- Reflection 可能陷入反复自我修正。
- Multi-Agent 可能导致职责不清、状态混乱。
- Human-in-the-loop 可能中断任务流。
- Tool Use 可能产生真实世界的副作用。

第 6 章要解决的问题是：

> 如何用 Harness 架构，把 Memory、RAG、Planning、Reflection、Tools、Multi-Agent、Human-in-the-loop 等能力，从零散调用变成可调度、可交接、可恢复、可观测、可控制的运行系统？

本章基于 2026 年 7 月的主流实践抽象而来。不同框架的名字不一样：LangGraph 讲 graph state、checkpoint、store、interrupt 和 trace；OpenAI Agents SDK 讲 agent loop、sessions、guardrails、handoffs 和 tracing；Anthropic 的工程实践区分 predefined workflow 和动态 agent，并强调从简单方案开始、在必要时增加复杂度。本章不绑定某个框架 API，而是提炼这些实践背后的运行架构问题。

## 从能力层到运行层：本章的阅读地图

```text
能力层：Memory / RAG / Planning / Reflection / Multi-Agent / HITL / Tools
          ↓
运行层：State / Orchestration / Flow / Observability / Recovery / Control
          ↓
系统目标：稳定、可靠、可持续、可审计、可演进
```

读完本章，你应该能做三件事：

1. 画出一个 Agent Harness 的运行架构图，并标注状态、编排、可观测、恢复和控制面。
2. 判断一个 Agent 问题到底是能力不足，还是运行秩序缺失。
3. 为一个真实业务 Agent 设计最小可落地的 Runtime State、Trace、Checkpoint 和运行控制策略。

## 目录

- [6.1 能力越多，Agent 反而越容易失控](#61-能力越多agent-反而越容易失控)
  - [6.1.1 八个能力都合理，组合起来却失控](#611-八个能力都合理组合起来却失控)
  - [6.1.2 Demo 只要能跑，生产必须能解释和恢复](#612-demo-只要能跑生产必须能解释和恢复)
  - [6.1.3 每加一个能力，都要回答四个运行问题](#613-每加一个能力都要回答四个运行问题)
- [6.2 从能力模块到运行架构：Harness 才是系统中枢](#62-从能力模块到运行架构harness-才是系统中枢)
  - [6.2.1 Harness 不是第八个能力，而是能力的运行中枢](#621-harness-不是第八个能力而是能力的运行中枢)
  - [6.2.2 Harness 管的是状态、边界、恢复和证据链](#622-harness-管的是状态边界恢复和证据链)
- [6.3 状态中心：把前面学过的能力纳入同一套运行状态](#63-状态中心把前面学过的能力纳入同一套运行状态)
  - [6.3.1 崩溃后要恢复的不是聊天记录](#631-崩溃后要恢复的不是聊天记录)
  - [6.3.2 六类 State：把混在 prompt 里的东西拆开](#632-六类-state把混在-prompt-里的东西拆开)
  - [6.3.3 每一轮 Harness 都在读写状态](#633-每一轮-harness-都在读写状态)
  - [6.3.4 Task State：把用户请求变成任务契约](#634-task-state把用户请求变成任务契约)
  - [6.3.5 Execution State：让 Agent Loop 可以暂停和接上](#635-execution-state让-agent-loop-可以暂停和接上)
  - [6.3.6 Context State：让信息有来源、边界和有效期](#636-context-state让信息有来源边界和有效期)
  - [6.3.7 Capability State：记录哪些能力改变了任务走向](#637-capability-state记录哪些能力改变了任务走向)
  - [6.3.8 Control State：把权限、成本和风险变成硬边界](#638-control-state把权限成本和风险变成硬边界)
  - [6.3.9 Trace State：给每次状态变化留下证据链](#639-trace-state给每次状态变化留下证据链)
- [6.4 编排与状态流转：让能力在正确边界内接力](#64-编排与状态流转让能力在正确边界内接力)
  - [6.4.1 能力私下串联，系统就失去解释权](#641-能力私下串联系统就失去解释权)
  - [6.4.2 编排看的是当前状态，不是固定触发清单](#642-编排看的是当前状态不是固定触发清单)
  - [6.4.3 四类 Flow：输入、输出、转换和边界](#643-四类-flow输入输出转换和边界)
  - [6.4.4 一段伪代码看清 Harness 的接力顺序](#644-一段伪代码看清-harness-的接力顺序)
- [6.5 可观测性：先看见状态如何流动，才谈得上稳定](#65-可观测性先看见状态如何流动才谈得上稳定)
  - [6.5.1 线上故障最怕“看起来都成功”](#651-线上故障最怕看起来都成功)
  - [6.5.2 可观测性记录的是状态链，不是流水账](#652-可观测性记录的是状态链不是流水账)
  - [6.5.3 六类观测对象：从状态变化到外部副作用](#653-六类观测对象从状态变化到外部副作用)
  - [6.5.4 指标把单次 Trace 变成系统健康信号](#654-指标把单次-trace-变成系统健康信号)
- [6.6 任务恢复：让中断的 Agent 任务可以继续，而不是重来](#66-任务恢复让中断的-agent-任务可以继续而不是重来)
  - [6.6.1 审批之后崩溃，不能简单重跑](#661-审批之后崩溃不能简单重跑)
  - [6.6.2 能力失败可以重试，任务恢复必须识别副作用](#662-能力失败可以重试任务恢复必须识别副作用)
  - [6.6.3 Checkpoint 保存的是可执行状态](#663-checkpoint-保存的是可执行状态)
  - [6.6.4 Resume 先做恢复检查，再让模型继续](#664-resume-先做恢复检查再让模型继续)
  - [6.6.5 Idempotency 防止恢复时重复执行写操作](#665-idempotency-防止恢复时重复执行写操作)
  - [6.6.6 Compensation：不能回滚时就设计补偿动作](#666-compensation不能回滚时就设计补偿动作)
  - [6.6.7 Replan 只重规划剩余任务](#667-replan-只重规划剩余任务)
  - [6.6.8 Escalation：恢复不了就交给人](#668-escalation恢复不了就交给人)
- [6.7 运行控制面：让 Agent 在资源、权限和风险边界内运行](#67-运行控制面让-agent-在资源权限和风险边界内运行)
  - [6.7.1 单任务跑通后，系统级问题才开始](#671-单任务跑通后系统级问题才开始)
  - [6.7.2 Admission Control：先挡住不该进入系统的任务](#672-admission-control先挡住不该进入系统的任务)
  - [6.7.3 Scheduling：多任务争抢资源时谁先跑](#673-scheduling多任务争抢资源时谁先跑)
  - [6.7.4 Budget Control：成本必须参与运行决策](#674-budget-control成本必须参与运行决策)
  - [6.7.5 Permission Control：权限不能靠模型自觉](#675-permission-control权限不能靠模型自觉)
  - [6.7.6 Circuit Breaker：局部异常要在扩散前熔断](#676-circuit-breaker局部异常要在扩散前熔断)
  - [6.7.7 Runtime Config：没有版本就无法回放和回滚](#677-runtime-config没有版本就无法回放和回滚)
- [6.8 从单次成功到持续演进：Runtime 架构如何支持迭代](#68-从单次成功到持续演进runtime-架构如何支持迭代)
  - [6.8.1 一次跑通不代表系统变好了](#681-一次跑通不代表系统变好了)
  - [6.8.2 Runtime 数据能反向暴露能力失效点](#682-runtime-数据能反向暴露能力失效点)
  - [6.8.3 迭代闭环：从 Trace 到策略调整](#683-迭代闭环从-trace-到策略调整)
  - [6.8.4 有些任务应该从 Agent 退回 Workflow](#684-有些任务应该从-agent-退回-workflow)
- [本章速记](#本章速记)
- [课后练习](#课后练习)
- [验收标准](#验收标准)
- [参考资料](#参考资料)

---

# 6.1 能力越多，Agent 反而越容易失控

## 6.1.1 八个能力都合理，组合起来却失控

一个销售团队做了一个线索处理 Agent。它接到一条新线索后，会自动完成这些步骤：

1. 用 RAG 检索客户公司资料。
2. 用 Planning 制定跟进计划。
3. 调用 CRM 工具读取历史记录。
4. 生成邮件草稿。
5. 通过 Human-in-the-loop 等待销售确认。
6. 写入 Memory，供后续跟进使用。
7. 如果邮件质量不高，再触发 Reflection 修改。
8. 如果任务复杂，再交给多个子 Agent 分工。

每个能力单独看都合理。RAG 解决知识问题，Planning 解决多步骤问题，CRM 工具连接业务系统，Human-in-the-loop 控制风险，Memory 延续上下文，Reflection 改善质量，Multi-Agent 支持复杂分工。

但上线两周后，团队遇到的不是“能力不够强”，而是“系统不知道自己在干什么”：

- 计划状态和执行状态不一致：计划里说先查 CRM，实际先写了邮件。
- RAG 证据被当成确定事实：模型把一篇过期新闻当成当前客户战略。
- Reflection 改写了原始用户目标：销售只想要草稿，Agent 变成了自动制定整套销售方案。
- Human 修改没有回写状态：销售改过邮件后，Memory 里保存的仍是旧版本。
- 工具调用失败后重复执行：CRM 里出现两条重复跟进记录。
- 多个 Agent 对任务理解不一致：研究 Agent 说客户适合高端方案，邮件 Agent 继续使用低价话术。

这就是能力堆叠的典型失败：每个模块都“能跑”，组合起来却“不受控”。

## 6.1.2 Demo 只要能跑，生产必须能解释和恢复

Demo Agent 通常只要证明一件事：模型能不能基于上下文调用工具，拿到结果，再继续回答。

生产 Agent 要回答的问题更多：

```text
这次任务的目标是什么？
现在执行到哪一步？
哪些信息正在影响判断？
哪些动作已经对外部系统产生副作用？
如果中断，应该从哪里恢复？
如果结果错误，能不能回放当时的状态？
哪些动作必须经过人类确认？
成本、延迟、失败率是否还在可接受范围内？
```

如果这些问题都靠 prompt 里的自然语言来回答，系统很快会失控。Prompt 适合给模型提供当前轮的工作材料，不适合承担系统状态、权限、恢复、审计和治理的全部职责。

## 6.1.3 每加一个能力，都要回答四个运行问题

很多 Agent 项目会经历一个相似的路径：

```text
第 1 周：LLM + Tool，效果不错
第 2 周：加入 RAG，解决知识不足
第 3 周：加入 Memory，解决跨会话延续
第 4 周：加入 Planning，支持长任务
第 5 周：加入 Reflection，提高输出质量
第 6 周：加入 Human Review，控制风险
第 7 周：加入 Multi-Agent，处理复杂任务
第 8 周：任何问题都不知道是谁造成的
```

问题不是这些能力不该加，而是每加一个能力，都必须同时回答四个运行问题：

1. 它什么时候被触发？
2. 它能读取哪些状态？
3. 它能修改哪些状态？
4. 它失败后由谁接管？

如果回答不了，能力越多，系统越难调试、越难恢复、越难治理。


# 6.2 从能力模块到运行架构：Harness 才是系统中枢

## 6.2.1 Harness 不是第八个能力，而是能力的运行中枢

很多人第一次听到 Harness，会把它理解成“又一个框架组件”。这会误导架构判断。

Memory 是能力模块，RAG 是能力模块，Planning 是能力模块...，Harness 不是和它们并列的又一个能力模块，而是管理这些能力如何被调用、协作、约束和恢复的运行系统。

可以把 Agent 系统分成三层：

```text
基础执行层
- LLM Loop
- Tool Use

增强能力层
- Memory
- Context Engineering
- RAG
- Planning
- Reflection
- Multi-Agent
- Human-in-the-loop

运行架构层
- State Management
- Orchestration
- Flow Control
- Observability
- Recovery
- Runtime Control
```

第 3 章和第 4 章主要在基础执行层。第 5 章主要在增强能力层。第 6 章进入运行架构层。

## 6.2.2 Harness 管的是状态、边界、恢复和证据链

Harness 至少承担七类职责：

```text
状态保存：任务目标、执行进度、上下文证据、工具结果、审批状态。
能力触发：什么时候调用 RAG、Planning、Reflection、Human Review 或子 Agent。
状态流转：能力输出如何写回 Runtime State，哪些输出能影响后续步骤。
失败恢复：中断后从哪里恢复，哪些动作不能重复，哪些副作用需要补偿。
权限控制：当前任务能访问哪些数据、调用哪些工具、执行哪些动作。
过程记录：每次状态变化、能力调用、策略判断和外部动作都有 trace。
资源约束：token、模型调用次数、工具调用次数、并发、延迟和预算上限。
```

Harness 的设计不是把模型管死，而是把可自动化的部分交给模型，把不可越界的部分交给系统。


# 6.3 状态中心：把前面学过的能力纳入同一套运行状态

## 6.3.1 崩溃后要恢复的不是聊天记录

继续看销售线索处理 Agent：

```text
用户目标：分析一条销售线索，并生成跟进邮件草稿
执行过程：Planning 生成计划 -> RAG 查客户资料 -> Tool 读 CRM -> LLM 写邮件 -> Human 审批 -> Memory 写入后续跟进信息
```

如果系统只依赖 prompt 往下跑，会很快出现几个问题：

- 用户原始目标是什么，后面是否被 Reflection 改写了？
- Planning 生成了几步计划，现在执行到哪一步？
- RAG 检索到的信息来自哪里，可信度够不够？
- CRM 工具是否已经写入过状态，重试会不会重复写？
- Human 审批的是哪一版邮件，审批结果有没有覆盖旧计划？
- Memory 写入的是事实、偏好，还是一次临时判断？
- 如果系统中断，下一次应该从哪里恢复？

所谓 Runtime State，不是抽象名词，而是 Agent 运行到真实业务里之后必须回答的问题。

## 6.3.2 六类 State：把混在 prompt 里的东西拆开

本课程把 Runtime State 拆成六类。这不是业界统一模式，而是一组帮助你分析 Harness 的架构视角：

```text
Task State       -> 目标管理：这次任务到底要完成什么？
Execution State  -> 流程管理：现在执行到哪里，失败后从哪里恢复？
Context State    -> 信息管理：当前判断依据是什么，来源和可信度如何？
Capability State -> 能力管理：哪些增强能力参与了，它们产生了什么影响？
Control State    -> 边界管理：当前允许做什么，不允许做什么？
Trace State      -> 证据管理：事情是怎样一步步发生的？
```

不同框架会有不同实现。LangGraph 会把短期 thread-scoped 状态放进 checkpoint，把跨线程长期信息放进 store；OpenAI Agents SDK 会用 sessions 维持 agent loop 的工作上下文，并通过 tracing 观察流程；LlamaIndex Workflows 会用 event、step 和 context store 表达步骤、流转与共享状态。名字不重要，重要的是这些系统都没有把运行状态完全交给 prompt。

## 6.3.3 每一轮 Harness 都在读写状态

一个最小 Harness 循环可以这样理解：

```text
1. Read State
读取 Task / Execution / Context / Capability / Control

2. Decide
判断下一步要调用模型、RAG、工具、Reflection、Human Review，还是终止任务

3. Check Policy
用 Control State 检查权限、风险、预算、重试上限

4. Execute
执行对应能力或工具

5. Write State
把结果写回 Execution / Context / Capability / Control

6. Append Trace
记录本轮发生了什么、为什么发生、产生了哪些状态变化

7. Continue or Stop
根据 Task State 和 Execution State 判断继续、恢复、交给人或结束
```

Prompt 里所有东西都是混在一起的；Runtime State 的价值，是把目标、流程、上下文、能力调用、控制策略和运行证据拆成可管理的结构。


## 6.3.4 Task State：把用户请求变成任务契约

Task State 的重点不是把用户说过的话完整保存下来，而是把一个开放请求转成 Harness 可以判断、推进和终止的任务契约。

```yaml
task_id: lead-20260708-001
user_goal: 分析这条销售线索并生成一封跟进邮件草稿
success_criteria:
  - 邮件包含客户业务背景
  - 邮件引用 CRM 中最近一次互动
  - 邮件不得自动发送
scope:
  allowed:
    - 读取 CRM
    - 检索公开资料
    - 生成邮件草稿
  forbidden:
    - 自动发送邮件
    - 修改报价
    - 写入长期 Memory 前跳过审批
status: running
```

Task State 回答的是：这次运行到底服务于什么目标，什么条件下可以说任务完成，什么变化意味着任务已经偏离。

它的关键取舍是：目标要足够明确，能支持 Planning、审批和完成判断；但又不能把早期理解写死，导致后续澄清、范围调整和人工修正无法进入系统。

## 6.3.5 Execution State：让 Agent Loop 可以暂停和接上

Execution State 的重点不是记录所有中间动作，而是把 Agent Loop 从连续对话变成可以暂停、恢复、回退和接管的流程。

```yaml
plan:
  - id: step-1
    name: 读取 CRM 历史记录
    status: done
    external_effect: read_only
  - id: step-2
    name: 检索客户公开资料
    status: done
  - id: step-3
    name: 生成邮件草稿
    status: done
  - id: step-4
    name: 等待销售审批
    status: waiting_human
resume_from: step-4
last_checkpoint_id: ckpt-17
```

好的 Execution State 应该围绕恢复点、关键进度和不可重复动作来设计。记录太粗，失败后只能从头再来；记录太细，状态维护成本会上升，还可能让系统被历史步骤绑死。

## 6.3.6 Context State：让信息有来源、边界和有效期

Context State 的重点不是“把更多信息塞给模型”，而是让 Harness 知道哪些信息正在影响判断，以及这些信息从哪里来、适用于哪里、什么时候应该失效。

```yaml
evidence:
  - id: rag-42
    kind: retrieved_doc
    source: public-news
    created_at: 2026-07-08T10:12:00+08:00
    confidence: medium
    expires_at: 2026-08-08T00:00:00+08:00
    used_by_steps: [step-3]
  - id: crm-7
    kind: tool_result
    source: crm.get_interactions
    confidence: high
    permissions: [sales-read]
```

这里的核心取舍是信息完整性和上下文污染之间的取舍。信息太少，模型会猜；信息太多，旧信息、低可信信息和跨任务信息会混在一起，反而降低判断质量。

## 6.3.7 Capability State：记录哪些能力改变了任务走向

Capability State 记录哪些增强能力已经介入任务，以及它们的结果是否应该继续被信任。

```yaml
capability_runs:
  - capability: planning
    run_id: plan-3
    input_state: [task, context]
    output: execution_plan
    adopted: true
  - capability: reflection
    run_id: refl-2
    reason: 邮件语气过硬
    output: revised_draft
    adopted: true
    retry_count: 1
  - capability: memory
    run_id: mem-1
    output: candidate_memory
    adopted: false
    reason: 等待人工确认
```

能力之间不能只靠 prompt 隐式传话，否则 RAG、Memory、Planning、Reflection、Tool、Human-in-the-loop 的影响会混在一起。Capability State 不需要暴露每个能力的全部内部细节，但要记录能力调用的意图、结果、采纳状态和风险影响。

## 6.3.8 Control State：把权限、成本和风险变成硬边界

Control State 负责把权限、预算、风险和审批条件变成运行时可以执行的边界。

```yaml
budget:
  max_model_calls: 8
  used_model_calls: 4
  max_tool_calls: 12
  used_tool_calls: 5
permissions:
  crm: read_only
  email: draft_only
  memory: write_requires_approval
risk:
  level: medium
  requires_human_before:
    - send_email
    - write_long_term_memory
stop_conditions:
  max_reflection_rounds: 2
  max_runtime_minutes: 10
```

边界过松，系统可能在错误上下文中继续执行高风险动作；边界过紧，Agent 每一步都需要人工确认，自动化价值会消失。Control State 要把“可以自动做什么”“必须停下来等什么”“什么时候必须终止”表达清楚。

## 6.3.9 Trace State：给每次状态变化留下证据链

Trace State 不是多打一份日志，而是给状态变化留下可解释、可审计、可复盘的证据链。

```text
10:00 TaskCreated(task_id=lead-001)
10:01 PlanGenerated(plan_id=plan-3, adopted=true)
10:02 ToolCalled(crm.get_interactions, read_only=true)
10:03 ContextUpdated(evidence=[crm-7, rag-42])
10:04 DraftGenerated(draft_id=draft-1)
10:05 HumanApprovalRequested(target=draft-1)
```

Trace State 应该围绕关键决策、关键状态变更和关键外部动作保存证据，让调试、恢复和责任归因有依据。只记录最终结果，事后无法定位问题；记录所有原始输入输出，又会带来成本、隐私和噪声问题。


# 6.4 编排与状态流转：让能力在正确边界内接力

## 6.4.1 能力私下串联，系统就失去解释权

直觉上，可以让 RAG 把结果交给 Planning，让 Planning 把计划交给 Tool，让 Tool 把结果交给 Reflection。这个设计在 Demo 里看起来很顺，但在真实系统里会很快失控。

问题不在于能力之间不能合作，而在于它们不能绕过 Harness 私下传递影响。否则系统很难回答：

- 某个判断来自哪里？
- 某个工具为什么被调用？
- 某个上下文是否仍然可信？
- 某个高风险动作是否经过审批？
- 某个能力输出能不能进入长期 Memory？

能力协作的基本原则是：

```text
能力不直接把结果塞给下一个能力
  -> Harness 接收能力输出
  -> 写回 Runtime State
  -> 检查权限、风险、成本和边界
  -> 再决定下一步调用哪个能力
```

这个模型牺牲了一部分短路径效率，换来的是可解释、可恢复和可治理。Agent Runtime 的稳定性，很多时候就来自这种“多走一步”的中间层。

## 6.4.2 编排看的是当前状态，不是固定触发清单

编排不是为每个能力写一条固定触发规则，而是围绕当前 State 做判断。

```text
Task State       -> 任务是否仍在服务原始目标？
Execution State  -> 当前走到哪一步，是否需要继续、恢复或重规划？
Context State    -> 信息是否足够，是否需要检索、澄清或过滤？
Capability State -> 前面哪些能力已经运行，结果是否可信？
Control State    -> 当前动作是否允许自动执行？
Trace State      -> 历史上发生了什么，是否有失败模式正在重复？
```

这里的关键取舍是：编排策略要足够明确，避免模型凭感觉调用能力；但也不能僵硬到把所有任务都塞进固定流程。

例如：

- 简单问答不需要完整 Planning。
- 信息不足时应该先检索或澄清，而不是直接生成。
- 高风险写操作必须先检查权限和审批。
- Reflection 只应该在有明确反馈信号时触发，并有重试上限。
- Human Review 返回后，要接到等待中的 Execution State，而不是重新开始任务。

## 6.4.3 四类 Flow：输入、输出、转换和边界

### 6.4.3.1 Input Flow：输入不是越多越好

Input Flow 关心的是一个能力在运行前应该读取哪些 State。设计原则不是“把所有上下文都给它”，而是按任务阶段、能力职责和风险等级选择输入。

RAG 只需要用户目标、当前步骤和检索约束，不需要看到全部 CRM 私密记录。Reflection 需要看到候选输出和评价标准，不一定需要看到所有历史对话。子 Agent 只需要被委托任务的目标、权限和输出格式，不应该默认继承主 Agent 的全部上下文。

输入过少，能力会缺少判断依据；输入过多，能力会被无关信息污染，还可能接触到不该接触的数据。

### 6.4.3.2 Output Flow：输出必须变成可管理的状态

Output Flow 关心的是能力执行后的结果如何写回 Runtime。重要输出不能只追加到 prompt，也不能只留在某个能力内部，而要进入相应的 State，供后续编排、恢复、审计和治理使用。

```text
RAG 输出 -> Context State：证据、来源、置信度、有效期
Planning 输出 -> Execution State：步骤、依赖、恢复点
Reflection 输出 -> Capability State：修正建议、采纳状态、重试次数
Tool 输出 -> Execution / Context / Trace：结果、副作用、幂等键
Human 输入 -> Control / Execution / Trace：审批结论、覆盖范围、责任人
Memory 输出 -> Context / Store：写入候选、审批状态、撤销策略
```

写得太少，后续系统无法判断结果是否可信、是否可复用、是否产生副作用；写得太细，状态中心会变成低价值日志仓库。更合理的做法是只写入会影响后续决策的结果、证据、进度、审批、风险和外部影响。

### 6.4.3.3 Transformation Flow：状态变化要保留语义

Transformation Flow 关心的是能力如何改变状态的形态。用户请求可能变成任务契约，检索结果可能变成上下文证据，计划草案可能变成执行进度，人工审批可能改变控制边界。

如果一个能力只是产出文本，但 Harness 不知道它是在补充证据、修改计划、提出候选修正，还是确认风险放行，后续编排就会变得模糊。

状态转换要记录“这次转换改变了系统对任务的什么理解”，而不只是“数据从 A 到 B”。

### 6.4.3.4 Boundary Flow：每次流转都要控制影响范围

任何能力输出都不应该默认拥有全局影响力。

检索证据可以影响当前判断，但不一定能进入长期记忆。Reflection 可以提出修正，但不应该无限覆盖原始目标。工具结果可能改变外部系统，所以必须经过权限、风险和幂等检查。人工输入可以覆盖自动结果，但也需要留下 Trace。

边界设计的核心不是不信任能力，而是承认不同能力的输出具有不同可信度、不同副作用和不同传播范围。

## 6.4.4 一段伪代码看清 Harness 的接力顺序

```python
def run_next(task_id: str):
    state = state_store.load(task_id)

    decision = orchestrator.decide(
        task=state.task,
        execution=state.execution,
        context=state.context,
        capability=state.capability,
        control=state.control,
        trace=state.trace_summary,
    )

    policy_result = policy.check(decision, state.control)
    if not policy_result.allowed:
        return pause_or_escalate(task_id, policy_result)

    result = executor.execute(decision)
    state_update = state_mapper.map(decision, result)

    state_store.apply(task_id, state_update)
    trace.append(task_id, decision, result, state_update)

    return continue_or_stop(task_id)
```

这段代码的重点不是具体类名，而是顺序：先读状态，再做决策，再检查策略，再执行，再写状态，最后追加 trace。不要让能力之间绕过这个顺序直接传递结果。


# 6.5 可观测性：先看见状态如何流动，才谈得上稳定

## 6.5.1 线上故障最怕“看起来都成功”

一个客户投诉：Agent 自动生成的跟进邮件引用了错误的客户信息。

你打开日志，只看到：

```text
request received
llm call success
tool call success
response generated
```

这四行日志没有任何调试价值。真正要回答的问题是：

- 错误信息来自 RAG、Memory、CRM，还是模型幻觉？
- 哪一轮上下文组装把它放进了 prompt？
- 模型有没有引用证据 id？
- Reflection 有没有发现这个问题？
- Human Review 为什么没有拦截？
- Memory 是否把错误信息长期保存了？

这就是 Agent 可观测性和普通应用日志的区别。普通日志记录“函数有没有执行”，Agent 观测要记录“状态如何变化，决策为什么发生，能力输出如何影响后续步骤”。

## 6.5.2 可观测性记录的是状态链，不是流水账

可观测性是 Harness 把一次 Agent 任务的运行过程变成可观察的状态变化链：

```text
User Goal
  -> Task State 创建
  -> Planning 写入 Execution State
  -> RAG 写入 Context State
  -> Tool 更新 Execution / Context
  -> Human 更新 Control / Execution
  -> Memory 写入长期状态
  -> Final Result
```

关键问题不是最后答案对不对，而是：

- 每一步为什么发生？
- 哪个能力被调用？
- 它读取了哪些 State？
- 它写回了哪些 State？
- 状态变化是否符合预期？
- 成本、延迟、重试、人工介入发生在哪里？
- 如果结果错误，能不能回放到出错的状态变化？

## 6.5.3 六类观测对象：从状态变化到外部副作用

### 6.5.3.1 State Change：状态读写前后发生了什么

记录哪个 State 被读取、哪个 State 被写入、写入前后发生了什么变化。

```json
{
  "event": "state_changed",
  "state": "context",
  "added": ["rag-42", "crm-7"],
  "removed": ["old-memory-3"],
  "reason": "new evidence for current execution step"
}
```

### 6.5.3.2 Capability Run：能力为什么触发，结果是否采纳

记录哪个能力被触发，触发原因是什么，输入和输出是什么，结果是否被采纳。

```json
{
  "event": "capability_run",
  "capability": "reflection",
  "reason": "draft failed tone check",
  "adopted": true,
  "retry_count": 1
}
```

### 6.5.3.3 Decision Point：Harness 为什么选择下一步

记录 Harness 为什么选择下一步，为什么继续、暂停、重试、交给人或终止。

```json
{
  "event": "decision",
  "decision": "request_human_approval",
  "reason": "email_send is forbidden; draft approval required",
  "policy": "sales-email-v4"
}
```

### 6.5.3.4 Policy Check：哪些边界通过或拦截

记录权限、预算、风险、重试次数是否通过，哪些动作被拦截。

### 6.5.3.5 Human Event：人工输入如何改变状态

记录谁审批了什么，审批前后的状态变化是什么。Human-in-the-loop 不是简单的“用户点了确认”，而是一个改变 Control State 和 Execution State 的事件。

### 6.5.3.6 External Effect：外部副作用必须可追踪

记录调用了哪个外部工具，是否产生副作用，是否需要补偿或回滚。只读工具和写操作的 trace 粒度应该不同。

## 6.5.4 指标把单次 Trace 变成系统健康信号

Trace 解决单次任务复盘，指标解决系统趋势判断。Harness 至少应该收集这些指标：

```text
任务完成率
平均执行时长
平均成本
状态恢复成功率
工具调用失败率
重试率
人工介入率
能力误触发率
Memory 写入撤销率
多 Agent 冲突率
任务中断恢复率
```

这些指标可以帮助你发现架构问题。例如：

- Reflection 触发率很高但成功率很低，说明评价信号不可靠。
- Human Review 介入率持续升高，说明自动化边界可能设得太宽。
- Memory 写入撤销率高，说明记忆筛选策略太激进。
- 工具失败率高但重试成功率低，说明问题不是瞬时失败，应该熔断或降级。


# 6.6 任务恢复：让中断的 Agent 任务可以继续，而不是重来

## 6.6.1 审批之后崩溃，不能简单重跑

销售线索处理 Agent 执行到一半：

```text
计划已经生成
RAG 已经检索客户资料
CRM 已经写入一次跟进状态
邮件草稿等待销售审批
系统进程重启，或销售 2 小时后才审批
```

此时不能简单重新跑一遍。重新跑可能重复写 CRM，可能用新的 RAG 结果覆盖旧判断，可能生成另一版邮件，可能让审批结果接不到原来的任务上。

Harness 必须知道：

- 哪些步骤已经完成？
- 哪些信息仍然有效？
- 哪些工具调用已经产生副作用？
- 哪一步可以安全重试？
- 是否需要重新规划？
- 人工审批回来后应该接到哪个状态？

## 6.6.2 能力失败可以重试，任务恢复必须识别副作用

第 5 章可以讲某个能力遇到问题怎么修正，例如 RAG 没检索到怎么办、Reflection 不收敛怎么办、Tool 调用失败怎么办。

第 6.6 讲的是任务运行系统如何恢复：

```text
能力级异常处理：
某个能力失败了，怎么重试、替换或降级。

任务级恢复：
整个任务已经执行到一半，系统如何知道从哪里继续、哪些步骤不能重复、哪些副作用需要补偿。
```

能力级异常处理关注局部动作，任务级恢复关注整条任务链。

## 6.6.3 Checkpoint 保存的是可执行状态

每个关键步骤完成后，Harness 要把 Runtime State 持久化。

```text
Task State：任务目标和完成标准
Execution State：当前步骤和已完成步骤
Context State：可继续使用的信息
Capability State：哪些能力已运行
Control State：当前权限、预算、审批状态
Trace State：之前发生过什么
```

Checkpoint 的目的不是保存聊天记录，而是保存任务能继续执行所需的最小状态。

一个实用判断是：如果只给系统这个 checkpoint，不给它完整聊天记录，它能不能安全判断下一步？如果不能，checkpoint 缺了关键状态。

## 6.6.4 Resume 先做恢复检查，再让模型继续

恢复时，Harness 不应该把历史对话塞给模型，然后问“你觉得下一步该干什么”。它应该先做恢复检查：

```text
从哪一步继续？
当前 step 的输入是否仍然有效？
哪些工具不能重复调用？
哪些人工审批仍然有效？
是否需要重新读取上下文？
是否需要重新规划剩余步骤？
预算、权限和策略版本是否发生变化？
```

只有恢复检查通过，才进入下一轮执行。

## 6.6.5 Idempotency 防止恢复时重复执行写操作

任务级恢复最容易出事的地方，是重复执行已经产生外部影响的动作。

```text
重复写 CRM
重复发送邮件
重复创建工单
重复扣费
重复更新用户状态
```

Tool 调用结果必须写入 Execution State 和 Trace State，恢复时先检查动作是否已经执行过。

```yaml
tool_call:
  id: crm-write-17
  tool: crm.update_lead_status
  idempotency_key: lead-001:status:draft-created
  effect: write
  status: success
  external_ref: crm-event-8831
```

如果恢复时再次遇到同一个 idempotency_key，Harness 应该读取已有结果，而不是重新调用工具。

## 6.6.6 Compensation：不能回滚时就设计补偿动作

Agent 恢复不是数据库事务。很多真实世界动作无法真正回滚，只能补偿。

```text
邮件已经发送 -> 发送更正邮件
CRM 状态写错 -> 写入修正记录
任务分配错误 -> 创建重新分配动作
Memory 写入错误 -> 标记撤销或降低可信度
```

所以工具设计时要提前标注副作用类型：

```text
read_only        -> 可安全重试
idempotent_write -> 可用幂等键重试
non_idempotent   -> 必须记录外部引用，恢复时禁止自动重复
irreversible     -> 必须经过人工确认，并设计补偿动作
```

## 6.6.7 Replan 只重规划剩余任务

恢复不总是从原计划继续。有时上下文变化、人工审批结果变化、预算变化，原计划已经不适用。

```text
读取当前 Runtime State
  -> 判断原计划是否仍然有效
  -> 保留已完成步骤
  -> 只重新规划剩余步骤
  -> 写回新的 Execution State
```

关键是“只重新规划剩余步骤”。已经产生副作用的步骤不能被新计划当作不存在。

## 6.6.8 Escalation：恢复不了就交给人

任务级恢复也需要终止和升级条件：

```text
状态冲突无法自动解决
外部副作用不确定
多次恢复失败
风险等级超过阈值
人工审批超时
任务目标已经不明确
```

这些情况不应该让 Agent 继续猜，而应该进入 Human Review 或安全终止。


# 6.7 运行控制面：让 Agent 在资源、权限和风险边界内运行

## 6.7.1 单任务跑通后，系统级问题才开始

6.3 到 6.6 更关注单个任务的生命周期：

```text
State -> Orchestration -> Flow -> Observability -> Recovery
```

真实系统不是只跑一个任务。它会同时面对多个用户、多个任务、多个工具、多个风险等级和有限资源。

运行控制面要回答的是：

```text
哪些任务能进来？
哪些任务应该排队？
哪些任务需要降级？
哪些工具和数据可以访问？
哪些资源最多能消耗多少？
哪些异常需要熔断？
哪些配置需要被版本化和回放？
```

6.6 让一个任务断了还能接上；6.7 让整个 Runtime 在多任务、多用户、多风险、多资源约束下不被跑垮、不越权、不失控。

## 6.7.2 Admission Control：先挡住不该进入系统的任务

Admission Control 负责判断一个任务能不能进入 Runtime。

```text
需要判断：
- 任务类型是否被支持
- 用户或租户是否有权限
- 是否缺少必要输入
- 是否超过配额
- 是否属于高风险任务
- 当前系统负载是否允许接收
```

很多不稳定不是执行过程中产生的，而是系统一开始就接收了不该接收、无法完成、权限不够或风险过高的任务。

例如，一个普通销售账号提交“批量导出全部客户联系方式并生成外呼计划”。如果 Admission Control 不拦截，后面的 RAG、Planning、Tool、HITL 都会被迫处理一个本来就不该进入系统的任务。

## 6.7.3 Scheduling：多任务争抢资源时谁先跑

如果只是单用户、短任务、同步响应的对话式 Agent，任务排队和优先级通常被产品或平台隐藏。

但一旦 Agent 进入后台任务、批处理、多用户、多工具、长任务或人工审批场景，Scheduling 就会自然出现：

```text
VIP 客户投诉邮件需要 5 分钟内生成回复草稿
批量整理 300 条销售线索可以后台慢慢跑
周报生成任务今晚 10 点前完成即可
CRM API 正在限流，相关任务需要等待或降级
某个任务正在等待人工审批，应该释放执行资源，只保留状态
```

Scheduling 不是聊天产品里的表层体验，而是 Agent 从单次对话变成后台任务系统之后，Runtime 必须处理的执行顺序、并发和资源分配问题。

## 6.7.4 Budget Control：成本必须参与运行决策

Budget Control 不是简单记录花了多少钱，而是在任务运行中持续限制资源消耗。

```text
需要控制：
- 每个任务最多消耗多少 token
- 每个任务最多调用多少次模型
- 每个任务最多调用多少次工具
- 每个能力最多触发多少次
- 超预算后是降级、暂停、转人工，还是终止
```

没有成本、延迟、调用次数的观测，就无法做预算控制。预算控制也不应该只在账单层出现，它应该参与编排决策。

例如，当任务剩余预算只够一次模型调用时，Harness 不应该再触发 Reflection，而应该生成当前最佳结果并标注风险，或者暂停交给人。

## 6.7.5 Permission Control：权限不能靠模型自觉

Permission Control 负责限制任务能访问什么数据、调用什么工具、执行什么外部动作。

```text
需要控制：
- 当前任务能访问哪些用户数据
- 当前角色能看到哪些上下文
- 当前任务能调用哪些工具
- 哪些工具只读，哪些可写
- 哪些外部动作必须人工确认
- 数据能不能跨用户、跨任务、跨组织流动
```

第 4 章讲 Agent 如何调用工具；6.7 讲 Runtime 如何决定某个任务在当前权限下能不能调用这个工具。

不要把“请不要访问无关客户数据”只写进 prompt。权限必须在工具执行层和上下文组装层强制执行。

## 6.7.6 Circuit Breaker：局部异常要在扩散前熔断

Circuit Breaker 负责在局部异常扩散前暂停某条运行路径。

```text
触发条件：
- 某个工具失败率过高
- 某个外部系统响应变慢
- 某类任务成本异常升高
- 某个能力误触发过多
- 某个模型输出质量突然下降
- 某个用户或租户触发异常调用模式

处理方式：
- 暂停相关工具
- 降级为只读模式
- 暂停某类任务
- 切换模型或工具版本
- 强制进入 Human Review
- 临时关闭某类自动化动作
```

恢复机制是任务级，熔断机制是系统级。恢复关注“这个任务怎么继续”，熔断关注“这类问题不要继续扩大”。

## 6.7.7 Runtime Config：没有版本就无法回放和回滚

为了支持回放、回滚和对比，Runtime 需要记录每次任务使用的配置版本。

```text
需要记录：
- 模型版本
- Prompt 版本
- 工具版本
- 策略版本
- RAG 配置版本
- Memory 策略版本
- Orchestration 配置版本
```

否则出现问题时，很难回答：

```text
这次任务为什么和上次表现不一样？
是模型变了，prompt 变了，工具变了，还是策略变了？
能不能回滚到旧版本？
能不能对比两个配置版本的效果？
```

Runtime Config 让可观测性、恢复和持续演进都有版本依据。


# 6.8 从单次成功到持续演进：Runtime 架构如何支持迭代

## 6.8.1 一次跑通不代表系统变好了

Agent 项目最容易被单次成功误导。一次任务完成了，不代表系统稳定；一次回答正确了，不代表能力组合合理；一次用户满意了，不代表成本、风险和恢复路径可接受。

Runtime 架构的长期价值，是把每次运行留下来的状态、trace、失败记录和评估指标，变成系统改进的反馈。

## 6.8.2 Runtime 数据能反向暴露能力失效点

当 Harness 有了状态和 trace，你就可以系统性分析：

- 哪些能力经常被误触发？
- 哪些工具最容易失败？
- 哪类任务最需要人工介入？
- 哪类 Memory 写入容易被撤销？
- 哪些 Planning 模式经常走不通？
- 哪些任务成本过高？
- 哪些错误可以通过策略提前拦截？
- 哪些流程应该从 Agent 自动执行改为工作流控制？

这些问题靠读 prompt 和聊天记录很难回答，靠 Runtime State 和 Trace 才能回答。

## 6.8.3 迭代闭环：从 Trace 到策略调整

一个成熟的 Agent Runtime 应该形成这样的闭环：

```text
运行过程
  ↓
Trace 记录
  ↓
指标分析
  ↓
发现问题
  ↓
调整策略、状态模型或编排流程
  ↓
重新上线验证
```

举例：

```text
发现：销售邮件 Agent 的人工介入率从 18% 升到 46%
Trace 分析：多数介入发生在报价相关段落
状态分析：RAG 经常召回旧价格政策
调整：报价类证据增加有效期校验；高风险报价信息必须来自 CRM 工具而非 RAG
验证：人工介入率下降到 22%，错误报价率下降
```

这就是 Runtime 架构支持迭代的方式：不是凭感觉改 prompt，而是基于状态和 trace 找到具体失效点。

## 6.8.4 有些任务应该从 Agent 退回 Workflow

持续演进不总是意味着让 Agent 更自主。有时 trace 会告诉你：某类任务其实不需要动态 agent，固定 workflow 更稳定。

Anthropic 的工程实践里有一个重要区分：workflow 适合预定义路径，agent 适合模型动态决定过程。这个区分对产品落地很重要。

如果某类任务长期呈现这些特征：

- 步骤稳定，分支很少。
- 工具调用顺序固定。
- 错误主要来自越界，而不是能力不足。
- 用户更看重可预测性，而不是灵活性。

那它可能应该从“自主 Agent”退回“明确 Workflow + 局部 LLM 调用”。这不是倒退，而是成熟的系统设计。Harness 的数据应该帮助你做这种判断。

# 本章速记

第 5 章讲的是 Agent 有哪些增强能力，第 6 章讲的是这些能力如何被运行架构管理起来。Agent Runtime 的核心任务，是把 Memory、RAG、Planning、Reflection、Tools、Multi-Agent、Human-in-the-loop 等能力，从零散调用变成可调度、可交接、可恢复、可观测、可控制的系统。

一个稳定的 Agent 系统，不是能力越多越好，而是每个能力都知道什么时候该启动、能看到什么、能修改什么、失败后谁接管、运行过程如何被记录。Harness 不创造新的智能，它让已有的智能变得可控、可靠、可治理。第 6 章的最终目标，是让你从“会增强 Agent”，升级到“会架构 Agent 系统”。

# 课后练习

## 练习 1：为一个业务 Agent 画出 Runtime State

选择一个你熟悉的 Agent 场景，例如代码审查 Agent、销售线索 Agent、客服工单 Agent、个人知识助手或数据分析 Agent。

请按下面模板填写：

```text
业务场景：

Task State：
- 用户目标：
- 完成标准：
- 禁止范围：

Execution State：
- 主要步骤：
- 当前步骤：
- 可恢复点：
- 不可重复动作：

Context State：
- 信息来源：
- 可信度规则：
- 过期规则：

Capability State：
- 会用到哪些能力：
- 每个能力的输出是否会被采纳：
- 哪些能力需要重试上限：

Control State：
- 权限边界：
- 预算上限：
- 人工审批条件：

Trace State：
- 必须记录的关键事件：
- 出错后需要回放的证据：
```

合格标准：每一类 State 至少写出 3 条具体字段，并能说明其中 1 条字段如何影响恢复、审批或后续编排。

## 练习 2：设计一次中断恢复流程

沿用练习 1 的场景，构造一次任务中断：

```text
中断发生在哪一步：
中断前已经完成哪些动作：
哪些动作有外部副作用：
恢复时应该从哪里继续：
哪些动作禁止重复：
哪些信息需要重新验证：
什么时候必须交给人：
```

合格标准：恢复流程不能简单写“重新执行任务”。必须明确 checkpoint、resume point、幂等检查和人工升级条件。

## 练习 3：写一份 Harness Trace 样例

为同一个场景写出 8-12 条 trace 事件，至少覆盖：

```text
TaskCreated
PlanGenerated
ContextUpdated
CapabilityRun
PolicyCheck
ToolCalled
HumanEvent
StateChanged
TaskCompleted 或 TaskPaused
```

合格标准：每条 trace 至少包含 event、reason、state_delta 或 external_effect 中的两个字段。读者只看 trace，应该能复盘任务为什么走到最终结果。

## 练习 4：判断哪些流程应该自动化，哪些应该固定化

从你的场景中选出 3 类任务，分别判断它们更适合：

```text
固定 Workflow
Agent 动态决策
Workflow + 局部 Agent
```

输出格式：

```text
任务类型：
推荐模式：
原因：
- 步骤是否固定：
- 风险是否可控：
- 是否需要动态工具选择：
- 用户更看重稳定性还是灵活性：
```

合格标准：不能只写“复杂所以用 Agent”。必须说明为什么动态性带来的收益大于成本，或为什么固定流程更合适。

---

# 验收标准

完成本章后，你应该能够：

1. 解释 Harness 和 Memory、RAG、Planning、Reflection 等能力模块的区别。
2. 用 Task / Execution / Context / Capability / Control / Trace 六类状态分析一个 Agent 系统。
3. 说明为什么能力之间不应该绕过 Harness 直接传递结果。
4. 设计一个最小 Trace schema，用于回放 Agent 的关键状态变化。
5. 区分能力级异常处理和任务级恢复。
6. 为有副作用的工具调用设计幂等键、恢复检查和补偿动作。
7. 说明 Admission Control、Scheduling、Budget Control、Permission Control、Circuit Breaker 各自解决什么问题。
8. 基于运行数据判断某类任务应该继续用 Agent，还是退回固定 Workflow。

---

# 参考资料

- LangGraph Docs：Persistence, Checkpointers, Stores, Interrupts, Fault Tolerance, Observability。
- OpenAI Agents SDK Docs：Agent loop, Sessions, Guardrails, Handoffs, Human-in-the-loop, Tracing。
- LlamaIndex Workflows Docs：event-driven workflows, steps, shared state, validation, durable workflows。
- Anthropic Engineering：Building Effective AI Agents，尤其是 workflow 和 agent 的架构区分，以及“先用最简单方案，必要时再增加复杂度”的实践建议。
