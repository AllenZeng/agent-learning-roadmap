# Course 05-04 Planning / Workflow Patterns 示例

本目录包含课程五第四章「Planning / Workflow Patterns」的可运行示例代码。

## 场景：发布助手

所有示例围绕同一个场景：**你的 Agent 需要完成软件发布准备工作**。

任务包含四个步骤：

1. **检查 README** — 检查完整性，验证必要章节
2. **运行测试** — 运行全量测试套件
3. **整理 changelog** — 基于 git log 生成 changelog
4. **生成 checklist** — 汇总发布前所有待确认项

步骤间存在依赖关系：changelog 必须在测试通过后生成，checklist 依赖所有前置步骤完成。

## 四种 Planning 模式

| 模式 | Python 文件 | Node.js 文件 | 描述 |
|------|-------------|--------------|------|
| **Chain** | `python/patterns/chain.py` | `nodejs/planning_demo.mjs` | 固定顺序执行，遇错即停，最简单可控 |
| **Router** | `python/patterns/router.py` | `nodejs/planning_demo.mjs` | 分类器 + 多条 Chain，根据输入类型路由 |
| **Plan-Execute** | `python/patterns/plan_execute.py` | `nodejs/planning_demo.mjs` | 生成结构化计划 → 用户确认 → 执行 → 失败重规划 |
| **Graph** | `python/patterns/graph.py` | `nodejs/planning_demo.mjs` | 节点 + 条件边 + 状态机，支持失败分支跳转 |

## 快速开始

### Python

```bash
cd examples/course-05-04-planning/python
python3 planning_demo.py
```

REPL 提供这些演示选项：

- `1` — Chain 正常执行
- `1b` — Chain 遇到失败（观察遇错即停）
- `2` — Router 分类路由
- `3` — Plan-Execute 正常执行
- `3b` — Plan-Execute 失败→重规划（观察动态调整）
- `4` — Graph 正常执行
- `4b` — Graph 失败分支跳转
- `5` — 四种模式对比总结
- `0` — 退出

### Node.js

```bash
cd examples/course-05-04-planning/nodejs
npm start
```

Python 和 Node.js 版本提供相同的演示选项。

## 学习路径建议

1. 先运行 `1`（Chain）理解最基本的模式
2. 运行 `1b` 观察 Chain 的局限性
3. 运行 `3` 和 `3b` 理解 Plan-Execute 如何解决 Chain 的问题
4. 运行 `4` 和 `4b` 理解 Graph 的灵活性和成本
5. 运行 `5` 查看对比总结

## 关键设计决策

示例中的每个模式都展示了一个关键的设计权衡：

- **Chain vs Plan-Execute**：固定顺序 vs 动态规划——灵活性提升，但复杂度也提升
- **Plan-Execute vs Graph**：动态生成路径 vs 预定义所有路径——Graph 更可预测但建模成本更高
- **失败处理策略**：遇错即停（Chain）→ 重试+重规划（Plan-Execute）→ 跳转到错误分支（Graph）

## 示例边界

示例代码为了便于学习做了简化：

- Plan-Execute 用按 Enter 模拟用户确认；真实系统需要保存 confirmed plan，并在结构变化时重新请求确认。
- Plan-Execute 已包含 `max_replan_count` 和重复重规划检测，避免失败路径进入无限循环。
- Graph 示例记录执行路径用于回放，但不持久化状态；生产系统若要支持恢复执行，需要保存节点状态、上下文和结果。
