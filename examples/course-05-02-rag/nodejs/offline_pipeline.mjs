/**
 * Offline indexing pipeline: raw notes -> searchable index
 *
 * Corresponds to course-05-02 sections 2.4.2-2.4.4:
 *   2.4.2 Data ingestion and preprocessing - scan, parse, clean, and tag metadata
 *   2.4.3 Chunking strategy      - split by Markdown heading hierarchy
 *   2.4.4 Embedding and indexing   - vectorization + BM25 indexing
 *
 * Usage:
 *   node offline_pipeline.mjs
 *   node offline_pipeline.mjs --notes-dir custom/notes --index-dir custom/index
 */

import { readdir, readFile, mkdir, writeFile, stat } from "node:fs/promises";
import { join, extname } from "node:path";
import {
  DEFAULT_RETRIEVER,
  PSEUDO_EMBEDDING_DIM,
  SimpleBM25,
  buildIdf,
  buildPseudoEmbeddings,
  tokenize,
} from "./retrieval_core.mjs";

// ---------- Configuration ----------

const MIN_CHUNK_CHARS = 100;

// ---------- Helper functions ----------

function parseArgs() {
  const args = process.argv.slice(2);
  const opts = {
    notesDir: "notes",
    indexDir: "output",
    retriever: DEFAULT_RETRIEVER,
  };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--notes-dir" && args[i + 1]) opts.notesDir = args[++i];
    if (args[i] === "--index-dir" && args[i + 1]) opts.indexDir = args[++i];
  }
  return opts;
}

// ================================================================
// Stage 1: data ingestion and preprocessing (section 2.4.2)
// ================================================================

async function scanNotes(notesDir) {
  try {
    const files = await readdir(notesDir);
    const mdFiles = files.filter((f) => extname(f) === ".md");

    // Sort by modification time
    const withStats = await Promise.all(
      mdFiles.map(async (f) => {
        const s = await stat(join(notesDir, f));
        return { name: f, mtime: s.mtime };
      })
    );
    withStats.sort((a, b) => b.mtime - a.mtime);

    console.log(`[scan] found ${mdFiles.length} Markdown notes`);
    for (const f of withStats) {
      console.log(
        `        ${f.name}  (modified at ${f.mtime.toISOString().slice(0, 10)})`
      );
    }
    return withStats.map((f) => f.name);
  } catch {
    console.error(`[error] notes directory does not exist: ${notesDir}`);
    process.exit(1);
  }
}

function parseFrontmatter(text) {
  const meta = {};
  let body = text;
  if (text.startsWith("---")) {
    const parts = text.split("---");
    if (parts.length >= 3) {
      for (const line of parts[1].trim().split("\n")) {
        const colonIdx = line.indexOf(":");
        if (colonIdx > 0) {
          const key = line.slice(0, colonIdx).trim();
          let val = line.slice(colonIdx + 1).trim();
          if (val.startsWith("[") && val.endsWith("]")) {
            val = val
              .slice(1, -1)
              .split(",")
              .map((v) => v.trim().replace(/['"]/g, ""));
          }
          meta[key] = val;
        }
      }
      body = parts.slice(2).join("---");
    }
  }
  return { meta, body };
}

function extractHeadings(text) {
  const headings = [];
  const re = /^(#{1,6})\s+(.+)$/gm;
  let m;
  while ((m = re.exec(text)) !== null) {
    headings.push({
      level: m[1].length,
      title: m[2].trim(),
      position: m.index,
    });
  }
  return headings;
}

function buildSectionPath(headings, chunkIdx) {
  if (chunkIdx >= headings.length) return "body";

  let current = headings[chunkIdx];
  const pathParts = [];

  for (let i = chunkIdx; i >= 0; i--) {
    const h = headings[i];
    if (h.level <= current.level) {
      pathParts.unshift(h.title);
      if (h.level === 1) break;
      current = h;
    }
  }

  return pathParts.length > 0 ? pathParts.join(" > ") : headings[chunkIdx].title;
}

function cleanContent(text) {
  text = text.replace(/\r\n/g, "\n").replace(/\r/g, "\n");
  text = text.replace(/\n{4,}/g, "\n\n\n");
  return text.trim();
}

// ================================================================
// Stage 2: Chunking (section 2.4.3)
// ================================================================

function chunkByHeadings(text, headings) {
  const chunks = [];
  const effective = headings.filter((h) => h.level >= 2);

  for (let i = 0; i < effective.length; i++) {
    const heading = effective[i];
    const start = heading.position;
    const end =
      i + 1 < effective.length ? effective[i + 1].position : text.length;
    let content = text.slice(start, end).trim();

    const firstNewline = content.indexOf("\n");
    if (firstNewline > 0) {
      content = content.slice(firstNewline).trim();
    }

    if (content.length >= MIN_CHUNK_CHARS) {
      const headingIndex = headings.indexOf(heading);
      chunks.push({
        content,
        charCount: content.length,
        sectionPath: buildSectionPath(headings, headingIndex),
        headingLevel: heading.level,
        headingTitle: heading.title,
      });
    }
  }

  // No ## headings -> treat the whole document as one chunk
  if (chunks.length === 0 && text.trim().length >= MIN_CHUNK_CHARS) {
    let body = text;
    if (headings.length > 0 && headings[0].level === 1) {
      const firstLineEnd = text.indexOf("\n");
      if (firstLineEnd > 0) body = text.slice(firstLineEnd).trim();
    }
    chunks.push({
      content: body,
      charCount: body.length,
      sectionPath: headings.length > 0 ? headings[0].title : "body",
      headingLevel: 1,
      headingTitle: headings.length > 0 ? headings[0].title : "",
    });
  }

  return chunks;
}

// ================================================================
// Stage 3: metadata tagging (section 2.4.2)
// ================================================================

function annotateChunk(chunk, sourceFile, frontmatter, idx) {
  const safeName = sourceFile.replace(/\.md$/, "").replace(/\s+/g, "-").toLowerCase();
  const safeSection = chunk.sectionPath
    .replace(/[^\w]+/g, "-")
    .toLowerCase()
    .slice(0, 50);
  const chunkId = `${safeName}_sec_${String(idx).padStart(2, "0")}`;

  return {
    chunk_id: chunkId,
    source: sourceFile,
    section_path: chunk.sectionPath,
    char_count: chunk.charCount,
    created_at: String(frontmatter.created || ""),
    updated_at: String(frontmatter.updated || ""),
    tags: frontmatter.tags || [],
    status: frontmatter.status || "unknown",
    content: chunk.content,
  };
}

// ================================================================
// Stage 4: Embedding + BM25 index (section 2.4.4)
// ================================================================

function buildBM25Index(chunks) {
  console.log(`[BM25] building keyword index...`);
  const docs = chunks.map((c) => c.content);
  const index = new SimpleBM25(docs);
  console.log(`[BM25] complete, vocabulary size: ${Object.keys(index.idf).length}`);
  return index;
}

// ================================================================
// Save the index
// ================================================================

async function saveIndex(indexDir, chunks, embeddings, bm25Index, indexMeta) {
  await mkdir(indexDir, { recursive: true });

  // 1. Chunks metadata + content -> JSON
  const chunksPath = join(indexDir, "chunks.json");
  await writeFile(chunksPath, JSON.stringify(chunks, null, 2), "utf-8");
  console.log(`[save] chunks.json  (${chunks.length} records)`);

  // 2. Vector embeddings -> JSON
  const embPath = join(indexDir, "embeddings.json");
  await writeFile(embPath, JSON.stringify(embeddings), "utf-8");
  console.log(
    `[save] embeddings.json  (${embeddings.length} × ${embeddings[0]?.length || 0})`
  );

  // 3. BM25 → JSON
  const bm25Path = join(indexDir, "bm25_index.json");
  // Save tokenized docs for later retrieval
  const bm25Data = {
    ...bm25Index.toJSON(),
    docs: chunks.map((c) => tokenize(c.content)),
  };
  await writeFile(bm25Path, JSON.stringify(bm25Data), "utf-8");
  console.log(`[save] bm25_index.json`);

  // 4. Index metadata
  const meta = {
    total_chunks: chunks.length,
    embedding_dim: embeddings[0]?.length || 0,
    retriever: indexMeta.retriever,
    embedding_model: indexMeta.embeddingModel,
    pseudo_embedding_dim: indexMeta.pseudoEmbeddingDim,
    pseudo_embedding_idf: indexMeta.pseudoEmbeddingIdf,
    total_chars: chunks.reduce((s, c) => s + c.char_count, 0),
    sources: [...new Set(chunks.map((c) => c.source))],
    built_at: new Date().toISOString(),
  };
  const metaPath = join(indexDir, "index_meta.json");
  await writeFile(metaPath, JSON.stringify(meta, null, 2), "utf-8");
  console.log(`[save] index_meta.json`);
}

// ================================================================
// Main flow
// ================================================================

async function runOfflinePipeline(opts) {
  const { notesDir, indexDir, retriever } = opts;
  console.log("=".repeat(60));
  console.log("  Offline Indexing Pipeline");
  console.log("  raw notes -> parse and clean -> Chunking -> Embedding -> index storage");
  console.log("=".repeat(60));

  // ── Step 1: Scan ──
  const files = await scanNotes(notesDir);
  if (files.length === 0) {
    console.log("[error] No Markdown files found");
    return;
  }

  const allChunks = [];

  for (const fileName of files) {
    console.log(`\n── Processing: ${fileName} ──`);

    // ── Step 2: Parse ──
    const rawText = await readFile(join(notesDir, fileName), "utf-8");
    const { meta, body } = parseFrontmatter(rawText);
    console.log(
      `   Status: ${meta.status || "unknown"}  |  ` +
        `tags: [${(meta.tags || []).join(", ")}]  |  ` +
        `Updated: ${meta.updated || "?"}`
    );

    // ── Step 3: Clean ──
    const cleaned = cleanContent(body);

    // ── Step 4: Chunking ──
    const headings = extractHeadings(cleaned);
    const chunks = chunkByHeadings(cleaned, headings);
    console.log(
      `   heading levels: ${headings.length}  | split out ${chunks.length} chunks`
    );

    // ── Step 5: Metadata tagging ──
    for (let i = 0; i < chunks.length; i++) {
      const annotated = annotateChunk(chunks[i], fileName, meta, i);
      allChunks.push(annotated);
      console.log(
        `     chunk ${String(i).padStart(2, "0")}: ${annotated.chunk_id}  ` +
          `(${annotated.char_count} characters)  → ${annotated.section_path.slice(0, 60)}`
      );
    }
  }

  // ── Step 6: Filter drafts ──
  const published = allChunks.filter((c) => c.status !== "draft");
  if (published.length < allChunks.length) {
    console.log(
      `\n[filter] excluded ${allChunks.length - published.length} draft chunks，` +
        `kept ${published.length} published chunks`
    );
  }

  // ── Step 7: Embedding ──
  console.log(`\n[Embedding] using pseudo embedding (hashing TF-IDF, ${PSEUDO_EMBEDDING_DIM} dimensions)`);
  const docs = published.map((c) => c.content);
  const pseudoEmbeddingIdf = buildIdf(docs);
  const embeddings = buildPseudoEmbeddings(docs, pseudoEmbeddingIdf);
  console.log(`[Embedding] complete, vector dimension: ${embeddings[0]?.length || "?"}`);

  // ── Step 9: BM25 index ──
  const bm25Index = buildBM25Index(published);

  // ── Step 10: Save ──
  console.log(`\n── save index to ${indexDir}/ ──`);
  await saveIndex(indexDir, published, embeddings, bm25Index, {
    retriever,
    embeddingModel: "pseudo-hashing-tfidf",
    pseudoEmbeddingDim: PSEUDO_EMBEDDING_DIM,
    pseudoEmbeddingIdf,
  });

  console.log(`\n${"=".repeat(60)}`);
  console.log(`  Offline indexing complete!`);
  console.log(`  notes: ${files.length} files`);
  console.log(`  Chunk: ${published.length} published`);
  console.log(
    `  total characters: ${published.reduce((s, c) => s + c.char_count, 0).toLocaleString()}`
  );
  console.log(`  Index directory: ${indexDir}/`);
  console.log(`${"=".repeat(60)}`);
}

// Run
const opts = parseArgs();
runOfflinePipeline(opts).catch((err) => {
  console.error("Pipeline failed:", err);
  process.exit(1);
});
