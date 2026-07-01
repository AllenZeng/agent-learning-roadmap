# 课程四：工具机制

## 课程导言

课程三讲清了最小 Agent 闭环：

```text
Agent = LLM 决策 + 工具/环境交互 + 状态管理 + 循环控制
```

课程四深入其中连接"决策"和"执行"的关键环节：**工具/环境交互**。

很多人第一次做 Agent，会以为"给模型接几个函数"就完成了 Tool Use。实际上，只要你在真实任务里跑过几次，就会撞上各种意想不到的问题：

- 模型明明有搜索工具，却在应该查资料的时候直接编了一个答案。
- 工具执行成功了，但返回了 5000 行日志，下一轮上下文被撑爆，模型"忘"了用户最初的指令。
- 模型生成了一个看起来合理的文件路径，但那个路径在 workspace 外面——如果 Runtime 不拦截，它就会读到不该读的文件。
- 用户说"帮我发封邮件"，模型直接调了 `send_email`，没有确认收件人、没有预览内容——用户吓出一身冷汗。

这些问题不是"模型不够强"导致的。它们的根源在于：**工具调用不是一次孤立的 API 请求，而是一段需要被精心设计的运行时机制。** 

本课从课程二提到的 Function Calling 历史出发，把工具调用拆成一条完整的链路：

```text
LLM Decision → Tool Selection → Parameter Generation
    → Permission Check → Tool Execution
    → Observation / Feedback → State Update
```

链路中每一步都可能失败，每一步都需要对应的机制来兜底。课程四的目标不是让你"接入更多工具"，而是让你理解如何把工具调用设计成**可选择、可执行、可控、可复用、可审计**的系统机制。

---

## 学习目标

学完本课，你将能够：

1. **画出完整工具调用链路** — 理解从模型决策到工具执行再到状态更新的每一步及其风险
2. **设计清晰的工具定义** — 写出让模型准确理解"何时用、何时不用"的工具描述和参数 Schema
3. **诊断工具选择失败** — 区分该用不用、不该用乱用、选错工具、参数猜错、重复调用，并找到根因
4. **实现工具执行与回填** — 掌握参数校验、超时、重试、错误结构化和结果摘要的基本代码模式
5. **设计工具权限策略** — 使用风险分级、Deny-first、最小权限、审计日志控制高风险动作
6. **设计 Human-in-the-loop 控制点** — 明确哪些工具动作必须由人确认、修改或接管
7. **区分 Function Calling、MCP、Tool、Skill 的位置** — 明确它们分别解决工具链路上的哪一段问题
8. **把重复工具组合沉淀成 Skill** — 理解任务经验、默认流程、失败处理和复用边界

---

## 目录

- [课程导言](#课程导言)
- [学习目标](#学习目标)
- [第一章：Agent 如何调用工具](#第一章agent-如何调用工具)
  - [1.1 工具调用不是一次 API 请求](#11-工具调用不是一次-api-请求)
  - [1.2 工具调用链路](#12-工具调用链路)
  - [1.3 从 Function Calling 到工具机制体系](#13-从-function-calling-到工具机制体系)
- [第二章：工具定义 —— 让模型知道工具是什么](#第二章工具定义--让模型知道工具是什么)
  - [2.1 工具定义的本质](#21-工具定义的本质)
  - [2.2 工具名、描述和参数 Schema](#22-工具名描述和参数-schema)
  - [2.3 返回值结构和错误结构](#23-返回值结构和错误结构)
  - [2.4 工具粒度：原子 vs 组合](#24-工具粒度原子-vs-组合)
  - [2.5 好工具的设计原则](#25-好工具的设计原则)
- [第三章：工具选择 —— 让模型知道什么时候用哪个](#第三章工具选择--让模型知道什么时候用哪个)
  - [3.1 工具选择的三件事](#31-工具选择的三件事)
  - [3.2 三种路由方式](#32-三种路由方式)
  - [3.3 候选集管理：不要把所有工具都交给模型](#33-候选集管理不要把所有工具都交给模型)
  - [3.4 工具选择失败分类与调试](#34-工具选择失败分类与调试)
- [第四章：执行与回填 —— 让工具结果进入下一轮](#第四章执行与回填--让工具结果进入下一轮)
  - [4.1 Runtime 才是真正的执行者](#41-runtime-才是真正的执行者)
  - [4.2 参数校验、超时、重试和幂等](#42-参数校验超时重试和幂等)
  - [4.3 错误结构化](#43-错误结构化)
  - [4.4 结果处理：摘要、分页、截断和转资源](#44-结果处理摘要分页截断和转资源)
  - [4.5 Observation：为下一轮决策提供依据](#45-observation为下一轮决策提供依据)
- [第五章：权限与安全 —— 让工具调用可控](#第五章权限与安全--让工具调用可控)
  - [5.1 为什么工具权限不是可选项](#51-为什么工具权限不是可选项)
  - [5.2 风险分级与默认策略](#52-风险分级与默认策略)
  - [5.3 Deny-first 和最小权限](#53-deny-first-和最小权限)
  - [5.4 渐进式授权和审计日志](#54-渐进式授权和审计日志)
- [第六章：Human-in-the-loop —— 让人参与高风险决策](#第六章human-in-the-loop--让人参与高风险决策)
  - [6.1 模型不应该独自决定一切](#61-模型不应该独自决定一切)
  - [6.2 触发条件与介入方式](#62-触发条件与介入方式)
  - [6.3 确认界面和反馈闭环](#63-确认界面和反馈闭环)
- [第七章：MCP —— 让工具接入标准化](#第七章mcp--让工具接入标准化)
  - [7.1 当工具越来越多时会发生什么](#71-当工具越来越多时会发生什么)
  - [7.2 MCP 和 Function Calling 的分工](#72-mcp-和-function-calling-的分工)
  - [7.3 Tools / Resources / Prompts](#73-tools--resources--prompts)
  - [7.4 什么时候引入 MCP](#74-什么时候引入-mcp)
- [第八章：Skill —— 把重复任务沉淀成能力包](#第八章skill--把重复任务沉淀成能力包)
  - [8.1 从"每次都重新想"到"把经验打包"](#81-从每次都重新想到把经验打包)
  - [8.2 Skill 的结构](#82-skill-的结构)
  - [8.3 Skill vs Tool vs Workflow](#83-skill-vs-tool-vs-workflow)
- [课后练习](#课后练习)
- [验收标准](#验收标准)
- [参考资料](#参考资料)
- [下一课衔接](#下一课衔接)

---

## 第一章：Agent 如何调用工具

### 1.1 工具调用不是一次 API 请求

回想课程二讲过的 Toolformer 和 Function Calling。Toolformer 证明了一件事：模型可以学会"什么时候该调用 API"。Function Calling 把这件事标准化成了工程接口：模型不再输出"建议你去查一下数据库"，而是输出一个结构化的 `{"tool": "query_db", "arguments": {...}}`。

但这里有一个容易被忽视的跳跃。在 Function Calling 的设计中，模型只负责**生成调用意图**——真正执行的是 Runtime。这个分工意味着：从模型的"我想调用这个工具"到"工具结果回到下一轮决策"之间，有一整条链路的工程问题需要处理。

单纯把工具调用看成"模型输出工具名 → 程序调 API → 返回结果"，会漏掉一堆关键问题：

- 模型怎么知道有哪些工具？
- 模型怎么知道什么时候该用、什么时候不该用？
- 多个工具都可能有用时，模型怎么选？
- 模型生成的参数是否可信？（它编造了一个不存在的文件名怎么办？）
- 工具执行失败怎么办？
- 工具结果太长，塞进上下文后把关键信息挤掉了怎么办？
- 工具动作有真实世界影响（发邮件、删文件、下单），谁负责批准？
- 多个工具经常一起使用来完成任务，怎么沉淀成可复用的模式？

这些问题单靠"模型变强"解决不了——它们需要 Runtime 层面的系统性设计。

### 1.2 工具调用链路

把工具调用展开，它是一条七步链路：

![工具调用七步链路](../assets/course-04-tool-call-chain.svg)

这条链路可以直接映射回课程三的最小闭环——它就是把闭环中"工具/环境交互"这一步展开了。

### 1.3 从 Function Calling 到工具机制体系

课程二梳理过工具调用的演进：Toolformer（2023.2）证明了模型可以学会使用工具 → ChatGPT Plugins（2023.3）把"AI 能做事"变成大众体验 → Function Calling（2023.6）标准化了模型生成工具调用的接口 → MCP（2024）试图标准化工具的发现和连接。

课程四站在这些历史节点之上，聚焦于一个问题：**当你真的要在自己的系统里让模型调用工具时，需要设计哪些机制？** 

![工具机制体系总览](../assets/course-04-tool-mechanism-map.svg)

---

## 第二章：工具定义 —— 让模型知道工具是什么

### 2.1 工具定义的本质

工具定义是模型理解工具的唯一入口。模型不知道你的函数内部是怎么实现的，不知道你的数据库里有什么，不知道你的 API 有什么限制。它只知道你告诉它的东西。

所以工具定义的质量直接决定了工具调用的上限。描述模糊 → 模型犹豫或误用。参数约束缺失 → 模型自由发挥填错值。错误格式不统一 → 模型拿到一个"failed"不知道下一步该干什么。

工具定义要回答六个问题：
- 这个工具能做什么？
- 这个工具**不能**做什么？
- 什么时候应该使用它？什么时候不应该？
- 使用它需要哪些参数？每个参数的含义和约束是什么？
- 成功时返回什么？什么格式？
- 失败时返回什么？包含哪些信息帮助下一步决策？

### 2.2 工具名、描述和参数 Schema

一个工具定义至少包含名称、描述和参数 Schema。下面是 Python 代码中一个规范的 JSON Schema 工具定义：

```python
TOOL_READ_FILE = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": (
            "读取 workspace 下的 UTF-8 文本文件。"
            "当用户要求查看、阅读、检查某个文件内容时使用此工具。"
            "注意：只能读取 workspace 目录下的文件，不能读取系统文件或外部路径。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "文件相对于 workspace 的路径，例如 'notes.md' "
                }
            },
            "required": ["path"]
        }
    }
}
```

设计要点：
- **名称要具体**，不要叫 `do_task`、`helper`、`process`。模型通过名称建立第一印象。
- **描述要说明适用场景和不适用场景**。这比参数说明更重要——模型先判断"该不该用"，再考虑"怎么用"。
- **参数要有类型、约束和示例**。不要留给模型"猜"的空间。
- **工具边界要清楚**，避免多个工具能力重叠。如果 `search_web` 和 `search_database` 的描述太像，模型就会随机选。

对比两个描述的质量差异：

```python
# 糟糕的描述 — 太模糊，模型无法判断何时使用
BAD_TOOL = {
    "name": "process_data",
    "description": "处理数据",
    "parameters": {"properties": {"input": {"type": "string"}}}
}

# 好的描述 — 明确了场景、边界和约束
GOOD_TOOL = {
    "name": "summarize_document",
    "description": (
        "将文本文件内容总结为指定数量的要点。"
        "当用户要求'总结'、'概括'、'提炼要点'时使用。"
        "注意：需要先通过 read_file 获取文件内容，不要在没有内容时调用。"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "要总结的文本内容（通常来自 read_file 的返回结果）"
            },
            "num_points": {
                "type": "integer",
                "minimum": 1,
                "maximum": 10,
                "default": 5,
                "description": "总结的要点数量，1-10，默认 5"
            }
        },
        "required": ["content"]
    }
}
```

### 2.3 返回值结构和错误结构

工具返回值也需要约定格式。如果成功时返回自然语言、失败时返回异常堆栈，模型和 Runtime 都会很难处理。

推荐统一的结构化返回格式。在 Python 中实现：

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class ToolResult:
    """统一的工具返回结构"""
    status: str                          # "success" | "error"
    summary: str                         # 简短摘要，会被放入上下文
    data: Any | None = None              # 完整数据，可能较长
    error: dict[str, str] | None = None  # 错误详情，仅 status="error" 时有值

    @classmethod
    def success(cls, summary: str, data: Any = None) -> "ToolResult":
        return cls(status="success", summary=summary, data=data)

    @classmethod
    def error(cls, code: str, message: str,
              retryable: bool = False,
              suggested_action: str = "") -> "ToolResult":
        return cls(
            status="error",
            summary=message,
            error={
                "code": code,
                "message": message,
                "retryable": str(retryable).lower(),
                "suggested_action": suggested_action,
            }
        )
```

结构化返回的核心价值：**模型看到 `error.code == "file_not_found"` 和 `suggested_action`，就能直接给出有针对性的下一步决策**，而不是收到一个模糊的"失败了"然后开始乱猜。

### 2.4 工具粒度：原子 vs 组合

工具粒度是最容易被忽视但影响最大的设计决策。

![工具粒度选择：原子 vs 组合](../assets/course-04-atomic-vs-composite.svg)

### 2.5 好工具的设计原则

汇总一下，好工具通常具备这些特征：

- **原子性**：一个工具做好一类清晰动作。不要一个工具既读文件又发邮件。
- **描述即文档**：工具描述是模型理解工具的主要甚至唯一文档。
- **边界清晰**：明确说明什么时候该用、什么时候不该用。后者和前者一样重要。
- **结构化返回**：成功和失败都有统一的格式，错误包含编码、原因和建议。
- **可重试性明确**：失败时告诉模型"这个可以重试"还是"这个别再试了"。
- **副作用可控**：写入、删除、发送、支付等动作必须有权限控制，不能默认自动执行。
- **可观测**：每次调用的参数、结果、耗时都被记录。

---

## 第三章：工具选择 —— 让模型知道什么时候用哪个

### 3.1 工具选择的三件事

工具选择本质上在一个决策点上回答三个问题：

```text
什么时候用工具 → 用哪个工具 → 参数怎么填
```

这三步中任何一步出错，工具调用就会失败。而且错误的根因经常不在"模型不行"，而在工具定义、上下文或路由设计。

举个例子，用户说：

```text
请总结 notes.md 的内容。
```

正确的行为和可能的错误：

```text
正确：read_file("notes.md") → 获取内容 → 返回总结
错误1：不读文件，直接编造一份"总结"        ← 该用不用（幻觉）
错误2：search_web("notes.md")              ← 选错工具（边界混淆）
错误3：read_file("note.md")               ← 参数填错（少了一个 s）
错误4：read_file 成功后再次 read_file     ← 重复调用（缺进展判断）
```

### 3.2 三种路由方式

先看一个真实系统里很常见的问题：Agent 接入工具的第一周，只有 `read_file`、`search_web`、`calculator` 三个工具，模型通常选得还不错。两个月后，工具列表变成 40 个：文件读写、代码搜索、网页搜索、数据库查询、发邮件、创建工单、部署、回滚、支付退款、用户资料查询。此时如果还把所有工具一次性塞进上下文，让模型"自己看着办"，错误会明显增多。

问题不只是模型选错。工具越多，工具描述本身占用的上下文越多；相似工具越多，边界越模糊；高风险工具和低风险工具混在一起，权限控制也会变得危险。生产系统里的工具路由，核心不是"模型够不够聪明"，而是：

```text
系统应该让模型在什么范围内做决策？
```

工具选择通常有三种实现方式，它们的核心区别在于"决策权在谁手里"。

**方式一：模型自主选择**。把工具列表注入上下文，让模型自己判断是否调用、调用哪个。

**方式二：规则路由**。根据输入特征由代码决定工具。

**方式三：混合路由**。规则先缩小候选集，模型在候选集中选择。

实践中，混合路由是最常见的生产选择：**系统先缩小范围，模型再精准选择。**

![三种路由方式对比](../assets/course-04-three-routing-methods.svg)

### 3.3 候选集管理：不要把所有工具都交给模型

候选集管理解决的是一个更底层的问题：**当前这一步，模型应该看见哪些工具？**

有些场景下，是否调用工具不应该由模型决定：

**应该强制调用工具的场景**：用户要求查询实时数据、用户要求读取文件、用户要求精确计算、用户要求验证外部环境。如果不调工具，模型大概率会凭记忆或语言模式生成一个看似合理但不可验证的答案。

**应该禁止调用工具的场景**：用户只是闲聊或概念解释、用户请求越权动作、当前任务已经完成、高风险动作尚未确认。如果此时调工具，要么浪费资源，要么带来安全风险。

除了强制和禁止，中间的大多数情况都应该进入候选集筛选，而不是把所有工具交给模型。

#### 渐进式披露：先给目录，再给细节

Claude Code / Agent Skills 的实践里有一个值得借鉴的思路：**渐进式披露（progressive disclosure）**。它的核心不是某个特定文件格式，而是一种上下文管理原则：

```text
不要在一开始暴露所有能力细节。
先暴露能力索引。
模型判断相关后，再加载具体说明。
真正要执行时，再读取深层文档、示例或脚本。
```

把这个思路放到工具机制里，可以分成三层：

![渐进式披露：三层工具信息模型](../assets/course-04-progressive-disclosure.svg)

这解决了两个问题。第一，节省上下文：一个 Agent 可以拥有很多工具，但当前轮次不必携带全部工具说明。第二，降低干扰：模型只在当前任务相关的工具之间选择，不会被无关工具诱导。

#### 混合路由如何根据上下文筛选工具

候选集不是简单按关键词过滤。一个更可靠的路由器会同时看七类上下文：

- **意图**：用户是在查询、写入、计算、搜索、执行命令，还是请求确认？
- **任务阶段**：当前处于探索、读取、分析、修改、验证、提交，还是结束阶段？
- **资源范围**：任务涉及本地文件、当前项目、外部网页、数据库，还是第三方 API？
- **用户权限**：当前用户是否有读权限、写权限、执行权限、生产环境权限？
- **风险等级**：工具是只读、可逆写入、不可逆写入、外部副作用，还是高危操作？
- **上下文证据**：当前信息是否足够？是否需要读取真实文件、查询实时数据或验证环境？
- **历史轨迹**：刚才调用过什么？是否已经失败？是否正在重复调用同一个无进展工具？

一个具体例子：

```text
用户请求：帮我看看 notes.md 里关于工具机制写得怎么样。

上下文判断：
- 意图：读取 + 分析
- 阶段：探索 / 读取
- 资源范围：本地文件
- 权限：允许读取，不允许写入
- 风险：低风险，只读
- 证据：必须读取真实文件，不能凭空总结

候选工具：
- read_file
- list_files（如果文件路径不明确）

被过滤掉的工具：
- write_file（用户没有要求修改）
- search_web（用户指定的是本地文件）
- send_email（无关且有外部副作用）
- deploy_project（无关且高风险）
```

这时模型不是在几十个工具中自由选择，而是在一个非常小的候选集中判断："路径明确，所以直接调用 `read_file`。"

本节最重要的结论是：**工具路由不是把选择权全部交给模型，而是把选择权分层。** 系统决定候选范围，模型在范围内做语义判断，Runtime 在执行前做权限和参数校验。工具越多、风险越高，越应该使用候选集管理和渐进式披露。

### 3.4 工具选择失败分类与调试

当工具选择出错时，不要只改 Prompt。先按类型定位问题：

| 失败类型 | 表现 | 常见根因 | 调试方向 |
|---|---|---|---|
| 该用不用 | 需要查数据却不调工具 | 工具描述太弱，模型不知道它能做这个 | 强化描述中的使用场景 |
| 不该用乱用 | 闲聊也调搜索 API | 工具描述诱导性太强，或 Prompt 没约束 | 在描述中加"不要使用"的场景 |
| 选错工具 | 该读文件却搜网页 | 工具边界重叠，描述太相似 | 区分两个工具的使用场景描述 |
| 参数猜错 | 文件名、ID 编造 | 参数约束不足，或上下文缺信息 | 加强 Schema 约束 + 检查上下文是否包含所需参数 |
| 重复调用 | 同工具反复调无新结果 | 缺少循环控制和进展判断 | 在 Runtime 层面加重复检测 |

一个具体的调试案例：

```text
问题：用户说"帮我看看 notes.md 写了什么"，模型调了 search_web("notes.md")

根因分析：
1. 检查上下文 — 模型收到了 tools 列表，其中包括 read_file 和 search_web
2. 检查工具描述 — read_file 的描述只说"Read a file"，没说它和 search_web 的区别
3. 检查语义边界 — 两个工具的描述都没有明确各自的适用/不适用场景，模型无法有效区分

修复：
- read_file 描述中加上："当用户指定了具体文件名时使用此工具，例如'读取 notes.md'。"
- search_web 描述中加上："当用户要求搜索广泛信息、最新资讯时使用。不要用于读取用户指定的本地文件。"
```

调试工具选择问题的原则：**先排除工具定义的问题，再调整 Prompt，最后才怀疑模型能力。**

---

## 第四章：执行与回填 —— 让工具结果进入下一轮

### 4.1 Runtime 才是真正的执行者

模型生成了 tool call，不代表工具已经被执行。模型只是说"我想调用 read_file，参数是 notes.md"。真正去读文件、处理错误、格式化结果的是 Runtime。

Runtime 在工具执行环节的职责：

```python
execute_tool_call(tool_name, arguments, tools, permissions, logger):
    # 1. 校验工具是否存在 → 不存在则返回 tool_not_found 错误
    # 2. 校验参数（必填项、类型、约束）→ 不通过则返回具体校验错误
    # 3. 检查权限（deny 优先，默认拒绝）→ 不通过则返回 permission_denied
    # 4. 记录审计日志（谁、什么工具、什么参数、什么时间）
    # 5. 执行工具 → 成功返回结果，异常返回结构化错误（含 retryable 标记）
```

这就是课程三的核心原则在工具层的具体体现：**模型决策，Runtime 执行。** 模型不应该有机会绕过权限检查，也不应该自己决定"文件读不到就算了"。

### 4.2 参数校验、超时、重试和幂等

执行前的参数校验是拦截错误的第一道防线：

```python
validate_params(tool_name, arguments, tools):
    # 1. 从工具的 parameters Schema 中读取 required 和 properties
    # 2. 遍历 required 列表 → 缺失则返回 missing_required 错误
    # 3. 遍历 arguments → 检查类型匹配（integer 不能传 string）
    #                    → 检查 enum 约束（值必须在允许范围内）
    # 4. 全部通过返回 None，任何失败返回结构化错误
```

工具执行还需要超时和重试保护。核心模式：

```python
# 超时：每个工具设置执行时限，超时即中断
# 重试：仅对幂等操作重试（读文件 ✓，发邮件 ✗），指数退避
# 两者通过装饰器或中间件统一施加，不要在工具函数内部实现

@timeout(30s)
@retry(max=2, backoff=exponential)
query_database(sql) → 只读查询，幂等 → 安全重试

@timeout(10s)
send_email(to, subject, body) → 非幂等 → 不加 retry，防止重复发送
```

重试策略的关键判断：**这个操作重试后结果是否一致？** 读文件 → 可以重试。查数据库（只读）→ 可以重试。发邮件 → 不能随便重试（可能重复发送）。创建订单 → 不能随便重试（可能重复扣费）。

### 4.3 错误结构化

工具失败时，返回的信息质量决定了模型下一轮决策的质量。

比较两种错误返回：

```python
# 糟糕：模型拿到这个不知道该干什么
"Error: failed"

# 好的：模型能据此判断下一步
{
  "status": "error",
  "error": {
    "code": "permission_denied",
    "message": "文件 '/etc/passwd' 不在允许的 workspace 范围内",
    "retryable": false,
    "suggested_action": "请选择 workspace 目录下的文件重试"
  }
}
```

结构化错误至少包含五个字段：错误码（`code`）、可读信息（`message`）、是否可重试（`retryable`）、建议下一步（`suggested_action`）、是否需要用户介入（`needs_user`）。这五个字段让模型下一轮可以做出有依据的判断，而不是从"failed"这个词上胡乱猜测。

### 4.4 结果处理：摘要、分页、截断和转资源

工具结果经常很长——搜索返回 20 个网页、数据库返回 1000 条记录、文件有 10 万字、测试日志有几千行。全部塞进上下文会撑爆窗口，关键信息被淹没。

| 方法 | 适用场景 |
|---|---|
| 摘要 | 结果长但只需关键信息（搜索、API 响应） |
| 分页 | 结果列表长，需要逐步查看（数据库查询） |
| 截断 | 只留头部和尾部（日志、长文件） |
| 转资源 | 原始结果写入临时文件，模型拿引用路径 |
| 结构化提取 | 从结果中只提取字段、错误码、匹配项 |

### 4.5 Observation 如何塑造下一轮决策

前面四节讲了工具怎么执行、结果怎么处理。但还有一个关键问题没有展开：**工具结果回到模型面前时，模型到底是怎么"用"它的？**

Observation 在工具调用链路中的位置很特殊——它既是上一轮的终点（工具执行完了），也是下一轮的起点（模型要基于它做决策）。这个双重身份决定了 Observation 的设计质量直接影响到整个闭环的运转质量。

#### 4.5.1 Observation 的本质：为下一轮决策提供依据

先看一个具体对比。假设模型调了 `read_file("notes.md")`，文件不存在。

**糟糕的 Observation：**
```text
Error: failed
```

模型拿到这个，它不知道是文件不存在、权限不够、磁盘满了还是网络断了。它只能猜。猜错了 → 下一步也错 → 用户看到的是 Agent 在胡言乱语。

**好的 Observation：**
```json
{
  "status": "error",
  "error": {
    "code": "file_not_found",
    "message": "文件 'notes.md' 在 workspace 中不存在",
    "retryable": false,
    "suggested_action": "请确认文件路径是否正确，或使用 list_files 查看 workspace 中的可用文件"
  }
}
```

模型拿到这个，它可以立即做出合理判断：
```python
Thought: 文件不存在。我应该列出 workspace 下的文件，让用户看到有哪些可选。
Action: list_files()
Observation: ["notes.txt", "readme.md", "src/"]
Thought: 没有 notes.md，但有一个 notes.txt，可能是用户记错了文件名。
Action: ask_user("没有找到 notes.md，但发现了 notes.txt。您是指这个文件吗？")
```

这个对比说明了 Observation 最核心的设计原则：**Observation 不是在汇报"发生了什么"，而是在为下一轮决策提供"依据"。** 它应该让模型不需要猜测就能判断下一步该做什么。

#### 4.5.2 Observation 设计的四个维度

**维度一：信息完整性。** 

**维度二：结构一致性。** 

**维度三：上下文感知。** 

**维度四：模型可操作性。** 

![Observation 设计的四个维度](../assets/course-04-observation-four-dimensions.svg)


#### 4.5.3 常见 Observation 设计失误

| 失误 | 表现 | 后果 | 修复 |
|---|---|---|---|
| **过于简略** | 只返回 `"ok"` 或 `"failed"` | 模型无法判断下一步，开始胡猜 | 返回结构化的状态码、摘要和上下文提示 |
| **过于冗长** | 把 5000 行日志全塞进 Observation | 上下文被撑爆，模型"忘记"之前的关键信息 | 先用 4.4 的结果处理策略做摘要/截断 |
| **格式混乱** | 每个工具返回格式不同 | 模型需要不断适应新格式，增加误判概率 | 统一 `{status, summary, data, error}` 结构 |
| **缺少上下文** | 只报告"搜到 3 条结果"，不说是什么、与任务的关系 | 模型不知道这些结果的意义 | 加上 `context_hint` 字段 |
| **把空结果当错误** | `search` 没找到匹配 → 返回 error | 模型以为工具坏了，可能换工具或放弃 | 区分"工具执行失败"和"工具执行成功但没有匹配" |
| **错误码不区分** | 所有错误都返回 `"error"` | 模型不知道是临时故障（可重试）还是永久错误（该换策略） | 用 `retryable` 字段明确标识 |

---

## 第五章：权限与安全 —— 让工具调用可控

### 5.1 为什么工具权限不是可选项

工具调用一旦能影响外部世界，权限和安全就从"上线前再考虑"变成了"第一天就要设计"。Agent 可能做的危险操作：读取私有文件、写入或删除文件、查询用户数据、发送消息、修改配置、创建订单、触发付款、发布内容。

这些操作的问题不在于"模型心怀恶意"，而在于**模型不理解后果**。它看到的不是"这个操作会删掉用户三年的数据"，而是"根据概率分布，下一个 Token 可能是 DELETE"。

### 5.2 风险分级与默认策略

先对工具做风险分级：

```python
风险等级（从低到高）：
  L1 READ_ONLY_LOW   — 读取公开资料、搜索网页        → auto（自动执行）
  L2 READ_ONLY_MED   — 读取用户文件、查询数据库      → auto
  L3 WRITE_LOW       — 写入草稿、生成本地临时文件    → confirm（执行前确认）
  L4 WRITE_HIGH      — 修改用户文件、更新数据库记录  → confirm
  L5 DANGEROUS       — 删除、支付、发布、线上配置    → deny（默认禁止）
```

风险分级不是一劳永逸。它还要结合操作对象（删除临时文件 vs 删除生产数据）、操作范围（修改一个字段 vs 修改整张表）、用户授权级别来判断。

### 5.3 Deny-first 和最小权限

权限设计的核心原则只有两条：

```text
Deny-first：默认拒绝，明确允许。
最小权限：只给 Agent 当前任务所需的最小工具、最小数据、最小作用域。
```

代码实现：

```python
PermissionChecker:
    rules = []   # 规则列表，deny 优先级高于 allow

    allow(tool, condition=None)   # 添加允许规则
    deny(tool, condition=None)    # 添加拒绝规则

    check(tool_name, arguments):
        for rule in rules:
            if rule is deny and match(rule, tool_name, arguments):
                return False          # 命中 deny → 直接拒绝
        for rule in rules:
            if rule is allow and match(rule, tool_name, arguments):
                return True           # 命中 allow → 允许
        return False                  # 都没命中 → 默认拒绝

# 配置示例
checker.allow("read_file", path in "workspace/")
checker.deny("read_file",  path contains "secrets")
checker.allow("write_file", path in "workspace/output/")
checker.deny("delete_file")               # 全面禁止
checker.deny("send_email")
# 未列出的工具 → 默认拒绝
```

这个设计的要点是：**deny 优先于 allow，没列出的工具默认拒绝。** 这让权限策略的安全边界清晰可控——你不需要担心"有没有漏掉一个危险工具"，因为没列出的自动就是不能用的。

### 5.4 渐进式授权和审计日志

Agent 产品不应该一开始就要求用户配置大量永久权限。渐进式授权更合理：
- 低风险只读动作可以自动执行。
- 中风险写入动作初次执行时请求确认，用户可选择"本次会话记住"。
- 高风险动作每次都需要确认，不允许记住。
- 用户可以随时撤销已授权的权限。

审计日志是工具调用安全的基础——没有日志，出问题时你无从排查：

```json
{
  "timestamp": "2026-06-30T10:42:18Z",
  "user_id": "user_123",
  "task_id": "task_20260630_001",
  "tool_call_id": "call_0007",
  "tool_name": "write_file",
  "arguments": {
    "path": "output/summary.md",
    "content_preview": "课程四工具机制总结...",
    "content_sha256": "9f86d081884c7d659a2feaa0c55ad015"
  },
  "risk_level": "WRITE_LOW",
  "permission": {
    "result": "confirmed_by_user",
    "policy": "confirm_on_first_write",
    "confirmed_by": "user_123",
    "confirmed_at": "2026-06-30T10:42:21Z",
    "remember_scope": "session"
  },
  "execution": {
    "result": "success",
    "duration_ms": 184,
    "error": null
  }
}
```

审计日志每条记录回答：谁、什么时候、在哪个任务里、想调什么工具、参数是什么、权限检查结果、谁确认的、执行结果。这不仅是合规需要，更是调试和用户信任的基础。

---

## 第六章：Human-in-the-loop —— 让人参与高风险决策

### 6.1 模型不应该独自决定一切

工具机制走到这里，还有一个关键控制点需要覆盖：**什么样的动作模型可以自己做决定，什么样的动作必须经过人类确认？**

答案是：当动作的后果不可逆、影响真实用户、或者模型自身的置信度不够高时，应该把人类拉入循环。

Human-in-the-loop 不是"Agent 能力不够时的临时补丁"，而是**工具机制中的结构性控制点**。它承认一个基本事实：模型不理解后果，最终的责任在人。

### 6.2 触发条件与介入方式

常见触发条件：
- 高风险动作（删除、支付、发布、发送消息）。
- 模型自己表示不确定（低置信度决策）。
- 权限不足但用户可能授权。
- 动作不可撤销。
- 参数存在歧义，模型在"猜"。

用户介入不只是"同意/拒绝"二选一。完整的介入方式包括：确认执行、驳回动作、修改参数、编辑计划、要求解释、接管执行、回滚结果、补充信息。

### 6.3 确认界面和反馈闭环

高风险动作确认时，展示信息至少要包含：动作是什么、作用对象、影响范围、参数、是否可撤销、失败后怎么处理、为什么 Agent 建议执行。用户需要足够上下文才能判断，不能只给一个"是否允许？"的按钮。

用户反馈必须回到 Agent 状态：

```python
handle_user_feedback(state, feedback):
    # 将用户反馈写入状态，影响下一轮决策
    state.user_feedback = feedback
    state.history.append({step, type: "user_feedback", feedback})

    if feedback.type == "rejected":
        # 用户拒绝 → 记录原因，模型下一轮据此调整策略
        state.context_hint = "上轮被拒绝，原因：{reason}"
    elif feedback.type == "modified":
        # 用户修改了参数 → 用修改后的参数重新执行
        state.pending_action = {tool, arguments: modified_args}
    return state
```

如果用户反馈不进入状态，Agent 下一轮会基于旧上下文做出同样的决策，再次触发同一个确认——用户会觉得自己在和一个没有记忆的系统反复拉扯。

---

## 第七章：MCP —— 让工具接入标准化

### 7.1 当工具越来越多时会发生什么

前面几章假设工具是你在代码里手动定义和注册的。这在工具数量少（3-10 个）的时候没问题。但当工具数量增长、来源多样化时，新的问题出现了：
- 每个工具的接入方式不同（REST API、gRPC、数据库连接、本地函数）。
- 工具描述格式不统一（有些用 OpenAPI、有些用自定义 JSON、有些没文档）。
- 工具需要动态发现（今天有这个工具，明天可能下线了）。
- 不同 Agent 或应用需要复用同一组工具，但每个都要写一套集成代码。

这就像每买一个电器就需要重新装修一次插座——不可持续。

### 7.2 MCP 和 Function Calling 的分工

MCP（Model Context Protocol，2024 年由 Anthropic 发布）解决的就是"工具接入标准化"的问题。要理解它的定位，关键是把 MCP 和 Function Calling 分开：

| 概念 | 解决的问题 | 所在层 |
|---|---|---|
| Function Calling | 模型如何表达"我要调用哪个函数、参数是什么" | 模型接口层 |
| MCP | 工具服务如何被发现、描述、调用和复用 | 工具接入层 |

它们不是竞争关系，而是配合关系：MCP Server 暴露工具，Agent Runtime 通过这些标准接口发现和调用工具，然后把工具描述转成模型能理解的 Function Calling 格式，模型决策后 Runtime 通过 MCP 协议真正执行。

### 7.3 Tools / Resources / Prompts

MCP 定义了三种核心对象。下面通过一个完整的 MCP Server 定义示例来理解它们各自是什么：

```python
# MCP Server 定义示例：一个"文件管理"服务

server = Server("file_manager")

# 1. Tools — 可执行动作（有名称、描述、参数 Schema）
@server.tool()
def read_file(path: str) -> str:
    """读取 workspace 下的文本文件。当用户指定具体文件名时使用。"""

@server.tool()
def search_files(query: str, path: str) -> list:
    """搜索文件内容。当用户要求'找一下'、'有没有关于X的文件'时使用。"""

# 2. Resources — 可读取的数据资源（只读，通过 URI 访问）
@server.resource("docs://{name}")
def get_document(name: str) -> str: ...

@server.resource("config://app")
def get_app_config() -> dict: ...

# 3. Prompts — 可复用的提示模板（任务级，按需载入）
@server.prompt()
def code_review_template(diff: str) -> str:
    """代码审查模板，定义审查维度和输出格式。"""

# 启动：两种传输方式
server.run(transport="stdio")   # 本地子进程，适合开发调试
server.run(transport="http")    # HTTP + SSE，适合生产环境、多 Agent 共享
```

这个示例展示了 MCP Server 的全貌。注意两种传输方式的选择：

- **stdio**：Server 作为子进程启动，通过标准输入输出与 Client 通信。适合单机开发——简单、不需要网络配置，但 Server 生命周期绑定 Client 进程。
- **HTTP/SSE**：Server 作为独立 HTTP 服务运行，Client 通过 HTTP + Server-Sent Events 远程连接。适合生产环境——Server 可以独立部署、水平扩展、被多个 Agent 共享。

- **Tools**（`read_file`、`search_files`）：Agent 可以调用的可执行动作。每个 Tool 有名称、描述和参数 Schema（通过类型注解自动生成）。对应本课前面讨论的工具定义——MCP 把定义和执行放在了同一个 Server 里。

- **Resources**（`docs://{name}`、`config://app`）：Agent 可以读取的数据资源。Tool 执行动作，Resource 暴露数据。Resource 是只读的——Agent 可以通过 `docs://readme` 这样的 URI 读取文档，但不能修改它。

- **Prompts**（`code_review_template`）：可复用的提示模板。与 System Prompt 的区别在于：Prompt 是**任务级**的——Agent 在处理特定任务时按需载入，而不是始终存在于上下文中。

对 Agent 开发者来说，MCP 的价值是把"接入一个新工具"从"写一套集成代码"变成了"连接一个 MCP Server"。这个 Server 可以独立部署、独立更新、被多个 Agent 共享——就像编辑器通过 LSP 连接任意语言的语法服务一样。

#### 7.3.1 MCP Client：Agent 侧如何连接和调用

Server 定义了工具，Client 负责发现、连接和调用。下面是一个 MCP Client 在 Agent Runtime 中的使用示例：

```python
# MCP Client 的核心职责：连接 → 发现 → 注册 → 调用

class MCPToolProvider:
    clients: dict   # server_name → Client 连接
    tools: dict     # tool_name → {schema, callable}

    # ── 两种传输方式 ──
    connect_stdio(name, command, args):
        # 启动本地子进程，通过标准输入输出通信
        # 适用：单机开发，零网络配置

    connect_http(name, url):
        # 连接远程 HTTP Server，通过 SSE 维持通道
        # 适用：Server 独立部署，多 Agent 共享

    # ── 两种注册方式 ──
    discover_and_register(server, client):
        # 连接后调用 list_tools() 自动发现，动态注册
        # 优点：Server 更新工具后 Client 无需改代码

    register_static(server, url, tool_defs):
        # 提前声明工具 Schema，lazy connect（首次调用时才建立连接）
        # 优点：启动时不依赖 Server 在线

    # ── 调用 ──
    call_tool(server, tool, args):
        # 通过 MCP 协议调用远程工具，返回统一格式结果

# ── 在 Agent 循环中的使用 ──
provider = MCPToolProvider()
provider.connect_stdio("file_manager", "python", ["mcp_server.py"])
provider.connect_http("weather", "http://tools.internal:8090/sse")

# 所有工具合并为统一 Function Calling Schema → 模型看到的是统一列表
all_tools = {**provider.tools, **local_tools}
```

这个 Client 示例展示了 MCP 在 Agent 中的完整运作方式：

**两种传输方式：**
- `connect_stdio`：启动本地子进程，通过标准输入输出通信。适合开发调试——零网络配置。
- `connect_http`：连接远程 HTTP Server（通过 `/sse` 端点建立 Server-Sent Events 通道）。适合生产环境——Server 可以独立部署、被多个 Agent 共享、独立扩缩容。

**两种注册方式：**
- **动态发现**（`_discover_and_register`）：连接 Server 后调用 `list_tools()` 自动获取工具列表。Server 新增工具后 Client 无需改代码。缺点是必须先连上 Server 才知道有什么工具。
- **静态声明**（`register_static`）：注册时就清楚声明"这个 Server 提供哪些工具"，模型立即能看到 Schema，实际的 MCP 连接延迟到首次调用时建立。适合工具列表稳定、或 Server 可能暂时不可用的场景——Agent 启动时不需要等所有 Server 就绪。

**共同的底层原则：** 无论哪种传输方式、哪种注册方式，模型看到的永远是统一的 Function Calling 格式。MCP 的职责是标准化"接入"，而不是改变模型和工具的交互模型。

### 7.4 什么时候引入 MCP

适合引入 MCP 的场景：
- 工具来自多个外部服务，每个都有不同的接入方式。
- 多个 Agent 或应用需要复用同一组工具。
- 工具需要动态发现和热更新。
- 团队希望把工具服务独立部署和维护。

**不需要** MCP 的场景：
- 只有 2-3 个本地函数。（你在课程三和本课的练习中就是这个阶段）
- 工具边界还没稳定，还在频繁调整定义。
- 你还在学习最小闭环，不应该引入协议层复杂度。

本课引入 MCP 的目标不是让你立刻搭一套 MCP 体系，而是让你知道它在哪里、解决什么问题——当你的工具数量某天从 5 个变成 50 个时，你知道该往哪个方向走。

---

## 第八章：Skill —— 把重复任务沉淀成能力包

### 8.1 从"每次都重新想"到"把经验打包"

假设你发现 Agent 在执行"代码审查"任务时，总是按这个模式走：

```text
1. 读 git diff
2. 判断改动类型（新增/修改/删除）
3. 逐文件检查潜在 bug
4. 检查测试覆盖是否足够
5. 如果改动涉及关键路径，运行相关测试
6. 按严重程度组织 review 输出
```

每次任务模型都要把这几步重新"想"一遍，浪费 Token，而且偶尔会漏步骤。这就是 Skill 要解决的问题：**把稳定的工具组合和步骤经验打包成可复用的能力单元。**

Tool 解决"能做什么动作"（读文件、跑测试）。Skill 解决"如何完成一类任务"（代码审查、文档总结、数据分析）。两者的关系就像"螺丝刀"和"家具组装说明书"——前者是工具，后者告诉你用什么工具、什么顺序、遇到问题怎么处理。

### 8.2 Skill 的结构

一个 Skill 通常包含以下部分：

```python
CODE_REVIEW_SKILL = {
    name: "code_review"
    description: "审查 git diff，检查 bug、安全问题、测试覆盖和代码质量"
    when_to_use: "用户要求 review、审查代码、检查 PR 时"
    when_not_to_use: "用户只是询问代码含义、要求写新代码时"
    tools_needed: [read_file, run_shell, search_text]

    recommended_steps:
        1. git diff → 获取改动
        2. 判断改动类型和范围（新增/修改/删除，涉及哪些模块）
        3. 逐文件 read_file → 检查逻辑变更和边界条件
        4. search_text → 检查测试覆盖
        5. run_shell → 运行关键测试（仅当改动涉及关键路径）
        6. 按严重程度组织输出：Critical > Major > Minor > Suggestion

    failure_handling:
        git_diff_empty → "告知用户无改动，确认分支"
        test_not_found → "标记缺少测试覆盖，不阻塞流程"
        diff_too_large → "先摘要再分段审查"

    disabled_scenarios:
        - 不在无 git 仓库的目录使用
        - 不用于审查二进制文件
}
```

Skill 不是固定流程——模型可以根据实际情况决定是否完全遵循推荐步骤，还是根据上下文调整。这和 Workflow 的关键区别在于：Workflow 是"你必须按这个顺序走"，Skill 是"按经验你应该这样走，但你可以判断是否需要调整"。

### 8.3 Skill vs Tool vs Workflow

三者容易混淆，放在一起对比：

| 概念 | 本质 | 由谁决定执行 | 例子 |
|---|---|---|---|
| Tool | 原子动作 | Runtime 执行，模型选择 | `read_file`、`run_tests` |
| Skill | 可复用任务能力包 | 模型决定是否使用、如何调整 | 代码审查、文档总结 |
| Workflow | 固定执行流程 | 系统预设，不能跳过 | 提交 → 审批 → 发布 |

Skill 的边界：它应该让 Agent 更高效，但不能让用户和开发者失去控制。如果 Skill 内部隐藏了大量不可见的操作（比如悄悄修改了文件、静默发了通知），它就变成了一个黑箱陷阱。

## 课后练习

### 练习一：设计 5 个工具定义

为课程三的最小 Agent 扩展 5 个工具。每个工具写出：工具名、description（含适用和不适用场景）、参数 Schema（类型、约束、默认值）、返回值结构（成功和失败）、风险等级。

### 练习二：分析工具选择失败

设计 5 个用户任务，判断模型可能出现什么工具选择失败，并写出调试方向。至少覆盖：该用不用、不该用乱用、选错工具、参数猜错、重复调用。

### 练习三：实现带权限检查的工具执行器

参考 4.1 和 5.3 的代码，实现一个带参数校验、权限检查、超时和错误结构化的 `execute_tool_call` 函数。为至少 4 个工具配置 Deny-first 权限策略。

### 练习四：设计一个 Skill

选择一个常见任务（代码审查、文档总结、数据分析、竞品调研），设计一个完整的 Skill 定义。包含推荐步骤、失败处理、禁用边界。

### 练习五：设计 Human-in-the-loop 节点

为"Agent 根据用户输入生成并发送客户邮件"这个场景，设计确认节点：何时触发、展示什么信息、用户可以如何修改、拒绝后 Agent 怎么继续。

---

## 可运行示例

完成本课练习后，可以对照运行课程四的工具机制示例：

- [课程四工具机制示例](../examples/course-04-tool-mechanism/README.md)

该示例基于课程三的最小 Agent 闭环，补充了工具定义、参数 Schema、Deny-first 权限策略、工具执行器、结构化错误、结果截断、幂等重试和审计日志。示例同时提供 Python 和 Node.js 两个版本，便于对照理解 Runtime 如何把工具调用变成可控机制。

---

## 验收标准

- [ ] 我能画出工具调用完整链路，并标注工具选择、参数生成、执行、Observation、State Update 中的典型失败点。
- [ ] 我能为一个真实任务设计工具定义，包括 description、参数 Schema、返回结构、风险等级和适用边界。
- [ ] 我能诊断工具选择失败，区分是工具定义、候选集路由、上下文缺失还是模型判断错误。
- [ ] 我能实现一个受控工具执行器，覆盖参数校验、Deny-first 权限、超时、错误结构化、结果摘要和审计日志。
- [ ] 我能说明 MCP、Tool、Skill、Workflow 和 Human-in-the-loop 各自解决什么问题，并在具体场景中选择合适机制。

---

## 参考资料

- OpenAI Function Calling
  <https://platform.openai.com/docs/guides/function-calling>
- Anthropic Tool Use
  <https://docs.anthropic.com/en/docs/agents-and-tools/tool-use>
- Model Context Protocol
  <https://modelcontextprotocol.io/>
- Anthropic Building Effective Agents
  <https://www.anthropic.com/engineering/building-effective-agents>
