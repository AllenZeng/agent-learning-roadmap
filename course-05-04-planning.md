# 第四章：Planning / Workflow Patterns

[返回课程五主文档](./course-05-00-scenario-enhancement.md) | [上一章](./course-05-03-memory.md) | [下一章](./course-05-05-reflection.md)

## 本章目录

- [4.1 任务变长后 Agent 开始漂移](#41-任务变长后-agent-开始漂移)
- [4.2 从 ReAct 到 LangGraph](#42-从-react-到-langgraph)
- [4.3 任务组织比单步决策更重要](#43-任务组织比单步决策更重要)
- [4.4 常见任务组织模式](#44-常见任务组织模式)
  - [Chain](#chain)
  - [Router](#router)
  - [ReAct Loop](#react-loop)
  - [Plan-Execute](#plan-execute)
  - [Graph](#graph)
- [4.5 从固定步骤到可回放图结构](#45-从固定步骤到可回放图结构)
- [4.6 常见失败与修正](#46-常见失败与修正)
- [4.7 什么时候不需要 Planning](#47-什么时候不需要-planning)

---

### 4.1 任务变长后 Agent 开始漂移

回到 1.1 的知识助手。你给它一个多步骤任务：

```text
帮我做发布准备：检查 README 完整性、跑一遍测试、整理 changelog、生成 release checklist。
```

Agent 开始工作。第一步，它读了 README，写了一段评论。第二步，它……开始去翻源码核实 README 里提到的一个细节。第三步，它又去搜了相关的 GitHub issue。五分钟后你回来检查，发现它偏离原始目标，不知道在做什么。你翻 trace 才发现：它在第 4 步之后就再也没碰过任何和"发布"相关的操作。

根因不是工具不好用，不是 State 丢了，不是没记住偏好。根因是：**裸 ReAct 循环没有"全局任务结构"的概念。** 它每步都在做局部最优的决策，但局部最优之和不一定能到达目标。就像一个没有导航的司机，每个路口都选看起来对的方向，但可能永远到不了目的地。

任务越长，越需要一种机制来回答：

- 要做哪些步骤？步骤之间的依赖关系是什么？
- 哪些步骤可以并行执行？
- 哪些步骤执行前需要用户确认？
- 某一步失败后，是重试、跳过、重规划还是停止？

这就是 Planning / Workflow Patterns 要解决的核心问题。

### 4.2 从 ReAct 到 LangGraph

Planning 在 Agent 领域不是一开始就有的。回顾一下演进：

**2022 年 10 月，ReAct 论文（Yao et al.）。** 论文的核心发现是：让 LLM 在"推理"和"行动"之间交替循环，能大幅提升复杂任务的完成率。但 ReAct 的模式是"每一步临场判断"——模型看到当前 Observation，决定下一步 Action。这对 3-5 步的任务有效，但步数一多就暴露了问题：模型没有全局视野，容易漂移。

**2023 年初，Plan-and-Execute 模式出现。** 思路很直接：让模型先把整个任务拆成执行计划，用户确认后再逐步执行。这解决了 ReAct 的"没有全局视图"问题，但引入了新问题——计划可能不可执行（模型列出的步骤在实际环境中无法完成），或者环境变化后原计划不再适用。

**2023 年下半年，图结构（Graph）思想兴起。** LangGraph、CrewAI 等框架开始把任务建模成节点和边的图——每个节点是一个动作或判断，边代表状态迁移，失败后可以跳回特定节点重试。图结构本质上是对 Plan-and-Execute 的泛化：计划不再是一维的步骤列表，而是一个可以有分支、回溯、并行路径的有向图。

**2024 年至今，Workflow Patterns 成为共识。** Anthropic 的"Building Effective Agents"文章确立了一个重要观点：大多数 Agent 场景不需要复杂的 Graph，简单的 Chain 或 Router 就能覆盖。关键不是"用不用 LangGraph"，而是"根据任务形态选择对应模式"。

### 4.3 任务组织比单步决策更重要

ReAct Loop 擅长动态决策，但不擅长天然保证全局结构。

复杂任务通常有几种形态：

| 任务形态 | 例子 | 适合模式 |
|---|---|---|
| 步骤固定 | 读取文件 -> 摘要 -> 输出 | Chain |
| 输入类型差异大 | 问答、写作、代码审查走不同路径 | Router |
| 工具选择动态 | 需要边查边决定下一步 | ReAct Loop |
| 任务可先拆解 | 发布准备、调研报告、代码迁移 | Plan-Execute |
| 状态和分支复杂 | 工单处理、审批流、多阶段任务 | Graph |

所以不要问"Planning 好不好"，而要问：

- 任务是否足够复杂，需要先拆解？
- 步骤是否稳定，可以固化成流程？
- 是否需要中途重规划？
- 用户是否需要确认计划？
- 失败后是否需要回到某个节点？

### 4.4 常见任务组织模式

#### Chain

Chain 是固定顺序执行。

```text
输入 -> 分类 -> 检索 -> 生成 -> 校验 -> 输出
```

适合步骤稳定、异常少的任务。优点是简单、可控、易调试。缺点是灵活性低。

#### Router

Router 根据输入类型或状态选择路径。

```text
用户请求
  -> 文档问答路径
  -> 代码审查路径
  -> 任务执行路径
```

适合多类型任务入口。关键是分类准确，以及分类失败后的兜底路径。

#### ReAct Loop

ReAct Loop 让模型根据当前状态选择工具并观察结果。

适合信息不完整、需要探索的任务。风险是步骤不稳定，需要停止条件、工具约束和 trace。

#### Plan-Execute

先生成计划，再按计划执行。

```text
目标 -> 计划 -> 用户确认 -> 执行步骤 -> 观察结果 -> 必要时重规划
```

适合中长任务。计划最好是结构化的，而不是一段漂亮文字。

#### Graph

Graph 把任务建模成节点和边：

- 节点表示动作、判断、工具调用、人工确认。
- 边表示状态迁移。
- 每个节点可以有输入、输出、失败路径。

Graph 适合复杂状态机、需要回放和恢复的任务。缺点是建模和调试成本高。

四种核心模式的关键接口骨架——核心区别在于"谁决定下一步"：

```python
# ── Chain：固定顺序，确定性最强 ──
def chain_execute(steps: list[Step], context: dict) -> dict:
    """每步的输出是下一步的输入，无分支"""
    for i, step in enumerate(steps):
        result = execute_step(step, context)
        if result.status == "error" and not step.allow_skip:
            return {"status": "failed", "failed_at": i, "error": result.error}
        context[step.name] = result.output
    return {"status": "completed", "context": context}

# ── Router：根据输入特征选择路径 ──
def router_execute(query: str, routes: dict[str, list[Step]]) -> dict:
    """分类器决定走哪条路径，失败时走 default 兜底"""
    category = classify(query, list(routes.keys()))
    selected = routes.get(category, routes["default"])
    return chain_execute(selected, {"query": query})

# ── Plan-Execute：先规划再执行，支持中途重规划 ──
def plan_execute(goal: str, tools: dict, max_retries: int = 2) -> dict:
    """生成计划 → 用户确认 → 逐步执行 → 失败时重规划"""
    plan = generate_plan(goal, tools)        # 结构化步骤列表
    if not user_confirm(plan):
        return {"status": "rejected"}
    
    for step in plan.steps:
        result = execute_step(step)
        if result.status == "error":
            if step.retries < max_retries:
                # 重规划：从当前状态生成新的后续步骤
                new_steps = replan(goal, plan.completed_steps, result.error)
                plan.replace_remaining(new_steps)
                continue
            else:
                return {"status": "failed", "step": step, "error": result.error}
        plan.mark_completed(step)
    
    return {"status": "completed", "result": plan.final_output}

# ── Graph：节点+边+状态机 ──
class WorkflowGraph:
    """节点是动作，边是条件跳转，每个节点有失败出口"""
    def __init__(self):
        self.nodes: dict[str, Node] = {}   # name → Node(action, next, on_error)
        self.edges: list[Edge] = []         # (from, to, condition)
    
    def add_node(self, name: str, action: callable, 
                 on_success: str = None, on_error: str = None):
        self.nodes[name] = Node(action, on_success, on_error)
    
    def run(self, entry: str, context: dict) -> dict:
        current = entry
        visited = set()
        while current and current not in visited:
            visited.add(current)
            node = self.nodes[current]
            result = node.action(context)
            context[node.name] = result
            current = node.on_error if result.error else node.on_success
        return {"status": "completed", "context": context}
```

> **选择指南**：任务步骤完全固定 → Chain；多类型入口 → Router；需要全局规划且有验证需求 → Plan-Execute；状态复杂、分支多、需要回放和恢复 → Graph。不要把简单任务硬塞进 Graph——那就像用 Kubernetes 部署一个静态网页。

### 4.5 从固定步骤到可回放图结构

Planning / Workflow Patterns 可以这样迭代：

| 阶段 | 做什么 | 适合目标 |
|---|---|---|
| V0：裸 ReAct | 模型逐步决定工具 | 探索任务形态 |
| V1：Checklist | 让模型先列出步骤清单 | 减少漏步骤 |
| V2：用户确认计划 | 执行前让用户修改计划 | 提升可控性 |
| V3：结构化 Plan | 每步包含目标、工具、输入、验收标准 | 支持执行和追踪 |
| V4：动态重规划 | 失败或环境变化时调整计划 | 支持复杂任务 |
| V5：Graph | 将任务节点、状态和分支显式化 | 支持恢复、评测、回放 |

初学阶段建议做到 V2 或 V3。Graph 等到状态和分支真的复杂时再引入。

### 4.6 常见失败与修正

| 失败模式 | 表现 | 可能原因 | 修正方向 |
|---|---|---|---|
| 计划不可执行 | 步骤看似合理但无法落地 | 没有工具和环境约束 | 计划中绑定工具和验收标准 |
| 计划过细 | 生成大量无意义步骤 | 追求形式完整 | 限制步骤数和粒度 |
| 执行偏离计划 | 执行时忘记原计划 | 状态没有记录当前步骤 | 每步执行后更新状态 |
| 不会重规划 | 工具失败后硬继续 | 没有失败分支 | 增加重规划触发条件 |
| 过度工程化 | 小任务也上 Graph | 技术驱动 | 从 Chain / Router 开始 |
| 用户不买账 | 计划不符合用户真实目标 | 缺少确认节点 | 计划执行前让用户确认 |

### 4.7 什么时候不需要 Planning

以下场景不需要复杂 Planning：

- 任务一步就能完成。
- 两三步固定流程已经足够。
- 用户更想要快速结果，不需要先看计划。
- 计划无法验证，只是生成一段中间文本。
- 任务由确定性业务流程稳定承载。
- 引入计划后成本和延迟明显上升，但质量没有提升。

实用判断：

```text
如果问题主要是”漏步骤、走偏、无法恢复”，考虑 Planning。
如果问题只是”某一步工具调用错了”，先修工具机制。
```

> **这个故事还没完。** Planning 让 Agent 有了全局任务视图，发布准备不再漏步骤。但新问题来了：Agent 执行到”运行测试”这一步时测试失败了，TypeError 清清楚楚地打在日志里——Agent 看到了，却继续写 changelog，没有停下来分析为什么失败。它缺少”失败→分析→修正→重试”的能力。这就是下一章要讲的 Reflection。

---
