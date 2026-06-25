#!/usr/bin/env node
/**
 * 课程五 05-03 Memory 示例 —— 交互式 Memory 生命周期演示
 *
 * 模拟知识助手从周一到周三的跨会话对话，展示 Memory 系统的完整生命周期：
 *   识别候选记忆 → 写入决策 → 存储 → 召回 → 更新与遗忘
 *
 * 纯 Node.js 标准库实现（bag-of-words 向量），无需外部依赖。
 *
 * 用法：
 *   node memory_demo.mjs           # 交互模式（每一步按 Enter 继续）
 *   node memory_demo.mjs --auto    # 自动模式（适合查看完整输出）
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
// 轻量 Memory 实现（核心逻辑）
// ============================================================

class AgentMemory {
  /** 分层存储 + 写入守卫 + 语义召回 + 审计日志 */
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

  // ── 识别候选记忆 ──
  identifyCandidates(userMessage) {
    const candidates = [];
    for (const pattern of [/以后[^，。]*/g, /每次[^，。]*/g, /不要[^，。]*/g, /默认[^，。]*/g]) {
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

    if (/(?:api[_\s]?key|secret|token|密码)\s*[：:=]\s*\S+/i.test(userMessage)) {
      candidates.push({
        type: "sensitive",
        content: "[敏感信息]",
        source: "detected",
        confidence: 0.99,
        sensitive: true,
      });
    }

    for (const match of userMessage.matchAll(/这次[^，。]*/g)) {
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

  // ── 写入守卫 ──
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

  // ── 写入 ──
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

  // ── 召回 ──
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

  // ── 更新 / 删除 / 衰减 ──
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
// 交互式演示
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
    console.log(`\n${DIM}── 自动进入下一步 ──${RESET}`);
    await sleep(500);
  } else if (rl) {
    await rl.question(message);
  }
}

function showBanner() {
  console.log(`
${CYAN}${BOLD}╔══════════════════════════════════════════════════════════╗
║     课程五 05-03 Memory 生命周期演示                         ║
║     模拟知识助手 周一 → 周三 的跨会话 Memory 行为              ║
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
    console.log(`  ${DIM}(无相关记忆)${RESET}`);
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
    // SESSION 1: 周一
    // ═══════════════════════════════════════════════════
    console.log(`${BOLD}${"─".repeat(60)}${RESET}`);
    console.log(`${BOLD}  SESSION 1：周一 10:00-10:45${RESET}`);
    console.log(`${BOLD}${"─".repeat(60)}${RESET}`);

    await memory.startSession("user-001");
    console.log(`\n${DIM}[会话开始] decay check: 无过期记忆（系统初始化）${RESET}`);

    const msg = "以后写技术文章，先给我大纲确认，再展开正文。语气直接，不要营销化。";
    console.log(`\n${GREEN}👤 用户：${msg}${RESET}`);

    const candidates = memory.identifyCandidates(msg);
    console.log(`${DIM}[identify] 识别到 ${candidates.length} 条候选记忆${RESET}`);
    for (const candidate of candidates) {
      const category =
        candidate.content.includes("大纲") || candidate.content.includes("先给")
          ? "writing_workflow"
          : candidate.content.includes("语气") || candidate.content.includes("营销")
            ? "writing_tone"
            : "writing_style";
      const result = await memory.write({ ...candidate, category });
      const status =
        result.status === "written"
          ? `${GREEN}✅ 写入${RESET}`
          : `${RED}❌ 拒绝: ${result.reason}${RESET}`;
      console.log(`  → ${candidate.content.slice(0, 50)}... ${status}`);
    }

    const msg2 = "我最近在用 TypeScript 写 Agent 框架，帮我看看这段代码";
    console.log(`\n${GREEN}👤 用户：${msg2}${RESET}`);
    console.log(`${DIM}[identify] 此消息未触发显式偏好规则，但系统从行为中推断：用户可能偏好 TypeScript${RESET}`);

    const inferred = await memory.write({
      type: "preference",
      category: "code_style",
      content: "用户可能偏好 TypeScript 示例代码",
      source: "inferred",
      confidence: 0.5,
      sensitive: false,
    });
    const inferredStatus =
      inferred.status === "written"
        ? `${YELLOW}⚠️ 写入为候选记忆（低置信度推断，待用户确认）${RESET}`
        : `${RED}❌ 拒绝${RESET}`;
    if (inferred.status === "written") {
      memory.pending.push({ id: inferred.id, content: "用户可能偏好 TypeScript 示例代码" });
    }
    console.log(`  → 推断偏好: TypeScript 示例代码... ${inferredStatus}`);

    const msg3 = "帮我写一篇 Agent Memory 的技术文章";
    console.log(`\n${GREEN}👤 用户：${msg3}${RESET}`);
    const recalled = memory.recall(msg3, 5);
    console.log(`${DIM}[recall] 召回 ${recalled.length} 条相关记忆:${RESET}`);
    showRecallResults(recalled);
    console.log(`\n${CYAN}🤖 Agent：（因为有 #1 偏好记忆，先输出大纲等待确认）${RESET}`);

    await memory.write({
      type: "task_result",
      content: "先大纲再正文在技术文章中效果好，3轮迭代完成",
      source: "auto",
      confidence: 0.8,
    });
    console.log(`${DIM}[write] 任务经验已记录${RESET}`);

    showMemoryState(memory, "Session 1 结束时的 Memory 状态");
    await memory.endSession();

    // ═══════════════════════════════════════════════════
    // SESSION 2: 周二（跨会话！）
    // ═══════════════════════════════════════════════════
    await wait(`\n${DIM}按 Enter 进入 Session 2（周二，跨会话）...${RESET}`, auto, rl);

    console.log(`\n${BOLD}${"─".repeat(60)}${RESET}`);
    console.log(`${BOLD}  SESSION 2：周二 09:00-09:30  ← 跨会话！${RESET}`);
    console.log(`${BOLD}${"─".repeat(60)}${RESET}`);

    await memory.startSession("user-001");
    console.log(`${DIM}[会话开始] decay check: 无过期（才过了一天）${RESET}`);

    const msg4 = "帮我写一篇 RAG 最佳实践的技术文章";
    console.log(`\n${GREEN}👤 用户：${msg4}${RESET}`);
    const recalled2 = memory.recall(msg4, 5);
    console.log(`${DIM}[recall] 跨会话召回 ${recalled2.length} 条相关记忆:${RESET}`);
    showRecallResults(recalled2);
    if (recalled2.some((item) => String(item.content ?? "").includes("写作") || String(item.content ?? "").includes("大纲"))) {
      console.log(`\n${CYAN}🤖 Agent：（Memory 跨会话生效！先输出大纲，语气直接）${RESET}`);
      console.log(`    用户不需要重新说『先给大纲』——偏好跨会话保持了。${RESET}`);
    }

    await memory.write({
      type: "task_result",
      content: "RAG 文章用先大纲方式完成，用户满意",
      source: "auto",
      confidence: 0.8,
    });

    showMemoryState(memory, "Session 2 结束时的 Memory 状态");
    await memory.endSession();

    // ═══════════════════════════════════════════════════
    // SESSION 3: 周三（偏好变更！）
    // ═══════════════════════════════════════════════════
    await wait(`\n${DIM}按 Enter 进入 Session 3（周三，偏好变更）...${RESET}`, auto, rl);

    console.log(`\n${BOLD}${"─".repeat(60)}${RESET}`);
    console.log(`${BOLD}  SESSION 3：周三 14:00-14:30  ← 偏好变更！${RESET}`);
    console.log(`${BOLD}${"─".repeat(60)}${RESET}`);

    await memory.startSession("user-001");

    const msg5 = "以后示例代码改用 Python";
    console.log(`\n${GREEN}👤 用户：${msg5}${RESET}`);
    const candidates5 = memory.identifyCandidates(msg5);
    for (const candidate of candidates5) {
      const result = await memory.write({ ...candidate, category: "code_style" });
      if (result.status === "written") {
        console.log(`  → ${candidate.content.slice(0, 50)}... ${GREEN}✅ 写入（检测到冲突，旧 TS 偏好已标记 superseded）${RESET}`);
      } else {
        console.log(`  → ${candidate.content.slice(0, 50)}... ${RED}❌ 拒绝: ${result.reason}${RESET}`);
      }
    }

    const msg6 = "帮我写一篇 Python Agent 框架的技术文章";
    console.log(`\n${GREEN}👤 用户：${msg6}${RESET}`);
    const recalled3 = memory.recall(msg6, 5);
    console.log(`${DIM}[recall] 召回 ${recalled3.length} 条相关记忆:${RESET}`);
    showRecallResults(recalled3);
    console.log(`\n${CYAN}🤖 Agent：（用 Python 示例，不是 TS！偏好变更生效了）${RESET}`);

    showMemoryState(memory, "Session 3 结束时的 Memory 状态");
    await memory.endSession();

    // ═══════════════════════════════════════════════════
    // 总结
    // ═══════════════════════════════════════════════════
    console.log(`\n${BOLD}${"─".repeat(60)}${RESET}`);
    console.log(`${BOLD}  📊 完整生命周期总结${RESET}`);
    console.log(`${BOLD}${"─".repeat(60)}${RESET}`);

    console.log(`
  ✅ 跨会话延续：Session 2 不需要重新说"先给大纲"
  ✅ 冲突替换：Session 3"用 Python"覆盖了"用 TS"
  ✅ 审计可见：旧 TS 偏好仍保留（superseded），可追溯
  ✅ 推断 vs 确认：推断偏好（TS）自动被显式声明（Python）覆盖
  ✅ 审计日志：${GREEN}memory_store/audit.jsonl${RESET} 记录了所有操作

  ${DIM}查看存储文件：${RESET}
    ${CYAN}memory_store/preferences.json${RESET}  - 用户偏好
    ${CYAN}memory_store/facts.json${RESET}        - 长期事实
    ${CYAN}memory_store/task_history.json${RESET} - 任务经验
    ${CYAN}memory_store/audit.jsonl${RESET}       - 审计日志
`);
  } finally {
    rl?.close();
  }
}

const autoMode = process.argv.includes("--auto");
await simulate(autoMode);
