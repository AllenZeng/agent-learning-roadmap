# Course 05-08 Multi-Agent 示例项目

本目录是课程五 05-08「Multi-Agent：从一个人干活到一支团队协作」的可运行示例。

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

## 示例覆盖的三种模式

### 1. Reviewer 模式

一个 Executor 生成 API 技术方案，一个 Reviewer 只基于最终产物和审查清单做结构化审查。

你会看到：

- Executor 和 Reviewer 在输入、工具、目标、验收标准上都有真实差异。
- 第一轮 Reviewer 发现输入长度、密钥、权限、依赖锁定 4 个具体问题。
- Runtime 只把结构化 issues 传回 Executor，不传“整体质量不好”这类主观评价。
- 第二轮审查通过。
- Reviewer 永远收不到 Executor 的 private trace。
- 两轮仍未通过时进入 `disputed`，等待人工裁决。

### 2. Supervisor 模式

一个 Supervisor 把“调研 Agent 架构的四个主流方向”拆成 Tool Use、Memory、Planning、Multi-Agent 四个子任务，派发给四个 Worker，再按统一模板汇总。

你会看到：

- 每个子任务都有 `scope`、`exclude` 和统一输出字段。
- Worker 只输出结构化字段，不写自由散文，降低汇总成本。
- Supervisor 合并时去重、保留缺失，不假装失败 Worker 已完成。
- 测试覆盖 Worker 超时时报告 `partial` 和 `数据缺失`。

### 3. Parallel Specialists 模式

多个专家看同一段 `checkout.py` 输入，但分别从 correctness、security、performance 三个互斥维度分析。

你会看到：

- 相同位置 + 相同问题类型 + 相同判断会自动去重，并标注来源维度。
- 对同一位置的矛盾判断不会自动消解，而是进入 `conflicts`。
- 测试覆盖 `checkout.py:55 idempotency` 同时出现 `safe` 与 `problem` 时保留冲突。

## 教学简化说明

- 示例不调用真实 LLM，用确定性函数模拟 Agent 行为。
- “并行”在代码中用顺序调用模拟，重点展示可并行任务的输入输出边界；真实系统可替换为线程池、队列、Promise 并发或远程 Agent 调度。
- 真实生产系统需要把检查项、Worker 结果、冲突、trace、成本和延迟统计持久化，并接入人工裁决界面。
