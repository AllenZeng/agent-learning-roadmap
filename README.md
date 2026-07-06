# Agent Learning Roadmap — 从最小闭环到产品化系统

一套面向开发者的 AI Agent 系统化学习路线，关注从 Minimal Agent、Tool Use、RAG、Memory 到 Runtime Harness 与产品化实践的完整演进过程。

[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC_BY--SA_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Status](https://img.shields.io/badge/status-active-success.svg)](https://github.com/AllenZeng/agent-learning-roadmap)
![Language](https://img.shields.io/badge/language-中文-red.svg)

> 当前状态：v0.5。课程主体初稿已完成，课程 07 之前的章节 Review 已推进，代码示例覆盖最小 Agent、工具机制、RAG、Memory 与 Planning。

---

![Agent Learning Roadmap 课程内容总览](assets/course-roadmap.svg)

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
- 已经了解 LLM API，但不知道如何继续深入 Tool Use、RAG、Memory等的学习者；
- 想从 Demo 走向真实 Agent 产品设计的工程师；
- 希望理解 Agent 产品化、评估、安全、成本和运行时架构的产品/技术负责人。

本项目不适合：

- 只想快速复制一个现成 Agent 模板的人；
- 只关注模型训练、微调、底层算法的人；
- 暂时不打算做工程实践、只希望泛泛了解概念的读者。


## 快速开始

### 从这里开始

建议先阅读 [课程总纲](syllabus.md)，用 10-15 分钟建立对整套课程的全局认识：它会先说明 Agent 学习的知识体系如何分层，以及每门课程分别解决什么问题。读完总纲后，你可以根据自己的基础和目标，沿着推荐路线选择最需要补齐的部分。

如果你希望系统学习，可以从 [课程一](courses/course-01-first-encounter.md) 开始，按照课程顺序逐步推进：先建立产品直觉，再理解范式演进，最后进入最小闭环、工具机制、场景增强、运行时架构和产品化实践。

如果你已经有明确问题，也可以直接参考下方课程结构，有针对性地选择感兴趣的章节阅读。例如：想先动手做 Agent，可以从课程三开始；想补工具调用，可以看课程四；想理解 RAG、Memory、Planning 等能力的引入时机，可以从课程五开始。

## 课程结构

| 课程 | 建议时间 | 学习重点 |
|---|---|---|
| [课程一：初识 Agent](courses/course-01-first-encounter.md) | 0.5-1 天 | 建立产品直觉和观察框架 |
| [课程二：Agent 范式演进](courses/course-02-evolution.md) | 1-2 天 | 理解 Agent 范式为什么出现 |
| [课程三：最小 Agent 闭环](courses/course-03-minimal-agent-loop.md) | 2-4 天 | 做出最小可运行 Agent |
| [课程四：工具机制](courses/course-04-tool-mechanism.md) | 2-4 天 | 把工具调用做成可控机制 |
| [课程五：场景增强能力](courses/course-05-01-scenario-enhancement.md) | 2-5 天 | 学会判断哪些增强能力值得引入 |
| [课程六：Harness 运行时架构](courses/course-06-runtime-architecture.md) | 4-7 天 | 将最小闭环工程化为 Harness |
| [课程七：Agent 产品化实践](courses/course-07-productization.md) | 2-4 天 | 做产品化、指标、安全和成本设计 |
| [课程八：项目实战与生态跟进](courses/course-08-project-practice.md) | 5-10 天 | 完成一个综合项目 |

**完整学习通常需要 3-6 周。** 时间差异主要来自实践深度：只读路线图会很快，真正做出可运行项目会显著增加投入。

## Examples

代码示例包括：

- `examples/course-03-minimal-agent`：课程三最小 Agent 闭环；
- `examples/course-04-tool-mechanism`：课程四工具机制；
- `examples/course-05-02-rag`：课程五 05-02 RAG / 外部知识接入；
- `examples/course-05-03-memory`：课程五 05-03 Memory / 长期记忆机制；
- `examples/course-05-04-context-engineering`：课程五 05-04 Context Engineering / 上下文工程；
- `examples/course-05-05-planning`：课程五 05-05 Planning / 任务规划模式；
- `examples/course-05-06-reflection`：课程五 05-06 Reflection / 基于反馈的决策闭环；
- `examples/course-05-07-human-in-the-loop`：课程五 05-07 Human-in-the-loop / 人类介入机制；
- `examples/course-05-08-multi-agent`：课程五 05-08 Multi-Agent / 多智能体协作；

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
