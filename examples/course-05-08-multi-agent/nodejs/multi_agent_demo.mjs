#!/usr/bin/env node
/**
 * 课程五 05-08 Multi-Agent 示例
 *
 * 同一个离线示例项目演示三种协作模式：
 * 1. Reviewer：一个 Agent 写方案，另一个 Agent 独立审查
 * 2. Supervisor：一个 Supervisor 拆解任务，多个 Worker 产出结构化结果
 * 3. Parallel Specialists：多个专家看同一个输入，从不同维度并行分析
 */

export function countAgentDifferences(left, right) {
  const differences = {
    inputs: !sameSet(left.inputs, right.inputs),
    tools: !sameSet(left.tools, right.tools),
    goal: left.goal !== right.goal,
    acceptance: left.acceptance !== right.acceptance,
  };
  return { ...differences, total: Object.values(differences).filter(Boolean).length };
}

function sameSet(left, right) {
  if (left.size !== right.size) return false;
  for (const item of left) {
    if (!right.has(item)) return false;
  }
  return true;
}

export class DemoExecutorAgent {
  constructor(options = {}) {
    this.fixableIssueIds = options.fixableIssueIds ?? null;
    this.revisions = [];
  }

  run(task, options = {}) {
    const applied = this.applicableIssueIds(options.fixInstructions ?? []);
    this.revisions.push([...applied].sort());
    return {
      output: this.renderArtifact(applied),
      privateTrace: "为了本地演示先用明文 key；权限模型先简化成 admin；依赖版本先不锁定，后续再补。",
    };
  }

  applicableIssueIds(issues) {
    const issueIds = new Set(issues.map((issue) => issue.id));
    if (!this.fixableIssueIds) return issueIds;
    return new Set([...issueIds].filter((id) => this.fixableIssueIds.has(id)));
  }

  renderArtifact(fixed) {
    const apiLine = fixed.has("C1") ? "12: input: string, max_length: 256" : "12: input: string";
    const configLine = fixed.has("C2") ? '8: api_key: "${API_KEY}"' : '8: api_key: "sk-demo-plaintext"';
    const permissionLine = fixed.has("C3") ? "3-5: roles: reader, writer, admin" : "3-5: roles: admin";
    const dependencyLine = fixed.has("C4") ? "requirements.txt: fastapi==0.111.0" : "requirements.txt: fastapi>=0.111";
    return [
      "# API 模块技术方案",
      "",
      "## api_schema.yaml",
      apiLine,
      "",
      "## config.yaml",
      configLine,
      "",
      "## permissions.py",
      permissionLine,
      "",
      "## dependencies",
      dependencyLine,
    ].join("\n");
  }
}

export class DemoReviewerAgent {
  constructor() {
    this.reviewRequests = [];
    this.seenPrivateTraces = [];
  }

  run(request) {
    this.reviewRequests.push(request);
    if (request.executorPrivateTrace) this.seenPrivateTraces.push(request.executorPrivateTrace);

    const checks = [];
    const issues = [];
    for (const item of request.criteria) {
      const result = this.check(item, request.artifact);
      checks.push(result);
      if (!result.passed) {
        issues.push({
          id: item.id,
          description: this.description(item.id),
          location: this.location(item.id),
          severity: item.severity,
          suggestion: result.suggestion ?? "按审查项补齐缺失约束",
        });
      }
    }
    return { verdict: issues.length === 0 ? "approved" : "rejected", checks, issues };
  }

  check(item, artifact) {
    if (item.id === "C1") {
      const passed = artifact.includes("max_length: 256");
      return {
        checkId: item.id,
        passed,
        evidence: passed ? "api_schema.yaml:12 包含 max_length" : "api_schema.yaml:12 缺少 max_length",
        suggestion: passed ? null : "为 input 参数增加 max_length: 256",
      };
    }
    if (item.id === "C2") {
      const passed = artifact.includes("${API_KEY}") && !artifact.includes("sk-demo-plaintext");
      return {
        checkId: item.id,
        passed,
        evidence: passed ? "config.yaml:8 使用环境变量" : "config.yaml:8 出现明文 api_key",
        suggestion: passed ? null : "改用 ${API_KEY} 环境变量",
      };
    }
    if (item.id === "C3") {
      const passed = artifact.includes("reader, writer, admin");
      return {
        checkId: item.id,
        passed,
        evidence: passed ? "permissions.py:3-5 区分 reader/writer/admin" : "permissions.py:3-5 只有 admin 角色",
        suggestion: passed ? null : "拆分 reader 和 writer 角色",
      };
    }
    if (item.id === "C4") {
      const passed = artifact.includes("fastapi==0.111.0");
      return {
        checkId: item.id,
        passed,
        evidence: passed ? "requirements.txt 使用 == 锁定版本" : "requirements.txt 使用 >=，版本未锁定",
        suggestion: passed ? null : "使用 == 锁定依赖版本",
      };
    }
    return { checkId: item.id, passed: false, evidence: "not_found", suggestion: "补充可验证证据" };
  }

  description(checkId) {
    return {
      C1: "/api/data 缺少输入长度限制",
      C2: "API key 明文存储",
      C3: "权限模型缺少读写分离",
      C4: "第三方依赖未锁定版本",
    }[checkId] ?? "未知审查项未通过";
  }

  location(checkId) {
    return {
      C1: "api_schema.yaml:12",
      C2: "config.yaml:8",
      C3: "permissions.py:3-5",
      C4: "requirements.txt",
    }[checkId] ?? "unknown";
  }
}

export class ReviewerPattern {
  constructor(executor, reviewer, options = {}) {
    this.executor = executor;
    this.reviewer = reviewer;
    this.maxRounds = options.maxRounds ?? 2;
  }

  run(task, criteria, options = {}) {
    const verbose = options.verbose ?? true;
    let draft = this.executor.run(task);
    const reviewTrace = [];

    for (let roundIndex = 0; roundIndex < this.maxRounds; roundIndex += 1) {
      if (verbose) console.log(`\n[Reviewer Round ${roundIndex + 1}]`);
      const review = this.reviewer.run({
        originalRequirement: task,
        artifact: draft.output,
        criteria,
        executorPrivateTrace: null,
      });
      reviewTrace.push(review);
      if (verbose) printReview(review);

      if (review.verdict === "approved") {
        return { status: "approved", output: draft.output, reviewRounds: roundIndex + 1, reviewTrace, unresolvedIssues: [], reason: "" };
      }
      if (roundIndex < this.maxRounds - 1) {
        if (verbose) console.log("[Runtime] 只把具体 issues 传回 Executor，不传主观评价。");
        draft = this.executor.run(task, { fixInstructions: review.issues });
      }
    }

    return {
      status: "disputed",
      output: draft.output,
      reviewRounds: this.maxRounds,
      reviewTrace,
      unresolvedIssues: reviewTrace.at(-1).issues,
      reason: "max_review_rounds",
    };
  }
}

export class DemoSupervisorAgent {
  decompose(task) {
    const outputFields = ["key_findings", "risks", "recommendations"];
    return {
      subtasks: [
        { id: "T1", topic: "Tool Use", worker: "tool_worker", scope: "工具调用链路、失败模式、权限边界", exclude: "不分析 Memory 或 Multi-Agent 中的工具协作", outputFields },
        { id: "T2", topic: "Memory", worker: "memory_worker", scope: "短期记忆、长期记忆、检索式记忆的工程取舍", exclude: "不分析纯 RAG 检索排序细节", outputFields },
        { id: "T3", topic: "Planning", worker: "planning_worker", scope: "plan-and-execute、动态重规划、停止条件", exclude: "不分析多 Agent 派发策略", outputFields },
        { id: "T4", topic: "Multi-Agent", worker: "multi_agent_worker", scope: "Reviewer、Supervisor、Parallel Specialists 的协作边界", exclude: "不重复单 Agent Tool Use 机制", outputFields },
      ],
    };
  }

  synthesize(task, plan, results) {
    const missingTopics = results.filter((result) => result.status !== "ok").map((result) => result.topic);
    const lines = [`# 汇总报告: ${task}`, ""];
    const seenFindings = new Set();
    for (const result of results) {
      lines.push(`## ${result.topic}`);
      if (result.status !== "ok") {
        lines.push(`- 数据缺失: ${result.missingReason}`);
        lines.push("");
        continue;
      }
      for (const finding of result.findings) {
        if (!seenFindings.has(finding)) {
          lines.push(`- 发现: ${finding}`);
          seenFindings.add(finding);
        }
      }
      for (const risk of result.risks) lines.push(`- 风险: ${risk}`);
      for (const recommendation of result.recommendations) lines.push(`- 建议: ${recommendation}`);
      lines.push("");
    }
    return {
      status: missingTopics.length > 0 ? "partial" : "complete",
      plan,
      workerResults: results,
      finalReport: lines.join("\n").trim(),
      missingTopics,
    };
  }
}

export class DemoResearchWorker {
  constructor(name, options = {}) {
    this.name = name;
    this.shouldFail = options.shouldFail ?? false;
    this.receivedSubtasks = [];
  }

  execute(subtask) {
    this.receivedSubtasks.push(subtask);
    if (this.shouldFail) {
      return { subtaskId: subtask.id, worker: this.name, topic: subtask.topic, status: "failed", findings: [], risks: [], recommendations: [], missingReason: "worker_timeout" };
    }
    const library = {
      "Tool Use": [
        ["工具白名单比 prompt 约束更可靠", "工具结果必须进入可追踪 observation"],
        ["读写工具混给同一 Agent 会放大误操作风险"],
        ["按 Agent 注册最小工具集，并记录 tool_call_id"],
      ],
      Memory: [
        ["长期记忆应先经过检索和摘要，而不是全量塞回上下文", "记忆写入需要显式触发条件"],
        ["把用户事实、任务状态、偏好分库存储"],
        ["把写入条件和过期策略做成配置"],
      ],
      Planning: [
        ["计划需要可验证 checkpoint，不能只是一段自然语言列表", "动态重规划必须有停止条件"],
        ["计划过细会让执行成本超过收益"],
        ["把计划项设计成可执行、可验收的小步"],
      ],
      "Multi-Agent": [
        ["拆分价值来自输入、工具、目标、验收标准的真实差异", "合并阶段必须保留冲突和缺失，不应自动粉饰"],
        ["自由对话式通信会让边界失控"],
        ["优先从 Reviewer 模式开始，再扩展 Supervisor 或多专家"],
      ],
    };
    const [findings, risks, recommendations] = library[subtask.topic];
    return { subtaskId: subtask.id, worker: this.name, topic: subtask.topic, status: "ok", findings, risks, recommendations, missingReason: "" };
  }
}

export class SupervisorPattern {
  constructor(supervisor, workers) {
    this.supervisor = supervisor;
    this.workers = workers;
  }

  run(task, options = {}) {
    const verbose = options.verbose ?? true;
    const plan = this.supervisor.decompose(task);
    const results = plan.subtasks.map((subtask) => this.workers[subtask.worker].execute(subtask));
    const final = this.supervisor.synthesize(task, plan, results);
    if (verbose) {
      console.log("\n[Supervisor]");
      console.log(`subtasks: ${plan.subtasks.length}, status: ${final.status}, missing: ${final.missingTopics.join(",")}`);
    }
    return final;
  }
}

export class DemoSpecialistAgent {
  constructor(dimension) {
    this.dimension = dimension;
  }

  analyze(artifact, dimension) {
    const findings = {
      correctness: [
        { id: "F1", dimension: "correctness", location: "checkout.py:18", problemType: "missing_validation", judgment: "problem", evidence: "amount 可以为负数", severity: "must_fix" },
        { id: "F2", dimension: "correctness", location: "checkout.py:33", problemType: "state_consistency", judgment: "problem", evidence: "扣库存和创建订单之间没有事务边界", severity: "must_fix" },
      ],
      security: [
        { id: "F3", dimension: "security", location: "checkout.py:18", problemType: "missing_validation", judgment: "problem", evidence: "未校验 amount 可能绕过限额规则", severity: "must_fix" },
        { id: "F4", dimension: "security", location: "checkout.py:41", problemType: "credential_exposure", judgment: "problem", evidence: "日志打印 payment_token", severity: "must_fix" },
        { id: "F5", dimension: "security", location: "checkout.py:55", problemType: "idempotency", judgment: "safe", evidence: "幂等键由服务端生成且不过期窗口合理", severity: "info" },
      ],
      performance: [
        { id: "F6", dimension: "performance", location: "checkout.py:27", problemType: "n_plus_one_query", judgment: "problem", evidence: "循环中逐个查询 coupon", severity: "should_fix" },
        { id: "F7", dimension: "performance", location: "checkout.py:55", problemType: "idempotency", judgment: "problem", evidence: "幂等记录未设置索引，订单高峰期会拖慢写入", severity: "should_fix" },
      ],
    }[this.dimension];
    return { dimension: dimension.name, findings };
  }
}

export class ParallelSpecialists {
  constructor(specialists) {
    this.specialists = specialists;
  }

  run(artifact, dimensions, options = {}) {
    const verbose = options.verbose ?? true;
    const results = dimensions.map((dimension) => this.specialists[dimension.agent].analyze(artifact, dimension));
    const final = this.merge(results);
    if (verbose) {
      console.log("\n[Parallel Specialists]");
      console.log(`findings: ${final.findings.length}, conflicts: ${final.conflicts.length}`);
    }
    return final;
  }

  merge(results) {
    const grouped = new Map();
    const dimensionSummary = Object.fromEntries(results.map((result) => [result.dimension, result.findings.length]));

    for (const result of results) {
      for (const finding of result.findings) {
        const key = `${finding.location}\u0000${finding.problemType}\u0000${finding.judgment}`;
        if (!grouped.has(key)) grouped.set(key, []);
        grouped.get(key).push(finding);
      }
    }

    const findings = [];
    for (const [key, items] of grouped) {
      const [location, problemType, judgment] = key.split("\u0000");
      findings.push({
        location,
        problemType,
        judgment,
        dimensions: [...new Set(items.map((item) => item.dimension))].sort(),
        evidence: items.map((item) => item.evidence),
        severity: items.map((item) => item.severity).sort((a, b) => severityRank(b) - severityRank(a))[0],
      });
    }

    const judgmentsByLocationType = new Map();
    const dimensionsByLocationType = new Map();
    for (const finding of findings) {
      const key = `${finding.location}\u0000${finding.problemType}`;
      if (!judgmentsByLocationType.has(key)) judgmentsByLocationType.set(key, new Set());
      if (!dimensionsByLocationType.has(key)) dimensionsByLocationType.set(key, new Set());
      judgmentsByLocationType.get(key).add(finding.judgment);
      for (const dimension of finding.dimensions) dimensionsByLocationType.get(key).add(dimension);
    }

    const conflicts = [];
    for (const [key, judgments] of judgmentsByLocationType) {
      if (judgments.size > 1) {
        const [location, problemType] = key.split("\u0000");
        conflicts.push({
          location,
          problemType,
          judgments: [...judgments].sort(),
          dimensions: [...dimensionsByLocationType.get(key)].sort(),
        });
      }
    }
    return { findings, conflicts, dimensionSummary };
  }
}

function severityRank(value) {
  return { info: 0, should_fix: 1, must_fix: 2 }[value] ?? -1;
}

export function defaultCriteria() {
  return [
    { id: "C1", check: "输入长度限制", howToVerify: "检查 /api/data 的 input 参数是否声明 max_length", severity: "must_fix" },
    { id: "C2", check: "密钥管理", howToVerify: "检查配置示例是否使用环境变量而不是明文 key", severity: "must_fix" },
    { id: "C3", check: "权限模型", howToVerify: "检查是否区分 reader 和 writer 角色", severity: "must_fix" },
    { id: "C4", check: "依赖锁定", howToVerify: "检查依赖是否使用 == 锁定版本", severity: "should_fix" },
  ];
}

export function defaultWorkers(options = {}) {
  const failingWorker = options.failingWorker ?? null;
  return {
    tool_worker: new DemoResearchWorker("tool_worker", { shouldFail: failingWorker === "tool_worker" }),
    memory_worker: new DemoResearchWorker("memory_worker", { shouldFail: failingWorker === "memory_worker" }),
    planning_worker: new DemoResearchWorker("planning_worker", { shouldFail: failingWorker === "planning_worker" }),
    multi_agent_worker: new DemoResearchWorker("multi_agent_worker", { shouldFail: failingWorker === "multi_agent_worker" }),
  };
}

export function defaultDimensions() {
  return [
    { name: "correctness", agent: "correctness_agent", focus: "逻辑错误、边界条件、异常处理、状态一致性", exclude: "不分析安全漏洞和性能瓶颈" },
    { name: "security", agent: "security_agent", focus: "注入风险、密钥泄露、权限越界、敏感数据暴露", exclude: "不分析普通逻辑错误和性能瓶颈" },
    { name: "performance", agent: "performance_agent", focus: "时间复杂度、I/O 瓶颈、索引和缓存策略", exclude: "不分析正确性和安全性影响" },
  ];
}

export function defaultSpecialists() {
  return {
    correctness_agent: new DemoSpecialistAgent("correctness"),
    security_agent: new DemoSpecialistAgent("security"),
    performance_agent: new DemoSpecialistAgent("performance"),
  };
}

function printReview(review) {
  console.log(`verdict: ${review.verdict}`);
  for (const check of review.checks) {
    console.log(`  ${check.checkId}: ${check.passed ? "PASS" : "FAIL"} - ${check.evidence}`);
  }
}

export function main() {
  const reviewerResult = new ReviewerPattern(new DemoExecutorAgent(), new DemoReviewerAgent(), { maxRounds: 2 }).run(
    "写一份 API 模块技术方案，并从安全角度审查",
    defaultCriteria()
  );
  console.log("\nReviewer 最终状态:", reviewerResult.status);

  const supervisorResult = new SupervisorPattern(new DemoSupervisorAgent(), defaultWorkers()).run(
    "调研 Agent 架构的四个主流方向"
  );
  console.log(supervisorResult.finalReport);

  const specialistsResult = new ParallelSpecialists(defaultSpecialists()).run("checkout.py 代码片段", defaultDimensions());
  for (const conflict of specialistsResult.conflicts) {
    console.log(`冲突: ${conflict.location} ${conflict.problemType} -> ${conflict.judgments.join(",")}`);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
