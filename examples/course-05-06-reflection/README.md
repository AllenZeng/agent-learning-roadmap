# Course 05-06 Reflection 示例项目

本目录是课程五 05-06「Reflection：基于反馈的决策闭环」的可运行示例。示例围绕知识助手和发布助手场景，展示 Reflection 如何把外部反馈信号变成可控的下一步决策。

两个版本都使用标准库实现，不需要外部服务或 API key：

- `python/reflection_demo.py`：Python 交互式演示。
- `nodejs/reflection_demo.mjs`：Node.js 交互式演示。

## 快速运行

Python：

```bash
cd examples/course-05-06-reflection/python
python3 reflection_demo.py
python3 -m unittest test_reflection_demo.py
```

Node.js：

```bash
cd examples/course-05-06-reflection/nodejs
npm start
```

`npm start` 进入交互模式。

## 你会看到什么

1. **V0 无反思**：测试失败被当成普通 Observation，Agent 继续执行后续步骤。
2. **V1 格式修复**：JSON Schema 校验失败触发重新生成。
3. **V2 工具错误处理**：工具参数错误被分类后，决定修正参数、重试或停止。
4. **V3 测试驱动处理**：测试失败提供外部证据，决定修代码、修环境、重试或停止。
5. **V4 引用校验**：生成内容中的 API 引用会被反向检索到笔记原文中验证。
6. **停止条件**：相同反馈重复出现时硬停止，避免无限处理。

## 和课程正文的关系

示例覆盖课程 05-06 的核心决策：

- 6.3：Reflection 必须依赖外部反馈信号，而不是模型自评。
- 6.4：触发、分类、决策、处理、验证或停止的闭环。
- 6.5：什么时候不需要 Reflection。

## 教学简化说明

- 示例不调用真实 LLM，用确定性函数模拟「第一次生成失败，第二次基于反馈决定下一步」。
- 测试执行和笔记检索是本地模拟，重点是展示 Runtime 中 Reflection 循环的位置和边界。
- 成本统计使用固定数字，真实系统需要接入模型调用计费、耗时和重试预算。
