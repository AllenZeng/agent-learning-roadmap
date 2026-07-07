# Chapter IX: Portfolio of capacities and sequence of introduction

[Return Course Five Document](./course-05-01-scenario-enhancement.md) | [Previous Chapter](./course-05-08-multi-agent.md) | [Next part: after-school exercises](./course-05-01-scenario-enhancement.md#课后练习)

## Table of contents of this chapter

- [9.1 No one-time capacity stacked](#91-no-one-time-capacity-stacked)
  - [9.1.1 Anti-curricular materials: disasters introduced by the Big Bang](#911-anti-curricular-materials-disasters-introduced-by-the-big-bang)
  - [9.1.2 Hidden costs of capabilities](#912-hidden-costs-of-capabilities)
  - [9.1.3 Levels of capacity complexity](#913-levels-of-capacity-complexity)
  - [9.1.4 Correct problem-driven rhythm](#914-correct-problem-driven-rhythm)
  - [9.1.5 What's the "minimal circle"?](#915-whats-the-minimal-circle)
- [9.2 Capacity portfolio cases](#92-capacity-portfolio-cases)
  - [Case I: Personal Knowledge Assistant](#case-i-personal-knowledge-assistant)
  - [Case II: Code Review](#case-ii-code-review)
  - [Case III: Individual assignments](#case-iii-individual-assignments)
  - [Case four: Smart customer service, Agent.](#case-four-smart-customer-service-agent)
  - [Case V: Data Analysis Assistant](#case-v-data-analysis-assistant)
  - [Case VI: Writing Collaboration](#case-vi-writing-collaboration)
  - Cross-case comparison overview
- [9.3 Counter-model of capacity mix](#93-counter-model-of-capacity-mix)
- [9.4 Gradual introduction of rhythms and signals](#94-gradual-introduction-of-rhythms-and-signals)
- [9.5 Degradation and removal of capabilities](#95-degradation-and-removal-of-capabilities)
- [9.6 Field exercise: capacity to make decisions for new scenes](#96-field-exercise-capacity-to-make-decisions-for-new-scenes)

---

## 9.1 No one-time capacity stacked

Agent, a knowledge assistant in Ri, eventually brought together seven capacities. But this is not an end in itself — it has been used for months, and one problem after another has been pushed out.

In real projects, empowerment does occur frequently. Personal Knowledge Assistant needs RAG + Memory; Code ReviewAgent needs Tool Use + Reflection + Reviewer. However, a combination does not amount to a one-time drawing of the architecture in the design document.

The better order is - let the problem drive into the rhythm:

```text
先让最小闭环跑起来
  -> 观察第一个明确的问题模式
  -> 用最小版本的能力修复它
  -> 评测是否真的变好了
  -> 再观察下一个瓶颈
  -> 循环
```

Do not join the system because a certain ability is popular in the community. Each capability should be supported by problematic evidence and evaluation methods before entering the system. If you can't say "What problem the user has at what point when there is no RAG," then RAG should not be your first priority.

### 9.1.1 Anti-curricular materials: disasters introduced by the Big Bang

Look at a scene. A team decided to be an "Agent" all-powerful code assistant, introducing seven capabilities simultaneously in a sprint:

```
Sprint 目标：构建 SuperCodeAgent v1.0

第一周：
- 接入 RAG：索引公司内部全部代码仓库文档
- 接入 Memory：保存用户所有编码习惯和偏好
- 接入 Planning：支持多步骤重构计划自动拆解

第二周：
- 接入 Reflection：代码生成后自动审查并修正
- 接入 Multi-Agent：一个写代码，一个审代码，一个写测试

Sprint 结束后上线，结果：
```
**User feedback on first day:**| Problem | Gene. | User perception |
|------|------|----------|
| Agent's response was too slow (25 seconds average) | Five superpowers lead to an extremely long single request chain. | "Not as fast as I can write." |
| The results are often irrelevant. | RAG Index quality was not polished in time | "It's not about what I asked." |
| Memoory remembers a lot of useless preferences. | No memory screening strategy. | "It recorded the configuration of my temporary test, and it was officially completely out of order." |
| Plan, the steps are always off track. | Planning didn't match the scene. | "Step 10, step 3 begins to do irrelevant things." |
| Two Agents. | Multi-Agent does not define conflict resolution rules | "The guy who writes the code says it's okay. The guy who reviews the code says it's rewrite." |**Core lesson:**Not that these capabilities are bad, but that one-time introduction leads to:

1. **Debugging dilemma**: When a problem arises, you cannot quickly locate what caused it.
2. **Evaluation difficulty**: you do not have a "pre-inclusion" baseline to compare
3. **User trust overdraft**: first experience poor and users may not give you a second chance
4. **Team perception overload**: maintainers need to understand five complex subsystems simultaneously

> **Remember one sentence: one capacity, one problem, one assessment. The three principles of "one" are the bottom line for introducing rhythm.** ### 9.1.2 Hidden costs of capabilities

Every capacity also has a quiet cost in solving problems. Before the decision is taken, the bill is clear:

| Capacity | Solve what? | The cost. |
|------|-------------|-----------|
|**RAG / External Knowledge Access** | Model does not know private/real time information | Index maintenance, search delay (+500ms-2s), reference verification, document update synchronization |
|**Memory** | Cross-session/cross-wheel extension | Storage expansion, forgotten tactics, privacy compliance, perpetuation of false memories |
|**Context Engineering** | Multiple information sources cause context confusion | Layer design costs, Token budget need to be continuously aligned, over-compression leads to information distortion |
|**Planning / Workflow** | Multistep Tasks Organization | Prompt length surge, step drift, error cascade, interruption recovery |
|**Reflection** | Automatically detect and correct errors | Multi-rotation cost (x2-3 token), endless cycle, overcorrection |
|**Human-in-the-loop** | High-risk operations require human identification. | Block waiting, UX interruption, confirmation of fatigue, process delay |
|**Multi-Agent** | Conflict of roles, parallel implementation | Coordinated spending, Agent conflict decisions, Trade complexity multiplying, and cost linear growth |
|**Tool Use** | Interaction with the outside world | Tool Call Failed, Timeout Control, Permission Security, Results Validation |**Cost amplification effect:**When multiple combinations of capacities, the cost is not simply added up, but is interactively amplified:

```text
单能力延迟：
  RAG 检索：800ms
  Planning 拆解：1.2s
  Reflection 修正：+1 轮 LLM 调用（1.5s）
  Multi-Agent 协调：+500ms

组合后延迟：
  RAG + Planning + Reflection + Multi-Agent
  = 800ms + 1.2s + (1.5s × Agent数) + 500ms + 协调等待
  ≈ 5-8 秒（用户感知的"卡顿"）
```

That is why the introduction of capabilities requires restraint — the waiting time of users, your debugging time, the probability of system error is growing every step.

### 9.1.3 Levels of capacity complexity

Instead of using capability as a binary switch, let's see how complicated they are. The following figure is not the route of upgrading that all Agent must follow, but is an incremental reference**: the higher the system, the higher the delay, debugging, state consistency and evaluation costs.

```text
                        ┌─────────────────────────┐
                        │  高复杂度：自适应协同     │
                        │  多 Agent 根据任务自动    │
                        │  组队、分工、互审         │
                        ├─────────────────────────┤
                        │  高复杂度：决策边界       │
                        │  具备 Human-in-the-loop   │
                        │  高风险操作人类确认       │
                        ├─────────────────────────┤
                        │  中高复杂度：自我修正     │
                        │  单 Agent 具备 Reflection │
                        │  检测失败并自动重试/修正  │
                        ├─────────────────────────┤
                        │  中高复杂度：复杂任务编排 │
                        │  单 Agent 具备 Planning   │
                        │  多步骤任务自动拆分执行   │
                        ├─────────────────────────┤
                        │  中复杂度：上下文管理     │
                        │  具备 Context Engineering │
                        │  分层、预算、优先级管理   │
                        ├─────────────────────────┤
                        │  中复杂度：状态感知       │
                        │  单 Agent 具备 RAG+Memory │
                        │  能访问外部知识、记住偏好 │
                        ├─────────────────────────┤
                        │  基线：最小闭环           │
                        │  LLM + Tool Use + Loop    │
                        │  处理简单、独立的任务     │
                        └─────────────────────────┘
```
**The correct way to use this ladder:**-**Do not use it as a road map**: not first RAG, then Memory, then Planning, then Multi-Agent. The true order is determined by the question.
- **There is evidence for each addition**: confirmation that current problems cannot be solved in a simpler way and that more complex capabilities are introduced.
- **Allowing a combination of low complexity**: Not all scenarios need to climb to high complexity. A lot of scenes at RAG + Light Memory is the best solution.
- **Revertable**: If high-complexity capacity causes more problems, a more simple combination is a mature decision. **Self-examination:** - What kind of capability does the current scene have?
- Is there data or user feedback support for this ability to address issues?
- Are the indicators of capacity in place stable?
- Is it worth adding complexity, delay and maintenance costs?

### 9.1.4 Correct problem-driven rhythm

The following is the actual introduction of the rhythm (simplified) within three months by Agent:

```text
┌─────────────────────────────────────────────────────────┐
│  第 0 周：最小闭环上线                                    │
│  - LLM + 基础对话                                         │
│  - 用户手动粘贴资料内容                                    │
│  - 核心指标：回答是否合理（人工判断）                       │
├─────────────────────────────────────────────────────────┤
│  第 2 周：问题发现 — RAG 引入                              │
│  用户反馈："每次都要手动粘贴笔记，太麻烦了"                  │
│  问自己："这个问题有多频繁？" → 70% 的对话都需要查资料       │
│  引入：Markdown 文档索引 + 向量检索 + 引用输出              │
│  评测：20 个固定问题，检查召回率、答案准确性、引用正确性       │
│  结果：召回率 78% → 优化分块策略后 → 89%                   │
├─────────────────────────────────────────────────────────┤
│  第 6 周：问题发现 — Memory 引入                           │
│  用户反馈："每次开启新对话，它都忘了我在研究什么"            │
│  问自己："跨会话上下文对体验影响多大？" → 用户平均 3-5 次会话 │
│  引入：会话摘要 + 关键信息持久化                            │
│  评测：跨会话追问 10 个场景，检查上下文衔接准确性            │
│  结果：衔接准确率 82% → 调整摘要策略后 → 91%               │
├─────────────────────────────────────────────────────────┤
│  第 8 周：问题发现 — Context Engineering 引入              │
│  用户反馈："接了 RAG 和 Memory 后，上下文经常超限，         │
│           偶尔会忽略我之前设的规则"                           │
│  问自己："几个信息源了？组织方式合理吗？" → 3 个信息源       │
│  引入：上下文分层 + Token 预算 + 工具输出压缩                │
│  评测：10 个约束遗忘测试场景，检查约束遵守率                  │
│  结果：约束遵守率从 72% 提升到 94%                          │
├─────────────────────────────────────────────────────────┤
│  第 12 周：问题发现 — Planning 引入                        │
│  用户反馈："让它帮我整理一周的笔记，它经常漏掉某些文件夹"      │
│  问自己："任务是线性的还是需要动态规划？" → 需要分支处理     │
│  引入：简单的 ReAct 模式，允许 Agent 自己决定下一步           │
│  评测：10 个多步骤整理任务，检查步骤覆盖率和遗漏率            │
│  结果：遗漏率从 20% 降到 5%                                │
├─────────────────────────────────────────────────────────┤
│  第 16 周：问题发现 — HITL 引入                            │
│  用户反馈："它删了一个我不确定该不该删的文件，没问我"        │
│  问自己："哪些操作风险高到必须确认？" → 文件删除、配置修改   │
│  引入：风险分级 + 确认模式 + 批次确认                        │
│  评测：高风险操作确认率 100%，用户误确认率 < 5%             │
│  结果：无意外文件删除事件，用户信任度提升                    │
├─────────────────────────────────────────────────────────┤
│  第 18 周：暂不引入任何新能力                               │
│  原因：当前五个能力稳定，无明确问题信号                       │
│  Reflection 和 Multi-Agent 留到有证据时再说                  │
└─────────────────────────────────────────────────────────┘
```
**Key observations:**1.**Every capacity is introduced with a specific problem trigger**not because "others are using it"
2. **Every time it's introduced, it's a quantitative assessment.** It's not like it's getting better.
3. **There are enough observation periods between the two introductions** (2-4 weeks) and the pattern of issues is really clear
4. **Week 18 has chosen not to be introduced**, which is the easiest but equally important decision to ignore

### 9.1.5 What's the "minimal circle"?

Before we talk about the power mix, we need to figure out what the "minimal closure" is -- because you need to have something to run before you can introduce anything.

```text
最小闭环 = prompt + LLM 决策 + 工具调用 + 循环控制 + 状态管理
```
**What can the smallest closed ring do:**- Receive user commands
- Call tool to get information/ execute operations
- Results-based decision-making for the next steps
- Loop until the job is finished
- Return final result **Minimum closed circle boundary:**```text
✅ 属于最小闭环：
  - "帮我搜索这个文件夹里的所有 .md 文件"
  - "把这段代码里的 foo 替换成 bar"
  - "读这个 CSV 文件，统计每个分类的数量"

❌ 需要增强能力：
  - "根据我的笔记回答这个问题" → 需要 RAG
  - "记住我上次说的偏好" → 需要 Memory
  - "信息源多了，上下文经常乱" → 需要 Context Engineering
  - "把这个需求拆成子任务逐一完成" → 需要 Planning
  - "检查你生成的代码有没有 bug" → 需要 Reflection
  - "这个操作太重要，不能让它自己决定" → 需要 Human-in-the-loop
  - "找人审查你的方案" → 需要 Multi-Agent
```
**Importance of the minimum closed ring as a baseline:**Answer these questions with a minimum closed loop before introducing any enhancements:

1.**Can this task be done with a minimum closed ring?**→ If so, why do we have to do it?
2.**Where's the card when it's done? This is the only legitimate reason for introducing new capabilities.
3.**How much better is the new capability compared to the minimum closed ring?**→ This is the baseline for evaluation

---

## 9.2 Capacity portfolio cases

The following six cases cover the most common Agent scene. Each case starts with a "start-up problem" and introduces capacity sequentially, with a clear indication that "not for the time being" — the latter is as important as the former.

#### Case I: Personal Knowledge Assistant**Scene description:**Users have a large number of local notes (Markdown, PDF, Web Clip) and hope that Agent will be able to answer questions based on this information and give sources of reference.**Start question:**- User information is extensive and the model does not know what the information is.
- User needs to cite the source.**Priority capacity:**-**RAG / External knowledge access**. That's core competence -- without it, Agent can only give a generic answer, and it can't meet the core requirement of "my notes."**Minimal version achieved:**```text
文档目录 → 文档解析（Markdown/PDF → 纯文本）
         → 文本切分（按段落/标题，每块 500-1000 tokens）
         → 向量化（embedding model）
         → 存入向量数据库（Chroma / Milvus / Pinecone）

用户询问 → 查询向量化 → 检索 Top-K（K=5-10）
        → 拼接检索结果到 Prompt
        → LLM 生成回答（附带引用标记）
```
**Assessment of dimensions:**- Recall rate: Retrieving relevant documents found Blocks
- Accuracy of answer: Whether the resulting answers correctly use the information retrieved
- Quoting correctness: whether the reference mark points to the correct source
- Refusal rate: When the information is not relevant, Agent honestly indicates that he does not know **Follow-up questions:** - Users would like to remember the current research theme and the next dialogue could continue.
- Multicycle queries need to be followed by context.
- There is a lack of correlation between the multiple questions and answers on the same subject. **Reintroduced:** - **Summaries of sessions and lightweight Memoory**. Note that this is not the introduction of a complete long-term memory system, but a light solution to the specific issue of "Remembering the current research theme". **Memory Minimum:**```text
每次会话结束：
  → 用 LLM 生成会话摘要（研究主题、关键发现、待解决问题）
  → 持久化存储（JSON 文件或轻量数据库）

下次用户开启新会话：
  → 加载最近的会话摘要
  → 附加到系统 Prompt 中作为上下文
  → 用户可以随时要求"忘记之前的上下文"
```
**Not introduced:**-**Multi-Agent**unless there is a clear need for parallel research or review. If the user is just a person, single Agent is totally enough.
-**Reflection**, unless there are clear systemic problems with the quality of search results. RAG's search quality issues should be addressed as a matter of priority by optimizing the segmenting strategy and adjusting the search parameters, rather than introducing Reflection so that it "checks itself".
-**Planning**unless the user's assignment becomes clearly multi-step (e.g. "Help me cross-check between the three sources").**Introduction of path overview:**```text
最小闭环
  → RAG
    → 检索质量迭代
      → Memory
        → 稳定运行
          → Planning？（等待问题信号）
```

---

#### Case II: Code Review **Scene description:**Team needs an Agent to review Pull Request, not only on the surface of diff, but also to understand the context of the code and perform test validation judgement. **Start question:** - Agent, read diff only and output general recommendations (e.g., "Consider adding notes", "check empty pointers").
- I can't verify my judgment -- I can say, "there may be a performance problem," but I can't actually verify it.
- The absence of context is suggested - there is no understanding of the caller or caller for this function. **Priority capacity:** - **Tool calls: reading files, searching codes, running tests**. It's the key to moving from "prisal censorship" to "in-depth censorship".
- **Reflection: modified judgement after test failure**. Agent needs to correct its own conclusions when the tool calls results that contradict the initial judgement. **Minimal version achieved:**```text
接收到 PR diff
  → 分析 diff 中的变更
  → 对每个可疑点，调用工具：
      - read_file: 读取相关文件的完整内容
      - search_code: 搜索函数/变量的所有引用位置
      - run_test: 运行相关测试
  → 基于工具结果形成审查意见
  → 如果测试失败，Reflection：
      - 分析失败原因
      - 确认是自己的判断有误还是代码确实有问题
      - 修正审查意见
  → 输出最终审查报告
```
**Key design decisions: why first introduce Reflect rather than Multi-Agent?**For the code review scene, the first response is "introducing Multi-Agent, writing one review." But if you examine Agent without the tools to call, the other Agent just says, "Read it again and diff give general advice" -- two blind people can't see it together.

The correct sequence is:**Let individual Agent call "see" through the tool, then "Correct" through the Reflection, and finally consider Multi-Agent's division of labour.****Follow-up questions:**- After the review has reached a certain stage, Agent will need to conduct a second review of the revised code (to examine whether the revised code introduces new issues).
- There is a conflict between the role of a single Agent, who also plays the role of "reviewer" and "reviser" -- it may be too tolerant of its own proposals.**Reintroduced:**-**Multi-Agent**: One Agent reviews and makes recommendations and the other Agent reviews the revised code. Note that this is not a complete Multi-Agent system, but the "Reviewer Model" -- two Agent serial work, not complex coordination.**Multi-Agent Minimum:**```text
Reviewer Agent（审查者）：
  输入：PR diff
  输出：审查意见列表
  工具：读文件、搜索代码、运行测试

Verifier Agent（验证者）：
  输入：修改后的代码 + Reviewer 的审查意见
  输出：验证报告
  行为：逐条检查 Reviewer 的建议是否被正确实现
       检查修改是否引入了新问题

冲突解决规则（简单版）：
  - 如果 Reviewer 和 Verifier 意见一致 → 采纳
  - 如果意见不一致 → 标记为"需人工审查"
  - 禁止两个 Agent 互相调用形成循环
```
**Not introduced:**-**Long-term memory**unless it is necessary to remember project engagements, test habits or user preferences. If project specifications and testing strategies have been defined in the project document, the marginal benefits of Memoory are low.
- **Planning**, unless the review mission becomes clearly multi-step (e.g. "Censorship safety first, performance later, readability last"). **Introduction of path overview:**```text
最小闭环
  → Tool Use（有工具才能深入分析）
    → Reflection（有外部信号才能修正）
      → Multi-Agent Reviewer（角色冲突时才分工）
        → 稳定运行
          → Memory？（等待需求证据）
```

---

#### Case III: Individual assignments**Scene description:**User hopes that Agent can help with complex multi-step tasks (e.g., "Appointing CI/CD for this open-source project"), to continue after the critical nodes have been suspended and support has been interrupted.**Start question:**- The task is multi-step and easy to miss.
- The user wishes to confirm the key node (e.g. before creating GitHub Security).
- Manual tracking of the mission is cumbersome.**Priority capacity:**-**Planning / Worklow Pattersons**. Multi-step missions naturally require structured organizations.
-**Human-in-the-loop**. Critical operations require manual validation, which is a safety requirement rather than an experiential optimization.**Minimal version achieved:**```text
用户任务："为仓库配置 CI/CD"
  → Planning Agent 拆解：
      Step 1: 分析项目结构，确定 CI/CD 方案
      Step 2: 编写 CI 配置文件
      Step 3: 生成需要的 Secrets 列表
      Step 4: [HITL] 等待用户确认 Secrets 列表
      Step 5: 配置 GitHub Secrets
      Step 6: 触发首次 CI 运行
      Step 7: [HITL] 检查运行结果，等待用户确认
  → 每个步骤执行完后更新状态
  → 用户可随时查看进度
```
**Human-in-the-loop design elements:**```text
✅ 好的 HITL 设计：
  - 在不可逆操作前暂停（删除、发布、权限变更）
  - 暂停时给出明确的选项："确认执行 / 跳过 / 修改参数"
  - 超时后的默认行为是"不执行"（safe default）

❌ 不好的 HITL 设计：
  - 每一步都暂停（确认疲劳）
  - 暂停时信息不足，用户无法判断
  - 超时后自动执行高危操作
```
**Follow-up questions:**- This will continue after a long break.
- The history of mandate implementation requires traceability.**Reintroduced:**-**Task status and Checkpoint**, part of which will go into six courses. The core idea is to perpetuate the mandate and support recovery from the point of interruption.**Checkpoint Minimum:**```text
任务状态结构：
{
  "task_id": "xxx",
  "goal": "为仓库配置 CI/CD",
  "steps": [
    {"id": 1, "desc": "分析项目结构", "status": "done"},
    {"id": 2, "desc": "编写 CI 配置", "status": "done"},
    {"id": 3, "desc": "生成 Secrets 列表", "status": "in_progress"},
    ...
  ],
  "checkpoint_data": {
    "branch": "feature/ci-setup",
    "ci_file": ".github/workflows/ci.yml",
    ...
  },
  "last_updated": "2024-03-15T10:30:00Z"
}

恢复流程：
  用户重新连接 → 检测未完成任务 → 加载 Checkpoint → 从断点继续
```
**Not introduced:**-**Automatically long term, unless the user clearly requires a cross-mission preference. Independence between mandates is a feature rather than a flaw.
- **RAG**, unless task execution requires frequent access to external documents.
- **Multi-Agent** does not need parallels in a single user scenario. **Introduction of path overview:**```text
最小闭环
  → Planning + HITL（任务结构化和安全需求）
    → Checkpoint（中断恢复需求）
      → 稳定运行
        → Memory？（跨任务偏好是否需要延续）
```

---

#### Case four: Smart customer service, Agent.**Scene description:**Smart customer service for the electrician platform, which needs to answer product questions, process refunds, query the order status. Some of the issues can be dealt with automatically, sensitive operations (e.g. refunds) need to be manually identified and complex issues need to be transferred to manual passenger service.**Start question:**- User consulting product information, Agent needs a product bank-based response.
- User query order status, Agent needs access to order system.
- Refund/exchange operations involve funds and inventories and cannot be implemented automatically.**Priority capacity:**-**RAG / External knowledge access**: Product information, policy documents, FAQ etc. require real-time retrieval.
-**Tool Use**: Call an internal system of order query API, Logistics query API etc.
-**Human-in-the-loop**: sensitive operations such as refunds, exchange clearances require manual confirmation.**Why are these three capacities introduced simultaneously?**The special features of the guest scene are that RAG, Tool Use, HITL are not solving the "several deepening of the same problem" but are addressing the "three independent and simultaneous hard demands":

- No RAG → Product Information Unable to answer
- Unable to query purchase order without Tool Use
- There's no HITL. There's a financial risk of refund.

This is "the scenario itself requires multiple capabilities to produce the least available product". But even so, step-by-step verification is recommended - make sure the RAG is retrieved correctly, then access Tool Use, and finally add HITL.**Minimal version achieved:**```text
用户消息
  → 意图分类（产品咨询 / 订单查询 / 售后处理 / 闲聊）
  → 路由到对应处理流程：

产品咨询流程：
  → RAG 检索产品知识库
  → 拼接检索结果生成回答
  → 附带产品链接

订单查询流程：
  → 验证用户身份
  → 调用订单 API
  → 格式化订单信息返回

售后处理流程：
  → 查询订单状态
  → 判断是否符合退换货条件
  → [HITL] 如需退款 → 生成退款申请 → 等待人工审批
  → [HITL] 审批通过 → 执行退款 → 通知用户
```
**Follow-up questions:**- Users contact the client ' s service several times and are rejustified each time.
- Returners ' preferences and historical issues need to be remembered.
- When complex issues are transferred manually, artificial passenger service needs to see the context of the dialogue. **Reintroduced:** - **Session Memory**: Remember the context of the current session and the recent history of contact. Attention is given to "talk-level" rather than "user-level long-term archives" — the former addressing the problem of repetitive statements, the latter involving privacy compliance. **Memory Design (Customs Special):**```text
会话级记忆（7 天有效）：
  - 本次会话的对话历史
  - 本次会话涉及的产品/订单
  - 本次会话的未解决问题

用户级记忆（需要用户授权）：
  - 常用收货地址
  - 最近 3 次购买记录
  - 语言偏好

记忆清理策略：
  - 会话级记忆：会话结束后 7 天自动清除
  - 用户级记忆：用户可随时查看和删除
  - 敏感信息（支付、密码）永不记录
```
**Not introduced:**-**Planning**: client dialogue is usually linear (if-else route) and does not require dynamic planning
-**Reflection**: feedback from the guest scene is from user satisfaction rating instead of Agent self-correction
-**Multi-Agent**: Unless two different roles, pre-sale and post-sale, need to be addressed simultaneously, but usually by route**Introduction of path overview:**```text
最小闭环
  → RAG + Tool Use + HITL（场景硬需求，但分步验证）
    → Memory（减少重复说明，注意隐私边界）
      → 稳定运行
        → 根据用户满意度数据决定下一步
```

---

#### Case V: Data Analysis Assistant **Scene description:**Data analyst needs Agent to help write SQL, analyze data, and generate visualized reports. The task is usually multi-step: understand the need to write a query → validates the results → explains the finding → produces a chart. **Start question:** - Users describe needs in natural languages, and Agent needs to be translated into SQL.
- After SQL execution, Agent needs to check whether the results match expectations.
- If the result is not correct, Agent needs to fix the query itself. **Priority capacity:** - **Tool Use**: Implementation of SQL, reading table structure, query data dictionary.
- **Reflection**: SQL automatically check and amends when performance fails or results are abnormal. **Why first?

For single-form queries and one-time indicators to calculate such tasks, the user ' s natural language has given the main analytical objectives - "Look at sales trends last month, split by region, and find the three fastest growing categories." The first thing to do at this point is not "will it plan" but "can it read Schema correctly, generate SQLs, perform queries and fix them when the wrong information appears."

But it's not that data analysis doesn't need Planning. Planning is of clear value only when the task is upgraded to cross-table exploration, staged validation assumptions, first checking A, then results-based B, and final consolidation visualization. The sequence should be to stabilize the implementation and validation loops and then introduce a multi-step analysis of needs into Planning. **Minimal version achieved:**```text
用户需求 → Agent 分析：
  1. 读取数据库 Schema，了解表结构和字段
  2. 生成 SQL 查询
  3. 执行 SQL
  4. 检查结果：
     - 执行是否成功？→ 如果失败，Reflection：分析错误信息，修正 SQL
     - 结果是否合理？→ 如果行数为 0 或数值异常，Reflection：检查查询逻辑
     - 结果是否符合用户意图？→ 对结果做合理性检查
  5. 解释发现
  6. 可选：生成可视化代码（matplotlib / eCharts）
```
**Reflection for specific applications in the data analysis scene:**```text
Reflection 触发条件：
  ✅ SQL 语法错误 → 读取错误信息，修正语法
  ✅ 结果集为空 → 检查 WHERE 条件是否过于严格
  ✅ 数值明显异常 → 检查 JOIN 是否正确
  ✅ 结果与常识矛盾 → 提醒用户可能存在数据质量问题

Reflection 停止条件：
  ❌ 修正 3 次后仍然失败 → 向用户说明情况，请求指导
  ❌ 不确定是否正确 → 标注"需要人工验证"
  ❌ 发现数据源本身有问题 → 报告问题，不继续尝试修复
```
**Follow-up questions:**- Complex analysis requires multiple steps (see table A, based on table B, combined analysis).
- User wants Agent to remember the usual analytical templates and preferences.
- The analysis across multiple data sources requires structured steps. **Reintroduced:** - **Planning**: introduced when analytical tasks are upgraded from "one query" to "multi-step analysis process".
- **Memory**: Remember user analytical habits (commonly used indicators, preferred chart type, naming norm). **Not introduced:** - **RAG**: unless analysis requires frequent reference to external methods for documentation or industry standards
- **Multi-Agent**: Single-person analysis scenario, no role conflicts **Introduction of path overview:**```text
最小闭环
  → Tool Use + Reflection（翻译+修正，分析场景核心）
    → Planning（多步骤分析需求明确后）
      → Memory（分析习惯复用需求明确后）
        → 稳定运行
```

---

#### Case VI: Writing Collaboration**Scene description:**Users and Agent collaborate on technical blogs. Agent needs to understand the user style of writing, remember the points discussed earlier, retrieve references and perform quality checks based on external evidence after each change.**Start question:**- User wants Agent consistent writing style.
- User needs Agent reference technology.
- After Agent has finished a paragraph, the user hopes that it will be able to check the problem (retroactivity of the reference, operation of the code example, compliance of terms with the agreement and whether user feedback has been processed).**Priority capacity:**-**RAG**: Retrieving technical references, related articles, API documents.
-**Memory**: Remember user writing style preferences, terminology choices, structure habits.**Why is this scene being introduced at the same time by RAG+Memory?**In writing scenes, RAG and Memory solve different dimensions:
- RAG solves "What to write" - providing accurate technical content.
- Memoory solves "How to write" -- consistent style and terminology.

They are independent of each other but cannot be separated. There's no RAG inaccuracies, there's no memory incoherence.**Minimal version achieved:**```text
写作协作流程：
  1. 用户提出写作主题
  2. Agent 检索参考资料（RAG）
  3. Agent 回忆用户风格偏好（Memory）
  4. Agent 生成初稿
  5. [HITL] 用户审阅，提出修改意见
  6. Agent 根据反馈修改
  7. Agent 质量检查：
     - 引用校验（检索原文，确认引用存在）
     - 代码示例测试（运行或静态检查）
     - 术语/风格清单检查（对照 Memory 中的明确偏好）
     - 用户反馈核对（逐条确认修改意见已处理）
  8. 输出终稿

Memory 存储结构（写作场景）：
{
  "style_preferences": {
    "tone": "专业但亲切",
    "sentence_length": "中短句为主",
    "code_style": "Python, type hints 必加",
    "preferred_terms": {
      "use": ["数据库", "查询"],
      "avoid": ["DB", "query"]
    }
  },
  "structural_habits": {
    "opening": "故事/问题引入",
    "body": "概念 → 原理 → 示例 → 注意事项",
    "closing": "总结 + 延伸阅读"
  },
  "common_mistakes_to_avoid": [
    "不要过度使用被动语态",
    "代码示例需要可运行",
    "技术术语首次出现需要解释"
  ]
}
```
**Follow-up questions:**- After changing multiple rounds, Agent needs to verify the quality of articles based on a clear check (not relying on user-by-user identification).
- The long articles are complex in structure and require section management. **Reintroduced:** - **Reflection**: Quality check only for external feedback signals — can references be found in the original text, can code examples run, whether user changes are article-by-article covered, and if terms are consistent with the established style list.
- **Planning**: Structural planning and outline management. **Reflection in the design of the writing scene:**```text
触发信号：
  1. 引用校验失败：生成内容中的来源无法在 RAG 原文中找到
  2. 代码检查失败：代码示例无法运行、类型检查失败或输出不符合预期
  3. 术语清单不匹配：使用了用户明确要求避免的术语
  4. 用户反馈未覆盖：修改意见清单中仍有未处理项

修正规则：
  - 每完成一个章节后自动运行
  - 发现问题后只修正对应问题，不重写整篇
  - 同类问题修正超过 2 次仍失败 → 标记并请用户介入
  - 纯主观表达质量（"够不够好看"、"语气是否高级"）交给用户或 Reviewer 清单，不用模型自评冒充 Reflection
```
**Not introduced:**-**Multi-Agent**: Writing is creative work, and an Agent co-reads enough. The introduction of the Multi-Agent "A Writing One Review" could lead to a lack of consistency in style.
-**Human-in-the-loop**enhanced version: Writing collaboration is naturally a HITL mode (HITL for each user review) and no additional system-level HITL mechanism is required.**Introduction of path overview:**```text
最小闭环
  → RAG + Memory（内容准确 + 风格一致）
    → Reflection（基于外部信号做质量检查）
      → Planning（长文结构管理）
        → 稳定运行
```

---

## 9.3 Counter-model of capacity mix

I said, "Do what." This subsection says, "Don't do it."

#### Counter-model I: Capability Hoarding **Symptoms:**```text
"我们的 Agent 用了 RAG + Memory + Planning + Reflection + Multi-Agent，
  还有 Tool Use、Guardrails、Human-in-the-loop..."
```
**Problem diagnosis:**Says "what" but says "why." Each ability is added to "if it works." As a result, the system was so complicated that no one could fully understand and no one could be held responsible for it.**The antidote:**- Each ability must have a corresponding "issue/ticket" to record the reasons for its introduction.
- Regular "Capacity Inventory": Is it still working? Still solve the problem?
- If no one can explain why a power exists, consider removing it.

---

#### Counter-model two: "Online when it's perfect."**Symptoms:**```text
"RAG 的召回率才 78%，等优化到 90% 再上线"
"Memory 的遗忘策略还没调好，先不上"
"Planning 有时候会漂移，等我们解决了再发布"
```
**Diagnosis of the problem:**Waiting for a perfect minimum is equal to never being published. Users prefer a flawed Assistant to wait for a non-existent Assistant. Furthermore, real use feedback is not available without publication and no real optimization without feedback.**The antidote:**- Define "good enough" threshold, not "perfect".
- The ability below the threshold can be online but labelled as "experimental function".
- Set up a user feedback channel for real use driver optimization **Criteria for judgement:**```text
能上线的最低标准：
☐ 核心功能是否可用？（不能有阻塞性 bug）
☐ 安全问题是否处理？（不能泄露数据、执行危险操作）
☐ 失败模式是否优雅？（出问题时告诉用户，而不是悄悄出错）
☐ 用户是否可以选择不使用？（能力应该是可选的）

不需要等到的标准：
☐ 性能是否最优？（可以后续优化）
☐ 边界情况是否全覆盖？（有些边界只有用了才会发现）
☐ 所有评测指标是否达标？（真实数据可能和评测集不同）
```

---

#### Anti-model three: blind and wind.**Symptoms:**```text
"Hacker News 上那篇文章说了，Multi-Agent 是 2024 年最重要的趋势"
"大家都在用 LangGraph 做 Agent 工作流，我们也应该用"
"XXX 公司的技术博客说他们的 Agent 用了 Reflection，效果很好"
```
**Problem diagnosis:**The scene, data, constraints, users are different from you. The solutions that suit them don't necessarily suit you. The replacement of community hot spots with their own problem analysis is the fastest way to introduce unnecessary complexity.**The antidote:**- When reading other people's programs, you focus on "what's wrong with them," not "what's the technology they use?"
- If you can't spell it out in one sentence, you can't introduce it.
- Think of community articles as "menu of options" instead of "list of necessity." **Conversion exercise:**```text
读到："我们用 Multi-Agent 提升了代码审查质量"
不要想："我也应该加 Multi-Agent"
应该想："他们的代码审查遇到了什么问题？这个问题我也有吗？
        他们用 Multi-Agent 解决了什么？为什么单 Agent 不够？
        我的代码审查流程中，单 Agent 的瓶颈是什么？"
```

---

#### Counter-module IV: No assessment, no overlap after introduction**Symptoms:**```text
"我们两周前加了 RAG，用户说好像好了一点...其实我也不确定"
"Memory 加上去了，没看效果，反正应该有用"
"Planning 的步骤有时候不太对，但大部分时候还行吧"
```
**Diagnosis of the problem:**Introduction capacity is only the beginning, not the end. The introduction of non-assessed capabilities is tantamount to adding "no impact" variables to the system. Over time, you don't know whether the quality of the system is rising or falling.**The antidote:**- Each capability must be predefined when introduced
- Weekly/monthly access to assessment indicators to confirm no degradation
- Re-engineer all available capabilities when new capabilities are introduced and check if they affect each other **Evaluation of rhythm recommendations:**```text
引入前：建立基线评测（当前系统在这些指标上的表现）
引入后第 1 周：每日评测（快速确认方向是否正确）
引入后第 2-4 周：每周评测（观察使用模式稳定后的表现）
引入后第 2 个月起：每月评测（持续监控，防止退化）
```

---

#### Counter-model V: Lack of coordination between capacities**Symptoms:**```text
RAG 检索到的内容，Memory 也记了一份（重复存储）
Planning 生成了 5 步计划，但 Reflection 认为第 2 步已经完成（信息不一致）
Multi-Agent 中的 Agent A 修改了文件，Agent B 不知道（状态不同步）
```
**Problem diagnosis:**Capabilities are not stand-alone plugins that share status and influence each other ' s behaviour. System behaviour is unpredictable when multiple capacities have different understandings of the same data.**The antidote:**- Defining the boundaries of competence: who is responsible for what data
- Unified state management: all capabilities read through the same State layer Write
- Clear compacts (schema/format) for transmission of information between competencies
- Consistency between periodic checks **CAPACITY COORDINATION LIST:**```text
☐ RAG 检索结果是否进入了 Memory 系统？如果是，是否需要？
☐ Memory 中的信息是否影响了 Planning 的步骤生成？
☐ Reflection 的修正是否更新了 Planning 的状态？
☐ Multi-Agent 中的各 Agent 是否共享同一个 Memory 视图？
☐ 一个能力的输出变更是否会破坏另一个能力的输入假设？
```

When a combination of capabilities begins, they should not be matched by a Prompt ad hoc agreement, but should be carried at the time of operation: a unified State, Trade, Checkpoint, Eval regression and permission boundaries will be carried out in the Harness structure of Course 6. This chapter deals with "shouldn't it be a combination" and course six with "how to stabilize after a combination."

---

## 9.4 Gradual introduction of rhythms and signals

#### When should we speed up the introduction?

The following signals indicate that the user ' s needs have clearly exceeded the current system ' s capacity boundaries and that accelerated introduction is reasonable:

```text
加速信号：
✅ 同一个问题的用户反馈在 2 周内出现了 5+ 次
✅ 当前能力的评测指标持续下降（说明需求在增长但能力没跟上）
✅ 竞争对手已经提供了这个能力，用户开始流失
✅ 问题的解决方案明确且风险可控
✅ 用户明确表示"如果不支持 X 我就没法继续用了"
```
**Speeding up does not represent a rush.**Even if it accelerates, keep the process of "inclusion of evaluation and observation". The acceleration is the observation cycle (e.g. from 4 weeks to 2 weeks) rather than skipping the evaluation.

#### When should we suspend and consolidate?

The following signals indicate that you need to stop and digest, rather than continue to add new capabilities:

```text
暂停信号：
🛑 上一次引入的能力的评测指标还不稳定
🛑 有已知 bug 还没修（超过 3 个 open issue）
🛑 团队成员反映"系统太复杂了，新加入的人看不懂"
🛑 用户反馈中关于"慢"和"不可靠"的比例在上升
🛑 你发现自己说不清当前系统有多少个能力在工作
```
**The suspension is not a failure; it is responsible.**The suspension may include:
- Fix known bug
- Refine document and Trace
- Optimizing the assessment system
- Capacity no longer required for clean-up (see 9.5)
- Reduce system complexity

#### Three principles of rhythm control**Principle I: a new variable at a time**Only a new capability is introduced at any given time. If a capacity is not working well when it is introduced, you can only determine that it is. You never know which one works and which brings the problem.

```text
❌ 同时引入 RAG + Memory：
  "检索变好了，但跨会话上下文好像也有改善...不确定是哪个原因"

✅ 先引入 RAG，稳定 2 周后引入 Memory：
  "RAG 引入后召回率从 0% 提升到 85%（确定是 RAG 的效果）"
  "2 周后引入 Memory，跨会话衔接准确率从 28% 提升到 80%（确定是 Memory 的效果）"
```
**Principle II: Assessment indicators always precede new capabilities**If you do not have a running evaluation process, do not introduce new capabilities. The introduction without an evaluation is like walking with your eyes closed -- you don't know if you're going right or if you're going further away from the target.**Principle III: Reissued periodically**Regardless of whether the system is stable or not, a capacity reset is regularly performed:

```text
复盘检查清单：
☐ 每个已引入的能力：评测指标是否稳定或改善？
☐ 每个暂未引入的能力：不引入的理由是否仍然成立？
☐ 是否有新的问题模式出现？
☐ 是否有能力可以被降级或移除？
☐ 系统整体复杂度是否可以降低？
☐ 团队对系统的理解是否充分（新成员能否快速上手）？
```


## 9.5 Degradation and removal of capabilities

Most of the classes only say "how" and don't say "how." But mature system design and mature engineers must be able to judge when a capability should be removed.

#### When should we consider removing them?

| Signal | Annotations | Example: |
|------|------|------|
|**Problem disappeared**| The problem that was introduced to this ability no longer exists. | User changed workflow, no more cross-conferences, memory |
|**Capacity has never been used**| Plus consistently useless and very low usage rate (< 5%) | The Planning system is perfect, but 95% of the tasks are one step. |
|**Cost is greater than gain**| Capacity maintenance costs/delayed/mistakes exceed its value | Memoory often misreading causes user trouble, maintaining forgotten strategies takes longer than saving time. |
|**There are simpler options**| I found out I didn't need that ability to solve the problem. | Prompt Optimize + Better Tool Description achieves effects close to Planning |
|**Conflict with other capabilities**| The behavior of both abilities is contradictory, and users are confused. | Memoory remembers one style, but RAG retrieves examples of another style |
|**Evaluation indicators continue to decline**| Quality of capacity continues to deteriorate and optimizes costs High | RAG index updates are slower and recall rates continue to decline |

#### How to safely downgrade or remove

Removal capacity needs to be more cautious than introducing capacity, as users may already have relied on certain behaviours.**Downgrade removal process:**```text
第一步：确认影响范围
  - 统计该能力的使用频率
  - 列出依赖该能力的用户场景
  - 评估移除后的用户体验变化

第二步：寻找替代方案
  - 能否用更简单的方式覆盖核心需求？
  - 能否把能力从"自动"改为"按需触发"？
  - 能否把能力限制到更小的范围？

第三步：渐进降级
  方案 A：从"自动"改为"手动"
    原：每次对话自动执行 Memory 摘要
    改：用户输入 /summarize 时才执行

  方案 B：缩小范围
    原：Memory 记录所有对话
    改：Memory 只记录用户明确标记为"重要"的对话

  方案 C：用更轻量的替代
    原：完整的 ReAct Planning
    改：固定的 Chain 流程（如果大部分任务已标准化）

第四步：灰度移除
  - 对 10% 用户关闭该能力，观察反馈
  - 如果无负面反馈，扩大到 50%
  - 如果持续无问题，完全移除

第五步：记录决策
  - 为什么移除？当初为什么引入？学到了什么？
  - 这段经验对未来的能力引入决策有什么帮助？
```
**Degraded better than direct removal:**In many cases, reducing capacity from "active" to "passive" is a better option:

```text
原状态：Memory 自动记录每次会话
降级后：Memory 只在用户明确要求时记录

原状态：RAG 自动检索每次查询
降级后：RAG 只在用户提及"查一下"时触发

原状态：Planning 自动拆解所有任务
降级后：Planning 只在任务超过 5 步时触发

原状态：Multi-Agent 并行处理
降级后：默认单 Agent 处理，用户添加 --review 标记时启动 Reviewer
```

#### Validation of effects after removal

After removing a capability, need to be confirmed:
- Has the problem previously addressed by that capacity re-emerged?
- Has the system delay improved?
- Has the user feedback changed?
- Has the maintenance burden been reduced?

If one capacity is removed, none of the above indicators change — that means that it is unnecessary and that the removal is correct.

---

## 9.6 Field exercise: capacity to make decisions for new scenes

Here are three new scenarios. For each scene:
1. To determine which capacities should be prioritized
2. Indicate which competencies are not introduced and why
3. Draw capability introduction path

#### Practice I: Review of legal instrumentsAgent **Scene:**The law firm needs an Agent to assist the solicitor in reviewing the contract. Agent needed to check whether the contract terms were in compliance, whether there were risk clauses and whether key clauses were missing. The results of the review require final confirmation by a manual lawyer. **Binding:** - The contract contents are highly sensitive and cannot be uploaded to external services
- Different contract templates for different industries (technology, finance, real estate)
- Possible legal risk of an error being reviewed
- All internal knowledge base (past case, contract template library) **Please judge:** - Priority capacity:      
- Not included:   
- Entry path:   

<details > <summary > </summary > **Priority capacity:** - **RAG**: Need to retrieve the Institute ' s internal knowledge base (past case, contract template) and have to be locally deployed (privileged)
- **human-in-the-loop**: final decision on legal review must be confirmed by a human lawyer, which is a hard demand **Not introduced:** - **Memory**: each contract is independent and cross-contract memory may lead to confusion of information
- **Planning**: contract review is structured (article-by-article) and a fixed review list is sufficient without dynamic planning
- **Reflection**: Agent self-inspects contracts of less quality than human lawyers and self-checks for external signals of lack of legal judgement
- **Multi-Agent**: Single-person review of scenes, an Agent + human lawyer confirmed sufficient **Introduction path:**```text
最小闭环（LLM + 合同读取工具）
  → RAG（检索知识库，对比合同条款）
    → HITL（人工确认节点）
      → 稳定运行
```

</details>

---

#### Practice II: Smart Home Control Agent**scene:**Users interact with Agent by voice/text. Agent needs to control the lighting, air conditioning, curtains, sound, etc., to understand the user's daily habits and to adjust automatically to the scene (e.g. "I'm going to sleep" to trigger lights, close curtains, lower air conditioning).**Binding:**- Low delay required for equipment control (<500ms)
- User habits vary from person to person.
- The scene trigger requires user confirmation (prevent error)
- Support multiple users (family members have preferences)**Please judge:**- Priority capacity:      
- Not included:   
- Entry path:   

<details > <summary > </summary >**Priority capacity:**-**Tool Use**: Base capacity of control equipment (calling equipment API)
-**Memory**: Remember user preferences (temperature, light, common scenes)
-**Human-in-the-load**: confirmation to users when scene triggers (security requirements)**Not introduced:**-**RAG**: Smart home control does not depend on external knowledge
-**Planning**: scenes are usually predefined ("Sleep" + Lights + Curtains + Temperature) without dynamic planning
-**Reflection**: Device control results can be confirmed by sensor feedback (lights turned off), no Agent reflection is required
-**Multi-Agent**: single-user service, no parallel**Introduction path:**```text
最小闭环 + Tool Use（设备控制）
  → Memory（记住用户偏好）
    → HITL（场景确认）
      → 稳定运行
```

</details>

---

#### Practice III: Auto-maintenance of technical documents **scene:**Open-source project maintainer needs an Agent auto-maintenance technical document. When the code changes, Agent needs to detect which documents need to be updated, automatically generate the document PR and explain the changes in the PR. **Binding:** - Consistency between documents and codes is essential.
- Need to understand the impact of changes across multiple documents
- Document quality influences the onboarding experience of new users
- Document changes require final approval by human defenders **Please judge:** - Priority capacity:      
- Not included:   
- Entry path:   

<details > <summary > </summary > **Priority capacity:** - **Tool Use**: Read replacement code diff, search affected documents, create PR
- **Reflection**: Compare code and document consistency after document generation (e.g. check for API parameter names)
- **Planning**: complex changes may affect multiple documents and require structured processing **Not introduced:** - **RAG**: document content is derived from the code itself and does not require external knowledge Library
- **Memory**: no cross-session status required for independent processing of each document update
- **Multi-Agent**: Single Agent can complete the full process of reading changes → updating documents **verifying consistency'. PR Approval is done by human defenders, no need for Agent Reviewer** Introduction path:**```text
最小闭环 + Tool Use（读代码、搜文档、创 PR）
  → Reflection（验证文档-代码一致性）
    → Planning（多文件变更的文档更新编排）
      → 稳定运行
```

</details>
