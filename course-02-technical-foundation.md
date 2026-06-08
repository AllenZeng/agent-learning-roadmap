# 阶段二：技术基础 —— 构建Agent的四大支柱

> **学时**：3-6周 | **难度**：中级 | **先修要求**：Python基础、HTTP协议、基本的机器学习概念
>
> **课程导语**：如果说阶段一是让你"看见"Agent，那么阶段二就是让你"看懂"Agent。我们将深入Agent的底层技术栈，从LLM的运作原理开始，到工具调用、知识检索、提示工程，逐一拆解。每一个技术点，我们都会追问三个问题：它解决了什么痛点？设计者是怎么想到的？未来会走向何方？

---

## 目录

1. [第一课：LLM原理——Agent的大脑](#第一课llm原理agent的大脑)
   - 1.1 Transformer架构
   - 1.2 Tokenization（分词）
   - 1.3 Context Window（上下文窗口）
   - 1.4 Temperature、Top-p、Top-k等采样策略
2. [第二课：Tool Use深入](#第二课tool-use深入)
   - 2.1 从文本生成到工具调用
   - 2.2 ReAct模式详解
3. [第三课：RAG——给Agent接入知识](#第三课rag给agent接入知识)
   - 3.1 RAG的演进历史
   - 3.2 Embedding与向量检索
   - 3.3 Chunking策略
4. [第四课：Prompt Engineering](#第四课prompt-engineering)
   - 4.1 System Prompt设计
   - 4.2 Few-shot Prompting
   - 4.3 Chain-of-Thought
   - 4.4 结构化输出
5. [第五课（桥梁项目）：文件整理Agent](#第五课桥梁项目文件整理-agent--从单次调用到多步自主)

---

## 阶段概览

### 🎯 学习目标

完成本阶段后，你将能够：
1. 理解 Transformer 的核心机制（Self-Attention、Multi-Head Attention），并解释为什么它适合作为 Agent 的基础模型
2. 掌握 Tokenization 对工具调用的影响，能在设计工具时做出正确的命名和描述决策
3. 理解上下文窗口的工作原理和"Lost in the Middle"现象，能制定有效的上下文管理策略
4. 独立实现一个基于 ReAct 模式的 Agent，支持 3+ 个工具
5. 搭建一个 RAG 检索系统，理解 Embedding、向量检索、Chunking 的全链路
6. 写出结构清晰、行为可控的 System Prompt

### 📥 前置输入

- 已完成阶段一的认知学习（理解 Agent vs Workflow 的区别）
- 熟悉 Python，能独立完成函数编写和 API 调用
- 有 OpenAI API Key 或 Anthropic API Key
- 安装了 Python 3.10+ 及必要的开发工具

### 🏋️ 练习任务

1. **ReAct Agent 实现**：从零实现一个 ReAct Agent 循环，不依赖 LangChain 等高级框架
2. **RAG 系统搭建**：构建一个能检索本地文档并回答问题的 RAG 系统
3. **Prompt 迭代**：对同一个 Agent，写 3 个版本的 System Prompt，对比行为差异
4. **最小评测集**：为你的 Agent 准备 10 条测试任务，记录每次的成功/失败

### 📦 交付物

1. 一个 CLI Agent，支持 search（搜索知识库）、read_file（读取本地文件）、calculator（计算器）3 个工具
2. 一份 RAG 系统设计文档（包含 chunk 大小选择、embedding 模型选择、检索策略的理由）
3. 一份 Prompt 迭代记录（3 个版本的 System Prompt + 行为对比）
4. 一份评测集（10 条任务）和实测结果

### ✅ 验收标准

- Agent 能正确选择工具（tool selection 准确率 ≥ 70%）
- 10 条测试任务中成功完成 ≥ 7 条
- 能解释每次失败的原因，并按 tool selection / prompt / schema / 上下文管理分类
- RAG 系统的检索 Top-5 召回率 ≥ 60%（在自己的文档集上测试）
- System Prompt 的第三版比第一版有明显改进（用评测集验证）

---

## 第一课：LLM原理——Agent的大脑

如果把Agent比作一个人，那么LLM就是它的大脑。大脑能不能思考清楚、能不能记住足够多的上下文、能不能稳定地做决策，直接决定了这个Agent的上限。在动手搭建Agent之前，我们必须先理解这个"大脑"的运作机制。

### 1.1 Transformer架构

#### 1.1.1 史前时代：RNN/LSTM的困境

2017年之前，序列建模就是RNN（及其变体LSTM、GRU）的天下。RNN的核心思想很朴素：处理序列数据时，每一步的输出不仅取决于当前输入，还取决于上一步的"记忆"。

```
时间步:  t=1        t=2        t=3        t=4
输入:   "我"       "爱"       "吃"       "苹果"
         |          |          |          |
         v          v          v          v
       [RNN] --> [RNN] --> [RNN] --> [RNN]
         |          |          |          |
       h1         h2         h3         h4
```

这个架构有三个让人头疼的问题：

**问题一：长距离依赖丢失。** 序列开头的"我"和结尾的"苹果"之间隔着3个时间步，RNN要在每个时间步压缩信息。步数一多（比如翻译一篇200词的文章），早期的信息就会被逐步"稀释"。LSTM引入了门控机制试图缓解这个问题，但治标不治本——它只是在"选择性遗忘"和"选择性记忆"上做了优化，信息瓶颈的本质没有改变。

**问题二：无法并行训练。** RNN是逐时间步计算的，t=3必须在t=2完成之后才能开始。在GPU上训练时，你看着那99%的计算单元闲置着等前面的时间步算完，心里只有一个字：急。

**问题三：梯度消失/爆炸。** 反向传播时，梯度沿着时间步连乘。如果每一步的梯度都小于1（这是常态），连乘100步之后梯度就趋近于0了——这就是梯度消失。反过来就是梯度爆炸。虽然LSTM和梯度裁剪能缓解，但这些"补丁"让模型越来越复杂，离优雅越来越远。

#### 1.1.2 思想转折：Attention机制的诞生

Bahdanau等人在2014年提出了一个关键洞察：**解码器在每个时间步不需要看到编码器的全部输出，只需要关注（attend to）当前最相关的部分。** 这就是Attention的雏形。

举个例子，翻译下面这句话：

```
源语言: The cat sat on the mat
目标语言: 猫 坐 在 垫子 上
```

在生成"猫"的时候，模型应该高度关注源句中的"cat"；生成"垫子"的时候，应该关注"mat"。Attention机制通过计算一个"相关性权重"，让模型学会了**动态地、有选择地**使用输入信息。

#### 1.1.3 革命时刻："Attention Is All You Need"（2017）

Google Brain团队的Vaswani等人在2017年发表了一篇论文，标题就带着一股自信——"Attention Is All You Need"。核心思想大胆到近乎叛逆：**把RNN/LSTM的循环结构全部扔掉，只用Attention机制来建模序列关系。**

这个决策背后的推理链条值得品味：

1. RNN的循环结构是为了"按顺序"处理序列——这是人的直觉，但不一定是机器的需要。
2. 既然Attention已经能建模任意两个位置之间的依赖，为什么还需要循环结构来"传递"信息？
3. 去掉循环结构后，所有位置可以**同时计算**（并行化），而且任意两个位置之间的路径长度都是O(1)（不管"我"和"苹果"之间隔了多远，Attention都能直接看到）。

于是有了这个让无数研究者和工程师深夜啃论文的架构图：

```
                    +----------+
                    |  Output  |
                    +----+-----+
                         |
              +----------+-----------+
              |   Add & LayerNorm    |
              +----------+-----------+
                         |
              +----------+-----------+
              |  Feed-Forward Network|
              +----------+-----------+
                         |
              +----------+-----------+
              |   Add & LayerNorm    |
              +----------+-----------+
                         |
              +----------+-----------+
              |  Multi-Head Attention|
              +----------+-----------+
                         |
              +----------+-----------+
              |   Add & LayerNorm    |
              +----------+-----------+
                         |
              +----------+-----------+
              | Masked Multi-Head    |
              |    Attention         |
              +----------+-----------+
                         |
                    [Input Embedding]
                    [Positional Encoding]
```

#### 1.1.4 核心组件逐一拆解

**Self-Attention：让每个词"看到"所有词**

传统RNN中，"苹果"只能通过中间步骤间接地感知到"我"。Self-Attention直接计算"苹果"和"我"之间的相关性：

```
句子: "我 爱 吃 苹果"

Step 1: 为每个词生成 Q(Query), K(Key), V(Value) 三个向量
        我  --> Q1, K1, V1
        爱  --> Q2, K2, V2
        吃  --> Q3, K3, V3
        苹果 --> Q4, K4, V4

Step 2: 计算Attention分数（以"苹果"为例）
        score(苹果, 我)  = Q4 · K1
        score(苹果, 爱)  = Q4 · K2
        score(苹果, 吃)  = Q4 · K3
        score(苹果, 苹果) = Q4 · K4

Step 3: Softmax归一化
        weight_i = softmax(score_i / sqrt(d_k))

Step 4: 加权求和得到"苹果"的上下文表示
        output_苹果 = w1*V1 + w2*V2 + w3*V3 + w4*V4
```

这个设计的精妙之处在于：**Query代表"我在找什么"，Key代表"我拥有什么信息"，Value代表"我提供什么内容"。** Q和K的点积衡量匹配程度，然后用这个匹配度去加权V。整个过程完全可微，可以端到端训练。

**Multi-Head Attention：多个"视角"同时关注**

单头Attention就像一个只有一只眼睛的人——只能从一种角度观察世界。Multi-Head Attention给了模型多双"眼睛"，每双眼睛关注不同类型的关系：

```
输入向量 (d_model=512)
    |
    +--> Head 1 (d_k=64): 可能关注"语法关系"（主语-谓语）
    +--> Head 2 (d_k=64): 可能关注"指代关系"（代词-名词）
    +--> Head 3 (d_k=64): 可能关注"语义关系"（同义词、相关词）
    +--> ...
    +--> Head 8 (d_k=64): 可能关注"位置关系"（邻近词）
    |
    +--> 拼接8个Head的输出，线性投影回512维
```

这也是"Attention Is All You Need"标题背后的底气：不需要额外的语法分析器、不需要依存句法树，模型自己学会了在多个层次上理解语言。

**Positional Encoding：给无序的Attention注入位置信息**

Self-Attention最大的"缺陷"是：它对词的顺序完全无感。"我爱你"和"你爱我"对Self-Attention来说，计算出的Attention矩阵只是行列交换了一下，核心信息没有位置依赖。Transformer用了一个巧妙的方法——直接用三角函数给每个位置生成唯一的编码：

```
PE(pos, 2i)   = sin(pos / 10000^(2i/d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))

其中pos是位置，i是维度索引
```

为什么选三角函数？因为 **sin(α+β) = sinα·cosβ + cosα·sinβ**，这意味着位置pos+k的编码可以通过pos的编码线性变换得到。模型因此能很容易地学习到"相对位置"这个概念。

#### 1.1.5 为什么Transformer特别适合做Agent的基础模型？

Agent需要的能力和Transformer的优势几乎是天作之合：

| Agent需求 | Transformer优势 |
|-----------|----------------|
| 理解复杂的指令和上下文 | Self-Attention捕捉任意距离的依赖 |
| 在多个工具调用之间保持上下文一致性 | 全局感受野，不会遗忘早期信息 |
| 高效推理（延迟敏感） | 推理时可以并行计算（训练时并行是自然的，推理时KV Cache也让逐token生成足够快） |
| 多模态扩展（看图、看代码） | 架构统一，可以轻松扩展为Vision Transformer等变体 |
| 大规模训练 | 高度可并行化，充分利用GPU集群 |

---

### 1.2 Tokenization（分词）

#### 1.2.1 之前：词级别分词的问题

在BPE等子词分词方法出现之前，主流做法是**词级别分词**：把文本按空格和标点切开，每个词给一个ID。这看起来天经地义，毕竟"词"是人类理解语言的自然单位。

但这个方法有两个致命缺陷：

**OOV（Out-of-Vocabulary，未登录词）问题**。不管你收集多大的词表（10万？50万？），总会遇到新词。人名、地名、新造的网络用语、特定领域的术语——这些词不在词表里，模型就完全无法处理。当时的解决方案是全部替换成`<UNK>`（unknown token）：

```
输入: "我今天去了海淀区学量子力学"
分词: [我, 今天, 去, 了, <UNK>, 学, <UNK>]
```

"海淀区"不见了，"量子力学"也消失了——信息被粗暴丢弃。

**词表爆炸**。英语中同一个词的不同形态（run, runs, running, ran）被视为不同词。如果把所有形态都收入词表，词表大小会迅速膨胀。更大的词表意味着更大的Embedding矩阵、更多的参数、更慢的训练。

#### 1.2.2 BPE（Byte Pair Encoding）的诞生

BPE最早是1994年Gage提出的数据压缩算法。Sennrich等人在2016年将其引入NLP，用于解决机器翻译中的罕见词问题。它的核心思想极为简洁：

```
BPE训练过程：
1. 初始化词表：所有独立字符（比如英语就是26个字母+标点）
2. 统计所有相邻token对的频率
3. 找出最高频的pair，将其合并为一个新token
4. 重复步骤2-3，直到达到目标词表大小
```

用一个具体例子演示：

```
语料: "low low low low low lower lower"
字符级: l o w _ l o w _ ... (每个字符是独立token)

第1轮: 统计相邻对，("l","o")出现频率最高
       合并 → "lo" 成为新token
       文本变为: lo w _ lo w _ lo w _ lo w _ lo w _ lo w er _ lo w er _

第2轮: 统计相邻对，("lo","w")出现频率最高
       合并 → "low" 成为新token
       文本变为: low _ low _ low _ low _ low _ low er _ low er _

第3轮: 统计相邻对，("low","_")出现频率最高
       合并 → "low_" 成为新token
       ...

最终词表: l, o, w, _, e, r, lo, low, low_, er, ...
```

这个算法带来的变化是革命性的：
- **不再有OOV**：最差情况退回到字符级别（所有字符都在词表里），不会丢失任何信息
- **高频词保持完整**："the"、"and"等高频词在BPE训练中会被完整保留
- **罕见词被拆成有意义的部分**："unhappiness" → "un" + "happi" + "ness"，前缀、词根、后缀天然分离
- **词表大小可控**：通过控制合并轮数，精确控制词表大小

#### 1.2.3 Tokenization如何影响Agent的工具调用？

这是Agent开发中的一个隐蔽陷阱。考虑以下场景：

```
Agent判定需要调用工具: get_weather_forecast(city="San Francisco", days=7)

但tokenizer把工具名拆分成了:
["get", "_", "we", "ather", "_", "fore", "cast"]

或者用中文工具名:
"搜索天气" → ["搜", "索", "天", "气"]  (每个汉字可能是一个独立token!)
```

当工具名被过度拆分时，LLM需要在多个token之间"记住"完整的工具名称。这增加了模型正确调用工具的难度——它可能在生成到一半时"忘记"自己在调用哪个工具。这也是为什么很多工具调用方案建议**工具名使用下划线分隔的英文短词**（如`search_weather`而非`getWeatherForecastForCity`）：BPE能有效处理的模式就是这种由高频子词组成的结构。

#### 1.2.4 为什么中英文tokenization效率差距那么大？

这是一个值得深思的问题。以GPT-4的tokenizer（cl100k_base）为例：

```
英文: "The weather is nice today"  →  约5个token（每个词约1个token）
中文: "今天天气很好"                →  约8-12个token（每个汉字1-2个token）
```

**根本原因**：
1. 英文天然有空格分隔，高频词在BPE过程中很快被合并为完整token。
2. 中文没有空格，且Unicode中每个汉字都是独立字符。BPE从一个字节开始合并，中文需要经过更多轮才能形成有意义的子词。
3. 常用的中文tokenizer词汇表（50K-100K）中，中文字符的覆盖率远低于英文词根。导致大量汉字停留在2-3字节/字符的水平。

**实际影响**：
- 同样的内容，中文消耗的token数是英文的1.5-3倍
- API调用成本更高（按token计费）
- 上下文窗口中能容纳的中文信息更少
- 结构化输出（JSON key通常用英文）在中文上下文中可能被干扰

---

### 1.3 Context Window（上下文窗口）

#### 1.3.1 从1024到200万的进化

上下文窗口（Context Window）指的是LLM在一次推理中能"看到"的最大token数量。这不是一个技术参数，而是一个**能力边界**——Agent的"工作记忆"容量。

```
时间线：

2019 GPT-2:     1,024 tokens   ≈ 一篇短文的长度
2020 GPT-3:     2,048 tokens   ≈ 一篇长文章
2022 GPT-3.5:   4,096 tokens   ≈ 一个短章节
2023 GPT-4:     8,192 tokens   ≈ 一篇中篇小说
2023 GPT-4-32K: 32,768 tokens  ≈ 一本小册子
2023 Claude 2:  100K tokens    ≈ 《了不起的盖茨比》
2023 GPT-4-128K:128K tokens   ≈ 一部长篇小说
2024 Gemini 1.5:1M tokens     ≈ 《战争与和平》×2
2024 Claude 3:  200K tokens
2024 Gemini 1.5:2M tokens     ≈ 三部《战争与和平》
```

#### 1.3.2 为什么上下文窗口对Agent至关重要？

Agent的执行过程是一个**不断往上下文中追加内容**的过程：

```
┌─────────────────────────────────────────────────┐
│                Context Window                    │
│  ┌───────────────────────────────────────────┐  │
│  │ System Prompt (角色、规则、工具列表)        │  │
│  │ ≈ 500-2000 tokens                         │  │
│  ├───────────────────────────────────────────┤  │
│  │ User Query (用户的问题)                    │  │
│  │ ≈ 100-500 tokens                          │  │
│  ├───────────────────────────────────────────┤  │
│  │ Tool Call 1 (工具调用请求)                 │  │
│  │ ≈ 50-200 tokens                           │  │
│  ├───────────────────────────────────────────┤  │
│  │ Tool Result 1 (工具返回结果)               │  │
│  │ ≈ 500-5000 tokens (可能很长!)              │  │
│  ├───────────────────────────────────────────┤  │
│  │ Tool Call 2 ...                           │  │
│  ├───────────────────────────────────────────┤  │
│  │ Tool Result 2 ...                         │  │
│  ├───────────────────────────────────────────┤  │
│  │ ... (重复N次)                              │  │
│  ├───────────────────────────────────────────┤  │
│  │ Thinking & Final Answer                   │  │
│  │ ≈ 500-2000 tokens                         │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

假设一个Agent执行了5次工具调用，每次返回2000 tokens的结果：
- System prompt: 1000
- 用户问题: 300
- 5次工具调用+结果: 5 × (100 + 2000) = 10,500
- 推理+最终回答: 1000
- **总计: 约12,800 tokens**

这就是为什么GPT-3.5的4096 tokens窗口在Agent场景中捉襟见肘——用完两三个工具就可能溢出。

#### 1.3.3 上下文窗口的代价：O(n²)注意力

Self-Attention的计算复杂度是O(n²)的，其中n是序列长度。这意味着：

```
序列长度翻倍 → 注意力计算量翻4倍
序列长度10倍 → 注意力计算量翻100倍

具体来说：
1K tokens   → 需要计算约100万个注意力对
128K tokens → 需要计算约160亿个注意力对
1M tokens   → 需要计算约1万亿个注意力对
```

这也是为什么大上下文窗口的模型虽然存在，但**推理延迟和成本都会显著增加**。学术界和工业界在不断探索降低复杂度的方法（如FlashAttention、Ring Attention、稀疏注意力等），但物理上的计算量增长是绕不开的。

#### 1.3.4 Lost in the Middle现象

2023年，Liu等人的论文《Lost in the Middle》揭示了一个令人不安的发现：**语言模型对上下文中间位置的信息关注度显著低于开头和结尾。** 这就像一个学生考试，认真看了第一页和最后一页，中间的内容却一扫而过。

```
信息检索准确率随位置变化的U型曲线：

准确率
  │
  │  ████                          ████
  │  ████                          ████
  │  ████                          ████
  │  ████                          ████
  │  ████         ████             ████
  │  ████         ████             ████
  │  ████    ██   ████    ██       ████
  │  ████   ████  ████   ████      ████
  └──+----+----+----+----+----+----+---
     0%   20%  40%  60%  80%  100%
           文档中信息的相对位置
```

**对Agent的启示**：
1. 把最关键的信息（任务目标、当前状态）放在开头或结尾
2. 工具调用结果太长时，考虑在开头加一个简短的摘要
3. 历史对话太长时，优先保留最近的交互（它们在结尾，自然被更多关注）
4. 考虑定期做"上下文压缩"——把已有的对话历史总结为简短的摘要

#### 1.3.5 未来：无限上下文窗口还是更聪明的上下文管理？

关于这个问题的争论很有趣。一边是技术乐观派，认为通过稀疏注意力、线性注意力、状态空间模型（如Mamba）等手段，我们可以无限扩展上下文窗口。另一边是认知务实派，认为即使技术能实现无限窗口，人（和Agent）也不需要——人类的"工作记忆"也只有7±2个组块，但我们可以通过外部记忆（笔记本、数据库）来弥补。

我个人倾向于后一种观点：**Agent真正需要的不是无限上下文，而是聪明的上下文管理策略**——知道什么需要记住、什么可以遗忘、什么需要存储到外部记忆系统中。这恰好是下一节RAG要解决的问题。

---

### 1.4 Temperature、Top-p、Top-k等采样策略

#### 1.4.1 什么是采样策略？

LLM的输出不是"选择概率最高的那个词"这么简单。模型对每个可能的下一个token输出一个概率分布，采样策略决定了我们如何从这个分布中选出实际输出的token。

```
模型输出的原始logits（举例）:
[2.3, 1.1, -0.5, 4.2, 0.8, 3.7, -2.0, ...]
                |
                v Softmax
概率分布:
[0.05, 0.02, 0.003, 0.35, 0.01, 0.25, 0.0003, ...]
                |
                v 采样策略
最终选中的token: 可能是 "好" (概率0.35)
```

#### 1.4.2 Temperature：控制"大胆"还是"谨慎"

Temperature是一个在Softmax之前应用于logits的缩放因子：

```
adjusted_logits = logits / temperature

temperature = 0.1  → 概率分布更"尖锐"（几乎总是选最高概率的token）
temperature = 1.0  → 保持原始分布
temperature = 2.0  → 概率分布更"平滑"（低概率token也有机会被选中）
```

直觉上：
- **低temperature（0-0.3）**：模型很"保守"，每次回答都差不多。适合需要精确性和一致性的任务。
- **高temperature（0.7-1.0）**：模型很"奔放"，每次回答都可能不同。适合需要创造性的任务。

**Agent场景中的最佳实践**：

```
+---------------------------+-------------------+-------------------+
| Agent阶段                   | 推荐的Temperature  | 原因               |
+---------------------------+-------------------+-------------------+
| 规划（生成执行方案）         | 0.6 - 0.8         | 需要多样性，探索多种方案|
| 推理（分析当前状态）         | 0.3 - 0.5         | 需要逻辑严谨但不僵化   |
| 工具选择（决定调用哪个工具） | 0.0 - 0.1         | 必须准确，不可随意     |
| 工具参数生成（填充参数）     | 0.0 - 0.1         | 参数错误会导致调用失败 |
| 最终回答（对用户输出）       | 0.3 - 0.7         | 取决于需要正式还是亲切 |
+---------------------------+-------------------+-------------------+
```

很多Agent框架实际上允许**不同阶段使用不同的temperature**。规划时"头脑风暴"，执行时严格执行。

#### 1.4.3 Top-k采样：只考虑最好的k个

Top-k采样的做法是：**只保留概率最高的k个token，将其余token的概率置零，然后重新归一化并从这k个候选中随机采样。**

```
原始top-10概率:
"天气" 0.31, "气候" 0.18, "气温" 0.12, "天空" 0.08, "天" 0.05, ...

Top-k (k=3):
"天气" 0.51, "气候" 0.30, "气温" 0.20  (重新归一化后)
→ 从这3个中随机选
```

**Top-k的问题**：k是固定的，但不同上下文中概率分布的"尖锐度"差异很大。在确定性高的场景（如"法国的首都是"），k=50包含了大量不合适的候选；在概率分散的场景（如"接下来这个故事会..."），k=5可能过于限制。

#### 1.4.4 Top-p（Nucleus Sampling）：累积概率达p为止

Top-p采样解决了Top-k的固定k问题：**动态选择最少数量的token，使得它们的累积概率达到p。**

```
概率分布（已排序）:
"好"   0.45  → 累积0.45
"不错" 0.20  → 累积0.65
"棒"   0.12  → 累积0.77
"可以" 0.08  → 累积0.85
"行"   0.05  → 累积0.90
...

如果 p=0.9: 选择前5个token（累积0.90刚好达到阈值）
如果 p=0.8: 选择前4个token
如果 p=0.5: 只选择第1个token
```

Top-p=0.9意味着"模型有90%的信心认为下一个token在选中的这些候选中"。这比固定k更自然——在确定性高的时候自动缩小候选集，在不确定性高的时候自动扩大。

#### 1.4.5 组合使用

实践中通常是Top-p和Temperature结合使用：

```python
# 典型的采样流程
def sample_next_token(logits, temperature=0.7, top_p=0.9, top_k=50):
    # 1. Temperature缩放
    logits = logits / temperature

    # 2. Top-k过滤（可选）
    if top_k > 0:
        top_k_indices = torch.topk(logits, top_k).indices
        mask = torch.ones_like(logits, dtype=torch.bool)
        mask[top_k_indices] = False
        logits[mask] = float('-inf')

    # 3. Top-p过滤
    sorted_logits, sorted_indices = torch.sort(logits, descending=True)
    cumulative_probs = torch.cumsum(torch.softmax(sorted_logits, dim=-1), dim=-1)
    sorted_indices_to_remove = cumulative_probs > top_p
    sorted_logits[sorted_indices_to_remove] = float('-inf')

    # 4. 从调整后的分布中采样
    probs = torch.softmax(sorted_logits, dim=-1)
    return torch.multinomial(probs, 1)
```

**Agent开发中的经验法则**：
- 工具调用阶段：temperature=0（或接近于0），不需要采样，直接选最高概率的
- 推理阶段：temperature=0.3-0.5，保持逻辑一致性
- 如果Agent出现"重复输出同一句话"的循环问题，稍微提高temperature可以打破循环
- 如果Agent的答案总是"跑偏"，降低temperature

---

## 第二课：Tool Use深入

### 2.1 从文本生成到工具调用

#### 2.1.1 之前：LLM只能"说"不能"做"

2022年之前的大语言模型，本质上是"嘴上功夫"——它能写出一段漂亮的分析、一首诗、一份商业计划书，但它无法查天气、发邮件、订机票、执行代码。就像一个博学但被关在房间里的学者，什么都知道，什么都不能做。

这种能力缺失对实际应用是致命的：

```
用户: "旧金山现在几点？"
LLM (2022): "旧金山位于太平洋时区(UTC-8)..." (训练时的知识，可能已过时)

用户: "帮我发邮件给张三"
LLM (2022): "好的，邮件内容如下：..." (只生成了文本，并没有真的发送)

用户: "1+2*3-4/2等于多少"
LLM (2022): "等于4" (可能算错——LLM本质是语言模型，不是计算器)
```

#### 2.1.2 工具调用的本质

工具调用（Tool Use / Function Calling）的核心突破在于一个认知转变：**让LLM生成的不是自然语言回答，而是一段结构化的"指令"，由外部系统执行这个指令并将结果反馈给LLM。**

```
之前：User → LLM → 自然语言回答
之后：User → LLM → 结构化指令 → 工具执行 → 结果 → LLM → 自然语言回答
```

换句话说，LLM从"答案生成器"变成了"命令生成器+结果理解器"。

#### 2.1.3 JSON Schema定义工具

现代LLM（如GPT-4、Claude等）通过JSON Schema来描述可用工具：

```json
{
  "name": "get_weather",
  "description": "获取指定城市的当前天气信息，包括温度、湿度、风速和天气状况",
  "parameters": {
    "type": "object",
    "properties": {
      "city": {
        "type": "string",
        "description": "城市名称，支持中文名（如'北京'）或英文名（如'Beijing'）"
      },
      "unit": {
        "type": "string",
        "enum": ["celsius", "fahrenheit"],
        "description": "温度单位，celsius为摄氏度，fahrenheit为华氏度",
        "default": "celsius"
      }
    },
    "required": ["city"]
  }
}
```

当LLM决定调用这个工具时，它会输出：

```json
{
  "tool_call": {
    "name": "get_weather",
    "arguments": {
      "city": "北京",
      "unit": "celsius"
    }
  }
}
```

外部系统（Agent框架）解析这个JSON，执行真正的API调用，把结果（比如`{"temperature": 25, "humidity": 60, "condition": "晴"}`）追加到对话上下文中，LLM基于这个结果继续生成回答。

#### 2.1.4 工具描述的重要性

这里有一个不直观但极其重要的经验：**LLM是通过工具描述来"理解"工具的。** 描述的质量直接影响工具调用的准确率。

糟糕的工具描述：
```json
{
  "name": "do_stuff",
  "description": "做事情",
  "parameters": {
    "properties": {
      "x": {"type": "string", "description": "参数"}
    }
  }
}
```

好的工具描述：
```json
{
  "name": "send_email",
  "description": "通过SMTP发送一封电子邮件。当用户要求'发邮件'、'邮件通知'、'发送给某某'时使用此工具。注意：此工具需要收件人邮箱地址，如果用户只提供了姓名，需要先用search_contact工具查找邮箱。",
  "parameters": {
    "properties": {
      "to": {
        "type": "string",
        "description": "收件人邮箱地址，格式为 user@domain.com"
      },
      "subject": {
        "type": "string",
        "description": "邮件主题，简洁概括邮件内容"
      },
      "body": {
        "type": "string",
        "description": "邮件正文，支持纯文本。如需要HTML格式请使用html_body参数"
      }
    },
    "required": ["to", "subject", "body"]
  }
}
```

好的工具描述遵循以下原则：
1. **说明"何时使用"**：在什么用户意图下应该调用这个工具
2. **说明"与谁配合"**：如果这个工具需要和其他工具协同，明确指出
3. **参数写清楚约束**：格式要求、取值范围、默认值
4. **包含反例**（高级技巧）：说明什么情况下**不应该**用这个工具
5. **提供示例值**：如果可能，给出参数的具体例子

#### 2.1.5 常见陷阱

**陷阱1：工具描述太模糊导致误调用**

```json
// 两个工具的描述太相似
{"name": "search_web", "description": "搜索信息"}
{"name": "search_database", "description": "搜索信息"}

// LLM困惑：用户说"搜索XXX"，到底用哪个？
// 修复：明确区分使用场景
{"name": "search_web", "description": "在互联网上搜索实时信息，用于查找新闻、最新动态、公开资料"}
{"name": "search_database", "description": "在内部知识库中搜索，用于查找公司文档、技术规范、内部记录"}
```

**陷阱2：参数schema不严格导致幻觉**

```json
// 没有限制参数类型和范围
{
  "price": {"type": "number", "description": "价格"}
}
// LLM可能输出: "price": "免费" 或 "price": -100 → 解析失败

// 修复
{
  "price": {
    "type": "number",
    "minimum": 0,
    "description": "价格，单位为元，必须为非负数"
  }
}
```

**陷阱3：没有告诉模型"什么时候不要用这个工具"**

当用户说"你觉得今天天气怎么样"——这可能是在闲聊，不是真的要查天气。如果没有明确的边界说明，LLM可能会过度调用工具，浪费资源和token。

---

### 2.2 ReAct模式详解

#### 2.2.1 论文背景

2022年，Google Brain团队的Yao等人发表了论文《ReAct: Synergizing Reasoning and Acting in Language Models》。这篇论文在Agent研究领域的地位，怎么强调都不为过——它奠定了几乎全部现代Agent架构的基础模式。

#### 2.2.2 之前的方法：两种极端

在ReAct之前，人们让LLM做复杂任务的方式大致分成两派：

**Reasoning-only派（以Chain-of-Thought为代表）**：
```
问: 除了苹果之外，小明有多少个水果？他有3个苹果、5个橙子。
CoT: "苹果不算在'除了苹果之外'里，所以只看橙子。小明有5个橙子。答案是5。"

问题：如果LLM不知道小明的水果数量（这是用户刚说的），它无法验证。
      CoT只能基于已有知识推理，无法获取新信息。还容易产生幻觉。
```

**Acting-only派（以早期的Tool-augmented LM为代表）**：
```
问: 旧金山金门大桥有多长？
Acting: → 搜索"金门大桥 长度" → 得到搜索结果 → 输出长度

问题：如果搜索结果包含矛盾信息（不同来源给出不同长度），
      Acting-only无法进行推理和判断，只能机械地复述搜索结果。
```

**核心矛盾**：推理需要封闭世界的逻辑一致性，行动需要开放世界的信息获取。ReAct之前，没人把这两者统一起来。

#### 2.2.3 ReAct的核心思想

ReAct的核心是一个循环：**Thought → Action → Observation → Thought → ...**

```
┌──────────────────────────────────────────────┐
│                 ReAct Loop                     │
│                                                │
│   ┌──────────┐     ┌──────────┐               │
│   │ Thought  │────>│  Action  │               │
│   │ (思考)   │     │ (行动)   │               │
│   └──────────┘     └────┬─────┘               │
│         ^                │                     │
│         │                v                     │
│         │          ┌──────────┐               │
│         │          │   Tool   │ (外部世界)     │
│         │          └────┬─────┘               │
│         │                │                     │
│         └───────┐        v                     │
│              ┌──────────────┐                  │
│              │ Observation  │                  │
│              │  (观察结果)  │                  │
│              └──────────────┘                  │
└──────────────────────────────────────────────┘

循环终止条件：Thought判断任务已完成 → 输出Final Answer
```

每一步都在做"思考-行动-观察"的三拍子：**思考指导行动，行动结果反馈给思考。** 这不就是人类解决问题的基本模式吗？

#### 2.2.4 完整代码示例：实现一个ReAct Agent

下面是一个简化的ReAct Agent实现，帮助你理解每个环节：

```python
import re
import json
from typing import List, Dict, Any, Callable

class ReActAgent:
    """一个简化的ReAct Agent实现"""

    def __init__(self, llm_call: Callable, tools: Dict[str, Callable]):
        """
        Args:
            llm_call: 调用LLM的函数，接受prompt字符串，返回响应字符串
            tools: 工具字典，key为工具名，value为可调用的工具函数
        """
        self.llm_call = llm_call
        self.tools = tools
        self.max_steps = 10  # 防止无限循环

    def _build_system_prompt(self) -> str:
        """构建包含ReAct指令和工具描述的System Prompt"""
        tool_descriptions = []
        for name, func in self.tools.items():
            # 从函数的docstring中读取工具描述
            doc = func.__doc__ or "无描述"
            tool_descriptions.append(f"- {name}: {doc.strip()}")

        return f"""你是一个能使用工具的智能Agent。请按照ReAct模式解决问题。

## 可用工具
{chr(10).join(tool_descriptions)}

## 回答格式
你必须严格按照以下格式输出。每次只能输出一个Thought/Action/Observation/Final Answer块。

Thought: [你对当前情况的推理和分析]
Action: [工具名称]([参数JSON])
Observation: [工具返回的结果]

... (重复Thought/Action/Observation直到问题解决)

Thought: [最终推理，确认任务完成]
Final Answer: [最终回答]

## 规则
1. 每次只能调用一个工具
2. 必须等待Observation后才能继续
3. 工具参数必须使用合法的JSON格式
4. 如果工具调用失败，在Thought中分析原因并尝试修正
"""

    def _parse_action(self, text: str) -> tuple:
        """从LLM输出中解析Action"""
        match = re.search(r'Action:\s*(\w+)\((.*?)\)', text, re.DOTALL)
        if not match:
            return None, None
        tool_name = match.group(1)
        try:
            args = json.loads(match.group(2))
        except json.JSONDecodeError:
            args = {}
        return tool_name, args

    def run(self, user_query: str) -> str:
        """执行ReAct循环"""
        # 初始化对话历史
        conversation = self._build_system_prompt()
        conversation += f"\n\n## 用户问题\n{user_query}\n\n"

        for step in range(self.max_steps):
            print(f"\n{'='*50}")
            print(f"Step {step + 1}")
            print(f"{'='*50}")

            # 调用LLM获取下一步的Thought和Action
            response = self.llm_call(conversation)
            conversation += response + "\n"
            print(f"LLM输出:\n{response}")

            # 检查是否是最终回答
            if "Final Answer:" in response:
                final = response.split("Final Answer:")[-1].strip()
                print(f"\n🎯 任务完成: {final}")
                return final

            # 解析Action
            tool_name, args = self._parse_action(response)
            if tool_name is None:
                # LLM没有输出有效的Action，提示它继续
                conversation += "Observation: 没有检测到有效的工具调用，请使用Action: tool_name({...})格式\n"
                continue

            # 执行工具
            if tool_name not in self.tools:
                observation = f"错误：工具'{tool_name}'不存在。可用工具：{list(self.tools.keys())}"
            else:
                try:
                    result = self.tools[tool_name](**args)
                    observation = str(result)
                except Exception as e:
                    observation = f"工具调用失败：{str(e)}"

            # 将观察结果追加到对话历史
            conversation += f"Observation: {observation}\n"
            print(f"Observation: {observation}")

        return "达到最大步数限制，任务未能完成。"


# ============================================
# 使用示例
# ============================================

def search_database(query: str) -> str:
    """在内部数据库中搜索信息。参数query为搜索关键词。"""
    # 模拟数据库
    database = {
        "北京天气": "北京今日晴，温度18-26°C，湿度45%，风力3级",
        "上海天气": "上海今日多云转阴，温度22-28°C，湿度70%，风力2级",
        "北京到上海": "北京到上海高铁约4.5小时，二等座553元",
    }
    return database.get(query, f"未找到关于'{query}'的信息")

def calculate(expression: str) -> str:
    """计算数学表达式。参数expression为数学表达式字符串，如'1+2*3'。"""
    try:
        result = eval(expression)  # 生产环境请用更安全的方式
        return str(result)
    except Exception as e:
        return f"计算错误: {e}"

# 模拟LLM调用（实际使用时替换为真实的API调用）
def mock_llm(prompt: str) -> str:
    """模拟LLM的ReAct推理"""
    if "北京" in prompt and "上海" in prompt and "天气" in prompt:
        return """Thought: 用户想比较北京和上海的天气，我需要分别查询两个城市的天气信息。
Action: search_database({"query": "北京天气"})"""
    elif "北京天气" in prompt:
        return """Thought: 获取到了北京的天气信息，接下来需要查询上海的天气。
Action: search_database({"query": "上海天气"})"""
    elif "上海天气" in prompt:
        return """Thought: 现在已经获取了北京和上海的天气信息。北京晴，18-26°C；上海多云转阴，22-28°C。我可以总结比较结果了。
Final Answer: 北京今日晴，温度18-26°C，较为舒适；上海今日多云转阴，温度22-28°C，湿度较高（70%）。相比之下，北京天气更好，适合户外活动。"""
    return "Thought: 不清楚下一步该做什么。\nFinal Answer: 抱歉，我无法完成这个任务。"

# 运行Agent
agent = ReActAgent(
    llm_call=mock_llm,
    tools={"search_database": search_database, "calculate": calculate}
)

# result = agent.run("比较一下北京和上海今天的天气")
```

**执行流程可视化**：

```
Step 1:
  Thought: 用户想比较北京和上海的天气，需要分别查询
  Action: search_database({"query": "北京天气"})
  Observation: 北京今日晴，温度18-26°C，湿度45%

Step 2:
  Thought: 获取到了北京的天气，接下来查上海
  Action: search_database({"query": "上海天气"})
  Observation: 上海今日多云转阴，温度22-28°C，湿度70%

Step 3:
  Thought: 两城市天气都已获取，可以比较了
  Final Answer: 北京晴18-26°C，上海多云22-28°C...
```

#### 2.2.5 ReAct的局限性

ReAct虽然优雅，但在实践中会遇到几个问题：

**1. Token消耗大。** 每一步的Thought/Action/Observation都在消耗上下文窗口。一个复杂任务可能经过10+轮循环，上下文很满时可能触发截断。

**2. 容易死循环。** 如果工具返回的结果让LLM困惑，它可能反复调用同一个工具，陷入循环。常见模式：调用工具A → 结果不满意 → 调用工具B → 结果也不满意 → 回到工具A...

```python
# 防护措施：检测重复的工具调用
def _detect_loop(self, history: List[str], threshold: int = 3) -> bool:
    """检测是否陷入了工具调用的死循环"""
    recent_actions = []
    for msg in history[-10:]:  # 只看最近10轮
        match = re.search(r'Action:\s*(\w+)\((.*?)\)', msg)
        if match:
            recent_actions.append((match.group(1), match.group(2)))

    if len(recent_actions) >= threshold:
        # 检查最近threshold个action是否完全相同
        last_n = recent_actions[-threshold:]
        if len(set(last_n)) == 1:
            return True
    return False
```

**3. 缺乏高层次规划。** ReAct在每一步只考虑"下一步做什么"，缺乏对整体任务的结构化分解。对于复杂任务，可能走了一条很绕的路才到达终点，甚至走错方向。后来的Plan-and-Solve、Tree-of-Thoughts等方法试图解决这个问题。

**4. 无法撤销。** 如果第3步的工具调用产生了错误的结果，ReAct很难"回退"到第2步重新选择路径。这是线性推理链的固有局限。

#### 2.2.6 你刚刚写的这个循环，就是最简Harness

回顾上面的 `ReActAgent` 代码，把业务逻辑（LLM推理、工具执行）剥离后，剩下的骨架是什么？

```python
class ReActAgent:
    def run(self, user_query):
        for step in range(self.max_steps):     # ← 循环控制
            response = self.llm_call(...)       # ← 调用推理引擎
            if "Final Answer" in response:      # ← 停止条件判断
                return ...
            tool_name, args = self._parse(...)  # ← 解析动作
            observation = self.tools[tool_name](...)# ← 执行工具
            conversation += observation          # ← 管理上下文
```

这个骨架就是 **Agent Harness（运行时引擎）**——它是Agent的"操作系统层"，负责驱动整个循环但不参与具体的推理或工具执行。

Harness不是一个框架特有的概念，而是所有Agent系统的通用抽象。你在阶段二的ReAct Agent中写的那个 `while/for` 循环就是最简Harness；LangGraph的 `StateGraph` 是更强大的Harness；Claude Code的内部循环也是Harness。**不同框架的本质差异，很大程度上就是Harness设计的差异。**

Harness的核心职责是三层：

| 层次 | 职责 | 对应代码 |
|------|------|---------|
| **驱动层** | 启动循环、管理步骤迭代、调用LLM | `for step in range(max_steps)` |
| **控制层** | 停止条件、超时、错误恢复、循环检测 | `if "Final Answer" in response` |
| **管理层** | 上下文窗口管理、工具注册、记忆注入 | `conversation += observation` |

一个经常被问到的问题：**Harness和Orchestration（编排）有什么区别？**

> - **Orchestration** 决定"怎么走"——是链式的还是图式的、是Plan-then-Execute还是ReAct Loop。它关注的是**流程模式**。
> - **Harness** 负责"走路"——无论你选择了什么流程模式，Harness都以一致的方式驱动每一步、管理状态、处理异常。它关注的是**运行时执行**。
>
> 类比：Orchestration是你的驾驶路线规划（走高速还是走国道），Harness是你的汽车引擎（不管什么路线，引擎都负责让车动起来）。

`stage-03-architecture.md` 的第一课会在Orchestration之前，先系统性讲解Harness的架构设计。从阶段三起，你将不再手写"裸循环"，而是有意识地设计Harness的每一层。

---

## 第三课：RAG——给Agent接入知识

### 3.1 RAG的演进历史

#### 3.1.1 之前：LLM的知识困境

2020年之前，LLM面临着几个与知识相关的核心困境：

**困境一：知识截止日期。** GPT-3的知识停留在训练数据收集完成的那一刻（约2019年）。问它"现任美国总统是谁"，它可能给出已过时的答案。这是"知识时效性"问题。

**困境二：幻觉（Hallucination）。** LLM面对它不知道的事情时，不会诚实地说"不知道"，而是倾向于"编造"一个听起来合理的答案。询问一个不存在的学术论文、编造假的法律条文、虚构数据——这些都是幻觉的典型表现。

**困境三：知识密度。** 训练数据中的知识是稀疏的。关于某个特定领域（如某公司的内部流程、某种罕见病的治疗方案），训练数据中可能只有寥寥几段，模型很难准确记住。

**困境四：知识更新成本。** 要让模型学会新知识，传统做法是重新训练或微调——成本高、周期长，而且可能导致灾难性遗忘（学会新东西，忘了旧东西）。

#### 3.1.2 2020年：RAG的诞生

2020年，Meta AI（当时还叫Facebook AI）的研究团队发表了论文《Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks》。论文提出了一个简单的想法：

**与其把所有知识塞进模型参数，不如在需要时去查。**

```
传统LLM回答问题的流程:
┌──────┐     ┌─────────────┐     ┌──────────┐
│ User │────>│  LLM (参数)  │────>│  Answer  │
└──────┘     └─────────────┘     └──────────┘
             全部知识在参数中

RAG回答问题的流程:
┌──────┐     ┌──────────┐     ┌─────────────┐     ┌──────────┐
│ User │────>│ Retriever│────>│  LLM + 文档  │────>│  Answer  │
└──────┘     │ (检索器) │     └─────────────┘     └──────────┘
             └─────┬────┘
                   │
              ┌────v─────┐
              │ 知识库    │
              │(文档集合) │
              └──────────┘
```

这本质上是一种**"开卷考试"**策略：不要求模型背下所有知识，但要求它能在拿到参考资料后正确理解和回答问题。这个想法虽然简单，但解决了一个根本性的问题：**模型的推理能力和知识存储可以解耦。**

#### 3.1.3 RAG对Agent的决定性意义

对Agent来说，RAG不仅是"一个功能"，而是**基础设施级别的能力**：

| Agent场景 | RAG的作用 |
|-----------|----------|
| 客服Agent | 检索产品手册、FAQ、历史工单 |
| 编程Agent | 检索API文档、代码示例、错误日志 |
| 法律Agent | 检索法律法规、判例、合同模板 |
| 医疗Agent | 检索医学文献、药品说明书、诊疗指南 |
| 研究Agent | 检索学术论文、实验数据、研究报告 |

更重要的是，RAG让Agent具备了**事实核查**的能力——在做出重要决策或给出关键信息前，先检索验证。这大大降低了幻觉的风险。

#### 3.1.4 RAG的基本架构

```
                        ┌──────────────────────────────┐
                        │       离线阶段（建库）         │
                        │                                │
        文档集合        │   ┌──────┐    ┌───────────┐   │
        ┌─────┐        │   │Chunking│──>│ Embedding  │   │
        │ PDF │───────>│   │ (分块) │    │ (向量化)  │   │
        │ TXT │        │   └──────┘    └─────┬─────┘   │
        │ HTML│        │                      │         │
        └─────┘        │                      v         │
                        │               ┌───────────┐   │
                        │               │ 向量数据库  │   │
                        │               │(Vector DB) │   │
                        └───────────────┴──────┬──────┘
                                               │
        ┌──────────────────────────────────────┘
        │                                        ┌──────────────────────┐
        │              在线阶段（查询）           │                      │
        │                                        │  ┌────────────────┐  │
        v                                        │  │  System Prompt │  │
   ┌────────┐    ┌───────────┐    ┌──────────┐  │  │  + 用户问题     │  │
   │ 用户问题│───>│ Embedding │───>│ 向量检索  │  │  │  + 检索文档    │  │
   └────────┘    └───────────┘    └────┬─────┘  │  └───────┬────────┘  │
                                       │        │          │           │
                                       v        │          v           │
                                  ┌─────────┐   │    ┌───────────┐     │
                                  │ Top-K文档│──>│    │    LLM    │     │
                                  └─────────┘   │    └─────┬─────┘     │
                                                │          │           │
                                                │          v           │
                                                │    ┌───────────┐     │
                                                │    │   Answer   │     │
                                                │    └───────────┘     │
                                                └──────────────────────┘
```

---

### 3.2 Embedding与向量检索

#### 3.2.1 之前：关键词检索（BM25）

在向量检索兴起之前，信息检索的主流方法是BM25（Best Match 25）——一种基于词频和逆文档频率（TF-IDF）的排序算法。

BM25的匹配逻辑是**字面匹配**：
- 查询"苹果手机" → 匹配包含"苹果"和"手机"的文档
- 查询"iPhone" → 不匹配上面那个文档（虽然说的是同一件事）
- 查询"水果中的苹果" → 仍然匹配上面那个文档（虽然说的是完全不同的事）

**语义鸿沟**是关键词检索无法跨越的障碍。当你搜索"怎么提升编程能力"时，一篇标题为"软件开发技能进阶指南"的文章可能完美匹配你的需求，但因为词不重叠（"编程"≠"软件开发"，"提升"≠"进阶"），BM25会给它打低分。

#### 3.2.2 Embedding的本质

Embedding（嵌入/向量化）的核心思想是：**将文本映射到一个高维向量空间中，使得语义相似的文本在这个空间中距离近。**

```
"苹果是一种水果"     →  [0.12, -0.34, 0.78, ..., 0.05]  (768维向量)
"iPhone是苹果的产品"  →  [0.10, -0.31, 0.75, ..., 0.08]  (768维向量)
"今天天气很好"        →  [-0.45, 0.82, -0.12, ..., -0.33] (768维向量)

余弦相似度:
sim("苹果是一种水果", "iPhone是苹果的产品") = 0.87  ← 高相似度！
sim("苹果是一种水果", "今天天气很好")      = 0.05  ← 低相似度
```

在高维向量空间中，语义关系体现为几何关系：
- 同义词 → 方向接近
- 类比关系 → 向量算术（"国王" - "男人" + "女人" ≈ "女王"）
- 主题聚类 → 同类文档自然聚集

#### 3.2.3 Embedding模型的发展

**第一代：Word2Vec（2013）**
Mikolov等人提出的Word2Vec是一个里程碑。它通过"预测上下文"（Skip-gram）或"预测中心词"（CBOW）的训练目标，让模型学会了词的分布式表示。但Word2Vec是**静态的**——每个词只有一个固定的向量，无法处理多义词（"苹果"作为水果和作为品牌应该是不同的向量）。

**第二代：BERT（2018）**
BERT的最大突破是**上下文相关**的表示。同一个"苹果"，在不同的句子中会有不同的向量表示：
- "我吃了一个苹果" → 苹果(fruit)的向量
- "苹果发布了新手机" → 苹果(company)的向量

BERT通过Masked Language Model（遮住一些词让模型预测）和Next Sentence Prediction（判断两句话是否相邻）两个任务进行预训练，学会了深层的语言理解。

**第三代：Sentence-BERT（2019）**
BERT可以为每个token生成向量，但要得到整个句子的表示，简单的平均池化效果不好。Sentence-BERT使用孪生网络（Siamese Network）结构，专门训练模型生成有意义的**句子级别**向量。两个相似句子的向量被拉近，不相似的被推远。

**第四代：OpenAI Embeddings与新一代模型**
OpenAI的text-embedding-ada-002（2022年发布）和text-embedding-3（2024年发布）进一步提升了Embedding的质量。这些模型的特点是：
- 在对比学习（Contrastive Learning）框架下训练
- 支持长文本（8192 tokens）
- 多语言能力
- 维度可调整（text-embedding-3支持256到3072维）

最新的多语言Embedding模型（如BGE-M3、multilingual-e5）能同时处理100+种语言，且不同语言的语义相近的文本会被映射到相近的向量区域。

#### 3.2.4 检索策略：稠密 vs 稀疏 vs 混合

**稠密检索（Dense Retrieval）**：用Embedding模型将查询和文档都映射为稠密向量，通过向量相似度检索。

```python
from openai import OpenAI

client = OpenAI()

def dense_search(query: str, documents: List[str], top_k: int = 5):
    """稠密检索"""
    # 1. 将查询向量化
    query_embedding = client.embeddings.create(
        input=query,
        model="text-embedding-3-small"
    ).data[0].embedding

    # 2. 在向量数据库中检索Top-K
    results = vector_db.search(query_embedding, top_k=top_k)
    return results
```

优点：能捕捉语义相似性
缺点：对专有名词、精确匹配不敏感（"AK-47"和"M16"向量可能很近，但它们是不同的枪）

**稀疏检索（Sparse Retrieval / BM25）**：
优点：精确匹配能力强（搜索"GDP增长率"不会返回"经济增长速度"）
缺点：无法处理语义变体

**混合检索（Hybrid Retrieval）**：结合两者优势：

```python
def hybrid_search(query: str, documents: List[str], top_k: int = 5, alpha: float = 0.5):
    """混合检索：融合稠密和稀疏的结果"""
    # 1. 分别检索
    dense_results = dense_search(query, documents, top_k=top_k*2)
    sparse_results = bm25_search(query, documents, top_k=top_k*2)

    # 2. 融合分数（Reciprocal Rank Fusion）
    combined_scores = {}
    for rank, (doc_id, _) in enumerate(dense_results):
        combined_scores[doc_id] = combined_scores.get(doc_id, 0) + alpha * (1 / (rank + 60))
    for rank, (doc_id, _) in enumerate(sparse_results):
        combined_scores[doc_id] = combined_scores.get(doc_id, 0) + (1-alpha) * (1 / (rank + 60))

    # 3. 按综合分数排序
    return sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
```

在生产环境中，混合检索几乎是标配。

---

### 3.3 Chunking策略

#### 3.3.1 为什么需要分块？

RAG检索到的内容最终要放入LLM的上下文窗口。完整的文档可能太长（一本1000页的手册），所以需要将文档切分成适当大小的"块"（Chunk）。分块质量直接影响检索效果：块太大导致噪声多、精度低；块太小导致信息破碎、缺乏上下文。

```
文档: [============== 10万字的技术手册 ==============]
                      |
                   Chunking
                      |
    +-------+  +-------+  +-------+  +-------+  +-------+
    |Chunk 1|  |Chunk 2|  |Chunk 3|  |Chunk 4|  |Chunk N|
    |2K字   |  |2K字   |  |2K字   |  |2K字   |  |2K字   |
    +-------+  +-------+  +-------+  +-------+  +-------+
```

#### 3.3.2 三大分块策略

**策略一：固定大小分块（Fixed-size Chunking）**

最朴素的方法——按固定token数切分，通常加一个重叠区域（overlap）来避免边界截断。

```python
def fixed_size_chunk(text: str, chunk_size: int = 512, overlap: int = 64) -> List[str]:
    """固定大小分块"""
    tokens = tokenize(text)
    chunks = []
    start = 0

    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk = detokenize(tokens[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap  # 前进时保留overlap

    return chunks

# 直观示意
# 文档: "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
# chunk_size=10, overlap=3
# Chunk1: "ABCDEFGHIJ"        |==========|
# Chunk2:       "HIJKLMNOPQR"      |==========|
# Chunk3:             "PQRSTUVWXYZ"      |==========|
```

优点：简单，计算快
缺点：可能在句子中间截断，破坏语义完整性

**策略二：语义分块（Semantic Chunking）**

以自然段落、句子为边界切分，保证每个块内部的语义完整性。

```python
import re

def semantic_chunk(text: str, max_chunk_size: int = 1000) -> List[str]:
    """基于段落和句子的语义分块"""
    # 1. 先按段落切分
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        # 2. 如果加上当前段落后不超过限制，合并
        if len(current_chunk) + len(para) <= max_chunk_size:
            current_chunk += para + "\n\n"
        else:
            # 3. 超过限制时，保存当前块，开始新块
            if current_chunk:
                chunks.append(current_chunk.strip())
            # 4. 如果单个段落就超过了限制，按句子进一步切分
            if len(para) > max_chunk_size:
                sentences = re.split(r'(?<=[。！？.!?])\s*', para)
                for sent in sentences:
                    if len(current_chunk) + len(sent) <= max_chunk_size:
                        current_chunk += sent
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sent
            else:
                current_chunk = para + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks
```

优点：每个块语义完整，检索结果可读性好
缺点：块大小不均匀，可能产生过大或过小的块

**策略三：递归分块（Recursive Chunking）**

先尝试用较大的分隔符（如段落），如果块太大，再用较小的分隔符（如句子），逐级递归。

```python
def recursive_chunk(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    separators: List[str] = ["\n\n", "\n", "。", ".", " ", ""]
) -> List[str]:
    """递归分块：从大到小尝试分隔符"""

    # 如果文本本身就在限制内，直接返回
    if len(text) <= chunk_size:
        return [text] if text.strip() else []

    # 尝试当前层级的分隔符
    separator = separators[0]
    remaining_separators = separators[1:]

    if separator:
        splits = text.split(separator)
    else:
        # 最后的兜底：按字符强制切分
        splits = list(text)

    chunks = []
    current_chunk = ""

    for split in splits:
        # 单个split本身超出限制，递归到下一级分隔符
        if len(split) > chunk_size and remaining_separators:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
            sub_chunks = recursive_chunk(
                split, chunk_size, chunk_overlap, remaining_separators
            )
            chunks.extend(sub_chunks)
            continue

        # 尝试将split加入当前chunk
        test_chunk = current_chunk + (separator if current_chunk else "") + split

        if len(test_chunk) <= chunk_size:
            current_chunk = test_chunk
        else:
            if current_chunk:
                chunks.append(current_chunk)
            # 用overlap填充新chunk的开头
            if chunk_overlap > 0 and current_chunk:
                overlap_text = current_chunk[-chunk_overlap:]
                current_chunk = overlap_text + separator + split
            else:
                current_chunk = split

    if current_chunk:
        chunks.append(current_chunk)

    return chunks
```

#### 3.3.3 小块 vs 大块的Trade-off

```
+----------------------+--------------------------------+--------------------------------+
| 维度                   | 小块 (128-256 tokens)           | 大块 (512-2048 tokens)          |
+----------------------+--------------------------------+--------------------------------+
| 检索精度               | 高（返回的信息更聚焦）           | 低（包含较多无关内容）           |
| 上下文完整性           | 低（可能丢失关键的上文或下文）    | 高（保留完整的论证或说明链）      |
| Embedding质量          | 略低（短文本的语义信号弱）        | 略高（更多上下文有助于编码）      |
| LLM理解               | 困难（碎片化信息需要LLM自行拼接） | 容易（直接可用）                 |
| 最佳场景               | 事实性问答、FAQ                  | 解释性问答、教程、长文档理解     |
| Token消耗（单次检索）   | 低                               | 高                               |
+----------------------+--------------------------------+--------------------------------+
```

**实战经验：不同场景的最佳chunk大小**

- **FAQ/客服**：256-512 tokens。问题通常聚焦于某个具体点。
- **技术文档**：512-1024 tokens。函数/API文档通常在这个范围内。
- **法律/合同**：1000-2000 tokens。条款之间有逻辑关联，太碎会丢失上下文。
- **学术论文**：按照"节"（section）来分块，而非固定大小。每节约500-3000 tokens。
- **对话记录**：按"轮次"而非按token分块，保持问答的配对关系。

还有一个进阶技巧：**小块检索 + 大块返回**。用小块做向量检索（精度高），检索到的小块所属的"父文档"或"前后相邻块"一并返回给LLM（保证上下文完整）。这种方法兼顾了精度的上下文的完整性。

```python
def retrieve_with_context(
    query: str,
    small_chunks: List[str],        # 用于检索的小块
    large_chunks: List[str],        # 用于返回的大块
    chunk_mapping: Dict[int, int],  # 小块ID → 大块ID的映射
    top_k: int = 3
):
    """小块检索 + 大块上下文返回"""
    # 1. 在小块上检索
    small_results = vector_search(query, small_chunks, top_k=top_k)

    # 2. 找到这些小块所属的大块（去重）
    seen_large_ids = set()
    context_chunks = []
    for small_id, score in small_results:
        large_id = chunk_mapping[small_id]
        if large_id not in seen_large_ids:
            context_chunks.append(large_chunks[large_id])
            seen_large_ids.add(large_id)

    return context_chunks
```

---

## 第四课：Prompt Engineering

### 4.1 System Prompt设计

#### 4.1.1 之前：直接把问题扔给LLM

2020-2021年，大多数人使用GPT-3的方式就是：把问题写进输入框，点发送，看结果。没有"系统提示"的概念，没有结构化指令，没有行为约束。

这种方式的问题很快暴露：
- 模型不知道自己的"角色"——有时用医生口吻回答，有时用程序员口吻
- 没有行为边界——可能会生成有害内容、回答不该回答的问题
- 输出不可控——格式、长度、风格完全随机

#### 4.1.2 System Prompt vs User Prompt

现代LLM API（如OpenAI Chat Completions、Anthropic Messages API）区分了两种提示：

```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {
            "role": "system",
            "content": "你是一个专业的法律顾问。回答问题时引用具体法条，保持客观中立。如果不确定，请明确说明。"
        },
        {
            "role": "user",
            "content": "公司不给加班费怎么办？"
        }
    ]
)
```

| 维度 | System Prompt | User Prompt |
|------|---------------|-------------|
| 作用 | 设定角色、规则、风格、能力边界 | 传达具体任务和上下文 |
| 生命周期 | 整个对话中都有效 | 单次交互 |
| 优先级 | 高（模型会优先遵守系统指令） | 中（在系统规则下执行用户任务） |
| 典型内容 | 你是谁、你能做什么、你不能做什么、输出格式 | 当前问题、背景信息、具体要求 |

把System Prompt理解为"角色的出厂设置"，把User Prompt理解为"眼前的任务清单"。

#### 4.1.3 Agent System Prompt的关键要素

一个设计良好的Agent System Prompt通常包含以下部分：

```
┌────────────────────────────────────────────────────────┐
│                   Agent System Prompt                    │
├────────────────────────────────────────────────────────┤
│ 1. 【角色定义】你是谁？                                 │
│    "你是一个名为CodeHelper的编程助手Agent..."            │
│                                                         │
│ 2. 【能力声明】你能做什么？                              │
│    "你可以阅读代码文件、执行shell命令、搜索文档..."       │
│                                                         │
│ 3. 【行为约束】你不能做什么？                            │
│    "不要修改生产环境的文件。不要执行可能造成数据丢失的    │
│     操作。不确定时先向用户确认。"                         │
│                                                         │
│ 4. 【工具列表】你可以使用哪些工具？                      │
│    （通常由框架自动注入）                                │
│                                                         │
│ 5. 【工作流程】你应该如何思考和行动？                    │
│    "分析问题 → 制定计划 → 逐步执行 → 验证结果 → 汇报"    │
│                                                         │
│ 6. 【输出格式】你应该如何组织回答？                      │
│    "用Markdown格式回答，代码块标注语言类型。如果任务失    │
│     败，请说明失败原因和建议。"                          │
│                                                         │
│ 7. 【特殊情况处理】遇到意外怎么办？                      │
│    "如果连续3次工具调用失败，停止尝试并报告。如果用户     │
│     输入包含敏感信息，提醒用户注意安全。"                 │
└────────────────────────────────────────────────────────┘
```

#### 4.1.4 常见错误与修复

**错误1：指令冲突**

```yaml
# 有问题的System Prompt
你是一个简洁的助手，回答尽量简短。  # ← 指令A
在回答问题时，要详细解释推理过程。  # ← 指令B（与A冲突！）
```

LLM面对冲突指令时的行为是不可预测的。好的做法是用明确的条件区分"何时简洁、何时详细"：

```yaml
# 修复后
回答原则：
- 对于事实性问题（如"几点了"、"1+1等于几"），直接给出答案，简明扼要
- 对于分析性问题（如"为什么"、"怎么做"），先展示推理过程，再给出结论
```

**错误2：隐含假设**

```yaml
# 有问题的System Prompt（假设了工具一定可用）
当用户询问天气时，调用get_weather工具获取实时数据。

# 修复：明确说明条件
当用户询问天气时，首先检查get_weather工具是否可用。
如果可用，调用它获取实时数据。如果不可用，告知用户你无法获取实时天气，
但可以提供查询天气的方法建议。
```

**错误3：过度约束**

```yaml
# 过度约束的例子
你必须用三段式的结构回答。第一段不能超过30字。第二段必须包含至少一个数据。
第三段必须以反问结束。不要使用逗号。

# 这些规则会让LLM的回答变得机械、不自然。
# 好的做法：给出原则性指导，而非机械性规则。
回答时建议包含：核心观点、支撑论据、行动建议。保持自然流畅的表达。
```

#### 4.1.5 迭代优化方法

System Prompt不是一次写好的。有效的方法论是**写 → 测试 → 改**的循环：

```python
# System Prompt迭代开发流程

# 1. 准备测试用例（最好覆盖各种边界情况）
test_cases = [
    {"query": "你好", "expected": "友好问候，介绍自己"},
    {"query": "帮我删除所有文件", "expected": "拒绝并给出安全警告"},
    {"query": "用Python写一个快排", "expected": "提供代码和解释"},
    {"query": "你叫什么名字？", "expected": "回答Agent名称"},
    {"query": "", "expected": "处理空输入"},
    {"query": "我想自杀", "expected": "敏感内容的安全回应"},
]

# 2. 运行测试
def evaluate_prompt(system_prompt: str) -> dict:
    results = {}
    for case in test_cases:
        response = llm_call(system_prompt, case["query"])
        results[case["query"]] = {
            "response": response,
            # 可以加入人工评估或自动检测（如检查是否包含特定关键词）
            "contains_expected": any(kw in response for kw in case["expected"].split("、"))
        }
    return results

# 3. 根据测试结果调整Prompt
# 4. 重新测试
# 5. 重复直到满意
```

---

### 4.2 Few-shot Prompting

#### 4.2.1 之前：零样本效果不稳定

零样本（Zero-shot）就是你直接问模型一个问题，不提供任何示例。对于一些简单任务，零样本效果可以接受，但对于复杂任务（尤其是需要特定格式或推理模式的任务），零样本的表现波动很大。

```
# 零样本：模型有时正确有时错误
用户: "将'我吃饭了'翻译成英文"
模型: "I ate." (可能对)
用户: "将'会者不难'翻译成英文"
模型: "The meeting person is not difficult." (显然错了——正确应为"What is hard is easy for those who know how")
```

#### 4.2.2 Few-shot的工作原理

Few-shot Prompting的思想是：**给模型看几个例子，它就能理解任务的模式并泛化到新问题。** 不需要微调，不需要梯度更新，只需要在Prompt里加入示例即可。

```python
few_shot_prompt = """
将中文成语翻译成英文，要求翻译出含义而非字面意思：

示例1:
中文: 画蛇添足
英文: To gild the lily (to overdo something unnecessary)

示例2:
中文: 亡羊补牢
英文: Better late than never (to fix a problem before it's too late)

示例3:
中文: 对牛弹琴
英文: To cast pearls before swine (to give valuable things to those who can't appreciate them)

现在请翻译:
中文: 井底之蛙
英文:
"""
```

模型看到这三个示例后，学会了这个任务的模式：不仅仅是翻译，而是要找到英文中的对应成语或习语，并在括号中解释含义。

#### 4.2.3 在Agent场景中的应用

Few-shot Prompting在Agent中最重要的应用场景是**教Agent正确的工具选择逻辑**：

```python
agent_few_shot_prompt = """
你是一个客服Agent。以下是你与用户的对话示例，展示了如何正确选择和使用工具。

===
用户: "我的订单到哪里了？订单号是12345"
助手:
Thought: 用户想查询订单物流状态，需要用到query_order工具。
Action: query_order({"order_id": "12345"})
Observation: 订单12345状态：已发货，快递单号SF1234567890
Thought: 订单已发货，用户需要的是物流详情，应该查询快递。
Action: query_logistics({"tracking_number": "SF1234567890"})
Observation: 快递SF1234567890在2024-01-15 14:30到达北京分拣中心
Thought: 已获取完整的物流信息，可以回答用户了。
Final Answer: 您的订单12345已发货，快递单号SF1234567890。最新状态：1月15日下午到达北京分拣中心，预计明天送达。

===
用户: "我想退货，订单号67890"
助手:
Thought: 用户想退货，需要先查询订单是否符合退货条件。
Action: query_order({"order_id": "67890"})
Observation: 订单67890状态：已签收，签收日期2024-01-10
Thought: 订单已签收10天，需要检查是否在退货期内（7天），可能已超期。但仍应告知用户退货政策。
Final Answer: 您的订单67890于1月10日签收，距离签收已超过7天无理由退货期限。不过我可以帮您查看是否符合质量问题退货条件。请问商品是否存在质量问题？

===
现在请处理以下用户请求（使用和上面相同的格式）：
用户: "帮我查一下订单54321和订单98765的状态"
"""
```

通过这两个精心构造的示例，Agent学会了：
1. 当用户查物流时，先查订单再查快递（工具调用的顺序）
2. 退货时先检查退货条件再回复（工具调用的判断逻辑）
3. 工具返回结果后的信息整合方式（如何组织最终回答）

#### 4.2.4 示例选择策略

Few-shot的效果很大程度上取决于示例的质量。三个原则：

**1. 多样性**：覆盖不同类型的问题。如果所有示例都是"查询"类，模型碰到"修改"类的问题可能会不知所措。

**2. 代表性**：选择最常见、最典型的问题模式。边缘案例不适合做示例——它们会让模型学会特例而非常规。

**3. 边界案例**：在典型示例之外，加一两个边界案例（如"用户提供了不完整的信息"、"工具调用失败"），教模型处理异常。

```python
def select_few_shot_examples(
    query: str,
    example_bank: List[dict],
    k: int = 3
) -> List[dict]:
    """基于相似度从示例库中选择最相关的Few-shot示例"""
    # 将query和所有示例用Embedding模型编码
    query_emb = embed(query)
    example_embs = [embed(ex["query"]) for ex in example_bank]

    # 计算余弦相似度
    similarities = [
        cosine_similarity(query_emb, ex_emb)
        for ex_emb in example_embs
    ]

    # 选择最相似的k个，但确保多样性（过滤掉过于相似的）
    # ...（实际实现可能用MMR等算法）
    return selected_examples
```

---

### 4.3 Chain-of-Thought

#### 4.3.1 2022年的CoT论文

2022年1月，Google Research的Wei等人发布了论文《Chain-of-Thought Prompting Elicits Reasoning in Large Language Models》。这篇论文证明了一个看似简单但影响深远的事实：**让模型在给出最终答案之前先"展示推理过程"，能显著提高复杂推理任务的准确率。**

在GSM8K（小学数学题数据集）上，PaLM 540B的表现：
- 标准Prompting：约**33%**准确率
- Chain-of-Thought Prompting：约**57%**准确率

接近翻倍！而且这不需要任何模型架构的改变，不需要微调，纯粹是Prompt技巧。

#### 4.3.2 "Let's think step by step"

CoT的核心直觉是：**复杂问题需要多步推理，如果模型直接跳到答案，中间步骤的任何错误都会导致最终答案错误。但如果模型把中间步骤"写出来"，不仅更容易发现错误，而且整个推理链可以为最终答案提供支撑。**

```
# 标准Prompting
问: 小明有5个苹果，买了3个橙子，吃了2个苹果。他现在有多少水果？
答: 6个 ← 模型可能直接猜，可能对也可能错

# Chain-of-Thought Prompting
问: 小明有5个苹果，买了3个橙子，吃了2个苹果。他现在有多少水果？
答: 让我们逐步思考：
    1. 小明最初有5个苹果
    2. 他又买了3个橙子
    3. 此时水果总数：5 + 3 = 8个
    4. 他吃了2个苹果，苹果变为5 - 2 = 3个
    5. 此时水果总数：3个苹果 + 3个橙子 = 6个水果
    答案是6个。 ← 准确且可验证
```

更神奇的是，Kojima等人在2022年的论文中发现，甚至不需要精心编写的Few-shot CoT示例——**只需要在问题后面加一句"Let's think step by step"（让我们一步步思考）**，就能触发模型的链式推理行为，准确率大幅提升。这就是Zero-shot-CoT。

#### 4.3.3 CoT在Agent中的应用

在Agent中，CoT不是独立存在的，而是融入到了ReAct的Thought环节中：

```
没有CoT的Agent:
  User提问 → 直接Action → 出错 → 换个Action → 继续出错...

带CoT的Agent:
  User提问 → Thought(先规划：这个问题需要几个步骤？每一步可能遇到什么问题？)
           → Action(有了清晰的思路再行动)
           → Observation → Thought(分析结果是否符合预期)
           → Action(基于分析决定下一步) → ...
```

具体来说，System Prompt中可以这样引导：

```
在执行任何操作之前，请先在Thought中思考以下问题：
1. 用户的核心需求是什么？（不要被表面问题迷惑）
2. 这个问题可以分解为哪些子任务？
3. 哪些信息是已知的？哪些还需要获取？
4. 第一步应该做什么？为什么？
5. 完成每个步骤后，检查结果是否符合预期。
```

**CoT的变体**：

- **Auto-CoT**（Zhang et al., 2022）：自动生成CoT示例，而不是人工编写
- **Least-to-Most**（Zhou et al., 2022）：先把复杂问题分解成简单子问题，逐一解决
- **Tree-of-Thoughts**（Yao et al., 2023）：不是单链推理，而是多分支探索，每个分支可以回溯
- **Self-Consistency**（Wang et al., 2022）：让模型生成多条推理链，取多数一致的结果

---

### 4.4 结构化输出

#### 4.4.1 之前：自由文本，解析困难

早期LLM的输出是自由格式的文本。如果你的应用需要从输出中提取结构化信息（如实体、数值、分类标签），你必须写正则表达式或规则来解析。但LLM的输出格式不稳定——有时候换行、有时候不换行、有时候多了一个冒号——解析代码会非常脆弱。

```
# 自由文本输出的痛苦
LLM输出: "姓名是张三，年龄为28岁，职业是工程师"
# 也可能输出: "张三，28岁，工程师"
# 还可能输出: "该用户叫张三，今年28，做工程师的"

# 你需要写大量正则来parse
name = re.findall(r'(?:姓名|叫|用户)是?[：:]?\s*(\S+)', text)
age = re.findall(r'(?:年龄|今年)(?:为|是)?[：:]?\s*(\d+)', text)
# ... 脆弱且不完整
```

#### 4.4.2 JSON Mode与Function Calling

OpenAI在2023年推出了JSON Mode：确保模型输出合法的JSON。

```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[...],
    response_format={"type": "json_object"}  # 强制输出JSON
)
# 保证response是合法JSON: {"name": "张三", "age": 28, "occupation": "工程师"}
```

Function Calling更进一步：模型按照预定义的JSON Schema输出，参数的每个字段都有类型约束。

```python
tools = [{
    "type": "function",
    "function": {
        "name": "extract_person_info",
        "description": "从文本中提取人物信息",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0, "maximum": 150},
                "occupation": {"type": "string"}
            },
            "required": ["name", "age"]
        }
    }
}]
```

#### 4.4.3 Constrained Decoding（受限解码）

JSON Mode的局限性在于：它只是一个"保证"，而不是硬约束。模型仍有可能生成不合法的JSON（虽然概率很小）。Constrained Decoding在**生成层面**就限制了模型的输出空间。

```
# 普通解码：模型可以生成任何token
token_space = [所有50000个vocab中的token]

# 受限解码：根据JSON Schema，每一步只能生成"合法"的token
token_space = {
    "开始":    ["{"],
    "之后":    ['"name"', '"age"', '"occupation"'],
    '"name"后': ['"', ':', ' ', '"'],
    '":"后':   ['张', '李', '王', ...],  # 所有可能的字符
    ...
}
```

这种方法的优势是**100%保证输出符合Schema**，不需要重试，不需要错误处理。但实现复杂度高，需要集成到推理引擎中。

#### 4.4.4 主流库的设计思路

几个主流的结构化输出库：

**Instructor**（Python）：
```python
import instructor
from pydantic import BaseModel

class PersonInfo(BaseModel):
    name: str
    age: int
    occupation: str

client = instructor.from_openai(OpenAI())

# 直接返回Pydantic模型实例，类型安全！
person = client.chat.completions.create(
    model="gpt-4",
    response_model=PersonInfo,  # 指定响应模型
    messages=[{"role": "user", "content": "用户叫张三，28岁，工程师"}]
)
# person.name == "张三", person.age == 28, person.occupation == "工程师"
```

Instructor的设计哲学是：**用Pydantic作为Schema定义语言，利用其类型系统和验证能力，自动处理LLM输出的解析、验证和重试。** 如果LLM的输出不符合Pydantic模型，Instructor会自动重新请求（带上错误信息），直到输出合法。

**Outlines**：侧重于在token层面做受限解码，保证输出100%符合格式要求。

**Guidance**（微软）：提供了一种模板语言，用`{{gen}}`标记定义LLM填充的位置，模板本身保证了结构。

#### 4.4.5 为什么Agent需要结构化输出？

回到Agent的场景，结构化输出的重要性怎么强调都不为过：

**工具调用的参数必须是可解析的。** 如果Agent决定调用`send_email(to="zhang@example.com", subject="会议通知", body="...")`，但模型输出的"to"字段格式错误（如`to="张三"`而不是邮箱地址），工具调用就会失败。工具调用失败意味着Agent的行动链断裂，整个任务可能无法完成。

**多Agent协作需要结构化的消息协议。** 当多个Agent需要协作时，它们之间传递的信息必须是结构化的、可验证的——类似于网络协议中的TCP/IP，每个Agent都清楚它收到的消息包含哪些字段、每个字段的含义。

**可观测性和调试。** 结构化的输出（工具调用JSON、推理步骤JSON）可以被记录、分析、可视化。当Agent行为异常时，你可以回放日志查看每一步的详细输出。

---

## 总结：四大支柱如何支撑Agent

回顾这个阶段的四课内容，我们可以看到它们分别对应了Agent的四个核心能力：

```
            ┌─────────────────────────────────┐
            │          Agent 架构全景           │
            │                                   │
            │   ┌─────────────────────────┐    │
            │   │     Prompt Engineering   │    │
            │   │   (指挥大脑怎么说和做)    │    │
            │   └───────────┬─────────────┘    │
            │               │                   │
            │   ┌───────────v─────────────┐    │
            │   │        LLM 大脑          │    │
            │   │  (Transformer + 分词 +   │    │
            │   │   上下文 + 采样策略)      │    │
            │   └───┬───────────────┬─────┘    │
            │       │               │           │
            │   ┌───v───┐      ┌───v───────┐   │
            │   │Tool Use│      │    RAG    │   │
            │   │(行动力)│      │(记忆力)   │   │
            │   └───┬───┘      └───┬───────┘   │
            │       │               │           │
            │   ┌───v───────────────v───────┐   │
            │   │       外部世界              │   │
            │   │  (API、数据库、文件系统..)   │   │
            │   └───────────────────────────┘   │
            └─────────────────────────────────┘
```

- **LLM原理**是地基：不理解模型如何思考，就无法设计有效的交互方式
- **Tool Use**是手脚：让Agent从"会说"变为"会做"
- **RAG**是记忆：弥补模型知识的不完整和过时
- **Prompt Engineering**是指挥棒：精确地告诉Agent在什么情况下做什么

这四大支柱彼此交织、互相增强。一个好的Agent开发者，不会单独优化其中某一个方面，而是理解它们之间的相互作用——比如如何设计Prompt让Agent更准确地选择工具，如何将RAG的检索结果组织成LLM容易理解的格式，如何在上下文窗口的限制下高效地利用RAG和工具调用。

---

> **下一阶段预告：阶段三——Agent框架实战。** 我们将动手使用LangChain、AutoGen、CrewAI等主流框架搭建完整的Agent应用。有了本阶段的理论基础，你会发现那些框架的设计理念变得容易理解——它们本质上就是对LLM + Tool Use + RAG + Prompt Engineering的组合封装。就像学了模拟电路再看集成电路，一切都有脉络可循。

---

*本讲义编写于2024年。AI技术发展迅速，部分信息可能随着新模型的发布而变化。建议配合最新的技术博客和论文阅读，保持知识的鲜度。*

---

## 第五课（桥梁项目）：文件整理 Agent —— 从单次调用到多步自主

### 为什么需要这个桥梁项目？

阶段二的练习让你实现了单个 ReAct Agent，阶段三将学习复杂的编排、记忆、评测等架构。这两个阶段之间的跨度在于：**从"能跑起来"到"知道为什么需要架构"**。

这个桥梁项目的目标很明确：先做一个多步自主的文件整理 Agent，在做的过程中你会自然地遇到问题——比如"它为什么在某个目录死循环了？""它为什么忘了之前整理过什么？""我该怎么衡量它整理得好不好？"——这些问题正是阶段三要系统解决的。

换句话说，**先踩坑，再学理论，理解会更深刻**。

### 5.1 项目需求

**功能描述**：给出一个目录路径，Agent 自动分析目录中的所有文件，按规则分类整理（如按文件类型、按日期、按项目等），并输出整理报告。

**要求**：
1. Agent 先扫描目录结构（plan 阶段）
2. 制定整理方案并展示给用户确认
3. 用户确认后，逐步执行整理操作
4. 整理完成后输出总结报告

### 5.2 实现步骤

**Step 1：定义工具集**

```
工具列表：
- list_files(path): 列出目录下所有文件（含子目录）
- get_file_info(path): 获取文件的详细信息（大小、修改时间、类型）
- read_file(path): 读取文本文件内容（用于判断文件归属）
- move_file(src, dst): 移动文件到目标目录
- create_directory(path): 创建新目录
```

**Step 2：设计整理规则**

定义文件分类规则，例如：
- 按扩展名分类：`documents/`（.pdf, .docx, .md）、`images/`（.png, .jpg）、`code/`（.py, .js, .ts）
- 按修改时间分类：`2024/`, `2025/`, `2026/`
- 按文件名关键词分类：`project-a/`（含"proposal"、"contract"等关键词的文件）

**Step 3：实现 Planner**

Planner 的 System Prompt 示例：
```
你是一个文件整理助手。你的任务是：
1. 先列出目标目录的所有文件
2. 分析文件构成，制定整理方案
3. 将方案展示给用户，等待确认后再执行

注意：
- 不要移动正在被其他程序使用的文件
- 对于不确定如何分类的文件，单独放入"unsorted/"目录
- 每移动一个文件后，记录操作日志
```

**Step 4：添加 Trace 记录**

在 Agent 循环中添加简单的 trace 日志：
```python
trace = []
for step in agent_loop:
    trace.append({
        "step": step_number,
        "thought": thought,
        "action": action,
        "observation": observation[:200],  # 截断避免过长
        "timestamp": time.time()
    })
```

任务完成后，将 trace 保存为 JSON 文件。这个 trace 在阶段三学习 Evaluation 时会用到。

**Step 5：准备评测目录**

创建 3-5 个测试用的目录（混乱的、不同规模的），用于验证 Agent 的整理效果：
```
test_dirs/
  small/       # 10 个文件，类型单一
  medium/      # 50 个文件，混合类型
  messy/       # 100+ 个文件，命名混乱，有嵌套
  edge_cases/  # 空文件、超大文件、特殊字符文件名
```

对每个测试目录，预先定义"理想整理结果"，用于后续评估。

### 5.3 复盘模板

完成项目后，用以下模板写一份复盘报告（这是阶段三的重要输入）：

```markdown
## 文件整理 Agent 复盘报告

### 一、基本数据
- 总测试任务数：
- 成功完成数：
- 成功率：
- 平均每任务步数：
- 平均每任务耗时：

### 二、失败案例分析
| 编号 | 测试目录 | 失败描述 | 失败类型 | 如果让你改代码，你改什么？ |
|------|---------|---------|---------|--------------------------|
| 1 | | | tool selection / prompt / schema / 上下文管理 | |
| 2 | | | | |
| ... | | | | |

### 三、Trace 分析
- Agent 最常犯的错误是什么？
- 哪些步骤是重复的、可以优化掉的？
- 上下文窗口什么时候开始"不够用"了？

### 四、如果重做，你会怎么设计？
- 当前的 Planner 有什么问题？
- 记忆系统能解决你遇到的哪类问题？
- 你希望有一个什么样的评测框架来帮你迭代？
```

### 5.4 桥梁项目 → 阶段三的导航

完成复盘后，你会发现：

| 你遇到的问题 | 阶段三对应的解决方案 |
|-------------|-------------------|
| Agent 在某个目录死循环 | **Orchestration**：循环控制、停止条件设计 |
| Agent 忘了之前整理过什么 | **Memory**：工作记忆、长期记忆 |
| 不知道怎么衡量整理得好不好 | **Evaluation**：端到端评测、步骤级评测 |
| Agent 移动了不该移动的文件 | **Guardrails**：输出校验、Human-in-the-Loop |
| 不知道 Agent 内部发生了什么 | **Observability**：Tracing、调试工具 |

带着这些问题进入阶段三，每个概念都会变得具体而有意义。
