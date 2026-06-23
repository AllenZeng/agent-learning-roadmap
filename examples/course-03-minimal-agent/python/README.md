# 01 Minimal Agent Python

这是课程三「最小 Agent 闭环」的可运行示例。它刻意不使用 Agent 框架，直接展示：

- `prompt.py`：Prompt 行为定义。
- `llm.py`：LLM 调用边界，包含可复现的 `ScriptedLLM` 和真实 OpenAI Responses API 适配。
- `tools.py`：本地工具 `read_file`、`write_file`、`search_text`。
- `agent.py`：Runtime 主循环、Context Assembly、Observation、State Update、停止条件和 Trace。
- `SessionState`：会话级状态，跨多轮用户输入保存消息和每轮结果。
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

## 运行多轮对话

```bash
cd examples/course-03-minimal-agent/python
python3 main.py --chat
```

`--chat` 会持续读取用户输入。每一轮都会调用一次 `run_turn()`：它先把用户消息写入 `SessionState.messages`，再执行内部 Agent loop，最后把助手回答和本轮 Trace 写回会话状态。输入 `exit` 或 `quit` 结束。

## 使用真实 LLM

```bash
cd examples/course-03-minimal-agent/python
export OPENAI_API_KEY="..."
export OPENAI_MODEL="gpt-4.1-mini"
python3 main.py --real-llm --goal "读取 data/notes.md，总结后写入 output/summary.md"
python3 main.py --real-llm --chat
```

真实 LLM 模式会调用 OpenAI Responses API。模型必须按 `prompt.py` 要求返回 JSON 决策。

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
- `SessionState` 能在多轮对话中保留用户/助手消息，并把最近对话注入下一轮上下文。
