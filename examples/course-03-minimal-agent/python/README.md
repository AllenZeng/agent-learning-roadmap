# 01 Minimal Agent Python

这是课程三「最小 Agent 闭环」的可运行示例。它刻意不使用 Agent 框架，直接展示：

- `prompt.py`：Prompt 行为定义。
- `llm.py`：LLM 调用边界，包含可复现的 `ScriptedLLM` 和真实 DeepSeek Chat Completions API 适配。
- `tools.py`：本地工具 `read_file`、`write_file`、`search_text`。
- `agent.py`：Runtime 主循环、Context Assembly、Observation、State Update、停止条件和 Trace。
- `main.py`：命令行入口。

## 运行离线示例

```bash
cd examples/course-03-minimal-agent
cd python
python3 main.py
```

默认使用 `ScriptedLLM`，不需要网络和 API Key。运行后会写入：

```text
examples/course-03-minimal-agent/python/output/summary.md
```

## 使用真实 LLM

```bash
cd examples/course-03-minimal-agent/python
export DEEPSEEK_API_KEY="..."
export DEEPSEEK_MODEL="deepseek-v4-flash"
python3 main.py --real-llm --goal "读取 data/notes.md，总结后写入 output/summary.md"
```

真实 LLM 模式会调用 DeepSeek Chat Completions API。模型必须按 `prompt.py` 要求返回 JSON 决策。可用模型名请以 DeepSeek 官方模型列表为准；示例默认使用 `deepseek-v4-flash`。

## 运行测试

```bash
cd examples/course-03-minimal-agent/python
python3 -m unittest discover -s tests
```

测试覆盖：

- 多步读取、写入、最终回答。
- 工具错误写入 `AgentState.errors`。
- 连续重复相同工具调用时由 Runtime 停止。
- `AgentState.recent_history()` 只返回最近历史。
