# 02 Tool Mechanism

这是课程四「工具机制」的可运行示例项目。它基于课程三的最小 Agent 闭环扩展，重点展示工具调用如何从“调用一个函数”升级为一条可控、可验证、可审计的运行时链路。

同一个示例包含两个实现版本：

- `python/`：Python 标准库实现。
- `nodejs/`：Node.js 标准库实现。

两个版本都包含：

- 工具定义：description、参数 Schema、风险等级、幂等性。
- 参数校验：必填参数、类型、未知字段。
- Deny-first 权限策略：未显式允许的工具默认拒绝。
- 工具执行器：统一处理权限、执行、重试和结构化错误。
- Observation 处理：长内容截断，保留 `full_content_ref`。
- 审计日志：记录校验、权限和执行结果。
- Agent Runtime：在课程三 loop 基础上接入工具执行机制。

## Python

```bash
cd examples/course-04-tool-mechanism/python
python3 main.py
python3 -m unittest discover -s tests
```

## Node.js

```bash
cd examples/course-04-tool-mechanism/nodejs
npm start
npm test
```

默认运行使用离线 `ScriptedLLM`，不需要网络和 API Key。真实 LLM 模式请分别参考子目录 README。

## 与课程三示例的区别

课程三示例的目标是跑通最小 Agent 闭环：模型给出结构化决策，Runtime 执行本地工具，把 Observation 写回 State，然后继续或停止。课程四示例不改变这个主循环，而是把其中的“工具/环境交互”展开成完整工具机制。

| 维度 | 课程三 `course-03-minimal-agent` | 课程四 `course-04-tool-mechanism` |
|---|---|---|
| 工具暴露方式 | 直接把函数名和 docstring 放进上下文 | 通过 `ToolDefinition` 暴露 description、参数 Schema、风险等级和幂等性 |
| 工具集合 | 普通 dict / object：`read_file`、`write_file`、`search_text` | `ToolRegistry` 统一注册工具，并生成给模型看的安全工具视图 |
| 参数处理 | 主要依赖 Python/JS 函数调用时报错 | Runtime 在执行前检查必填参数、类型和未知字段 |
| 权限控制 | 主要靠路径限制等工具内部边界 | 增加 Deny-first `PermissionPolicy`，未授权工具默认拒绝 |
| 执行入口 | Agent loop 直接调用工具函数 | Agent loop 只调用 `execute_tool_call()` / `executeToolCall()` |
| 错误返回 | 有结构化错误，但字段较少 | 错误包含 `code`、`retryable`、`suggested_action` / `suggestedAction`、`needs_user` / `needsUser` |
| 重试策略 | 不区分幂等性重试 | 只允许幂等工具有限重试，避免写入/发送类副作用重复发生 |
| 长结果处理 | 工具结果基本原样进入 State 和上下文 | 长文本会变成 preview + `full_content_ref` / `fullContentRef` |
| 审计能力 | Trace 记录 Agent loop 步骤 | 增加 tool-level audit log，记录 lookup、validation、permission、execution 阶段 |
| 教学重点 | 理解 Agent 最小运行链路 | 理解工具调用如何变成可选择、可执行、可控、可复用、可审计的机制 |

可以把课程四示例理解为：保留课程三的 Agent loop 骨架，但把 `Tool Use` 这一步拆成一条更接近真实产品的执行链路。
