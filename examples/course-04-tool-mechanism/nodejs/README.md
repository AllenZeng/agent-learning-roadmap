# 02 Tool Mechanism Node.js

这是课程四「工具机制」的 Node.js 可运行示例。它基于课程三的最小 Agent loop，重点补齐工具调用链路中的工程机制。

目录结构：

- `src/prompt.js`：工具机制示例的 Prompt 行为定义。
- `src/llm.js`：LLM 调用边界，包含 `ScriptedLLM` 和 DeepSeek Chat Completions 适配。
- `src/tools.js`：工具定义、参数 Schema、权限策略、审计日志、重试和 Observation 处理。
- `src/agent.js`：Runtime 主循环，接入 `executeToolCall()`。
- `main.js`：命令行入口。
- `test/tool-mechanism.test.js`：基于 `node:test` 的工具机制测试。

## 运行离线示例

```bash
cd examples/course-04-tool-mechanism/nodejs
npm start
```

默认使用 `ScriptedLLM`，不需要网络和 API Key。运行后会写入：

```text
examples/course-04-tool-mechanism/nodejs/output/summary.md
```

## 使用真实 LLM

```bash
cd examples/course-04-tool-mechanism/nodejs
export DEEPSEEK_API_KEY="..."
export DEEPSEEK_MODEL="deepseek-v4"
node main.js --real-llm --goal "读取 data/notes.md，总结后写入 output/summary.md"
```

真实 LLM 模式会调用 DeepSeek Chat Completions API。模型必须按 `src/prompt.js` 要求返回 JSON 决策。

## 运行测试

```bash
cd examples/course-04-tool-mechanism/nodejs
npm test
```

测试覆盖：

- 工具上下文暴露 description、参数 Schema、风险等级和幂等性。
- 执行前参数校验。
- Deny-first 权限拒绝和审计日志。
- 长工具结果截断为模型可消费的 Observation。
- 幂等工具的有限重试。
- Agent loop 接入工具执行器和审计日志。

## 与课程三 Node.js 示例的代码差异

课程三的 Node.js 示例位于 `examples/course-03-minimal-agent/nodejs`。课程四版本沿用相同的最小 Agent loop 思路，但把工具层拆细：

| 文件 | 课程三做法 | 课程四变化 |
|---|---|---|
| `src/tools.js` | `buildTools()` 返回普通函数对象 | 新增 `ToolDefinition`、`ToolRegistry`、`PermissionPolicy`、`ToolResult` 和 `executeToolCall()` |
| `src/agent.js` | `executeTool()` 直接按工具名调用函数 | `runAgent()` 接收 `registry` 和 `permissions`，工具调用统一交给 `executeToolCall()` |
| `assembleContext()` | 只暴露工具名和 description | 暴露工具 description、参数 Schema、风险等级和幂等性 |
| `AgentState` | 记录 history、toolResults、errors | 新增 `auditLog`，记录工具调用在校验、权限、执行阶段的结果 |
| `main.js` | 只构造 `buildTools(root)` | 构造 `buildToolRegistry(root)` 和 `new PermissionPolicy({ allowedTools: [...] })` |

`src/tools.js` 是本示例的核心。建议按以下顺序阅读：

1. `ToolResult`：统一成功/失败 Observation 结构。
2. `ToolDefinition`：描述模型能看到什么、Runtime 执行什么。
3. `ToolRegistry`：集中管理工具定义，并生成上下文工具列表。
4. `PermissionPolicy`：展示 Deny-first 授权模型。
5. `executeToolCall()`：串起工具存在性检查、参数校验、权限检查、执行、重试、Observation 处理和审计。
6. `buildToolRegistry()`：定义 `read_file`、`write_file`、`list_files` 三个示例工具。

关键教学点：课程四没有让模型“更聪明”，而是让 Runtime 在模型和工具之间增加确定性的安全边界。
