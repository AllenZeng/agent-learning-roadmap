# Course 05-02 RAG 示例项目

基于课程五第2节《外部知识接入：RAG》实现的完整 RAG Pipeline。

## 项目结构

```
python/
├── notes/                      # 知识库：8 篇 Agent 开发主题笔记（与 Node.js 共享）
├── offline_pipeline.py         # 离线建库：笔记 → 解析 → Chunk → Embedding → 索引
├── online_pipeline.py          # 在线查询：问题 → 召回 → 重排序 → 上下文组装
├── output/                     # 生成的索引文件（运行后产生，已 gitignore）
└── requirements.txt

nodejs/
├── notes/                      # 同上（独立副本）
├── offline_pipeline.mjs        # 离线建库（Node.js 实现）
├── online_pipeline.mjs         # 在线查询（Node.js 实现）
├── index/                      # 生成的索引文件
└── package.json
```

## 快速开始

> 首次运行会从 Hugging Face 下载 Embedding 模型。没有网络或缓存不可用时，离线建库和在线查询会在加载模型阶段失败。

### Python

```bash
cd python
pip install -r requirements.txt
python offline_pipeline.py
python online_pipeline.py "Tool Use 和 Memory 的设计哲学有什么区别？"
python online_pipeline.py --interactive
```

### Node.js

```bash
cd nodejs
npm install
node offline_pipeline.mjs
node online_pipeline.mjs "Tool Use 和 Memory 的设计哲学有什么区别？"
node online_pipeline.mjs --interactive
```

## Pipeline 流程

### 离线阶段

```
原始笔记 (*.md)
  → 扫描 + 解析 frontmatter（§2.4.2）
  → 清洗（去噪、统一格式）
  → Chunking 按 ## 标题切分（§2.4.3）
  → 元数据标注（source、section_path、tags、status、时间）
  → 过滤草稿
  → Embedding（all-MiniLM-L6-v2）+ BM25 索引（§2.4.4）
  → Python 保存到 output/，Node.js 保存到 index/
```

### 在线阶段

```
用户问题
  → 查询理解（同义词扩展、指代检测）（§2.4.5）
  → 多路召回：向量语义 + BM25 关键词（§2.4.6）
  → 元数据过滤（排除草稿）
  → RRF 融合去重
  → 重排序（分数断崖检测 → 自动截断）
  → 上下文组装（来源标注、引用对齐）（§2.4.7）
  → 输出最终 Prompt
```

## 设计要点

- **混合检索**：向量保证语义泛化（不漏），BM25 保证精确匹配（不错），RRF 融合取两者之长
- **元数据驱动**：`status=draft` 的草稿笔记默认不进入检索范围
- **分数断崖**：rerank 后相邻 chunk 分数差 > 30% 时自动截断，避免噪声进入上下文
- **来源追溯**：每个 chunk 标注文件名、小节路径、更新时间，生成回答时可引用
- **本地存储**：向量存为 `.npy` 文件，无需外部向量数据库，适合学习和演示

## 教学简化说明

- 示例重点是让你看清 RAG 的离线建库和在线查询链路，不是生产级检索系统。
- 代码使用简单正则分词实现 BM25，对中文不会做专业分词；真实中文知识库应接入中文分词、字符 n-gram、学习型 sparse retrieval，或直接使用支持中文的检索服务。
- 默认 Embedding 模型 `all-MiniLM-L6-v2` 更适合英文教学演示；中文或中英混合语料建议替换为 BGE-M3、multilingual-e5 等多语言检索模型，并重新构建索引和评测集。
- `generate_answer()` / `generateAnswer()` 只输出最终 Prompt，没有调用真实 LLM；接入模型 API 后还需要做引用校验、低置信度拒答和 prompt injection 防护。

## 笔记内容

8 篇笔记覆盖课程涉及的核心主题，包含：
- YAML frontmatter 元数据（时间、标签、状态）
- Markdown 标题层级（h1/h2/h3）
- 代码块示例
- [[wiki]] 格式的交叉引用
- 不同完成度（7 篇 published + 1 篇 draft，展示草稿过滤）
