# Course 05-04 Context Engineering 示例项目

本目录是课程五 05-04「Context Engineering：上下文工程」的可运行示例。示例模拟一个发布助手在同一轮任务里同时面对用户目标、系统规则、RAG 片段、Memory、工具定义、工具结果和 Scratchpad 状态，展示两种策略的差异：

- **Naive 策略**：把所有信息原样塞进上下文。
- **Engineered 策略**：先分层，再做预算、筛选、工具输出瘦身、可信度标注和 Scratchpad 注入。

两个版本都使用标准库实现，不需要外部服务或 API key：

- `python/context_engineering_demo.py`：Python 版本。
- `nodejs/context_engineering_demo.mjs`：Node.js 版本。

## 快速运行

Python：

```bash
cd examples/course-05-04-context-engineering/python
python3 context_engineering_demo.py
python3 -m unittest test_context_engineering.py
```

Node.js：

```bash
cd examples/course-05-04-context-engineering/nodejs
npm start
```

## 你会看到什么

运行后会输出三组对比：
运行后会输出四组对比：

1. **上下文组装对比**：Naive 策略超预算且暴露无关日志；Engineered 策略按层保留高优先级信息。
2. **工具输出处理**：长文件读取、搜索结果、API 返回和通用输出会经过不同处理器，保留可行动摘要和外部索引。
3. **评测摘要**：对比 token 使用量、上下文利用率、关键信号保留、注入攻击暴露和缓存友好程度。
4. **上下文消融摘要**：分别移除 RAG、Memory、工具摘要和 Scratchpad，观察关键信号是否丢失。

## 和课程正文的关系

示例覆盖课程 05-04 中的关键模块：

- 4.4：上下文分层、Token 预算、优先级裁剪。
- 4.5：Scratchpad 写入、选择、压缩、隔离思想和缓存友好的组装顺序。
- 4.6：可插拔工具输出处理器，避免工具结果污染主上下文。
- 4.7：用 A/B 指标评估上下文策略是否真的有效。

## 教学简化说明

- Token 估算使用轻量字符启发式，不等同于真实模型 tokenizer。
- “压缩”和“注入检测”使用规则实现，目的是展示工程位置和数据流，不是生产级安全过滤。
- 示例没有调用真实 LLM；重点是看清楚模型调用前的上下文调度层如何工作。
