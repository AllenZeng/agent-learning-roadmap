# 05-03 Memory Node.js

这是课程五 05-03「Memory：状态延续能力」的 Node.js 可运行示例，对应 `../python/memory_demo.py`。

示例模拟知识助手从周一到周三的跨会话对话，展示 Memory 系统的完整生命周期：

- 识别候选记忆
- 写入决策
- 分层存储
- 召回
- 更新与遗忘

## 运行

```bash
cd examples/course-05-03-memory/nodejs
npm start
```

交互模式会在每个 Session 之间等待按 Enter。

自动模式：

```bash
npm run auto
```

## 输出文件

运行后会生成：

```text
memory_store/preferences.json
memory_store/facts.json
memory_store/task_history.json
memory_store/audit.jsonl
```

## 设计要点

- 纯 Node.js 标准库实现，无需安装第三方依赖。
- 使用规则识别显式偏好、临时约束和敏感信息。
- 使用写入守卫拒绝敏感信息、临时信息和低置信度候选。
- 使用关键词匹配与轻量 bag-of-words 向量做召回演示。
- 用 `superseded` 状态保留偏好变更审计链路。
