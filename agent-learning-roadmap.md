# Agent 开发与产品知识体系 & 路线图

一套从入门到精通的系统性学习路径，分为六个阶段。

---

## 阶段一：基础认知（1-2 周）

先建立对 Agent 的整体认知框架：

- **Agent 概念辨析**：理解 Workflow（固定流程）vs Agent（自主决策）的本质区别，推荐阅读 Anthropic 的 [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) 博文
- **核心范式了解**：Tool Use / Function Calling → Planning → Reflection → Multi-Agent，搞清楚每种范式解决什么问题
- **体验主流产品**：亲手使用 Claude Code、Cursor、Devin、Manus、OpenAI Deep Research 等产品，带着问题去用——"它为什么在这个时机做这个决策？"

---

## 阶段二：技术基础（3-6 周）

动手前需要的关键能力：

| 领域 | 核心内容 | 实践目标 |
|------|---------|---------|
| **LLM 原理** | Transformer、Tokenization、Prompting、Context Window、Temperature/Sampling | 理解模型为什么会"不听话" |
| **Tool Use** | JSON Schema 定义 tool、系统提示词结构、ReAct 模式 | 实现一个能调用 API/数据库的 Agent |
| **RAG** | Embedding、向量检索、Rerank、Chunking 策略 | 给 Agent 接入知识库 |
| **Prompt Engineering** | Few-shot、Chain-of-Thought、结构化输出、System Prompt 设计 | 写出稳定可控的提示词 |

**动手里程碑**：用 Python/TypeScript 从零写一个 ReAct Agent，能调用 2-3 个工具完成简单任务。

---

## 阶段三：Agent 架构深入（4-8 周）

| 主题 | 关键概念 | 推荐框架/工具 |
|------|---------|------------|
| **Orchestration** | Plan-then-Execute、Loop-based、DAG/Graph-based 调度 | LangGraph、CrewAI、AutoGen |
| **Memory** | 短期记忆（上下文窗口管理）、长期记忆（向量库 + 摘要压缩）、工作记忆 | Mem0、LangChain Memory |
| **Evaluation** | 端到端评测、步骤级评测、LLM-as-Judge、轨迹比对 | Braintrust、LangSmith、Ragas |
| **Guardrails** | 输入/输出校验、权限管控、Human-in-the-Loop | Guardrails-AI、自定义中间件 |
| **Observability** | Tracing、Token 用量、延迟分解、错误分类 | Langfuse、LangSmith、Phoenix |

**动手里程碑**：构建一个多步骤 Agent（规划→执行→反思→修正），配有记忆和可观测性。

---

## 阶段四：产品化能力（4-6 周）

这是从"能做出来"到"能上线"的关键阶段：

- **交互设计**：流式输出设计、中断与恢复、用户确认节点、渐进式信息披露
- **可靠性工程**：重试策略、降级机制、超时处理、Rate Limit 管理
- **成本控制**：模型选择策略（小模型做分类，大模型做推理）、Prompt Caching、输出长度控制
- **评价体系**：定义 Agent 产品的核心指标——任务完成率、平均步数、用户干预率、Token 效率
- **安全合规**：Prompt Injection 防御、数据脱敏、审计日志

---

## 阶段五：前沿与生态（持续跟进）

| 方向 | 关注内容 |
|------|---------|
| **MCP / A2A** | Model Context Protocol（工具标准化）、Agent-to-Agent 协议 |
| **Computer Use** | GUI Agent、浏览器自动化、桌面操作 |
| **Multi-Agent** | 角色分工、消息传递、协作与竞争机制 |
| **Code Agent** | SWE-bench 赛道、代码修复/生成的 Agent |
| **RL for Agent** | 基于反馈的强化学习微调（RLHF / GRPO） |

---

## 阶段六：构建作品集

最好的学习方式是做完整项目，推荐难度递增的三个项目：

1. **个人知识助手**：RAG + 搜索工具 + 笔记整理 Agent
2. **代码审查 Agent**：接入 GitHub API，自动 Review PR 并给出建议
3. **领域 Agent 产品**：结合你的领域知识（如数据分析、客服、法律等），做一个端到端可用的 Agent

---

## 推荐学习资源

- **必读论文**：ReAct、Toolformer、AutoGPT 论文、Voyager（Minecraft Agent）、SWE-Agent
- **博客**：Anthropic Research Blog、Lilian Weng（OpenAI）的 Agent 系列、LangChain Blog
- **课程**：DeepLearning.AI 的 Functions/Tools/Agents 系列、Berkeley LLM Agents MOOC
- **社区**：LangChain Discord、Anthropic Developer Discord、r/LocalLLaMA

---

> 这条路线的核心思想是：**先理解原理，再动手实践，最后回归产品**。不要一开始就陷入框架细节——手写一个 ReAct Agent 理解本质，比直接调 LangChain 有价值得多。
