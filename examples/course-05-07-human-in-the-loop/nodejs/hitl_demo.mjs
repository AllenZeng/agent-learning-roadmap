#!/usr/bin/env node
/**
 * Course 05-07 Human-in-the-loop example
 *
 * Usage:
 *   node hitl_demo.mjs
 */

import { appendFile, readFile, rm, writeFile } from "node:fs/promises";
import { existsSync, readFileSync } from "node:fs";
import { createInterface } from "node:readline/promises";
import { stdin as input, stdout as output } from "node:process";

const Risk = Object.freeze({
  LOW: "low",
  MEDIUM: "medium",
  HIGH: "high",
  CRITICAL: "critical",
});

const HitlMode = Object.freeze({
  NONE: "none",
  CONFIRMATION: "confirmation",
  CLARIFICATION: "clarification",
  TAKEOVER: "takeover",
  REVIEW: "review",
  TEACHING_FEEDBACK: "teaching_feedback",
});

class HitlPolicy {
  assess(action) {
    const metadata = action.metadata ?? {};

    if (["read_file", "search_notes"].includes(action.tool)) {
      return [Risk.LOW, HitlMode.NONE];
    }

    if (action.tool === "refund") {
      const amount = metadata.amount ?? 0;
      const previousRefunds = metadata.previous_refunds ?? 0;
      if (amount > 1000 || previousRefunds >= 3) {
        return [Risk.CRITICAL, HitlMode.TAKEOVER];
      }
      return [Risk.HIGH, HitlMode.CONFIRMATION];
    }

    if (action.tool === "database_migration") {
      return [Risk.CRITICAL, HitlMode.TAKEOVER];
    }

    if (action.tool === "delete_file") {
      if (action.target.includes("/.ssh/") || action.target.endsWith(".env") || action.target.includes(".env")) {
        return [Risk.CRITICAL, HitlMode.TAKEOVER];
      }
      if (!action.reversible) return [Risk.HIGH, HitlMode.CONFIRMATION];
      return [Risk.MEDIUM, HitlMode.CONFIRMATION];
    }

    if (["write_file", "send_email"].includes(action.tool)) {
      return [Risk.MEDIUM, HitlMode.CONFIRMATION];
    }

    return [Risk.MEDIUM, HitlMode.CONFIRMATION];
  }
}

class AuditLog {
  constructor(path = "hitl_audit.jsonl") {
    this.path = path;
  }

  async reset() {
    if (existsSync(this.path)) await rm(this.path);
  }

  async record(action, hitl) {
    const entry = {
      ts: new Date().toISOString(),
      action,
      hitl,
    };
    await appendFile(this.path, `${JSON.stringify(entry)}\n`, "utf8");
  }

  async load() {
    if (!existsSync(this.path)) return [];
    const content = await readFile(this.path, "utf8");
    return content
      .split("\n")
      .filter(Boolean)
      .map((line) => JSON.parse(line));
  }
}

class TeachingMemory {
  constructor(path = "hitl_memory.json") {
    this.path = path;
    this.items = [];
  }

  async reset() {
    this.items = [];
    if (existsSync(this.path)) await rm(this.path);
  }

  async remember(category, content, source) {
    const item = {
      category,
      content,
      source,
      created_at: new Date().toISOString(),
    };
    this.items.push(item);
    await writeFile(this.path, JSON.stringify(this.items, null, 2), "utf8");
  }
}

class HumanSimulator {
  constructor() {
    this.rl = input.isTTY ? createInterface({ input, output }) : null;
    this.pipedAnswers = input.isTTY ? [] : readFileSync(0, "utf8").split(/\r?\n/);
    this.answerIndex = 0;
  }

  async close() {
    if (this.rl) this.rl.close();
  }

  async choose(prompt, options, defaultKey) {
    console.log(prompt);
    for (const [key, label] of Object.entries(options)) {
      const marker = key === defaultKey ? " (default)" : "";
      console.log(`  ${key}. ${label}${marker}`);
    }

    let answer;
    if (this.rl) {
      answer = (await this.rl.question("  Please choose: ")).trim() || defaultKey;
    } else {
      const raw = this.pipedAnswers[this.answerIndex++] ?? "";
      answer = raw.trim() || defaultKey;
      console.log(`  Please choose: ${raw.trim()}`);
    }
    console.log();
    return options[answer] ? answer : defaultKey;
  }
}

class HitlAgent {
  constructor() {
    this.policy = new HitlPolicy();
    this.audit = new AuditLog();
    this.memory = new TeachingMemory();
    this.human = new HumanSimulator();
  }

  async reset() {
    await this.audit.reset();
    await this.memory.reset();
  }

  async close() {
    await this.human.close();
  }

  async propose(action) {
    const [risk, mode] = this.policy.assess(action);
    let decision;
    if (mode === HitlMode.NONE) {
      decision = { mode, risk, decision: "direct_execute", reason: "textlowRiskstext，nonetext" };
    } else if (mode === HitlMode.TAKEOVER) {
      decision = await this.takeover(action, risk);
    } else {
      decision = await this.confirmation(action, risk);
    }
    await this.audit.record(action, decision);
    return decision;
  }

  async confirmation(action, risk) {
    const metadata = action.metadata ?? {};
    let prompt = "\n[confirmation mode] Agent requests operation execution：\n";
    prompt += `  tool: ${action.tool}\n`;
    prompt += `  Goal: ${action.target}\n`;
    prompt += `  reason: ${action.reason}\n`;
    prompt += `  Risks: ${risk}\n`;
    if (metadata.impact) prompt += `  impact: ${metadata.impact}\n`;
    if (metadata.anomalies) prompt += `  anomalies: ${metadata.anomalies.join(", ")}\n`;

    const choice = await this.human.choose(
      prompt,
      {
        a: "approveexecute",
        s: "execute onlysafe subset",
        r: "reject",
        m: "switch tomanual handling",
      },
      metadata.default_decision ?? "s"
    );
    const mapping = {
      a: ["approved", "humanapprovetext"],
      s: ["safe_subset", "humantextRiskstextlowtext"],
      r: ["rejected", "humanrejecttext"],
      m: ["manual", "humantext"],
    };
    const [decision, reason] = mapping[choice];
    return { mode: HitlMode.CONFIRMATION, risk, decision, reason };
  }

  async takeover(action, risk) {
    console.log("\n[takeover mode] Agent will not execute this operation autonomously。");
    console.log(`  tool: ${action.tool}`);
    console.log(`  Goal: ${action.target}`);
    console.log(`  reason: ${action.reason}`);
    console.log("  textinstructions，texthumancompletetext Agent text。");
    if (action.tool === "database_migration") {
      console.log('  Recommendationstext: psql "$DATABASE_URL" -f ./migration.sql');
    }
    console.log();
    return {
      mode: HitlMode.TAKEOVER,
      risk,
      decision: "manual_required",
      reason: "Critical-risk operations require human execution",
    };
  }

  async clarifyRecentArticles() {
    const choice = await this.human.choose(
      "\n[clarification mode] usertext“organize recent articles”，Agent needs to clarify“recent”means what：",
      {
        a: "recent 7 text（3 files)",
        b: "recently modified articles（8 files)",
        c: "recently opened articles（5 files)",
        d: "texthe，textinstructions",
      },
      "b"
    );
    const labels = {
      a: "created_in_7_days",
      b: "modified_recently",
      c: "opened_recently",
      d: "custom",
    };
    await this.audit.record(
      { tool: "organize_articles", target: "articles", reason: "userinstructionstext", reversible: true },
      {
        mode: HitlMode.CLARIFICATION,
        risk: Risk.MEDIUM,
        decision: labels[choice],
        reason: "humantext",
      }
    );
  }

  async reviewReleaseDoc() {
    console.log("\n[review mode] Agent textreleasedocstext，and proactively marked uncertainties：");
    console.log("  1. architecture-change summary：text");
    console.log("  2. API textinstructions：text");
    console.log("  3. rollback plan：pending confirmation，database rollback window is uncertain");
    console.log("  4. release checklist：may miss database backup");
    const choice = await this.human.choose(
      "  Please review：",
      {
        p: "pass",
        e: "textstep",
        r: "return for rewrite",
      },
      "e"
    );
    const decision = choice === "p" ? "approved" : "needs_revision";
    await this.audit.record(
      { tool: "write_file", target: "release_notes.md", reason: "textreleasedocs", reversible: true },
      { mode: HitlMode.REVIEW, risk: Risk.MEDIUM, decision, reason: "humantext Agent text" }
    );

    if (choice === "e") {
      await this.applyTeachingFeedback("release checklist textstep", "release_checklist");
    }
  }

  async applyTeachingFeedback(correction, category) {
    console.log("\n[teaching-feedback mode] humantext：", correction);
    console.log("  Agent textcorrectiontextdocs，textWritetext。");
    await this.memory.remember(category, correction, "human_review");
    await this.audit.record(
      { tool: "update_memory", target: category, reason: "textmediumtext", reversible: true },
      {
        mode: HitlMode.TEACHING_FEEDBACK,
        risk: Risk.MEDIUM,
        decision: "remembered",
        reason: correction,
      }
    );
    console.log();
  }

  async analyzeAudit() {
    const entries = await this.audit.load();
    const stats = new Map();
    for (const entry of entries) {
      const tool = entry.action.tool;
      const decision = entry.hitl.decision;
      if (!stats.has(tool)) stats.set(tool, { total: 0, approved: 0, manual: 0, rejected: 0 });
      const data = stats.get(tool);
      data.total += 1;
      if (["approved", "safe_subset", "direct_execute"].includes(decision)) data.approved += 1;
      if (["manual", "manual_required"].includes(decision)) data.manual += 1;
      if (decision === "rejected") data.rejected += 1;
    }

    console.log("\n[HITL textanalysis] texttimesAudit logtextRecommendations：");
    for (const [tool, data] of stats.entries()) {
      const rate = data.approved / data.total;
      let advice = "keep current policy";
      if (rate >= 0.95 && data.manual === 0) advice = "textlowtext";
      if (data.manual > 0 || rate < 0.7) advice = "texthightext";
      console.log(`  - ${tool}: ${data.total} times，direct execution/approval rate ${(rate * 100).toFixed(0)}% -> ${advice}`);
    }

    if (this.memory.items.length > 0) {
      console.log("\n[Memory] preferences distilled from teaching feedback：");
      for (const item of this.memory.items) {
        console.log(`  - ${item.category}: ${item.content}`);
      }
    }
  }
}

async function runBatchDeleteDemo(agent) {
  console.log("\n=== 1. Riskstext + texttimesconfirm ===");
  const decision = await agent.propose({
    tool: "delete_file",
    target: "/tmp/logs/*",
    reason: "clean older than 30 days of log files",
    reversible: false,
    metadata: {
      impact: "textdelete 3 items .log text，total 48MB；text 1 textdefaultdelete",
      anomalies: ["/tmp/logs/.env.backup"],
      default_decision: "s",
    },
  });

  if (decision.decision === "safe_subset") {
    console.log("  Execution result: textdelete .log text，kept /tmp/logs/.env.backup\n");
  } else if (decision.decision === "approved") {
    console.log("  Execution result: deletetext\n");
  } else {
    console.log("  Execution result: not executeddelete\n");
  }
}

function printRefundResult(decision, orderId) {
  if (decision.decision === "approved") {
    console.log(`  Execution result: submitted ${orderId} textrefundtext，textWriterefundtext\n`);
  } else if (decision.decision === "safe_subset") {
    console.log(`  Execution result: textrefund，textMove  ${orderId} textmanual reviewtext\n`);
  } else if (decision.decision === "manual") {
    console.log(`  Execution result: humantext，Agent textrefundtextkeptdecisioncontext\n`);
  } else if (decision.decision === "manual_required") {
    console.log(`  Execution result: textRisksrefundnot executed，Agent textProcessinginstructions，textmanual handling\n`);
  } else {
    console.log(`  Execution result: textreject ${orderId} textrefundtext，textuserinstructionsreason\n`);
  }
}

function printTakeoverResult(decision, taskName) {
  if (decision.decision === "manual_required") {
    console.log(`  Execution result: ${taskName} not executed by Agent execute；Agent textStatus，texthumantext“Completed”\n`);
  } else if (decision.decision === "approved") {
    console.log(`  Execution result: ${taskName} textapprove，textRecommendationstextsystemmediumkepttext\n`);
  } else {
    console.log(`  Execution result: ${taskName} not executed，textmediumtext\n`);
  }
}

async function runRefundDemo(agent) {
  console.log("\n=== 2. refundtextcontextconfirm ===");
  const refundDecision = await agent.propose({
    tool: "refund",
    target: "order ORD-20260629-0042",
    reason: "usertextfeaturetext，order has not shipped",
    reversible: false,
    external_effect: true,
    metadata: {
      amount: 299,
      previous_refunds: 0,
      impact: "textrefund ¥299.00；usertext 2 text，previously 0 timesrefund",
      default_decision: "a",
    },
  });
  printRefundResult(refundDecision, "ORD-20260629-0042");

  const suspiciousRefundDecision = await agent.propose({
    tool: "refund",
    target: "order ORD-20260629-0099",
    reason: "hightextusertexttimesrefund",
    reversible: false,
    external_effect: true,
    metadata: { amount: 2400, previous_refunds: 5 },
  });
  printRefundResult(suspiciousRefundDecision, "ORD-20260629-0099");
}

async function runTakeoverDemo(agent) {
  console.log("\n=== 3. textRiskstext ===");
  const decision = await agent.propose({
    tool: "database_migration",
    target: "production users.email type change",
    reason: "text schema",
    reversible: false,
    external_effect: true,
  });
  printTakeoverResult(decision, "production database migration");
}

async function runDemo() {
  const agent = new HitlAgent();
  await agent.reset();

  console.log("=".repeat(68));
  console.log("  Human-in-the-loop — when Agent text");
  console.log("=".repeat(68));

  try {
    await runBatchDeleteDemo(agent);
    await agent.clarifyRecentArticles();
    await runRefundDemo(agent);
    await runTakeoverDemo(agent);
    await agent.reviewReleaseDoc();
    await agent.analyzeAudit();

    console.log("\nOutput files:");
    console.log("  - hitl_audit.jsonl");
    console.log("  - hitl_memory.json");
  } finally {
    await agent.close();
  }
}

await runDemo();
