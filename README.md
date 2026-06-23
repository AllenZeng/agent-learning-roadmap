# Agent Learning Roadmap — 从最小闭环到产品化系统

一套面向开发者的 AI Agent 系统化学习路线，关注从 Minimal Agent、Tool Use、RAG、Memory 到 Runtime Harness 与产品化实践的完整演进过程。

[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC_BY--SA_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Status](https://img.shields.io/badge/status-active-success.svg)](https://github.com/AllenZeng/agent-learning-roadmap)
![Language](https://img.shields.io/badge/language-中文-red.svg)

> 当前状态：v0.1 WIP。课程主体初稿已完成，代码示例和部分章节 Review 正在补充中。

---

## 这是什么？

这是一份面向希望**系统学习 Agent 产品开发**的路线图，目标是从"第一次接触 Agent"逐步走到"能够设计、实现、评估并上线 Agent 产品"。

核心观点：

```
Agent = Prompt（行为定义） + LLM 决策 + 工具/环境交互 + State（状态管理） + 循环控制
```

RAG、Memory、Planning、Reflection、Multi-Agent、MCP、Skill 都很重要，但不是所有 Agent 应用的必选项。它们应该围绕**最小 Agent 闭环**展开。

## 为什么做这个项目？

很多 Agent 学习资料会直接进入 RAG、Tool Use、LangGraph、MCP、Multi-Agent 等概念，但学习者容易遇到一个问题：

知道很多术语，却不知道它们分别解决什么问题；能跑通 Demo，却不知道如何设计一个可靠、可控、可评估、可上线的 Agent 系统。

这个项目尝试从一个更底层的问题出发：

> 一个 Agent 应用，如何从最小闭环逐步演进为可产品化系统？

因此，本项目不只关注「如何写一个 Agent Demo」，更关注：

- Agent 和 Chatbot / Workflow 的边界；
- 最小 Agent 闭环如何构成与运转；
- Tool Use、RAG、Memory、Planning、Reflection、Multi-Agent 的引入时机；
- Agent Runtime / Harness 如何支撑状态、工具、上下文、评估和恢复；
- 如何把 Agent 能力落到真实产品中。

## 适合谁？

本项目适合：

- 想系统学习 AI Agent 应用开发的开发者；
- 已经了解 LLM API，但不知道如何继续深入 Tool Use、RAG、Memory、LangGraph 的学习者；
- 想从 Demo 走向真实 Agent 产品设计的工程师；
- 希望理解 Agent 产品化、评估、安全、成本和运行时架构的产品/技术负责人。

本项目不适合：

- 只想快速复制一个现成 Agent 模板的人；
- 只关注模型训练、微调、底层算法的人；
- 暂时不打算做工程实践、只希望泛泛了解概念的读者。

## 学习路线

```text
建立直觉 → 理解范式演进 → 掌握最小 Agent 闭环 → 深入工具机制 → 学习场景增强能力
    → 设计 Harness 运行时 → 完成产品化实践 → 项目实战与生态跟进
```

| 课程 | 建议时间 | 学习重点 |
|---|---|---|
| [课程一：初识 Agent](docs/course-01-first-encounter.md) | 0.5-1 天 | 建立产品直觉和观察框架 |
| [课程二：Agent 范式演进](docs/course-02-evolution.md) | 1-2 天 | 理解 Agent 范式为什么出现 |
| [课程三：最小 Agent 闭环](docs/course-03-minimal-agent-loop.md) | 2-4 天 | 做出最小可运行 Agent |
| [课程四：工具机制](docs/course-04-tool-mechanism.md) | 2-4 天 | 把工具调用做成可控机制 |
| [课程五：场景增强能力](docs/course-05-01-scenario-enhancement.md) | 2-5 天 | 学会判断哪些增强能力值得引入 |
| [课程六：Harness 运行时架构](docs/course-06-runtime-architecture.md) | 4-7 天 | 将最小闭环工程化为 Harness |
| [课程七：Agent 产品化实践](docs/course-07-productization.md) | 2-4 天 | 做产品化、指标、安全和成本设计 |
| [课程八：项目实战与生态跟进](docs/course-08-project-practice.md) | 5-10 天 | 完成一个综合项目 |

**完整学习通常需要 3-6 周。** 时间差异主要来自实践深度：只读路线图会很快，真正做出可运行项目会显著增加投入。

## 推荐学习路径

### 路径一：快速建立 Agent 认知

适合产品、业务、刚接触 Agent 的读者：

课程一 → 课程二 → 课程五 → 课程七

### 路径二：工程实现路径

适合希望动手实现 Agent 的开发者：

课程三 → 课程四 → 课程五 → 课程六 → 课程八

### 路径三：求职 / 面试强化路径

适合准备 AI 应用开发、Agent 工程岗位的开发者：

课程二 → 课程三 → 课程四 → 课程五 → 课程六 → 课程七

## 设计原则

- **先感性，再结构化** — 先体验真实产品，再建立抽象概念
- **先最小闭环，再扩展能力** — 先实现多步决策的 Agent，再引入增强能力
- **Tool Use 作为独立主线** — 完整讲清工具定义、选择、执行、权限、MCP、Skill
- **RAG/Memory 放回场景中** — 它们不是必选项，而是按需选择的能力
- **从运行时理解架构** — Harness、Context Engineering、Evaluation 围绕 Agent 运行时展开
- **最终回到产品** — 目标是理解如何让 Agent 可靠、可控、低成本、安全

## 快速开始

### 从这里开始

1. 阅读 [课程总纲](roadmap.md) 了解完整知识体系
2. 从 [课程一](docs/course-01-first-encounter.md) 开始，建立 Agent 的感性认知
3. 按顺序推进，每课包含核心概念和实践练习；代码示例正在逐步补充。

## 课程结构

```
.
├── roadmap.md                          # 课程总纲
├── docs/
│   ├── course-01-first-encounter.md    # 初识 Agent
│   ├── course-02-evolution.md          # Agent 范式演进
│   ├── course-03-minimal-agent-loop.md # 最小 Agent 闭环
│   ├── course-04-tool-mechanism.md     # 工具机制
│   ├── course-05-01-scenario-enhancement.md  # 场景增强：总览
│   ├── course-05-02-rag.md             # 场景增强：RAG
│   ├── course-05-03-memory.md          # 场景增强：Memory
│   ├── course-05-04-planning.md        # 场景增强：Planning
│   ├── course-05-05-reflection.md      # 场景增强：Reflection
│   ├── course-05-06-multi-agent.md     # 场景增强：Multi-Agent
│   ├── course-05-07-composition.md     # 场景增强：组合案例
│   ├── course-06-runtime-architecture.md  # Harness 运行时架构
│   ├── course-07-productization.md     # Agent 产品化实践
│   └── course-08-project-practice.md   # 项目实战与生态跟进
```

## Examples

代码示例正在整理中，计划包括：

- `examples/01-minimal-agent`：最小 Agent 闭环；
- `examples/02-tool-calling-agent`：工具调用机制；
- `examples/03-rag-agent`：带检索增强的 Agent；
- `examples/04-langgraph-runtime`：基于 LangGraph 的运行时示例；
- `examples/05-multi-agent-reviewer`：多 Agent 评审模式。

## 当前状态

当前项目处于 v0.1 WIP 阶段。

已完成：

- 课程主线设计；
- 课程一至课程八的主体框架与初稿；
- Tool Use、RAG、Memory、Planning、Reflection、Multi-Agent、Harness、产品化等核心章节初稿。

进行中：

- 部分课程内容 review；
- 代码示例补充；
- Mermaid 架构图补充；
- Agent 实战项目整理。

后续计划：

- v0.2：补齐所有课程 Review；
- v0.3：补充 Minimal Agent / RAG Agent / LangGraph Agent 示例；
- v0.4：增加评估、观测、成本控制案例；
- v1.0：形成完整课程版本。

## 贡献

欢迎贡献！方式包括：

- 🐛 **内容纠错**：错别字、链接修复、概念澄清 → 直接提 PR
- 💡 **内容补充**：新章节、深度扩展 → 先开 Issue 讨论
- 🌍 **翻译**：英文或其他语言翻译
- 🔧 **代码示例**：补充或优化各课程的代码示例

详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## License

本项目采用双许可证：

- 文档、课程内容、图示与说明文字：采用 [CC BY-SA 4.0](LICENSE) 协议。
- 示例代码、Demo 工程与脚本：采用 [MIT](LICENSE-CODE) 协议，除非对应目录中另有说明。

这意味着你可以自由复制、传播、改编本文档内容，也可以用于商业用途，但需要保留署名，并且基于本文档改编后的内容也需要以相同协议共享。

---

如果这个项目对你有帮助，欢迎 Star、Issue 或 PR。
