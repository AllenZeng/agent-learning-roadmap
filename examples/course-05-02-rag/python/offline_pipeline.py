"""
Offline indexing pipeline: raw notes -> searchable index

Corresponds to course-05-02 sections 2.4.2-2.4.4:
  2.4.2 Data ingestion and preprocessing - scan, parse, clean, and tag metadata
  2.4.3 Chunking strategy      - split by Markdown heading hierarchy
  2.4.4 Embedding and indexing   - vectorization + BM25 indexing

Usage:
    python offline_pipeline.py                # Use default notes/ and index/
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
    """Scan the notes directory and return all .md file paths sorted by modification time"""
    dir_path = Path(notes_dir)
    if not dir_path.exists():
        print(f"[error] notes directory does not exist: {notes_dir}")
        sys.exit(1)

    files = sorted(dir_path.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
    print(f"[scan] found {len(files)} Markdown notes")
    for f in files:
        print(f"        {f.name}  (modified at {time.strftime('%Y-%m-%d', time.localtime(f.stat().st_mtime))})")
    return files


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML frontmatter wrapped in --- and return (metadata, body)"""
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
    """Extract Markdown heading levels and return [{level, title, position}, ...]"""
    headings = []
    for m in re.finditer(r"^(#{1,6})\s+(.+)$", text, re.MULTILINE):
        level = len(m.group(1))
        title = m.group(2).strip()
        headings.append({"level": level, "title": title, "position": m.start()})
    return headings


def build_section_path(headings: list[dict], chunk_idx: int) -> str:
    """Build section_path from heading levels, such as 'Agent Tool Use Design > Relationship between Tool Use and Memory'"""
    if chunk_idx >= len(headings):
        return "body"

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
    """Clean note body: remove extra blank lines while temporarily keeping code blocks"""
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
    Split into chunks by ## heading hierarchy.
    Each chunk is a logical section that contains one topic.

    Return: [{content, char_count, section_path, heading_level}, ...]
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
                "section_path": headings[0]["title"] if headings else "body",
                "heading_level": 1,
                "heading_title": headings[0]["title"] if headings else "",
            }
        )

    return chunks


# ================================================================
# Stage 3: metadata tagging (section 2.4.2)
# ================================================================

def annotate_chunk(chunk: dict, source_file: str, frontmatter: dict, idx: int) -> dict:
    """Attach metadata such as source, time, tags, and status to the chunk"""
    # Generate a semantic chunk_id
    safe_name = Path(source_file).stem.replace(" ", "-").lower()
    safe_section = re.sub(r"[^\w]+", "-", chunk.get("section_path", "body")).lower()[:50]
    chunk_id = f"{safe_name}_sec_{idx:02d}"

    return {
        "chunk_id": chunk_id,
        "source": Path(source_file).name,
        "section_path": chunk.get("section_path", "body"),
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
    """Build a BM25 sparse retrieval index"""
    print(f"[BM25] building keyword index...")
    docs = [c["content"] for c in chunks]
    index = SimpleBM25(docs)
    print(f"[BM25] complete, vocabulary size: {len(index.idf)}")
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
    """Save all index files to the index/ directory"""
    os.makedirs(index_dir, exist_ok=True)

    # 1. Chunk metadata + content -> JSON
    chunks_path = os.path.join(index_dir, "chunks.json")
    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"[save] chunks.json  ({len(chunks)} records)")

    # 2. Vector embeddings -> JSON
    emb_path = os.path.join(index_dir, "embeddings.json")
    with open(emb_path, "w", encoding="utf-8") as f:
        json.dump(embeddings, f)
    embedding_dim = len(embeddings[0]) if embeddings else 0
    print(f"[save] embeddings.json  ({len(embeddings)} × {embedding_dim})")

    # 3. BM25 index -> JSON
    bm25_path = os.path.join(index_dir, "bm25_index.json")
    with open(bm25_path, "w", encoding="utf-8") as f:
        json.dump(bm25_index.to_dict(), f, ensure_ascii=False)
    print(f"[save] bm25_index.json")

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
    print(f"[save] index_meta.json")


# ================================================================
# Main flow
# ================================================================

def run_offline_pipeline(notes_dir: str = "notes", index_dir: str = "output"):
    """Run the full offline indexing flow"""
    print("=" * 60)
    print("  Offline Indexing Pipeline")
    print("  raw notes -> parse and clean -> Chunking -> Embedding -> index storage")
    print("=" * 60)

    # ── Step 1: Scan ──
    files = scan_notes(notes_dir)
    if not files:
        print("[error] No Markdown files found; run generate_notes.py first")
        return

    all_chunks = []

    for file_path in files:
        print(f"\n── Processing: {file_path.name} ──")

        # ── Step 2: Parse ──
        raw_text = file_path.read_text(encoding="utf-8")
        frontmatter, body = parse_frontmatter(raw_text)
        print(f"   Status: {frontmatter.get('status', 'unknown')}  |  "
              f"tags: {frontmatter.get('tags', [])}  |  "
              f"Updated: {frontmatter.get('updated', '?')}")

        # ── Step 3: Clean ──
        body = clean_content(body)

        # ── Step 4: Chunking ──
        headings = extract_headings(body)
        print(f"   heading levels: {len(headings)}  |  ", end="")
        chunks = chunk_by_headings(body, headings)
        print(f"split out {len(chunks)} chunks")

        # ── Step 5: Metadata tagging ──
        for i, chunk in enumerate(chunks):
            annotated = annotate_chunk(chunk, str(file_path), frontmatter, i)
            all_chunks.append(annotated)
            print(f"     chunk {i:02d}: {annotated['chunk_id']}  "
                  f"({annotated['char_count']} characters)  "
                  f"→ {annotated['section_path'][:60]}")

    # ── Step 6: Filter drafts ──
    published = [c for c in all_chunks if c["status"] != "draft"]
    if len(published) < len(all_chunks):
        print(f"\n[filter] excluded {len(all_chunks) - len(published)} draft chunks，"
              f"kept {len(published)} published chunks")

    # ── Step 7: Embedding ──
    print(f"\n[Embedding] using pseudo embedding (hashing TF-IDF, {PSEUDO_EMBEDDING_DIM} dimensions)")
    docs = [c["content"] for c in published]
    pseudo_embedding_idf = build_idf(docs)
    embeddings = build_pseudo_embeddings(docs, pseudo_embedding_idf)
    embedding_dim = len(embeddings[0]) if embeddings else 0
    print(f"[Embedding] complete, vector dimension: {embedding_dim}")

    # ── Step 9: BM25 index ──
    bm25_index = build_bm25_index(published)

    # ── Step 10: Save ──
    print(f"\n── save index to {index_dir}/ ──")
    save_index(index_dir, published, embeddings, bm25_index, pseudo_embedding_idf)

    print(f"\n{'=' * 60}")
    print(f"  Offline indexing complete!")
    print(f"  notes: {len(files)} files")
    print(f"  Chunk: {len(published)} published")
    print(f"  total characters: {sum(c['char_count'] for c in published):,}")
    print(f"  Index directory: {index_dir}/")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Offline Indexing Pipeline")
    parser.add_argument("--notes-dir", default="notes", help="notes directory (default: notes/)")
    parser.add_argument("--index-dir", default="output", help="index output directory (default: output/)")
    args = parser.parse_args()
    run_offline_pipeline(args.notes_dir, args.index_dir)
