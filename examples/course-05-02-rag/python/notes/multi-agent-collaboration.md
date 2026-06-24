---
created: 2026-05-01
updated: 2026-05-28
tags: [agent, multi-agent, collaboration, architecture]
status: published
---

# 多 Agent 协作

## 什么时候需要多 Agent

单 Agent 在任务范围明确、步骤有限时足够。但当任务需要多领域知识、多工具组合、或者需要内部审查机制时，多 Agent 的优势就出来了。

## 常见协作模式

### Router 模式

一个主 Agent 分析用户意图，把任务分发给最合适的子 Agent。

```text
用户: "帮我审查代码并生成文档"
  → Router 判断: 代码审查 + 文档生成 → 两个专业 Agent 并行
```

### Reviewer 模式

一个 Agent 产出，另一个 Agent 审查。类似代码 review 的双人机制——生成者容易有盲区，审查者从不同角度检查。

适合高风险场景：代码部署、金融操作、合同生成。

### 辩论模式

两个 Agent 从不同立场论证同一个问题，最后综合得出结论。适合需要多角度分析的决策场景。

## 编排 vs 自治

多 Agent 系统有一个核心张力：是预设流程（编排），还是让 Agent 自己协商（自治）？

编排的好处是可预测、可审计，坏处是灵活性差。自治的好处是适应性强，坏处是可能出现预期外的行为。目前实践中，关键路径用编排保证可靠性，非关键部分允许自治提高效率。

## 与单 Agent 的关系

多 Agent 不是单 Agent 的替代，是单 Agent 的扩展。好的做法是先把单 Agent 跑稳，再拆分出多 Agent。参考 [[agent-architecture-overview]] 了解整体架构设计。

多 Agent 场景下，Memory 的共享策略变得更复杂——哪些记忆是 Agent 私有的，哪些是共享的？详见 [[agent-memory-mechanism]]。
