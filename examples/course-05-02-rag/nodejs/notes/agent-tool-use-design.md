---
created: 2026-03-15
updated: 2026-05-20
tags: [agent, tool-use, design-pattern]
status: published
---

# Agent Tool Use 设计

## 工具调用的本质

工具调用不是让模型"变强"，而是让模型把手伸到外部世界。Function Calling 标准化了这件事：模型不再输出"建议你去查一下数据库"，而是输出 `{"tool": "query_db", "arguments": {...}}`。

但这里有一个关键分工：**模型只负责生成调用意图，Runtime 负责执行**。这意味着从"我想调用"到"结果回到下一轮"之间，有一整条链路需要设计。

## Tool Use 与 Memory 的关系

工具调用是"向外看"，Memory 是"向内看"。工具负责执行动作，Memory 负责延续状态。两者的设计哲学根本不同：工具的关注点是"能不能完成动作"，Memory 的关注点是"该不该记住这件事"。

这个区别直接影响了各自的接口设计：工具需要明确的输入输出 schema 和失败模式；Memory 需要写入决策、召回过滤和遗忘机制。

详见 [[agent-memory-mechanism]]。

## 工具设计原则

### 单一职责的边界

一个工具做好一类清晰动作。不要一个工具既读文件又发邮件。如果 `search_web` 和 `search_database` 的描述太像，模型就会随机选——这不是模型的问题，是工具边界没画清楚。

### 失败模式的设计

每个工具调用都可能失败，失败时不能只返回 "Error: failed"。模型需要知道：
- 错误码（是什么类型的失败）
- 是否可重试（幂等操作可以，发邮件不行）
- 建议的下一步（换工具？改参数？请求用户介入？）

```python
# 好的错误返回
{
  "status": "error",
  "error": {
    "code": "file_not_found",
    "message": "文件 'notes.md' 不存在于 workspace 中",
    "retryable": false,
    "suggested_action": "使用 list_files 查看可用文件"
  }
}
```

## 工具粒度：原子 vs 组合

原子工具只做一件事（`read_file`、`write_file`），组合工具封装多步流程（`generate_report`）。先用原子工具跑通闭环，当某组工具组合在多个任务中反复出现时，再沉淀成 Skill。

参考 [[tool-definition-best-practices]] 了解工具 Schema 的详细设计规范。
