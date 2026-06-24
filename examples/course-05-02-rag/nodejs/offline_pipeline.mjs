/**
 * 离线建库 Pipeline：原始笔记 → 可检索索引
 *
 * 对应 course-05-02 §2.4.2–2.4.4：
 *   2.4.2 数据接入与预处理 — 扫描、解析、清洗、元数据标注
 *   2.4.3 Chunking 策略      — 按 Markdown 标题层级切分
 *   2.4.4 Embedding 与索引   — 向量化 + BM25 索引入库
 *
 * 用法：
 *   node offline_pipeline.mjs
 *   node offline_pipeline.mjs --notes-dir custom/notes --index-dir custom/index
 */

import { readdir, readFile, mkdir, writeFile, stat } from "node:fs/promises";
import { join, extname } from "node:path";
import { fileURLToPath } from "node:url";
import { pipeline } from "@huggingface/transformers";

// ---------- 配置 ----------

const EMBEDDING_MODEL = "Xenova/all-MiniLM-L6-v2";
const MIN_CHUNK_CHARS = 100;

// ---------- 工具函数 ----------

function tokenize(text) {
  return text.toLowerCase().match(/\w+/g) || [];
}

function parseArgs() {
  const args = process.argv.slice(2);
  const opts = { notesDir: "notes", indexDir: "output" };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--notes-dir" && args[i + 1]) opts.notesDir = args[++i];
    if (args[i] === "--index-dir" && args[i + 1]) opts.indexDir = args[++i];
  }
  return opts;
}

// ================================================================
// 阶段一：数据接入与预处理（§2.4.2）
// ================================================================

async function scanNotes(notesDir) {
  try {
    const files = await readdir(notesDir);
    const mdFiles = files.filter((f) => extname(f) === ".md");

    // 按修改时间排序
    const withStats = await Promise.all(
      mdFiles.map(async (f) => {
        const s = await stat(join(notesDir, f));
        return { name: f, mtime: s.mtime };
      })
    );
    withStats.sort((a, b) => b.mtime - a.mtime);

    console.log(`[扫描] 发现 ${mdFiles.length} 篇 Markdown 笔记`);
    for (const f of withStats) {
      console.log(
        `        ${f.name}  (修改于 ${f.mtime.toISOString().slice(0, 10)})`
      );
    }
    return withStats.map((f) => f.name);
  } catch {
    console.error(`[错误] notes 目录不存在: ${notesDir}`);
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
  if (chunkIdx >= headings.length) return "正文";

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
// 阶段二：Chunking（§2.4.3）
// ================================================================

function chunkByHeadings(text, headings) {
  const chunks = [];
  const effective = headings.filter((h) => h.level >= 2);

  for (let i = 0; i < effective.length; i++) {
    const start = effective[i].position;
    const end =
      i + 1 < effective.length ? effective[i + 1].position : text.length;
    let content = text.slice(start, end).trim();

    const firstNewline = content.indexOf("\n");
    if (firstNewline > 0) {
      content = content.slice(firstNewline).trim();
    }

    if (content.length >= MIN_CHUNK_CHARS) {
      chunks.push({
        content,
        charCount: content.length,
        sectionPath: buildSectionPath(headings, i),
        headingLevel: effective[i].level,
        headingTitle: effective[i].title,
      });
    }
  }

  // 无 ## 标题 → 整篇作为一个 chunk
  if (chunks.length === 0 && text.trim().length >= MIN_CHUNK_CHARS) {
    let body = text;
    if (headings.length > 0 && headings[0].level === 1) {
      const firstLineEnd = text.indexOf("\n");
      if (firstLineEnd > 0) body = text.slice(firstLineEnd).trim();
    }
    chunks.push({
      content: body,
      charCount: body.length,
      sectionPath: headings.length > 0 ? headings[0].title : "正文",
      headingLevel: 1,
      headingTitle: headings.length > 0 ? headings[0].title : "",
    });
  }

  return chunks;
}

// ================================================================
// 阶段三：元数据标注（§2.4.2）
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
// 阶段四：Embedding + BM25 索引（§2.4.4）
// ================================================================

async function buildEmbeddings(chunks, extractor) {
  console.log(`[Embedding] 正在为 ${chunks.length} 个 chunk 生成向量...`);
  const texts = chunks.map((c) => c.content);
  const embeddings = [];

  // 批量提取（ transformers.js 内部已批处理优化）
  for (let i = 0; i < texts.length; i++) {
    const output = await extractor(texts[i], {
      pooling: "mean",
      normalize: true,
    });
    embeddings.push(Array.from(output.data));
    if ((i + 1) % 10 === 0 || i === texts.length - 1) {
      process.stdout.write(`\r  进度: ${i + 1}/${texts.length}`);
    }
  }
  console.log(
    `\n[Embedding] 完成，向量维度: ${embeddings[0]?.length || "?"}`
  );
  return embeddings;
}

/**
 * 简易 BM25 实现（避免额外依赖）
 *
 * BM25(q, d) = Σ IDF(qi) * (tf(qi, d) * (k1 + 1)) / (tf(qi, d) + k1 * (1 - b + b * |d|/avgdl))
 */
class SimpleBM25 {
  constructor(docs, k1 = 1.5, b = 0.75) {
    this.k1 = k1;
    this.b = b;
    this.docs = docs.map((d) => tokenize(d));
    this.docCount = docs.length;
    this.avgdl = this.docs.reduce((s, d) => s + d.length, 0) / this.docCount;

    // 计算 IDF
    const df = {};
    for (const doc of this.docs) {
      const seen = new Set(doc);
      for (const term of seen) {
        df[term] = (df[term] || 0) + 1;
      }
    }
    this.idf = {};
    for (const [term, count] of Object.entries(df)) {
      this.idf[term] = Math.log(
        (this.docCount - count + 0.5) / (count + 0.5) + 1
      );
    }
  }

  getScores(queryTokens) {
    return this.docs.map((doc, docIdx) => {
      let score = 0;
      const tf = {};
      for (const t of doc) tf[t] = (tf[t] || 0) + 1;

      for (const term of queryTokens) {
        if (!this.idf[term] || !tf[term]) continue;
        const numerator = tf[term] * (this.k1 + 1);
        const denominator =
          tf[term] +
          this.k1 * (1 - this.b + (this.b * doc.length) / this.avgdl);
        score += this.idf[term] * (numerator / denominator);
      }
      return score;
    });
  }

  toJSON() {
    return {
      k1: this.k1,
      b: this.b,
      docCount: this.docCount,
      avgdl: this.avgdl,
      idf: this.idf,
    };
  }

  static fromJSON(data) {
    const bm25 = Object.create(SimpleBM25.prototype);
    Object.assign(bm25, data);
    bm25.docs = []; // 检索时需要重新设置
    return bm25;
  }
}

function buildBM25Index(chunks) {
  console.log(`[BM25] 正在构建关键词索引...`);
  const docs = chunks.map((c) => c.content);
  const index = new SimpleBM25(docs);
  console.log(`[BM25] 完成，词汇量: ${Object.keys(index.idf).length}`);
  return index;
}

// ================================================================
// 保存索引
// ================================================================

async function saveIndex(indexDir, chunks, embeddings, bm25Index) {
  await mkdir(indexDir, { recursive: true });

  // 1. Chunks 元数据 + 内容 → JSON
  const chunksPath = join(indexDir, "chunks.json");
  await writeFile(chunksPath, JSON.stringify(chunks, null, 2), "utf-8");
  console.log(`[保存] chunks.json  (${chunks.length} 条记录)`);

  // 2. 向量嵌入 → JSON
  const embPath = join(indexDir, "embeddings.json");
  await writeFile(embPath, JSON.stringify(embeddings), "utf-8");
  console.log(
    `[保存] embeddings.json  (${embeddings.length} × ${embeddings[0]?.length || 0})`
  );

  // 3. BM25 → JSON
  const bm25Path = join(indexDir, "bm25_index.json");
  // 保存 tokenized docs 供后续检索使用
  const bm25Data = {
    ...bm25Index.toJSON(),
    docs: chunks.map((c) => tokenize(c.content)),
  };
  await writeFile(bm25Path, JSON.stringify(bm25Data), "utf-8");
  console.log(`[保存] bm25_index.json`);

  // 4. 索引元信息
  const meta = {
    total_chunks: chunks.length,
    embedding_dim: embeddings[0]?.length || 0,
    embedding_model: EMBEDDING_MODEL,
    total_chars: chunks.reduce((s, c) => s + c.char_count, 0),
    sources: [...new Set(chunks.map((c) => c.source))],
    built_at: new Date().toISOString(),
  };
  const metaPath = join(indexDir, "index_meta.json");
  await writeFile(metaPath, JSON.stringify(meta, null, 2), "utf-8");
  console.log(`[保存] index_meta.json`);
}

// ================================================================
// 主流程
// ================================================================

async function runOfflinePipeline(notesDir = "notes", indexDir = "index") {
  console.log("=".repeat(60));
  console.log("  离线建库 Pipeline");
  console.log("  原始笔记 → 解析清洗 → Chunking → Embedding → 索引入库");
  console.log("=".repeat(60));

  // ── Step 1: 扫描 ──
  const files = await scanNotes(notesDir);
  if (files.length === 0) {
    console.log("[错误] 没有找到 Markdown 文件");
    return;
  }

  const allChunks = [];

  for (const fileName of files) {
    console.log(`\n── 处理: ${fileName} ──`);

    // ── Step 2: 解析 ──
    const rawText = await readFile(join(notesDir, fileName), "utf-8");
    const { meta, body } = parseFrontmatter(rawText);
    console.log(
      `   状态: ${meta.status || "unknown"}  |  ` +
        `标签: [${(meta.tags || []).join(", ")}]  |  ` +
        `更新: ${meta.updated || "?"}`
    );

    // ── Step 3: 清洗 ──
    const cleaned = cleanContent(body);

    // ── Step 4: Chunking ──
    const headings = extractHeadings(cleaned);
    const chunks = chunkByHeadings(cleaned, headings);
    console.log(
      `   标题层级: ${headings.length} 个  |  切出 ${chunks.length} 个 chunk`
    );

    // ── Step 5: 元数据标注 ──
    for (let i = 0; i < chunks.length; i++) {
      const annotated = annotateChunk(chunks[i], fileName, meta, i);
      allChunks.push(annotated);
      console.log(
        `     chunk ${String(i).padStart(2, "0")}: ${annotated.chunk_id}  ` +
          `(${annotated.char_count} 字符)  → ${annotated.section_path.slice(0, 60)}`
      );
    }
  }

  // ── Step 6: 过滤草稿 ──
  const published = allChunks.filter((c) => c.status !== "draft");
  if (published.length < allChunks.length) {
    console.log(
      `\n[过滤] 排除 ${allChunks.length - published.length} 个草稿 chunk，` +
        `保留 ${published.length} 个已发布 chunk`
    );
  }

  // ── Step 7: 加载 Embedding 模型 ──
  console.log(`\n[模型] 加载 Embedding 模型: ${EMBEDDING_MODEL}`);
  const extractor = await pipeline("feature-extraction", EMBEDDING_MODEL);

  // ── Step 8: Embedding ──
  const embeddings = await buildEmbeddings(published, extractor);

  // ── Step 9: BM25 索引 ──
  const bm25Index = buildBM25Index(published);

  // ── Step 10: 保存 ──
  console.log(`\n── 保存索引到 ${indexDir}/ ──`);
  await saveIndex(indexDir, published, embeddings, bm25Index);

  console.log(`\n${"=".repeat(60)}`);
  console.log(`  离线建库完成！`);
  console.log(`  笔记: ${files.length} 篇`);
  console.log(`  Chunk: ${published.length} 个（已发布）`);
  console.log(
    `  总字符: ${published.reduce((s, c) => s + c.char_count, 0).toLocaleString()}`
  );
  console.log(`  索引目录: ${indexDir}/`);
  console.log(`${"=".repeat(60)}`);
}

// 运行
const opts = parseArgs();
runOfflinePipeline(opts.notesDir, opts.indexDir).catch((err) => {
  console.error("Pipeline 失败:", err);
  process.exit(1);
});
