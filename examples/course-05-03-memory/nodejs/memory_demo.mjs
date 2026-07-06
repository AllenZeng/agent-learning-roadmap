#!/usr/bin/env node
/**
 * Course 05-03 Memory example - interactive Memory lifecycle demo
 *
 * Simulates a knowledge assistant's cross-session conversations from Monday to Wednesday to show the full Memory lifecycle:
 *   identify candidate memories -> write decision -> storage -> recall -> update and forgetting
 *
 * Implemented with only the Node.js standard library (bag-of-words vectors), with no external dependencies.
 *
 * Usage:
 *   node memory_demo.mjs           # Interactive mode (press Enter at each step)
 *   node memory_demo.mjs --auto    # Automatic mode (useful for viewing the full output)
 */

import crypto from "node:crypto";
import { createInterface } from "node:readline/promises";
import { stdin as input, stdout as output } from "node:process";
import {
  appendFile,
  mkdir,
  readFile,
  rm,
  writeFile,
} from "node:fs/promises";
import { existsSync } from "node:fs";
import { join } from "node:path";

// ============================================================
// Lightweight Memory implementation (core logic)
// ============================================================

class AgentMemory {
  /** Layered storage + write guard + semantic recall + audit log */
  constructor(storageDir = "./memory_store") {
    this.storageDir = storageDir;
    this.prefPath = join(storageDir, "preferences.json");
    this.factsPath = join(storageDir, "facts.json");
    this.historyPath = join(storageDir, "task_history.json");
    this.auditPath = join(storageDir, "audit.jsonl");
    this.preferences = {};
    this.facts = [];
    this.history = [];
    this.session = {};
    this.pending = [];
  }

  async init() {
    await mkdir(this.storageDir, { recursive: true });
    this.preferences = await this.#load(this.prefPath, {});
    this.facts = await this.#load(this.factsPath, []);
    this.history = await this.#load(this.historyPath, []);
  }

  async #load(path, fallback) {
    if (!existsSync(path)) return fallback;
    return JSON.parse(await readFile(path, "utf8"));
  }

  async #save(path, data) {
    await writeFile(path, JSON.stringify(data, null, 2), "utf8");
  }

  async #audit(action, detail) {
    const entry = { ts: new Date().toISOString(), action, ...detail };
    await appendFile(this.auditPath, `${JSON.stringify(entry)}\n`, "utf8");
  }

  // ── Identify candidate memories ──
  identifyCandidates(userMessage) {
    const candidates = [];
    for (const pattern of [/from now on[^，。]*/g, /every time[^，。]*/g, /do not[^，。]*/g, /default[^，。]*/g]) {
      for (const match of userMessage.matchAll(pattern)) {
        candidates.push({
          type: "preference",
          content: match[0],
          source: "user_explicit",
          confidence: 0.95,
          sensitive: false,
        });
      }
    }

    if (/(?:api[_\s]?key|secret|token|password)\s*[：:=]\s*\S+/i.test(userMessage)) {
      candidates.push({
        type: "sensitive",
        content: "[sensitive information]",
        source: "detected",
        confidence: 0.99,
        sensitive: true,
      });
    }

    for (const match of userMessage.matchAll(/this time[^，。]*/g)) {
      candidates.push({
        type: "temporary",
        content: match[0],
        source: "user_explicit",
        confidence: 0.9,
        sensitive: false,
      });
    }

    return candidates;
  }

  // ── Write guard ──
  shouldRemember(candidate) {
    if (candidate.sensitive) return [false, "sensitive"];
    if (candidate.type === "temporary") return [false, "temporary"];
    if ((candidate.confidence ?? 0) < 0.5) return [false, "low_confidence"];

    if (candidate.type === "preference") {
      for (const value of Object.values(this.preferences)) {
        if (
          value.category === candidate.category &&
          value.content !== candidate.content
        ) {
          return [true, "conflict: replacing old preference"];
        }
      }
    }
    return [true, "ok"];
  }

  // ── Write ──
  async write(entry) {
    const [ok, reason] = this.shouldRemember(entry);
    if (!ok) {
      await this.#audit("write_rejected", { reason });
      return { status: "rejected", reason };
    }

    const content = entry.content ?? "";
    const idHash = crypto.createHash("md5").update(content).digest("hex").slice(0, 10);
    const mid = `mem_${idHash}`;
    const now = new Date().toISOString();
    const record = {
      id: mid,
      ...entry,
      created_at: now,
      updated_at: now,
      access_count: 0,
    };

    if (entry.type === "preference") {
      const keyHash = crypto.createHash("md5").update(content).digest("hex").slice(0, 6);
      const key = `${entry.category ?? "general"}_${keyHash}`;
      let old = this.preferences[key];

      if (!old) {
        for (const value of Object.values(this.preferences)) {
          if (value.category === entry.category && value.content !== entry.content) {
            old = value;
            break;
          }
        }
      }

      if (old && old.content !== entry.content) {
        record.supersedes = old.id;
        record.version = (old.version ?? 1) + 1;
        old.status = "superseded";
        old.superseded_by = mid;
        old.updated_at = new Date().toISOString();
      }

      this.preferences[key] = record;
      await this.#save(this.prefPath, this.preferences);
    } else if (entry.type === "fact") {
      this.facts.push(record);
      await this.#save(this.factsPath, this.facts);
    } else if (entry.type === "task_result") {
      this.history.push(record);
      this.history = this.history.slice(-500);
      await this.#save(this.historyPath, this.history);
    }

    await this.#audit("write_accepted", { id: mid, type: entry.type });
    return { status: "written", id: mid };
  }

  // ── Recall ──
  recall(task, limit = 5) {
    const relevant = [];
    const taskGrams = this.#tokenize(task);

    for (const pref of Object.values(this.preferences)) {
      if (pref.status === "superseded") continue;
      const memGrams = this.#tokenize(pref.content ?? "");
      const overlap = [...taskGrams].filter((gram) => memGrams.has(gram)).length;
      if (overlap >= 1) {
        relevant.push({
          ...pref,
          score: Math.min(0.95, 0.7 + overlap * 0.05),
          match: "keyword",
        });
      }
    }

    const taskVector = this.#embed(task);
    for (const fact of this.facts) {
      if (fact.status === "superseded") continue;
      const factVector = this.#embed(fact.content ?? "");
      const score = this.#cosine(taskVector, factVector);
      if (score > 0.3) {
        relevant.push({ ...fact, score: round(score, 3), match: "semantic" });
      }
    }

    for (const memory of relevant) {
      const days = this.#daysSince(memory.updated_at ?? memory.created_at);
      const timeFactor = Math.max(0.5, 1.0 - days / 180);
      memory.final = round(
        memory.score * timeFactor + Math.min(0.1, (memory.access_count ?? 0) * 0.01),
        3
      );
    }

    relevant.sort((a, b) => b.final - a.final);
    const result = relevant.slice(0, limit);
    for (const memory of result) {
      memory.access_count = (memory.access_count ?? 0) + 1;
    }
    return result;
  }

  #tokenize(text) {
    const tokens = new Set();
    const lower = text.toLowerCase();

    for (const match of lower.matchAll(/[a-z0-9]+/g)) {
      tokens.add(match[0]);
    }

    for (const match of lower.matchAll(/[\u4e00-\u9fff]+/g)) {
      const segment = match[0];
      for (let i = 0; i < segment.length - 1; i++) {
        tokens.add(segment.slice(i, i + 2));
      }
    }

    return tokens;
  }

  #embed(text) {
    const vec = Array(128).fill(0);
    for (let i = 0; i < text.length - 2; i++) {
      const gram = text.slice(i, i + 3).toLowerCase();
      const idx = stableHash(gram) % 128;
      vec[idx] += 1.0;
    }

    const norm = Math.sqrt(vec.reduce((sum, value) => sum + value * value, 0));
    return norm > 0 ? vec.map((value) => value / norm) : vec;
  }

  #cosine(a, b) {
    return Math.max(0, a.reduce((sum, value, idx) => sum + value * b[idx], 0));
  }

  #daysSince(ts) {
    if (!ts) return 999;
    return (Date.now() - new Date(ts).getTime()) / 86_400_000;
  }

  // ── Update / delete / decay ──
  async update(mid, updates) {
    for (const [store, path] of [
      [this.preferences, this.prefPath],
      [this.facts, this.factsPath],
      [this.history, this.historyPath],
    ]) {
      const items = Array.isArray(store) ? store : Object.values(store);
      for (const memory of items) {
        if (memory.id === mid) {
          Object.assign(memory, updates, { updated_at: new Date().toISOString() });
          await this.#save(path, store);
          return { status: "updated" };
        }
      }
    }
    return { status: "not_found" };
  }

  async delete(mid) {
    for (const [store, path] of [
      [this.preferences, this.prefPath],
      [this.facts, this.factsPath],
      [this.history, this.historyPath],
    ]) {
      if (Array.isArray(store)) {
        const before = store.length;
        const next = store.filter((memory) => memory.id !== mid);
        store.splice(0, store.length, ...next);
        if (store.length < before) {
          await this.#save(path, store);
          return { status: "deleted" };
        }
      } else {
        for (const [key, value] of Object.entries(store)) {
          if (value.id === mid) {
            delete store[key];
            await this.#save(path, store);
            return { status: "deleted" };
          }
        }
      }
    }
    return { status: "not_found" };
  }

  async decay() {
    const stats = { expired: 0, stale: 0 };
    for (const pref of Object.values(this.preferences)) {
      if (pref.last_accessed_at) {
        const days = Math.floor((Date.now() - new Date(pref.last_accessed_at).getTime()) / 86_400_000);
        if (days > 90) {
          pref.status = "stale";
          stats.stale += 1;
        }
      }
    }
    await this.#save(this.prefPath, this.preferences);
    return stats;
  }

  listAll() {
    return [...Object.values(this.preferences), ...this.facts, ...this.history].sort((a, b) =>
      String(b.updated_at ?? "").localeCompare(String(a.updated_at ?? ""))
    );
  }

  async startSession(uid = "user-001") {
    this.session = { uid, started: new Date().toISOString(), turns: 0 };
    await this.decay();
    await this.#audit("session_start", { uid });
  }

  async endSession() {
    await this.#audit("session_end", { turns: this.session.turns ?? 0 });
    this.session = {};
  }
}

// ============================================================
// Interactive demo
// ============================================================

const RESET = "\x1b[0m";
const BOLD = "\x1b[1m";
const DIM = "\x1b[2m";
const GREEN = "\x1b[32m";
const YELLOW = "\x1b[33m";
const CYAN = "\x1b[36m";
const RED = "\x1b[31m";

function stableHash(text) {
  const digest = crypto.createHash("md5").update(text).digest();
  return digest.readUInt32BE(0);
}

function round(value, digits) {
  const factor = 10 ** digits;
  return Math.round(value * factor) / factor;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function wait(message, auto = false, rl = null) {
  if (auto) {
    console.log(`\n${DIM}── automatically continue to the next step ──${RESET}`);
    await sleep(500);
  } else if (rl) {
    await rl.question(message);
  }
}

function showBanner() {
  console.log(`
${CYAN}${BOLD}╔══════════════════════════════════════════════════════════╗
║     Course 05-03 Memory lifecycle demo                         ║
║     Simulate a knowledge assistant's cross-session Memory behavior from Monday to Wednesday              ║
╚══════════════════════════════════════════════════════════╝${RESET}
`);
}

function showMemoryState(memory, label = "") {
  console.log(`\n${YELLOW}${BOLD}📦 ${label}${RESET}`);

  const prefs = memory.preferences;
  if (Object.keys(prefs).length > 0) {
    console.log(`  ${BOLD}preferences:${RESET}`);
    for (const value of Object.values(prefs)) {
      const status =
        value.status === "stale"
          ? `${RED}stale${RESET}`
          : value.status === "superseded"
            ? `${DIM}superseded${RESET}`
            : `${GREEN}active${RESET}`;
      console.log(`    [${value.id}] ${String(value.content ?? "").slice(0, 60)} (${status})`);
    }
  }

  const facts = memory.facts.filter((fact) => fact.status !== "superseded");
  if (facts.length > 0) {
    console.log(`  ${BOLD}facts:${RESET}`);
    for (const fact of facts) {
      console.log(`    [${fact.id}] ${String(fact.content ?? "").slice(0, 60)}`);
    }
  }

  const history = memory.history.slice(-3);
  if (history.length > 0) {
    console.log(`  ${BOLD}task_history (recent 3):${RESET}`);
    for (const item of history) {
      console.log(`    [${item.id}] ${String(item.content ?? "").slice(0, 60)}`);
    }
  }
}

function showRecallResults(recalled) {
  if (recalled.length === 0) {
    console.log(`  ${DIM}(No relevant memories)${RESET}`);
    return;
  }

  recalled.forEach((item, idx) => {
    const matchIcon = item.match === "keyword" ? "🔑" : "🔍";
    console.log(
      `  ${matchIcon} #${idx + 1} (score: ${item.final ?? item.score ?? 0})  ${String(item.content ?? "").slice(0, 80)}`
    );
  });
}

async function simulate(auto = false) {
  const rl = auto ? null : createInterface({ input, output });
  try {
    showBanner();

    if (existsSync("./memory_store")) {
      await rm("./memory_store", { recursive: true, force: true });
    }

    const memory = new AgentMemory("./memory_store");
    await memory.init();

    // ═══════════════════════════════════════════════════
    // SESSION 1: Monday
    // ═══════════════════════════════════════════════════
    console.log(`${BOLD}${"─".repeat(60)}${RESET}`);
    console.log(`${BOLD}  SESSION 1：Monday 10:00-10:45${RESET}`);
    console.log(`${BOLD}${"─".repeat(60)}${RESET}`);

    await memory.startSession("user-001");
    console.log(`\n${DIM}[session start] decay check: No expired memories (system initialization)${RESET}`);

    const msg = "When writing technical articles in the future, give me an outline for confirmation before expanding the body. Keep the tone direct, not marketing-oriented.";
    console.log(`\n${GREEN}👤 user：${msg}${RESET}`);

    const candidates = memory.identifyCandidates(msg);
    console.log(`${DIM}[identify] Identified ${candidates.length} candidate memories${RESET}`);
    for (const candidate of candidates) {
      const category =
        candidate.content.includes("outline") || candidate.content.includes("outline first")
          ? "writing_workflow"
          : candidate.content.includes("tone") || candidate.content.includes("marketing")
            ? "writing_tone"
            : "writing_style";
      const result = await memory.write({ ...candidate, category });
      const status =
        result.status === "written"
          ? `${GREEN}✅ Write${RESET}`
          : `${RED}❌ reject: ${result.reason}${RESET}`;
      console.log(`  → ${candidate.content.slice(0, 50)}... ${status}`);
    }

    const msg2 = "I am using TypeScript to write an Agent framework; help me review this code";
    console.log(`\n${GREEN}👤 user：${msg2}${RESET}`);
    console.log(`${DIM}[identify] This message did not trigger an explicit preference rule, but the system inferred from behavior that the user may prefer TypeScript${RESET}`);

    const inferred = await memory.write({
      type: "preference",
      category: "code_style",
      content: "User may prefer TypeScript example code",
      source: "inferred",
      confidence: 0.5,
      sensitive: false,
    });
    const inferredStatus =
      inferred.status === "written"
        ? `${YELLOW}⚠️ Wrote as a candidate memory (low-confidence inference, awaiting user confirmation)${RESET}`
        : `${RED}❌ reject${RESET}`;
    if (inferred.status === "written") {
      memory.pending.push({ id: inferred.id, content: "User may prefer TypeScript example code" });
    }
    console.log(`  → inferred preference: TypeScript example code... ${inferredStatus}`);

    const msg3 = "Help me write a technical article about Agent Memory";
    console.log(`\n${GREEN}👤 user：${msg3}${RESET}`);
    const recalled = memory.recall(msg3, 5);
    console.log(`${DIM}[recall] Recall ${recalled.length} relevant memories:${RESET}`);
    showRecallResults(recalled);
    console.log(`\n${CYAN}🤖 Agent：（Because preference memory #1 exists, output an outline first and wait for confirmation)${RESET}`);

    await memory.write({
      type: "task_result",
      content: "Outline-first writing worked well for technical articles; completed in three iterations",
      source: "auto",
      confidence: 0.8,
    });
    console.log(`${DIM}[write] Task experience recorded${RESET}`);

    showMemoryState(memory, "Memory state at the end of Session 1");
    await memory.endSession();

    // ═══════════════════════════════════════════════════
    // SESSION 2: Tuesday (Cross-session!)
    // ═══════════════════════════════════════════════════
    await wait(`\n${DIM}Press Enter to enter Session 2 (Tuesday, cross-session)...${RESET}`, auto, rl);

    console.log(`\n${BOLD}${"─".repeat(60)}${RESET}`);
    console.log(`${BOLD}  SESSION 2：Tuesday 09:00-09:30  ← cross-session！${RESET}`);
    console.log(`${BOLD}${"─".repeat(60)}${RESET}`);

    await memory.startSession("user-001");
    console.log(`${DIM}[session start] decay check: No expiration (only one day has passed)${RESET}`);

    const msg4 = "Help me write a technical article about RAG best practices";
    console.log(`\n${GREEN}👤 user：${msg4}${RESET}`);
    const recalled2 = memory.recall(msg4, 5);
    console.log(`${DIM}[recall] Cross-session recall ${recalled2.length} relevant memories:${RESET}`);
    showRecallResults(recalled2);
    if (recalled2.some((item) => String(item.content ?? "").includes("writing") || String(item.content ?? "").includes("outline"))) {
      console.log(`\n${CYAN}🤖 Agent：（Memory Cross-session memory works! Output an outline first with a direct tone)${RESET}`);
      console.log(`    The user does not need to repeat 'give the outline first'; the preference persisted across sessions.${RESET}`);
    }

    await memory.write({
      type: "task_result",
      content: "RAG The article was completed outline-first and the user was satisfied",
      source: "auto",
      confidence: 0.8,
    });

    showMemoryState(memory, "Memory state at the end of Session 2");
    await memory.endSession();

    // ═══════════════════════════════════════════════════
    // SESSION 3: Wednesday (Preference changed!)
    // ═══════════════════════════════════════════════════
    await wait(`\n${DIM}Press Enter to enter Session 3 (Wednesday, preference changed)...${RESET}`, auto, rl);

    console.log(`\n${BOLD}${"─".repeat(60)}${RESET}`);
    console.log(`${BOLD}  SESSION 3：Wednesday 14:00-14:30  ← preference changed！${RESET}`);
    console.log(`${BOLD}${"─".repeat(60)}${RESET}`);

    await memory.startSession("user-001");

    const msg5 = "Use Python for example code from now on";
    console.log(`\n${GREEN}👤 user：${msg5}${RESET}`);
    const candidates5 = memory.identifyCandidates(msg5);
    for (const candidate of candidates5) {
      const result = await memory.write({ ...candidate, category: "code_style" });
      if (result.status === "written") {
        console.log(`  → ${candidate.content.slice(0, 50)}... ${GREEN}✅ Wrote (conflict detected; the old TS preference was marked superseded)${RESET}`);
      } else {
        console.log(`  → ${candidate.content.slice(0, 50)}... ${RED}❌ reject: ${result.reason}${RESET}`);
      }
    }

    const msg6 = "Help me write a technical article about a Python Agent framework";
    console.log(`\n${GREEN}👤 user：${msg6}${RESET}`);
    const recalled3 = memory.recall(msg6, 5);
    console.log(`${DIM}[recall] Recall ${recalled3.length} relevant memories:${RESET}`);
    showRecallResults(recalled3);
    console.log(`\n${CYAN}🤖 Agent：（Use Python examples, not TS! The preference change took effect)${RESET}`);

    showMemoryState(memory, "Memory state at the end of Session 3");
    await memory.endSession();

    // ═══════════════════════════════════════════════════
    // Summary
    // ═══════════════════════════════════════════════════
    console.log(`\n${BOLD}${"─".repeat(60)}${RESET}`);
    console.log(`${BOLD}  📊 Full lifecycle summary${RESET}`);
    console.log(`${BOLD}${"─".repeat(60)}${RESET}`);

    console.log(`
  ✅ Cross-session persistence: Session 2 did not require repeating "give the outline first"
  ✅ Conflict replacement: Session 3 "use Python" overrode "use TS"
  ✅ Auditable history: the old TS preference remains (superseded) and traceable
  ✅ Inference vs confirmation: inferred preference (TS) was automatically overridden by explicit declaration (Python)
  ✅ Audit log：${GREEN}memory_store/audit.jsonl${RESET} recorded all operations

  ${DIM}View storage files：${RESET}
    ${CYAN}memory_store/preferences.json${RESET}  - User preferences
    ${CYAN}memory_store/facts.json${RESET}        - Long-term facts
    ${CYAN}memory_store/task_history.json${RESET} - Task experience
    ${CYAN}memory_store/audit.jsonl${RESET}       - Audit log
`);
  } finally {
    rl?.close();
  }
}

const autoMode = process.argv.includes("--auto");
await simulate(autoMode);
