# 课程三：最小 Agent 闭环 笔记

## 核心公式

Agent = Prompt（行为定义） + LLM 决策 + 工具/环境交互 + State（状态管理） + 循环控制

## 五个组成

1. **Prompt（行为定义）**：System Prompt 定义 Agent 的角色、行为协议和可用决策格式。
2. **LLM 决策**：模型根据当前上下文（目标、历史、工具结果）输出结构化的下一步决策。
3. **工具/环境交互**：Runtime 执行 LLM 请求的工具调用，获取外部反馈。
4. **State（状态管理）**：Runtime 维护任务状态、历史记录、工具结果和错误信息。
5. **循环控制**：Runtime 判断继续执行、停止（完成/失败/超限）还是请求用户输入。

## 运行链路

User Goal → Context Assembly → LLM Decision → Tool/Environment Interaction
    → Observation/Feedback → State Update → Continue or Stop

## 关键原则

- 模型负责理解目标和判断下一步；确定性基础设施负责执行、权限、安全、状态恢复。
- 最小闭环必须有任务状态和循环控制，但不一定需要长期 Memory 或 RAG。
- 停止条件由 Runtime 判断，不依赖模型自觉。
