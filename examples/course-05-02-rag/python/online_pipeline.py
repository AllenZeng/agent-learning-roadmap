"""
Online query pipeline: user question -> note-based answer

Corresponds to course-05-02 sections 2.4.5-2.4.7:
  2.4.5 Query understanding and rewriting   - reference resolution and intent completion
  2.4.6 Retrieval and reranking     - multi-route retrieval + RRF fusion + rerank + truncation
  2.4.7 Context assembly and generation - chunk ordering, source labels, and citation alignment

Usage:
    python online_pipeline.py "the difference between Tool Use and Memory"
    python online_pipeline.py --interactive            # Interactive mode
    python online_pipeline.py --top-k 5 "what Chunking is"
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

from retrieval_core import SimpleBM25, dot_product, pseudo_embed, tokenize

# ---------- Configuration ----------

DEFAULT_TOP_K = 5
VECTOR_WEIGHT = 0.6  # Weight of vector retrieval in RRF fusion
BM25_WEIGHT = 0.4     # Weight of BM25 in RRF fusion
MAX_CONTEXT_CHARS = 3000


# ================================================================
# Stage 1: load index
# ================================================================

def load_index(index_dir: str) -> tuple[list[dict], list[list[float]], SimpleBM25, dict]:
    """Load all index files"""
    base = Path(index_dir)

    # Chunks metadata + content
    with open(base / "chunks.json", encoding="utf-8") as f:
        chunks = json.load(f)
    print(f"[load] chunks.json — {len(chunks)} chunks")

    # Vector embeddings
    with open(base / "embeddings.json", encoding="utf-8") as f:
        embeddings = json.load(f)
    embedding_dim = len(embeddings[0]) if embeddings else 0
    print(f"[load] embeddings.json — {len(embeddings)} × {embedding_dim}")

    # BM25 index
    with open(base / "bm25_index.json", encoding="utf-8") as f:
        bm25_index = SimpleBM25.from_dict(json.load(f))
    print(f"[load] bm25_index.json — {len(bm25_index.idf)} terms")

    with open(base / "index_meta.json") as f:
        meta = json.load(f)
    print(f"[load] pseudo embedding: hashing TF-IDF ({meta.get('pseudo_embedding_dim', embedding_dim)} dimensions)")

    return chunks, embeddings, bm25_index, meta


# ================================================================
# Stage 2: query understanding and rewriting (section 2.4.5)
# ================================================================

def understand_query(query: str) -> dict:
    """
    Perform simple query understanding and expansion.
    A full implementation would include reference resolution, synonym expansion, and intent classification.
    This shows the core idea.
    """
    # Detect whether this is a follow-up question with references
    has_pronoun = any(w in query for w in ["it", "he", "she", "this", "that", "these", "those"])

    # Simple synonym expansion
    expansions = {
        "tool use": ["tool calling", "tool use", "function calling"],
        "memory": ["memory", "state management", "context"],
        "rag": ["retrieval-augmented generation", "external knowledge", "knowledge base"],
        "chunking": ["chunking", "splitting", "document splitting"],
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
# Stage 3: retrieval (section 2.4.6)
# ================================================================

def dense_retrieve(
    query: str,
    meta: dict,
    embeddings: list[list[float]],
    chunks: list[dict],
    top_k: int = 20,
) -> list[dict]:
    """
    Pseudo vector retrieval: hashing TF-IDF embeds the query -> cosine similarity -> top-k.
    It keeps the teaching structure of dense retrieval without depending on external models.
    """
    query_vec = pseudo_embed(query, meta.get("pseudo_embedding_idf", {}))
    scores = [dot_product(emb, query_vec) for emb in embeddings]
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

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


def sparse_retrieve(query: str, bm25_index: SimpleBM25, chunks: list[dict], top_k: int = 20) -> list[dict]:
    """
    BM25 keyword recall: exact matching for proper nouns and terminology.
    Good at exact matching, but it does not understand semantic variants such as 'Tool Use' vs 'tool calling'.
    """
    tokenized = tokenize(query)
    scores = bm25_index.get_scores(tokenized)
    # Normalize BM25 scores to [0, 1]
    max_score = max(scores) if scores and max(scores) > 0 else 1
    scores = [s / max_score for s in scores]

    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

    results = []
    for idx in top_indices:
        if scores[idx] > 0:  # Keep only matched results
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
    """Filter: exclude drafts and stale content"""
    filtered = []
    for r in results:
        c = r["chunk"]
        # Filter drafts
        if c.get("status") == "draft":
            continue
        filtered.append(r)
    return filtered


def rrf_fusion(dense_results: list[dict], sparse_results: list[dict], k: int = 60) -> list[dict]:
    """
    Reciprocal Rank Fusion: merge two recall paths and deduplicate.
    The same chunk from different paths receives a higher rank because both paths agree.
    """
    scores = {}  # chunk_idx → fused_score

    for rank, r in enumerate(dense_results):
        idx = r["chunk_idx"]
        scores[idx] = scores.get(idx, 0) + VECTOR_WEIGHT / (k + rank + 1)

    for rank, r in enumerate(sparse_results):
        idx = r["chunk_idx"]
        scores[idx] = scores.get(idx, 0) + BM25_WEIGHT / (k + rank + 1)

    # Sort by fused score
    sorted_indices = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # Rebuild results while preserving chunk references, sources, and raw scores
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
# Stage 4: reranking (section 2.4.6)
# ================================================================

def rerank(
    query: str, candidates: list[dict], meta: dict, top_k: int = DEFAULT_TOP_K
) -> list[dict]:
    """
    Reranking: finely sort candidate chunks.

    This uses a score-based method: cosine similarity plus weighted fused score.
    In production, a cross-encoder is recommended for pairwise scoring; it is more accurate but more expensive.

    Key signal: score cliff. When the score drops sharply from #N to #N+1, truncate at N.
    """
    if len(candidates) <= top_k:
        return candidates

    query_vec = pseudo_embed(query, meta.get("pseudo_embedding_idf", {}))

    # Combine with the fused score using weights
    for c in candidates:
        chunk_vec = pseudo_embed(c["chunk"]["content"], meta.get("pseudo_embedding_idf", {}))
        sim_score = dot_product(chunk_vec, query_vec)
        c["rerank_score"] = 0.7 * float(sim_score) + 0.3 * c["fused_score"]

    # Sort
    ranked = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)

    # Detect score cliffs: adjacent score gap > 30% -> truncate
    cut_at = top_k
    for i in range(top_k, len(ranked)):
        if ranked[i - 1]["rerank_score"] > 0 and ranked[i]["rerank_score"] / ranked[i - 1]["rerank_score"] < 0.7:
            cut_at = i
            break

    return ranked[:cut_at]


# ================================================================
# Stage 5: context assembly (section 2.4.7)
# ================================================================

def assemble_context(query: str, ranked_chunks: list[dict], max_chars: int = MAX_CONTEXT_CHARS) -> str:
    """
    Arrange retrieval results into context usable by the LLM.
    Each chunk is labeled with source number, file name, section path, and updated time.
    """
    parts = []
    total_chars = 0

    for i, r in enumerate(ranked_chunks):
        c = r["chunk"]
        header = (
            f"[source {i + 1}] {c['source']} — {c['section_path']}\n"
            f"Updated at {c.get('updated_at', '?')}  |  "
            f"tags: {', '.join(c.get('tags', []))}  |  "
            f"score: {r.get('rerank_score', r['fused_score']):.3f}"
        )

        content = c["content"]
        total_chars += len(header) + len(content) + 4

        if total_chars > max_chars and i > 0:
            print(f"  [truncate] reached token budget limit, used {i} / {len(ranked_chunks)} chunks")
            break

        parts.append(f"{header}\n\n{content}")

    return "\n\n---\n\n".join(parts)


# ================================================================
# Stage 6: generation (simulated)
# ================================================================

def generate_answer(query: str, context: str, ranked_chunks: list[dict]) -> str:
    """
    Generate the final answer.

    This is a simulation showing the full prompt structure that would enter LLM context.
    In real use, replace this with an LLM API call.
    """
    sources_summary = "\n".join(
        f"  [{i + 1}] {r['chunk']['source']} → {r['chunk']['section_path']} "
        f"(score: {r.get('rerank_score', r['fused_score']):.3f})"
        for i, r in enumerate(ranked_chunks)
    )

    prompt = f"""You are a personal knowledge assistant. Answer the user's question based on the notes below.

## User Question
{query}

## Relevant Notes
{context}

## Answer Requirements
- Answer based on the notes above; do not fabricate
- Cite specific sources, such as [Source 1]
- If the notes do not contain a direct answer, say so clearly
- If the notes conflict, point that out and explain
"""
    print("\n" + "=" * 60)
    print("  📤 Final Prompt (to be sent to the LLM)")
    print("=" * 60)
    print(f"\n{prompt}\n")
    print(f"[tip] the prompt above is about {len(prompt)} characters")
    print(f"[tip] replace generate_answer() with an LLM API call to get the final answer\n")

    return prompt


# ================================================================
# Main flow
# ================================================================

def run_online_pipeline(
    query: str,
    index_dir: str = "output",
    top_k: int = DEFAULT_TOP_K,
    debug: bool = False,
):
    """Run the full online query flow"""
    print("=" * 60)
    print(f"  Online Query Pipeline")
    print(f"  Query: \"{query}\"")
    print("=" * 60)

    # ── Step 1: Load index ──
    print()
    chunks, embeddings, bm25_index, meta = load_index(index_dir)

    # ── Step 2: Query understanding ──
    print(f"\n── Query understanding (§2.4.5) ──")
    query_info = understand_query(query)
    print(f"  Original query: {query_info['original']}")
    if query_info["has_pronoun"]:
        print(f"  ⚠️ Detected references; context completion may be needed")
    if query_info["expanded_terms"]:
        print(f"  Expanded terms: {query_info['expanded_terms']}")

    search_query = query_info["expanded_query"]

    # ── Step 3: Multi-route retrieval ──
    print(f"\n── Multi-route retrieval (§2.4.6) ──")
    print(f"  Vector retrieval top-20 ...", end=" ")
    dense_results = dense_retrieve(search_query, meta, embeddings, chunks, top_k=20)
    print(f"hits {len(dense_results)}")

    print(f"  BM25 Recall top-20 ...", end=" ")
    sparse_results = sparse_retrieve(search_query, bm25_index, chunks, top_k=20)
    print(f"hits {len(sparse_results)}")

    # Metadata filtering
    dense_results = metadata_filter(dense_results)
    sparse_results = metadata_filter(sparse_results)

    # RRF fusion
    fused = rrf_fusion(dense_results, sparse_results)
    print(f"  RRF fusion → {len(fused)} candidates after deduplication")

    if debug:
        print(f"\n  Candidate details:")
        for i, r in enumerate(fused[:15]):
            c = r["chunk"]
            print(f"    #{i + 1} [{r['source']}] {c['section_path'][:50]} — "
                  f"fused score: {r['fused_score']:.4f}")

    # ── Step 4: Reranking ──
    print(f"\n── Reranking (§2.4.6) ──")
    ranked = rerank(search_query, fused, meta, top_k=top_k)
    print(f"  Rerank → top-{len(ranked)}")

    print(f"\n  Final selected chunks:")
    for i, r in enumerate(ranked):
        c = r["chunk"]
        print(f"    #{i + 1} [{c['source']}] {c['section_path']}")
        print(f"        score: {r['rerank_score']:.3f}  |  "
              f"{c['char_count']} characters  |  tags: {c.get('tags', [])}")

    # Score-cliff detection
    if len(ranked) >= 2:
        last = ranked[-1]["rerank_score"]
        if len(fused) > len(ranked):
            print(f"    🔻 Score cliff: after rank  {len(ranked)}  the remaining content contributes much less to the answer")

    # ── Step 5: Context assembly ──
    print(f"\n── Context assembly (§2.4.7) ──")
    context = assemble_context(query, ranked)
    print(f"  Assembly complete, total {len(context)} characters")

    # ── Step 6: Generate answer ──
    generate_answer(query, context, ranked)

    return ranked, context


# ================================================================
# CLI entry point
# ================================================================

def interactive_mode(index_dir: str, top_k: int, debug: bool):
    """Interactive query mode"""
    print("=" * 60)
    print("  Personal Knowledge Assistant - Interactive Query")
    print("  Enter a question to search; enter /quit to exit and /debug to toggle details")
    print("=" * 60)

    # Preload the index
    chunks, embeddings, bm25_index, meta = load_index(index_dir)

    while True:
        try:
            query = input("\n🔍 Your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
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
    parser = argparse.ArgumentParser(description="Online Query Pipeline")
    parser.add_argument("query", nargs="?", help="Query text")
    parser.add_argument("--index-dir", default="output", help="Index directory (default: output/)")
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K, help=f"Number to return (default: {DEFAULT_TOP_K})")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--debug", action="store_true", help="Show detailed candidate set")
    args = parser.parse_args()

    if args.interactive or not args.query:
        interactive_mode(args.index_dir, args.top_k, args.debug)
    else:
        run_online_pipeline(args.query, args.index_dir, args.top_k, args.debug)
