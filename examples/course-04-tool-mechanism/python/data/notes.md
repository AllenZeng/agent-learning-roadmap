# 课程四：工具机制笔记

工具调用不是一次简单的函数调用，而是一条运行时链路：

LLM Decision → Tool Selection → Parameter Generation → Permission Check → Tool Execution → Observation → State Update

## 核心机制

1. **工具定义**：工具需要清晰的 description、参数 Schema、风险等级和适用边界。
2. **参数校验**：Runtime 在执行前检查必填参数、类型和未知字段。
3. **权限检查**：采用 Deny-first 策略，未显式允许的工具默认拒绝。
4. **执行与重试**：只对幂等工具做有限重试，避免重复发送、重复写入等副作用。
5. **Observation 处理**：工具结果需要结构化，长内容要截断或转成资源引用。
6. **审计日志**：记录工具名、参数、校验结果、权限结果和执行结果，便于调试和追责。

## 工程原则

- 模型只提出工具调用意图，Runtime 才是真正的执行者。
- 工具错误要提供 code、retryable、suggested_action 和 needs_user。
- 高风险动作需要用户确认或明确授权。
