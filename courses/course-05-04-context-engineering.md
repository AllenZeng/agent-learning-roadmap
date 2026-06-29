# 第四章：Context Engineering —— 从"全塞进去"到"精准投喂"

[返回课程五主文档](./course-05-01-scenario-enhancement.md) | [上一章](./course-05-03-memory.md) | [下一章](./course-05-05-planning.md)

## 本章目录

- [4.1 "我明明写了要求，它为什么没看见"](#41-我明明写了要求它为什么没看见)
- [4.2 上下文是 Agent 唯一的"视野"](#42-上下文是-agent-唯一的视野)
- [4.3 上下文管线的三步法：分层、预算、选择](#43-上下文管线的三步法分层预算选择)
  - [4.3.1 分层：每类信息各就各位](#431-分层每类信息各就各位)
  - [4.3.2 预算：Token 不是无限的](#432-预算token-不是无限的)
  - [4.3.3 选择：超限时谁先出局](#433-选择超限时谁先出局)
- [4.4 工具输出：最容易被忽视的上下文杀手](#44-工具输出最容易被忽视的上下文杀手)
  - [4.4.1 为什么工具输出最容易爆炸](#441-为什么工具输出最容易爆炸)
  - [4.4.2 结果瘦身策略](#442-结果瘦身策略)
  - [4.4.3 代码骨架：可插拔的结果处理器](#443-代码骨架可插拔的结果处理器)
- [4.5 进化路线：从"全塞进去"到"精准投喂"](#45-进化路线从全塞进去到精准投喂)
- [4.6 上下文失败的六种典型症状与救治](#46-上下文失败的六种典型症状与救治)
- [4.7 什么时候不需要过度设计 Context Engineering](#47-什么时候不需要过度设计-context-engineering)
- [本章速记](#本章速记)
- [可运行示例](#可运行示例)

---

### 4.1 "我明明写了要求，它为什么没看见"

知识助手 Agent 已经接入了 RAG（第二章）和 Memory（第三章）。Notion 笔记能检索了，用户偏好也能跨会话记住了。一切看起来在变好。

然后你遇到了一个诡异的问题。

你给 Agent 的 System Prompt 里写了很清楚的约束：

```text
## 输出格式约束
- 始终使用中文回复
- 代码块标注语言
- 不确定时明确说"不确定"，不要猜测
- 回答末尾标注信息来源
```

某天你问了一个关于 Agent 架构的问题。Agent 检索了你的笔记，召回了偏好，开始回答。回答内容本身没问题——但它是英文的。Sources 也没标。

你翻看 trace，发现在第 3 步之后，模型的输出就偏离了 System Prompt 的约束。而 System Prompt 明明在上下文的最开头。

发生了什么？

**上下文太长了，关键约束被淹没了。**

在第 3 步，上下文里塞了这些东西：

- 系统提示词（1200 tokens）
- 用户目标（50 tokens）
- RAG 检索到的 3 个文档片段（共 4200 tokens）
- Memory 召回的 2 条偏好（300 tokens）
- 第 1 步的工具调用结果——一个 1500 行的日志文件（8000 tokens）
- 第 2 步的工具调用结果——代码库搜索结果（2500 tokens）
- 历史消息（1800 tokens）

总计约 18000 tokens。模型在第 15000 个 token 处做决策时，1200 tokens 之前的 System Prompt 约束在注意力机制中已经严重衰减。"使用中文回复"这条指令，模型"看见"了，但没有"注意到"。

这不是 RAG 的问题。不是 Memory 的问题。不是工具的问题。

**这是上下文管理的问题。** 当多个信息源同时向上下文注入内容，上下文不再是一个精心设计的信息结构，而是一个不断膨胀的信息堆。你往里面塞了所有"可能有用的东西"，但模型在里面迷路了。

### 4.2 上下文是 Agent 唯一的"视野"

先退一步，想清楚一个根本问题：**模型能看到什么？**

模型没有眼睛。没有耳朵。它看不到你的代码仓库，看不到你的数据库，看不到你的文件系统。它唯一能看到的东西，是你调用 API 时传进去的那一堆文本——**上下文（Context）**。

```text
模型的"世界" = 你传进去的上下文

模型不知道上下文之外有任何东西。
模型不会"想起来"你上次说过什么（除非在上下文里）。
模型不会"主动去查"什么（除非它决定调用工具，而工具结果又回到上下文里）。
```

上下文就是 Agent 的视野。视野有多大、有多清晰、信息组织得有多好，直接决定了 Agent 的决策质量。

而随着课程二到课程四引入的能力越来越多，上下文的信息源也在增加：

```text
V0（最小闭环）：
  上下文 = System Prompt + 用户消息 + 历史消息 + 工具结果

V1（接入 RAG）：
  上下文 = System Prompt + RAG 片段 + 用户消息 + 历史消息 + 工具结果

V2（接入 Memory）：
  上下文 = System Prompt + Memory 召回 + RAG 片段 + 用户消息 + 历史消息 + 工具结果

V3（接入 Planning）：
  上下文 = System Prompt + 执行计划 + Memory 召回 + RAG 片段 + 用户消息 + 历史消息 + 工具结果

每一步都在往上下文里加东西，但很少有人停下来问：
这些东西的组织方式还合理吗？
```

这引出了 Context Engineering 的核心命题：**不是"要不要往上下文里放东西"，而是"怎么有结构地放、怎么决定放多少、什么该放什么不该放"。**

Context Engineering 和 RAG、Memory 的关系是：

```text
RAG 负责"查什么"   ──→ 生产者
Memory 负责"记什么" ──→ 生产者
工具负责"执行什么"  ──→ 生产者（工具结果也是上下文的一部分）

Context Engineering 负责"怎么组织这些生产者的产出" ──→ 组织者
```

没有组织者，生产者越多越乱。这不是效率问题，是正确性问题——模型真的会"看不到"被淹没在上下文里的关键信息。

### 4.3 上下文管线的三步法：分层、预算、选择

Context Engineering 的核心方法论可以用三步概括：**分层、预算、选择**。

#### 4.3.1 分层：每类信息各就各位

不要把不同类型的信息混在一起扔给模型。用结构化的方式组织上下文，让模型能区分"这是规则"、"这是参考资料"、"这是当前状态"。

```text
┌─────────────────────────────────────────┐
│ Layer 0: System Prompt（行为定义）        │  ← 最高优先级，永不裁剪
│ - 角色、约束、输出格式、安全规则          │
├─────────────────────────────────────────┤
│ Layer 1: 用户目标 + 当前任务              │  ← 高优先级
│ - 用户原始消息、确认后的计划              │
├─────────────────────────────────────────┤
│ Layer 2: 参考资料（RAG + Memory）         │  ← 中优先级，内容相关
│ - 检索到的文档片段、召回的用户偏好        │
├─────────────────────────────────────────┤
│ Layer 3: 运行时状态                       │  ← 中优先级，动态变化
│ - 最近 N 步的工具调用与结果               │
├─────────────────────────────────────────┤
│ Layer 4: 历史消息                         │  ← 低优先级，摘要化
│ - 更早的消息用摘要代替原文                │
└─────────────────────────────────────────┘
```

每一层用明确的标记分隔，帮助模型的注意力机制定位信息：

```text
<system>
## 角色定义
你是个人知识助手……
## 行为约束
- 使用中文回复
- 不确定时明确说"不确定"
- 回答末尾标注来源
</system>

<user_goal>
帮我写一篇关于 Agent Context Engineering 的技术文章
</user_goal>

<reference>
## 相关笔记
[检索到的 3 篇笔记内容……]

## 用户偏好
- 技术文章先给大纲确认
- 语气直接，不要营销化
- 代码示例使用 Python
</reference>

<runtime_state>
## 当前进度
- 步骤 1/4：收集资料 ✅ 已完成
- 步骤 2/4：写大纲 ⏳ 等待用户确认

## 上一步工具输出摘要
文件搜索 "context window" 返回 12 个结果，其中 3 个相关：
1. context_engineering_notes.md - 上下文分层策略 (2.3K tokens)
2. llm_attention_mechanism.md - 注意力机制与上下文位置 (1.8K tokens)
3. production_context_pipeline.py - 上下文管线代码 (0.9K tokens)
</runtime_state>

<history_summary>
用户之前讨论了 Context Engineering 和 RAG 的区别。结论：RAG 是生产者，CE 是组织者。
</history_summary>
```

这种分层方式的核心价值不是"看起来整齐"，而是**让关键信息占据注意力的优势位置**。模型对上下文开头和结尾的信息关注度最高（"Lost in the Middle"效应）。把行为约束放在开头、当前任务放在紧随其后的位置，是最优的注意力分配。

#### 4.3.2 预算：Token 不是无限的

分层解决了"放在哪"的问题，预算解决"放多少"的问题。

即使模型支持 128K 或 200K token 的上下文窗口，你也不应该填满。原因：

1. **注意力衰减**：上下文越长，模型对中间位置的关注度越低。100K token 不等于"100K 都有效"。
2. **延迟和成本**：上下文越长，每次调用越慢、越贵。每多 1000 token，延迟和成本都在增加。
3. **约束稀释**：System Prompt 的约束在长上下文中被大量中间内容稀释。

给每一层设定 Token 预算：

| 层 | 预算（token） | 说明 |
|---|---|---|
| System Prompt | 1000-2000 | 核心约束，不参与裁剪 |
| 用户目标 + 计划 | 500-1000 | 保持完整 |
| RAG 结果 | 2000-4000 | 按相关性截断，标注截断点 |
| Memory 召回 | 500-1000 | 只召回最相关的 3-5 条 |
| 工具结果（最近 N 步） | 3000-5000 | 对长结果做摘要后再放入 |
| 历史消息 | 2000-3000 | 早期消息用摘要替代 |
| **总计** | **约 10000-16000** | 远低于模型上限，但信息密度高 |

预算分配要跟着任务类型走。代码审查任务的工具输出预算应该更大（需要看代码），知识问答任务的 RAG 预算应该更大。

#### 4.3.3 选择：超限时谁先出局

预算定了，但实际运行时还是会超。工具返回了一个 10000 行的日志，RAG 召回了 20 个片段。必须做选择。

选择的核心原则：**按"模型决策对该信息的依赖程度"排序。**

```text
裁剪优先级（从先裁到后裁）：

1. 最早的工具输出 → 用摘要替代原文
   "步骤 2 的文件读取返回了 config.py，内容已记录在状态中"

2. 相关性低的 RAG 片段 → 丢弃
   保留 score > 阈值的片段

3. 早期历史消息 → 用摘要替代
   "前 5 轮对话讨论了 X，结论是 Y"

4. Memory 召回 → 只保留用户明确设定的偏好
   丢弃自动推断的、置信度低的记忆

永远不裁：
- System Prompt 的核心约束
- 用户当前消息
- 当前任务的执行计划
```

这里有一个重要的设计选择：**裁剪逻辑应该放在"注入上下文之前"，而不是放在"模型已经读了上下文之后"。** 上下文一旦进入模型的注意力窗口，就已经产生了计算成本和注意力稀释。在注入之前做选择，是对 Token 预算的主动管理，而不是事后的被动截断。

### 4.4 工具输出：最容易被忽视的上下文杀手

#### 4.4.1 为什么工具输出最容易爆炸

在所有上下文污染源中，工具输出是破坏力最强的。原因很简单：**你无法控制工具输出的大小。**

- System Prompt 是你写的，长度可控。
- RAG 结果是你检索的，你可以只取 top-K。
- Memory 召回是你控制的，你可以设置数量上限。

但工具输出——你让 Agent 读一个文件，它可能是 50 行，也可能是 5000 行。你让它搜索代码库，可能返回 3 个结果，也可能返回 300 个。你让它跑一个命令，stdout 可能只有一行，也可能有几万行。

而且工具输出一旦进入上下文，就会成为下一轮 LLM 调用的输入。模型基于这些（可能无用、可能过时、可能误导的）信息做下一步决策。一个臃肿的工具输出不仅浪费 Token，更危险的是——它可能引导模型在无关信息上钻牛角尖。

回到 1.1 的场景：Agent 读到 README 里的一个技术细节后，偏离了"发布准备"的目标。这就是工具输出污染上下文的经典案例。

#### 4.4.2 结果瘦身策略

不同工具需要不同的瘦身策略：

**策略一：截断 + 标注（适合文件读取、日志查看）**

```text
原始输出：1500 行日志
处理后：
[前 50 行]
……
[日志中间 1350 行已省略，包含 23 条 INFO、5 条 WARNING]
……
[后 50 行]
总计 1500 行，已显示首尾各 50 行。如需查看完整日志，请指定行号范围。
```

关键：截断后必须标注"截断了什么"和"如何获取剩余内容"。否则模型可能基于不完整信息做错误推断。

**策略二：提取 + 摘要（适合代码搜索、文档检索）**

```text
原始输出：grep 返回 120 个匹配结果
处理后：
搜索 "context window" 在 8 个文件中找到 120 处匹配。按文件分组：

1. src/context/builder.py - 15 处匹配（上下文构建主文件）
   L42: def build_context(layers: List[ContextLayer]) -> str:
   L78: window_budget = self.calculate_budget(model_max_tokens)
   L156: truncated = self.truncate_by_priority(layers, remaining)

2. src/context/compressor.py - 8 处匹配（上下文压缩）
   L23: class ContextCompressor:
   L45: def compress_tool_output(self, output: str, max_tokens: int):

3-8. [其他 6 个文件共 97 处匹配，涉及测试和配置文件]
   使用 "grep -n 'context window' <file>" 查看具体行
```

关键：结构化呈现搜索结果，让模型能快速定位最相关的文件，而不是迷失在 120 行 grep 输出里。

**策略三：结构化 + 过滤（适合 API 调用、数据库查询）**

```text
原始输出：API 返回 200 条用户记录（JSON，每条 20 个字段）
处理后：
查询返回 200 条记录。按状态分组：
- active: 142 条
- inactive: 43 条
- suspended: 15 条

最近 5 条 active 记录的关键字段：
| id | name | email | last_login |
|----|------|-------|------------|
| 1  | ...  | ...   | ...        |

完整数据已写入临时文件 /tmp/query_result_20260629.json
需要进一步分析时，使用 read_file 工具读取指定字段。
```

关键：不要让模型"记住"大量结构化数据。保留摘要和索引，把完整数据放到模型可以通过工具再次访问的地方。

#### 4.4.3 代码骨架：可插拔的结果处理器

不为每种工具写死处理逻辑。用一个可插拔的结果处理器，按工具注册不同的处理策略：

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class ProcessedResult:
    """处理后的工具输出"""
    content: str                # 注入上下文的内容
    original_size: int          # 原始大小（tokens）
    processed_size: int         # 处理后大小（tokens）
    truncated: bool             # 是否被截断
    truncation_note: Optional[str]  # 截断说明（供模型理解）

class ResultProcessor(ABC):
    """工具输出处理器基类"""
    @abstractmethod
    def process(self, raw_output: str, max_tokens: int) -> ProcessedResult:
        ...

class FileReadProcessor(ResultProcessor):
    """文件读取：保留首尾，中间截断"""
    def process(self, raw_output: str, max_tokens: int) -> ProcessedResult:
        lines = raw_output.split("\n")
        if len(lines) <= 100:
            return ProcessedResult(
                content=raw_output,
                original_size=len(raw_output),
                processed_size=len(raw_output),
                truncated=False
            )
        head = "\n".join(lines[:50])
        tail = "\n".join(lines[-50:])
        content = f"{head}\n……\n[中间 {len(lines) - 100} 行已省略]\n……\n{tail}"
        return ProcessedResult(
            content=content,
            original_size=len(raw_output),
            processed_size=len(content),
            truncated=True,
            truncation_note=f"文件共 {len(lines)} 行，已显示首尾各 50 行"
        )

class SearchResultProcessor(ResultProcessor):
    """搜索结果：结构化分组摘要"""
    def process(self, raw_output: str, max_tokens: int) -> ProcessedResult:
        # 分组、去重、按文件聚合……
        # 返回结构化的搜索结果摘要
        ...

class GenericProcessor(ResultProcessor):
    """通用处理器：简单截断"""
    def process(self, raw_output: str, max_tokens: int) -> ProcessedResult:
        if len(raw_output) <= max_tokens * 4:  # 粗略估算 1 token ≈ 4 chars
            return ProcessedResult(
                content=raw_output,
                original_size=len(raw_output),
                processed_size=len(raw_output),
                truncated=False
            )
        truncated = raw_output[: max_tokens * 4]
        return ProcessedResult(
            content=f"{truncated}\n\n[输出已截断，原始长度 {len(raw_output)} 字符]",
            original_size=len(raw_output),
            processed_size=len(truncated),
            truncated=True,
            truncation_note=f"输出超出限制，已截断至约 {max_tokens} tokens"
        )

# 注册处理器
result_processors = {
    "read_file": FileReadProcessor(),
    "search_codebase": SearchResultProcessor(),
    # 未注册的工具使用 GenericProcessor
}
default_processor = GenericProcessor()

def process_tool_output(tool_name: str, raw_output: str, max_tokens: int) -> ProcessedResult:
    """对工具输出进行处理后再注入上下文"""
    processor = result_processors.get(tool_name, default_processor)
    return processor.process(raw_output, max_tokens)
```

这个骨架的核心设计思路：

1. **每种工具独立处理逻辑**：文件读取和代码搜索的输出形态完全不同，不能一刀切
2. **处理结果透明**：告诉模型"原始大小、处理后大小、是否截断"，模型需要这些元信息来做判断
3. **截断说明是给模型看的**：`"文件共 1500 行，已显示首尾各 50 行"`——模型知道信息不完整，它会决定是继续基于现有信息回答，还是调用工具获取更多内容

### 4.5 进化路线：从"全塞进去"到"精准投喂"

Context Engineering 不需要一步到位。和所有增强能力一样，它也应该从最小版本开始迭代：

| 阶段 | 做了什么 | 适用场景 |
|---|---|---|
| **V0：全塞进去** | 所有信息原封不动注入上下文，超限时用 tokenizer 截断 | 原型验证、单步简单任务 |
| **V1：加个预算** | 给每类信息设定最大 token 数，超出时简单截断 | 信息源不超过 3 个的原型 |
| **V2：工具输出处理** | 为高频工具注册专门的结果处理器，长输出先压缩 | 工具调用频繁、输出容易爆炸 |
| **V3：分层 + 优先级** | 上下文结构化分层，超限时按优先级裁剪而非简单截断 | 信息源 3+ 个，任务多步骤 |
| **V4：动态预算 + 去重** | 根据任务类型动态调整各层预算；RAG 和 Memory 的结果去重 | 生产环境，多种任务类型 |
| **V5：上下文效果评测** | 对上下文组装策略做 A/B 评测，量化不同策略对任务完成率的影响 | 持续优化的生产系统 |

大多数项目的合理目标是 **V3**。V4 和 V5 适合上下文质量直接影响核心指标的产品。

一个重要的经验法则：**每当你往上下文里加一个新信息源，同时就加一段处理逻辑。** 不要只加生产者，不加组织者。

### 4.6 上下文失败的六种典型症状与救治

| 症状 | 底层原因 | 救治方向 |
|---|---|---|
| **约束遗忘**：模型违反 System Prompt 中的明确约束 | 约束在长上下文中被后续内容"淹没" | 将关键约束放在上下文末尾重复一次；缩短上下文；提高约束所在的 Layer 优先级 |
| **中间迷失**：模型对上下文中间的信息视而不见 | "Lost in the Middle"效应——注意力对中间位置衰减最严重 | 将关键信息放在开头或结尾；对中间内容做摘要前移 |
| **工具结果中毒**：模型被一次无关的工具输出引导跑偏 | 工具输出未经过滤直接注入，占据大量注意力 | 为工具输出注册处理器；设定单次工具输出的 Token 上限 |
| **信息冲突**：RAG 片段和 Memory 召回给出了矛盾的偏好 | 不同信息源缺乏去重和冲突解决 | 加入去重逻辑；当信息冲突时优先采用时间戳更新的、或来源更权威的 |
| **上下文膨胀**：每轮都追加工具结果，上下文逐渐逼近上限 | 历史工具输出未被压缩或淘汰 | 对超过 N 步的工具输出做摘要替换；设置上下文使用率告警阈值（如 70%） |
| **重复注入**：同一条知识同时出现在 RAG 结果和 Memory 中 | 信息源之间缺乏协调 | 在 Context Assembly 阶段做跨源去重；相同内容优先使用来源质量更高的版本 |

这些症状不会同时出现，但几乎每个从原型向生产演进的 Agent 项目都会遇到其中 2-3 个。

### 4.7 什么时候不需要过度设计 Context Engineering

Context Engineering 也遵循"按需引入"原则。以下情况不需要复杂的设计：

1. **单步简单任务**：用户问一句、模型答一句，没有工具调用、没有多轮历史。直接传 System Prompt + 用户消息就够了。
2. **信息源单一**：只有 System Prompt 和用户消息，没有 RAG、Memory、工具输出。没有"组织"的需求。
3. **上下文远低于模型上限**：总 Token 数不到模型上限的 30%，且任务简单。过度设计上下文管线是浪费。
4. **原型验证阶段**：还在验证"这个方向能不能 work"。V0 的"全塞进去"完全可以接受。

一个判断信号：**当你发现自己开始在 System Prompt 里写"请务必遵守第 X 条规则"时，说明上下文已经长到模型需要被"提醒"才能记住约束了。这是该引入 Context Engineering 的信号。**

### 本章速记

> 上下文是 Agent 唯一的视野。RAG 和 Memory 是信息的生产者，Context Engineering 是信息的组织者——分层决定"放在哪"，预算决定"放多少"，选择决定"谁出局"。工具输出是最容易被忽视的上下文杀手，需要为高频工具注册专门的结果处理器。进化从"全塞进去"开始，以"精准投喂"为目标，但大多数项目停在 V3（分层+优先级）就够了。当你开始在 Prompt 里写"请务必遵守第 X 条规则"时，就该引入 Context Engineering 了。

### 可运行示例

完整可运行代码见 `examples/course-05-04-context-engineering/`，包含：
- 上下文分层构建器
- Token 预算管理器
- 可插拔的工具输出处理器（FileRead、Search、Generic）
- 优先级裁剪器

运行方式：
```bash
cd examples/course-05-04-context-engineering
python demo.py
```
