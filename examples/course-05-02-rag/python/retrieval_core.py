import math
import re
from collections import Counter
from typing import Optional

PSEUDO_EMBEDDING_DIM = 384
DEFAULT_RETRIEVER = "pseudo"

TOKEN_RE = re.compile(r"[\u4e00-\u9fff]|[a-z0-9]+", re.IGNORECASE)
HAN_RE = re.compile(r"^[\u4e00-\u9fff]$")


def tokenize(text: str) -> list[str]:
    raw = TOKEN_RE.findall(str(text).lower())
    tokens: list[str] = []

    for i, token in enumerate(raw):
        tokens.append(token)
        next_token = raw[i + 1] if i + 1 < len(raw) else ""
        if HAN_RE.match(token) and HAN_RE.match(next_token):
            tokens.append(token + next_token)

    return tokens


def _hash_token(token: str) -> int:
    h = 2166136261
    for ch in token:
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF
    return h


def dot_product(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def _normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(v * v for v in vector))
    if norm == 0:
        return vector
    return [v / norm for v in vector]


def pseudo_embed(
    text: str,
    idf: Optional[dict[str, float]] = None,
    dim: int = PSEUDO_EMBEDDING_DIM,
) -> list[float]:
    idf = idf or {}
    vector = [0.0] * dim
    tf = Counter(tokenize(text))

    for token, count in tf.items():
        bucket = _hash_token(token) % dim
        sign = 1 if _hash_token(f"{token}#sign") % 2 == 0 else -1
        weight = (1 + math.log(count)) * idf.get(token, 1.0)
        vector[bucket] += sign * weight

    return _normalize(vector)


def build_idf(docs: list[str]) -> dict[str, float]:
    df: Counter[str] = Counter()
    for doc in docs:
        df.update(set(tokenize(doc)))

    doc_count = len(docs) or 1
    return {
        token: math.log((doc_count + 1) / (count + 1)) + 1
        for token, count in df.items()
    }


def build_pseudo_embeddings(
    docs: list[str],
    idf: Optional[dict[str, float]] = None,
) -> list[list[float]]:
    idf = idf or build_idf(docs)
    return [pseudo_embed(doc, idf) for doc in docs]


class SimpleBM25:
    def __init__(self, docs: list[str], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.docs = [tokenize(doc) for doc in docs]
        self.doc_count = len(docs)
        self.avgdl = (
            sum(len(doc) for doc in self.docs) / self.doc_count
            if self.doc_count
            else 0
        )

        df: Counter[str] = Counter()
        for doc in self.docs:
            df.update(set(doc))

        self.idf = {
            term: math.log((self.doc_count - count + 0.5) / (count + 0.5) + 1)
            for term, count in df.items()
        }

    def get_scores(self, query_tokens: list[str]) -> list[float]:
        scores = []
        for doc in self.docs:
            if not doc or self.avgdl == 0:
                scores.append(0.0)
                continue

            score = 0.0
            tf = Counter(doc)
            for term in query_tokens:
                if term not in self.idf or term not in tf:
                    continue
                numerator = tf[term] * (self.k1 + 1)
                denominator = tf[term] + self.k1 * (
                    1 - self.b + (self.b * len(doc)) / self.avgdl
                )
                score += self.idf[term] * (numerator / denominator)
            scores.append(score)
        return scores

    def to_dict(self) -> dict:
        return {
            "k1": self.k1,
            "b": self.b,
            "doc_count": self.doc_count,
            "avgdl": self.avgdl,
            "idf": self.idf,
            "docs": self.docs,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SimpleBM25":
        bm25 = cls.__new__(cls)
        bm25.k1 = data["k1"]
        bm25.b = data["b"]
        bm25.doc_count = data["doc_count"]
        bm25.avgdl = data["avgdl"]
        bm25.idf = data["idf"]
        bm25.docs = data["docs"]
        return bm25
