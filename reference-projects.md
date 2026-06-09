# Agent 学习参考项目清单

与课程路线图配套的开源项目推荐，按学习课程对应。

---

## 课程一（初识Agent）→ 先体验

| 项目 | Stars | 为什么要看 |
|------|-------|----------|
| [AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) | ~170k | Agent 概念的"破圈者"，体验它来建立对"什么是 Agent"的直觉——它能自主分解任务并执行，是很好的感性认知入口 |

---

## 课程二（Agent演进）→ 看源码理解核心能力

| 项目 | Stars | 为什么要看 |
|------|-------|----------|
| [GPT-Researcher](https://github.com/assafelovic/gpt-researcher) | ~25k | 非常适合拆解学习的 Agent 产品——规划→搜索→综合→输出的流程很清晰，能直观看到 Tool Use、Planning、Reflection 三大范式如何协作 |

---

## 课程三（底层核心）→ 参考源码学实现

| 项目 | Stars | 对应课程 | 推荐理由 |
|------|-------|---------|---------|
| [smolagents](https://github.com/huggingface/smolagents) | ~27k | Tool Use、ReAct | HuggingFace 出品，代码简洁（code-as-action 而非 JSON 调用），适合读源码理解 Agent 循环 |
| [LlamaIndex](https://github.com/run-llama/llama_index) | ~49k | RAG、Embedding | RAG 领域最成熟的框架，300+ 集成，学 RAG 首选参考实现 |
| [PydanticAI](https://github.com/pydantic/pydantic-ai) | ~14k | 结构化输出、Tool Use | 类型安全的 Agent 框架，代码质量极高，适合学习"怎么写好 Agent 代码" |

---

## 课程四（架构深入）→ 用框架，但要理解原理

| 项目 | Stars | 对应课程 | 推荐理由 |
|------|-------|---------|---------|
| [LangGraph](https://github.com/langchain-ai/langgraph) | ~33k | Orchestration | **当前生产环境事实标准**，状态图 + 条件边 + Checkpointing，Klarna/Cisco 等大厂在用 |
| [CrewAI](https://github.com/crewAIInc/crewAI) | ~52k | Multi-Agent | 角色分工式多 Agent 最直观的实现，2700万+ 下载 |
| [Letta](https://github.com/letta-ai/letta) (原 MemGPT) | ~15k | Memory | 记忆管理的标杆项目，虚拟内存管理思想引入 Agent |
| [Langfuse](https://github.com/langfuse/langfuse) | ~15k | Observability | 开源的 LLM Tracing 平台，可以自部署 |
| [AutoGen / AG2](https://github.com/ag2-ai/ag2) | ~58k | Multi-Agent | 微软出品，对话式多 Agent 协作；AG2 是社区维护的活跃分支 |
| [Mem0](https://github.com/mem0ai/mem0) | ~25k | Memory | 专为 Agent 设计的记忆层，支持记忆的写入、检索、更新 |

---

## 课程五（走向生产环境）→ 参考生产级实践

| 项目 | Stars | 推荐理由 |
|------|-------|---------|
| [OpenHands](https://github.com/All-Hands-AI/OpenHands) (原 OpenDevin) | ~67k | Code Agent 的完整产品化案例，沙箱执行、人机协作、安全边界设计都有参考价值 |
| [Dify](https://github.com/langgenius/dify) | ~143k | 可视化 Agent+RAG 平台，看它如何处理多租户、权限、审计日志等产品化问题 |
| [SuperAGI](https://github.com/TransformerOptimus/SuperAGI) | ~16k | 企业级 Agent 管理平台，多 Agent 监控、工具复用、生产部署的方案参考 |
| [OpenClaw](https://github.com/openclaw/openclaw) | ~347k | **GitHub 历史 Star 数最高的软件仓库**。四层架构（Gateway→Agent→Skills→Memory）是课程中 Harness 三层模型的生产级范本；SKILL.md 的"文档即工具定义"思路是对 JSON Schema 的互补；自托管、本地优先、多模型路由 |

---

## 课程七（最新发展趋势）

| 项目 | Stars | 方向 | 推荐理由 |
|------|-------|------|---------|
| [browser-use](https://github.com/browser-use/browser-use) | ~97k | Computer Use | 浏览器自动化 Agent 最火项目，MIT 协议 |
| [OpenCode](https://github.com/anthropics/opencode) | ~55k | Code Agent | 多模型终端编程 Agent |
| [Cline](https://github.com/cline/cline) | ~49k | Code Agent | VS Code 内自主编程 Agent |
| [MetaGPT](https://github.com/geekan/MetaGPT) | ~60k | Multi-Agent | 模拟完整软件公司（PM+架构师+工程师）的多 Agent 协作 |

---

## 建议的精读顺序

如果时间有限，优先看这五个：

1. **smolagents** — 代码量不大，花一个下午读完核心循环，你就会真正理解 ReAct Agent 是怎么工作的
2. **LangGraph** — 生产标准，文档质量高，边看边理解状态图编排
3. **Letta** — 记忆系统设计思路独一无二，能开阔视野
4. **OpenHands** — 看一个成熟 Code Agent 产品怎么处理安全、沙箱、人机协作
5. **OpenClaw** — 看分层架构如何落地为工程化的 Agent 平台，Gateway/Agent/Skills/Memory 四层解耦值得反复研究

---

## 选型速查表

| 你的需求 | 推荐项目 |
|----------|----------|
| 学习 Agent 循环原理 | smolagents |
| 搭建 RAG 系统 | LlamaIndex |
| 生产级 Agent 编排 | LangGraph |
| 多 Agent 角色协作 | CrewAI |
| Agent 记忆系统 | Letta / Mem0 |
| Agent 可观测性 | Langfuse |
| 可视化 Agent 平台 | Dify |
| 浏览器自动化 | browser-use |
| 代码 Agent（终端） | OpenCode / Claude Code |
| 代码 Agent（VS Code） | Cline |
| 企业级部署 | SuperAGI |
| 自托管个人 Agent 平台 | OpenClaw |

---

## Awesome List（保持更新的汇总仓库）

- [awesome-llm-agents](https://github.com/kaushikb11/awesome-llm-agents) — 最全面的 Agent 框架清单
- [awesome-ai-agents-2026](https://github.com/Zijian-Ni/awesome-ai-agents-2026) — 2026 年持续更新的 Agent 生态汇总
- [bestony/awesome-agents](https://github.com/bestony/awesome-agents) — 中文视角的 Agent 项目汇总

建议先浏览这些 Awesome List 建立全局地图，再按上述精读顺序深入具体项目。

---

> 注意：Star 数和项目状态会实时变化，以上数据为 2026 年 6 月快照。生产环境使用前请评估项目的活跃度、协议、社区支持情况。
