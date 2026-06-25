# Course 05-04 Planning 示例 (Node.js)

## 运行

```bash
npm start
```

## 内容

交互式 REPL 演示四种 Planning 模式：

1. **Chain** — 固定顺序执行
2. **Router** — 根据输入分类路由
3. **Plan-Execute** — 生成计划、执行、重规划
4. **Graph** — 节点图、条件跳转、失败分支

每种模式都有正常执行和失败注入两种演示。

## 说明

Node.js 版本是单文件教学实现，和 Python 版本展示相同的 REPL 选项。Plan-Execute 包含最大重规划次数和重复重规划检测；Graph 会记录执行路径，但不做持久化恢复。
