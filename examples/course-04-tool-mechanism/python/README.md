# 02 Tool Mechanism Python

这是课程四「工具机制」的 Python 可运行示例。它基于课程三的最小 Agent loop，重点补齐工具调用链路中的工程机制。

目录结构：

- `tool_agent/prompt.py`：工具机制示例的 Prompt 行为定义。
- `tool_agent/llm.py`：LLM 调用边界，包含 `ScriptedLLM` 和 DeepSeek Chat Completions 适配。
- `tool_agent/tools.py`：工具定义、参数 Schema、权限策略、审计日志、重试和 Observation 处理。
- `tool_agent/agent.py`：Runtime 主循环，接入 `execute_tool_call()`。
- `main.py`：命令行入口。
- `tests/test_tool_mechanism.py`：工具机制测试。

## 运行离线示例

```bash
cd examples/course-04-tool-mechanism/python
python3 main.py
```

默认使用 `ScriptedLLM`，不需要网络和 API Key。运行后会写入：

```text
examples/course-04-tool-mechanism/python/output/summary.md
```

## 使用真实 LLM

```bash
cd examples/course-04-tool-mechanism/python
export DEEPSEEK_API_KEY="..."
export DEEPSEEK_MODEL="deepseek-v4"
python3 main.py --real-llm --goal "读取 data/notes.md，总结后写入 output/summary.md"
```

真实 LLM 模式会调用 DeepSeek Chat Completions API。模型必须按 `prompt.py` 要求返回 JSON 决策。

## 运行测试

```bash
cd examples/course-04-tool-mechanism/python
python3 -m unittest discover -s tests
```

测试覆盖：

- 工具上下文暴露 description、参数 Schema、风险等级和幂等性。
- 执行前参数校验。
- Deny-first 权限拒绝和审计日志。
- 长工具结果截断为模型可消费的 Observation。
- 幂等工具的有限重试。
- Agent loop 接入工具执行器和审计日志。

## 与课程三 Python 示例的代码差异

课程三的 Python 示例位于 `examples/course-03-minimal-agent/python`。课程四版本沿用相同的最小 Agent loop 思路，但把工具层拆细：

| 文件 | 课程三做法 | 课程四变化 |
|---|---|---|
| `minimal_agent/tools.py` → `tool_agent/tools.py` | `build_tools()` 返回普通函数字典 | 新增 `ToolDefinition`、`ToolRegistry`、`PermissionPolicy`、`ToolResult` 和 `execute_tool_call()` |
| `agent.py` | `_execute_tool()` 直接按工具名调用函数 | `run_agent()` 接收 `registry` 和 `permissions`，工具调用统一交给 `execute_tool_call()` |
| `assemble_context()` | 只暴露工具名和 docstring | 暴露工具 description、参数 Schema、风险等级和幂等性 |
| `AgentState` | 记录 history、tool_results、errors | 新增 `audit_log`，记录工具调用在校验、权限、执行阶段的结果 |
| `main.py` | 只构造 `build_tools(root)` | 构造 `build_tool_registry(root)` 和 `PermissionPolicy(allowed_tools=...)` |

`tool_agent/tools.py` 是本示例的核心。建议按以下顺序阅读：

1. `ToolResult`：统一成功/失败 Observation 结构。
2. `ToolDefinition`：描述模型能看到什么、Runtime 执行什么。
3. `ToolRegistry`：集中管理工具定义，并生成上下文工具列表。
4. `PermissionPolicy`：展示 Deny-first 授权模型。
5. `execute_tool_call()`：串起工具名检查、参数校验、权限检查、执行、重试、Observation 处理和审计。
6. `build_tool_registry()`：定义 `read_file`、`write_file`、`list_files` 三个示例工具。

关键教学点：课程四没有让模型“更聪明”，而是让 Runtime 在模型和工具之间增加确定性的安全边界。
