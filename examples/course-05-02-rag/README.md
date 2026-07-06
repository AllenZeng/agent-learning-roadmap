# Course 05-02 RAG 示例项目

基于课程五第2节《外部知识接入：RAG》实现的完整 RAG Pipeline。

## 项目结构

```
python/
├── notes/                      # 知识库：8 篇 Agent 开发主题笔记（与 Node.js 共享）
├── offline_pipeline.py         # 离线建库：笔记 → 解析 → Chunk → 伪 Embedding → 索引
├── online_pipeline.py          # 在线查询：问题 → 召回 → 重排序 → 上下文组装
├── retrieval_core.py           # 分词、BM25、hashing TF-IDF 伪向量
├── output/                     # 生成的索引文件（运行后产生，已 gitignore）
└── requirements.txt

nodejs/
├── notes/                      # 同上（独立副本）
├── offline_pipeline.mjs        # 离线建库（Node.js 实现）
├── online_pipeline.mjs         # 在线查询（Node.js 实现）
├── retrieval_core.mjs          # 分词、BM25、hashing TF-IDF 伪向量
├── output/                     # 生成的索引文件
└── package.json
```

## 快速开始

> 本示例默认不依赖外部向量数据库，向量召回使用 deterministic hashing TF-IDF 伪 embedding，用于教学演示 RAG 的完整链路。

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
npm run offline
npm run online -- "Tool Use 和 Memory 的设计哲学有什么区别？"
npm run online -- --interactive
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
  → 伪 Embedding（hashing TF-IDF）+ BM25 索引（§2.4.4）
  → 保存到 output/
```

### 在线阶段

```
用户问题
  → 查询理解（同义词扩展、指代检测）（§2.4.5）
  → 多路召回：伪向量 + BM25 关键词（§2.4.6）
  → 元数据过滤（排除草稿）
  → RRF 融合去重
  → 重排序（分数断崖检测 → 自动截断）
  → 上下文组装（来源标注、引用对齐）（§2.4.7）
  → 输出最终 Prompt
```

## 教学简化说明

- 示例重点是让你看清 RAG 的离线建库和在线查询链路，不是生产级检索系统。
- 代码使用中文单字 + bigram、英文/数字 word token 的简化分词，足够支撑教学演示；真实中文知识库应接入更专业的中文分词、学习型 sparse retrieval，或直接使用支持中文的检索服务。
- 伪 embedding 不是语义模型，不能真正理解同义词和深层语义。它的价值是让示例无网络、无模型下载、开箱可跑，同时保留“向量召回 + BM25 + RRF + rerank”的结构。
