# 01 Minimal Agent

这是课程三「最小 Agent 闭环」的可运行示例项目。为了便于对照学习，同一个示例包含两个实现版本：

- `python/`：Python 标准库实现。
- `nodejs/`：Node.js 标准库实现。

两个版本都刻意不使用 Agent 框架，核心结构保持一致：

- Prompt 行为定义。
- LLM 决策调用边界，默认提供可复现的 `ScriptedLLM`。
- 本地工具 `read_file`、`write_file`、`search_text`。
- Runtime 主循环、Context Assembly、Observation、State Update、停止条件和 Trace。
- 可选真实 DeepSeek Chat Completions API 调用。

## Python

```bash
cd examples/course-03-minimal-agent/python
python3 main.py
python3 -m unittest discover -s tests
```

## Node.js

```bash
cd examples/course-03-minimal-agent/nodejs
npm start
npm test
```

默认运行都使用离线 `ScriptedLLM`，不需要网络和 API Key。`main.py` / `npm start` 演示单次任务循环。真实 LLM 模式请分别参考子目录 README。
