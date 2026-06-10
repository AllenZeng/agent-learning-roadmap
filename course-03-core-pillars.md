# 课程三：Agent 底层核心 —— 五大核心模块

---

## 课程导言

课程一是让你看见 Agent，课程二是让你理解 Agent 的核心能力演进，课程三是让你动手实现。

我们将深入 Agent 的底层技术栈，从 LLM 的运作原理开始，到工具调用、知识检索、记忆管理、提示工程，逐一拆解。这五大核心模块都是围绕 LLM 的根本局限而发展出来的——Tool Use 解决"只能说不"的问题，RAG 解决"知识过时"的问题，Memory 解决"转瞬即忘"的问题，Prompt Engineering 解决"输出不可控"的问题。ReAct 则是将这些模块串联为可运行的决策循环。

每一个技术点，我们都会追问三个问题：它解决了什么痛点？设计者是怎么想到的？未来会走向何方？

---

## 学习目标

完成本课程后，你将能够：

1. 理解 Transformer 的核心机制（Self-Attention、Multi-Head Attention），并解释为什么它适合作为 Agent 的基础模型
2. 掌握 Tokenization 对工具调用的影响，能在设计工具时做出正确的命名和描述决策
3. 理解上下文窗口的工作原理和"Lost in the Middle"现象，能制定有效的上下文管理策略
4. 独立实现一个基于 ReAct 模式的 Agent，支持 3+ 个工具
5. 搭建一个 RAG 检索系统，理解 Embedding、向量检索、Chunking 的全链路
6. 理解 Memory 的分层概念（短期/长期），实现最简的跨会话记忆持久化
7. 写出结构清晰、行为可控的 System Prompt

---

## 目录

- [第一章：LLM 原理 —— Agent 的大脑](#第一章llm-原理--agent-的大脑)
- [第二章：Tool Use —— 让 Agent 能够行动](#第二章tool-use--让-agent-能够行动)
- [第三章：RAG —— 给 Agent 接入外部知识](#第三章rag--给-agent-接入外部知识)
- [第四章：Prompt Engineering —— 让 Agent 输出可控](#第四章prompt-engineering--让-agent-输出可控)
- [第五章：Memory —— 让 Agent 不再转瞬即忘](#第五章memory--让-agent-不再转瞬即忘)
- [第六章：ReAct —— 将五大模块串联为决策循环](#第六章react--将五大模块串联为决策循环)
- [总结：五大核心模块构成 Agent](#总结五大核心模块构成-agent)
- [附加实践：桥梁项目 —— 文件整理 Agent](#附加实践桥梁项目--文件整理-agent)

---

## 第一章：LLM 原理 —— Agent 的大脑

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

#### 1.1.6 多模态 LLM 对 Agent 的影响

上述讨论聚焦于纯文本 LLM，但今天的 Agent 已经可以"看见"世界。GPT-4o、Claude 3.5、Gemini 2.0 等模型原生支持图像输入。这对 Agent 意味着什么？

**改变了工具返回结果的形态**：传统工具返回纯文本（JSON、日志、搜索结果），现在可以直接返回截图、图表、PDF 页面截图。Agent 不再需要"OCR→理解→推理"的间接链路，而是可以直接"看懂"视觉信息。

**改变了 Agent 的操作范式**：Computer Use（课程七）中的截屏分析、GUI 元素定位，本质上是让多模态 LLM 扮演"眼睛"的角色。浏览器自动化的混合方案（截图+DOM 标记）也依赖视觉理解能力。

**改变了工具定义的方式**：某些工具不再需要精确的 JSON Schema——Agent 可以通过"看图"来理解工具界面，通过视觉定位来操作按钮和输入框。

**当前局限**：视觉理解的延迟远高于文本处理（图像 token 化产生大量输入 token），精度尚不如专用的 Object Detection 模型，且视觉"幻觉"（看错按钮、读错数字）比文本幻觉更难检测。

> **在课程三中的定位**：多模态 Agent 不是本课程的重点，但你需要在认知层面建立这个意识。当你设计工具时，考虑"这个工具的返回结果可以是图片吗？"；当你选择模型时，考虑"这个任务需要视觉理解能力吗？"。

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

## 第二章：Tool Use —— 让 Agent 能够行动

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

## 第三章：RAG —— 给 Agent 接入外部知识

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

### 3.4 数据管线：RAG 不只是"检索+生成"

前面的内容聚焦在检索和生成的"在线"阶段。但一个生产可用的 RAG 系统，离线阶段的数据工程管线同样关键——检索质量的上限由数据质量决定。

#### 3.4.1 多源数据摄入

Agent 需要从多种来源获取知识：

| 数据源 | 摄入方式 | 注意事项 |
|--------|---------|---------|
| 数据库 | JDBC/ODBC 连接器、CDC 变更捕获 | 注意增量更新，避免全量重拉 |
| API | REST/GraphQL 定时拉取 | 处理限流、分页、认证过期 |
| 文件（PDF/Word/Markdown） | 文档解析器 + OCR | 扫描件需要 OCR，表格需要结构化提取 |
| 网页 | Crawler + HTML→Markdown | 反爬处理、动态渲染页面 |
| 对话记录 | 从日志系统导出 | 注意 PII 脱敏 |

#### 3.4.2 数据清洗与标准化

原始文档通常很"脏"——嵌入的广告、页眉页脚、水印、格式标记。清洗步骤包括：

```
原始文档 → 去除格式噪声 → 去除重复段落 → 统一格式(UTF-8) → 元数据标注 → 分块 → 向量化
```

元数据标注尤其重要——每条 chunk 应携带：
- 来源（哪个文档、哪个章节）
- 时效性（发布时间、有效期限）
- 权威性（官方文档 vs 个人博客）
- 类型（API 文档 / FAQ / 教程 / 规范）

这些元数据在后续检索时可用于过滤（"只搜索近 3 个月的文档"）和排序（"优先官方文档"）。

#### 3.4.3 数据新鲜度管理

知识库需要持续更新：

- **增量更新**：新增文档只对新 chunk 做 embedding，不重建整个索引
- **过期检测**：定期检查文档的"有效期"，自动标记过时内容
- **版本管理**：同一文档的不同版本保留在索引中，检索时默认返回最新版本
- **反馈闭环**：当用户指出检索结果不准确时，记录反馈并触发人工审核

#### 3.4.4 知识图谱的互补

向量检索擅长语义匹配，但在精确关系查询上较弱（"A 是 B 的上游依赖"）。知识图谱（Knowledge Graph）通过结构化的实体-关系-实体三元组来组织知识，与向量检索形成互补：

```
向量检索：擅长"告诉我关于 X 的一切"（语义泛化）
知识图谱：擅长"X 和 Y 是什么关系？"（精确关系）
```

在实际项目中，通常先用向量检索找到相关实体，再用知识图谱查询实体之间的关系。这个方向在课程四的 Memory 深入中会进一步涉及。

> **实战建议**：在课程三的 RAG 练习中，即使只处理本地文件，也尝试记录每条 chunk 的元数据（文件名、页码、添加时间）。这个习惯在知识库扩展到数百个文档时会体现出价值。

---

## 第四章：Prompt Engineering —— 让 Agent 输出可控

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

## 第五章：Memory —— 让 Agent 不再转瞬即忘

### 5.1 Memory 基础

在前面的课程中，我们已经涉及了"记忆"的雏形：RAG 检索外部知识可以视为一种"只读记忆"，ReAct 循环中的 `conversation` 变量保存了当前会话的历史。但这些都不够。

Memory 作为独立的核心模块，要解决的是两个具体问题：

| 问题 | 表现 | 根源 |
|------|------|------|
| **上下文窗口有限** | Agent 执行到第 8 步时"忘记"了第 1 步的关键信息 | LLM 的上下文窗口有硬限制，满了就只能截断 |
| **跨会话无状态** | 用户关闭窗口重新打开后，Agent 完全不记得上次聊了什么 | LLM 是无状态的，每次调用都是"第一次见面" |

这两个问题本质上源自同一个事实：**LLM 的"记忆"完全依赖上下文窗口中的文本，它本身没有任何持久化的内部状态。** 如果说 RAG 解决了"世界知识"的问题，Memory 解决的就是"个人经验"的问题——Agent 在这次任务中学到了什么？用户的偏好是什么？上次失败的原因是哪个工具参数写错了？

#### 5.1.1 之前的世界：每次对话都是"初见"

在 Memory 概念被系统化之前，Agent 的典型表现是：

- 用户："帮我查一下北京到上海的航班"
- Agent：查询 → 返回结果
- 用户："那广州呢？"
- Agent："请问您是想查询从广州到上海的航班，还是……" ← 已经忘了上下文

即使是单个会话内，当对话变长、历史信息被截断后，Agent 也会丢失早期对话中的关键信息——比如用户在第 1 轮说的"只查直飞航班，不要转机的"。

#### 5.1.2 关键洞察：人类记忆不是一块完整的录像带

认知心理学告诉我们，人类的记忆不是精确录像，而是分为三个层次：

- **感觉记忆**：容量大但持续不到 1 秒
- **工作记忆**：容量约 7±2 个组块（Miller's Law），持续 10-20 秒
- **长期记忆**：容量几乎无限，但需要检索和提取

Agent 的 Memory 设计直接借鉴了这个分层模型：上下文窗口类似工作记忆（容量有限但精度高），持久化存储类似长期记忆（需要检索但容量大）。这个类比是理解所有 Agent Memory 系统的关键。

### 5.2 短期记忆：上下文窗口管理

#### 5.2.1 Lost in the Middle——为什么"放进去"不等于"记住了"

一个容易被忽视但极其重要的发现：**LLM 对上下文中不同位置的信息，关注度是不均匀的。**

2023 年，斯坦福、UC Berkeley 和 Samaya 的研究者发表了一篇实验报告，标题直截了当：*Lost in the Middle: How Language Models Use Long Contexts*。

他们对当时支持长上下文的模型做了系统性测试：将需要回答的"关键信息"分别放在文档的开头、中间和末尾位置，然后测试模型能否正确回答。结果是——**无论是什么模型，中间位置的信息总是更容易被忽略，开头和末尾的信息则被更好地利用**。

```
模型对信息位置的注意力分布（示意）：

注意力
 ↑
 │  ████████                         ████████
 │  ████████                         ████████
 │  ████████         ░░░░            ████████
 │  ████████         ░░░░            ████████
 │  ████████         ░░░░            ████████
 └──────────────────────────────────────────→ 位置
    开头             中间              末尾

█ = 高关注度区域    ░ = 低关注度区域（Lost in the Middle）
```

**这对 Agent 意味着什么？** 如果 Agent 在任务开始时用户说了一句"所有操作都不要动生产环境"，而这句话恰好在上下文窗口的"中间地带"，随着后续工具调用结果不断追加，Agent 可能会——在实践中确实会——忘记这个关键约束。

#### 5.2.2 三种基础的上下文管理策略

**策略一：滑动窗口**

最简单的方法：保留最近 N 个消息，超过就丢弃最旧的。

```python
def sliding_window(messages, max_messages=20):
    return messages[-max_messages:]
```

优点：简单、高性能。缺点：早期的重要信息（如用户的核心指令）会被无情丢弃。

**策略二：摘要压缩**

用 LLM 将历史对话压缩为一段摘要，用摘要替代完整历史。

```python
def compress_history(messages):
    """将长对话压缩为摘要"""
    history_text = format_messages(messages[:-5])  # 除了最近5轮
    summary = llm.generate(
        f"将以下对话历史压缩为一段摘要，保留所有关键信息：\n{history_text}"
    )
    return [SystemMessage(f"历史对话摘要：{summary}")] + messages[-5:]
```

优点：保留信息的"精华"而非全部细节。缺点：摘要过程消耗 Token，且可能丢失对后续任务关键但"看起来不重要的"细节。

**策略三：重要性过滤**

不是按时间，而是按"对当前任务是否有用"来判断保留什么。

```python
def filter_by_relevance(messages, current_task):
    """只保留与当前任务相关的历史消息"""
    relevant = []
    for msg in messages:
        score = relevance_judge(msg, current_task)  # 用轻量模型或规则判断
        if score > THRESHOLD:
            relevant.append(msg)
    return relevant
```

优点：更智能，能精准保留关键信息。缺点：需要一个"重要性判断器"，如果判断不准反而更糟。

#### 5.2.3 一个简单的组合方案

实践中更常见的做法是**三层上下文**：

```
┌──────────────────────────────────────┐
│  第三层：冷数据（长期记忆检索结果）     │ ← 只在相关时检索并注入
│  第二层：温数据（早期对话的压缩摘要）   │ ← 始终存在，节省 Token
│  第一层：热数据（最近 3-5 轮对话原文）  │ ← 保留完整原文，最高精度
└──────────────────────────────────────┘
```

这个方案的实现不超过 30 行代码，但能显著提升长对话场景下的 Agent 表现。它是课程四 Memory 架构深入课程的前置基础。

### 5.3 长期记忆：跨会话持久化

#### 5.3.1 短期 vs 长期：一条明确的界线

| 维度 | 短期记忆 | 长期记忆 |
|------|---------|---------|
| 生命周期 | 当前会话内 | 跨会话持久化 |
| 存储位置 | 上下文窗口、内存变量 | 文件、数据库、向量库 |
| 访问方式 | 直接读取（已在上下文中） | 需要检索（类似 RAG） |
| 容量 | 受上下文窗口限制（10K-200K tokens） | 几乎无限 |
| 典型内容 | 当前任务的工具调用结果、推理步骤 | 用户偏好、历史任务经验、学到的知识 |

#### 5.3.2 长期记忆的最简实现

在引入向量数据库之前，先用最简单的方式理解长期记忆的本质：**把"记忆"存下来，下次启动时读取**。

```python
import json
import os
from datetime import datetime

class SimpleMemory:
    """最简长期记忆：基于 JSON 文件的键值存储"""
    
    def __init__(self, filepath="./agent_memory.json"):
        self.filepath = filepath
        self.memories = self._load()
    
    def _load(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r') as f:
                return json.load(f)
        return {"user_preferences": {}, "learned_facts": [], "task_history": []}
    
    def _save(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.memories, f, ensure_ascii=False, indent=2)
    
    def remember_preference(self, key: str, value: str):
        """记住用户偏好"""
        self.memories["user_preferences"][key] = value
        self._save()
    
    def remember_fact(self, fact: str):
        """记住一条事实"""
        self.memories["learned_facts"].append({
            "fact": fact,
            "timestamp": datetime.now().isoformat()
        })
        self._save()
    
    def record_task(self, task: str, result: str):
        """记录一次任务完成"""
        self.memories["task_history"].append({
            "task": task,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        self._save()
    
    def get_preference(self, key: str) -> str | None:
        """读取用户偏好"""
        return self.memories["user_preferences"].get(key)
    
    def get_recent_tasks(self, n=5) -> list:
        """获取最近 n 次任务"""
        return self.memories["task_history"][-n:]
    
    def generate_memory_prompt(self) -> str:
        """生成可注入 System Prompt 的记忆片段"""
        prefs = self.memories["user_preferences"]
        facts = self.memories["learned_facts"][-10:]  # 最近10条
        recent = self.memories["task_history"][-3:]    # 最近3次任务
        
        prompt = "## 记忆信息\n"
        if prefs:
            prompt += "用户偏好：\n"
            for k, v in prefs.items():
                prompt += f"- {k}: {v}\n"
        if facts:
            prompt += "\n已学习的事实：\n"
            for f in facts:
                prompt += f"- {f['fact']}\n"
        if recent:
            prompt += "\n近期任务：\n"
            for r in recent:
                prompt += f"- {r['task']} → {r['result']}\n"
        return prompt
```

**使用方式**：在每次 Agent 启动时，调用 `memory.generate_memory_prompt()` 将记忆注入 System Prompt，这样 Agent 就有了"跨会话的自我认知"。

这是最简陋的长期记忆实现，但它清晰地展示了 Memory 的本质：**存储 + 检索 + 注入**。课程四会在这个基础上展开：向量数据库实现语义检索、Mem0/MemGPT 的记忆管理、记忆衰减与更新策略。

### 5.4 Memory 与已有课程的坐标定位

学完这一课，你可能会想：Memory 和 RAG 有什么区别？

| 维度 | RAG | Memory |
|------|-----|--------|
| 存储内容 | 外部文档、知识库（"世界知识"） | 用户偏好、任务历史、Agent 经验（"个人知识"） |
| 更新方式 | 手动导入或定时抓取 | Agent 运行时自动写入 |
| 检索触发 | 用户问题驱动 | 系统启动时注入 + 任务中动态查询 |
| 典型工具 | 向量数据库、全文检索引擎 | JSON 文件、SQLite、Mem0、Letta |

**它们的交集**：当你学会了 RAG 的 Embedding + 向量检索技术，你可以把这些技术用在 Memory 上——两者的检索基础设施是共通的，差别只在"存什么"和"为什么时候用"。

---

> **本课小结**：Memory 是 Agent 五大核心模块中解决"遗忘"问题的模块。短期记忆管理让 Agent 在长对话中不丢失关键信息；长期记忆让 Agent 不再是"金鱼记忆"，能跨会话积累用户偏好和经验。课程四的 Memory 章节将在此基础上，深入向量数据库选型、MemGPT 虚拟内存思想、记忆衰减策略等架构话题。

---

## 第六章：ReAct —— 将五大模块串联为决策循环

前五课逐一拆解了 Agent 的五大核心模块：LLM 是大脑，Tool Use 是手，RAG 是外部知识库，Memory 是经验积累，Prompt Engineering 是行为规范。但你可能已经注意到一个问题：**这些模块各自独立，谁来协调它们？**

答案是 ReAct。

ReAct（Reasoning + Acting）由 Yao 等人在 2022 年 10 月提出，核心思想简洁而深刻：**让 LLM 在"推理"和"行动"之间交替循环**——推理（Thought）决定下一步做什么，行动（Action）去执行，观察（Observation）执行结果，再基于结果继续推理。这个循环将五大核心模块串联为一个有机整体。

### 为什么 ReAct 是 Agent 的"心脏"

看一个具体例子来感受 ReAct 与其他模式的区别：

```
用户问题: "2024年诺贝尔物理学奖得主的主要贡献是什么？"

纯 LLM（无 ReAct）:
  → 凭训练记忆直接回答（可能正确，可能过时，可能幻觉）

LLM + 单次工具调用:
  → 搜索一次 → 拿到结果 → 回答（如果第一次搜索结果不完整，无法补救）

ReAct Agent:
  Thought: 用户问的是2024年诺贝尔物理学奖，我需要查最新的信息
  Action: search("2024 Nobel Prize Physics winner")
  Observation: 搜索结果显示John Hopfield和Geoffrey Hinton获奖
  Thought: 找到了得主，但用户问的是"主要贡献"，我需要更详细的信息
  Action: search("John Hopfield contribution Nobel Prize 2024")
  Observation: Hopfield因"Hopfield网络"获奖，这是一种...
  Thought: 还需要查Hinton的贡献
  Action: search("Geoffrey Hinton contribution Nobel Prize 2024")
  Observation: Hinton因"玻尔兹曼机"和深度学习基础工作获奖
  Thought: 信息齐全了，可以综合回答
  Final Answer: 2024年诺贝尔物理学奖授予John Hopfield和Geoffrey Hinton...
```

ReAct 的关键在于：**每一步观察都可能改变下一步决策**。它不是在走预设流程，而是根据实际情况动态调整策略。

### ReAct 循环的完整实现

以下是 ReAct Agent 核心循环的完整实现，不依赖任何高级框架：

```python
import json
import re
from typing import Any

class ReActAgent:
    """ReAct Agent 核心实现。

    五大模块在 ReAct 中的角色：
    - LLM：_think() 中调用，负责理解当前状态并决定下一步
    - Tool Use：_execute_action() 中调用具体工具，结果注入 Observation
    - RAG：search_knowledge_base 工具在 Action 阶段检索外部知识
    - Memory：conversation_history 保存会话轨迹，外部 memory 提供跨会话上下文
    - Prompt Engineering：_build_system_prompt() 构建行为规范、工具描述和输出格式
    """

    def __init__(self, llm_client, tools: dict, system_prompt: str = "",
                 max_steps: int = 10, memory=None):
        self.llm = llm_client
        self.tools = tools              # {"tool_name": callable}
        self.tools_schema = self._build_tools_schema(tools)
        self.system_prompt = system_prompt
        self.max_steps = max_steps      # 防止死循环
        self.memory = memory            # 可选的跨会话记忆（Memory 模块）
        self.conversation_history: list[dict] = []

    # ── 工具 Schema 构建（Tool Use 模块的工程化） ──

    def _build_tools_schema(self, tools: dict) -> str:
        """将工具字典格式化为 LLM 可理解的描述。

        每个工具必须有 __name__ 和 __doc__，docstring 中需包含参数说明。
        例如：
            def search(query: str) -> str:
                '''搜索互联网获取实时信息。
                Args:
                    query: 搜索关键词，支持中英文。'''
        """
        lines = []
        for name, func in tools.items():
            lines.append(f"- {name}: {func.__doc__ or '(无描述)'}")
        return "\n".join(lines)

    # ── System Prompt 构建（Prompt Engineering 模块的核心） ──

    def _build_system_prompt(self) -> str:
        """构建完整的 System Prompt——融合角色、工具、记忆和行为规范。"""
        prompt_parts = []

        # 1. 角色和基础行为规范
        if self.system_prompt:
            prompt_parts.append(self.system_prompt)

        # 2. 工作流程说明（CoT 引导）
        prompt_parts.append("""
## 工作方式

你通过以下循环来完成任务：

1. **Thought**：分析当前状态，决定下一步做什么。思考时考虑：
   - 用户的核心需求是什么？
   - 目前已经获得了哪些信息？还缺什么？
   - 如果上一步失败了，原因是什么？换个什么方法？
2. **Action**：执行具体操作。格式为：
   Action: tool_name
   Action Input: {"param1": "value1", "param2": "value2"}
3. **Observation**：观察工具返回的结果，回到第 1 步。
4. 当任务完成时，输出：Final Answer: [你的最终回答]
   

## 重要规则

- 每次只执行一个 Action
- 对危险操作（删除、修改文件、发邮件），先描述你要做什么，不要直接执行
- 如果连续 3 次工具调用返回错误，停止重试并报告原因
- 不要编造工具返回结果中没有的信息
""")

        # 3. 工具列表
        prompt_parts.append("## 可用工具\n")
        prompt_parts.append(self.tools_schema)

        # 4. 跨会话记忆注入（Memory 模块）
        if self.memory:
            memory_context = self.memory.generate_memory_prompt()
            if memory_context:
                prompt_parts.append(f"\n{memory_context}")

        return "\n".join(prompt_parts)

    # ── 主循环 ──

    def run(self, user_input: str) -> str:
        """执行 ReAct 循环，直到任务完成或达到最大步数。

        循环结构：
            Thought → Action → Observation → Thought → Action → ... → Final Answer

        每次循环都是一个完整的"推理-行动-观察"三元组。
        """
        # 初始化：用户输入作为第一条消息
        self.conversation_history = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user",   "content": user_input}
        ]

        step = 0
        action_history = []  # 用于检测重复 Action（循环检测）

        while step < self.max_steps:
            step += 1
            print(f"\n{'='*60}")
            print(f"Step {step}/{self.max_steps}")
            print(f"{'='*60}")

            # ── Phase 1: Thought（推理） ──
            # LLM 分析当前状态，输出 Thought + Action 或 Final Answer
            response = self._think()

            # ── Phase 2: 解析 LLM 输出 ──
            # 检查是否为 Final Answer
            final_answer = self._parse_final_answer(response)
            if final_answer:
                print(f"\n✅ 任务完成")
                return final_answer

            # 解析 Action
            action_name, action_input = self._parse_action(response)
            if not action_name:
                # LLM 没有输出有效的 Action，尝试恢复
                print("⚠️  未能解析出有效的 Action，让 LLM 重新思考...")
                self.conversation_history.append({
                    "role": "user",
                    "content": "你的上一条回复中没有有效的 Action。请按格式输出 Action: tool_name 和 Action Input。"
                })
                continue

            # ── Phase 2.5: 循环检测 ──
            action_key = f"{action_name}:{json.dumps(action_input, sort_keys=True)}"
            if action_key in action_history[-3:]:  # 最近3步内重复
                print(f"⚠️  检测到重复 Action: {action_key}")
                self.conversation_history.append({
                    "role": "user",
                    "content": (
                        f"你刚才重复了相同的 Action ({action_name})。"
                        f"这可能是死循环。请检查："
                        f"1. 这个 Action 的返回结果是否和上次一样？"
                        f"2. 是否需要换一种方法？"
                        f"3. 是否已经有足够信息回答用户了？"
                    )
                })
                continue
            action_history.append(action_key)

            # ── Phase 3: Action（执行） ──
            print(f"\n🔧 Action: {action_name}")
            print(f"📥 Input:  {json.dumps(action_input, ensure_ascii=False)}")

            observation = self._execute_action(action_name, action_input)
            print(f"📤 Output: {str(observation)[:300]}")

            # ── Phase 4: Observation（观察结果注入上下文） ──
            # 将 Thought+Action 和 Observation 追加到对话历史
            self.conversation_history.append({
                "role": "assistant",
                "content": response
            })
            self.conversation_history.append({
                "role": "user",
                "content": f"Observation: {observation}"
            })

        # 达到最大步数仍未完成
        return (
            f"任务未能在 {self.max_steps} 步内完成。"
            f"最后的状态：{self.conversation_history[-1]['content'][:500]}"
        )

    # ── LLM 推理（LLM 模块的核心调用） ──

    def _think(self) -> str:
        """调用 LLM 进行推理。

        Temperature 选择：推理阶段使用 0.3-0.5，在逻辑严谨和灵活性之间平衡。
        工具选择阶段实际需要更低 temperature，但单次调用无法分开控制，
        这是课程四 Harness 要解决的问题之一。
        """
        try:
            response = self.llm.chat.completions.create(
                model="gpt-4",
                messages=self.conversation_history,
                temperature=0.3,
                max_tokens=2000
            )
            content = response.choices[0].message.content
            print(f"\n💭 Thought:\n{content[:500]}")
            return content
        except Exception as e:
            print(f"❌ LLM 调用失败: {e}")
            return f"LLM 调用出错: {e}"

    # ── Action 解析 ──

    def _parse_action(self, response: str) -> tuple[str | None, dict | None]:
        """从 LLM 输出中解析 Action 和参数。

        支持两种格式：
        1. Action: tool_name\nAction Input: {"key": "value"}
        2. ```json\n{"action": "tool_name", "action_input": {...}}\n```
        """
        # 格式 1：标准 ReAct 格式
        action_match = re.search(r'Action:\s*(\S+)', response)
        input_match = re.search(r'Action Input:\s*(\{.*?\})', response, re.DOTALL)

        if action_match and input_match:
            action_name = action_match.group(1).strip()
            try:
                action_input = json.loads(input_match.group(1))
                return action_name, action_input
            except json.JSONDecodeError:
                print(f"⚠️  Action Input 不是合法 JSON: {input_match.group(1)[:200]}")
                return action_name, None

        # 格式 2：JSON 块
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                return data.get("action"), data.get("action_input", {})
            except json.JSONDecodeError:
                pass

        return None, None

    def _parse_final_answer(self, response: str) -> str | None:
        """检查 LLM 是否输出了 Final Answer。"""
        match = re.search(r'Final Answer:\s*(.*)', response, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    # ── 工具执行（Tool Use 模块的运行时） ──

    def _execute_action(self, action_name: str, action_input: dict) -> str:
        """执行工具调用并返回 Observation。

        工具执行是 Agent 与外部世界交互的唯一通道。
        所有 RAG 检索、Memory 读写、API 调用都通过这一层完成。
        """
        if action_name not in self.tools:
            available = ", ".join(self.tools.keys())
            return f"错误：没有名为 '{action_name}' 的工具。可用工具：{available}"

        try:
            result = self.tools[action_name](**action_input)
            return str(result)
        except TypeError as e:
            return f"参数错误：{e}。请检查 Action Input 的字段是否与工具定义一致。"
        except Exception as e:
            return f"工具执行出错：{e}"
```

### 执行流程可视化

```
用户输入："帮我查一下最新AI新闻，整理成中文简报"
    │
    v
┌─────────────────────────────────────────────────────────────┐
│ ReAct 循环                                                    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ Step 1                                                │    │
│  │   💭 Thought: 需要搜索最新AI新闻，先用英文搜覆盖面更广  │    │
│  │   🔧 Action: search("latest AI news 2026")            │    │
│  │   📤 Observation: [10条新闻标题和摘要]                  │    │
│  └──────────────────────────────────────────────────────┘    │
│       │                                                       │
│       v                                                       │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ Step 2                                                │    │
│  │   💭 Thought: 结果偏技术，补充搜索中文来源              │    │
│  │   🔧 Action: search("AI 人工智能 最新动态 2026")       │    │
│  │   📤 Observation: [8条中文新闻]                        │    │
│  └──────────────────────────────────────────────────────┘    │
│       │                                                       │
│       v                                                       │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ Step 3                                                │    │
│  │   💭 Thought: 信息足够，可以整理为分类简报              │    │
│  │   📝 Final Answer: # 2026年6月 AI 新闻简报...          │    │
│  └──────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 五大模块在 ReAct 中的角色一览

```
                     ┌──────────────────────┐
                     │  Prompt Engineering   │
                     │  _build_system_prompt │
                     │  角色·规则·工具描述   │
                     └──────────┬───────────┘
                                │ 注入 System Prompt
                                v
    ┌──────────┐     ┌──────────────────┐     ┌──────────┐
    │  Memory  │────>│  conversation_    │<────│   RAG    │
    │  跨会话   │注入 │  history          │ 注入│ 知识检索  │
    │  记忆    │     │  (上下文窗口)      │     │  结果    │
    └──────────┘     └────────┬─────────┘     └──────────┘
                              │
                              v
                     ┌──────────────────┐
                     │       LLM        │
                     │   _think() 调用   │
                     │   推理+决策       │
                     └────────┬─────────┘
                              │ 输出 Thought + Action
                              v
                     ┌──────────────────┐
                     │    Tool Use      │
                     │ _execute_action  │
                     │ 执行工具·返回结果 │
                     └────────┬─────────┘
                              │ Observation
                              v
                     ┌──────────────────┐
                     │  conversation_    │
                     │  history.append   │──> 回到 LLM，下一轮思考
                     └──────────────────┘
```

每个模块在循环中的具体职责：

| 模块 | 在 ReAct 中的位置 | 具体职责 |
|------|-----------------|---------|
| **Prompt Engineering** | 循环启动前 | `_build_system_prompt()` 构建角色、规则、工具描述、CoT 引导 |
| **Memory** | 循环启动前 + 每步追加 | 启动时注入跨会话记忆；每步将 Thought/Action/Observation 追加到 conversation_history |
| **LLM** | 每步的 Thought 阶段 | `_think()` 分析当前状态，决定下一步行动 |
| **Tool Use** | 每步的 Action 阶段 | `_execute_action()` 执行具体工具（搜索、读文件、调 API） |
| **RAG** | Action 阶段的工具之一 | 作为 search/knowledge_base 工具被调用，结果以 Observation 形式注入 |

### 循环检测：防止 Agent "鬼打墙"

Agent 最常见的失败模式之一是死循环——LLM 反复执行相同的 Action 却期望不同的结果。在上面的实现中，`action_history` 记录了最近的操作签名，当检测到 3 步内重复相同的 Action 时，会主动提醒 LLM 检查是否陷入循环。

更完整的循环检测策略（课程四 Orchestration 会深入）：

```python
class LoopDetector:
    """检测并打破 Agent 循环。"""

    def __init__(self, window_size: int = 5):
        self.action_history: list[str] = []
        self.window_size = window_size

    def check(self, action_name: str, action_input: dict) -> str | None:
        """检查当前 Action 是否构成循环。返回干预消息，None 表示正常。"""
        key = f"{action_name}:{json.dumps(action_input, sort_keys=True)}"
        self.action_history.append(key)

        recent = self.action_history[-self.window_size:]

        # 检测 1：严格重复（同一 Action 连续出现 3 次）
        if len(recent) >= 3 and len(set(recent[-3:])) == 1:
            return (
                f"检测到死循环：Action '{action_name}' 已连续执行 3 次。"
                f"请停止当前策略，考虑：结果是否每次相同？是否需要换一种方法？"
                f"是否已经有足够信息来回答用户？"
            )

        # 检测 2：ABAB 模式（两个 Action 交替执行）
        if len(recent) >= 4:
            if recent[-4] == recent[-2] and recent[-3] == recent[-1]:
                return (
                    f"检测到交替循环：'{recent[-2]}' 和 '{recent[-1]}' 交替执行。"
                    f"请检查这两个 Action 的返回结果，判断是否需要改变策略。"
                )

        # 检测 3：Observation 内容不变（不同 Action 但结果相同）
        # 需要在上一层配合，比较 Observation 内容

        return None  # 无循环
```

### ReAct 的局限性——以及课程四的内容预告

完成上述实现后，你可能会注意到几个问题：

1. **单层循环不够用**：复杂任务（如"写一个 Web 应用"）需要先规划子任务，每个子任务内部再有独立的 ReAct 循环。这需要**分层编排**（Orchestration）。

2. **上下文窗口会不断膨胀**：每步的 Thought + Action + Observation 累积起来，长任务会撑爆上下文窗口。这需要**上下文工程**（Context Engineering）——课程四的核心主题之一。

3. **无法知道 Agent 做得对不对**：Agent 完成了任务，但完成得好不好？有没有做多余的动作？这需要**评测体系**（Evaluation）。

4. **遇到意外会很难调试**：Agent 多步执行后出错，回溯每一步发生了什么很痛苦。这需要**可观测性**（Observability）。

这些问题不是 ReAct 的缺陷，而是基础 ReAct 循环的自然边界——它们正是课程四要学习的内容。

---

> **ReAct 小结**：ReAct 是五大核心模块的运行时引擎。Prompt Engineering 设定规则，Memory 保存上下文，LLM 负责推理，Tool Use 负责执行，RAG 作为工具之一提供外部知识——ReAct 循环让它们协同工作。你现在可以跑一个完整的 Agent 了。接下来要解决的问题是：如何让它更稳定、更容易调试、更可评估。

---

## 总结：五大核心模块构成 Agent

回顾这五课内容，每个核心模块都是围绕 LLM 的一个根本局限而发展出来的：

```
       ┌──────────────────────────────────────────────────────────┐
       │               ReAct 循环（运行时引擎）                     │
       │         Thought → Action → Observation → Thought          │
       │                                                          │
       │   ┌──────────────────────────────────────────────────┐   │
       │   │                Agent 五大核心模块                      │   │
       │   │                                                  │   │
       │   │   ┌─────────────────────────┐                    │   │
       │   │   │     Prompt Engineering   │ ← 解决"输出不可控" │   │
       │   │   │   (指挥大脑怎么说和做)    │                    │   │
       │   │   └───────────┬─────────────┘                    │   │
       │   │               │                                   │   │
       │   │   ┌───────────v───────────────┐                   │   │
       │   │   │         LLM 大脑           │                  │   │
       │   │   │   (Transformer + 分词 +    │                   │   │
       │   │   │    上下文 + 采样策略)       │                  │   │
       │   │   └─┬──────┬──────────┬───────┘                  │   │
       │   │     │      │          │                           │   │
       │   │  ┌──v──┐ ┌─v───┐ ┌───v────┐                      │   │
       │   │  │Tool │ │ RAG │ │Memory  │                      │   │
       │   │  │Use  │ │(解决│ │(解决   │                      │   │
       │   │  │(解决│ │知识)│ │"遗忘") │                      │   │
       │   │  │"只能│ │     │ │        │                      │   │
       │   │  │说") │ │     │ │        │                      │   │
       │   │  └──┬──┘ └──┬──┘ └───┬────┘                      │   │
       │   │     │       │        │                            │   │
       │   │     └───────┴────────┘                            │   │
       │   │              │                                    │   │
       │   │       外部世界 & 持久化状态                         │   │
       │   └──────────────────────────────────────────────────┘   │
       └──────────────────────────────────────────────────────────┘
```

图中内层是五大核心模块，各自解决 LLM 的一个根本局限：

| 核心模块 | 解决的局限 | 核心思路 |
|------|----------|---------|
| **LLM 原理** | 不清楚模型为何"不听话" | 理解 Transformer、Tokenization、上下文窗口，才懂怎么设计 |
| **Tool Use** | LLM 只能"说"不能"做" | 让 LLM 输出结构化的工具调用指令，执行后拿到真实结果 |
| **RAG** | 知识截止于训练日期、缺乏专业领域知识 | 检索外部知识库，将相关文档注入上下文 |
| **Memory** | 上下文窗口有限、跨会话无状态 | 管理当前会话上下文 + 持久化跨会话信息 |
| **Prompt Engineering** | LLM 输出不稳定、不可控 | 通过 System Prompt、Few-shot、CoT 精确约束行为 |

**ReAct 循环（图中外层）** 则是运行时引擎。它不解决某个单一的局限，而是将五大核心模块串联为 Thought → Action → Observation 的决策循环——LLM 思考后决定调用哪个工具、检索什么知识、读写哪条记忆，观察结果后再进入下一轮思考。五大核心模块是构成 Agent 的"组件"，ReAct 是让这些组件协同工作的"机制"。

这五大核心模块彼此交织、互相增强。一个好的Agent开发者，不会单独优化其中某一个方面，而是理解它们之间的相互作用——比如如何设计Prompt让Agent更准确地选择工具，如何将RAG的检索结果组织成LLM容易理解的格式，如何在上下文窗口的限制下高效地利用RAG和工具调用，如何在正确的时机让Memory注入相关信息而不打断Agent的当前任务。

---

## 练习任务

1. **ReAct Agent 实现**：实现一个 ReAct Agent 循环，不依赖 LangChain 等高级框架
2. **RAG 系统搭建**：构建一个能检索本地文档并回答问题的 RAG 系统
3. **Memory 最简实现**：为你的 Agent 添加基于 JSON 文件的跨会话记忆（记住用户偏好、近期任务）
4. **Prompt 迭代**：对同一个 Agent，写 3 个版本的 System Prompt，对比行为差异
5. **最小评测集**：为你的 Agent 准备 10 条测试任务，记录每次的成功/失败

**交付物**：

1. 一个 CLI Agent，支持 search（搜索知识库）、read_file（读取本地文件）、calculator（计算器）3 个工具，并具备跨会话记忆能力
2. 一份 RAG 系统设计文档（包含 chunk 大小选择、embedding 模型选择、检索策略的理由）
3. 一份 Memory 实现说明（短期管理策略 + 长期记忆结构 + 记忆注入时机）
4. 一份 Prompt 迭代记录（3 个版本的 System Prompt + 行为对比）
5. 一份评测集（10 条任务）和实测结果

---

## 验收标准

- Agent 能正确选择工具（tool selection 准确率 ≥ 70%）
- 10 条测试任务中成功完成 ≥ 7 条
- 能解释每次失败的原因，并按 tool selection / prompt / schema / 上下文管理 / memory 分类
- RAG 系统的检索 Top-5 召回率 ≥ 60%（在自己的文档集上测试）
- Memory 能在两次独立会话之间正确恢复用户偏好和最近任务记录
- System Prompt 的第三版比第一版有明显改进（用评测集验证）

---

## 实践项目 —— 文件整理 Agent

### 为什么需要这个项目？

课程三的练习让你实现了单个 ReAct Agent，课程四将学习复杂的编排、记忆、评测等架构。这两个课程之间的跨度在于：**从"能跑起来"到"知道为什么需要架构"**。

这个桥梁项目的目标很明确：先做一个多步自主的文件整理 Agent，在做的过程中你会自然地遇到问题——比如"它为什么在某个目录死循环了？""它为什么忘了之前整理过什么？""我该怎么衡量它整理得好不好？"——这些问题正是课程四要系统解决的。

换句话说，**先踩坑，再学理论，理解会更深刻**。

### 1 项目需求

**功能描述**：给出一个目录路径，Agent 自动分析目录中的所有文件，按规则分类整理（如按文件类型、按日期、按项目等），并输出整理报告。

**要求**：
1. Agent 先扫描目录结构（plan 阶段）
2. 制定整理方案并展示给用户确认
3. 用户确认后，逐步执行整理操作
4. 整理完成后输出总结报告

### 2 实现步骤

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

任务完成后，将 trace 保存为 JSON 文件。这个 trace 在课程四学习 Evaluation 时会用到。

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

### 3 复盘模板

完成项目后，用以下模板写一份复盘报告（这是课程四的重要输入）：

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

### 4 桥梁项目 → 课程四的导航

完成复盘后，你会发现：

| 你遇到的问题 | 课程四对应的解决方案 |
|-------------|-------------------|
| Agent 在某个目录死循环 | **Orchestration**：循环控制、停止条件设计 |
| Agent 忘了之前整理过什么 | **Memory**：工作记忆、长期记忆 |
| 不知道怎么衡量整理得好不好 | **Evaluation**：端到端评测、步骤级评测 |
| Agent 移动了不该移动的文件 | **Guardrails**：输出校验、Human-in-the-Loop |
| 不知道 Agent 内部发生了什么 | **Observability**：Tracing、调试工具 |

带着这些问题进入课程四，每个概念都会变得具体而有意义。
