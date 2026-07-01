#!/usr/bin/env node
/**
 * 课程五 05-07 Human-in-the-loop 示例
 *
 * 用法：
 *   node hitl_demo.mjs --auto
 *   node hitl_demo.mjs
 */

import { appendFile, readFile, rm, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
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
  constructor(auto) {
    this.auto = auto;
    this.rl = createInterface({ input, output });
  }

  async close() {
    this.rl.close();
  }

  async choose(prompt, options, defaultKey) {
    console.log(prompt);
    for (const [key, label] of Object.entries(options)) {
      const marker = key === defaultKey ? " (默认)" : "";
      console.log(`  ${key}. ${label}${marker}`);
    }

    if (this.auto) {
      console.log(`  自动选择: ${defaultKey}\n`);
      return defaultKey;
    }

    const answer = (await this.rl.question("  请选择: ")).trim() || defaultKey;
    console.log();
    return options[answer] ? answer : defaultKey;
  }
}

class HitlAgent {
  constructor(auto) {
    this.policy = new HitlPolicy();
    this.audit = new AuditLog();
    this.memory = new TeachingMemory();
    this.human = new HumanSimulator(auto);
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
      decision = { mode, risk, decision: "auto_execute", reason: "只读或低风险操作，无需介入" };
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
    let prompt = "\n[确认模式] Agent 请求执行操作：\n";
    prompt += `  工具: ${action.tool}\n`;
    prompt += `  目标: ${action.target}\n`;
    prompt += `  原因: ${action.reason}\n`;
    prompt += `  风险: ${risk}\n`;
    if (metadata.impact) prompt += `  影响: ${metadata.impact}\n`;
    if (metadata.anomalies) prompt += `  异常项: ${metadata.anomalies.join(", ")}\n`;

    const choice = await this.human.choose(
      prompt,
      {
        a: "批准执行",
        s: "只执行安全子集",
        r: "拒绝",
        m: "转为人工处理",
      },
      metadata.default_decision ?? "s"
    );
    const mapping = {
      a: ["approved", "人类批准完整操作"],
      s: ["safe_subset", "人类选择只执行风险更低的子集"],
      r: ["rejected", "人类拒绝操作"],
      m: ["manual", "人类要求接管"],
    };
    const [decision, reason] = mapping[choice];
    return { mode: HitlMode.CONFIRMATION, risk, decision, reason };
  }

  async takeover(action, risk) {
    console.log("\n[接管模式] Agent 不会自主执行该操作。");
    console.log(`  工具: ${action.tool}`);
    console.log(`  目标: ${action.target}`);
    console.log(`  原因: ${action.reason}`);
    console.log("  已生成执行说明，由人类完成后再让 Agent 继续。");
    if (action.tool === "database_migration") {
      console.log('  建议命令: psql "$DATABASE_URL" -f ./migration.sql');
    }
    console.log();
    return {
      mode: HitlMode.TAKEOVER,
      risk,
      decision: "manual_required",
      reason: "关键风险操作需要人类执行",
    };
  }

  async clarifyRecentArticles() {
    const choice = await this.human.choose(
      "\n[澄清模式] 用户说“整理最近的文章”，Agent 需要明确“最近”指什么：",
      {
        a: "最近 7 天创建的文章（3 篇）",
        b: "最近修改过的文章（8 篇）",
        c: "最近打开过的文章（5 篇）",
        d: "其他，我手动说明",
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
      { tool: "organize_articles", target: "articles", reason: "用户指令存在多义性", reversible: true },
      {
        mode: HitlMode.CLARIFICATION,
        risk: Risk.MEDIUM,
        decision: labels[choice],
        reason: "人类定义模糊意图",
      }
    );
  }

  async reviewReleaseDoc() {
    console.log("\n[审核模式] Agent 生成了发布文档草稿，并主动标注不确定点：");
    console.log("  1. 架构变更摘要：已生成");
    console.log("  2. API 兼容性说明：已生成");
    console.log("  3. 回滚方案：待确认，数据库回滚窗口不确定");
    console.log("  4. 发布 checklist：可能遗漏数据库备份");
    const choice = await this.human.choose(
      "  请审核：",
      {
        p: "通过",
        e: "要求补充数据库备份步骤",
        r: "退回重写",
      },
      "e"
    );
    const decision = choice === "p" ? "approved" : "needs_revision";
    await this.audit.record(
      { tool: "write_file", target: "release_notes.md", reason: "生成发布文档", reversible: true },
      { mode: HitlMode.REVIEW, risk: Risk.MEDIUM, decision, reason: "人类审核 Agent 产出" }
    );

    if (choice === "e") {
      await this.applyTeachingFeedback("发布 checklist 必须包含数据库备份步骤", "release_checklist");
    }
  }

  async applyTeachingFeedback(correction, category) {
    console.log("\n[教学反馈模式] 人类指出：", correction);
    console.log("  Agent 即时修正当前文档，并写入可复用偏好。");
    await this.memory.remember(category, correction, "human_review");
    await this.audit.record(
      { tool: "update_memory", target: category, reason: "从人工反馈中学习", reversible: true },
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
      if (["approved", "safe_subset", "auto_execute"].includes(decision)) data.approved += 1;
      if (["manual", "manual_required"].includes(decision)) data.manual += 1;
      if (decision === "rejected") data.rejected += 1;
    }

    console.log("\n[HITL 数据分析] 基于本次审计日志生成策略建议：");
    for (const [tool, data] of stats.entries()) {
      const rate = data.approved / data.total;
      let advice = "保持当前策略";
      if (rate >= 0.95 && data.manual === 0) advice = "可考虑降低确认频率";
      if (data.manual > 0 || rate < 0.7) advice = "保持或提高介入强度";
      console.log(`  - ${tool}: ${data.total} 次，自动/通过率 ${(rate * 100).toFixed(0)}% -> ${advice}`);
    }

    if (this.memory.items.length > 0) {
      console.log("\n[Memory] 从教学反馈沉淀的偏好：");
      for (const item of this.memory.items) {
        console.log(`  - ${item.category}: ${item.content}`);
      }
    }
  }
}

async function runBatchDeleteDemo(agent) {
  console.log("\n=== 1. 风险分级 + 批次确认 ===");
  const decision = await agent.propose({
    tool: "delete_file",
    target: "/tmp/logs/*",
    reason: "清理超过 30 天的日志文件",
    reversible: false,
    metadata: {
      impact: "将删除 3 个 .log 文件，共 48MB；检测到 1 个非日志异常项不会默认删除",
      anomalies: ["/tmp/logs/.env.backup"],
      default_decision: "s",
    },
  });

  if (decision.decision === "safe_subset") {
    console.log("  执行结果: 只删除 .log 文件，保留 /tmp/logs/.env.backup\n");
  } else if (decision.decision === "approved") {
    console.log("  执行结果: 删除全部候选文件\n");
  } else {
    console.log("  执行结果: 未执行删除\n");
  }
}

async function runRefundDemo(agent) {
  console.log("\n=== 2. 退款操作的上下文确认 ===");
  await agent.propose({
    tool: "refund",
    target: "order ORD-20260629-0042",
    reason: "用户反馈产品功能与描述不符，订单未发货",
    reversible: false,
    external_effect: true,
    metadata: {
      amount: 299,
      previous_refunds: 0,
      impact: "全额退款 ¥299.00；用户注册 2 年，此前 0 次退款",
      default_decision: "a",
    },
  });

  await agent.propose({
    tool: "refund",
    target: "order ORD-20260629-0099",
    reason: "高额订单且用户近期多次退款",
    reversible: false,
    external_effect: true,
    metadata: { amount: 2400, previous_refunds: 5 },
  });
}

async function runTakeoverDemo(agent) {
  console.log("\n=== 3. 关键风险操作进入接管模式 ===");
  await agent.propose({
    tool: "database_migration",
    target: "production users.email type change",
    reason: "迁移脚本会修改生产数据库 schema",
    reversible: false,
    external_effect: true,
  });
}

async function runDemo() {
  const auto = process.argv.includes("--auto");
  const agent = new HitlAgent(auto);
  await agent.reset();

  console.log("=".repeat(68));
  console.log("  Human-in-the-loop — 当 Agent 不该自己决定时");
  console.log("=".repeat(68));

  try {
    await runBatchDeleteDemo(agent);
    await agent.clarifyRecentArticles();
    await runRefundDemo(agent);
    await runTakeoverDemo(agent);
    await agent.reviewReleaseDoc();
    await agent.analyzeAudit();

    console.log("\n输出文件:");
    console.log("  - hitl_audit.jsonl");
    console.log("  - hitl_memory.json");
  } finally {
    await agent.close();
  }
}

await runDemo();
