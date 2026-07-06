export const PSEUDO_EMBEDDING_DIM = 384;
export const DEFAULT_RETRIEVER = "pseudo";

const TOKEN_RE = /[\p{Script=Han}]|[a-z0-9]+/giu;

export function tokenize(text) {
  const raw = String(text).toLowerCase().match(TOKEN_RE) || [];
  const tokens = [];

  for (let i = 0; i < raw.length; i++) {
    tokens.push(raw[i]);
    if (/^[\p{Script=Han}]$/u.test(raw[i]) && /^[\p{Script=Han}]$/u.test(raw[i + 1] || "")) {
      tokens.push(raw[i] + raw[i + 1]);
    }
  }

  return tokens;
}

function hashToken(token) {
  let h = 2166136261;
  for (let i = 0; i < token.length; i++) {
    h ^= token.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

export function dotProduct(a, b) {
  let s = 0;
  for (let i = 0; i < a.length; i++) s += a[i] * b[i];
  return s;
}

function normalize(vector) {
  const norm = Math.sqrt(vector.reduce((sum, v) => sum + v * v, 0));
  if (norm === 0) return vector;
  return vector.map((v) => v / norm);
}

export function pseudoEmbed(text, idf = {}, dim = PSEUDO_EMBEDDING_DIM) {
  const vector = Array(dim).fill(0);
  const tf = {};

  for (const token of tokenize(text)) {
    tf[token] = (tf[token] || 0) + 1;
  }

  for (const [token, count] of Object.entries(tf)) {
    const h = hashToken(token);
    const bucket = h % dim;
    const sign = hashToken(`${token}#sign`) % 2 === 0 ? 1 : -1;
    const weight = (1 + Math.log(count)) * (idf[token] || 1);
    vector[bucket] += sign * weight;
  }

  return normalize(vector);
}

export function buildIdf(docs) {
  const df = {};
  for (const doc of docs) {
    for (const token of new Set(tokenize(doc))) {
      df[token] = (df[token] || 0) + 1;
    }
  }

  const docCount = docs.length || 1;
  const idf = {};
  for (const [token, count] of Object.entries(df)) {
    idf[token] = Math.log((docCount + 1) / (count + 1)) + 1;
  }
  return idf;
}

export function buildPseudoEmbeddings(docs, idf = buildIdf(docs)) {
  return docs.map((doc) => pseudoEmbed(doc, idf));
}

export class SimpleBM25 {
  constructor(docs, k1 = 1.5, b = 0.75) {
    this.k1 = k1;
    this.b = b;
    this.docs = docs.map((d) => tokenize(d));
    this.docCount = docs.length;
    this.avgdl =
      this.docCount === 0
        ? 0
        : this.docs.reduce((s, d) => s + d.length, 0) / this.docCount;

    const df = {};
    for (const doc of this.docs) {
      for (const term of new Set(doc)) {
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
    return this.docs.map((doc) => {
      if (doc.length === 0 || this.avgdl === 0) return 0;

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
      docs: this.docs,
    };
  }

  static fromJSON(data) {
    const bm25 = Object.create(SimpleBM25.prototype);
    Object.assign(bm25, data);
    return bm25;
  }
}
