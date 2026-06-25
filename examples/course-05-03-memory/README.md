# Course 05-03 Memory 示例项目

本目录是课程五 05-03「Memory：状态延续能力」的可运行示例。示例模拟知识助手从周一到周三的跨会话对话，展示 Memory 系统如何识别候选记忆、做写入决策、分层存储、召回、更新和遗忘。

两个版本都使用标准库实现，不需要外部服务或 API key：

- `python/memory_demo.py`：Python 版本。
- `nodejs/memory_demo.mjs`：Node.js 版本。

## 快速运行

Python：

```bash
cd examples/course-05-03-memory/python
python3 memory_demo.py --auto
```

Node.js：

```bash
cd examples/course-05-03-memory/nodejs
npm run auto
```

去掉 `--auto` 或使用 `npm start` 可以进入交互模式，每个 Session 之间按 Enter 继续。

## 输出文件

运行后会在当前语言目录下生成：

```text
memory_store/preferences.json
memory_store/facts.json
memory_store/task_history.json
memory_store/audit.jsonl
```

这些文件用于观察 Memory 的生命周期：

- `preferences.json`：用户偏好，包括 active 和 superseded 状态。
- `facts.json`：长期事实示例。
- `task_history.json`：最近任务经验。
- `audit.jsonl`：写入、拒绝、会话开始和结束的审计日志。

## 和课程正文的关系

课程正文讲的是产品级 Memory 设计原则；示例代码为了便于阅读和运行，做了简化：

- 推断偏好会写入 preference 存储，并在演示流程中提示为候选，用于演示后续冲突替换。
- 生产系统更建议使用独立的 `pending_candidate` 状态，让它默认不参与召回，等用户确认后再升级为 `active_memory`。
- 写作流程和语气偏好在示例中拆成细粒度 preference，方便观察 category 粒度对冲突检测的影响。
