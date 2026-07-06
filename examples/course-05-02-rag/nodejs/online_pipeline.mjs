/**
 * Online query pipeline: user question -> note-based answer
 *
 * Corresponds to course-05-02 sections 2.4.5-2.4.7:
 *   2.4.5 Query understanding and rewriting   - reference resolution and intent completion
 *   2.4.6 Retrieval and reranking     - multi-route retrieval + RRF fusion + rerank + truncation
 *   2.4.7 Context assembly and generation - chunk ordering, source labels, and citation alignment
 *
 * Usage:
 *   node online_pipeline.mjs "the difference between Tool Use and Memory"
 *   node online_pipeline.mjs --interactive
 *   node online_pipeline.mjs --top-k 5 "what Chunking is"
 */

import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { createInterface } from "node:readline";
import {
  DEFAULT_RETRIEVER,
  SimpleBM25,
  dotProduct,
  pseudoEmbed,
  tokenize,
} from "./retrieval_core.mjs";

// ---------- Configuration ----------

const DEFAULT_TOP_K = 5;
const VECTOR_WEIGHT = 0.6;
const BM25_WEIGHT = 0.4;
const MAX_CONTEXT_CHARS = 3000;

// ---------- Helper functions ----------

function argsortDesc(arr) {
  return arr
    .map((v, i) => ({ v, i }))
    .sort((a, b) => b.v - a.v)
    .map((x) => x.i);
}

function parseArgs() {
  const args = process.argv.slice(2);
  const opts = { indexDir: "output", topK: DEFAULT_TOP_K, interactive: false, debug: false, query: null };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--index-dir" && args[i + 1]) opts.indexDir = args[++i];
    else if (args[i] === "--top-k" && args[i + 1]) opts.topK = parseInt(args[++i], 10);
    else if (args[i] === "--interactive" || args[i] === "-i") opts.interactive = true;
    else if (args[i] === "--debug") opts.debug = true;
    else opts.query = args[i];
  }
  return opts;
}

// ================================================================
// Stage 1: load index
// ================================================================

async function loadIndex(indexDir) {
  // Chunks
  const chunksRaw = await readFile(join(indexDir, "chunks.json"), "utf-8");
  const chunks = JSON.parse(chunksRaw);
  console.log(`[加载] chunks.json — ${chunks.length} 个 chunk`);

  // Embeddings
  const embRaw = await readFile(join(indexDir, "embeddings.json"), "utf-8");
  const embeddings = JSON.parse(embRaw);
  console.log(`[加载] embeddings.json — ${embeddings.length} × ${embeddings[0]?.length || 0}`);

  // BM25
  const bm25Raw = await readFile(join(indexDir, "bm25_index.json"), "utf-8");
  const bm25Data = JSON.parse(bm25Raw);
  console.log(`[加载] bm25_index.json — ${Object.keys(bm25Data.idf).length} 个词条`);

  const metaRaw = await readFile(join(indexDir, "index_meta.json"), "utf-8");
  const meta = JSON.parse(metaRaw);

  // Rebuild the BM25 instance
  const bm25 = SimpleBM25.fromJSON(bm25Data);
  console.log(`[加载] 伪 embedding: hashing TF-IDF (${meta.pseudo_embedding_dim || embeddings[0]?.length || 0} 维)`);
  const vectorizer = {
    type: DEFAULT_RETRIEVER,
    embed: async (text) => pseudoEmbed(text, meta.pseudo_embedding_idf || {}),
  };

  return { chunks, embeddings, bm25, vectorizer };
}

// ================================================================
// Stage 2: query understanding and rewriting (section 2.4.5)
// ================================================================

function understandQuery(query) {
  const pronouns = ["它", "他", "她", "这个", "那个", "这些", "那些"];
  const hasPronoun = pronouns.some((p) => query.includes(p));

  const expansions = {
    "tool use": ["工具调用", "工具使用", "function calling"],
    memory: ["记忆", "状态管理", "上下文"],
    rag: ["检索增强生成", "外部知识", "知识库"],
    chunking: ["分块", "切分", "文档分割"],
  };

  const expandedTerms = [];
  for (const [key, terms] of Object.entries(expansions)) {
    if (query.toLowerCase().includes(key)) {
      expandedTerms.push(...terms);
    }
  }

  return {
    original: query,
    hasPronoun,
    expandedTerms,
    expandedQuery:
      expandedTerms.length > 0 ? `${query} ${expandedTerms.join(" ")}` : query,
  };
}

// ================================================================
// Stage 3: retrieval (section 2.4.6)
// ================================================================

async function denseRetrieve(query, vectorizer, embeddings, chunks, topK = 20) {
  const queryVec = await vectorizer.embed(query);
  const scores = embeddings.map((emb) => dotProduct(emb, queryVec));
  const indices = argsortDesc(scores).slice(0, topK);

  return indices.map((idx) => ({
    chunk_idx: idx,
    score: scores[idx],
    source: "dense",
    chunk: chunks[idx],
  }));
}

function sparseRetrieve(query, bm25, chunks, topK = 20) {
  const queryTokens = tokenize(query);
  const scores = bm25.getScores(queryTokens);
  const maxScore = Math.max(...scores, 1);
  const normalized = scores.map((s) => s / maxScore);
  const indices = argsortDesc(normalized).slice(0, topK);

  return indices
    .filter((idx) => normalized[idx] > 0)
    .map((idx) => ({
      chunk_idx: idx,
      score: normalized[idx],
      source: "sparse",
      chunk: chunks[idx],
    }));
}

function metadataFilter(results) {
  return results.filter((r) => r.chunk.status !== "draft");
}

function rrfFusion(denseResults, sparseResults, k = 60) {
  const scores = {}; // chunk_idx → fused_score

  denseResults.forEach((r, rank) => {
    scores[r.chunk_idx] =
      (scores[r.chunk_idx] || 0) + VECTOR_WEIGHT / (k + rank + 1);
  });

  sparseResults.forEach((r, rank) => {
    scores[r.chunk_idx] =
      (scores[r.chunk_idx] || 0) + BM25_WEIGHT / (k + rank + 1);
  });

  const sorted = Object.entries(scores).sort((a, b) => b[1] - a[1]);

  const chunkMap = {};
  for (const r of [...denseResults, ...sparseResults]) {
    if (!chunkMap[r.chunk_idx]) chunkMap[r.chunk_idx] = r;
  }

  return sorted.map(([idx, score]) => ({
    ...chunkMap[parseInt(idx)],
    fused_score: score,
  }));
}

// ================================================================
// Stage 4: reranking (section 2.4.6)
// ================================================================

async function rerank(query, candidates, vectorizer, topK = DEFAULT_TOP_K) {
  if (candidates.length <= topK) return candidates;

  // Recompute with finer-grained similarity
  const queryVec = await vectorizer.embed(query);

  for (const c of candidates) {
    const chunkVec = await vectorizer.embed(c.chunk.content);
    const simScore = dotProduct(queryVec, chunkVec);
    c.rerank_score = 0.7 * simScore + 0.3 * c.fused_score;
  }

  const ranked = candidates.sort((a, b) => b.rerank_score - a.rerank_score);

  // Score-cliff detection
  let cutAt = topK;
  for (let i = topK; i < ranked.length; i++) {
    if (
      ranked[i - 1].rerank_score > 0 &&
      ranked[i].rerank_score / ranked[i - 1].rerank_score < 0.7
    ) {
      cutAt = i;
      break;
    }
  }

  return ranked.slice(0, cutAt);
}

// ================================================================
// Stage 5: context assembly (section 2.4.7)
// ================================================================

function assembleContext(query, rankedChunks, maxChars = MAX_CONTEXT_CHARS) {
  const parts = [];
  let totalChars = 0;

  for (let i = 0; i < rankedChunks.length; i++) {
    const r = rankedChunks[i];
    const c = r.chunk;
    const score = (r.rerank_score || r.fused_score).toFixed(3);
    const header =
      `[来源 ${i + 1}] ${c.source} — ${c.section_path}\n` +
      `更新于 ${c.updated_at || "?"}  |  ` +
      `标签: ${(c.tags || []).join(", ")}  |  ` +
      `分数: ${score}`;

    totalChars += header.length + c.content.length + 6;

    if (totalChars > maxChars && i > 0) {
      console.log(
        `  [截断] 达到 token 预算上限，取了 ${i} / ${rankedChunks.length} 个 chunk`
      );
      break;
    }

    parts.push(`${header}\n\n${c.content}`);
  }

  return parts.join("\n\n---\n\n");
}

// ================================================================
// Stage 6: generation (simulated)
// ================================================================

function generateAnswer(query, context, rankedChunks) {
  const sourcesSummary = rankedChunks
    .map(
      (r, i) =>
        `  [${i + 1}] ${r.chunk.source} → ${r.chunk.section_path} ` +
        `(分数: ${(r.rerank_score || r.fused_score).toFixed(3)})`
    )
    .join("\n");

  const prompt = `你是一个个人知识助手。请基于以下笔记内容回答用户问题。

## 用户问题
${query}

## 相关笔记
${context}

## 回答要求
- 基于上述笔记内容回答，不要编造
- 引用具体来源（如 [来源 1]）
- 如果笔记中没有直接答案，明确说明
- 如果笔记内容存在矛盾，指出并说明
`;

  console.log("\n" + "=".repeat(60));
  console.log("  📤 最终 Prompt（将发送给 LLM）");
  console.log("=".repeat(60));
  console.log(`\n${prompt}\n`);
  console.log(`[提示] 以上 Prompt 共约 ${prompt.length} 字符`);
  console.log(
    `[提示] 替换 generateAnswer() 中的逻辑接入 LLM API 即可获得最终回答\n`
  );

  return prompt;
}

// ================================================================
// Main flow
// ================================================================

async function runOnlinePipeline(query, indexDir = "index", topK = DEFAULT_TOP_K, debug = false) {
  console.log("=".repeat(60));
  console.log(`  在线查询 Pipeline`);
  console.log(`  查询: "${query}"`);
  console.log("=".repeat(60));

  // ── Step 1: Load index ──
  console.log();
  const { chunks, embeddings, bm25, vectorizer } = await loadIndex(indexDir);

  // ── Step 2: Query understanding ──
  console.log(`\n── 查询理解 (§2.4.5) ──`);
  const queryInfo = understandQuery(query);
  console.log(`  原始查询: ${queryInfo.original}`);
  if (queryInfo.hasPronoun) {
    console.log(`  ⚠️ 检测到指代词，可能需要上下文补全`);
  }
  if (queryInfo.expandedTerms.length > 0) {
    console.log(`  扩展词: [${queryInfo.expandedTerms.join(", ")}]`);
  }
  const searchQuery = queryInfo.expandedQuery;

  // ── Step 3: Multi-route retrieval ──
  console.log(`\n── 多路召回 (§2.4.6) ──`);
  process.stdout.write(`  向量召回 top-20 ... `);
  const denseResults = await denseRetrieve(searchQuery, vectorizer, embeddings, chunks, 20);
  console.log(`命中 ${denseResults.length}`);

  process.stdout.write(`  BM25 召回 top-20 ... `);
  const sparseResults = sparseRetrieve(searchQuery, bm25, chunks, 20);
  console.log(`命中 ${sparseResults.length}`);

  // Metadata filtering + RRF fusion
  const filteredDense = metadataFilter(denseResults);
  const filteredSparse = metadataFilter(sparseResults);
  const fused = rrfFusion(filteredDense, filteredSparse);
  console.log(`  RRF 融合 → ${fused.length} 个候选（去重后）`);

  if (debug) {
    console.log(`\n  候选集详情:`);
    for (let i = 0; i < Math.min(fused.length, 15); i++) {
      const r = fused[i];
      console.log(
        `    #${i + 1} [${r.source}] ${r.chunk.section_path.slice(0, 50)} — ` +
          `融合分: ${r.fused_score.toFixed(4)}`
      );
    }
  }

  // ── Step 4: Reranking ──
  console.log(`\n── 重排序 (§2.4.6) ──`);
  const ranked = await rerank(searchQuery, fused, vectorizer, topK);
  console.log(`  Rerank → top-${ranked.length}`);

  console.log(`\n  最终选中的 chunk:`);
  for (let i = 0; i < ranked.length; i++) {
    const r = ranked[i];
    const c = r.chunk;
    console.log(
      `    #${i + 1} [${c.source}] ${c.section_path}`
    );
    console.log(
      `        分数: ${r.rerank_score.toFixed(3)}  |  ` +
        `${c.char_count} 字符  |  标签: [${(c.tags || []).join(", ")}]`
    );
  }

  if (ranked.length >= 2 && fused.length > ranked.length) {
    console.log(
      `    🔻 分数断崖：第 ${ranked.length} 名之后的内容对回答帮助显著下降`
    );
  }

  // ── Step 5: Context assembly ──
  console.log(`\n── 上下文组装 (§2.4.7) ──`);
  const context = assembleContext(query, ranked);
  console.log(`  组装完成，共 ${context.length} 字符`);

  // ── Step 6: Generate answer ──
  generateAnswer(query, context, ranked);

  return { ranked, context };
}

// ================================================================
// Interactive mode
// ================================================================

async function interactiveMode(indexDir, topK, debug) {
  console.log("=".repeat(60));
  console.log("  个人知识助手 — 交互查询");
  console.log("  输入问题进行检索，输入 /quit 退出，/debug 切换详情");
  console.log("=".repeat(60));

  const { chunks, embeddings, bm25, vectorizer } = await loadIndex(indexDir);

  const rl = createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  const ask = () =>
    new Promise((resolve) => rl.question("\n🔍 你的问题: ", resolve));

  while (true) {
    let query = await ask();
    query = query.trim();

    if (!query) continue;
    if (query === "/quit") break;
    if (query === "/debug") {
      debug = !debug;
      console.log(`  debug = ${debug}`);
      continue;
    }

    // Run one query inline
    console.log("=".repeat(60));
    console.log(`  查询: "${query}"`);
    console.log("=".repeat(60));

    const queryInfo = understandQuery(query);
    const searchQuery = queryInfo.expandedQuery;

    if (queryInfo.expandedTerms.length > 0) {
      console.log(`  扩展词: [${queryInfo.expandedTerms.join(", ")}]`);
    }

    console.log(`  向量召回 top-20 ...`);
    const denseResults = await denseRetrieve(searchQuery, vectorizer, embeddings, chunks, 20);
    console.log(`  命中 ${denseResults.length}`);

    const sparseResults = sparseRetrieve(searchQuery, bm25, chunks, 20);
    console.log(`  BM25 命中 ${sparseResults.length}`);

    const fused = rrfFusion(
      metadataFilter(denseResults),
      metadataFilter(sparseResults)
    );
    console.log(`  RRF 融合 → ${fused.length} 个候选`);

    const ranked = await rerank(searchQuery, fused, vectorizer, topK);
    console.log(`  Rerank → top-${ranked.length}`);

    console.log(`\n  最终选中的 chunk:`);
    for (let i = 0; i < ranked.length; i++) {
      console.log(
        `    #${i + 1} [${ranked[i].chunk.source}] ${ranked[i].chunk.section_path.slice(0, 60)}`
      );
    }

    const context = assembleContext(query, ranked);
    generateAnswer(query, context, ranked);
  }

  rl.close();
}

// ================================================================
// Entry point
// ================================================================

const opts = parseArgs();

(async () => {
  if (opts.interactive || !opts.query) {
    await interactiveMode(opts.indexDir, opts.topK, opts.debug);
  } else {
    await runOnlinePipeline(opts.query, opts.indexDir, opts.topK, opts.debug);
  }
})().catch((err) => {
  console.error("Pipeline 失败:", err);
  process.exit(1);
});
