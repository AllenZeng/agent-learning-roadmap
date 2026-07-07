# Chapter 8: Multi-Agent -- from "one person works" to "one team works."

[Return Course Five Document](./course-05-01-scenario-enhancement.md) | [Previous Chapter](./course-05-07-human-in-the-loop.md) | [Next chapter](./course-05-09-composition.md)

## Table of contents of this chapter

- [8.1 Three types of hard ceiling for single Agent](#81-three-types-of-hard-ceiling-for-single-agent)
  - [8.1.1 Conflict of roles: creators cannot review their work](#811-conflict-of-roles-creators-cannot-review-their-work)
  - [8.1.2 Context squeezing: Too much middle reasoning has become noise](#812-context-squeezing-too-much-middle-reasoning-has-become-noise)
  - [8.1.3 Serial bottlenecks: undependent tasks queuing](#813-serial-bottlenecks-undependent-tasks-queuing)
  - [8.1.4 "More models" why not the answer?](#814-more-models-why-not-the-answer)
- [8.2 What's the split?](#82-whats-the-split)
  - [8.2.1 Prompt not Multi-Agent](#821-prompt-not-multi-agent)
  - [8.2.2 Four different: input, tools, objectives, acceptance standards](#822-four-different-input-tools-objectives-acceptance-standards)
  - [8.2.3 Self-censorship List: Your scenes meet a few](#823-self-censorship-list-your-scenes-meet-a-few)
- [8.3 Reviewer Mode: Simple Multi-Agent Entry](#83-reviewer-mode-simple-multi-agent-mode)
  - [8.3.1 Model skeleton: one execution, one review](#831-model-skeleton-one-execution-one-review)
  - [8.3.2 Why independent context is more effective than changing role Prompt](#832-why-independent-context-is-more-effective-than-changing-role-prompt)
  - [8.3.3 Operational rollback: a single Agent self-review vs Reviewer review](#833-operational-rollback-a-single-agent-self-review-vs-reviewer-review)
  - [8.3.4 Obsolete boundary of Reviewer](#834-obsolete-boundary-of-reviewer)
- [8.4 Supervisor Model: Dismantling, Distribution, Summary](#84-supervisor-model-dismantling-distribution-summary)
  - [8.4.1 Model skeleton: one dispatcher + multiple implementers](#841-model-skeleton-one-dispatcher-multiple-implementers)
  - [8.4.2 Dismantling quality determines the value of the whole model](#842-dismantling-quality-determines-the-value-of-the-whole-model)
  - [8.4.3 Costs of consolidation - "Three Walkers ran out, Supervisor took longer to merge."](#843-costs-of-consolidation---three-walkers-ran-out-supervisor-took-longer-to-merge)
  - [8.4.4 Obsolete boundary of Supervisor](#844-obsolete-boundary-of-supervisor)
- [8.5 Parallel Specialists: same mission, multiple eyes](#85-parallel-specialists-same-mission-multiple-eyes)
  - [8.5.1 Distinction from Supervisor: same input, different dimensions](#851-distinction-from-supervisor-same-input-different-dimensions)
  - [8.5.2 Cross-dimensionalization is a parallel premise](#852-cross-dimensionalization-is-a-parallel-premise)
  - [8.5.3 Consolidation rule: conflict does not automatically abate](#853-consolidation-rule-conflict-does-not-automatically-abate)
- [8.6 Agent's settings and configurations -- how "different" landed.](#86-agents-settings-and-configurations----how-different-landed)
  - [8.6.1 Write Agent settings instead of Prompt](#861-write-agent-settings-instead-of-prompt)
  - [8.6.2 Mapping with four dimensions](#862-mapping-with-four-dimensions)
  - [8.6.3 Systems Prompt Design -- not just "rename."](#863-systems-prompt-design----not-just-rename)
  - [8.6.4 Allocation of tools — white list, not "please don't use"](#864-allocation-of-tools-white-list-not-please-dont-use)
  - [8.6.5 Model selection - not all players need the strongest model](#865-model-selection---not-all-players-need-the-strongest-model)
  - [8.6.6 Easing of parameters — different roles, different parameters](#866-easing-of-parameters-different-roles-different-parameters)
  - [8.6.7 Configuration management - from scattered locations to "configuration or code"](#867-configuration-management---from-scattered-locations-to-configuration-or-code)
- [8.7 Communication protocol-Agent cannot "what do you think?"](#87-communication-protocol-agent-cannot-what-do-you-think)
  - [8.7.1 Why is free dialogue a disaster?](#871-why-is-free-dialogue-a-disaster)
  - [8.7.2 Design communication formats by collaborative mode](#872-design-communication-formats-by-collaborative-mode)
  - [8.7.3 From internal communications engagement to Agent protocol](#873-from-internal-communications-engagement-to-agent-protocol)
- [8.8 award, suspension and background - Multi-Agent 'Rules of Traffic'](#88-award-suspension-and-background---multi-agent-rules-of-traffic)
  - [8.8.1 Adjudication mechanisms: who rules when differences arise](#881-adjudication-mechanisms-who-rules-when-differences-arise)
  - [8.8.2 Conditions for cessation: not unlimited return](#882-conditions-for-cessation-not-unlimited-return)
  - [8.8.3 Bottom strategy: what if Walker dies?](#883-bottom-strategy-what-if-walker-dies)
- [8.9 The truth of the cost - not just Token's bill](#89-the-truth-of-the-cost---not-just-tokens-bill)
  - [8.9.1 An estimated comparative bill](#891-an-estimated-comparative-bill)
  - [8.9.2 Delay magnification: the real cost of communications travel](#892-delay-magnification-the-real-cost-of-communications-travel)
  - [8.9.3 Long-term costs: Trade complexity and difficulty of taking over](#893-long-term-costs-trade-complexity-and-difficulty-of-taking-over)
- [8.10 After-school exercise: write the subvisor dismantling to implementable](#810-after-school-exercise-write-supervisor-dismantling-to-implementable)

---

## 8.1 Three types of hard ceiling for single Agent

Before discussing how Multi-Agent designed it, we need to figure out a more fundamental question: **Where exactly is Agent's card?** If you don't understand the question, then you introduce Multi-Agent probably is "structure for architecture."

The single Agent capacity bottleneck is not "not smart enough" but structural. There are three types of hard ceilings that correspond to three different patterns of failure.

### 8.1.1 Conflict of roles: creators cannot review their work

Back to the scene at the beginning of this chapter. After the knowledge assistant wrote the API technology program, you let it be reviewed from a security perspective. It says "no obvious problem" -- and you look at three security hazards.

This is not an issue of attitude, but of mechanisms. The same Agent created a lot of middle reasoning under the "Creative Mode" - – "In order to facilitate local development, let's simplify the power model first with an explicit key, then refine it later" – these reasonings are a reasonable trade-off at the time of creation, but they remain in the context. And when you switch it to "review mode," these reasonings become preconceived "explains": seeing the explicit key, it's thinking, "This is for the convenience of development," not "This is a security loophole."

For example, it took you two hours to complete a 300-word technical program, and you were immediately asked to "check the program from a safety perspective." Even if you're a person with security experience, you'll defend your design unconsciously. The same brain, preconceived, is not about attitude, is about cognitive mechanisms. Same thing with Agent -- except that its "preliminary" expression is those tokens that already exist in the context. **The structural causes of role conflicts**: The creator's goal is to complete the programme and the examiner's goal is to identify the problem. These two objectives are naturally contradictory. Let the same context and the same target function serve both conflicting objectives - – The result is a compromise between objectives, and the review becomes an exercise.

### 8.1.2 Context squeezing: Too much middle reasoning has become noise

When single Agent handles complex tasks, a large number of intermediates are piled up in context windows: drafts of the first edition, track of failed attempts, results of exploratory searches, provisional records of all kinds "to be written down and used later".

These things were valuable at the moment they were produced. But when Agent needed to judge on the basis of the final output, these intermediate reasoning became **noise** — they took up context space, distracted attention and introduced outdated assumptions.

This is typical of the crowding:

```text
Agent 上下文窗口（简化示意）：
┌────────────────────────────────────────────────────────────┐
│ System Prompt (500 tokens)                                 │
│ 任务：写技术方案 + 安全审查                                  │
├────────────────────────────────────────────────────────────┤
│ 用户消息 (100 tokens)                                       │
├────────────────────────────────────────────────────────────┤
│ 第 1 轮：尝试用方案 A，发现不合理，放弃 (800 tokens)         │  ← 噪声
│ 第 2 轮：尝试用方案 B，写了一部分 (1200 tokens)              │  ← 部分噪声
│ 第 3 轮：完成方案 B 的初稿 (2000 tokens)                     │  ← 有用
│ 检索中间结果：关于 API 设计的 5 篇笔记摘要 (1500 tokens)     │  ← 部分噪声
│ 第 4 轮：润色方案 (800 tokens)                              │  ← 噪声
├────────────────────────────────────────────────────────────┤
│ 用户："现在从安全角度审查"                                   │
│ Agent 需要在上述全部上下文中做安全判断                        │
│                                                             │
│ 问题：它看到了第 1 轮中"为了简化先用明文"的推理，              │
│ 这个推理会在审查时变成"这是有意为之，不是问题"                 │
└────────────────────────────────────────────────────────────┘
```
**The structural root cause of the squeezing of the context**: The context window for single Agent is the "public pool" of all information. The middle product of the creation process is mixed with the final output, and Agent can't distinguish between "this is the final decision" and "this is an abandoned attempt". At the time of the review, the historical information had polluted the judgement.

### 8.1.3 Serial bottlenecks: undependent tasks queuing

The first two are quality issues and the third is speed.

The knowledge assistant received a research mission: "Help me look into the four main directions of the Agent architecture - Tool Use, Memory, Planning, Multi-Agent - and give me an update on each of them. "Single Agent treatment:

```text
时间线（串行执行）：
├─ [0:00-1:30] 调研 Tool Use：检索笔记 + 搜索最新资料 + 整理输出
├─ [1:30-3:00] 调研 Memory：检索笔记 + 搜索最新资料 + 整理输出
├─ [3:00-4:30] 调研 Planning：检索笔记 + 搜索最新资料 + 整理输出
├─ [4:30-6:00] 调研 Multi-Agent：检索笔记 + 搜索最新资料 + 整理输出
└─ [6:00-7:00] 汇总四份调研，生成最终报告

总耗时：约 7 分钟
```

But look closely at these four research missions — they are not dependent on each other. The study Memory does not have to wait for the results of Tool Use. They can be carried out simultaneously. **The structural causes of the serial bottlenecks**: single Agent has only one execution thread. Even if there is no dependency between mandates, there can be only one. This is not a question of the speed of the model — the speed of the model's reasoning, and the total time of queuing four tasks is the sum of four tasks.

### 8.1.4 "More models" why not the answer?

A natural idea is: will these problems be solved automatically when a stronger model comes out?

Nope. As these three types of ceiling are structural problems**, not capacity problems**.

- **Role conflict** is not a model that is not smart enough to read it — it is a conflicting goal in the same context. A stronger model might be better transposed between the two objectives, but a pre-emptive "interpretation" would soften the review criteria as long as creation and review shared the same context.
- **Context squeezing** is not the size of the context window of the model - it is the information structure. The larger window simply plugs in more noise and does not address the structural flaws of the "intermediate reasoning of pollution final judgment".
- **Serial bottlenecks** are more unrelated to modelling capabilities — one-way is one-way.

This is the rationale behind the existence of Multi-Agent: when the single Agent's **structure (rather than capacity) becomes a bottleneck, these structural limitations need to be broken with more than** examples, context, tool sets**.

---

## 8.2 What's the split?

The next step is not "defining Agent's Role" but to find out: **Multi-Agent's Distinction?**

### 8.2.1 Prompt not Multi-Agent

The easiest mistake: to write "System Prompt" as "create Argentina." Define three roles — researcher, engineer, examiner — to write to each role a piece of System Prompt, and then rotate the same model. It's not Multi-Agent, it's called role-playing.

The difference between role-playing and the nature of Multi-Agent:

```text
"假" Multi-Agent（改 Prompt）：
┌─────────────────────────────────────────────────────┐
│ 同一个 LLM 实例                                      │
│ 同一个上下文窗口                                     │
│ 同一个工具集                                        │
│                                                     │
│ Round 1: System = "你是研究员" → 产出调研报告         │
│ Round 2: System = "你是工程师" → 看到调研报告 + 所有  │
│          中间推理 → 产出技术方案                      │
│ Round 3: System = "你是审查员" → 看到技术方案 + 调研  │
│          报告 + 所有中间推理 → "没有明显问题"          │
│                                                     │
│ 三个角色共享同一个大脑、同一段记忆、同一套工具。        │
│ "审查员"看到了"研究员"和"工程师"的所有思考过程——       │
│ 包括那些"这里简化一下后面再说"的妥协。                 │
└─────────────────────────────────────────────────────┘

"真" Multi-Agent（独立实例）：
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Agent A: 研究员  │  │ Agent B: 工程师  │  │ Agent C: 审查员  │
│                 │  │                 │  │                 │
│ 上下文：         │  │ 上下文：         │  │ 上下文：         │
│ - 调研任务       │  │ - 技术方案任务    │  │ - 审查标准       │
│ - 检索结果       │  │ - 调研报告（最终） │  │ - 技术方案（最终）│
│                 │  │                 │  │ - 原始需求       │
│ 工具：           │  │ 工具：           │  │                 │
│ - 搜索          │  │ - 写文件         │  │ 工具：           │
│ - 检索笔记       │  │ - 读文件         │  │ - 读文件（只读）  │
│                 │  │                 │  │ - 安全扫描       │
│ 看不到：         │  │ 看不到：         │  │                 │
│ - 工程师的推理    │  │ - 研究员的中间推理 │  │ 看不到：         │
│ - 审查员的判断    │  │ - 审查员的判断    │  │ - 研究员的推理    │
│                 │  │                 │  │ - 工程师的妥协    │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

The key difference is not how well it is written in Prompt, but in **every Agent sees things differently and can do different things.**

### 8.2.2 Four different: input, tools, objectives, acceptance standards

The real Multi-Agent splits four dimensions. For example, the knowledge assistant's "writing technology program + security clearance" scene:

| Dimensions | Form Agent (self-review) | Multi-Agent（Author + Reviewer） |
|---|---|---|
|**Entered differently** | Author and Reviewer are in the same context. Reviewer "sees" the middle reasoning and compromise of Author. | The Author context requires documentation, notes search results, writing tools. Reviewer context **only** final option + review criteria not available for Author's draft and "simplified later." |
|**Different tools** | The same tool set -- it can write files and make security scans. | Author can write documents and retrieve notes. Reviewer can only read files, run safety scans -- **can't write** to make sure the examiner doesn't quietly "do it again" |
|**Different goals** | "Full the user's mission" -- the goal is vague and the sub-goals compromise. | Objective: Technical programmes with outputs to meet demand. Objective Reviewer: To find all issues that do not meet safety standards. **Targets do not compromise with each other** |
|**Different acceptance standards** | "As long as the user thinks it's okay," no objective criteria. | Author standard: Programme fully covers needs. Reviewer standard: review list adopted article by article, any one FAIL as a whole REJECT |**Of these four dimensions, at least two are different, and Multi-Agent is worth it.** If the two Agents have the same input, the same tools, the same goals and the same acceptance criteria - whatever name they are given, they are essentially the same Agent. You're just wasting token and delaying.

Here's one of the simplest criteria: **If you can't say two Agents, "What difference does it make?", then you don't need two Agents.**

### 8.2.3 Self-censorship List: Your scenes meet a few

Before introducing Multi-Agent, answer by article:

```text
□ 角色冲突：是否存在两个目标天然矛盾的角色？
   （例：创作者 vs 审查者、优化者 vs 安全评估者、推销者 vs 风险分析师）
   如果不存在天然矛盾，单 Agent + 清晰的 Prompt 通常就够了。

□ 独立上下文需求：一个角色的中间推理对另一个角色是噪声还是必要信息？
   （例：代码实现过程中的调试 trace 对安全审查是噪声；方案讨论中的妥协对最终验收是噪声）
   如果中间推理对所有角色都有用，那不需要拆分上下文。

□ 工具权限分离：是否有些操作不应该由同一个 Agent 负责？
   （例：批准部署 vs 执行部署、写代码 vs 合并到主分支、生成发票 vs 审批发票）
   如果所有操作可以被同一个 Agent 安全地完成，不需要拆分。

□ 并行可能性：是否存在互不依赖、可以同时执行的子任务？
   （例：调研四个独立方向、分析三个独立模块、从五个数据源并行拉取数据）
   如果任务有严格的顺序依赖，并行的价值为零。

□ 视角多样性：是否需要从不同立场、不同假设、不同风险偏好来审视同一个问题？
   （例：技术方案需要同时从成本、安全、可维护性三个角度评估）
   如果单一视角已经能覆盖所有关注点，不需要多视角。
```
**Introductory judgement**: satisfaction of at least two of these is worth serious consideration. When only one is satisfied, there is usually a simpler method (better Prompt, more detailed tool privileges, predefined checklist) to achieve similar results.

---

## 8.3 Reviewer Mode: Simple Multi-Agent Mode

Reviewer is the "Hello World" of Multi-Agent -- it only takes two Agents, the simplest mode of communication and the easiest to assess. If not even the Reviewer can't get away, let's not think about Supervisor, Debate or Graph Collaboization.

It solves only one problem: **implementers cannot review their outputs impartially.**

### 8.3.1 Model skeleton: one execution, one review

```text
Executor Agent（执行者）                   Reviewer Agent（审查者）
┌──────────────────────────┐              ┌──────────────────────────┐
│ System: 你是技术方案撰写者 │              │ System: 你是安全审查员     │
│                          │              │                          │
│ 工具：                    │              │ 工具：                    │
│  - 写文件                 │   最终产出    │  - 读文件（只能读！）       │
│  - 检索笔记               │─────────────►│  - 检索安全规范            │
│  - Web 搜索               │              │  - 检查清单核对            │
│                          │   审查意见    │                          │
│ 上下文：                   │◄─────────────│ 上下文：                   │
│  - 需求文档               │              │  - 最终产出（只有这个！）    │
│  - 笔记检索结果            │              │  - 审查标准清单            │
│  - 创作过程中的草稿和推理   │              │  - 安全规范文档            │
│                          │              │                          │
│ 目标：完成技术方案          │              │ 目标：找出所有安全问题       │
│ 验收：方案覆盖需求          │              │ 验收：审查清单逐条通过       │
└──────────────────────────┘              └──────────────────────────┘
```

Core skeleton code:

```python
# Reviewer 模式：最简 Multi-Agent，2 个 Agent + 结构化审查
class ReviewerPattern:
    """Executor 产出 → Reviewer 审查 → 修正或上报"""

    def __init__(self, executor: Agent, reviewer: Agent):
        self.executor = executor
        self.reviewer = reviewer

    def run(self, task: str, criteria: list[dict]) -> dict:
        """
        task: 用户任务描述
        criteria: 审查清单，每项是可逐条核对的检查项
          [{"id": "C1", "check": "所有用户输入是否经过长度校验？",
            "how_to_verify": "检查 API 端点定义中的参数声明"},
           {"id": "C2", "check": "API 密钥是否存储在环境变量中？",
            "how_to_verify": "搜索配置文件中是否包含 key=或 secret= 字面量"},
           ...]
        """
        # Step 1: Executor 产出
        draft = self.executor.run(task)

        for round_num in range(2):  # 最多修正两轮
            # Step 2: Reviewer 审查
            # 关键：reviewer 只收到最终产出和审查标准，收不到 executor 的中间推理
            review = self.reviewer.run(
                task="对照审查清单，逐条检查以下产出。给出具体的通过/不通过判断和证据。",
                context={
                    "original_requirement": task,
                    "artifact": draft.output,
                    "criteria": criteria
                }
            )

            if review.verdict == "approved":
                return {
                    "status": "approved",
                    "output": draft.output,
                    "review_rounds": round_num + 1,
                    "review_trace": review
                }

            # Step 3: Executor 修正
            # 关键：只传具体的 issues，不传 reviewer 的主观评价
            draft = self.executor.run(
                task=task,
                fix_instructions=review.issues  # 具体问题列表，不是"整体质量较差"
            )

        # 两轮未通过：标记分歧，人工裁决
        return {
            "status": "disputed",
            "output": draft.output,
            "unresolved_issues": review.issues,
            "message": "两轮修正仍未通过审查，需要人工裁决"
        }
```

> **Design element**: Exporter and Reviewer uses separate LLM examples - different Systems Prompt, different tool sets, different context windows.`fix_instructions`Only the specific questions found by Reviewer (e.g., "line 3 lacks input length verification") and no subjective evaluation by Reviewer (e.g., "of poor overall quality"). Let Executor modify it on the basis of facts, rather than being influenced by the subjective opinion of another model. The two-round cap is a protective mechanism — the marginal benefits of the third round of amendment are often insufficient to cover communication costs and decision-making fatigue.

### 8.3.2 Why independent context is more effective than changing role Prompt

The most critical mechanism of the Reviewer model is the independent context**. It's not "let the model think in a different angle" -- it's a different angle in the same context, and the first message is still there. The context of independence is the middle reasoning of Reviewer** not physically visible **Executor.

Specifically, Reviewer can't see these things:

| Execuator information in context but not available in Reviewer | Why can't Reviewer see it? |
|---|---|
| "In order to facilitate local development, you can store the key with a clear message." | It'll make Reviewer re-understand the word "security breach" to "intentional ad hoc solution." |
| "The permission model is simplified to an admin, then refined." | Reviewer, seeing this explanation, may no longer mark "the lack of minimal permission" as FAIL |
| First two versions of the three drafts (released) | Noise - not related to the final scenario, but may confuse the Reviewer's understanding of the programme structure |
| Executor's uncertainty and hesitation in writing. | It'll create unnecessary suspicion or let go of real flaws. |**The very nature of the context of independence is asymmetrical information** - and **the information deliberately designed is incorrect**. Execuator knows more than Reviewer, but some of the messages Reviewer shouldn't know -- it affects judgment. This is one of the reasons for "blindness" in reality: the reviewer does not know who the author is, not the question of competence, but the design of the system — blocking identity information to make judgement more objective.

### 8.3.3 Operational rollback: a single Agent self-review vs Reviewer review

Here's the end-to-end comparison with the Knowledge Assistant, Writing Technology Program + Security Review.

```text
═══════════════════════════════════════════════════════════════════
任务：写一份 API 模块技术方案，并从安全角度审查
═══════════════════════════════════════════════════════════════════

方式一：单 Agent（自审）
┌─────────────────────────────────────────────────────────────────┐
│ [10:00] Agent 写方案（35 秒）                                    │
│         产出：API 设计文档，含端点定义、数据流、配置说明            │
│                                                                 │
│ [10:01] 用户："现在从安全角度审查"                                │
│         Agent："经过审查，该方案在安全方面没有明显问题。"           │
│                                                                 │
│         隐藏的四个问题（审查漏掉的）：                               │
│         ① /api/data 端点没有输入长度限制                          │
│         ② API key 明文写在 config.yaml 中                        │
│         ③ 权限模型只有 admin 一种角色，所有操作需要 admin 权限      │
│         ④ requirements.txt 未锁定第三方依赖版本                   │
│                                                                 │
│         为什么漏掉？Agent 在写方案时的中间推理里包含了：              │
│         - "为了方便本地开发，先用明文"                              │
│         - "权限模型后续再细化"                                     │
│         这些推理在审查时变成了"解释"，削弱了审查标准。               │
└─────────────────────────────────────────────────────────────────┘

方式二：Reviewer 模式
┌─────────────────────────────────────────────────────────────────┐
│ [10:00] Author Agent 写方案（35 秒）                              │
│         产出：同上                                                │
│                                                                 │
│ [10:01] Reviewer Agent 收到：                                    │
│         - 最终方案文本（没有 Author 的中间推理）                    │
│         - 审查清单（4 项，每项有具体的 verify 方法）                │
│         - 安全规范文档（作为参考）                                  │
│         - 工具：读文件、检索规范、逐条核对                          │
│                                                                 │
│         Reviewer 逐条审查：                                       │
│         ┌─────────────────────────────────────────────────────┐  │
│         │ C1: 输入校验                                         │  │
│         │   verify: 检查 API 端点定义中的参数声明                │  │
│         │   结果: /api/data 端点 input 参数无长度限制 → FAIL    │  │
│         │   证据: api_schema.yaml 第 12 行                      │  │
│         │                                                      │  │
│         │ C2: 密钥管理                                         │  │
│         │   verify: 搜索配置文件中 key=/secret= 字面量          │  │
│         │   结果: config.yaml 第 8 行 api_key: "sk-abc123" → FAIL│  │
│         │   证据: config.yaml 第 8 行                           │  │
│         │                                                      │  │
│         │ C3: 权限模型                                         │  │
│         │   verify: 检查是否存在非 admin 的角色定义              │  │
│         │   结果: 只有 admin 角色，缺少 read/write 分离 → FAIL  │  │
│         │   证据: permissions.py 第 3-5 行                      │  │
│         │                                                      │  │
│         │ C4: 依赖安全                                         │  │
│         │   verify: 检查 requirements.txt 是否有版本锁定         │  │
│         │   结果: 所有依赖使用 >= 而非 ==，未锁定 → FAIL         │  │
│         │   证据: requirements.txt 全文                         │  │
│         └─────────────────────────────────────────────────────┘  │
│                                                                 │
│         verdict: rejected (4/4 FAIL)                             │
│         issues: [                                               │
│           {id:"C1", desc:"/api/data 缺少输入长度限制",            │
│            location:"api_schema.yaml:12", suggestion:"加 max_length"},│
│           {id:"C2", desc:"API key 明文存储",                     │
│            location:"config.yaml:8", suggestion:"改用环境变量"},  │
│           ...                                                   │
│         ]                                                       │
│                                                                 │
│ [10:02] Author 收到审查意见，逐条修正（25 秒）                     │
│                                                                 │
│ [10:03] Reviewer 第二轮审查：                                    │
│         C1: PASS  C2: PASS  C3: PASS  C4: PASS                  │
│         verdict: approved                                        │
│                                                                 │
│ 对比：                                                           │
│ 单 Agent 自审：漏了 4 个安全隐患，声称"没有明显问题"               │
│ Reviewer 模式：发现并修正了全部 4 个问题                          │
│ 额外成本：+1 分钟（Reviewer 审查 + Author 修正）+ $0.04 token    │
│ 收益：从"有安全漏洞上线"变为"通过安全审查清单"                      │
═══════════════════════════════════════════════════════════════════
```

### 8.3.4 Obsolete boundary of Reviewer

The Reviewer model works, but it works only under certain conditions. Here are its four failed borders: **Boundary I: Expiry when the list is vague.** If the review criterion is "Check if the program is safe" (one sentence), Reviewer's output will be the same as the single Agent self-censorship - "no obvious problem". The review list must be specific, article-by-article, with a clear verify methodology.

```text
模糊的审查标准：
  "检查方案是否安全" → Reviewer 输出"整体安全，没有明显问题"

具体的审查标准：
  "1. 所有用户输入是否经过长度和类型校验？验证方法：检查 API schema 中每个参数声明。
   2. 密钥是否存储在环境变量或密钥管理服务中？验证方法：grep config 文件中的 key= 模式。
   3. 是否存在非 admin 的角色定义？验证方法：检查权限模块中定义的角色列表。
   4. 第三方依赖是否锁定了版本号？验证方法：检查 requirements.txt 中的版本声明格式。"
```
**Boundary II: Reviewer lapses when no independent authentication tool is available.**If the Reviewer can only read the text of the scheme and then judge it is not different from the individual Agent self-examination. Reviewer must have a validation tool independent of Executor: read the original profile (rather than read the excurator's description in the program), run linter, retrieve the original security code. Core principle:**Reviewer validates "real things", not Executor "proclaimed things."****Boundaries III: Reviewer is too harsh to be locked.**If every recommendation of review is "must be modified," when Excelctor finishes the round, Reviewer finds a new problem... - Look, it's a new problem, not a problem that hasn't been fixed -- and then Execuator changes it, Reviewer discovers a new problem and never appears. Method of amendment: Distinguishing between "must modify" and "recommended to optimize"; must not exceed 5 and the recommendation does not block adoption.**Boundaries IV: Execuator learned the "prejudice" review list.**This is the most hidden pattern of failure. After a number of times, Execuator learned to proactively add to the program the description "Looks like a security measure" - "This module follows the best practice of safety" - "All inputs have been fully verified" - but these descriptions do not correspond to actual realization. After seeing these statements, Reviewer marked "Save security measures mentioned" in the check list. In practice, however, security measures have not been implemented. Method of amendment: To review the list from "Whether or not to mention" to "Whether or not to implement" - do not check that "the program discusses key management" but check that "the key in the program is actually stored in the environment variable (grep authentication). "

---

## 8.4 Supervisor Model: Dismantling, Distribution, Summary

Reviewer addresses the issue of "quality" — the implementer needs to be independently reviewed. But when the task itself can naturally be broken down into several non-dependent sub-tasks, the single Agent encounters the problem of **speed** - a chain bottleneck.

The Supervisor model uses a scheduler Agent to dismantle and aggregate, and multiple worker Agents are implemented in parallel.

### 8.4.1 Model skeleton: one dispatcher + multiple implementers

```text
Supervisor Agent                             Worker Agents
┌─────────────────────────┐       ┌─────────────────────────────────┐
│ 接收用户任务              │       │ Worker 1: 调研 Tool Use         │
│                         │       │  - 独立上下文                    │
│ 拆解为 N 个子任务：       │       │  - 独立检索工具                  │
│  - 明确边界               │───┬───│  - 输出：结构化调研结果           │
│  - 指定输出格式           │   │   │                                 │
│  - 指派 Worker           │   │   │ Worker 2: 调研 Memory           │
│                         │   │   │  - 独立上下文                    │
│ 汇总 N 份结果：           │   │   │  - 独立检索工具                  │
│  - 去重                  │   │   │  - 输出：结构化调研结果           │
│  - 识别冲突               │◄──┴──│                                 │
│  - 标注缺失               │       │ Worker 3: 调研 Planning         │
│  - 合成最终输出           │       │  ...                            │
└─────────────────────────┘       │ Worker 4: 调研 Multi-Agent      │
                                  └─────────────────────────────────┘
```

Core skeleton code:

```python
class SupervisorPattern:
    """Supervisor 拆任务 → Workers 并行 → Supervisor 汇总"""

    def __init__(self, supervisor: Agent, workers: dict[str, Agent]):
        self.supervisor = supervisor
        self.workers = workers

    def run(self, task: str) -> dict:
        # Step 1: Supervisor 拆解任务
        # 拆解结果必须包含：边界、输出模板、Worker 指派
        plan = self.supervisor.decompose(task)
        # plan.subtasks = [
        #   {"id": "T1", "topic": "Tool Use 最新实践",
        #    "worker": "researcher_1",
        #    "scope": "设计模式、失败模式、框架对比",
        #    "exclude": "不包含与其他方向的交叉内容（交叉由汇总时处理）",
        #    "output_template": "## Tool Use\n### 关键发现\n- ...\n### 失败模式\n- ...\n### 来源\n- ..."},
        #   ...
        # ]

        # Step 2: 并行执行
        results = parallel_execute(
            plan.subtasks,
            lambda st: self.workers[st.worker].execute(
                task=f"调研 {st.topic}。范围：{st.scope}。排除：{st.exclude}。"
                     f"输出格式：{st.output_template}",
                tools=["search_notes", "web_search"]
            )
        )
        # results 中失败或超时的 Worker 返回 None，不阻塞其他 Worker

        # Step 3: Supervisor 汇总
        # 关键操作：去重、识别冲突、标注缺失、合成
        final = self.supervisor.synthesize(
            task=task,
            worker_results=results,
            instructions="""
            汇总规则：
            1. 如果两个 Worker 对同一话题给出矛盾结论 → 标注"存在分歧"而非自动选择
            2. 如果某个 Worker 超时或失败 → 在报告中标注"该方向数据缺失"
            3. 去重：相同发现合并，标注来自哪些 Worker
            4. 最终输出按统一结构组织，不要直接拼接 Worker 原文
            """
        )
        return final
```

### 8.4.2 Dismantling quality determines the value of the whole model

The most easily underestimated step of the Supervisor model is the dismantling**. A lot of it has been done to simplify dismantling to "let LLM divide tasks into several" -- and then it's discovered that the worker output is highly overlapping, inconsistent in format and unable to merge.

Good dismantling takes four things: **1. Clear borders (include)** Not only "your research A, your research B," but also to say, "Don't touch anything."

```text
糟糕的拆解：
  Worker 1: 调研 Tool Use
  Worker 2: 调研 Multi-Agent
  → 两个 Worker 都在写关于"Tool Use 在 Multi-Agent 中的应用"
  → 30% 内容重叠

好的拆解：
  Worker 1: 调研 Tool Use 的设计模式、失败模式和框架实现
            exclude: 不涉及 Tool Use 在 Multi-Agent 协作中的角色（由 Worker 4 覆盖）
  Worker 2: 调研 Multi-Agent 的协作模式、通信协议和故障模式
            exclude: 不涉及单个 Agent 的 Tool Use 机制（由 Worker 1 覆盖）
```
**2. Unified output template**Each Worker must output with the same structure, otherwise Supervisor cannot merge automatically.

```text
输出模板（所有 Worker 共用）：
## {调研方向}
### 关键发现
- 发现 1（1-2 句话 + 来源引用）
- 发现 2
### 失败模式
- 常见失败 1（表现 + 原因 + 修正方向）
### 推荐实践
- 实践 1（适用场景 + 不适用场景）
### 来源引用
- [来源 1](链接或笔记路径)
```
**3. Worker Capability Match**Not all Walkers should be the same model. Research-type Worker may require a strong search capability (networked search, context) and analytical-type Worker may require a strong reasoning capability. assigns the right task to the right workker.**.4. Control of the particle size of dismantling**It was too detailed (10 subtasks) and the cost of communication and aggregation exceeded the implementation benefits. It's too coarse (2 subtasks) and insufficiently parallel. An empirical rule:**Number of sub-tasks = Min (number of separate dimensions that can be used in parallel, number of workr, 5)**. Marginal gains over 5 sub-tasks are generally insufficient to cover coordination costs.

### 8.4.3 Costs of consolidation - "Three Walkers ran out, Supervisor took longer to merge."

This is Supervisor's classic roll-over scene:

```text
场景：用户要求"调研 Agent Memory 的最新实践"
Supervisor 拆解为 3 个子任务 → 3 个 Worker 并行执行

时间线：
├─ Worker 1 调研"短期记忆"（45 秒）
├─ Worker 2 调研"长期记忆"（50 秒）
├─ Worker 3 调研"Memory 框架"（40 秒）
│  并行耗时：50 秒 ✓ 比串行快
│
├─ Supervisor 开始合并（60 秒）← 问题在这里
│  为什么？因为三个 Worker 的产出：
│  - Worker 1 输出了 3 页 Markdown（概述 + 详细分析 + 代码示例）
│  - Worker 2 输出了 5 个要点 + 1 个表格
│  - Worker 3 输出了 8 个框架的列表（没有分析）
│  格式完全不同，结构完全不同，覆盖范围有大量重叠。
│  Supervisor 无法"自动合并"——它实际上是在让 LLM 重新"综合"
│  三份报告，而这个综合工作如果从一开始就让一个 Agent 做，
│  可能只需要 70 秒。
│
├─ 总耗时：50 秒（并行执行）+ 60 秒（合并）= 110 秒
│  串行耗时：约 120 秒（三个方向 × 40 秒 + 自然汇总 10 秒）
│  并行收益：几乎为零。引入了 3 倍复杂度，省了 10 秒。
└─ 

根因：拆解时没有指定输出模板。三个 Worker 各自按自己的理解输出，
      合并成本抵消了并行收益。

修复：
1. 拆解时强制指定统一输出模板（结构、字段、长度限制）
2. 每个 Worker 的输出长度控制在 300 字内（禁止输出"概述"和"背景介绍"）
3. Worker 只输出"提取后的信息"，不做综合和总结——综合由 Supervisor 负责
```
**The core lesson of the rollover**: The parallel value is not "Worker runs fast", but**"Worker's output can be combined directly, without LLM understanding and synthesis"**. If combining steps requires LLM to read through all Worker outputs and "rewrite them," then let one of the Agent write from the beginning.

### 8.4.4 Obsolete boundary of Supervisor

| Expiry Mode | Performance | Gene. | Amendments |
|---|---|---|---|
| Dismantling border blur | Worker output 30 per cent | No exclude range defined when dismantling | Each submission with a clear exclude statement |
| Format Unharmonized | Worker output cannot be automatically merged, Supervisor needs to be re-integrated | No output template | Force the output template when dismantling (enable Worker to play freely in the template) |
| Worker failed to complete the report | Worker 2 timeout, Supervisor pretended to have completed all four directions. | There was no "data missing" in the summary. | Compulsion of aggregation rules: Failed Worker's corresponding orientation label "Default of data, cause: {overtime/ error} |
| Parallel Shape | Dismantling itself took 30 seconds. | Dismantling logic relies too much on LLM decision-making | Predefined breakup template: common tasks are fixed to break down dimensions and LLM is adjusted only in case of anomalies |
| Supervisor becomes a bottleneck. | Five. Walker's waiting for Supervisor's dismantling. | Dismantling and distribution are a series. | For standard tasks, use predefined dismantling (cachel), skip LLM dismantling |

---

## 8.5 Parallel Specialists: same mission, multiple eyes

Each Worker of Supervisor handles different tasks. Parallel Specialists is a variant: **The same task, with multiple experts analysing it from different dimensions at the same time and then combining it.**

### 8.5.1 Distinction from Supervisor: same input, different dimensions

```text
Supervisor 模式：                    Parallel Specialists 模式：
                                    
任务 A → Worker 1                   同一个任务
任务 B → Worker 2                         │
任务 C → Worker 3               ┌─────────┼─────────┐
                                ▼         ▼         ▼
不同任务，不同 Worker           Specialist A  Specialist B  Specialist C
                                (正确性)     (安全性)     (性能)
                                    │         │         │
                                    └─────────┼─────────┘
                                              ▼
                                          合并结果
                                      
不同维度，同一输入
```

Application scenario: A code requires both correctness, security and performance. A programme needs to assess both technical feasibility, cost and maintenance. A response requires simultaneous examination of factual accuracy, logical completeness and clarity of presentation.

### 8.5.2 Cross-dimensionalization is a parallel premise

A central prerequisite for the success of this model is the non-dependence of **dimensions.** If performance analysis requires first knowing the conclusions of correctness analysis, then it cannot go in parallel — it has to run correctness before running performance.

The dimensions design requires two conditions:
1. **Overlapping**: no overlap of attention per dimension. If "right" and "safe" both analyze input validation, 60% of the content repeats.
2. **Independent**: the result of each dimension can be concluded by simply entering + its own focus, which does not require other dimensions.

```python
class ParallelSpecialists:
    """多个专家并行处理同一任务的不同维度"""

    def __init__(self, specialists: dict[str, Agent]):
        self.specialists = specialists

    def run(self, task: str, dimensions: list[dict]) -> dict:
        """
        dimensions = [
          {"name": "correctness", "agent": "code_reviewer",
           "focus": "逻辑错误、边界条件、异常处理、状态一致性",
           "exclude": "不分析安全漏洞和性能瓶颈"},
          {"name": "security", "agent": "security_auditor",
           "focus": "注入风险、密钥泄露、权限越界、敏感数据暴露",
           "exclude": "不分析逻辑错误（即使它可能导致不确定行为）"},
          {"name": "performance", "agent": "perf_analyzer",
           "focus": "时间复杂度、空间占用、I/O 瓶颈、缓存策略",
           "exclude": "不分析正确性和安全性影响"},
        ]
        """
        # 并行执行
        results = parallel_execute(
            dimensions,
            lambda d: self.specialists[d["agent"]].analyze(
                task=task,
                focus=d["focus"],
                exclude=d["exclude"]
            )
        )

        # 合并：去重 + 标注来源 + 冲突识别
        return self.merge(results, dimensions)

    def merge(self, results: list[dict], dimensions: list[dict]) -> dict:
        """合并多维度分析结果"""
        all_findings = []
        conflicts = []

        for i, result in enumerate(results):
            for finding in result.findings:
                finding["source_dimension"] = dimensions[i]["name"]
                all_findings.append(finding)

        # 去重：相同位置 + 相同问题描述 → 合并为一条，标注来自多个维度
        deduped = self._deduplicate(all_findings)

        # 冲突检测：如果两个维度对同一位置给出矛盾判断
        # 例：Specialist A 说"这里的设计是安全的"
        #     Specialist B 说"这里有注入风险"
        # → 不能自动消解，标注为"存在分歧"
        conflicts = self._detect_conflicts(deduped)

        return {
            "findings": deduped,
            "conflicts": conflicts,  # 标注但不自动解决
            "dimension_summary": {
                d["name"]: len(r.findings) for d, r in zip(dimensions, results)
            }
        }
```

### 8.5.3 Consolidation rule: conflict does not automatically abate

The most dangerous moment for Parallel Specialists is integration. When two experts make conflicting judgements, the easiest mistake is to allow LLM to choose automatically -- for example, "take a majority" or "let Supervisor decide."

But this auto-dissociation will mask the real problem. If one expert says "safe" and the other says "a loophole," that means at least one expert has a problem with analysis -- - Maybe one of them's focus definition is not clear enough, maybe one of them lacks the key context. Automatically choosing "majority" just covered up the problem. **Consolidation rules**:
1. **The same finding automatically removes weight**: two experts identified the same problem (the same location + the same type of problem) and merged it into one article, marked from two dimensions.
2. **Contradictory judgement does not automatically abate**: labeled as "Different analysis of security dimensions requires manual review" with the specific basis of two experts.
3. **Source notation**: Each discovery indicates the dimensions from which the discovery was made, so that the reader knows what perspective the discovery was made.

A common failure of this model:

| Expiry Mode | Performance | Amendments |
|---|---|---|
| It's a repetition of dimensions. | "Rightness" and "security" experts, 60 percent of the output overlaps. | Clear range of focus and exclude for each dimension |
| Merge Lost Conflict | Specialist A says safety, specialist B says there's a problem. | The merger rule is clear: conflict labels are not abated |
| Too many parallels. | Eight specialists, API, and a limit to trigger limit. | ≤5 dimensions; grouping in parallel when exceeding 5 dimensions |
| Some expert's too soft. | "Performance" expert output, no apparent performance problem. | Review whether the expert dimension definition of Focus gives enough specificity to the check item |

---

## 8.6 Agent's settings and configurations -- how "different" landed.

8.2 The four dimensions of Multi-Agent split were described: different inputs, different tools, different targets, and different acceptance standards. 8.3 to 8.5 The structural design of three modes of collaboration is described. But structural design only solves the question of how to organize between Agents, and it doesn't solve a more advanced question: **How each Agent is configured to make them really different?**

### 8.6.1 Write Agent settings instead of Prompt

Multi-Agent's first step is to open the editor to write

```text
你是研究员。
你是工程师。
你是审查员。
```

It's too early. Prompt is part of Agent's configuration, but not Agent's setting itself. What really should be written first is an **Agent setup card**: it's like a job description, like a running time configuration list. It places duties, inputs, tools, models, parameters, output protocols and failure processing in the same place so that you can judge whether this Agent is really different from other Agents.

Here is an example of a set card for Reviewer Argentina:

```yaml
agent: security_reviewer
responsibility: 只审查安全风险，不修改产物
input:
  - final_artifact
  - original_requirement
  - security_checklist
excluded_input:
  - author_private_trace
  - draft_history
  - author_self_justification
tools:
  - read_file
  - run_security_scan
model:
  capability: instruction_following
  reason: 需要稳定遵循审查清单和结构化输出，不需要高创造性
parameters:
  temperature: 0
  max_tokens: 1000
output_schema: ReviewResponse
acceptance:
  - 每个 FAIL 必须包含 location 和 evidence
  - 不确定时不能猜测通过，必须标记 insufficient_information
fallback:
  - 两轮修正仍未通过时进入 human_review
```

This one's not the key.`agent`Name, but a few sets of constraints:

- **Boundaries of responsibility**: it is responsible for what, not what. Reviewer only reviews and does not change; Supervisor only dismantles and aggregates and does not replace Worker research.
- **Enter boundary**: it can see anything, it can't see anything. Reviewer could not see Author ' s draft and self-defence, which was a prerequisite for an independent review.
- **Tool boundary**: What tools can it call. Nothing.`write_file`The authority's Reviewer, it's not subject to revision.
- **Model boundary**: what capacity it requires. Not all Agents use the strongest models, but match model capabilities by duty.
- **Export boundary**: it must be delivered by what schema. Without structured output, after that, Agent can only re-understand a natural language.
- **Failed boundary**: What happens when it fails. Retesting, downgrading, changing models, handing over people must be defined in advance.

If an Agent set card can't be written, this Agent is not clearly designed. This is the time to continue writing Prompt, which only creates a text actor who looks like a character and actually has no boundaries.

### 8.6.2 Mapping with four dimensions

| Dimensions | Project Configuration Tool | Take Author + Reviewer, for example |
|---|---|---|
|**Entered differently** | Context range declaration in System Prompt + information filter in Runtime | The context of Author contains the results of the notes search, the history of the creation, the draft. Reviewer context is only injected into the final scenario + review criteria filtering out all middle reasoning of Author |
|**Different tools** | Agent Class White List in Tool Registration Table | Author is registered to write file, search notes, web search. Reviewer registers only read file, run security scan -- no write permission |
|**Different goals** | Task definition in System Prompt + description of success criteria | Author: "Technology of output to meet demand, covering all demand points". Reviewer: "Find out all problems that do not meet safety standards, give location and evidence by article." |
|**Different acceptance standards** | Output Schema binding + cessation condition | Author's output is not mandatory. Reviewer output must be`{verdict, checks[], issues[]}`,verdict has two values only. |

The above table is a quick look map. Below is an itemized list of specific practices and common errors for each configuration dimension.

### 8.6.3 Systems Prompt Design -- not just "rename."

The most common spelling is:

```text
# Author
"你是一个技术方案撰写者，请根据需求写出完整的技术方案。"

# Reviewer
"你是一个安全审查员，请审查这个技术方案的安全性。"
```

These two Prompt differences are only character names and verbs. They have no definition: what the Reviewer is specifically concerned with, what criteria to judge, what the output must contain, and what to do when it is uncertain. The result is that Reviewer is no different from the individual Agent -- it only knows its name as "censor," but it doesn't know what the censor should do. **Effective Systems Prompt must define five elements.** The following is an example:

```text
# Reviewer Agent — System Prompt 结构

## 1. 身份与职责范围（你管什么，不管什么）
"你是安全审查员。你只负责从安全角度审查技术方案。

你关注：输入校验、密钥管理、权限模型、依赖安全、数据保护。
你不关注：技术可行性、代码质量、架构设计、性能优化——
那些由其他角色负责，你不要在你的审查报告中提及。"

## 2. 输入说明（你能看到什么，看不到什么）
"你会收到一份技术方案的最终版本。

你不会看到：方案撰写过程中的草稿、讨论记录、妥协权衡的推理过程。
你只能基于最终方案文本和审查标准做判断。
如果你在方案中看到类似'为了开发方便，这里先用明文'的描述——
不要将其视为'合理的临时方案'，而要将其视为'安全漏洞'。
你的判断不因作者的意图而软化。"

## 3. 审查标准（逐条，可验证的）
"你必须逐条检查以下标准。每一条都附有验证方法——你必须实际执行验证，
不能只凭方案中的文字描述判断。

C1: 输入校验
    标准：所有用户输入点是否声明了长度和类型校验？
    验证：查看方案中 API 定义的 input schema，确认每个参数有 type 和 max_length。
    
C2: 密钥管理
    标准：所有密钥和敏感配置是否存储在环境变量或密钥管理服务中？
    验证：搜索方案文本和配置文件中的 key=、secret=、password= 字面量。
          如果找到硬编码值 → FAIL。如果引用环境变量 → PASS。
    
C3: 权限模型
    标准：是否存在非 admin 的角色定义？是否遵循最小权限原则？
    验证：检查方案中是否定义了多个角色（如 read/write/admin），
          以及每个操作是否声明了所需的最低权限。
    
C4: 依赖安全
    标准：第三方依赖是否锁定了版本号？
    验证：检查 requirements.txt 或等效文件中的版本声明格式（== 还是 >=）。"

## 4. 输出格式（强制结构）
"你的输出必须是一个 JSON 对象，不能包含其他文字：
{
  "verdict": "approved" | "rejected",
  "checks": [
    {
      "id": "C1",
      "passed": true | false,
      "evidence": "你在方案中的哪个位置（文件名:行号）找到了什么内容，
                   支持你的判断。如果找不到足够信息，填'insufficient_information'。"
    }
  ],
  "issues": [
    {
      "id": "I1",
      "description": "具体问题描述（不是主观评价，是事实陈述）",
      "location": "文件名:行号",
      "severity": "must_fix" | "should_fix",
      "suggestion": "修正建议，不超过 2 句话"
    }
  ]
}

不允许输出'整体评价''总结''建议进一步讨论'等内容。
如果某个检查项不确定，passed 设为 false，evidence 说明为何不确定——
这比错误地设为 true 要好。"

## 5. 边界行为（不确定时怎么做）
"以下情况按规则处理，不要自行发挥：

- 方案中没有足够信息判断某个检查项 → passed=false，evidence='insufficient_information'
- 方案中写了'已遵循安全最佳实践'但没有具体说明 → 不等于 PASS，
  你需要验证的是'实际做了什么'，不是'声称要做什么'
- 某个 issues 的 severity 不确定是 must_fix 还是 should_fix → 
  按 must_fix 处理，由人工裁决降级
- 你发现了一个不在审查清单中的安全问题 → 
  仍然报告，severity 标注为 should_fix，在 description 中说明'不在清单中但建议关注'"
```
**Design principles for five elements**:

- **"Whatever" is more important than "whatever."** It not only prevents Agent from crossing the border (Reviewer evaluated the quality of the code), but also narrows the focus of Agent to focus on its own responsibilities.
- **The review criteria have been changed from "assessment" to "inspection availability".** "Check the safety of the programme" is an assessment — vague, subjective and susceptible to general impressions. "The existence of key = volume in the text of the search program" is to check existence — specific, objective and without judgement.
- **Border behavior defines Agent's character**. Do you guess when you're not sure? When you see a vague statement, when you're in evidence or when you're asking questions? These are not technical parameters, but determine the reliability of Agent. A Reviewer that'll guess is more dangerous than no Reviewer -- its miscalculation will be considered "reviewed through".

### 8.6.4 Allocation of tools — white list, not "please don't use"

The most common error in the distribution of tools in Multi-Agent is the registration of the full volume set for each Agent, and then the System Prompt says, "Please use only the tools you need."

It's equivalent to giving every employee access to all lock cards, and then a note says, "Please just go into your room." System Prompt is a suggestion, tool registration is hard. The proposal can be ignored by the model (especially when the model considers that "a better task can be accomplished with this tool"), and not by hard restraints. **Correct practice: white list.** Every Agent only registers the tools it needs, and the tools that are not on the white list don't exist for it -- Runtme directly rejects the tools at the level of their call, and the models don't even know the tools exist.

```python
# 工具注册：白名单制
# 每个 Agent 创建时，只传入它需要的工具——不是传入全量然后靠 Prompt 约束

AGENT_TOOL_WHITELIST = {
    "author": {
        "search_notes",      # 检索笔记——需要查资料
        "web_search",        # 网络搜索——需要最新信息
        "read_file",         # 读文件——需要参考已有文档
        "write_file",        # 写文件 ← Author 独有，产出物需要持久化
    },
    "reviewer": {
        "read_file",         # 读文件——读 Author 的产出
        "search_notes",      # 检索安全规范——查安全标准
        "run_security_scan", # 安全扫描 ← Reviewer 独有，Author 没有
        # 注意：没有 write_file——Reviewer 不能修改 Author 的产出
        # 注意：没有 web_search——Reviewer 不需要外部信息
    },
    "supervisor": {
        "read_file",         # 读 Worker 产出
        # 注意：没有 write_file——Supervisor 只产出汇总报告，不修改原始文件
        # 注意：没有 search——Supervisor 不做调研，那是 Worker 的工作
    },
    "worker_researcher": {
        "search_notes",      # 检索笔记
        "web_search",        # 网络搜索
        "read_file",         # 读文件
        # 注意：没有 write_file——Worker 只输出分析结果到上下文，
        #       不修改文件系统
    },
}
```
**Iron law for the distribution of tools**:

1. **Agent can perform a dangerous operation and can't approve it at the same time.** Write file and approve deploy are never the same Agent. Merge pr and code review will never be the same Agent. It's not just security considerations -- when the same Agent can "do" and "do" it, it takes a shortcut: do it, do it.
2. **The output tool is registered only on the necessary Agent.** In a 3-Agent system, there is usually only one Agent that needs write file privileges. The output of the other Agent is sent back to the caller by a communication protocol, which determines whether or not to last.
3. **When it's not clear whether or not to register a tool for an Agent.** The after-action tool is easy (add a line to the configuration) and it is difficult to recover afterwards (Agent may have relied on that tool to develop a certain pattern of behaviour).

### 8.6.5 Model selection - not all players need the strongest model

Not all Agent needs the strongest and most expensive model. The demand for modelling capacity varies from one actor to another. If all Agents use the same model, you're not only wasting money, but you're also likely to undermine the system's reliability.

| Agent Role | Core competency requirements | Model selection recommendations | Rationale |
|---|---|---|---|
|**Executor / Author** | Long text generation, creative expression, integration of multi-source information | The strongest model | Output quality directly impacts the end result, with the highest returns on inputs |
|**Reviewer** | Detailed comparison, article-by-article check, following structured output format | Medium-power model focusing on command compliance and structured output | No creativity is needed. What is needed is "not to miss the check" and "not to fabricate evidence". temperature should read 0 |
|**Supervisor (dismantling phase)** | Mission analysis, structural design, boundary definition | The strongest model | Dismantling quality determines the quality of all work and the total cost of the task. There's an extra $ 0.02 to save Worker. |
|**Supervisor (consolidation phase)** | Reload, formatting, conflict labels | Medium Model | Mainly structural operations - contrast fields, merge lists, check formats. There's no need for in-depth reasoning. |
|**Worker (research)** | Retrieve + Summary + Output by Template | Medium model, need search tools Okay. | Speed is a priority, requiring multiple running in parallel and cost-sensitive. Output quality is subject to template rather than model capacity |
|**Worker (analytical)** | Deep reasoning, multistep analysis | Strong Model | Quality analysis determines the quality of decision-making. If Worker's analysis is the basis of Supervisor's decision, it's hard to save input here. |
|**Debate Participants** | Arguments, rebuttals, multidimensional thinking | Strong Model | Weak models are easy to miss or get into text games in Debate. But if it's just the "singing back" role, you can use the medium model. |

The above table selects the model by the Agent role. There's a different angle to be taken into account in the actual project: **What is the strength of the bottom model?** "The Strong Model" is not a single dimension. A model may be strong in reasoning but weak in code, may have long context but inconsistent in following instructions, or may be cheap and fast but not suitable for final adjudication.

Dismantling by capacity type makes model selection clearer:

| Model capacity type | More appropriate, Agent. | Not suitable, Agent. | Reason for selection |
|---|---|---|---|
|**Strong reasoning model** | Supervisor Dismantling, Planner, Risk Analyst, Complex Code Reviewer | Lots of simple workker, format conversions Argentina | Suitable for task decomposition, trade-offs, conflict judgement and implied risk identification; high cost, not for mechanical extraction |
|**Code-capable model** | Code Worker、Test Fixer、Code Reviewer | Word, brief summary, Agent. | Understand project structure, language API, test failure and boundary conditions; waste capacity for non-code tasks |
|**Context Model** | Research Worker、Document Analyst、Migration Planner | Shortlist Reviewer, One Step Tool Call | It's appropriate to read a lot of information and long documents; but the context is not the same as a more critical judgement, and the noise gets more. |
|**Strong Command Compliance Model** | Reviewer、Schema Extractor、Policy Checker | Creative Author, Open Brainstom Age | Suitable for fixed processes, fixed schema, article by article; low temperature, emphasis on stability rather than novel |
|**Low delay/low cost model** | Batch classification | Final adjudicators, complex planners | Fits to multiple, low-risk single task; error can be driven by a subsequent strong model or rule Stay. |
|**Multimodular Model** | UI Reviewer, Chart Parsing Worker, Screenshot QA Agent | Plain Text Protocol Merge | Value only when input contains screenshots, PDF pages, drafts; should not be used by default for all Agents |

Here is a practical judgement: **put the strongest model in the worst position of error, not all.** Supervisor debugging the task, leaving all workr running in vain; Reviewer missing the high-risk problem, making the user believe "passed" ; and the final merger fabricated the conclusion, contaminating the final delivery. These positions deserve stronger and more stable models. On the contrary, tasks such as batch extraction fields, template filling, format conversions, i.e. error using a cheap model, are usually captured by a schema check or lower Reviewer. **A common rollover scene**: All Agents have created a "creative" version of the edifice under the téperature of 0.7, with the same model + téperature → Reviewer, which appears to be PASS, but two of the ividences are fictional and the whole review is more dangerous than it is without review (because the user trusts the mark that has been reviewed). **Reviewer's specialty**: Reviewer is the most intriguable character in Multi-Agent -- its judgment is the system's "quality gate". The Reviewer model does not need to be "smart." What is needed is "temperature 0", structured output enforcement, and evidence field requires specific filenames: line numbers. There are one or two imperfect solutions that Execut wrote -- users can fix themselves. Reviewer missed a security check -- users trusted the pass mark, which could lead to an online accident.

### 8.6.6 Easing of parameters — different roles, different parameters

The same model, different parameter configurations allow the same model to present completely different behavioural characteristics. Different roles in Multi-Agent need different parameter configurations:

| Parameters | Executor/Author | Reviewer | Supervisor | Worker (research) |
|---|---|---|---|---|
|**Temperature** | 0.3-0.7 |**0-0.1** | Dismantling 0.2-0.3 / Summary 0-0.1 | 0.1-0.3 |
|**Max Tokens** | Estimated by output x 1.3 |**Projected by structured output** (usually 500-1000, stop if sufficient) | Dismantling 1024 / Summary 2048 | Estimated by template (usually 500-800) |
|**Stop Sequences** | No Special | JSON Ender`}`Stop After | Same Reviewer | Same Reviewer |
|**Top P** | 0.9-0.95 |**1.0** (certainty) | 0.95-1.0 | 0.95 |**Key decision-making for parameter design**:

- **Reviewer's temperature must be zero or close to zero.** This is the most easily neglected but most influential configuration. When temperature is not 0, the Reviewer field runs different text each time it runs -- This means that the two reviews of the same programme may have different results. For "Quality Gate", certainty is much more important than creativity.
- **Max Tokens isn't "ceiling," it's "budget".** Too many max tokens set for Reviewer will not allow it to review more carefully -- it will start "additional" after the output of the structured results, "recommends" "commends". Sets just enough max tokens to tell the model: "Exit the requested structure and stop."
- **Supervisor disassembly and aggregateture should be different.** Dismantling requires some flexibility (the decomposition dimensions of each task are not identical), but aggregation requires certainty (the same worker output should have the same aggregate results).

### 8.6.7 Configuration management - from scattered locations to "configuration or code"

Three Agents managed manually okay. At five Agents, Systems Prompt, White List of Tools, Model Selection, Parameters are scattered in multiple files. Modifys the review criteria for Reviewer, forgetting that the summary logic of Supervisor is being updated simultaneously - the system is beginning to show subtle inconsistencies. **Recommended practice: Agent configuration centralized, Systems Prompt external documentation.**```python
# agent_configs.py — 所有 Agent 配置的单一事实来源
# 修改任何一个 Agent 的配置，只需改这一个文件。
# 新增一个 Agent 时，在一个地方声明它的全部配置。
# 代码 review 时，能一眼看到"这次改动影响哪些 Agent 的哪些配置"。

AGENT_CONFIGS = {
    "author": {
        "model": "claude-sonnet-4-6",
        "temperature": 0.4,
        "max_tokens": 4096,
        "system_prompt": "prompts/author_system.txt",  # 外部文件，便于 diff
        "tools": ["search_notes", "web_search", "read_file", "write_file"],
        "output_schema": None,  # 不强制结构化输出
    },
    "reviewer": {
        "model": "claude-sonnet-4-6",
        "temperature": 0.0,  # 确定性——质量闸门不能有随机性
        "max_tokens": 1024,  # 刚好够结构化输出，防止"补充说明"
        "system_prompt": "prompts/reviewer_system.txt",
        "tools": ["read_file", "search_notes", "run_security_scan"],
        "output_schema": "schemas/review_result.json",  # 强制结构化输出
        "max_rounds": 2,  # Reviewer 特定的控制参数
    },
    "supervisor": {
        "model": "claude-fable-5",
        "temperature": 0.2,
        "max_tokens": 2048,
        "system_prompt": "prompts/supervisor_system.txt",
        "tools": ["read_file"],
        "decomposition_strategy": "template_first",  # 优先预定义模板
        "merge_conflict_policy": "flag_not_resolve", # 冲突标注不解消
    },
    "worker_researcher": {
        "model": "claude-haiku-4-5",  # 调研型用便宜模型
        "temperature": 0.2,
        "max_tokens": 800,
        "system_prompt": "prompts/worker_researcher_system.txt",
        "tools": ["search_notes", "web_search", "read_file"],
        "output_template": "templates/research_report.md",  # 强制输出格式
    },
}
```
**Three principles of configuration management**:

1.**System Prompt External Documentation.**No long strings to die in code. External files can diff ("What review criteria have been changed this time?"), review, roll back. When the system behaves abnormally, look at the latest System Prompt Diff -- the problem is not code change, it's Prompt change.
2.**The white list of tools is centralized on the configuration level.**A file with all Agent tool privileges. Add a new hazard tool (e.g.`delete_file`At the time, the examiner was able to see at first sight "what this tool has been assigned to Agent" -- not ten files of grep.
3.**Configure Change Walk Report.**Changed the review criteria for Reviewer? Changed Supervisor's dismantling strategy? These changes have no less impact than changes in business codes. One review criterion was changed from "Check if there's a specified key" to "Check if there's a key management service"? - Looks like a change in the sentence, which could actually result in the project being adopted. The risk of this change is comparable to the core business logic of the change.

## 8.7 Communication protocol-Agent cannot "what do you think?"

We've talked about the structure of the three modes of collaboration and how each Agent can be configured to be really different. How exactly do you communicate between the configured Agents? This is the most undervalued issue in Multi-Agent. Many systems are well designed for collaborative models, and Agent configurations are different, but they fall on communication protocols.

### 8.7.1 Why is free dialogue a disaster?

The most intuitive means of communication is to allow Agent to speak freely — as human beings do, you talk to me. This is the Group Chat mode: multiple Agents speak freely in a shared conversation.

However, in Multi-Agent, free dialogue is the most expensive, difficult to debug and the easiest to fail. There are three reasons:**1. Information decay.**The original message declines every time it passes between Agent. AgentA's discovery was repeated by AgentB, and then by AgentC's quote - when it came to Supervisor, the original specific judgment became a vague impression.

```text
原始："config.yaml 第 8 行 api_key 字段为明文，存在泄露风险"
↓ Agent B 复述：
"A 提到了配置文件中有密钥管理问题"
↓ Agent C 引用：
"前面的讨论涉及了安全性方面的考虑"
↓ Supervisor 收到：
"团队讨论了安全性" ← 原始信息完全丢失
```
**2. Intentional distortion.**One Agent says "recommended optimization", the other Agent understands "must optimization". The word "recommended" and "must" distinguish between human communication, and the word between Agent is easily lost.**3. Blur decision-making.**Free dialogue has no "decision point". Agent can keep talking about "consent" and "complement" and "advice" and "further consider" -- no one says "discussion is over, and the following is a decision." The final output was not a decision-making exercise, but a summary of the discussions.

### 8.7.2 Design communication formats by collaborative mode

Alternatives to free dialogue are**structured communications**. This is not the definition of a low-to-high protocol hierarchy, but rather the translation of three of the previously mentioned collaboration models into a specific message format: Reviewer needs to review worksheets, Supervisor needs task sheets and reports, and Paallel Specialists needs to show results with dimensions.**Reviewer mode: command-response**Reviewer should not have received a sentence "Look at this program for me," but rather a review sheet. It's clear in the worksheet: what to review, what criteria to review, how to give evidence after failure.

```json
{
  "type": "review_request",
  "artifact": "API 设计方案 v1",
  "context": {
    "user_goal": "为内部知识库设计查询 API",
    "constraints": ["不能暴露未授权文档", "响应时间小于 2 秒"]
  },
  "criteria": [
    {
      "id": "security.authz",
      "check": "是否说明文档级权限校验",
      "how_to_verify": "方案中必须出现权限来源、校验位置和失败返回",
      "severity": "must_fix"
    },
    {
      "id": "reliability.timeout",
      "check": "是否定义超时和降级策略",
      "how_to_verify": "方案中必须说明超时时间、重试次数和用户可见结果",
      "severity": "should_fix"
    }
  ]
}
```

Reviewer's response will be equally rigid. Note that there is no "overview" field, because "overall is okay" is the kind of bullshit that is the easiest to hide.

```json
{
  "type": "review_response",
  "verdict": "rejected",
  "checks": [
    {
      "check_id": "security.authz",
      "passed": false,
      "evidence": "方案只写了'后续接入权限系统'，没有说明校验位置和失败返回",
      "suggestion": "补充权限来源、查询前校验点，以及无权限时的错误响应。"
    },
    {
      "check_id": "reliability.timeout",
      "passed": true,
      "evidence": "第 4 节定义了 2 秒超时和缓存降级",
      "suggestion": null
    }
  ],
  "issues": [
    {
      "id": "issue-001",
      "location": "第 3 节：权限模型",
      "severity": "must_fix",
      "description": "权限校验停留在承诺层，没有落到请求链路。",
      "suggestion": "把'后续接入权限系统'改成可执行的权限校验流程。"
    }
  ]
}
```

This format is suitable for quality gates: security clearance, front-line inspection, programme acceptance, code review. It is characterised by the fact that**both input and output are binding**and Agent cannot circumvent judgement in natural languages.**Supervisor Mode: Template - Fill**When Supervisor dismantles the mission, don't just say, "You go to the research vector database." It should give Worker a filled list of tasks: what to do, what to do, what to deliver.

```json
{
  "type": "subtask_assignment",
  "task_id": "research-vector-db",
  "worker": "researcher-1",
  "topic": "向量数据库在 RAG 系统中的选型",
  "scope": "只比较 Milvus、pgvector、Pinecone 的工程适用性",
  "exclude": "不展开向量检索算法原理，不写市场背景",
  "output_template": {
    "key_findings": "最多 3 条",
    "failure_modes": "最多 2 条",
    "recommended_use": "一句话说明适合什么场景",
    "sources": "列出引用来源"
  },
  "max_length": 300
}
```

Worker, when you return, do not write a long, freely developed text, but complete the template:

```json
{
  "type": "worker_report",
  "task_id": "research-vector-db",
  "status": "completed",
  "content": {
    "key_findings": [
      "pgvector 适合已有 Postgres 团队，运维成本最低。",
      "Milvus 适合向量规模和检索性能要求更高的场景。",
      "Pinecone 适合希望减少自运维负担的团队。"
    ],
    "failure_modes": [
      "只看检索性能，忽略数据同步和权限过滤。",
      "过早引入独立向量数据库，增加运维复杂度。"
    ],
    "recommended_use": "如果团队已有 Postgres，先用 pgvector 建立基线。",
    "sources": ["官方文档", "项目 README", "工程实践文章"]
  },
  "error": null
}
```

This format is suitable for parallel research and aggregation. It doesn't have the Reviewer so rigid, but it limits the output shape through templates to avoid three different reports from Walker.**Parallel Specialists Mode: Dimensions - Mark**The key to Parallel Specialists is not "talk to each other", but to each discovery with its source dimension. In this way, Supervisor is able to focus on the conflict, rather than drawing a vague summary of different perspectives.

```json
{
  "type": "dimension_analysis",
  "dimension": "security",
  "findings": [
    {
      "id": "sec-001",
      "location": "/login",
      "severity": "must_fix",
      "description": "登录接口没有说明失败次数限制。",
      "evidence": "方案只描述账号密码校验，没有提到 rate limit 或 lockout。"
    }
  ]
}
```

The result of the merger would also be to retain the structure. If two dimensions make the opposite judgement of the same position, not automatically "cut off" but expose the conflict.

```json
{
  "type": "merge_result",
  "findings": [
    {
      "id": "sec-001",
      "dimension": "security",
      "location": "/login",
      "severity": "must_fix",
      "description": "登录接口没有说明失败次数限制。"
    }
  ],
  "conflicts": [
    {
      "location": "/login",
      "finding_a": "security 判断缺少失败次数限制",
      "finding_b": "performance 判断不建议增加额外校验",
      "resolution": "needs_human_review"
    }
  ],
  "coverage": {
    "correctness": 2,
    "security": 1,
    "performance": 1
  }
}
```

This format is suitable for a multi-perspective review of the same product: correctness, safety, performance, cost, user experience. It does not focus on reaching agreement among multiple Agents, but rather on allowing different dimensions of judgement to be tracked, merged and adjudicated.**Core principles of structured communications**:

-**Not accepted as "comprehensively all right"**: the results of the review must be specific, article-by-article and supported by evidence.
-**Free text only appears at leaf node**: the description may be a natural language, but the "bones" of communication (state, type, location, severity) must be structured fields.
-**Missing field is better than created field**: If Reviewer cannot find evidence, it is not possible to find evidence.`evidence`Field Filling`"not_found"`Instead of fabricating a description that sounds reasonable.
-**Human readable track**: Structured communication creates a searchable track -- you can grep`"verdict": "rejected"`All rejected reviews are found and the pass rate for each review item is measured.

### 8.7.3 From internal communications engagement to Agent protocol

Designed in front of this section`review_request`、`worker_report`、`dimension_analysis`, an internal communication agreement. It is usually sufficient for real projects to do so at an early stage: clear fields, clear status, clear product and clear reasons for failure.

But when Agent no longer exists in the same code library, the same frame, the same team, the problem goes up further: how does one Agent find another? How do you know what they can do? How is tasking, tracking status, receiving results, handling failures? This requires a more standardized Agent communication protocol.

After 2025, there have been some related attempts in the industry:

-**MCP (Model subject Protocol)**: mainly addresses how Agent standardizes connectivity tools, data sources and context.
-**A2A (Agent2AgentProtocol)**: mainly addresses how different Agents discover, commission, exchange information and return products.
-**Agreements such as ACP / ANP are explored**: an attempt to address Agent communications, identity, discovery, multi-modular messages and cross-platform interoperability from different perspectives.

The common direction of these agreements is not "to make Agent more free to talk," but the opposite: to tear out the vague parts of the natural language and turn them into verifiable objects of agreement, such as capability descriptions, task status, type of message, product, error and permission.

For most business projects, full industry agreements need not be introduced at the outset. The more realistic path is:

1. Clear definition of structured communication formats within the system;
2. When the number of Agents, team boundaries, tools become more ecologically complex, standard agreements such as MCP/A2A are considered;
3. Don't treat the agreement as a reliable substitute, it only solves "how to communicate", it doesn't automatically solve "who can trust, who decides, when to stop, what to do wrong."


## 8.8 award, suspension and background - Multi-Agent 'Rules of Traffic'

The collaboration model defines how Agent divides, the communication protocol defines how Agent communicates information. But there is a third level:**the control mechanism**— who decides when, when and how?

The Multi-Agent system without this layer is not a "decision-making system" but a "discussion group" -- it's probably a good discussion, but nobody boarded it.

### 8.8.1 Adjudication mechanisms: who rules when differences arise

There are three types of disagreement in the Multi-Agent system, each of which requires different methods of adjudication:

| Type of disagreement | Typical scene | Method of award | Why can't we just digest? |
|---|---|---|---|
| Reviewer vs Executor | Reviewer ruled Fail, Execuator, that "it's not a problem." | After two rounds of amendment, no manual decision was passed. Exportor should not have the power to overrule Reviewer's judgment | Allowing the subject to rule on the examiner is tantamount to cancelling the review |
| Worker vs Worker | Worker 1 says, "Framework A supports current output," and Worker 2 says, "No support." | Checks source references. Quoted confrontation (who is more authoritative). It's not clear from the source that there's a difference of fact. | The facts need to be traced, not voted. |
| Worker vs Worker | Specialist A says "safe," Specialist B says, "a gap." | Mark conflict manual review. No automatic vote or "majority." | To judge conflict means that at least one person has missed or missed it, and it requires a fresh look at it. |**Principles for the design of adjudication mechanisms**:

1.**The adjudicator cannot be a party**. Exportor cannot rule on the reasonableness of the review by Reviewer. Worker cannot rule on the correctness of his output.
2.**Manual decision superiors automatic decision**. When two Agents make contradictory judgements, it is safer to suspend and request human intervention, rather than to allow the third Agent to "vote" -- the third Agent could also make mistakes.
3.**The award requires a "final deadline".**Tasks cannot be blocked indefinitely by waiting for a manual decision. Set timeout: Manual decision exceeding N minutes does not respond to the most conservative choice (e.g. Reviewer 's judgement gives priority or suspends the mission and keeps the site).

### 8.8.2 Conditions for cessation: not unlimited return

Multi-Agent's suspension conditions are similar to those of Reflect, but there are more dimensions specific to collaboration:

| Conditions for discontinuation | Proposal for thresholds | Conduct at Trigger |
|---|---|---|
| Reviewer Number of round trips | 2 rounds after correction | Mark "disputed", manual ruling, not into Round 3. |
| Number of Supervisor summaries | 1 Dismantling - Summary | If the summary results are missing, do not reopen - label missing and output |
| Worker and timeout. | Maximum Worker time-consuming x 1.5 | The result of Worker's timeout is discarded, and the report indicates that the data is missing. |
| Total token consumption | Single task 50K tokens | Stop all Agents, return partial results completed |
| Can not open message | 3 consecutive rounds of communications with similar content > 90 per cent | Called "dialogue dead" and forced to stop and output the current state. |
| Error Upgrade | Recoverable error failure (e.g. network overtime becomes disk full) | Stop All Agent, keep the scene and notify the user |**The conditions for stopping must be coded hard and cannot be decided by Agent itself.**Agent has no instinct to stop -- it'll still start a new round of communications confidently on the sixth round. The condition for cessation is a mandatory check on the Runtme layer, unrelated to Agent 's reasoning ability.

### 8.8.3 Bottom strategy: what if Walker dies?

When the Multi-Agent system is running, Worker Agent may fail for various reasons: API limit, network timeout, output unresolved, context spilling. The system must pre-empt every failure:

```text
Worker 失败模式              兜底策略
─────────────────────────────────────────────────────
单个 Worker 超时          → 丢弃该 Worker 结果
                           在最终报告中标注"方向X: 数据缺失（超时）"
                           不重试，不阻塞其他 Worker 的产出

单个 Worker 输出不可解析   → 尝试重新生成一次（仅一次）
                           仍不可解析→同上，标注"数据缺失（格式错误）"

多个 Worker 同时失败       → 可能根因是上游问题（如 API 故障）
（≥50% Worker 失败）         停止全部执行，返回部分结果 + 错误诊断
                           不继续——继续可能只是消耗更多 token

Supervisor 拆解失败        → 如果拆解方案不满足最小要求（如边界重叠>30%）
                           降级为"单 Agent 直接执行"，跳过 Multi-Agent
                           通知用户："拆解方案质量不满足并行条件，已降级"

Supervisor 汇总失败        → 返回各 Worker 的原始产出（标注为"未汇总"）
                           不尝试让 LLM 重新汇总——第一次汇总失败的原因
                           可能仍然存在
```
**Core principle at the bottom: demotion without silence.**The system can be downgraded to single Agent if Multi-Agent is not available - but cannot pretend Multi-Agent is successful. Missing data, failed worker, skipping check items - all clearly marked in the final output.

---

## 8.9 The truth of the cost - not just Token's bill

Multi-Agent's costs are often underestimated because its head is not on a monthly API bill.

### 8.9.1 An estimated comparative bill

Take the example of the knowledge assistant writing technology program + security clearance mission, comparing typical consumption of the Agent and Reviewer models. The figures below are teaching estimates, which are used to train in cost dismantling methods and do not represent a fixed bill for a production system.

```text
═══════════════════════════════════════════════════════════════════
任务：写一份 API 模块技术方案（约 2000 字），从安全角度审查

单 Agent（自审）：
┌─────────────────────────────────────────────────────────────────┐
│ 写作阶段：                                                       │
│   System Prompt: 800 tokens                                     │
│   用户输入 + 上下文: 500 tokens                                   │
│   模型输出（方案）: 2,500 tokens                                  │
│   小计: 3,800 tokens                                            │
│                                                                 │
│ 自审阶段（同一上下文，追加一轮）：                                  │
│   用户追加消息: 100 tokens                                       │
│   模型输出（审查）: 300 tokens                                    │
│   小计: 400 tokens                                              │
│                                                                 │
│ 总计: ~4,200 tokens                                             │
│ 耗时: ~40 秒                                                    │
│ 成本: ~$0.06（以 Claude Sonnet 定价估算）                         │
│ 结果: 漏了 4 个安全隐患                                          │
└─────────────────────────────────────────────────────────────────┘

Reviewer 模式：
┌─────────────────────────────────────────────────────────────────┐
│ Author Agent（独立实例）：                                        │
│   System Prompt: 400 tokens（只管创作，不含审查逻辑）              │
│   用户输入 + 上下文: 500 tokens                                   │
│   模型输出（方案）: 2,500 tokens                                  │
│   小计: 3,400 tokens                                            │
│                                                                 │
│ Reviewer Agent（独立实例，独立上下文）：                           │
│   System Prompt: 300 tokens（只管审查，不含创作逻辑）              │
│   写入上下文（方案 + 审查清单）: 2,800 tokens                      │
│   模型输出（结构化审查结果）: 600 tokens                           │
│   小计: 3,700 tokens                                            │
│                                                                 │
│ Author 修正阶段（独立实例，只收到 issues）：                       │
│   写入上下文（方案 + issues）: 3,300 tokens                       │
│   模型输出（修正后方案）: 2,600 tokens                             │
│   小计: 5,900 tokens                                            │
│                                                                 │
│ Reviewer 第二轮审查：                                             │
│   写入上下文（修正后方案 + 审查清单）: 2,900 tokens                 │
│   模型输出（审查结果）: 300 tokens                                 │
│   小计: 3,200 tokens                                            │
│                                                                 │
│ 总计: ~16,200 tokens（单 Agent 的 3.9 倍）                        │
│ 耗时: ~80 秒（单 Agent 的 2 倍）                                  │
│ 成本: ~$0.22（单 Agent 的 3.7 倍）                                │
│ 结果: 发现并修正了全部 4 个安全隐患                                │
└─────────────────────────────────────────────────────────────────┘

成本-收益分析：
┌─────────────────────────────────────────────────────────────────┐
│ 额外成本: +$0.16, +40 秒                                        │
│ 收益: 从"有 4 个安全漏洞"变为"通过安全审查清单"                     │
│                                                                 │
│ 判断: 如果这个方案部署后出现安全事件，修复成本 >> $0.16            │
│       在这个场景中，额外成本是值得的                                │
│                                                                 │
│ 但如果任务是一个低风险的内部备忘录？                                │
│ 额外成本可能不值得——不是所有场景都需要 Multi-Agent                 │
└─────────────────────────────────────────────────────────────────┘
```
**Key Insight**: Token consumption of Multi-Agent is usually 2-5 times that of single Agent. It's not "expensive" -- it's "additional token buys what." If it's the "Face Found" Agent's gonna miss four safety holes," then $0.16 is cheap. If it's "three Agents to discuss 12 rounds, but output is the same as single Agent", every penny is wasted.

### 8.9.2 Delay magnification: the real cost of communications travel

Multi-Agent's delay is not a simple "model reasoning time x Agent number". Real delays include:

```text
Reviewer 模式延迟拆解：
┌──────────────────────────────────────────────────────────────┐
│ Author 推理: 30 秒                                            │
│ +                                                             │
│ Reviewer 推理: 25 秒                                          │
│ +                                                             │
│ 上下文构建和传递: 5 秒                                         │
│   （将 Author 产出 + 审查清单打包为 Reviewer 的输入上下文）       │
│ +                                                             │
│ Author 修正推理: 20 秒                                        │
│ +                                                             │
│ Reviewer 二轮推理: 10 秒                                      │
│ =                                                             │
│ 总计: ~90 秒                                                  │
│                                                                │
│ 用户感知延迟: 90 秒（从发起到拿到 approved 结果）               │
│ 单 Agent 自审: ~40 秒                                         │
│ 延迟放大: 2.25 倍                                             │
│                                                                │
│ Supervisor 模式延迟（4 个 Worker 并行）：                       │
│ Supervisor 拆解: 8 秒                                         │
│ +                                                             │
│ 并行 Worker（取最慢）: 45 秒                                   │
│ +                                                             │
│ Supervisor 汇总: 15 秒                                        │
│ =                                                             │
│ 总计: ~68 秒                                                  │
│ 串行（4 × 40 秒 + 10 秒汇总）: ~170 秒                         │
│ 加速比: 2.5 倍 ✓                                              │
└──────────────────────────────────────────────────────────────┘
```
**Key to delayed optimization**:
- The Reviewer model is inherently slower than the single Agent - one more reasoned delay per round trip. Design to minimize the number of round trips (up to two rounds).
- The delayed benefits of the Supervisor model come from parallel. If the number of workingrs is small or the task is very different (one workingr 45 seconds, another 10 seconds), the acceleration effect is reduced.
- The time-consuming construction and transmission of the context is easily ignored - especially when the content is long (e.g. complete programme text).

### 8.9.3 Long-term costs: Trade complexity and difficulty of taking over

Multi-Agent's most hidden costs are not on the bill, on**maintenance**.

Three months later, when the new guy took over the system, Ta faced:

```text
单 Agent 系统：
├─ 1 个 System Prompt
├─ 1 个工具集
├─ 1 条 trace（线性执行记录）
└─ 调试：找到出问题的步骤 → 修正 Prompt 或工具

Multi-Agent 系统：
├─ 3 个 System Prompt（Author、Reviewer、Supervisor）
├─ 3 个工具集（权限各不相同）
├─ 多条交叉 trace（Agent A 的输出是 Agent B 的输入，找出"这个错误是谁引入的"
│   需要同时翻 3 条 trace 并交叉对照）
├─ 调试："为什么最终方案少了一个安全检查？"
│   → Reviewer 漏掉了（检查 Reviewer 的 trace）
│   → Author 在修正时忽略了（检查 Author 的 trace）
│   → Supervisor 在汇总时丢失了（检查 Supervisor 的 trace）
│   → 通信协议中某个字段被错误地解析了（检查通信层的序列化逻辑）
└─ 修改影响面：改了 Reviewer 的审查清单 → 可能影响 Author 的修正策略
                → 可能影响 Supervisor 的判断逻辑
```

It's not that Multi-Agent shouldn't be used. It says:**Should only be introduced if you are convinced that the additional maintenance costs can be covered by the value created by Multi-Agent.**If only Agent + good Prompt could do 90 points, the cost of introducing Multi-Agent for 95 points could be three times the maintenance complexity.


## 8.10 After-school exercise: Write Supervisor dismantling to implementable**Corresponding section**: 8.4 Supervisor model, 8.7 Structured communications, 8.8 Bottom-up strategy.**scene**User request: "Help me study the latest practices in three Agent directions: Memoory, Tool Use, Multi-Agent. The key findings, common failure patterns, recommended practices and sources are exported in each direction."**Binding**- Up to 3 Walkers.
- Each Worker output does not exceed 300 words.
- Each Worker must give at least two sources.
- If a Worker is out of time, the final report cannot pretend that the direction has been completed.**Exit requirements**Write a Supervisor distribution plan in the following format:

```json
{
  "subtasks": [
    {
      "id": "T1",
      "worker": "worker_memory",
      "topic": "",
      "scope": "",
      "exclude": "",
      "output_template": "",
      "timeout_seconds": 60
    }
  ],
  "merge_rules": [
    "",
    ""
  ],
  "fallback_rules": [
    "",
    ""
  ]
}
```
**Criteria for eligibility**- Every submission.`scope`and`exclude`, and the scope of the three Workers cannot clearly overlap.
- `output_template`Must contain the "Key Discovery / Failed Mode / Recommended Practice / Source" field.
- `merge_rules`It was important to explain how to weigh, how to deal with conflicts of fact and how to identify sources.
- `fallback_rules`It is important to explain how the three scenarios of workingrker's timeout, non-resolveable output and insufficient sources are dealt with.
