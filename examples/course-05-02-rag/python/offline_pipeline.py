"""
离线建库 Pipeline：原始笔记 → 可检索索引

对应 course-05-02 §2.4.2–2.4.4 的内容：
  2.4.2 数据接入与预处理 — 扫描、解析、清洗、元数据标注
  2.4.3 Chunking 策略      — 按 Markdown 标题层级切分
  2.4.4 Embedding 与索引   — 向量化 + BM25 索引入库

用法：
    python offline_pipeline.py                # 使用默认 notes/ 和 index/
    python offline_pipeline.py --notes-dir custom/notes --index-dir custom/index
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

from retrieval_core import (
    DEFAULT_RETRIEVER,
    PSEUDO_EMBEDDING_DIM,
    SimpleBM25,
    build_idf,
    build_pseudo_embeddings,
    tokenize,
)

# ---------- Configuration ----------

# Minimum chunk character count (shorter chunks are merged into the previous chunk)
MIN_CHUNK_CHARS = 100


# ================================================================
# Stage 1: data ingestion and preprocessing (section 2.4.2)
# ================================================================

def scan_notes(notes_dir: str) -> list[Path]:
    """扫描 notes 目录，返回所有 .md 文件路径（按修改时间排序）"""
    dir_path = Path(notes_dir)
    if not dir_path.exists():
        print(f"[错误] notes 目录不存在: {notes_dir}")
        sys.exit(1)

    files = sorted(dir_path.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
    print(f"[扫描] 发现 {len(files)} 篇 Markdown 笔记")
    for f in files:
        print(f"        {f.name}  (修改于 {time.strftime('%Y-%m-%d', time.localtime(f.stat().st_mtime))})")
    return files


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """解析 YAML frontmatter（--- 包裹的元数据块），返回 (元数据, 正文)"""
    meta = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().split("\n"):
                if ":" in line:
                    key, _, val = line.partition(":")
                    key, val = key.strip(), val.strip()
                    # Simple list parsing [a, b, c]
                    if val.startswith("[") and val.endswith("]"):
                        val = [v.strip().strip("\"'") for v in val[1:-1].split(",")]
                    meta[key] = val
            body = parts[2]
    return meta, body


def extract_headings(text: str) -> list[dict]:
    """提取 Markdown 标题层级，返回 [{level, title, position}, ...]"""
    headings = []
    for m in re.finditer(r"^(#{1,6})\s+(.+)$", text, re.MULTILINE):
        level = len(m.group(1))
        title = m.group(2).strip()
        headings.append({"level": level, "title": title, "position": m.start()})
    return headings


def build_section_path(headings: list[dict], chunk_idx: int) -> str:
    """根据标题层级构建 section_path，如 'Agent Tool Use 设计 > Tool Use 与 Memory 的关系'"""
    if chunk_idx >= len(headings):
        return "正文"

    current = headings[chunk_idx]
    path_parts = []

    # Look upward for parent headings
    for h in reversed(headings[: chunk_idx + 1]):
        if h["level"] <= current["level"]:
            path_parts.insert(0, h["title"])
            if h["level"] == 1:
                break
        current = h

    return " > ".join(path_parts) if path_parts else headings[chunk_idx]["title"]


def clean_content(text: str) -> str:
    """清洗笔记正文：去除多余空行、代码块暂时保留"""
    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Remove runs of more than three blank lines
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip()


# ================================================================
# Stage 2: Chunking (section 2.4.3)
# ================================================================

def chunk_by_headings(text: str, headings: list[dict]) -> list[dict]:
    """
    按 ## 标题层级切分为 chunk。
    每个 chunk 是一个逻辑小节，自包含一个主题。

    返回: [{content, char_count, section_path, heading_level}, ...]
    """
    chunks = []
    effective_headings = [h for h in headings if h["level"] >= 2]

    for i, h in enumerate(effective_headings):
        start = h["position"]
        # End position of the next peer heading
        end = effective_headings[i + 1]["position"] if i + 1 < len(effective_headings) else len(text)
        content = text[start:end].strip()

        # Extract content after the heading line
        first_newline = content.find("\n")
        if first_newline > 0:
            content = content[first_newline:].strip()

        if len(content) >= MIN_CHUNK_CHARS:
            chunks.append(
                {
                    "content": content,
                    "char_count": len(content),
                    "section_path": build_section_path(headings, headings.index(h)),
                    "heading_level": h["level"],
                    "heading_title": h["title"],
                }
            )

    # If there are no ## headings, treat the whole document as one chunk
    if not chunks and len(text.strip()) >= MIN_CHUNK_CHARS:
        # Remove the h1 heading line
        body = text
        if headings and headings[0]["level"] == 1:
            first_line_end = text.find("\n")
            if first_line_end > 0:
                body = text[first_line_end:].strip()
        chunks.append(
            {
                "content": body,
                "char_count": len(body),
                "section_path": headings[0]["title"] if headings else "正文",
                "heading_level": 1,
                "heading_title": headings[0]["title"] if headings else "",
            }
        )

    return chunks


# ================================================================
# Stage 3: metadata tagging (section 2.4.2)
# ================================================================

def annotate_chunk(chunk: dict, source_file: str, frontmatter: dict, idx: int) -> dict:
    """为 chunk 绑定来源、时间、标签、状态等元数据"""
    # Generate a semantic chunk_id
    safe_name = Path(source_file).stem.replace(" ", "-").lower()
    safe_section = re.sub(r"[^\w]+", "-", chunk.get("section_path", "body")).lower()[:50]
    chunk_id = f"{safe_name}_sec_{idx:02d}"

    return {
        "chunk_id": chunk_id,
        "source": Path(source_file).name,
        "section_path": chunk.get("section_path", "正文"),
        "char_count": chunk["char_count"],
        "created_at": str(frontmatter.get("created", "")),
        "updated_at": str(frontmatter.get("updated", "")),
        "tags": frontmatter.get("tags", []),
        "status": frontmatter.get("status", "unknown"),
        "content": chunk["content"],
    }


# ================================================================
# Stage 4: pseudo-Embedding + index (section 2.4.4)
# ================================================================

def build_bm25_index(chunks: list[dict]):
    """构建 BM25 稀疏检索索引"""
    print(f"[BM25] 正在构建关键词索引...")
    docs = [c["content"] for c in chunks]
    index = SimpleBM25(docs)
    print(f"[BM25] 完成，词汇量: {len(index.idf)}")
    return index


# ================================================================
# Save the index
# ================================================================

def save_index(
    index_dir: str,
    chunks: list[dict],
    embeddings: list[list[float]],
    bm25_index: SimpleBM25,
    pseudo_embedding_idf: dict[str, float],
):
    """保存所有索引文件到 index/ 目录"""
    os.makedirs(index_dir, exist_ok=True)

    # 1. Chunk metadata + content -> JSON
    chunks_path = os.path.join(index_dir, "chunks.json")
    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"[保存] chunks.json  ({len(chunks)} 条记录)")

    # 2. Vector embeddings -> JSON
    emb_path = os.path.join(index_dir, "embeddings.json")
    with open(emb_path, "w", encoding="utf-8") as f:
        json.dump(embeddings, f)
    embedding_dim = len(embeddings[0]) if embeddings else 0
    print(f"[保存] embeddings.json  ({len(embeddings)} × {embedding_dim})")

    # 3. BM25 index -> JSON
    bm25_path = os.path.join(index_dir, "bm25_index.json")
    with open(bm25_path, "w", encoding="utf-8") as f:
        json.dump(bm25_index.to_dict(), f, ensure_ascii=False)
    print(f"[保存] bm25_index.json")

    # 4. Index metadata
    meta = {
        "total_chunks": len(chunks),
        "embedding_dim": embedding_dim,
        "retriever": DEFAULT_RETRIEVER,
        "embedding_model": "pseudo-hashing-tfidf",
        "pseudo_embedding_dim": PSEUDO_EMBEDDING_DIM,
        "pseudo_embedding_idf": pseudo_embedding_idf,
        "total_chars": sum(c["char_count"] for c in chunks),
        "sources": list(set(c["source"] for c in chunks)),
        "built_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    meta_path = os.path.join(index_dir, "index_meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"[保存] index_meta.json")


# ================================================================
# Main flow
# ================================================================

def run_offline_pipeline(notes_dir: str = "notes", index_dir: str = "output"):
    """执行完整的离线建库流程"""
    print("=" * 60)
    print("  离线建库 Pipeline")
    print("  原始笔记 → 解析清洗 → Chunking → Embedding → 索引入库")
    print("=" * 60)

    # ── Step 1: Scan ──
    files = scan_notes(notes_dir)
    if not files:
        print("[错误] 没有找到 Markdown 文件，请先运行 generate_notes.py")
        return

    all_chunks = []

    for file_path in files:
        print(f"\n── 处理: {file_path.name} ──")

        # ── Step 2: Parse ──
        raw_text = file_path.read_text(encoding="utf-8")
        frontmatter, body = parse_frontmatter(raw_text)
        print(f"   状态: {frontmatter.get('status', 'unknown')}  |  "
              f"标签: {frontmatter.get('tags', [])}  |  "
              f"更新: {frontmatter.get('updated', '?')}")

        # ── Step 3: Clean ──
        body = clean_content(body)

        # ── Step 4: Chunking ──
        headings = extract_headings(body)
        print(f"   标题层级: {len(headings)} 个  |  ", end="")
        chunks = chunk_by_headings(body, headings)
        print(f"切出 {len(chunks)} 个 chunk")

        # ── Step 5: Metadata tagging ──
        for i, chunk in enumerate(chunks):
            annotated = annotate_chunk(chunk, str(file_path), frontmatter, i)
            all_chunks.append(annotated)
            print(f"     chunk {i:02d}: {annotated['chunk_id']}  "
                  f"({annotated['char_count']} 字符)  "
                  f"→ {annotated['section_path'][:60]}")

    # ── Step 6: Filter drafts ──
    published = [c for c in all_chunks if c["status"] != "draft"]
    if len(published) < len(all_chunks):
        print(f"\n[过滤] 排除 {len(all_chunks) - len(published)} 个草稿 chunk，"
              f"保留 {len(published)} 个已发布 chunk")

    # ── Step 7: Embedding ──
    print(f"\n[Embedding] 使用伪 embedding（hashing TF-IDF, {PSEUDO_EMBEDDING_DIM} 维）")
    docs = [c["content"] for c in published]
    pseudo_embedding_idf = build_idf(docs)
    embeddings = build_pseudo_embeddings(docs, pseudo_embedding_idf)
    embedding_dim = len(embeddings[0]) if embeddings else 0
    print(f"[Embedding] 完成，向量维度: {embedding_dim}")

    # ── Step 9: BM25 index ──
    bm25_index = build_bm25_index(published)

    # ── Step 10: Save ──
    print(f"\n── 保存索引到 {index_dir}/ ──")
    save_index(index_dir, published, embeddings, bm25_index, pseudo_embedding_idf)

    print(f"\n{'=' * 60}")
    print(f"  离线建库完成！")
    print(f"  笔记: {len(files)} 篇")
    print(f"  Chunk: {len(published)} 个（已发布）")
    print(f"  总字符: {sum(c['char_count'] for c in published):,}")
    print(f"  索引目录: {index_dir}/")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="离线建库 Pipeline")
    parser.add_argument("--notes-dir", default="notes", help="笔记目录 (默认: notes/)")
    parser.add_argument("--index-dir", default="output", help="索引输出目录 (默认: output/)")
    args = parser.parse_args()
    run_offline_pipeline(args.notes_dir, args.index_dir)
