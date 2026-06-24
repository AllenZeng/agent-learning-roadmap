"""
在线查询 Pipeline：用户问题 → 基于笔记的回答

对应 course-05-02 §2.4.5–2.4.7 的内容：
  2.4.5 查询理解与改写   — 指代消解、意图补全
  2.4.6 召回与重排序     — 多路召回 + RRF 融合 + rerank + 截断
  2.4.7 上下文组装与生成 — chunk 编排、来源标注、引用对齐

用法：
    python online_pipeline.py "Tool Use 和 Memory 的区别"
    python online_pipeline.py --interactive            # 交互模式
    python online_pipeline.py --top-k 5 "什么是 Chunking"
"""

import argparse
import json
import os
import pickle
import re
import sys
from pathlib import Path

import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

# ---------- 配置 ----------

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DEFAULT_TOP_K = 5
VECTOR_WEIGHT = 0.6  # 向量召回在 RRF 融合中的权重
BM25_WEIGHT = 0.4     # BM25 在 RRF 融合中的权重
MAX_CONTEXT_CHARS = 3000


def tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


# ================================================================
# 阶段一：加载索引
# ================================================================

def load_index(index_dir: str) -> tuple[list[dict], np.ndarray, BM25Okapi, SentenceTransformer]:
    """加载所有索引文件"""
    base = Path(index_dir)

    # Chunks 元数据 + 内容
    with open(base / "chunks.json", encoding="utf-8") as f:
        chunks = json.load(f)
    print(f"[加载] chunks.json — {len(chunks)} 个 chunk")

    # 向量嵌入
    embeddings = np.load(base / "embeddings.npy")
    print(f"[加载] embeddings.npy — shape {embeddings.shape}")

    # BM25 索引
    with open(base / "bm25_index.pkl", "rb") as f:
        bm25_index = pickle.load(f)
    print(f"[加载] bm25_index.pkl — {len(bm25_index.idf)} 个词条")

    # Embedding 模型
    with open(base / "index_meta.json") as f:
        meta = json.load(f)
    model_name = meta.get("embedding_model", EMBEDDING_MODEL)
    print(f"[加载] Embedding 模型: {model_name}")
    model = SentenceTransformer(model_name)

    return chunks, embeddings, bm25_index, model


# ================================================================
# 阶段二：查询理解与改写（§2.4.5）
# ================================================================

def understand_query(query: str) -> dict:
    """
    对查询做简单理解和扩展。
    完整实现会包括：指代消解、同义词扩展、意图分类。
    此处展示核心思路。
    """
    # 检测是否是跟进问题（包含指代词）
    has_pronoun = any(w in query for w in ["它", "他", "她", "这个", "那个", "这些", "那些"])

    # 简单同义词扩展
    expansions = {
        "tool use": ["工具调用", "工具使用", "function calling"],
        "memory": ["记忆", "状态管理", "上下文"],
        "rag": ["检索增强生成", "外部知识", "知识库"],
        "chunking": ["分块", "切分", "文档分割"],
    }

    expanded_terms = []
    for key, terms in expansions.items():
        if key in query.lower():
            expanded_terms.extend(terms)

    return {
        "original": query,
        "has_pronoun": has_pronoun,
        "expanded_terms": expanded_terms,
        "expanded_query": f"{query} {' '.join(expanded_terms)}" if expanded_terms else query,
    }


# ================================================================
# 阶段三：召回（§2.4.6）
# ================================================================

def dense_retrieve(
    query: str, model: SentenceTransformer, embeddings: np.ndarray, chunks: list[dict], top_k: int = 20
) -> list[dict]:
    """
    向量语义召回：embed query → cosine similarity → top-k。
    向量擅长语义泛化，但可能误命中不直接回答问题的内容。
    """
    query_vec = model.encode([query], normalize_embeddings=True)[0]
    # cosine similarity（向量已归一化，点积即相似度）
    scores = np.dot(embeddings, query_vec)
    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for idx in top_indices:
        results.append(
            {
                "chunk_idx": int(idx),
                "score": float(scores[idx]),
                "source": "dense",
                "chunk": chunks[idx],
            }
        )
    return results


def sparse_retrieve(query: str, bm25_index: BM25Okapi, chunks: list[dict], top_k: int = 20) -> list[dict]:
    """
    BM25 关键词召回：精确匹配专有名词和术语。
    擅长精确匹配，但不懂语义变体（'Tool Use' vs '工具调用'）。
    """
    tokenized = tokenize(query)
    scores = bm25_index.get_scores(tokenized)
    # BM25 分数归一化到 [0, 1]
    max_score = scores.max() if scores.max() > 0 else 1
    scores = scores / max_score

    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for idx in top_indices:
        if scores[idx] > 0:  # 只保留有匹配的
            results.append(
                {
                    "chunk_idx": int(idx),
                    "score": float(scores[idx]),
                    "source": "sparse",
                    "chunk": chunks[idx],
                }
            )
    return results


def metadata_filter(results: list[dict]) -> list[dict]:
    """过滤：排除草稿、过旧内容"""
    filtered = []
    for r in results:
        c = r["chunk"]
        # 过滤草稿
        if c.get("status") == "draft":
            continue
        filtered.append(r)
    return filtered


def rrf_fusion(dense_results: list[dict], sparse_results: list[dict], k: int = 60) -> list[dict]:
    """
    Reciprocal Rank Fusion：合并两路召回并去重。
    来自不同路的同一 chunk 会获得更高排名（两路都认可）。
    """
    scores = {}  # chunk_idx → fused_score

    for rank, r in enumerate(dense_results):
        idx = r["chunk_idx"]
        scores[idx] = scores.get(idx, 0) + VECTOR_WEIGHT / (k + rank + 1)

    for rank, r in enumerate(sparse_results):
        idx = r["chunk_idx"]
        scores[idx] = scores.get(idx, 0) + BM25_WEIGHT / (k + rank + 1)

    # 按融合分数排序
    sorted_indices = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # 重建结果（保留 chunk 引用、来源、原始分数）
    chunk_map = {}
    for r in dense_results + sparse_results:
        if r["chunk_idx"] not in chunk_map:
            chunk_map[r["chunk_idx"]] = r

    fused = []
    for idx, score in sorted_indices:
        r = chunk_map[idx]
        fused.append({**r, "fused_score": score})

    return fused


# ================================================================
# 阶段四：重排序（§2.4.6）
# ================================================================

def rerank(
    query: str, candidates: list[dict], model: SentenceTransformer, top_k: int = DEFAULT_TOP_K
) -> list[dict]:
    """
    重排序：对候选 chunk 做精细排序。

    此处使用 score-based 方法（余弦相似度 + 融合分数加权）。
    生产环境中建议用 cross-encoder 逐对评分，精度更高但计算成本大。

    关键信号：分数断崖。当 #N 到 #N+1 的分数骤降时，截断在 N。
    """
    if len(candidates) <= top_k:
        return candidates

    # 用更精细的相似度重算分数
    chunk_texts = [c["chunk"]["content"] for c in candidates]
    query_vec = model.encode([query], normalize_embeddings=True)[0]
    chunk_vecs = model.encode(chunk_texts, normalize_embeddings=True)
    sim_scores = np.dot(chunk_vecs, query_vec)

    # 与融合分数加权结合
    for i, c in enumerate(candidates):
        c["rerank_score"] = 0.7 * float(sim_scores[i]) + 0.3 * c["fused_score"]

    # 排序
    ranked = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)

    # 检测分数断崖：相邻分数差 > 30% → 截断
    cut_at = top_k
    for i in range(top_k, len(ranked)):
        if ranked[i - 1]["rerank_score"] > 0 and ranked[i]["rerank_score"] / ranked[i - 1]["rerank_score"] < 0.7:
            cut_at = i
            break

    return ranked[:cut_at]


# ================================================================
# 阶段五：上下文组装（§2.4.7）
# ================================================================

def assemble_context(query: str, ranked_chunks: list[dict], max_chars: int = MAX_CONTEXT_CHARS) -> str:
    """
    将检索结果编排为 LLM 可用的上下文。
    每个 chunk 标注来源编号、文件名、小节路径、更新时间。
    """
    parts = []
    total_chars = 0

    for i, r in enumerate(ranked_chunks):
        c = r["chunk"]
        header = (
            f"[来源 {i + 1}] {c['source']} — {c['section_path']}\n"
            f"更新于 {c.get('updated_at', '?')}  |  "
            f"标签: {', '.join(c.get('tags', []))}  |  "
            f"分数: {r.get('rerank_score', r['fused_score']):.3f}"
        )

        content = c["content"]
        total_chars += len(header) + len(content) + 4

        if total_chars > max_chars and i > 0:
            print(f"  [截断] 达到 token 预算上限，取了 {i} / {len(ranked_chunks)} 个 chunk")
            break

        parts.append(f"{header}\n\n{content}")

    return "\n\n---\n\n".join(parts)


# ================================================================
# 阶段六：生成（模拟）
# ================================================================

def generate_answer(query: str, context: str, ranked_chunks: list[dict]) -> str:
    """
    生成最终回答。

    此处为模拟——展示会进入 LLM 上下文的完整 prompt 结构。
    实际使用时可替换为 LLM API 调用。
    """
    sources_summary = "\n".join(
        f"  [{i + 1}] {r['chunk']['source']} → {r['chunk']['section_path']} "
        f"(分数: {r.get('rerank_score', r['fused_score']):.3f})"
        for i, r in enumerate(ranked_chunks)
    )

    prompt = f"""你是一个个人知识助手。请基于以下笔记内容回答用户问题。

## 用户问题
{query}

## 相关笔记
{context}

## 回答要求
- 基于上述笔记内容回答，不要编造
- 引用具体来源（如 [来源 1]）
- 如果笔记中没有直接答案，明确说明
- 如果笔记内容存在矛盾，指出并说明
"""
    print("\n" + "=" * 60)
    print("  📤 最终 Prompt（将发送给 LLM）")
    print("=" * 60)
    print(f"\n{prompt}\n")
    print(f"[提示] 以上 Prompt 共约 {len(prompt)} 字符")
    print(f"[提示] 替换 generate_answer() 中的逻辑接入 LLM API 即可获得最终回答\n")

    return prompt


# ================================================================
# 主流程
# ================================================================

def run_online_pipeline(
    query: str,
    index_dir: str = "output",
    top_k: int = DEFAULT_TOP_K,
    debug: bool = False,
):
    """执行完整的在线查询流程"""
    print("=" * 60)
    print(f"  在线查询 Pipeline")
    print(f"  查询: \"{query}\"")
    print("=" * 60)

    # ── Step 1: 加载索引 ──
    print()
    chunks, embeddings, bm25_index, model = load_index(index_dir)

    # ── Step 2: 查询理解 ──
    print(f"\n── 查询理解 (§2.4.5) ──")
    query_info = understand_query(query)
    print(f"  原始查询: {query_info['original']}")
    if query_info["has_pronoun"]:
        print(f"  ⚠️ 检测到指代词，可能需要上下文补全")
    if query_info["expanded_terms"]:
        print(f"  扩展词: {query_info['expanded_terms']}")

    search_query = query_info["expanded_query"]

    # ── Step 3: 多路召回 ──
    print(f"\n── 多路召回 (§2.4.6) ──")
    print(f"  向量召回 top-20 ...", end=" ")
    dense_results = dense_retrieve(search_query, model, embeddings, chunks, top_k=20)
    print(f"命中 {len(dense_results)}")

    print(f"  BM25 召回 top-20 ...", end=" ")
    sparse_results = sparse_retrieve(search_query, bm25_index, chunks, top_k=20)
    print(f"命中 {len(sparse_results)}")

    # 元数据过滤
    dense_results = metadata_filter(dense_results)
    sparse_results = metadata_filter(sparse_results)

    # RRF 融合
    fused = rrf_fusion(dense_results, sparse_results)
    print(f"  RRF 融合 → {len(fused)} 个候选（去重后）")

    if debug:
        print(f"\n  候选集详情:")
        for i, r in enumerate(fused[:15]):
            c = r["chunk"]
            print(f"    #{i + 1} [{r['source']}] {c['section_path'][:50]} — "
                  f"融合分: {r['fused_score']:.4f}")

    # ── Step 4: 重排序 ──
    print(f"\n── 重排序 (§2.4.6) ──")
    ranked = rerank(search_query, fused, model, top_k=top_k)
    print(f"  Rerank → top-{len(ranked)}")

    print(f"\n  最终选中的 chunk:")
    for i, r in enumerate(ranked):
        c = r["chunk"]
        print(f"    #{i + 1} [{c['source']}] {c['section_path']}")
        print(f"        分数: {r['rerank_score']:.3f}  |  "
              f"{c['char_count']} 字符  |  标签: {c.get('tags', [])}")

    # 分数断崖检测
    if len(ranked) >= 2:
        last = ranked[-1]["rerank_score"]
        if len(fused) > len(ranked):
            print(f"    🔻 分数断崖：第 {len(ranked)} 名之后的内容对回答帮助显著下降")

    # ── Step 5: 上下文组装 ──
    print(f"\n── 上下文组装 (§2.4.7) ──")
    context = assemble_context(query, ranked)
    print(f"  组装完成，共 {len(context)} 字符")

    # ── Step 6: 生成回答 ──
    generate_answer(query, context, ranked)

    return ranked, context


# ================================================================
# CLI 入口
# ================================================================

def interactive_mode(index_dir: str, top_k: int, debug: bool):
    """交互式查询模式"""
    print("=" * 60)
    print("  个人知识助手 — 交互查询")
    print("  输入问题进行检索，输入 /quit 退出，/debug 切换详情")
    print("=" * 60)

    # 预加载索引
    chunks, embeddings, bm25_index, model = load_index(index_dir)

    while True:
        try:
            query = input("\n🔍 你的问题: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not query:
            continue
        if query == "/quit":
            break
        if query == "/debug":
            debug = not debug
            print(f"  debug = {debug}")
            continue

        run_online_pipeline(query, index_dir, top_k, debug)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="在线查询 Pipeline")
    parser.add_argument("query", nargs="?", help="查询文本")
    parser.add_argument("--index-dir", default="output", help="索引目录 (默认: output/)")
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K, help=f"返回数量 (默认: {DEFAULT_TOP_K})")
    parser.add_argument("--interactive", "-i", action="store_true", help="交互模式")
    parser.add_argument("--debug", action="store_true", help="显示详细候选集")
    args = parser.parse_args()

    if args.interactive or not args.query:
        interactive_mode(args.index_dir, args.top_k, args.debug)
    else:
        run_online_pipeline(args.query, args.index_dir, args.top_k, args.debug)
