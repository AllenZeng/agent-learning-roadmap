# Agent Learning Roadmap — 从最小闭环到产品化系统

> **English Abstract**: A systematic, Chinese-language learning roadmap for AI Agent product development. Starting from "first encountering an Agent" to "designing, implementing, evaluating, and shipping an Agent product." Covers minimal agent loops, tool mechanisms, scenario enhancement (RAG/Memory/Planning/Reflection/Multi-Agent), runtime architecture (Harness), and production practices. ~24,000 lines across 8 courses, designed for 3–6 weeks of study. Core philosophy: *Agent = LLM-driven goal-oriented runtime + callable tools + manageable context + verifiable execution.*

[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC_BY--SA_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Status](https://img.shields.io/badge/status-active-success.svg)](https://github.com/zengjun/agent-learning-roadmap)
![Language](https://img.shields.io/badge/language-中文-red.svg)

---

## 这是什么？

这是一份面向希望**系统学习 Agent 产品开发**的路线图，目标是从"第一次接触 Agent"逐步走到"能够设计、实现、评估并上线 Agent 产品"。

核心观点：

```
Agent = LLM 驱动的目标导向运行时 + 可调用工具 + 可管理上下文 + 可验证执行过程
```

RAG、Memory、Planning、Reflection、Multi-Agent、MCP、Skill 都很重要，但它们不是同一层级的东西，也不是所有 Agent 应用的必选项。它们应该围绕**最小 Agent 闭环**展开。

## 学习路线

```text
建立直觉 → 理解范式演进 → 掌握最小 Agent 闭环
    → 深入工具机制 → 学习场景增强能力
    → 设计 Harness 运行时 → 完成产品化实践
    → 项目实战与生态跟进
```

| 课程 | 建议时间 | 学习重点 |
|---|---|---|
| [课程一：初识 Agent](docs/course-01-first-encounter.md) | 0.5-1 天 | 建立产品直觉和观察框架 |
| [课程二：Agent 范式演进](docs/course-02-evolution.md) | 1-2 天 | 理解 Agent 范式为什么出现 |
| [课程三：最小 Agent 闭环](docs/course-03-minimal-agent-loop.md) | 2-4 天 | 做出最小可运行 Agent |
| [课程四：工具机制](docs/course-04-tool-mechanism.md) | 2-4 天 | 把工具调用做成可控机制 |
| [课程五：场景增强能力](docs/course-05-00-scenario-enhancement.md) | 2-5 天 | 学会判断哪些增强能力值得引入 |
| [课程六：Harness 运行时架构](docs/course-06-runtime-architecture.md) | 4-7 天 | 将最小闭环工程化为 Harness |
| [课程七：Agent 产品化实践](docs/course-07-productization.md) | 2-4 天 | 做产品化、指标、安全和成本设计 |
| [课程八：项目实战与生态跟进](docs/course-08-project-practice.md) | 5-10 天 | 完成一个综合项目 |

**完整学习通常需要 3-6 周。** 时间差异主要来自实践深度：只读路线图会很快，真正做出可运行项目会显著增加投入。

## 设计原则

- **先感性，再结构化** — 先体验真实产品，再建立抽象概念
- **先最小闭环，再扩展能力** — 先实现多步决策的 Agent，再引入增强能力
- **Tool Use 作为独立主线** — 完整讲清工具定义、选择、执行、权限、MCP、Skill
- **RAG/Memory 放回场景中** — 它们不是必选项，而是按需选择的能力
- **从运行时理解架构** — Harness、Context Engineering、Evaluation 围绕 Agent 运行时展开
- **最终回到产品** — 目标是理解如何让 Agent 可靠、可控、低成本、安全

## 快速开始

### 先修要求

- 至少熟悉一门编程语言，能写 API 调用、文件读写和基础测试
- 了解 LLM 基本使用方式（Prompt、上下文窗口、结构化输出、模型 API）
- 理解 Web API、JSON、数据库或文件系统中的至少一种外部数据/工具形态
- 偏产品/业务角色可跳过实现细节，但需能读懂运行链路和产品化约束

### 从这里开始

1. 阅读 [课程总纲](docs/agent-learning-roadmap.md) 了解完整知识体系
2. 从 [课程一](docs/course-01-first-encounter.md) 开始，建立 Agent 的感性认知
3. 按顺序推进，每课包含核心概念 + 代码示例 + 实践练习

## 课程结构

```
docs/
├── agent-learning-roadmap.md          # 课程总纲
├── course-01-first-encounter.md       # 初识 Agent
├── course-02-evolution.md             # Agent 范式演进
├── course-03-minimal-agent-loop.md    # 最小 Agent 闭环
├── course-04-tool-mechanism.md        # 工具机制
├── course-05-00-scenario-enhancement.md  # 场景增强：总览
├── course-05-02-rag.md                # 场景增强：RAG
├── course-05-03-memory.md             # 场景增强：Memory
├── course-05-04-planning.md           # 场景增强：Planning
├── course-05-05-reflection.md         # 场景增强：Reflection
├── course-05-06-multi-agent.md        # 场景增强：Multi-Agent
├── course-05-07-composition.md        # 场景增强：组合案例
├── course-06-runtime-architecture.md  # Harness 运行时架构
├── course-07-productization.md        # Agent 产品化实践
└── course-08-project-practice.md      # 项目实战与生态跟进
```

## 贡献

欢迎贡献！方式包括：

- 🐛 **内容纠错**：错别字、链接修复、概念澄清 → 直接提 PR
- 💡 **内容补充**：新章节、深度扩展 → 先开 Issue 讨论
- 🌍 **翻译**：英文或其他语言翻译
- 🔧 **代码示例**：补充或优化各课程的代码示例

详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## License

本项目的课程文字内容采用 [CC BY-SA 4.0](LICENSE) 许可。代码示例采用 MIT 许可。

---

⭐ 如果这份路线图对你有帮助，请给个 Star 支持一下！
