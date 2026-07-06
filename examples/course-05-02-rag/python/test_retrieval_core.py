import json
import math
import unittest
from pathlib import Path

from retrieval_core import (
    PSEUDO_EMBEDDING_DIM,
    build_pseudo_embeddings,
    dot_product,
    pseudo_embed,
    tokenize,
)


class RetrievalCoreTest(unittest.TestCase):
    def test_tokenize_emits_english_words_and_chinese_bigrams(self):
        tokens = tokenize("RAG \u68c0\u7d22\u589e\u5f3a\u751f\u6210 tool-use")

        self.assertIn("rag", tokens)
        self.assertIn("tool", tokens)
        self.assertIn("use", tokens)
        self.assertIn("\u68c0", tokens)
        self.assertIn("\u68c0\u7d22", tokens)
        self.assertIn("\u589e\u5f3a", tokens)

    def test_pseudo_embed_returns_normalized_fixed_size_vector(self):
        vector = pseudo_embed("RAG retrieval-augmented generation")
        norm = math.sqrt(sum(v * v for v in vector))

        self.assertEqual(len(vector), PSEUDO_EMBEDDING_DIM)
        self.assertLess(abs(norm - 1), 1e-9)

    def test_pseudo_embeddings_rank_related_text_above_unrelated_text(self):
        docs = [
            "RAG uses retrieval-augmented generation to place external knowledge into context.",
            "Multi-Agent collaboration usually includes routing, orchestration, and autonomy.",
        ]
        embeddings = build_pseudo_embeddings(docs)
        query_vec = pseudo_embed("What is RAG retrieval-augmented generation")
        scores = [dot_product(emb, query_vec) for emb in embeddings]

        self.assertGreater(scores[0], scores[1])


class NoExternalEmbeddingDependencyTest(unittest.TestCase):
    def test_python_example_does_not_depend_on_external_embedding_packages(self):
        base = Path(__file__).parent
        files = [
            "offline_pipeline.py",
            "online_pipeline.py",
            "retrieval_core.py",
            "requirements.txt",
        ]
        forbidden = [
            "sentence_" + "trans" + "formers",
            "Sentence" + "Transformer",
            "rank_" + "bm25",
            "BM25" + "Okapi",
            "num" + "py",
            "to" + "rch",
            "trans" + "formers",
            "fa" + "iss",
        ]

        for file_name in files:
            text = (base / file_name).read_text(encoding="utf-8")
            for token in forbidden:
                with self.subTest(file=file_name, token=token):
                    self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main()
