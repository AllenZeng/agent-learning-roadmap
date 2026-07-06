import test from "node:test";
import assert from "node:assert/strict";
import {
  PSEUDO_EMBEDDING_DIM,
  buildPseudoEmbeddings,
  dotProduct,
  pseudoEmbed,
  tokenize,
} from "../retrieval_core.mjs";

test("tokenize emits English words and Chinese character bigrams", () => {
  const tokens = tokenize("RAG 检索增强生成 tool-use");

  assert.ok(tokens.includes("rag"));
  assert.ok(tokens.includes("tool"));
  assert.ok(tokens.includes("use"));
  assert.ok(tokens.includes("检"));
  assert.ok(tokens.includes("检索"));
  assert.ok(tokens.includes("增强"));
});

test("pseudoEmbed returns normalized fixed-size vectors", () => {
  const vector = pseudoEmbed("RAG 检索增强生成");
  const norm = Math.sqrt(vector.reduce((sum, v) => sum + v * v, 0));

  assert.equal(vector.length, PSEUDO_EMBEDDING_DIM);
  assert.ok(Math.abs(norm - 1) < 1e-9);
});

test("pseudo embeddings rank related text above unrelated text", () => {
  const docs = [
    "RAG 使用检索增强生成，把外部知识放入上下文。",
    "多 Agent 协作通常包含路由、编排和自治。",
  ];
  const embeddings = buildPseudoEmbeddings(docs);
  const queryVec = pseudoEmbed("什么是 RAG 检索增强生成");
  const scores = embeddings.map((emb) => dotProduct(emb, queryVec));

  assert.ok(scores[0] > scores[1]);
});
