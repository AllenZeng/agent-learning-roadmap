---
created: 2026-04-02
updated: 2026-06-10
tags: [agent, memory, architecture]
status: published
---

# Agent Memory 机制

## Memory 解决什么问题

没有 Memory 的 Agent 每次都从零开始。用户说"继续刚才的工作"，Agent 一脸茫然——它不记得上一轮做了什么。Memory 做的就是让 Agent 能在多轮交互中保持状态。

## 设计哲学

Memory 的设计核心不是"存什么"，而是"什么时候存、什么时候忘"。

人类记忆不是录像机，是高度选择性的压缩和重建。Agent Memory 也应该如此——不是把每一轮对话原样存下来，而是提取关键信息，在需要时召回。

## 写入决策与遗忘机制

写入 Memory 时需要回答三个问题：
1. **该不该记？** 用户随口说的和明确要求的，权重不同
2. **记什么粒度？** 完整对话 vs 关键结论 vs 用户偏好
3. **记多久？** 会话级、任务级还是长期记忆

遗忘同样重要。如果 Memory 只增不减，检索精度会随着数据膨胀持续下降。遗忘策略包括：
- **时间衰减**：超过 N 天未访问的记录降低权重
- **覆盖更新**：新信息覆盖矛盾的旧信息
- **显式删除**：用户主动要求忘记

```python
# Memory 写入决策的简化逻辑
def should_write(message, context):
    if message.contains_explicit_request:  # "记住..."
        return True, "long_term"
    if message.is_key_decision:            # 重要的设计决策
        return True, "task_level"
    if message.is_casual:                  # 闲聊
        return False, None
    return maybe, "session_level"
```

## 与 Tool Use 的关系

Tool Use 和 Memory 经常一起出现——工具调用结果需要记住，Memory 里存的信息会影响工具选择。但它们是两个独立的设计维度。详见 [[agent-tool-use-design]]。
