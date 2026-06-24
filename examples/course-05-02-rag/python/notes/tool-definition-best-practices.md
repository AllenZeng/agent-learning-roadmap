---
created: 2026-03-10
updated: 2026-04-25
tags: [agent, tool-use, schema-design, best-practice]
status: draft
---

# 工具定义最佳实践

> ⚠️ 这篇笔记还在完善中，部分内容可能不完整。

## 工具定义是模型的唯一入口

模型不知道你的函数内部怎么实现，不知道数据库里有什么，不知道 API 有什么限制。它只知道你告诉它的东西。工具定义的质量直接决定了工具调用的上限。

## 好描述的要素

工具描述要回答六个问题：
1. 这个工具能做什么？
2. 这个工具**不能**做什么？
3. 什么时候应该用它？什么时候不应该？
4. 需要哪些参数？每个的含义和约束？
5. 成功时返回什么？
6. 失败时返回什么？包含哪些帮助决策的信息？

## 名称的重要性

名称是模型对工具的第一印象。不要叫 `do_task`、`helper`、`process`——这些名字什么都没说。`search_web`、`read_file`、`send_email` 让模型一眼就知道用途。

## 参数 Schema

参数要有类型、约束和示例。不要留给模型"猜"的空间：

```python
"parameters": {
    "type": "object",
    "properties": {
        "path": {
            "type": "string",
            "description": "文件相对于 workspace 的路径，例如 'notes.md'"
        }
    },
    "required": ["path"]
}
```

## 边界清晰

如果有两个工具 `search_web` 和 `search_database`，它们的描述必须清楚区分各自的使用场景。边界重叠 → 模型随机选 → 诊断困难。

修复方案：在描述中同时说明"什么时候用"和"什么时候不要用"。

## 结构化返回

成功和失败都要统一格式。失败时至少包含：错误码、是否可重试、建议的下一步。

详见 [[agent-tool-use-design]] 了解工具设计的完整讨论。
