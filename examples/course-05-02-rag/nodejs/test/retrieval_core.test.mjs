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
  const tokens = tokenize("RAG \u68c0\u7d22\u589e\u5f3a\u751f\u6210 tool-use");

  assert.ok(tokens.includes("rag"));
  assert.ok(tokens.includes("tool"));
  assert.ok(tokens.includes("use"));
  assert.ok(tokens.includes("\u68c0"));
  assert.ok(tokens.includes("\u68c0\u7d22"));
  assert.ok(tokens.includes("\u589e\u5f3a"));
});

test("pseudoEmbed returns normalized fixed-size vectors", () => {
  const vector = pseudoEmbed("RAG retrieval-augmented generation");
  const norm = Math.sqrt(vector.reduce((sum, v) => sum + v * v, 0));

  assert.equal(vector.length, PSEUDO_EMBEDDING_DIM);
  assert.ok(Math.abs(norm - 1) < 1e-9);
});

test("pseudo embeddings rank related text above unrelated text", () => {
  const docs = [
    "RAG uses retrieval-augmented generation to place external knowledge into context.",
    "Multi-Agent collaboration usually includes routing, orchestration, and autonomy.",
  ];
  const embeddings = buildPseudoEmbeddings(docs);
  const queryVec = pseudoEmbed("What is RAG retrieval-augmented generation");
  const scores = embeddings.map((emb) => dotProduct(emb, queryVec));

  assert.ok(scores[0] > scores[1]);
});
