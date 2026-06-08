# 阶段六：构建作品集（持续实践）

> **课程定位**：本阶段是Agent学习路径的收官阶段。前五个阶段你已经掌握了理论基础、工具使用、框架原理和评估方法，现在需要将这些能力转化为实际可展示的作品。本课程包含三个难度递进的项目，从入门级的知识助手到中级的代码审查Agent，再到高级的垂直领域产品。每个项目都可以独立成为一个完整的作品集案例。

---

## 目录

1. [教学方法说明](#教学方法说明)
2. [项目一：个人知识助手Agent](#项目一个人知识助手agent)
3. [项目二：代码审查Agent](#项目二代码审查agent)
4. [项目三：领域Agent产品](#项目三领域agent产品)
5. [通用方法论：如何做好一个Agent项目](#通用方法论如何做好一个agent项目)
6. [课程总结与下一步](#课程总结与下一步)

---

## 教学方法说明

在正式进入项目之前，我想和你分享一个重要的学习理念。

很多人学习技术的方式是"看懂了就以为自己会了"。他们读完文档、看完教程、理解了概念，就跳到下一个主题。但事实是：**只有你亲手搭建出来的东西，才是你真正掌握的**。

这三个项目的设计遵循"爬-走-跑"的节奏：

- **项目一（知识助手）** 是"爬"，它覆盖了Agent开发的所有基本环节，让你跑通第一个完整的Agent循环。即使你之前没有独立做过Agent，跟着教程也能完成。
- **项目二（代码审查）** 是"走"，它引入了外部服务集成、结构化输出和领域知识注入这些真实项目中必须面对的问题。你需要自己处理更多的边界情况。
- **项目三（领域产品）** 是"跑"，这个阶段我不再给你完整的代码，而是给你设计框架和关键决策点的指导。你需要结合自己的领域知识，做出真正属于你的产品。

每个项目的课程结构如下：

1. **课前思考**：先让你自己思考几个关键问题，带着问题学习
2. **设计思路**：为什么要这样做，而不那样做
3. **技术选型理由**：每个技术决策背后的权衡
4. **完整实现步骤**：跟着教程一步步做出成品
5. **常见问题与解决方案**：整理了历届学员最常遇到的坑
6. **课后作业**：巩固学习成果的练习

让我们开始吧。

---

## 阶段概览

### 🎯 学习目标

完成本阶段后，你将能够：
1. 独立从零设计并实现一个完整的 Agent 产品
2. 根据需求选择合适的技术栈，并说明选型理由
3. 将阶段一到阶段四学到的所有能力（Tool Use、编排、记忆、评测、护栏、交互、可靠性、成本控制）整合到一个项目中
4. 建立自己的 Agent 开发方法论和代码库

### 📥 前置输入

- 已完成阶段一到阶段四的系统学习
- 有一个经过多轮迭代的 Agent 项目基础（可以基于阶段二/三的项目继续开发）
- 对某个应用场景有深入的领域理解（数据分析、客服、法律、运维等）

### 🏋️ 练习任务

根据你的时间和技术水平，选择以下三个项目之一深度完成：

1. **个人知识助手 Agent**（入门）：适合刚学完阶段二、想巩固基础的学员
2. **代码审查 Agent**（中级）：适合有 GitHub 使用经验、想做更复杂工具集成的学员
3. **领域 Agent 产品**（高级）：适合在自己的领域有一定积累、想做端到端产品的学员

### 📦 交付物

1. 完整的项目代码（GitHub 仓库）
2. 一份技术设计文档（架构、技术选型理由、关键决策记录）
3. 一份项目复盘报告（遇到的问题、解决方案、如果重做会怎么改进）
4. 一份评测报告（用阶段三学的评测框架，对最终版本做一次完整评测）

### ✅ 验收标准

每个项目有三级标准，根据自身情况选择达标级别：

**项目一：个人知识助手 Agent**

| 级别 | 标准 |
|------|------|
| **合格版** | Agent 能检索本地文档并回答事实性问题；支持至少 2 个工具；正确率 ≥ 60%（10 条评测） |
| **进阶版** | 支持混合检索 + Rerank；有多轮对话记忆；流式输出；正确率 ≥ 80%（20 条评测）；有完整的评测报告 |
| **产品版** | 有 Web 界面；支持多用户和多知识库；有使用数据统计；正确率 ≥ 90%（50 条评测）；有错误分类分析和改进路线图 |

**项目二：代码审查 Agent**

| 级别 | 标准 |
|------|------|
| **合格版** | 能读取 PR diff 并输出结构化的审查意见；覆盖安全和正确性两类检查 |
| **进阶版** | 能调用测试、静态分析工具；获取变更文件的上下文代码；支持自定义审查规则；审查意见有置信度标注 |
| **产品版** | 集成 GitHub App 自动触发；在 PR 中发布行内评论；有误报反馈机制；有审计日志和审查质量评测集 |

**项目三：领域 Agent 产品**

| 级别 | 标准 |
|------|------|
| **合格版** | 核心功能可用；在 5 个典型场景中能正确完成任务；有基本的错误处理 |
| **进阶版** | 覆盖 20+ 场景；有评测集和评测报告；有交互优化（流式、进度、确认节点）；成本可控 |
| **产品版** | 有真实用户（哪怕是内部同事）使用过并给出反馈；有监控和告警；有持续迭代的计划和实际迭代记录 |

---

## 项目一：个人知识助手Agent

> **难度等级**：入门 | **建议用时**：10 天 | **达标目标**：至少达到"合格版"，鼓励冲击"进阶版"

### 课前思考

在开始写代码之前，请花5分钟思考以下问题：

1. 你平时是如何管理自己的学习笔记和文档的？遇到问题时，你通常怎么找到之前记录的答案？
2. 如果你让ChatGPT回答一个关于你个人项目的问题，它能回答吗？为什么？
3. 普通的关键词搜索（Ctrl+F）和"理解你的意图后搜索"有什么区别？

带着这些思考，我们来构建一个能真正理解你、帮你管理知识的个人助手。

### 设计思路

#### 从用户需求出发

个人知识助手要解决的核心问题是：**如何让AI访问你的私有知识，并用这些知识来回答你的问题**。

这个需求拆解开来包含三个子问题：

1. **知识在哪里？** —— 你的笔记、PDF、网页剪藏分散在各处，Agent需要能访问它们
2. **怎么找到相关知识？** —— 你的问题是自然语言（"我之前学到的关于数据库索引优化的笔记"），但知识存储在文件中
3. **找到后怎么用？** —— 找到相关文档后，Agent需要理解内容，并结合上下文生成有用的回答

#### Agent的核心循环

这个项目会让你理解和实现Agent最核心的模式——**ReAct循环**（Reasoning + Acting）：

```
用户: "帮我整理一下关于Transformer架构的学习笔记"

Agent思考: 我需要先去知识库中搜索"Transformer 架构"
  → 调用工具: search_knowledge_base("Transformer 架构")
  → 工具返回: [找到了3篇相关笔记]

Agent思考: 这3篇笔记内容足够丰富，我可以整理一份总结
  → 生成回答: "根据你的笔记，Transformer架构的核心要点是..."

Agent思考: 这份整理值得保存下来
  → 调用工具: save_note("Transformer架构学习总结", 整理的内容)
  → 工具返回: 笔记已保存

Agent: "我已经为你整理了Transformer架构的学习笔记并保存。"
```

这个循环的精妙之处在于：Agent不只是"回答问题"，而是像一个真正的研究助理一样，**主动使用工具、多步推理、持续优化结果**。

#### 为什么会选择RAG而不是微调？

这是很多初学者都会问的问题。核心原因有三：

1. **知识更新成本**：微调需要重新训练（或至少重新微调）模型，耗时且昂贵。RAG只需要更新向量数据库中的文档，即时生效。
2. **知识来源可追溯**：RAG可以明确告诉用户"这个答案来自你10月5日的笔记"，微调模型则无法追溯信息来源。
3. **知识隔离**：RAG将知识存储在外部，不污染模型的通用能力。微调可能造成灾难性遗忘。

对于个人知识助手这个场景，你的知识每天在增长和变化，RAG是最合适的选择。

### 技术选型理由

#### 为什么用向量数据库？

让我们对比三种检索方式：

| 检索方式 | 原理 | 优点 | 缺点 |
|---------|------|------|------|
| 关键词搜索（BM25） | 精确匹配词语 | 快，精确匹配有效 | 不理解语义，"汽车"搜不到"轿车" |
| 语义检索（Embedding） | 向量相似度 | 理解语义，容错性强 | 计算成本较高，可能召回不相关内容 |
| 混合检索 | 两者结合 | 取长补短 | 实现稍复杂，需要融合排序 |

向量数据库是语义检索的存储和计算基础设施。它将文本转换为高维向量（embedding），相似的文本在向量空间中距离更近。

#### 为什么选ChromaDB？

对于学习阶段，ChromaDB有不可替代的优势：

- **零配置**：`pip install chromadb` 即可使用，不需要Docker、不需要独立服务
- **内置Embedding**：内置了sentence-transformers，不调用外部API也能跑通
- **Python原生**：API设计简洁，学习曲线平缓
- **足够快**：十万级别的文档量，检索速度在毫秒级

生产环境可能会换用Milvus、Qdrant或Pinecone，但学习阶段ChromaDB是最佳选择。

#### 为什么需要Rerank？

很多人忽略Rerank环节，直接将向量检索的Top-K结果喂给LLM。但实际上：

- **向量检索的Top-1精度通常在60%-70%**，这意味着有30%-40%的情况下，最相关的文档并不在第一位
- **Rerank可以将精度提升到85%-95%**

Rerank的原理是使用一个更强大的模型（通常是Cross-Encoder），将查询和每个候选文档拼在一起，做一个更精细的相关性判断。典型的pipeline是：

```
用户查询 → 向量检索（粗筛，召回100条） → Rerank（精排，保留Top-5） → 喂给LLM
```

第一阶段追求召回率（不遗漏相关文档），第二阶段追求精确率（只保留最相关的）。

### 完整实现步骤

#### 第1天：环境搭建

**1.1 创建项目结构**

```bash
mkdir personal-knowledge-agent
cd personal-knowledge-agent
mkdir -p src/{core,knowledge_base,tools,ui} data/documents tests
```

项目目录说明：
- `src/core/`：Agent核心循环逻辑
- `src/knowledge_base/`：知识库构建与检索
- `src/tools/`：工具定义与实现
- `src/ui/`：交互界面
- `data/documents/`：存放原始文档
- `tests/`：测试文件

**1.2 创建虚拟环境并安装依赖**

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

创建 `requirements.txt`：

```
chromadb>=0.4.0
openai>=1.0.0
anthropic>=0.18.0
sentence-transformers>=2.2.0
pypdf2>=3.0.0
markdown>=3.4.0
beautifulsoup4>=4.12.0
rich>=13.0.0
python-dotenv>=1.0.0
tiktoken>=0.5.0
```

```bash
pip install -r requirements.txt
```

**1.3 配置API Key**

创建 `.env` 文件（记得加入 `.gitignore`）：

```
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

创建 `src/config.py`：

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # LLM配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    
    # 模型选择
    LLM_MODEL = "gpt-4o"  # 或 "claude-sonnet-4-20250514"
    
    # Embedding配置
    EMBEDDING_MODEL = "text-embedding-3-small"
    
    # 向量数据库
    CHROMA_PERSIST_DIR = "./data/chroma_db"
    
    # 检索配置
    TOP_K_RETRIEVAL = 20      # 初次检索返回数量
    TOP_K_RERANK = 5          # Rerank后保留数量
    CHUNK_SIZE = 500          # 文档分块大小
    CHUNK_OVERLAP = 50        # 分块重叠大小
    
    # Agent配置
    MAX_STEPS = 10            # 最大循环步数
```

#### 第2-3天：知识库构建

**2.1 文档解析器**

创建 `src/knowledge_base/document_parser.py`：

```python
from typing import List, Dict
import os
from pathlib import Path
import pypdf2
import markdown
from bs4 import BeautifulSoup

class DocumentParser:
    """解析不同格式的文档，提取纯文本内容"""
    
    def parse_file(self, file_path: str) -> Dict:
        """解析单个文件，返回文档元信息和内容"""
        path = Path(file_path)
        ext = path.suffix.lower()
        
        if ext == '.md':
            content = self._parse_markdown(file_path)
        elif ext == '.pdf':
            content = self._parse_pdf(file_path)
        elif ext == '.txt':
            content = self._parse_text(file_path)
        elif ext in ['.html', '.htm']:
            content = self._parse_html(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {ext}")
        
        return {
            "file_path": file_path,
            "file_name": path.name,
            "content": content,
            "file_type": ext
        }
    
    def _parse_markdown(self, file_path: str) -> str:
        """解析Markdown文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        # 转换为纯文本（移除Markdown标记）
        html = markdown.markdown(md_content)
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text()
    
    def _parse_pdf(self, file_path: str) -> str:
        """解析PDF文件"""
        texts = []
        with open(file_path, 'rb') as f:
            reader = pypdf2.PdfReader(f)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    texts.append(text)
        return '\n'.join(texts)
    
    def _parse_text(self, file_path: str) -> str:
        """解析纯文本文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _parse_html(self, file_path: str) -> str:
        """解析HTML文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        # 移除script和style标签
        for tag in soup(['script', 'style']):
            tag.decompose()
        return soup.get_text()
```

**2.2 文本分块器（Chunker）**

创建 `src/knowledge_base/chunker.py`：

```python
from typing import List
import tiktoken

class TextChunker:
    """将长文本切分为适合Embedding的小块"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def chunk(self, text: str) -> List[str]:
        """
        将文本切分为多个chunk
        
        切分策略：
        1. 首先按段落(\n\n)切分
        2. 如果段落仍然过长，按句子切分
        3. 合并句子直到接近chunk_size，保留chunk_overlap
        """
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # 如果当前段落单独就超过了chunk_size
            if self._token_count(para) > self.chunk_size:
                # 保存当前chunk
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                # 将长段落按句子切分
                sentences = self._split_sentences(para)
                for sentence in sentences:
                    if self._token_count(current_chunk + sentence) > self.chunk_size:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                            # 保留重叠部分
                            overlap_text = self._get_last_n_tokens(
                                current_chunk, self.chunk_overlap
                            )
                            current_chunk = overlap_text + sentence
                        else:
                            current_chunk = sentence
                    else:
                        current_chunk += sentence
            else:
                # 正常情况：段落 + 当前chunk 不超过限制
                if self._token_count(current_chunk + para) > self.chunk_size:
                    chunks.append(current_chunk.strip())
                    overlap_text = self._get_last_n_tokens(
                        current_chunk, self.chunk_overlap
                    )
                    current_chunk = overlap_text + '\n\n' + para
                else:
                    if current_chunk:
                        current_chunk += '\n\n'
                    current_chunk += para
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _token_count(self, text: str) -> int:
        """计算文本的token数量"""
        return len(self.tokenizer.encode(text))
    
    def _split_sentences(self, text: str) -> List[str]:
        """简单的句子切分"""
        import re
        sentences = re.split(r'(?<=[。！？.!?])\s*', text)
        return [s for s in sentences if s.strip()]
    
    def _get_last_n_tokens(self, text: str, n: int) -> str:
        """获取文本最后n个token对应的文字"""
        tokens = self.tokenizer.encode(text)
        if len(tokens) <= n:
            return text
        return self.tokenizer.decode(tokens[-n:])
```

**chunk_size的选择技巧**：

一般来说，chunk_size的选择遵循以下经验法则：

- **太小（< 100 tokens）**：语义信息不足，检索精度下降
- **适中（300-800 tokens）**：最常见的选择，平衡了语义完整性和检索精度
- **太大（> 2000 tokens）**：单个chunk包含过多信息，检索精确度下降，且LLM处理时容易忽略关键信息

建议从500开始，根据你的文档类型调整。技术文档通常偏短（300-500），长篇文章可以偏长（800-1000）。

**2.3 Embedding生成与入库**

创建 `src/knowledge_base/vector_store.py`：

```python
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Optional
import uuid

class VectorStore:
    """向量数据库管理器"""
    
    def __init__(
        self, 
        persist_dir: str = "./data/chroma_db",
        embedding_model: str = "text-embedding-3-small"
    ):
        self.client = chromadb.PersistentClient(path=persist_dir)
        
        # 选择Embedding函数
        if embedding_model.startswith("text-embedding"):
            # OpenAI Embedding
            import openai
            import os
            self.embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
                api_key=os.getenv("OPENAI_API_KEY"),
                model_name=embedding_model
            )
        else:
            # 本地Embedding模型（默认sentence-transformers）
            self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        
        self.collection_name = "personal_knowledge"
        self.collection = self._get_or_create_collection()
    
    def _get_or_create_collection(self):
        """获取或创建集合"""
        try:
            return self.client.get_collection(
                self.collection_name,
                embedding_function=self.embedding_fn
            )
        except Exception:
            return self.client.create_collection(
                self.collection_name,
                embedding_function=self.embedding_fn,
                metadata={"hnsw:space": "cosine"}
            )
    
    def add_documents(
        self, 
        chunks: List[str], 
        metadatas: List[Dict],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        将文档块添加到向量数据库
        
        参数:
            chunks: 文档块文本列表
            metadatas: 每个块的元信息（来源文件、位置等）
            ids: 可选的ID列表，不提供则自动生成
        
        返回:
            添加的文档ID列表
        """
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in chunks]
        
        self.collection.add(
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        return ids
    
    def search(
        self, 
        query: str, 
        top_k: int = 20,
        where: Optional[Dict] = None
    ) -> Dict:
        """
        语义检索
        
        参数:
            query: 查询文本
            top_k: 返回数量
            where: 过滤条件（例如只搜索特定文件的文档）
        
        返回:
            包含ids, documents, metadatas, distances的结果字典
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where
        )
        return {
            "ids": results["ids"][0],
            "documents": results["documents"][0],
            "metadatas": results["metadatas"][0],
            "distances": results["distances"][0]
        }
    
    def delete_collection(self):
        """删除整个集合（重新构建知识库时使用）"""
        self.client.delete_collection(self.collection_name)
        self.collection = self._get_or_create_collection()
```

**2.4 知识库构建流水线**

创建 `src/knowledge_base/builder.py`：

```python
import os
from pathlib import Path
from typing import List
from .document_parser import DocumentParser
from .chunker import TextChunker
from .vector_store import VectorStore
from src.config import Config

class KnowledgeBaseBuilder:
    """知识库构建流水线"""
    
    def __init__(self):
        self.parser = DocumentParser()
        self.chunker = TextChunker(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )
        self.vector_store = VectorStore(
            persist_dir=Config.CHROMA_PERSIST_DIR
        )
    
    def build_from_directory(self, doc_dir: str) -> int:
        """
        从目录构建知识库
        
        流程：
        1. 扫描所有文档文件
        2. 解析每个文件
        3. 分块
        4. 生成Embedding并存入向量数据库
        """
        doc_path = Path(doc_dir)
        supported_exts = ['.md', '.pdf', '.txt', '.html', '.htm']
        
        total_chunks = 0
        files = []
        
        # 收集所有支持的文档
        for ext in supported_exts:
            files.extend(doc_path.glob(f"**/*{ext}"))
        
        print(f"找到 {len(files)} 个文档")
        
        for file_path in files:
            try:
                # 1. 解析文档
                doc = self.parser.parse_file(str(file_path))
                print(f"解析: {doc['file_name']}")
                
                # 2. 分块
                chunks = self.chunker.chunk(doc['content'])
                print(f"  分为 {len(chunks)} 个块")
                
                # 3. 构造元数据
                metadatas = []
                for i, chunk in enumerate(chunks):
                    metadatas.append({
                        "file_name": doc['file_name'],
                        "file_path": str(file_path),
                        "file_type": doc['file_type'],
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    })
                
                # 4. 存入向量数据库
                self.vector_store.add_documents(chunks, metadatas)
                total_chunks += len(chunks)
                
            except Exception as e:
                print(f"  处理文件 {file_path} 时出错: {e}")
                continue
        
        print(f"\n知识库构建完成，共 {total_chunks} 个文档块")
        return total_chunks
    
    def add_single_document(self, file_path: str) -> int:
        """添加单个文档到知识库"""
        doc = self.parser.parse_file(file_path)
        chunks = self.chunker.chunk(doc['content'])
        metadatas = []
        for i, chunk in enumerate(chunks):
            metadatas.append({
                "file_name": doc['file_name'],
                "file_path": str(file_path),
                "file_type": doc['file_type'],
                "chunk_index": i,
                "total_chunks": len(chunks)
            })
        self.vector_store.add_documents(chunks, metadatas)
        return len(chunks)
```

#### 第3-4天：检索模块

**3.1 混合检索器**

创建 `src/knowledge_base/retriever.py`：

```python
from typing import List, Dict
import re
from .vector_store import VectorStore
from src.config import Config

class HybridRetriever:
    """混合检索器：结合语义检索和关键词检索"""
    
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.top_k_retrieval = Config.TOP_K_RETRIEVAL
    
    def retrieve(self, query: str) -> List[Dict]:
        """
        混合检索
        
        策略：
        1. 语义检索获取top_k_retrieval条结果
        2. 关键词检索（BM25）获取top_k_retrieval条结果
        3. 使用倒数排名融合（Reciprocal Rank Fusion）合并排序
        """
        # 语义检索
        semantic_results = self._semantic_search(query)
        
        # 关键词检索
        keyword_results = self._keyword_search(query)
        
        # 融合排序
        fused_results = self._reciprocal_rank_fusion(
            semantic_results, keyword_results
        )
        
        return fused_results
    
    def _semantic_search(self, query: str) -> List[Dict]:
        """语义检索"""
        results = self.vector_store.search(query, top_k=self.top_k_retrieval)
        formatted = []
        for i in range(len(results["ids"])):
            formatted.append({
                "id": results["ids"][i],
                "content": results["documents"][i],
                "metadata": results["metadatas"][i],
                "score": 1 - results["distances"][i],  # 距离转相似度
                "source": "semantic",
                "rank": i + 1
            })
        return formatted
    
    def _keyword_search(self, query: str) -> List[Dict]:
        """关键词检索（简易BM25）"""
        # 提取查询中的关键词
        keywords = self._extract_keywords(query)
        if not keywords:
            return []
        
        # 从向量数据库获取所有文档做关键词匹配
        # 注意：ChromaDB 的 get 方法可以按条件过滤
        all_docs = self.vector_store.collection.get()
        
        scored = []
        for i, doc in enumerate(all_docs["documents"]):
            score = self._bm25_score(doc, keywords)
            if score > 0:
                scored.append({
                    "id": all_docs["ids"][i],
                    "content": doc,
                    "metadata": all_docs["metadatas"][i] if all_docs["metadatas"] else {},
                    "score": score,
                    "source": "keyword"
                })
        
        # 按分数排序，取top_k
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:self.top_k_retrieval]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """从查询中提取关键词"""
        # 简单的中英文分词
        # 英文：按空格和标点分割，过滤停用词
        # 中文：这里用简单的字符级处理，生产环境建议用jieba
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 
                     '的', '了', '在', '是', '我', '有', '和', '就',
                     '不', '人', '都', '一', '个', '上', '也', '很'}
        
        # 分词
        words = re.findall(r'[一-鿿]|[a-zA-Z]+', text.lower())
        return [w for w in words if w not in stopwords and len(w) > 1]
    
    def _bm25_score(self, document: str, keywords: List[str]) -> float:
        """简易BM25评分"""
        doc_lower = document.lower()
        score = 0.0
        k1 = 1.5  # BM25参数
        b = 0.75
        
        doc_len = len(doc_lower.split())
        avg_doc_len = 200  # 简化：假设平均文档长度
        
        for keyword in keywords:
            # 词频
            tf = doc_lower.count(keyword)
            if tf == 0:
                continue
            
            # BM25公式简化版
            tf_component = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * doc_len / avg_doc_len))
            score += tf_component
        
        return score
    
    def _reciprocal_rank_fusion(
        self, 
        results_a: List[Dict], 
        results_b: List[Dict],
        k: int = 60
    ) -> List[Dict]:
        """
        倒数排名融合
        
        原理：对每个文档，计算它在两个结果列表中的排名的倒数和
        score = 1/(k + rank_in_A) + 1/(k + rank_in_B)
        """
        scores = {}
        doc_map = {}
        
        # 处理第一个结果集
        for i, doc in enumerate(results_a):
            doc_id = doc["id"]
            scores[doc_id] = 1.0 / (k + i + 1)
            doc_map[doc_id] = doc
        
        # 处理第二个结果集
        for i, doc in enumerate(results_b):
            doc_id = doc["id"]
            if doc_id in scores:
                scores[doc_id] += 1.0 / (k + i + 1)
            else:
                scores[doc_id] = 1.0 / (k + i + 1)
                doc_map[doc_id] = doc
        
        # 排序
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        
        results = []
        for doc_id in sorted_ids[:self.top_k_retrieval]:
            doc = doc_map[doc_id].copy()
            doc["fusion_score"] = scores[doc_id]
            results.append(doc)
        
        return results
```

**3.2 Reranker**

创建 `src/knowledge_base/reranker.py`：

```python
from typing import List, Dict
from openai import OpenAI
from src.config import Config
import os

class Reranker:
    """使用LLM进行重排序"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.top_k = Config.TOP_K_RERANK
    
    def rerank(self, query: str, candidates: List[Dict]) -> List[Dict]:
        """
        对候选文档进行重排序
        
        方法：使用LLM作为Cross-Encoder，对每个候选文档评估相关性。
        
        对于大量候选文档（> 30），也可以使用专门的Rerank API
        （如Cohere Rerank），但LLM打分更灵活且无需额外服务。
        """
        if len(candidates) <= self.top_k:
            return candidates
        
        # 为每个候选文档评分
        scored = []
        for i, doc in enumerate(candidates):
            relevance_score = self._score_relevance(query, doc["content"])
            scored.append({
                **doc,
                "relevance_score": relevance_score
            })
        
        # 按相关性排序
        scored.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored[:self.top_k]
    
    def _score_relevance(self, query: str, document: str) -> float:
        """
        用LLM评估文档与查询的相关性
        
        返回0-10的分数
        """
        prompt = f"""评估以下文档与查询的相关性。请给出0-10的分数。

查询: {query}

文档: {document[:1000]}

评分标准:
- 0-2: 完全不相关
- 3-4: 略微相关但信息量不足
- 5-6: 部分相关
- 7-8: 高度相关，包含有用的信息
- 9-10: 完全匹配，直接回答了查询

只返回一个数字（0-10），不要返回其他内容。"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # 使用便宜模型做rerank
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=5
            )
            score_text = response.choices[0].message.content.strip()
            return float(score_text) / 10.0
        except Exception:
            # 降级：如果LLM评分失败，使用原始检索分数
            return 0.5
```

#### 第4-6天：Agent核心循环

**4.1 工具定义**

创建 `src/tools/definitions.py`：

```python
"""
工具定义

这是在Agent开发中最容易被低估但又最关键的环节。
工具的描述本质上就是Agent的"世界模型"——Agent对它能做什么的认知，
完全来自于这些描述。写得不好，Agent就像一个看不清东西的人，
不知道该用什么工具。
"""

TOOLS = [
    {
        "name": "search_knowledge_base",
        "description": (
            "在个人知识库中搜索相关文档。当你需要查找用户之前保存的笔记、"
            "学习材料或任何私人知识时使用。支持自然语言查询，会返回最相关的"
            "文档片段及其来源信息。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索查询，用自然语言描述你想找什么内容。"
                                   "例如：'Transformer架构中的自注意力机制'"
                },
                "top_k": {
                    "type": "integer",
                    "description": "返回的文档片段数量，默认5",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_web",
        "description": (
            "搜索互联网获取最新信息。当知识库中没有相关内容，或需要实时"
            "信息时使用。注意：这个工具的结果来自公共网络，可能包含不准确"
            "的信息，使用时需要标注来源。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索查询"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "save_note",
        "description": (
            "保存一条笔记到知识库。当你整理出有价值的总结，或想记住某个"
            "信息时使用。笔记会自动被索引，以后可以搜索到。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "笔记标题"
                },
                "content": {
                    "type": "string",
                    "description": "笔记的完整内容"
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "用于分类的标签列表"
                }
            },
            "required": ["title", "content"]
        }
    }
]
```

**4.2 工具执行器**

创建 `src/tools/executor.py`：

```python
from typing import Dict, Any, Optional
from src.knowledge_base.vector_store import VectorStore
from src.knowledge_base.retriever import HybridRetriever
from src.knowledge_base.reranker import Reranker
from src.config import Config
import json

class ToolExecutor:
    """工具执行器——桥接Agent决策和实际操作"""
    
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.retriever = HybridRetriever(vector_store)
        self.reranker = Reranker()
    
    def execute(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """
        执行工具调用并返回结果
        
        关键设计原则：
        - 工具返回的是"Agent能理解的自然语言描述"
        - 不能返回原始的二进制数据或内部数据结构
        - 必须包含足够的上下文让Agent判断下一步动作
        """
        if tool_name == "search_knowledge_base":
            return self._search_knowledge_base(parameters)
        elif tool_name == "search_web":
            return self._search_web(parameters)
        elif tool_name == "save_note":
            return self._save_note(parameters)
        else:
            return f"错误: 未知工具 '{tool_name}'。可用工具有：search_knowledge_base, search_web, save_note"
    
    def _search_knowledge_base(self, params: Dict) -> str:
        """搜索知识库"""
        query = params["query"]
        top_k = params.get("top_k", 5)
        
        # 1. 混合检索
        candidates = self.retriever.retrieve(query)
        
        # 2. Rerank
        results = self.reranker.rerank(query, candidates)
        results = results[:top_k]
        
        if not results:
            return "知识库中没有找到相关内容。建议尝试使用 search_web 工具搜索网络，或调整查询关键词。"
        
        # 格式化返回结果
        formatted = []
        for i, doc in enumerate(results):
            source = doc["metadata"].get("file_name", "未知来源")
            formatted.append(
                f"[{i+1}] 来源: {source}\n"
                f"相关性分数: {doc.get('relevance_score', doc.get('score', 0)):.2f}\n"
                f"内容: {doc['content'][:500]}..."
            )
        
        return f"在知识库中找到 {len(results)} 个相关结果：\n\n" + "\n\n".join(formatted)
    
    def _search_web(self, params: Dict) -> str:
        """搜索网络（简化实现，生产环境应接入真实搜索API）"""
        query = params["query"]
        return (
            f"注意: 网络搜索功能需要配置搜索API（如Bing Search API或SerpAPI）。\n"
            f"当前为模拟结果。查询: '{query}'\n"
            f"在生产环境中，这里会返回实际的网络搜索结果。"
        )
    
    def _save_note(self, params: Dict) -> str:
        """保存笔记到知识库"""
        title = params["title"]
        content = params["content"]
        tags = params.get("tags", [])
        
        # 将标题和内容拼接为一个文档
        full_content = f"# {title}\n\n标签: {', '.join(tags)}\n\n{content}"
        
        # 添加到向量数据库
        self.vector_store.add_documents(
            chunks=[full_content],
            metadatas=[{
                "file_name": f"note_{title}.md",
                "file_path": f"notes/{title}.md",
                "file_type": ".md",
                "chunk_index": 0,
                "total_chunks": 1,
                "tags": ",".join(tags),
                "is_note": True
            }]
        )
        
        return f"笔记'{title}'已成功保存到知识库。标签: {', '.join(tags)}"
```

**4.3 Agent核心循环**

创建 `src/core/agent.py`：

```python
from typing import List, Dict, Any
import json
from openai import OpenAI
from src.config import Config
from src.tools.definitions import TOOLS
from src.tools.executor import ToolExecutor
from src.knowledge_base.vector_store import VectorStore

class KnowledgeAgent:
    """个人知识助手Agent"""
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.vector_store = VectorStore(persist_dir=Config.CHROMA_PERSIST_DIR)
        self.tool_executor = ToolExecutor(self.vector_store)
        self.max_steps = Config.MAX_STEPS
        
        # 会话历史
        self.messages: List[Dict] = []
        
        # 用户偏好（记忆系统的一部分）
        self.user_preferences: Dict = {}
    
    def chat(self, user_message: str) -> str:
        """
        与Agent进行一轮对话
        
        这是Agent的核心循环：ReAct (Reasoning + Acting)
        """
        # 1. 添加用户消息到历史
        self.messages.append({"role": "user", "content": user_message})
        
        # 2. 构建系统消息
        system_message = self._build_system_message()
        
        # 3. 启动ReAct循环
        step = 0
        while step < self.max_steps:
            step += 1
            
            # 构建完整的消息列表
            full_messages = [system_message] + self.messages
            
            # 调用LLM
            response = self.client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=full_messages,
                tools=self._format_tools_for_openai(),
                tool_choice="auto",
                temperature=0.7
            )
            
            assistant_message = response.choices[0].message
            
            # 检查是否需要调用工具
            if assistant_message.tool_calls:
                # --- 工具调用阶段 ---
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_params = json.loads(tool_call.function.arguments)
                    
                    print(f"  [Agent调用工具] {tool_name}({tool_params})")
                    
                    # 执行工具
                    tool_result = self.tool_executor.execute(
                        tool_name, tool_params
                    )
                    
                    # 将工具调用和结果添加到消息历史
                    self.messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [{
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_name,
                                "arguments": tool_call.function.arguments
                            }
                        }]
                    })
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result
                    })
            else:
                # --- 最终回答阶段 ---
                final_answer = assistant_message.content
                self.messages.append({
                    "role": "assistant",
                    "content": final_answer
                })
                return final_answer
        
        # 达到最大步数仍未完成任务
        return (
            "抱歉，我在处理你的请求时遇到了困难（已尝试{self.max_steps}步）。"
            "请尝试用更具体的方式描述你的需求。"
        )
    
    def _build_system_message(self) -> Dict:
        """构建系统消息"""
        return {
            "role": "system",
            "content": f"""你是一个个人知识助手Agent。你的任务是帮助用户管理和利用他们的个人知识库。

## 你的能力
1. 搜索用户的个人知识库（笔记、文档、学习材料等）
2. 搜索互联网获取最新信息
3. 保存整理后的笔记到知识库

## 行为准则
- 优先使用知识库中的信息，只有在知识库中没有相关信息时才搜索网络
- 回答时明确标注信息来源
- 当你整理出有价值的内容时，主动询问用户是否要保存为笔记
- 如果搜索的结果不够好，尝试用不同的关键词重新搜索
- 不要编造信息。如果找不到相关信息，诚实告知用户

## 用户偏好
{json.dumps(self.user_preferences, ensure_ascii=False, indent=2) if self.user_preferences else "尚未收集到用户偏好"}

## 当前会话上下文
你可以使用工具来完成用户的任务。每次工具调用后，你会收到工具返回的结果。
仔细分析这些结果，判断是否需要进一步检索或调整查询。
当你认为已经收集到足够的信息来回答用户的问题时，直接给出最终回答。"""
        }
    
    def _format_tools_for_openai(self) -> List[Dict]:
        """将工具定义转换为OpenAI格式"""
        return [{"type": "function", "function": tool} for tool in TOOLS]
    
    def update_preference(self, key: str, value: Any):
        """更新用户偏好"""
        self.user_preferences[key] = value
    
    def clear_history(self):
        """清空会话历史"""
        self.messages = []
```

**4.4 停止条件设计**

停止条件是Agent循环中经常被忽视但至关重要的设计。一个好的停止条件可以防止Agent在死循环中浪费资源，同时不会过早中断有价值的探索。

停止条件分为三类：

1. **显式停止**：Agent明确表示任务完成（LLM返回了不带tool_calls的文本回复）
2. **隐式停止**：达到了最大步数上限（`MAX_STEPS`）
3. **智能停止**（进阶）：检测到Agent在重复之前的操作（相同的工具调用+相同参数）——这种情况说明Agent陷入了困境

```python
# 智能停止检测的实现（可添加到Agent类的chat方法中）
def _should_stop_early(self, new_tool_call) -> bool:
    """检测是否应该提前停止"""
    # 检查最近的工具调用历史
    recent_calls = []
    for msg in self.messages[-6:]:  # 检查最近3轮（每轮2条消息）
        if msg.get("role") == "assistant" and msg.get("tool_calls"):
            for tc in msg["tool_calls"]:
                recent_calls.append({
                    "name": tc["function"]["name"],
                    "args": tc["function"]["arguments"]
                })
    
    # 如果有连续3次相同的工具调用
    if len(recent_calls) >= 3:
        if (recent_calls[-1] == recent_calls[-2] == recent_calls[-3]):
            return True
    
    return False
```

#### 第6-7天：记忆系统

**5.1 会话记忆**

会话记忆是最基础的记忆形式，已经在Agent核心循环中实现了（`self.messages`）。关键设计点：

- **记忆窗口管理**：随着对话增长，消息列表会超过LLM的上下文窗口。需要实现滑动窗口或摘要机制。

```python
# 添加在 Agent 类中
def _manage_conversation_window(self, max_tokens: int = 8000):
    """管理会话窗口，避免超出上下文限制"""
    total_tokens = sum(
        len(msg.get("content", "") or "") // 4  # 粗略token估算
        for msg in self.messages
    )
    
    if total_tokens > max_tokens:
        # 策略：保留system message、最近5轮对话，其余用摘要替代
        if len(self.messages) > 12:  # 至少6轮
            # 生成历史摘要
            old_messages = self.messages[:-10]
            summary = self._summarize_conversation(old_messages)
            
            # 替换旧消息
            self.messages = [
                {"role": "system", "content": f"对话历史摘要: {summary}"}
            ] + self.messages[-10:]
```

**5.2 用户偏好记忆**

```python
# 添加到 KnowledgeAgent 类中
def learn_preference(self, conversation_fragment: str):
    """从对话片段中学习用户偏好"""
    prompt = f"""从以下对话中提取用户的知识偏好。只提取明确表达的偏好，不要推测。

对话：
{conversation_fragment}

请以JSON格式返回提取的偏好。如果没有发现任何偏好，返回空对象。
格式：{{"preference_name": "preference_value"}}"""

    # 调用LLM提取偏好
    response = self.client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    
    try:
        new_prefs = json.loads(response.choices[0].message.content)
        self.user_preferences.update(new_prefs)
    except json.JSONDecodeError:
        pass  # 解析失败不影响主流程
```

#### 第7-8天：交互界面

**6.1 命令行界面**

创建 `src/ui/cli.py`：

```python
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from src.core.agent import KnowledgeAgent

console = Console()

def main():
    """命令行入口"""
    console.print(Panel.fit(
        "[bold blue]个人知识助手 Agent[/bold blue]\n"
        "输入 'quit' 退出 | 'clear' 清空对话 | 'prefs' 查看用户偏好",
        border_style="blue"
    ))
    
    agent = KnowledgeAgent()
    
    while True:
        # 获取用户输入
        user_input = console.input("\n[bold green]你:[/bold green] ")
        
        if user_input.lower() == 'quit':
            console.print("[yellow]再见！[/yellow]")
            break
        elif user_input.lower() == 'clear':
            agent.clear_history()
            console.print("[yellow]对话历史已清空[/yellow]")
            continue
        elif user_input.lower() == 'prefs':
            console.print(agent.user_preferences)
            continue
        
        # 显示思考中
        with console.status("[bold yellow]Agent思考中...[/bold yellow]"):
            try:
                response = agent.chat(user_input)
            except Exception as e:
                response = f"出错了: {str(e)}"
        
        # 显示回复
        console.print()
        console.print(Panel(
            Markdown(response),
            title="[bold blue]Agent[/bold blue]",
            border_style="blue"
        ))

if __name__ == "__main__":
    main()
```

**6.2 可选：Gradio Web界面**

创建 `src/ui/web_ui.py`：

```python
import gradio as gr
from src.core.agent import KnowledgeAgent

def create_web_ui():
    agent = KnowledgeAgent()
    
    def respond(message, history):
        """处理用户消息"""
        response = agent.chat(message)
        return response
    
    demo = gr.ChatInterface(
        fn=respond,
        title="个人知识助手",
        description="用自然语言搜索和管理你的个人知识库",
        examples=[
            "帮我找到关于Python装饰器的笔记",
            "总结一下我这周学习的内容",
            "搜索知识库中与机器学习相关的最重要的3个概念"
        ],
        theme="soft"
    )
    
    return demo

if __name__ == "__main__":
    demo = create_web_ui()
    demo.launch(share=False)
```

#### 第8-10天：测试与优化

**7.1 构建测试问题集**

一个好的测试集应该覆盖多种场景：

```python
# tests/test_questions.py
TEST_QUESTIONS = [
    # 精确查询
    {
        "query": "什么是Transformer架构？",
        "expected_source": "knowledge_base",  # 期望从知识库回答
        "difficulty": "easy"
    },
    # 语义查询
    {
        "query": "怎么让深度学习模型更好地关注重要信息？",
        "expected_source": "knowledge_base",
        "difficulty": "medium"  # 需要语义理解，不直接提到"注意力机制"
    },
    # 跨文档查询
    {
        "query": "比较CNN和Transformer在图像处理上的优劣",
        "expected_source": "knowledge_base",
        "difficulty": "hard"  # 需要综合多篇文档的信息
    },
    # 知识库外查询
    {
        "query": "今天的天气怎么样？",
        "expected_source": "web_search",
        "difficulty": "easy"
    }
]
```

**7.2 检索精度评估**

```python
# tests/evaluate_retrieval.py
def evaluate_retrieval():
    """评估检索模块的性能"""
    from src.knowledge_base.retriever import HybridRetriever
    from src.knowledge_base.vector_store import VectorStore
    
    vs = VectorStore()
    retriever = HybridRetriever(vs)
    
    metrics = {
        "precision_at_1": [],
        "precision_at_3": [],
        "precision_at_5": [],
        "mrr": []  # Mean Reciprocal Rank
    }
    
    for test_case in TEST_QUESTIONS:
        results = retriever.retrieve(test_case["query"])
        
        # 检查相关文档是否在结果中
        relevant_ids = test_case.get("relevant_ids", [])
        if relevant_ids:
            # Precision@k
            for k in [1, 3, 5]:
                top_k_ids = [r["id"] for r in results[:k]]
                hits = len(set(top_k_ids) & set(relevant_ids))
                metrics[f"precision_at_{k}"].append(hits / k)
            
            # MRR
            for rank, doc in enumerate(results):
                if doc["id"] in relevant_ids:
                    metrics["mrr"].append(1.0 / (rank + 1))
                    break
            else:
                metrics["mrr"].append(0.0)
    
    # 打印结果
    for metric, values in metrics.items():
        if values:
            avg = sum(values) / len(values)
            print(f"{metric}: {avg:.3f}")
```

**7.3 Prompt迭代优化技巧**

Prompt优化是Agent开发中最耗时但也最有效的环节。这里分享几个通用技巧：

1. **角色设定要具体，不要泛泛而谈**：
   - 差："你是一个有用的助手"
   - 好："你是一个个人知识管理专家，擅长从大量文档中提炼关键信息，并以结构化的方式呈现"

2. **工具使用要明确指令**：
   - 差："你可以使用工具"
   - 好："当用户提问时，首先使用search_knowledge_base搜索相关知识。如果前3条结果的相关性都不足0.5，尝试用不同关键词重新搜索。只有确认知识库中没有相关信息时，才使用search_web"

3. **给出正确和错误的示例**：
   - 在System Prompt中加入few-shot示例，展示期望的行为模式

4. **标注不确定性**：
   - 要求Agent在不确定时明确说明："如果你不确定某个信息的准确性，请明确标注'需要人工核实'"

### 常见问题与解决方案

**Q1: ChromaDB提示"embedding dimension mismatch"**

这是因为你在不同时间用不同的embedding模型构建了知识库。解决方案：删除旧的数据库文件（`./data/chroma_db`），用同一模型重新构建。

**Q2: 检索结果总是不相关**

首先检查chunking策略：如果chunk太小，可能缺少上下文；如果太大，检索精度会下降。建议从chunk_size=500开始，根据你的文档类型逐步调整。其次检查文档解析质量：PDF解析出的文本可能有很多噪音（页眉页脚、乱码），需要增加清洗步骤。

**Q3: Agent频繁调用同一个工具但得不到好结果**

这说明Agent的失败恢复逻辑不够好。在System Prompt中加入指导："如果连续两次使用同一工具没有得到满意的结果，请尝试改变查询方式或使用其他工具。不要重复相同的搜索。"

**Q4: LLM返回的工具调用参数格式不对**

在System Prompt中加入工具参数的具体示例。例如："search_knowledge_base的query参数应该是一个完整的自然语言问题，而不是几个关键词。好的示例：'深度学习中的注意力机制是如何工作的？'，不好的示例：'attention mechanism'"

### 课后作业

1. **基础作业**：完成知识助手Agent的搭建，导入至少10篇你自己的学习笔记，用自然语言成功检索并生成3篇总结。
2. **进阶作业**：实现智能停止检测——当Agent连续3次进行相同的工具调用时，主动询问用户是否需要改变策略。
3. **挑战作业**：实现知识图谱增强检索——将文档中的实体和关系提取为知识图谱，在检索时同时利用向量检索和图结构检索。

---

## 项目二：代码审查Agent

> **难度等级**：中级 | **建议用时**：10-14 天 | **达标目标**：至少达到"合格版"，鼓励冲击"进阶版"

### 课前思考

1. 你最近一次Code Review时，最关注代码的哪些方面？安全？性能？可读性？
2. 如果让你设计一个自动审查工具，你认为它最可能产生的误报是什么？
3. 一个好的Code Review和不合格的Code Review之间，差距在哪里？

### 设计思路

代码审查Agent的核心价值在于：**它能够在代码提交后、人工审查前，提供第一轮自动审查，过滤掉那些机械性的问题（风格不一致、明显的空指针风险等），让人工审查者可以专注于逻辑正确性和架构设计这些更高层次的问题。**

这个项目的核心挑战有四个：

1. **信息获取**：如何从GitHub获取PR的完整上下文？
2. **代码理解**：如何理解一个diff不仅仅是文本变更，而是有语义的代码修改？
3. **结构化输出**：如何生成规范的、可操作的审查意见？
4. **反馈学习**：如何从用户的反馈中持续改进？

### 技术选型理由

#### 为什么用GitHub API？

很多开发者第一反应是"直接git clone下来本地分析不就行了"。这在技术上可行，但有严重缺陷：

1. **权限管理**：你不想让Agent拥有整个仓库的读写权限。GitHub App可以按仓库授权，权限粒度更细。
2. **事件驱动**：PR的创建、更新、评论都是事件，用Webhook接收比轮询更高效。
3. **评论发布**：GitHub Review API可以直接发布行内评论，这是Code Review的核心交互方式。
4. **标准化**：REST API接口稳定，不需要处理不同git服务器的差异。

#### 为什么需要代码理解步骤？

一个简单的例子就能说明问题：

```diff
+ if user.is_active and user.role == "admin":
- if user.role == "admin":
```

只看diff，这只是一个条件判断的修改。但如果Agent能看到上下文：

```python
def delete_all_records(user):
    # 原代码只检查了admin角色
    # 新增了is_active检查，防止停用的管理员账户执行危险操作
    if user.is_active and user.role == "admin":
        ...
```

Agent可以理解：这是一个安全性改进，防止已被停用的管理员账户仍能执行敏感操作。不获取上下文的话，Agent只会说"条件判断发生了变更"，这对审查毫无价值。

### 完整实现步骤

#### 第1-2天：GitHub集成

**1.1 创建GitHub App**

```bash
# 在GitHub上：Settings -> Developer settings -> GitHub Apps -> New GitHub App
# 配置：
# - Webhook URL: https://your-server.com/webhook
# - Permissions:
#   - Pull requests: Read & Write (用于读取PR和发布评论)
#   - Contents: Read (用于读取文件内容)
#   - Metadata: Read (默认)
# - Events: Pull Request
```

生成私钥后，保存为 `github-app-private-key.pem`。

**1.2 GitHub客户端封装**

创建 `src/github/client.py`：

```python
import requests
import jwt
import time
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class PRContext:
    """PR的完整上下文信息"""
    owner: str
    repo: str
    pr_number: int
    title: str
    description: str
    base_branch: str
    head_branch: str
    files: List[Dict]
    diff: str

class GitHubClient:
    """GitHub API客户端"""
    
    def __init__(self, app_id: str, private_key_path: str):
        self.app_id = app_id
        with open(private_key_path, 'r') as f:
            self.private_key = f.read()
        self.base_url = "https://api.github.com"
    
    def _get_installation_token(self, installation_id: int) -> str:
        """获取Installation级别的访问令牌"""
        # 生成JWT
        now = int(time.time())
        payload = {
            "iat": now,
            "exp": now + 600,  # 10分钟过期
            "iss": self.app_id
        }
        jwt_token = jwt.encode(payload, self.private_key, algorithm="RS256")
        
        # 获取Installation Token
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        response = requests.post(
            f"{self.base_url}/app/installations/{installation_id}/access_tokens",
            headers=headers
        )
        response.raise_for_status()
        return response.json()["token"]
    
    def get_pr_context(
        self, owner: str, repo: str, pr_number: int, installation_id: int
    ) -> PRContext:
        """获取PR的完整上下文"""
        token = self._get_installation_token(installation_id)
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # 获取PR基本信息
        pr_url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        pr_response = requests.get(pr_url, headers=headers)
        pr_response.raise_for_status()
        pr_data = pr_response.json()
        
        # 获取PR的文件列表
        files_url = f"{pr_url}/files"
        files_response = requests.get(files_url, headers=headers)
        files_response.raise_for_status()
        files_data = files_response.json()
        
        # 获取PR的diff（使用diff media type）
        diff_headers = {
            **headers,
            "Accept": "application/vnd.github.v3.diff"
        }
        diff_response = requests.get(pr_url, headers=diff_headers)
        
        return PRContext(
            owner=owner,
            repo=repo,
            pr_number=pr_number,
            title=pr_data.get("title", ""),
            description=pr_data.get("body", ""),
            base_branch=pr_data.get("base", {}).get("ref", ""),
            head_branch=pr_data.get("head", {}).get("ref", ""),
            files=files_data,
            diff=diff_response.text if diff_response.status_code == 200 else ""
        )
    
    def get_file_content(
        self, owner: str, repo: str, path: str, ref: str, installation_id: int
    ) -> Optional[str]:
        """获取某个文件在特定分支上的内容"""
        token = self._get_installation_token(installation_id)
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3.raw"
        }
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}?ref={ref}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.text
        return None
    
    def submit_review(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        installation_id: int,
        body: str,
        event: str = "COMMENT",
        comments: List[Dict] = None
    ):
        """
        提交PR审查
        
        参数:
            body: 审查的总体评论
            event: "APPROVE", "REQUEST_CHANGES", 或 "COMMENT"
            comments: 行内评论列表，每个评论包含 path, position, body
        """
        token = self._get_installation_token(installation_id)
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        payload = {
            "body": body,
            "event": event,
        }
        
        if comments:
            payload["comments"] = comments
        
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
```

**1.3 Webhook处理**

创建 `src/github/webhook.py`：

```python
from flask import Flask, request, jsonify
import hashlib
import hmac
from src.github.client import GitHubClient
from src.reviewer.agent import ReviewAgent

app = Flask(__name__)

# GitHub App配置
GITHUB_APP_ID = "your-app-id"
WEBHOOK_SECRET = "your-webhook-secret"

github_client = GitHubClient(
    app_id=GITHUB_APP_ID,
    private_key_path="github-app-private-key.pem"
)
review_agent = ReviewAgent(github_client)

def verify_signature(payload_body: bytes, signature: str) -> bool:
    """验证Webhook签名"""
    if not signature:
        return False
    sha_name, signature = signature.split("=")
    mac = hmac.new(
        WEBHOOK_SECRET.encode(),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    return hmac.compare_digest(mac.hexdigest(), signature)

@app.route("/webhook", methods=["POST"])
def webhook():
    """接收GitHub Webhook事件"""
    # 验证签名
    signature = request.headers.get("X-Hub-Signature-256")
    if not verify_signature(request.data, signature):
        return "Invalid signature", 403
    
    event = request.headers.get("X-GitHub-Event")
    payload = request.json
    
    if event == "pull_request":
        action = payload.get("action")
        
        # 只在PR创建或更新时触发审查
        if action in ["opened", "synchronize"]:
            installation_id = payload["installation"]["id"]
            pr_info = payload["pull_request"]
            
            owner = pr_info["base"]["repo"]["owner"]["login"]
            repo = pr_info["base"]["repo"]["name"]
            pr_number = pr_info["number"]
            
            print(f"收到PR事件: {owner}/{repo}#{pr_number} ({action})")
            
            # 异步处理（生产环境应使用任务队列）
            try:
                review_agent.review_pr(owner, repo, pr_number, installation_id)
            except Exception as e:
                print(f"审查失败: {e}")
    
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(port=8000)
```

#### 第2-4天：代码分析模块

**2.1 Diff解析器**

创建 `src/reviewer/diff_parser.py`：

```python
import re
from typing import List, Dict, NamedTuple
from dataclasses import dataclass

@dataclass
class FileChange:
    """单个文件的变更"""
    filename: str
    status: str  # added, modified, removed, renamed
    additions: int
    deletions: int
    hunks: List[Dict]
    full_diff: str

class DiffParser:
    """解析PR的diff内容，提取结构化的变更信息"""
    
    def parse_files(self, files_data: List[Dict]) -> List[FileChange]:
        """解析GitHub API返回的文件列表"""
        changes = []
        for file_info in files_data:
            change = FileChange(
                filename=file_info.get("filename", ""),
                status=file_info.get("status", "modified"),
                additions=file_info.get("additions", 0),
                deletions=file_info.get("deletions", 0),
                hunks=self._parse_patch(file_info.get("patch", "")),
                full_diff=file_info.get("patch", "")
            )
            changes.append(change)
        return changes
    
    def _parse_patch(self, patch: str) -> List[Dict]:
        """解析patch文本为结构化的hunks"""
        if not patch:
            return []
        
        hunks = []
        for hunk_text in re.split(r'\n(?=@@)', patch):
            if not hunk_text.startswith('@@'):
                continue
            
            # 解析hunk头: @@ -start,count +start,count @@
            header_match = re.match(
                r'@@ -(\d+),?(\d+)? \+(\d+),?(\d+)? @@(.*)', 
                hunk_text
            )
            if not header_match:
                continue
            
            old_start = int(header_match.group(1))
            new_start = int(header_match.group(3))
            
            lines = hunk_text.split('\n')
            changes = []
            old_line = old_start
            new_line = new_start
            
            for line in lines[1:]:  # 跳过header行
                if line.startswith('+'):
                    changes.append({
                        "type": "added",
                        "old_line": None,
                        "new_line": new_line,
                        "content": line[1:]
                    })
                    new_line += 1
                elif line.startswith('-'):
                    changes.append({
                        "type": "removed",
                        "old_line": old_line,
                        "new_line": None,
                        "content": line[1:]
                    })
                    old_line += 1
                elif line.startswith(' '):
                    changes.append({
                        "type": "context",
                        "old_line": old_line,
                        "new_line": new_line,
                        "content": line[1:]
                    })
                    old_line += 1
                    new_line += 1
            
            hunks.append({"changes": changes})
        
        return hunks
```

**2.2 上下文收集器**

创建 `src/reviewer/context_collector.py`：

```python
from typing import List, Dict
from src.github.client import GitHubClient
from src.reviewer.diff_parser import FileChange

class ContextCollector:
    """收集代码变更的上下文信息"""
    
    def __init__(self, github_client: GitHubClient):
        self.github = github_client
    
    def enrich_changes(
        self, owner: str, repo: str, base_ref: str,
        changes: List[FileChange], installation_id: int
    ) -> List[Dict]:
        """为每个文件的变更补充上下文"""
        enriched = []
        
        for change in changes:
            # 对于修改和删除的文件，获取原文件完整内容
            original_content = None
            if change.status in ["modified", "removed"]:
                original_content = self.github.get_file_content(
                    owner, repo, change.filename, base_ref, installation_id
                )
            
            # 获取同目录下的相关文件列表
            related_files = self._find_related_files(change, changes)
            
            # 判断文件类型
            file_type = self._detect_file_type(change.filename)
            
            enriched.append({
                "change": change,
                "file_type": file_type,
                "original_content": original_content,
                "related_files": related_files
            })
        
        return enriched
    
    def _find_related_files(
        self, change: FileChange, all_changes: List[FileChange]
    ) -> List[str]:
        """找到可能相关的文件（同目录、相似名称等）"""
        import os
        change_dir = os.path.dirname(change.filename)
        related = []
        
        for other in all_changes:
            if other.filename == change.filename:
                continue
            other_dir = os.path.dirname(other.filename)
            if change_dir == other_dir:
                related.append(other.filename)
            # 如果有import/require关系，也标记为相关
            # 这里简化处理，生产环境应做AST分析
        
        return related
    
    def _detect_file_type(self, filename: str) -> str:
        """检测文件类型"""
        ext = filename.split('.')[-1] if '.' in filename else ''
        type_map = {
            'py': 'python',
            'js': 'javascript',
            'ts': 'typescript',
            'jsx': 'react',
            'tsx': 'react-typescript',
            'java': 'java',
            'go': 'go',
            'rs': 'rust',
            'rb': 'ruby',
            'cpp': 'cpp',
            'c': 'c',
            'yaml': 'yaml',
            'yml': 'yaml',
            'json': 'json',
            'tf': 'terraform',
            'sql': 'sql'
        }
        return type_map.get(ext, 'unknown')
```

#### 第4-5天：审查规则引擎

创建 `src/reviewer/rules.py`：

```python
from typing import List, Dict
from dataclasses import dataclass
from enum import Enum

class Severity(Enum):
    CRITICAL = "critical"    # 安全漏洞、数据丢失风险
    HIGH = "high"            # 功能缺陷、性能严重问题
    MEDIUM = "medium"        # 代码质量问题、潜在的bug
    LOW = "low"             # 风格问题、小改进建议
    INFO = "info"           # 信息性提示

class Category(Enum):
    SECURITY = "security"
    CORRECTNESS = "correctness"
    PERFORMANCE = "performance"
    STYLE = "style"
    MAINTAINABILITY = "maintainability"

@dataclass
class ReviewRule:
    """审查规则定义"""
    id: str
    name: str
    description: str
    category: Category
    severity: Severity
    check_prompt: str  # 用于LLM检查的prompt

# 预定义审查规则
PREDEFINED_RULES = [
    ReviewRule(
        id="SEC001",
        name="硬编码密钥检测",
        description="检测代码中是否包含硬编码的API密钥、密码、Token等敏感信息",
        category=Category.SECURITY,
        severity=Severity.CRITICAL,
        check_prompt=(
            "检查以下代码变更中是否引入了硬编码的敏感信息，包括："
            "API密钥、密码、Token、私钥、数据库连接字符串等。"
            "注意：即使是测试代码或示例代码中的假密钥，也应标注为安全风险"
        )
    ),
    ReviewRule(
        id="SEC002",
        name="SQL注入风险",
        description="检测是否存在SQL注入风险的字符串拼接",
        category=Category.SECURITY,
        severity=Severity.CRITICAL,
        check_prompt=(
            "检查代码变更中的SQL查询构造方式。"
            "特别注意：字符串拼接(f-string, +操作符, format())构造SQL、"
            "未使用参数化查询的情况。"
        )
    ),
    ReviewRule(
        id="BUG001",
        name="空指针/None引用检查",
        description="检测是否有可能的空指针引用",
        category=Category.CORRECTNESS,
        severity=Severity.HIGH,
        check_prompt=(
            "检查代码变更中，是否在使用某个变量或函数返回值之前检查了它是否为None/null。"
            "特别注意：新代码中对可能为None的值的属性访问和方法调用"
        )
    ),
    ReviewRule(
        id="BUG002",
        name="异常处理检查",
        description="检测是否正确处理了可能的异常",
        category=Category.CORRECTNESS,
        severity=Severity.HIGH,
        check_prompt=(
            "检查代码变更中："
            "1. 是否有空的except块（吞掉了异常）"
            "2. 是否有过宽的异常捕获（except Exception），而应该捕获具体异常"
            "3. 对外部调用（API、数据库、文件）是否有适当的异常处理"
        )
    ),
    ReviewRule(
        id="PERF001",
        name="循环中的重复计算",
        description="检测循环内是否存在不必要的重复计算或资源申请",
        category=Category.PERFORMANCE,
        severity=Severity.MEDIUM,
        check_prompt=(
            "检查循环体内是否有可以移到循环外的操作，例如："
            "数据库连接、文件打开、正则编译、重复的函数调用等"
        )
    ),
    ReviewRule(
        id="STYLE001",
        name="命名规范检查",
        description="检查变量、函数命名是否符合项目规范",
        category=Category.STYLE,
        severity=Severity.LOW,
        check_prompt=(
            "检查新增的变量名、函数名、类名是否："
            "1. 具有描述性（不是x, temp, data这样的模糊命名）"
            "2. 遵循了语言的命名惯例"
        )
    ),
    ReviewRule(
        id="MAIN001",
        name="函数复杂度检查",
        description="检查新增或修改的函数是否过于复杂",
        category=Category.MAINTAINABILITY,
        severity=Severity.MEDIUM,
        check_prompt=(
            "检查新增或修改的函数："
            "1. 函数是否过长（超过50行应考虑拆分）"
            "2. 嵌套层级是否过深（超过3层嵌套应重构）"
            "3. 函数是否承担了太多职责（单一职责原则）"
        )
    ),
]

class RuleEngine:
    """审查规则引擎"""
    
    def __init__(self, rules: List[ReviewRule] = None):
        self.rules = rules or PREDEFINED_RULES
    
    def get_rules_for_file_type(self, file_type: str) -> List[ReviewRule]:
        """根据文件类型返回适用的规则"""
        # 所有规则默认适用，部分语言可能有特殊规则
        applicable = list(self.rules)
        
        # 可以在这里根据文件类型添加/移除规则
        # 例如：SQL文件不需要检查命名规范
        if file_type == "sql":
            applicable = [r for r in applicable if r.category != Category.STYLE]
        
        return applicable
    
    def get_rule_by_id(self, rule_id: str) -> ReviewRule:
        """根据ID获取规则"""
        for rule in self.rules:
            if rule.id == rule_id:
                return rule
        raise ValueError(f"未找到规则: {rule_id}")
    
    def format_rules_for_prompt(self, rules: List[ReviewRule]) -> str:
        """将规则格式化为LLM可理解的文本"""
        sections = []
        for category in Category:
            cat_rules = [r for r in rules if r.category == category]
            if cat_rules:
                sections.append(f"## {category.value}")
                for rule in cat_rules:
                    sections.append(
                        f"- [{rule.severity.value.upper()}] {rule.id}: {rule.name}\n"
                        f"  {rule.description}"
                    )
        return "\n\n".join(sections)
```

#### 第5-7天：Agent审查循环

创建 `src/reviewer/agent.py`：

```python
from typing import List, Dict
from openai import OpenAI
from src.config import Config
from src.github.client import GitHubClient, PRContext
from src.reviewer.diff_parser import DiffParser
from src.reviewer.context_collector import ContextCollector
from src.reviewer.rules import RuleEngine, ReviewRule

class ReviewAgent:
    """代码审查Agent"""
    
    def __init__(self, github_client: GitHubClient):
        self.github = github_client
        self.llm = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.diff_parser = DiffParser()
        self.context_collector = ContextCollector(github_client)
        self.rule_engine = RuleEngine()
    
    def review_pr(
        self, owner: str, repo: str, pr_number: int, installation_id: int
    ):
        """
        审查一个PR的完整流程：
        1. 获取PR上下文
        2. 解析代码变更
        3. 收集上下文
        4. 逐文件审查
        5. 生成审查报告
        6. 提交审查
        """
        # 1. 获取PR上下文
        pr_ctx = self.github.get_pr_context(
            owner, repo, pr_number, installation_id
        )
        
        # 2. 解析文件变更
        changes = self.diff_parser.parse_files(pr_ctx.files)
        
        # 过滤：跳过配置文件、锁文件、自动生成文件
        changes = self._filter_important_changes(changes)
        
        if not changes:
            self._comment_no_significant_changes(
                owner, repo, pr_number, installation_id
            )
            return
        
        # 3. 收集上下文
        enriched = self.context_collector.enrich_changes(
            owner, repo, pr_ctx.base_branch, changes, installation_id
        )
        
        # 4. 逐文件审查
        all_findings = []
        for file_info in enriched:
            findings = self._review_file(pr_ctx, file_info)
            all_findings.extend(findings)
        
        # 5. 生成审查报告
        review_body = self._generate_review_body(pr_ctx, all_findings)
        inline_comments = self._format_inline_comments(all_findings)
        
        # 6. 提交审查
        event = "COMMENT"
        if self._has_critical_findings(all_findings):
            event = "REQUEST_CHANGES"
        
        self.github.submit_review(
            owner, repo, pr_number, installation_id,
            body=review_body,
            event=event,
            comments=inline_comments
        )
    
    def _filter_important_changes(self, changes):
        """过滤掉不重要的文件变更"""
        skip_patterns = [
            'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
            'Cargo.lock', 'Gemfile.lock', 'poetry.lock',
            '*.min.js', '*.min.css', '*.map',
            '__pycache__/', '.pyc', '.pyo',
            '*.generated.*', '*.auto.*'
        ]
        
        import fnmatch
        important = []
        for change in changes:
            skip = False
            for pattern in skip_patterns:
                if fnmatch.fnmatch(change.filename, pattern):
                    skip = True
                    break
            if not skip:
                important.append(change)
        
        return important
    
    def _review_file(self, pr_ctx: PRContext, file_info: Dict) -> List[Dict]:
        """审查单个文件"""
        change = file_info["change"]
        file_type = file_info["file_type"]
        
        # 获取该文件适用的规则
        rules = self.rule_engine.get_rules_for_file_type(file_type)
        rules_text = self.rule_engine.format_rules_for_prompt(rules)
        
        # 对于大型变更，只审查关键部分
        diff_text = change.full_diff
        if len(diff_text) > 8000:
            diff_text = diff_text[:8000] + "\n... (diff过长，已截断)"
        
        # 构建审查prompt
        prompt = f"""你是一位资深代码审查员。请审查以下PR中的文件变更。

## PR信息
- 标题: {pr_ctx.title}
- 描述: {pr_ctx.description}

## 文件信息
- 文件: {change.filename}
- 类型: {file_type}
- 变更状态: {change.status}
- 新增行数: {change.additions}
- 删除行数: {change.deletions}

## 审查规则
{rules_text}

## 代码变更 (Diff)
```diff
{diff_text}
```

## 审查要求
请逐条检查以上所有审查规则。对于每个发现的问题，请用以下JSON格式输出：

```json
{{
  "findings": [
    {{
      "rule_id": "规则ID",
      "severity": "critical|high|medium|low|info",
      "line": 行号,
      "title": "问题简述",
      "description": "详细说明问题是什么",
      "suggestion": "具体的修改建议",
      "code_snippet": "有问题的代码片段"
    }}
  ]
}}

如果没有发现任何问题，返回空的findings数组。

注意事项:
- 只报告真实的问题，不要为了凑数而报告虚假问题
- 对于不确定的问题，在severity中标注为info，并在description中说明不确定性
- 修改建议要具体、可执行，最好是代码级别的
- 如果发现安全漏洞，severity必须标注为critical"""

        response = self.llm.chat.completions.create(
            model=Config.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # 低温，保持一致性
        )
        
        # 解析结果
        import json
        import re
        
        content = response.choices[0].message.content
        json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
        
        if json_match:
            try:
                result = json.loads(json_match.group(1))
                # 为每个finding添加文件信息
                for finding in result.get("findings", []):
                    finding["file"] = change.filename
                return result.get("findings", [])
            except json.JSONDecodeError:
                pass
        
        return []
    
    def _generate_review_body(
        self, pr_ctx: PRContext, findings: List[Dict]
    ) -> str:
        """生成审查报告正文"""
        if not findings:
            return (
                f"## 自动代码审查结果\n\n"
                f"经自动审查，未发现明显问题。\n\n"
                f"*此审查由AI自动生成，建议仍进行人工审查。*"
            )
        
        # 按严重程度分组统计
        from collections import Counter
        severity_count = Counter(f["severity"] for f in findings)
        
        body = (
            f"## 自动代码审查结果\n\n"
            f"### 审查摘要\n"
            f"- 审查文件数: {len(set(f['file'] for f in findings))}\n"
            f"- 发现问题数: {len(findings)}\n"
        )
        
        if severity_count.get("critical", 0) > 0:
            body += f"- **严重问题**: {severity_count['critical']} 个\n"
        if severity_count.get("high", 0) > 0:
            body += f"- **高危问题**: {severity_count['high']} 个\n"
        if severity_count.get("medium", 0) > 0:
            body += f"- **中等问题**: {severity_count['medium']} 个\n"
        if severity_count.get("low", 0) > 0:
            body += f"- **轻微问题**: {severity_count['low']} 个\n"
        
        body += (
            f"\n### 问题详情\n\n"
            f"详细问题已在对应代码行处标注。\n\n"
            f"---\n"
            f"*此审查由AI自动生成，建议仍进行人工审查。"
            f"如有误报，请标记以帮助改进审查质量。*"
        )
        
        return body
    
    def _format_inline_comments(self, findings: List[Dict]) -> List[Dict]:
        """将findings格式化为GitHub行内评论"""
        comments = []
        for finding in findings:
            if finding.get("line"):
                comment_body = (
                    f"**{finding.get('severity', 'info').upper()}** "
                    f"[{finding.get('rule_id', 'N/A')}] {finding.get('title', '')}\n\n"
                    f"{finding.get('description', '')}\n\n"
                    f"**建议:** {finding.get('suggestion', '无')}"
                )
                comments.append({
                    "path": finding["file"],
                    "position": finding["line"],
                    "body": comment_body
                })
        return comments
    
    def _has_critical_findings(self, findings: List[Dict]) -> bool:
        """检查是否有严重问题"""
        return any(
            f["severity"] in ["critical", "high"] for f in findings
        )
    
    def _comment_no_significant_changes(self, owner, repo, pr_number, installation_id):
        """评论无重大变更的PR"""
        self.github.submit_review(
            owner, repo, pr_number, installation_id,
            body="## 自动代码审查\n\n此PR仅包含非代码文件变更（配置文件、锁文件等），跳过详细审查。",
            event="APPROVE"
        )
```

#### 第7-9天：审查质量提升

**5.1 项目规范学习**

创建 `src/reviewer/style_learner.py`：

```python
"""
从代码库中学习和提取编码风格规则

这个方法的核心思路是：让LLM阅读项目的现有代码，
提炼出项目的编码规范（命名约定、缩进风格、注释习惯等），
然后在审查时参考这些规范。
"""

from typing import List, Dict
from openai import OpenAI
from src.config import Config

class StyleLearner:
    """从代码库学习编码风格"""
    
    def __init__(self):
        self.llm = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.project_style_rules: List[Dict] = []
    
    def learn_from_codebase(self, file_samples: List[Dict]) -> List[Dict]:
        """
        从代码样本中学习项目风格
        
        参数:
            file_samples: 包含filename和content的代码样本列表
        """
        # 按文件类型分组
        from collections import defaultdict
        by_type = defaultdict(list)
        for sample in file_samples:
            file_type = sample["filename"].split(".")[-1]
            by_type[file_type].append(sample)
        
        all_rules = []
        
        for file_type, samples in by_type.items():
            # 每种文件类型选取代表性样本
            representative = samples[:5]  # 最多取5个样本
            
            files_text = ""
            for s in representative:
                files_text += f"\n### {s['filename']}\n```\n{s['content'][:2000]}\n```\n"
            
            prompt = f"""分析以下{file_type}代码文件，提取该项目的编码风格规则。

{files_text}

请提取以下方面的规则：
1. 命名约定（变量、函数、类的命名风格）
2. 缩进和空格使用
3. 注释习惯
4. 导入语句的顺序和风格
5. 错误处理模式
6. 其他值得注意的模式

以JSON格式返回：
```json
{{
  "rules": [
    {{
      "category": "命名约定",
      "description": "具体的规则描述",
      "confidence": "high|medium|low"
    }}
  ]
}}
```"""
            
            response = self.llm.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            # 解析结果
            import json
            import re
            content = response.choices[0].message.content
            json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
            
            if json_match:
                try:
                    result = json.loads(json_match.group(1))
                    for rule in result.get("rules", []):
                        rule["file_type"] = file_type
                        all_rules.append(rule)
                except json.JSONDecodeError:
                    pass
        
        self.project_style_rules = all_rules
        return all_rules
    
    def format_style_rules_for_prompt(self) -> str:
        """将学习到的风格规则格式化为审查prompt"""
        if not self.project_style_rules:
            return "未学习项目风格规则"
        
        rules_text = "## 项目编码风格规范（从代码库学习）\n\n"
        for rule in self.project_style_rules:
            rules_text += (
                f"- [{rule.get('file_type', 'all')}] "
                f"{rule.get('category', '规范')}: "
                f"{rule.get('description', '')} "
                f"(置信度: {rule.get('confidence', 'unknown')})\n"
            )
        
        return rules_text
```

**5.2 反馈学习机制**

```python
# 添加到 ReviewAgent 类中
def handle_feedback(self, finding_id: str, is_false_positive: bool, 
                    user_comment: str = ""):
    """
    处理用户对审查结果的反馈
    
    当用户标记某个finding为误报时，将这个案例记录下来，
    用于改进后续审查的准确性。
    """
    feedback = {
        "finding_id": finding_id,
        "is_false_positive": is_false_positive,
        "user_comment": user_comment,
        "timestamp": time.time()
    }
    
    # 存储到反馈数据库
    self._store_feedback(feedback)
    
    # 如果积累了一定数量的误报，重新调整规则
    # 例如：某个规则频繁被标记为误报，降低其严重程度或调整检查逻辑
```

#### 第9-10天：部署与集成

部署代码审查Agent涉及以下关键步骤：

1. **容器化**：将Webhook服务打包为Docker镜像
2. **部署平台**：可以部署到AWS Lambda (API Gateway), Vercel, 或传统的ECS/EKS
3. **密钥管理**：GitHub App私钥和API密钥使用密钥管理服务（AWS Secrets Manager / GitHub Secrets）
4. **监控**：设置审查成功率、响应时间、误报率的监控面板

### 常见问题与解决方案

**Q1: GitHub App安装后收不到Webhook**

检查GitHub App的Webhook URL是否对公网可访问（本地开发可以用ngrok做隧道转发）。检查Webhook Deliveries是否有失败的记录。

**Q2: 审查结果误报率高**

这是自动审查最常见的挑战。降低误报率的策略：
- 在System Prompt中加入"宁可漏报、不要误报"的倾向性指令
- 建立误报案例库，在审查前让Agent学习这些案例
- 对不同类型的规则设置不同的审查标准（安全规则严格、风格规则宽松）

**Q3: 大PR审查超时或结果质量差**

大PR（超过20个文件或500+行变更）不适合一次性审查。策略：
- 对变更量排序，优先审查核心文件（非工具、非测试文件）
- 将大PR拆分为多个批次，每个批次审查后再综合
- 对大PR降低审查深度（只检查安全和高危问题）

### 课后作业

1. **基础作业**：完成GitHub App的创建和配置，能接收PR Webhook并返回审查评论。
2. **进阶作业**：为审查Agent添加对TypeScript/JavaScript项目的专项规则（React Hooks依赖检查、异步错误处理等）。
3. **挑战作业**：实现跨文件逻辑一致性检查——比如在一个文件中修改了函数签名，检查所有调用该函数的地方是否相应更新。

---

## 项目三：领域Agent产品

> **难度等级**：高级 | **建议用时**：14-21 天 | **达标目标**：至少达到"合格版"，根据投入时间冲击"进阶版"或"产品版"

### 设计思路

这是整个课程的巅峰项目。不同于前两个项目有相对明确的"正确答案"，这个项目需要你运用前面学到的所有知识，结合自己对某个领域的理解，从零开始设计和实现一个Agent产品。

这个项目的本质是训练三方面的能力：

1. **系统设计能力**：如何将一个模糊的需求转化为可实现的系统架构
2. **产品思维**：如何定义Agent的能力边界、设计用户交互方式、衡量产品价值
3. **端到端工程能力**：从需求分析到部署上线的全流程

### 可选方向分析

#### 方向A：数据分析Agent

**典型场景**：
> 市场运营人员在Slack中问："上个月新增用户的7天留存率是多少？和上上月对比一下，如果下降了，帮我分析可能的原因。"

**核心技术挑战**：

1. **Text-to-SQL的可靠性**：自然语言到SQL的转换是"看起来简单、做起来极难"的问题。关键措施：
   - 提供数据库Schema作为Agent的工具知识（用search_schema工具让Agent先了解表结构）
   - 生成SQL后先做语法检查和风险评估（是否包含DELETE/DROP等危险操作）
   - 用沙箱或只读账户执行，防止误操作

2. **数据安全处理**：
   - 敏感字段检测：自动识别手机号、身份证号、邮箱等字段
   - 结果脱敏：在返回结果前自动对敏感字段做脱敏处理
   - 查询日志记录：所有Agent生成的SQL都需要记录用于审计

3. **结果的解释性**：
   - Agent不仅返回数据，还需要解释"这些数字意味着什么"
   - 对于异常变化，Agent应主动提出可能的原因假设
   - 可视化选择：根据数据类型自动选择图表类型（趋势→折线图，分布→柱状图，占比→饼图）

**架构参考**：
```
用户输入 → Agent核心 → 工具层
                      ├── schema_explorer: 探索数据库表结构
                      ├── sql_generator: 生成SQL查询
                      ├── sql_executor: 在只读副本上执行SQL
                      ├── python_executor: 在沙箱中执行Python分析代码
                      └── chart_generator: 根据数据生成可视化图表
```

#### 方向B：客服Agent

**典型场景**：
> 用户在深夜发消息："我的包裹显示已签收但我没收到，能帮我查一下吗？"

**核心技术挑战**：

1. **意图识别与路由**：
   - 用户的问题可能跨越多个系统：订单查询（CRM）、物流追踪（物流API）、退款处理（支付系统）
   - Agent需要先识别意图，再调用正确的系统
   - 多意图时按优先级处理（退款请求优先于普通查询）

2. **情绪感知**：
   - 识别用户的情绪状态（愤怒、焦虑、平静）
   - 愤怒用户的处理策略：先道歉和共情，再做事实性回复
   - 及时升级：当用户情绪持续恶化或问题超出Agent能力时，无缝转接人工

3. **人机交接**：
   - 交接时提供完整的上下文摘要（不是原始聊天记录）
   - 标记Agent已确认和未确认的信息
   - 转接后Agent保持静默，由人工客服接管

**关键设计决策**：
- 客服Agent的回复风格应该由公司品牌调性决定（专业严谨 vs 亲切活泼）
- 需要建立一个"不确定时做什么"的策略（默认查知识库 → 查数据 → 升级人工）

#### 方向C：法律助手Agent

**典型场景**：
> 一位律师上传了一份30页的合同，问："帮我检查这份合同的数据保护条款是否符合GDPR的要求。"

**核心技术挑战**：

1. **专业术语理解**：法律文档中的术语有严格定义，Agent不能按日常语义理解
2. **严谨性要求**：法律场景下，错误的建议可能带来严重后果。Agent的输出需要有"引用支持"
3. **引用准确性**：引用法条时必须标注具体条款编号，不能是"根据相关法律规定"这种模糊表述

**策略建议**：
- 建立法律术语词典作为工具知识
- 所有输出必须关联到具体的法条或判例
- 在不确定时明确声明"本分析仅供参考，不构成法律意见"

#### 方向D：运维Agent

**典型场景**：
> 凌晨3点，监控系统触发告警："生产环境API响应时间超过5秒"。Agent自动开始诊断。

**核心技术挑战**：

1. **安全操作确认**：哪些操作Agent可以自动执行（查看监控面板、查看日志），哪些需要人工确认（重启服务、切换流量）
2. **时序数据处理**：运维数据天然是时间序列，Agent需要理解"某指标在特定时间窗口的变化"
3. **根因分析**：从多个系统（监控、日志、事件管理）收集线索，形成假设并验证

### 以数据分析Agent为例的完整实现

下面以数据分析Agent为例，展示从零到一的完整过程。其他方向的开发节奏类似。

#### 第1-3天：需求分析

**1.1 用户画像**

创建一个用户画像文档：

```yaml
目标用户: 非技术背景的业务人员（市场、运营、产品经理）
技术水平: 会使用Excel，不懂SQL或Python
核心痛点:
  - 想用数据支持决策但提数需要排期等数据团队
  - 看板上的固定报表无法回答探索性问题
  - 做分析需要数据组写脚本，沟通成本高
使用场景:
  - "对比这个月和上个月的核心指标"
  - "分析用户流失的主要原因"
  - "帮我算一下这次活动的ROI"
  - "生成一份上周的业务周报"
```

**1.2 能力边界定义**

这是整个项目最关键的一步：定义清楚Agent**能做什么**和**不能做什么**。

```yaml
能力边界:
  能做:
    - 查询数据库中的结构化数据
    - 执行常见的数据分析（聚合、趋势、对比、分布）
    - 生成常见的图表（折线图、柱状图、饼图、散点图）
    - 用自然语言解释分析结果
    - 导出结果为CSV或Excel
  
  不能做:
    - 修改数据库中的任何数据
    - 访问生产数据库（只能访问只读分析副本）
    - 执行运行时间超过30秒的查询
    - 创建或修改数据库表结构
    - 替代数据工程师的复杂ETL工作
  
  需要人工确认的操作:
    - 涉及用户个人身份信息的查询
    - 查询结果超过10000行（防止无意识的资源浪费）
    - 连续5次以上的查询未得到满意结果（主动建议用户找数据组）
```

#### 第3-5天：系统设计

**2.1 架构图**

```
┌─────────────────────────────────────────────────────────────┐
│                        交互层                                │
│  Slack Bot  │  Web Chat  │  CLI  │  API (供其他系统调用)      │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                     Agent核心                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  意图识别     │  │  计划生成     │  │  回复合成     │      │
│  │  (Classifier) │  │  (Planner)   │  │  (Synthesizer)│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                      工具层                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │Schema    │ │SQL       │ │Python    │ │Chart     │      │
│  │Explorer  │ │Executor  │ │Sandbox   │ │Generator │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                      数据层                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  只读数据库   │  │  缓存层       │  │  查询日志     │      │
│  │  (Read Replica)│  │  (Redis)     │  │  (ClickHouse) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

**2.2 数据库安全设计**

```python
# src/tools/sql_executor.py

class SQLExecutor:
    """安全的SQL执行器"""
    
    # 禁止的操作（即使Agent生成了也不执行）
    FORBIDDEN_KEYWORDS = [
        "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", 
        "CREATE", "TRUNCATE", "REPLACE", "GRANT", "REVOKE"
    ]
    
    # 敏感字段模式（需要脱敏的字段名）
    SENSITIVE_PATTERNS = [
        r'.*phone.*', r'.*mobile.*', r'.*email.*', 
        r'.*id_card.*', r'.*password.*', r'.*token.*',
        r'.*ssn.*', r'.*credit_card.*'
    ]
    
    def execute(self, sql: str) -> Dict:
        """
        安全地执行SQL查询
        
        返回: {"success": bool, "data": List[Dict], "message": str}
        """
        # 1. 安全检查
        security_check = self._check_sql_safety(sql)
        if not security_check["safe"]:
            return {
                "success": False,
                "data": [],
                "message": f"SQL安全检查未通过: {security_check['reason']}"
            }
        
        # 2. 执行查询（使用只读连接）
        try:
            with self.readonly_connection() as conn:
                # 设置查询超时
                conn.execute("SET statement_timeout = 30000")  # 30秒
                
                import pandas as pd
                df = pd.read_sql(sql, conn)
                
                # 3. 脱敏处理
                df = self._mask_sensitive_columns(df)
                
                # 4. 大小限制
                if len(df) > 10000:
                    return {
                        "success": False,
                        "data": [],
                        "message": f"查询结果超过10000行限制（实际{len(df)}行），请缩小查询范围"
                    }
                
                return {
                    "success": True,
                    "data": df.to_dict(orient="records"),
                    "row_count": len(df),
                    "columns": list(df.columns),
                    "message": f"查询成功，返回{len(df)}行数据"
                }
        except Exception as e:
            return {
                "success": False,
                "data": [],
                "message": f"查询执行失败: {str(e)}"
            }
    
    def _check_sql_safety(self, sql: str) -> Dict:
        """SQL安全检查"""
        upper_sql = sql.upper()
        
        # 检查禁止的关键词
        for keyword in self.FORBIDDEN_KEYWORDS:
            if re.search(r'\b' + keyword + r'\b', upper_sql):
                return {
                    "safe": False,
                    "reason": f"SQL包含禁止操作: {keyword}。只允许SELECT查询。"
                }
        
        # 确保是SELECT语句
        if not upper_sql.strip().startswith("SELECT"):
            return {
                "safe": False,
                "reason": "只允许执行SELECT查询"
            }
        
        return {"safe": True}
    
    def _mask_sensitive_columns(self, df):
        """对敏感列做脱敏"""
        import re
        for col in df.columns:
            for pattern in self.SENSITIVE_PATTERNS:
                if re.match(pattern, col, re.IGNORECASE):
                    # 手机号脱敏: 138****1234
                    df[col] = df[col].apply(
                        lambda x: str(x)[:3] + '****' + str(x)[-4:] 
                        if pd.notna(x) else x
                    )
                    break
        return df
```

**2.3 Python沙箱执行**

```python
# src/tools/python_sandbox.py
import subprocess
import tempfile
import os
import signal

class PythonSandbox:
    """Python代码沙箱——在隔离环境中执行分析代码"""
    
    def execute(self, code: str, data_context: Dict = None) -> Dict:
        """
        在隔离的Python环境中执行代码
        
        安全措施:
        1. 使用subprocess隔离进程
        2. 限制执行时间（超时自动终止）
        3. 限制可用内存
        4. 禁止网络访问
        5. 禁止文件系统写入（除了指定的临时目录）
        """
        # 将代码写入临时文件
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.py', delete=False
        ) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # 在子进程中执行
            result = subprocess.run(
                ["python", temp_file],
                capture_output=True,
                text=True,
                timeout=30,  # 30秒超时
                env={
                    **os.environ,
                    "PYTHONPATH": "/sandbox/libs",  # 限制库的搜索路径
                },
                preexec_fn=self._set_resource_limits  # Unix only
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout[:5000],  # 限制输出大小
                "stderr": result.stderr[:2000],
                "execution_time": result.returncode  # 简化处理
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "代码执行超时（30秒限制）"
            }
        finally:
            os.unlink(temp_file)
    
    def _set_resource_limits(self):
        """设置进程资源限制"""
        import resource
        # 限制最大内存 512MB
        resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, -1))
        # 限制CPU时间 30秒
        resource.setrlimit(resource.RLIMIT_CPU, (30, 30))
```

#### 第5-10天：Agent实现

**3.1 Schema理解工具**

```python
# src/tools/schema_explorer.py

class SchemaExplorer:
    """
    让Agent能够了解和理解数据库的表结构
    
    这是Text-to-SQL成功的关键：Agent在生成SQL之前，
    需要先知道有哪些表、每个表有哪些字段、字段的含义是什么。
    """
    
    def get_schema_summary(self) -> str:
        """获取所有表的摘要信息"""
        tables = self._fetch_tables()
        
        summary = "## 数据库表结构\n\n"
        for table_name, columns in tables.items():
            row_count = self._get_row_count(table_name)
            summary += f"### {table_name} (约{row_count}行)\n"
            summary += "| 字段名 | 类型 | 说明 |\n"
            summary += "|--------|------|------|\n"
            for col in columns:
                summary += f"| {col['name']} | {col['type']} | {col['comment']} |\n"
            summary += "\n"
        
        return summary
    
    def search_columns(self, keyword: str) -> str:
        """
        根据关键词搜索相关字段
        
        Agent可以先用这个方法了解哪些表和字段与用户问题相关
        """
        # 搜索字段名和注释中包含关键词的列
        results = self._search_in_schema(keyword)
        
        if not results:
            return f"未找到与'{keyword}'相关的字段，请尝试其他关键词"
        
        formatted = f"搜索'{keyword}'找到以下相关字段：\n\n"
        for r in results:
            formatted += (
                f"- 表: {r['table']}, 字段: {r['column']}\n"
                f"  类型: {r['type']}, 说明: {r['comment']}\n"
            )
        
        return formatted
```

**3.2 可视化生成器**

```python
# src/tools/chart_generator.py
import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import matplotlib.pyplot as plt
import io
import base64

class ChartGenerator:
    """根据数据自动选择并生成图表"""
    
    def generate(self, data: List[Dict], chart_type: str = "auto") -> Dict:
        """
        生成图表
        
        chart_type: "auto", "line", "bar", "pie", "scatter"
        """
        import pandas as pd
        df = pd.DataFrame(data)
        
        if chart_type == "auto":
            chart_type = self._auto_select_type(df)
        
        plt.figure(figsize=(10, 6))
        
        if chart_type == "line":
            self._draw_line(df)
        elif chart_type == "bar":
            self._draw_bar(df)
        elif chart_type == "pie":
            self._draw_pie(df)
        elif chart_type == "scatter":
            self._draw_scatter(df)
        
        # 转为base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        plt.close()
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode()
        
        return {
            "chart_type": chart_type,
            "image_base64": img_base64,
            "format": "png"
        }
    
    def _auto_select_type(self, df) -> str:
        """根据数据特征自动选择图表类型"""
        numeric_cols = df.select_dtypes(include=['number']).columns
        text_cols = df.select_dtypes(include=['object']).columns
        
        if len(df) <= 1:
            return "bar"
        
        # 如果有时间列 + 数值列 → 折线图
        if any('time' in c.lower() or 'date' in c.lower() for c in df.columns):
            if len(numeric_cols) >= 1:
                return "line"
        
        # 一个文本列 + 一个数值列(<=10行) → 饼图
        if len(text_cols) >= 1 and len(numeric_cols) == 1 and len(df) <= 10:
            return "pie"
        
        # 默认柱状图
        return "bar"
```

#### 第10-14天：产品化

**4.1 错误处理与降级策略**

```python
# src/core/graceful_degradation.py

class GracefulDegradation:
    """
    优雅降级策略
    
    当某个工具失败时，不是简单地抛出错误，
    而是提供最佳的降级方案。
    """
    
    DEGRADATION_PATHS = {
        "sql_executor": [
            # 第1次降级：尝试简化SQL（去掉ORDER BY、LIMIT子句）
            "简化SQL查询",
            # 第2次降级：只查询最近7天的数据
            "缩小时间范围到最近7天",
            # 第3次降级：建议用户找数据组
            "建议联系数据团队获取帮助"
        ],
        "chart_generator": [
            # 降级：生成Table格式的数据展示而不是图表
            "以表格形式展示数据"
        ],
        "python_sandbox": [
            # 降级：用SQL替代Python做简单聚合
            "尝试用SQL完成相同分析"
        ]
    }
    
    def handle_failure(self, tool_name: str, error: str, 
                       attempt: int, context: Dict) -> str:
        """
        处理工具失败
        
        返回给Agent的降级建议
        """
        if tool_name not in self.DEGRADATION_PATHS:
            return f"工具{tool_name}执行失败: {error}。请尝试其他方法完成用户需求。"
        
        paths = self.DEGRADATION_PATHS[tool_name]
        
        if attempt < len(paths):
            suggestion = paths[attempt]
            return (
                f"工具{tool_name}执行失败: {error}\n"
                f"建议降级方案: {suggestion}\n"
                f"请尝试降级方案，或简化你的查询。"
            )
        else:
            return (
                f"工具{tool_name}多次执行失败。"
                f"请告知用户暂时无法完成该分析，并建议联系数据团队。"
            )
```

**4.2 用户反馈机制**

```python
# 在每个Agent回复末尾添加反馈按钮
FEEDBACK_PROMPT = """
---
**这个回答对你有帮助吗？**
- [有帮助] [部分有帮助] [没有帮助]

如有改进建议，请输入：`feedback: 你的建议`
"""

# 在Agent类中处理反馈
def process_feedback(self, user_input: str):
    """处理用户反馈"""
    if user_input.startswith("feedback:"):
        feedback_text = user_input[9:].strip()
        self._store_feedback({
            "text": feedback_text,
            "timestamp": time.time(),
            "context": self.get_conversation_summary()
        })
        return "感谢你的反馈！我们会持续改进。"
```

### 常见问题与解决方案

**Q1: Agent生成的SQL总是报错**

这是Text-to-SQL阶段最常见的困难。核心问题是Agent对数据库Schema的理解不够准确。解决方案：
1. 加强Schema描述：不仅仅是列名和类型，还应该包含常见用法、示例查询、与其他表的关联关系
2. 在System Prompt中加入该数据库的查询风格示例（few-shot）
3. 实现SQL语法验证：在执行前用sqlparse库检查SQL语法
4. 建立一个"常见错误SQL"的案例库，在System Prompt中提醒Agent避免这些错误

**Q2: 用户不知道Agent能做什么**

这是产品设计中容易被忽略的问题。解决方案：
1. 在欢迎消息中列出3-5个典型的使用场景
2. 提供示例问题快捷按钮
3. 当用户的问题超出Agent能力时，清晰地告知边界（"我目前不支持这个，但我可以帮你做XXX"）

**Q3: Agent的分析结果过于技术化，用户看不懂**

核心问题是Agent没有做好"翻译"工作。解决方案：
1. 在System Prompt中明确角色定位："你是一个面向非技术用户的翻译官，你的核心价值不是展示技术能力，而是用通俗的语言解释数据背后的含义"
2. 对于技术术语，自动附带解释
3. 用对比和类比来解释数据："转化率从3%提升到5%，这意味着每100个访问用户中，多了2个人完成了购买"

---

## 通用方法论：如何做好一个Agent项目

经过三个项目的实践，你应该已经积累了不少经验。这里我将一些通用的方法论总结出来，这些原则适用于任何Agent项目。

### 1. 从最小可行Agent开始

很多人在做Agent项目时，一上来就想做一个"全能选手"——能回答任何问题、处理任何情况。这个想法会害了你。

正确的做法是：**先做一个在某些特定场景下能可靠工作的Agent**。这个Agent可能很"笨"——只能处理20%的问题，但它在这20%的问题上表现非常好。

为什么这样做是对的？

- **你可以快速验证核心假设**：你的技术方案是否真的能解决问题？用户是否真的需要这个Agent？
- **你可以积累真实的失败案例**：在实际使用中观察Agent在哪里失败，而不是凭空想象
- **你可以建立对复杂度的直觉**：只有亲手做过，你才知道哪些部分是最容易出问题的，哪些是相对简单的

### 2. 多跑、多看、多改

这个建议看起来像废话，但很多开发者确实不这么做。

你应该实际运行Agent至少100次（可以是自动化测试），仔细观察它的行为：

- 它在第几步开始"跑偏"？
- 它最常犯什么类型的错误？
- 它在哪些情况下会陷入死循环？
- 用户最常纠正它的方式是什么？

然后用这些观察来改进——改进工具描述、改进System Prompt、改进Chunking策略。这个过程不是一次性的，而是持续的。

### 3. 先优化工具描述，再优化Prompt

很多开发者一遇到Agent表现不好就改System Prompt。但根据我的经验，**工具的description对Agent行为的影响往往比System Prompt更大**。

原因很简单：Agent是一个依靠工具来理解世界和完成任务的系统。如果工具描述不准确或不完整，Agent就像近视的人看不清东西，System Prompt再怎么写也无济于事。

工具描述应该包含：
- **这个工具能做什么**（用它能解决什么问题）
- **什么时候用它**（什么场景下该用，什么场景下不该用）
- **参数应该怎么填**（给出好的示例和坏的示例）
- **返回结果的格式和含义**

### 4. 记录每一次失败

建立一个失败案例库（Failure Case Library），格式如下：

```yaml
case_id: FAIL-001
scenario: 用户要求"比较本月和上月的销售额"
what_happened: Agent生成的SQL没有正确处理日期范围，查询的是全部历史数据
root_cause: 工具描述中缺少对日期字段格式的说明
fix: 在search_columns工具中添加了日期字段格式的详细说明
regression_test: 添加了"比较本月和上月"的测试用例
```

这个案例库有三个作用：
1. 帮助你自己理解Agent的弱点
2. 作为回归测试的基础
3. 当你需要向别人解释Agent的能力边界时，这些案例是最好的说明

### 5. 让用户容易纠正Agent

一个"全自动"的Agent听起来很酷，但实际上，**一个允许用户说"不对，你应该……"的Agent远比一个假装全能的Agent有价值**。

实现方式：
- 在每个回答后面提供简单的纠正机制："这个答案对你有帮助吗？"
- 当Agent不确定时，主动询问："我理解你问的是XXX，对吗？如果不是，请帮我纠正。"
- 将用户的纠正记录下来，作为后续改进的依据

### Agent开发中的常见误区

| 误区 | 正确做法 |
|------|----------|
| 让Agent做太多事情 | 聚焦核心场景，做好一个再做下一个 |
| 过于依赖LLM的能力 | LLM是核心但不是全部，工具设计、检索质量同样重要 |
| 忽视用户交互设计 | 用户怎么和Agent交互，和Agent本身一样重要 |
| 不做充分的错误处理 | Agent在每一步都可能出错，错误处理是系统级的 |
| 只测试"正确答案" | 也要测试Agent在不知道该怎么做时是否得体地承认 |
| 工具太多 | 工具超过10个时Agent会出现选择困难，用工具组合替代单工具 |

### 持续学习的建议

Agent领域的技术演进非常快。以下资源可以帮助你保持更新：

1. **论文**：关注arXiv上相关的论文（搜索关键词：LLM Agent, Tool-augmented LLM, ReAct, RAG）
2. **开源项目**：LangChain（学习框架设计）、AutoGPT（学习自主Agent的设计）、SWE-agent（学习代码Agent的设计）
3. **产品**：GitHub Copilot（学习代码补全）、Cursor（学习Agent+IDE的融合）、Perplexity（学习搜索型Agent）
4. **博客和播客**：Anthropic的Research Blog、OpenAI的Blog、Lilian Weng的博客

---

## 课程总结与下一步

### 阶段六学习目标回顾

经过这六个阶段的完整学习，你应该已经：

1. **理论基础**（阶段一）：理解了LLM的工作原理、Agent的基本概念
2. **工具使用**（阶段二）：熟练使用主流Agent框架和工具
3. **框架原理**（阶段三）：能够深入框架内部，理解设计决策
4. **评估体系**（阶段四）：知道如何衡量Agent的质量
5. **高级主题**（阶段五）：掌握了多Agent协作、安全等进阶话题
6. **实践能力**（阶段六）：能够独立设计、实现和部署Agent产品

### 你现在的工具箱

- **三个完整的Agent项目**：个人知识助手、代码审查Agent、领域Agent产品
- **一套经过验证的开发方法论**：从MVP到迭代优化的完整流程
- **一份失败案例库**：记录了你在开发过程中遇到和解决的问题
- **对Agent能力的直觉**：知道什么场景适合用Agent、什么场景不适合

### 下一步可以做什么

1. **深化你的领域Agent产品**：把项目三的产品做得更好，让真实的用户来使用它
2. **学习多Agent协作**：研究多个Agent如何分工协作完成复杂任务（例如：一个Agent负责需求分析，另一个负责代码实现）
3. **探索Agent评估**：建立你的Agent产品的自动化评估体系
4. **开源你的作品**：把你的项目整理好开源，获得社区反馈
5. **关注前沿进展**：Agent领域日新月异，保持学习的节奏

### 最后的建议

学习Agent开发最好的方式就是——不断地做、不断地失败、不断地改进。这门课程给了你方法和框架，但真正的技能是你在键盘前一行一行敲出来的。

如果你完成了这三个项目，你就已经超过了99%的"Agent技术关注者"，成为了真正能上手做的实践者。带着这种实践精神继续前进，你会发现Agent技术能解决的问题范围远超你最初的想象。

**祝你在这个领域做出真正有价值的产品。**

---

*本课程完。总六阶段，本阶段字数约15000字。*

---

## 项目完成后的下一步

### 你已经掌握了什么

完成六个阶段的学习后，你应该具备以下能力：

1. **独立设计**：能根据需求设计 Agent 的架构（编排模式、工具集、记忆策略、交互流程）
2. **实现落地**：能从零实现一个 Agent 系统，不依赖"一键生成"的模板
3. **系统优化**：能用评测数据驱动 Agent 的迭代，知道改什么、怎么验证
4. **产品意识**：理解"能跑"和"能上线"之间的差距，知道如何填补

### 可以继续深入的方向

| 方向 | 适合人群 | 下一步行动 |
|------|---------|----------|
| **Agent 创业** | 有产品想法和领域经验 | 找 10 个目标用户深聊，验证需求；做一个最小可用的 MVP；收集真实反馈迭代 |
| **Agent 基础设施** | 对平台/框架/协议感兴趣 | 深入 MCP/A2A 生态；贡献开源项目（LangChain、CrewAI、Langfuse 等） |
| **Agent 研究** | 对算法/模型层感兴趣 | 复现 Agent 相关论文；在 SWE-bench 等评测上做改进；探索 RL for Agent |
| **Agent 应用开发** | 想在公司/团队中落地 Agent | 找一个内部痛点场景做 POC；建立评测集和监控；从"辅助"到"自主"逐步过渡 |

### 保持学习的方法

1. **每月跑一次生态扫描**：浏览 arXiv 上的 Agent 新论文、GitHub Trending 上的新项目
2. **维护你的失败案例库**：每次 Agent 出错都是学习机会
3. **分享你的经验**：写博客、做内部分享——教别人是最好的学习方式
4. **关注 3-5 个关键信源**：Anthropic Blog、OpenAI Blog、Lilian Weng 的博客、LangChain Blog、SWE-bench Leaderboard

---

> **最后的话**：学完这套课程，你不会成为"Agent 专家"——因为没有人是。这个领域变化太快，今天的"最佳实践"明天可能就是"反面教材"。但你学会了如何学习、如何分析、如何从实践中提炼认知——这些才是长期来看最有价值的东西。Agent 时代刚刚开始，你已经在路上了。
