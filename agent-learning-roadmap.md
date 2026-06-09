# Agent 开发与产品知识体系 & 路线图

一套从入门到精通的系统性学习路径，分为七个课程。

---

## 课程一：初识Agent

**定位**：建立感性认知，不写代码。先"看见"Agent，建立直觉。

- **Agent 概念辨析**：理解 Agent vs Chatbot vs Workflow 的本质区别——Chatbot 只能"说"，Workflow 是固定流水线，Agent 是自己决定怎么做。核心定义公式：`Agent = LLM + Tool Use + 循环决策`
- **为什么现在谈 Agent**：GPT-3.5/ChatGPT 让大众体验到了 LLM 的能力，但光"说"不够，需要"做"。Agent 是 LLM 能力从"对话"到"行动"的自然延伸
- **体验主流产品**：亲手使用 Claude Code、Cursor、Devin/OpenHands、GPT-Researcher 等产品，带着问题去用——"它什么时候自己做决定？什么时候问我？什么时候做错了？"
- **产品拆解模板**：用 9 维度观察框架（用户输入 / 规划时机 / 工具调用 / 用户确认 / 失败恢复 / 类型判断 / 惊喜与失望 / 改进建议）分析至少 3 款产品

**动手里程碑**：用产品拆解模板完成 3 份分析报告，每份覆盖全部 9 个维度。

---

## 课程二：Agent 当前的演进

**定位**：不写代码，但深入理解四大范式的来龙去脉。为课程三的动手做理论准备。

- **Agent 概念的历史渊源**：从强化学习的 Agent（Bellman 1957 → DQN 2013 → AlphaGo 2016），到软件 Agent（BDI 模型），再到 Russell & Norvig 四种 Agent 类型。理解传统 Agent 的根本痛点：封闭规则空间，无法泛化
- **LLM 带来的范式革命**：GPT-3 涌现能力（2020）→ ReAct（2022.10）首次将推理和行动融合为循环 → Toolformer（2023.2）让模型自监督学会用工具。关键转折：从"LLM 作为聊天机器人"到"LLM 作为自主决策核心"
- **核心范式一：Tool Use / Function Calling**：ChatGPT Plugins（2023.3）→ OpenAI Function Calling（2023.6）→ JSON Schema 标准化 → MCP 协议。核心问题：如何让 LLM 知道"什么时候该用工具、用哪个、怎么填参数"？
- **核心范式二：Planning（规划）**：CoT（2022）→ Tree-of-Thoughts（2023）→ Plan-and-Solve（2023）。核心矛盾：规划能力和执行能力往往是此消彼长的
- **核心范式三：Reflection（反思）**：Self-Refine（2023）→ Reflexion（2023）。关键洞察：Reflection 不是模型架构的能力，而是系统设计的能力
- **核心范式四：Multi-Agent（多智能体协作）**：AutoGen（2023）→ CrewAI（2024）→ 动态 Agent 团队。四种架构：层级式 / 对话式 / 辩论式 / 发布-订阅式

- **代码阅读过渡：从理论到实践的桥梁**：阅读 smolagents 等轻量框架源码，带着 5 个问题去读——ReAct 循环在哪？Tool Use 怎么实现的？Planning 如何触发？Reflection 长什么样？停止条件是什么？推荐入口：`src/smolagents/agents.py` → `run()` 和 `_step()`

**动手里程碑**：能用"之前有什么问题 → 提出者怎么想的 → 带来了什么变化"的框架讲清楚每个范式；能判断一篇 Agent 论文或产品公告属于哪个范式；能阅读开源 Agent 框架源码并画出核心执行流程。

---

## 课程三：Agent 底层核心

**定位**：开始动手写代码。理解并实现支撑 Agent 的五大核心技术支柱。

| 支柱 | 核心内容 | 实践目标 |
|------|---------|---------|
| **LLM 原理** | Transformer（Self-Attention / Multi-Head Attention）、Tokenization（BPE、对工具调用的影响）、Context Window（Lost in the Middle、注意力 O(n²)）、采样策略（Temperature / Top-p / Top-k）、多模态 LLM 对 Agent 的影响（视觉输入改变工具返回形态、Computer Use 范式） | 理解模型为什么会"不听话" |
| **Tool Use** | JSON Schema 定义工具、工具描述的黄金法则、工具选择核心问题（时机 / 选择 / 参数） | 实现一个能调用 API/数据库的 Agent |
| **RAG** | Embedding 与向量检索、Chunking 策略、混合检索 + Rerank、数据管线（多源接入 / 数据清洗与标准化 / 新鲜度管理 / 知识图谱互补） | 给 Agent 接入知识库，理解 RAG 不只是"检索+生成" |
| **Memory** | 短期记忆（滑动窗口 / 摘要压缩 / 重要性过滤）、长期记忆（跨会话持久化）、三层上下文架构（热数据 / 温数据 / 冷数据） | 让 Agent 不再"转瞬即忘" |
| **Prompt Engineering** | System Prompt 设计、Few-shot Prompting、Chain-of-Thought、结构化输出 | 写出稳定可控的提示词 |

**ReAct：五大支柱的联合运用**：实现 ReAct 循环（Thought → Action → Observation），停止条件设计，循环检测与防护。

**动手里程碑**：从零写一个 ReAct Agent（Python/TypeScript），支持 3+ 个工具，具备跨会话记忆。10 条测试任务成功 >= 7 条，能按 tool selection / prompt / schema / 上下文管理 / memory 分类失败原因。

---

## 课程四：Agent 架构深入

**定位**：让 Agent 从能用到好用。系统解决死循环、遗忘、越界、无法调试等问题。

| 主题 | 关键概念 | 推荐框架/工具 |
|------|---------|------------|
| **Harness（运行时引擎）** | 三层架构：驱动层 / 控制层 / 管理层；Harness vs Orchestration 的区别 | 主流框架的 Harness 设计对比 |
| **Skill 与 Plugin** | Tool → Skill → Plugin 三层抽象关系；Skill 核心设计要素（声明式描述、触发条件、工具集、上下文注入、知识库、输出 Schema）；动态加载与路由；与 MCP 的关系 | Claude Code Skills、ChatGPT GPTs、MCP |
| **Orchestration** | 四种模式：Chain / Router / Plan-Execute / ReAct Loop / Graph | LangGraph、CrewAI、AutoGen |
| **Memory 架构深入** | 向量数据库选型、MemGPT 虚拟内存思想、记忆衰减与更新策略、多 Agent 共享记忆 | Mem0、Letta |
| **Evaluation** | 端到端评测 vs 步骤级评测、LLM-as-Judge、评测集构建方法论 | Braintrust、LangSmith、Ragas |
| **Guardrails** | 输入护栏（Prompt Injection 防御）、输出护栏（工具参数校验、事实性校验）、Human-in-the-Loop 五级审批策略 | Guardrails-AI、自定义中间件 |
| **Observability** | Tracing 架构、关键指标（延迟分解、Token 消耗、错误分类）、调试与决策归因 | Langfuse、LangSmith、Phoenix |
| **Agent 测试金字塔** | 四层测试体系：Unit（工具解析、Schema 验证）→ Component（单步推理、Memory 读写）→ Integration（多步链路、工具调用链）→ E2E（完整任务 + LLM-as-Judge），与评测的互补关系 | pytest、自定义测试工具 |
| **MCP 协议入门** | Model Context Protocol 三大能力（Tools / Resources / Prompts）、JSON-RPC 传输层（stdio / SSE / Streamable HTTP）、对 Harness 管理层架构的影响。课程七有完整深入版本 | MCP Python/TypeScript SDK |

**动手里程碑**：将课程三的"裸循环"重构为三层 Harness 架构；构建多步骤 Agent（规划→执行→反思→修正），配有记忆和可观测性；Guardrails 至少拦截 1 次真实的越界行为；至少编写单元测试和集成测试各 3 个。

---

## 课程五：Agent 走向生产环境

**定位**：让 Agent 从好用到能上线。解决"用户觉得它慢、贵、不安全、不靠谱"的问题。

- **交互设计**：流式输出设计（SSE 原理）、中断与恢复（Checkpoint 机制）、渐进式信息披露、用户确认节点设计
- **可靠性工程**：重试策略（指数退避 + 智能重试）、降级机制（工具降级 / 模型降级 / 功能降级）、超时处理（分层超时）、Rate Limit 管理
- **成本控制**：模型选择策略（路由器模式 / 级联策略，小模型做分类、大模型做推理）、Prompt Caching 原理与实践、上下文窗口经济性
- **产品评价体系**：六大核心指标——任务完成率、平均步数、用户干预率、Token 效率、用户满意度、留存率。Agent A/B 测试的特殊挑战
- **安全合规**：Prompt Injection 防御体系、数据脱敏与审计日志、GDPR / SOC2 合规要点
- **失败模式清单**：工具调用类（选择错误 / 参数错误 / 死循环）、上下文管理类（遗漏约束 / RAG 误导）、决策逻辑类（过早执行 / 权限不明）
- **部署与基础设施**：容器化部署（Dockerfile 最佳实践、健康检查、优雅关闭）、多环境管理（dev / staging / prod 配置策略）、CI/CD 流水线（含 Prompt 版本管理）、服务编排与弹性伸缩（sticky session、任务队列）、监控告警（四层监控指标、Agent 专属告警规则）
- **Agent 经济学与伦理责任**：自建 vs API 成本对比、定价模式选择（按次 / 订阅 / Freemium / 混合）、ROI 评估框架；伦理四维度——透明度义务（用户有权知道在跟 Agent 交互）、偏见与公平性（训练数据与工具设计偏见缓解）、可问责性（Agent 决策的追溯与审计）、环境影响（大模型推理的碳足迹意识）

**动手里程碑**：流式输出延迟感知 <= 500ms；常见故障可自动恢复；单任务平均 Token 消耗降低 >= 20%；失败模式清单覆盖 >= 5 种类型；完成 Docker 化部署并能通过健康检查；撰写一份 Agent 产品的经济学评估与伦理合规清单。

---

## 课程六：Agent 项目实战

**定位**：整合所有知识。用一个完整的端到端项目，将前五门课程的知识串联输出。

三个递进项目：

| 项目 | 难度 | 合格版 | 进阶版 | 产品版 |
|------|------|--------|--------|--------|
| **个人知识助手** | 入门 | 检索+回答，2 工具，正确率>=60% | 混合检索+Rerank，多轮记忆，流式输出 | Web 界面，多用户，正确率>=90% |
| **代码审查 Agent** | 中级 | 读取 diff → 输出 review | 调用测试/静态分析，置信度标注 | GitHub App 自动触发，行内评论，误报反馈 |
| **领域 Agent 产品** | 高级 | 核心功能可用，5 场景 | 20+ 场景，有评测报告 | 有真实用户反馈，监控告警，持续迭代 |

每个项目都附带设计文档模板、复盘模板和评测框架。

**动手里程碑**：项目代码完整可运行（GitHub 仓库）；有设计文档（架构 + 技术选型理由）；有复盘报告（问题 + 解决方案 + 重做改进）；有评测报告（用课程四学的评测框架）。

---

## 课程七：Agent 最新发展趋势

**定位**：保持敏锐。了解正在发生什么，但主线精力不在此。定期浏览即可。

> ⚠️ **重要定位**：本课程是"跟进生态"，不是"主线必修"。建议在完成课程三到课程五之前，不要在这里投入过多时间。

| 方向 | 关注内容 | 与主线关联 |
|------|---------|----------|
| **MCP / A2A** | MCP 协议深入（Streamable HTTP、Session 管理、安全模型）、A2A 协议（Agent 间发现与协作）。基础内容已在课程四的"补充专题"中覆盖 | ⭐⭐⭐⭐⭐ 必修（基础在课程四，深入在课程七） |
| **Fine-tuning for Agent** | Prompt Engineering 的天花板在哪？三个方向——Function Calling 微调（提升工具选择准确率）、领域知识微调（LoRA 注入专业知识）、Agent 轨迹微调（模仿优秀决策路径）。决策框架：何时微调 vs 优化 Prompt | ⭐⭐⭐⭐ 工具调用准确率遇瓶颈时深入 |
| **Skill / Plugin 生态** | 能力封装与复用——将工具+提示词+知识打包为可组合、可分发的产品单元；Claude Code Skills、ChatGPT GPTs、MCP Marketplace 等生态对比；与 MCP/A2A 的协同关系。深入内容在课程四的 Skill 专题 | ⭐⭐⭐⭐ 构建可复用 Agent 能力时深入 |
| **Computer Use** | GUI Agent（截屏分析 + 元素定位 + 操作执行）、浏览器自动化（Playwright + LLM） | ⭐⭐⭐ 了解 + Demo |
| **Multi-Agent** | 四种架构模式深入、框架对比（AutoGen vs CrewAI vs LangGraph） | ⭐⭐⭐⭐ 单Agent准确率遇瓶颈时深入 |
| **Code Agent** | 里程碑：Copilot(2021) → SWE-bench(2023) → Devin(2024) → Claude Code(2025) | ⭐⭐⭐⭐⭐ 日常使用就是学习 |
| **RL for Agent** | RLHF → GRPO → DeepSeek-R1；Agent RL 的特殊挑战（奖励稀疏、探索空间大、环境非平稳） | ⭐⭐ 了解概念 |

---

## 课程依赖关系

```
课程一（初识Agent）
    │
    v
课程二（Agent演进）
    │
    v
课程三（底层核心·五大支柱）←──────── 动手起点
    │
    v
课程四（架构深入）         课程七（发展趋势）← 可并行，低优先级
    │  └─ MCP 基础 ────────→ （课程四含 MCP 入门专题，课程七为完整深入版）
    v
课程五（走向生产环境）
    │
    v
课程六（项目实战）
```

- 课程一 → 课程二 → 课程三：顺序依赖，不可跳
- 课程三 → 课程四 → 课程五：顺序依赖，不可跳
- 课程七：可在课程三之后随时开始，与课程四/五/六并行。MCP 基础建议先看课程四的"补充专题"，再进入课程七的深入内容
- 课程六：依赖课程一至课程五的学习，但可将项目拆分为阶段性交付

---

## 推荐学习资源

- **必读论文**：ReAct、Toolformer、AutoGPT 论文、Voyager（Minecraft Agent）、SWE-Agent、Self-Refine、Reflexion
- **博客**：Anthropic Research Blog、Lilian Weng（OpenAI）的 Agent 系列、LangChain Blog、MCP 官方博客（modelcontextprotocol.io）
- **课程**：DeepLearning.AI 的 Functions/Tools/Agents 系列、Berkeley LLM Agents MOOC
- **代码阅读**：[smolagents](https://github.com/huggingface/smolagents)（HuggingFace 轻量 Agent 框架，适合入门阅读）、[Mem0](https://github.com/mem0ai/mem0)（Memory 层参考实现）
- **协议标准**：[MCP 规范](https://modelcontextprotocol.io/)（工具标准化）、[A2A 协议](https://github.com/google/A2A)（Agent 间通信）
- **社区**：LangChain Discord、Anthropic Developer Discord、r/LocalLLaMA、HuggingFace 社区

---

> 这条路线的核心思想是：**先理解原理，再动手实践，最后回归产品**。不要一开始就陷入框架细节——手写一个 ReAct Agent 理解本质，比直接调 LangChain 有价值得多。相比早期版本，当前版本补充了多模态 LLM、数据管线、Skill/Plugin 能力封装、Agent 测试金字塔、MCP 协议入门、部署与基础设施、经济学与伦理责任、Fine-tuning 等关键主题，覆盖 Agent 从理论到上线的完整链路。
