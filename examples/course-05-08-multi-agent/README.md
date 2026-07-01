# Course 05-08 Multi-Agent 示例项目

本目录是课程五 05-08「Multi-Agent：从一个人干活到一支团队协作」的可运行示例。示例聚焦最小可落地的 Reviewer 模式：一个 Agent 写技术方案，另一个 Agent 只基于最终产物和审查清单做结构化审查。

两个版本都使用标准库实现，不需要外部服务或 API key：

- `python/multi_agent_demo.py`：Python 版本。
- `nodejs/multi_agent_demo.mjs`：Node.js 版本。

## 快速运行

Python：

```bash
cd examples/course-05-08-multi-agent/python
python3 multi_agent_demo.py
python3 -m unittest test_multi_agent_demo.py
```

Node.js：

```bash
cd examples/course-05-08-multi-agent/nodejs
npm start
npm test
```

## 你会看到什么

运行后会依次演示：

1. **四个不同检查**：Executor 和 Reviewer 在输入、工具、目标、验收标准上都有真实差异。
2. **第一轮审查失败**：Reviewer 按清单发现 4 个具体问题，并给出文件位置和证据。
3. **只传具体 issues**：Runtime 只把结构化问题传回 Executor，不传“整体质量不好”这类主观评价。
4. **第二轮审查通过**：Executor 根据具体 issue 修正后，Reviewer 逐条 PASS。
5. **上下文隔离**：Reviewer 不接收 Executor 的中间推理和妥协解释。
6. **硬停止条件**：测试中覆盖了两轮仍未通过时进入 `disputed`，等待人工裁决。

## 和课程正文的关系

示例覆盖课程 05-08 的核心决策：

- 8.2：Multi-Agent 不是换 Prompt，而是输入、工具、目标、验收标准至少两个维度真的不同。
- 8.3：Reviewer 模式是最小入口，解决“执行者不能公正审查自己的产出”。
- 8.7：Agent 之间使用结构化 `ReviewRequest` / `ReviewResponse`，避免自由对话。
- 8.8：最多两轮修正，仍失败则标记 `disputed`，不让 Agent 无限往返。

## 教学简化说明

- 示例不调用真实 LLM，用确定性函数模拟“第一版有问题，第二版按反馈修正”。
- 安全审查规则用字符串检查实现，重点是展示 Multi-Agent Runtime 的数据流和边界。
- 真实生产系统需要把 `CheckItem`、`Issue`、trace、成本和延迟统计持久化，并接入人工裁决界面。
