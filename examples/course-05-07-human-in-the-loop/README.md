# Course 05-07 Human-in-the-loop 示例项目

本目录是课程五 05-07「Human-in-the-loop：当 Agent 不该自己决定时」的可运行示例。示例模拟一个文件清理、退款处理和发布文档生成混合场景，展示 Agent 在不同风险等级下如何选择人类介入方式。

两个版本都使用标准库实现，不需要外部服务或 API key：

- `python/hitl_demo.py`：Python 版本。
- `nodejs/hitl_demo.mjs`：Node.js 版本。

## 快速运行

Python：

```bash
cd examples/course-05-07-human-in-the-loop/python
python3 hitl_demo.py
python3 -m unittest test_hitl_demo.py
```

Node.js：

```bash
cd examples/course-05-07-human-in-the-loop/nodejs
npm start
```

运行时按提示手动批准、拒绝或转交操作。直接按 Enter 会选择提示中的默认选项。

## 你会看到什么

运行后会依次演示：

1. **风险分级**：同一个 `delete_file` 操作，会因为路径和影响不同进入中风险、高风险或关键风险。
2. **确认模式**：批量删除日志前展示后果、异常项和中间选项，而不是只问“是否调用 delete_file”。
3. **澄清模式**：当用户说“整理最近的文章”时，Agent 给出具体候选含义。
4. **接管模式**：关键风险操作只生成执行说明和命令，由人类接管，Agent 暂停等待人工完成。
5. **审核模式**：Agent 生成发布文档后标注不确定点，让人类聚焦检查。
6. **教学反馈**：人类指出遗漏后，Agent 立即修正，并把可复用偏好写入轻量 Memory。
7. **HITL 数据分析**：根据审计日志统计通过率，辅助判断哪些操作应降低或提高介入强度。

## 输出文件

运行后会在当前语言目录下生成：

```text
hitl_audit.jsonl
hitl_memory.json
```

- `hitl_audit.jsonl`：每次人类介入的模式、风险等级、决策和原因。
- `hitl_memory.json`：教学反馈中沉淀的偏好，例如“发布 checklist 必须包含数据库备份”。

## 和课程正文的关系

示例覆盖课程 05-07 中的关键模块：

- 7.3：确认、澄清、接管、审核、教学反馈五种模式。
- 7.4：风险分级、频率控制和决策上下文呈现。
- 7.5：把 HITL 反馈转化为可复用的 Memory。
- 7.7：避免“每步都确认”和“确认框信息不足”两个常见反模式。

## 教学简化说明

- 风险评估使用规则实现，目的是展示判断位置和数据流，不是生产级安全策略。
- 示例需要手动选择 HITL 决策；直接按 Enter 会采用默认选项，方便连续观察完整流程。
- 示例中的“退款”和“数据库迁移”不会调用外部系统，只打印决策上下文、后续流程分支和审计记录。
