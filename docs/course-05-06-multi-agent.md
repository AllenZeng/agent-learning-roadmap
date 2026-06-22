# 第六章：Multi-Agent：角色分工能力

[返回课程五主文档](./course-05-00-scenario-enhancement.md) | [上一章](./course-05-05-reflection.md) | [下一章](./course-05-07-composition.md)

## 本章目录

- [6.1 单个 Agent 的角色开始过载](#61-单个-agent-的角色开始过载)
- [6.2 AutoGen、CrewAI 和"多智能体"的诱惑](#62-autogencrewai-和多智能体的诱惑)
- [6.3 多 Agent 不是多写几个角色 Prompt](#63-多-agent-不是多写几个角色-prompt)
- [6.4 分工、并行、互审和协调](#64-分工并行互审和协调)
- [6.5 从 Reviewer 到 Supervisor](#65-从-reviewer-到-supervisor)
- [6.6 常见失败与修正](#66-常见失败与修正)
- [6.7 什么时候不需要 Multi-Agent](#67-什么时候不需要-multi-agent)

---

### 6.1 单个 Agent 的角色开始过载

回到 1.1 的知识助手。现在它有了 RAG（能搜笔记）、Memory（记得偏好）、Planning（任务不漂移）、Reflection（错了会修正）。你觉得它已经很强了。

你让它写一份技术方案，然后从安全角度审查。它写完后，你说："现在从安全角度审查这个方案。"它输出：

```text
经过审查，该方案在安全方面没有明显问题。建议按计划实施。
```

你作为人类审了一眼，立刻发现了三个问题：方案没有考虑输入校验、API 密钥明文写在配置文件里、权限模型缺少最小权限原则。Agent 不是看不到这些问题——如果让它从零开始做安全审查，它可能能发现。问题是它刚刚才"作为作者"写完了方案，现在要让同一个大脑"作为审查者"审视自己的作品。

这是典型的**角色过载**：单一 Agent 上下文里同时承载了创作者、审查者、执行者、总结者等多个角色。这些角色有不同的目标、不同的判断标准、需要关注不同维度的信息。把它们全塞进一个上下文，结果就是互相干扰、先入为主、无法真正"切换视角"。

还有另一种过载：**并行需求**。调研任务需要同时阅读 10 篇文档，每篇文档的分析互不依赖。单 Agent 只能串行阅读——读完一篇再读下一篇——即使这些任务完全可以并行。

这就是 Multi-Agent 要解决的最后一类问题。

### 6.2 AutoGen、CrewAI 和"多智能体"的诱惑

Multi-Agent 这个概念有两股推动力：

**学术线：Multi-Agent Debate 和角色分工。** 2023 年，多个研究团队发现让多个 LLM 实例从不同立场辩论，能提升复杂推理任务的准确率。核心发现是：当多个 Agent 被迫互相质疑时，错误更容易被暴露和修正——这比单个 Agent 的 Self-Reflection 更有效，因为外部质疑比自我审视更客观。

**工程线：任务并行化和上下文隔离。** 随着 Agent 任务的复杂度上升，开发者发现单个 Agent 的上下文窗口是瓶颈——所有工具结果、历史决策、中间推理全挤在一个窗口里。把不同子任务分给不同 Agent，每个 Agent 有自己的上下文窗口，天然实现了信息隔离。同时，独立的子任务可以并行执行，降低端到端延迟。

**2023 年底，框架爆发。** Microsoft 发布了 AutoGen，CrewAI 和 ChatDev 等框架相继出现。它们的共同思路是：定义多个 Agent 角色，用消息传递机制协调它们的行为。但这也带来了"过度工程化"的风险——很多场景下，单个 Agent 配合良好的工具和上下文管理就能完成，引入 Multi-Agent 只会增加通信成本和调试难度。

### 6.3 多 Agent 不是多写几个角色 Prompt

Multi-Agent 的价值不在于把一个 Agent 改名成"研究员、工程师、审查员"。如果这些角色没有不同输入、不同工具、不同目标、不同验收标准，就只是 Prompt 装饰。

真正的 Multi-Agent 至少要有一个明确理由：

- **角色分工**：不同 Agent 负责不同目标。
- **并行处理**：多个子任务可以独立探索。
- **互相审查**：一个执行，一个审查。
- **视角对抗**：需要不同立场比较方案。
- **上下文隔离**：避免所有中间噪声污染主 Agent。

同时要意识到它的代价：

- 通信成本上升。
- Trace 更复杂。
- 多个 Agent 可能互相放大错误。
- 决策归属更难判断。
- 评测难度上升。

### 6.4 分工、并行、互审和协调

常见 Multi-Agent 模式：

| 模式 | 工作方式 | 适合场景 |
|---|---|---|
| Reviewer | 一个 Agent 执行，另一个审查 | 代码审查、文档审查、方案审查 |
| Supervisor | 主管 Agent 拆任务，Worker 执行 | 子任务边界清晰 |
| Parallel Specialists | 多个专家并行处理不同部分 | 调研、资料整理、多文件分析 |
| Debate | 多个 Agent 从不同立场辩论 | 方案权衡、风险判断 |
| Group Chat | 多 Agent 共享上下文协作 | 开放探索，但难控制 |
| Graph Collaboration | 用图结构定义协作关系 | 复杂流程、可回放协作 |

设计 Multi-Agent 时，要明确：

- 每个 Agent 的目标是什么。
- 每个 Agent 能看到什么上下文。
- 每个 Agent 能使用哪些工具。
- 谁做最终决策。
- Agent 之间如何通信。
- 中间结果如何汇总。
- 失败如何定位。

最推荐入门的模式是 Reviewer——分工清晰、评测容易、通信成本可控：

```python
# Reviewer 模式：一个执行，一个审查，结论带证据
class ReviewerPattern:
    """最简 Multi-Agent：Executor 产出 → Reviewer 审查 → 修正或通过"""
    
    def __init__(self, executor_agent, reviewer_agent):
        self.executor = executor_agent   # 有创作工具的 Agent
        self.reviewer = reviewer_agent   # 有审查工具但无创作工具的 Agent
    
    def run(self, task: str, review_criteria: list[str]) -> dict:
        """执行 → 审查 → 修正循环（最多修正两轮）"""
        # Step 1: Executor 产出
        draft = self.executor.run(task)
        
        for round_num in range(2):  # 最多修正两轮
            # Step 2: Reviewer 审查（独立上下文，独立工具）
            review = self.reviewer.run(
                task="审查以下产出，逐条对照审查标准，指出具体问题",
                context={
                    "original_task": task,
                    "output": draft.output,
                    "criteria": review_criteria  # ["安全性", "可维护性", "正确性"]
                }
            )
            
            if review.verdict == "approved":
                return {"status": "approved", "output": draft.output,
                        "review_rounds": round_num + 1}
            
            # Step 3: 反馈给 Executor 修正（只注入审查问题，不注入原始上下文）
            draft = self.executor.run(
                task=task,
                fix_instructions=review.issues  # 具体问题列表，不是审查 Agent 的主观评价
            )
        
        # 两轮未通过：标记分歧，由人工裁决
        return {"status": "disputed", "output": draft.output,
                "unresolved_issues": review.issues}
```

> **设计要点**：Executor 和 Reviewer 使用**不同的 System Prompt、不同的工具集、不同的上下文窗口**。如果只是改个名字把同一个 LLM 调两次，那不是真正的 Multi-Agent。`fix_instructions` 只传 Reviewer 发现的具体问题（如"第 3 行缺少输入校验"），不传 Reviewer 的主观评价（如"整体质量较差"）——让 Executor 根据事实修正，而不是被另一个模型的意见带偏。

### 6.5 从 Reviewer 到 Supervisor

Multi-Agent 不要一开始就做复杂群聊。可以这样迭代：

| 阶段 | 做什么 | 适合目标 |
|---|---|---|
| V0：单 Agent | 一个 Agent 完成全流程 | 建立基线 |
| V1：Reviewer | 增加审查 Agent | 提升质量和发现错误 |
| V2：子任务并行 | 不同 Agent 处理独立部分 | 降低耗时，隔离上下文 |
| V3：Supervisor | 主 Agent 分配任务、汇总结果 | 管理多分支任务 |
| V4：Debate | 多视角比较和反驳 | 方案权衡 |
| V5：Graph 协作 | 显式状态和协作关系 | 复杂生产系统 |

最推荐的起点是 Reviewer，因为它分工清晰、价值容易评测、通信成本相对可控。

### 6.6 常见失败与修正

| 失败模式 | 表现 | 原因 | 修正方向 |
|---|---|---|---|
| 角色重叠 | 多个 Agent 做同样的事 | 分工不清 | 明确输入、输出和验收标准 |
| 协调成本高 | 大量互相对话但结果少 | 缺少主持和停止条件 | 引入 Supervisor 和轮次上限 |
| 错误放大 | 一个 Agent 的错误被其他 Agent 接受 | 缺少证据要求 | 要求结论带证据和来源 |
| 难以调试 | 出错后不知道谁导致 | Trace 不完整 | 独立记录每个 Agent 的输入输出 |
| 成本失控 | 多 Agent 重复检索和推理 | 没有预算 | 设置并发、轮次、token 上限 |
| 决策不清 | 多个建议冲突 | 没有最终裁决者 | 指定最终决策 Agent 或人工确认 |

### 6.7 什么时候不需要 Multi-Agent

以下情况不建议引入 Multi-Agent：

- 单 Agent 加清晰工具和上下文管理已经能完成。
- 所谓多角色只是改了名字，没有真实分工。
- 任务无法并行。
- 没有 Trace 和评测，无法调试复杂协作。
- 成本和延迟已经紧张。
- 用户真正需要的是固定流程或人工确认，而不是多个 Agent。

实用判断：

```text
如果问题是”角色冲突、并行探索、互相审查”，可以考虑 Multi-Agent。
如果问题是”工具不好用、上下文混乱、状态不可恢复”，先修课程四和课程六的问题。
```

> **五类能力走完了。** 你跟着 1.1 的知识助手 Agent，从它第一次”不知道笔记内容”的问题开始，依次给它接上了 RAG（能查资料了）、Memory（能记住偏好了）、Planning（长任务不漏步骤了）、Reflection（测试失败会修正了）、Multi-Agent（能审查自己的工作了）。每加一层，系统都有新能力——也有新复杂度。最后一章要回答的是：在真实项目中，这些能力怎么组合？按什么顺序引入？以及什么时候应该——坚决地——什么都不加。

---
