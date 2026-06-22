# 第五章：Reflection：失败修正能力

[返回课程五主文档](./course-05-00-scenario-enhancement.md) | [上一章](./course-05-04-planning.md) | [下一章](./course-05-06-multi-agent.md)

## 本章目录

- [5.1 Agent 明明错了，却继续往下走](#51-agent-明明错了却继续往下走)
- [5.2 Self-Refine 和 Reflexion](#52-self-refine-和-reflexion)
- [5.3 反思必须依赖反馈信号](#53-反思必须依赖反馈信号)
- [5.4 触发、批判、修正、停止](#54-触发批判修正停止)
  - [触发信号](#触发信号)
  - [错误分类](#错误分类)
  - [修正方案](#修正方案)
  - [停止条件](#停止条件)
- [5.5 从格式校验到基于测试的修正](#55-从格式校验到基于测试的修正)
- [5.6 常见失败与修正](#56-常见失败与修正)
- [5.7 什么时候不需要 Reflection](#57-什么时候不需要-reflection)

---

### 5.1 Agent 明明错了，却继续往下走

回到 1.1。知识助手 Agent 现在有了 Planning，发布准备的四个步骤不再漏了。但执行到"运行测试"这一步时：

```text
TypeError: Cannot read properties of undefined (reading 'files')
```

Agent 看到了这个错误输出。然后它做了什么？它继续写 changelog，最后汇报"发布准备已完成"。

这不是工具问题，不是 Planning 问题，不是 Memory 问题。这是一个更根本的缺陷：**Agent 缺少"看到失败信号 → 停止 → 分析原因 → 修正 → 重试"的闭环。** 它看到了 TypeError，但它把那条输出当成了和"读取文件内容"一样的 Observation——一段需要被记录的信息——而不是一个需要被修正的错误。

换到知识问答场景。Agent 给了一段引用："根据《软件工程实践》第 3 章……"但你查看原文，发现那句话根本不在第 3 章。Agent 没有"引用校验"这一步，它生成引用时只是在生成"看起来像引用"的文本。

这类问题的本质是：**Agent 缺少被反馈信号触发的修正机制。** 它不会说"等等，这个测试失败了，让我看看为什么"。它只会继续生成下一个 Token。

### 5.2 Self-Refine 和 Reflexion

让 LLM "反思自己的输出"这个想法，经历了几个关键节点：

**2023 年 3 月，Self-Refine（Madaan et al.）。** 论文提出了一个简单但有效的流程：生成 → 反馈 → 修正。每一步都让同一个 LLM 完成——先输出初稿，再给自己提反馈，再根据反馈修改。这个流程在写作、代码生成等任务上取得了明显提升。但它的致命弱点是：**反馈完全来自模型自身，没有外部验证信号。** 一个错误的初稿可能导致模型给自己提一堆看似合理但方向全错的"反馈"。

**2023 年 6 月，Reflexion（Shinn et al.）。** 这个工作的突破在于引入了**外部验证信号**——不再让模型"自评"，而是让模型根据真实的执行结果（测试失败、编译器报错、API 返回）来判断哪里出错。Reflexion 把"反思"从生成策略升级为一种**基于环境反馈的强化学习式循环**：尝试 → 观察真实结果 → 分析失败原因 → 记录经验 → 重试。这比 Self-Refine 可靠得多，因为它有了外部锚点。

**2023 年底至今，Reflection 从学术概念走向工程实践。** 关键转变是：Reflection 不再被当成"模型的自省能力"，而是被设计成 Runtime 中的一个**带触发条件和停止条件的系统机制**。触发条件是什么信号（测试失败、Schema 校验失败、用户驳回），停止条件是什么情况（最大重试次数、成本上限、相同错误重复出现）。

### 5.3 反思必须依赖反馈信号

Reflection 容易被误解成"让模型自己检查一遍"。这不可靠。

模型自己说"我检查过了"并不等于真的可靠。更好的 Reflection 应该依赖外部反馈信号：

- JSON Schema 校验失败。
- 工具返回参数错误。
- 单元测试失败。
- 引用校验失败。
- 用户驳回。
- 权限检查不通过。
- 结果和验收标准不一致。

也就是说，Reflection 不是一个固定步骤，而是一个被触发的修正机制。

要回答四个问题：

- 什么时候触发反思？
- 反思要看哪些证据？
- 修正后是否重试？
- 重试几次后停止？

### 5.4 触发、批判、修正、停止

一个可控的 Reflection 机制可以分成四步：

```text
触发信号
  -> 错误分类 / 批判
  -> 生成修正方案
  -> 重试或停止
```

#### 触发信号

不要默认每一步都反思。常见触发信号包括：

| 触发信号 | 适合动作 |
|---|---|
| 输出格式不合法 | 重新生成结构化输出 |
| 工具参数错误 | 修正参数或请求用户补充 |
| 工具执行失败 | 分析错误类型，重试或降级 |
| 测试失败 | 定位失败原因并修改 |
| 引用不匹配 | 重新检索或修改回答 |
| 用户驳回 | 更新目标或约束 |
| 连续失败 | 停止并请求人工介入 |

#### 错误分类

Reflection 要先判断失败属于哪类：

- 目标理解错误。
- 上下文缺失。
- 工具选择错误。
- 工具参数错误。
- 外部环境错误。
- 输出格式错误。
- 权限不足。
- 结果质量不足。

不同错误需要不同修正方式。

#### 修正方案

修正可以是：

- 改写提示词。
- 调整工具参数。
- 换工具。
- 补充检索。
- 回到上一步。
- 请求用户澄清。
- 降级为人工确认。

#### 停止条件

必须设置停止条件：

- 最大重试次数。
- 最大成本。
- 最大耗时。
- 相同错误重复出现。
- 风险等级过高。
- 缺少足够反馈信号。

没有停止条件，Reflection 很容易变成无限循环。

Reflection 循环的核心骨架——关键是触发条件必须来自外部信号，停止条件必须硬编码：

```python
# Reflection 循环：只在有外部失败信号时触发，永远设置停止边界
def reflection_loop(
    action: callable,       # 执行动作（生成代码、回答问题等）
    validate: callable,     # 外部验证器（运行测试、检查 schema、校验引用）
    max_retries: int = 3,   # 硬上限
    cost_budget: float = 1.0  # 成本上限（美元）
) -> dict:
    """带 Reflection 的执行循环"""
    cost_spent = 0
    last_error = None
    
    for attempt in range(max_retries):
        # 1. 执行动作
        result = action(
            previous_error=last_error,  # 把上次失败原因注入上下文
            attempt=attempt
        )
        cost_spent += result.cost
        
        # 2. 外部验证（不是模型自评！）
        validation = validate(result.output)
        
        if validation.passed:
            return {"status": "success", "output": result.output, 
                    "attempts": attempt + 1, "cost": cost_spent}
        
        # 3. 分类失败，准备修正上下文
        last_error = {
            "type": classify_error(validation),  # schema_error | test_failure | tool_error | ...
            "message": validation.message,
            "evidence": validation.evidence,      # 具体报错行、引用原文等
            "suggested_fix": validation.suggestion
        }
        
        # 4. 停止条件检查
        if cost_spent > cost_budget:
            return {"status": "stopped", "reason": "cost_limit", 
                    "last_error": last_error}
        if last_error["type"] == "same_error" and attempt >= 2:
            return {"status": "stopped", "reason": "repeated_failure",
                    "last_error": last_error}
    
    return {"status": "stopped", "reason": "max_retries_exceeded",
            "last_error": last_error}

# 使用示例：代码修改 + 测试驱动的 Reflection
result = reflection_loop(
    action=lambda prev_err, attempt: llm_generate_code(
        task="fix the bug in user_service.py",
        test_failure=prev_err["evidence"] if prev_err else None
    ),
    validate=lambda code: run_tests(code),  # 外部测试框架，不是 LLM
    max_retries=3
)
```

> **设计要点**：`validate` 必须是外部验证器——跑测试、检查 schema、对比引用原文，不能是"让模型再看看"。`action` 接收 `previous_error` 作为修正信号，但只注入事实（报错内容、失败测试名），不注入模型的自我评价。

### 5.5 从格式校验到基于测试的修正

Reflection 可以按阶段迭代：

| 阶段 | 做什么 | 解决什么问题 |
|---|---|---|
| V0：无反思 | 失败直接返回 | 保持简单 |
| V1：格式修复 | JSON / schema 不合法时重试 | 结构化输出稳定性 |
| V2：工具错误修正 | 参数错误、超时、权限不足分类处理 | 工具调用稳定性 |
| V3：测试驱动修正 | 根据测试失败调整代码 | 代码类任务质量 |
| V4：引用和事实校验 | 检查回答是否有证据 | 知识问答可信度 |
| V5：用户反馈学习 | 把用户驳回纳入回归集 | 持续改进 |

不要为了"看起来更智能"每步都加自我批判。Reflection 应该服务具体问题。

### 5.6 常见失败与修正

| 失败模式 | 表现 | 原因 | 修正方向 |
|---|---|---|---|
| 错误反思 | 模型把错因分析错 | 缺少外部证据 | 引入测试、schema、工具错误码 |
| 无限重试 | 一直修正但不收敛 | 没有停止条件 | 设置重试、成本、耗时上限 |
| 成本过高 | 每步都反思 | 触发条件过宽 | 只在失败或低置信度触发 |
| 掩盖失败 | 反思后输出更自信但仍错误 | 自评替代验证 | 修正后必须重新验证 |
| 用户体验差 | Agent 反复解释过程，任务很慢 | 反思内容暴露过多 | 对用户展示摘要和关键选择 |

### 5.7 什么时候不需要 Reflection

以下场景不需要复杂 Reflection：

- 输出可以用确定性规则直接修正。
- 失败成本很低，简单重跑更便宜。
- 没有外部反馈信号，模型无法判断自己是否出错。
- 任务对延迟非常敏感。
- 高风险任务需要人工或规则校验，模型自评不能替代。

实用判断：

```text
如果有明确反馈信号，并且修正成本低于失败成本，Reflection 值得引入。
如果只是让模型”再想想”，通常不值得。
```

> **这个故事还没完。** Reflection 让 Agent 学会了从错误中修正，测试失败后会分析原因并重试。但还有一个根本性的问题：Agent 写完方案后，你让它从安全角度审查自己的方案——它说”没有明显问题”。你作为人类看了一眼，发现三个安全隐患。不是 Agent 不聪明，而是”创作者”和”审查者”需要不同的视角、不同的上下文、不同的判断标准。这就是最后一类增强能力要解决的：Multi-Agent。

---
