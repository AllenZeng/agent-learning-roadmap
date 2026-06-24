---
created: 2026-02-20
updated: 2026-06-15
tags: [agent, architecture, overview, fundamentals]
status: published
---

# Agent 架构总览

## Agent 的最小定义

Agent 不是一个模型，而是一个系统。最小闭环：

```
Agent = LLM 决策 + 工具/环境交互 + 状态管理 + 循环控制
```

这四个要素缺一不可。LLM 负责思考，工具负责执行，状态负责记忆，循环负责持续推进任务。

## 核心组件关系

```
┌──────────────────────────────────────┐
│              Agent Loop               │
│  ┌─────────┐  ┌─────────┐  ┌───────┐ │
│  │  LLM    │→ │  Tool   │→ │ State │ │
│  │ Decision│  │ Execute │  │Update │ │
│  └─────────┘  └─────────┘  └───────┘ │
│       ↑                         │     │
│       └─── Context Assembly ←───┘     │
└──────────────────────────────────────┘
```

## 工具机制

工具是 Agent 与外部世界的桥梁。工具调用的完整链路：LLM Decision → Tool Selection → Parameter Generation → Permission Check → Tool Execution → Observation → State Update。

每一步都可能失败，每一步都需要对应机制兜底。详见 [[agent-tool-use-design]] 和 [[tool-definition-best-practices]]。

## Memory 系统

Memory 让 Agent 有"持续感"。不是存所有东西，而是选择性地记住关键信息。详见 [[agent-memory-mechanism]]。

## 外部知识

Agent 的知识不只是模型参数里的东西。RAG 让 Agent 能查阅外部文档，用"开卷考试"的方式回答基于私有知识的问题。详见 [[rag-retrieval-practice]]。

## 人类参与

高风险动作需要 Human-in-the-loop。模型不理解后果——它看到的不是"这个操作会删掉三年数据"，而是"根据概率分布，下一个 token 可能是 DELETE"。详见 [[human-in-the-loop-design]]。
