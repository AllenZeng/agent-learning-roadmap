#!/usr/bin/env node
/**
 * 课程五 05-08 Multi-Agent 示例
 *
 * 用法：
 *   node multi_agent_demo.mjs
 *   node --test test/multi-agent.test.mjs
 */

export function countAgentDifferences(left, right) {
  const differences = {
    inputs: !sameSet(left.inputs, right.inputs),
    tools: !sameSet(left.tools, right.tools),
    goal: left.goal !== right.goal,
    acceptance: left.acceptance !== right.acceptance,
  };
  return {
    ...differences,
    total: Object.values(differences).filter(Boolean).length,
  };
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
    const fixInstructions = options.fixInstructions ?? [];
    const applied = this.applicableIssueIds(fixInstructions);
    this.revisions.push([...applied].sort());
    return {
      output: this.renderArtifact(applied),
      privateTrace:
        "为了本地演示先用明文 key；权限模型先简化成 admin；依赖版本先不锁定，后续再补。",
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
    if (request.executorPrivateTrace) {
      this.seenPrivateTraces.push(request.executorPrivateTrace);
    }

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

    return {
      verdict: issues.length === 0 ? "approved" : "rejected",
      checks,
      issues,
    };
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
    return {
      checkId: item.id,
      passed: false,
      evidence: "not_found",
      suggestion: "补充可验证证据",
    };
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
      if (verbose) console.log(`\n[Round ${roundIndex + 1}] Reviewer 开始审查`);

      const review = this.reviewer.run({
        originalRequirement: task,
        artifact: draft.output,
        criteria,
        executorPrivateTrace: null,
      });
      reviewTrace.push(review);

      if (verbose) printReview(review);

      if (review.verdict === "approved") {
        return {
          status: "approved",
          output: draft.output,
          reviewRounds: roundIndex + 1,
          reviewTrace,
          unresolvedIssues: [],
          reason: "",
        };
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

export function defaultCriteria() {
  return [
    {
      id: "C1",
      check: "输入长度限制",
      howToVerify: "检查 /api/data 的 input 参数是否声明 max_length",
      severity: "must_fix",
    },
    {
      id: "C2",
      check: "密钥管理",
      howToVerify: "检查配置示例是否使用环境变量而不是明文 key",
      severity: "must_fix",
    },
    {
      id: "C3",
      check: "权限模型",
      howToVerify: "检查是否区分 reader 和 writer 角色",
      severity: "must_fix",
    },
    {
      id: "C4",
      check: "依赖锁定",
      howToVerify: "检查依赖是否使用 == 锁定版本",
      severity: "should_fix",
    },
  ];
}

function printReview(review) {
  console.log(`verdict: ${review.verdict}`);
  for (const check of review.checks) {
    const status = check.passed ? "PASS" : "FAIL";
    console.log(`  ${check.checkId}: ${status} - ${check.evidence}`);
  }
  if (review.issues.length > 0) {
    console.log("issues:");
    for (const issue of review.issues) {
      console.log(`  - ${issue.id} ${issue.location}: ${issue.description}`);
    }
  }
}

function printConfigDifferenceDemo() {
  const executor = {
    name: "Executor",
    inputs: new Set(["requirement", "retrieved_notes", "draft_trace"]),
    tools: new Set(["search_notes", "write_file"]),
    goal: "完成技术方案",
    acceptance: "方案覆盖业务需求",
  };
  const reviewer = {
    name: "Reviewer",
    inputs: new Set(["final_artifact", "security_criteria"]),
    tools: new Set(["read_file", "run_checklist"]),
    goal: "找出安全问题",
    acceptance: "审查清单逐条通过",
  };
  const differences = countAgentDifferences(executor, reviewer);
  console.log("四个不同检查:");
  for (const key of ["inputs", "tools", "goal", "acceptance"]) {
    console.log(`  ${key}: ${differences[key] ? "different" : "same"}`);
  }
  console.log(`  total: ${differences.total}`);
}

export function main() {
  printConfigDifferenceDemo();
  const pattern = new ReviewerPattern(new DemoExecutorAgent(), new DemoReviewerAgent(), { maxRounds: 2 });
  const result = pattern.run("写一份 API 模块技术方案，并从安全角度审查", defaultCriteria());

  console.log("\n最终状态:", result.status);
  console.log("审查轮次:", result.reviewRounds);
  if (result.status === "approved") {
    console.log(`\n最终产物:\n${result.output}`);
  } else {
    console.log("未解决问题:", result.unresolvedIssues.map((issue) => issue.id));
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
