#!/usr/bin/env node
/**
 * Course 05-08 Multi-Agent example
 *
 * The same offline example project demonstrates three collaboration patterns:
 * 1. Reviewer: one Agent writes a proposal while another independently reviews it
 * 2. Supervisor: one Supervisor decomposes the task while multiple Workers produce structured results
 * 3. Parallel Specialists: multiple specialists inspect the same input and analyze it in parallel from different dimensions
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

export class MockLLM {
  constructor() {
    this.calls = [];
  }

  complete(prompt, userPayload) {
    this.calls.push({
      agent: prompt.name,
      systemPrompt: prompt.systemPrompt,
      userPayload,
      responseContract: prompt.responseContract,
    });
    if (prompt.name === "executor") {
      const fixed = new Set(userPayload.appliedIssueIds ?? []);
      return {
        output: renderApiPlan(fixed),
        privateTrace: "For the local demo, first use a plaintext key; simplify the permission model to admin;dependency versions are not pinned yet and will be completed later.",
      };
    }
    if (prompt.name === "reviewer") {
      return { review: buildReviewResponse(userPayload.criteria, userPayload.artifact) };
    }
    if (prompt.name === "supervisor") return { note: "decompose_or_synthesize" };
    if (prompt.name.endsWith("_worker") || prompt.name.endsWith("_agent")) return { note: "specialized_analysis" };
    return { note: "mock_response" };
  }
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
    this.llm = options.llm ?? new MockLLM();
    this.prompt = options.prompt ?? defaultAgentPrompts().executor;
    this.revisions = [];
  }

  run(task, options = {}) {
    const applied = this.applicableIssueIds(options.fixInstructions ?? []);
    this.revisions.push([...applied].sort());
    return this.llm.complete(this.prompt, {
      task,
      fixInstructions: options.fixInstructions ?? [],
      appliedIssueIds: [...applied].sort(),
    });
  }

  applicableIssueIds(issues) {
    const issueIds = new Set(issues.map((issue) => issue.id));
    if (!this.fixableIssueIds) return issueIds;
    return new Set([...issueIds].filter((id) => this.fixableIssueIds.has(id)));
  }

}

export class DemoReviewerAgent {
  constructor(options = {}) {
    this.llm = options.llm ?? new MockLLM();
    this.prompt = options.prompt ?? defaultAgentPrompts().reviewer;
    this.reviewRequests = [];
    this.seenPrivateTraces = [];
  }

  run(request) {
    this.reviewRequests.push(request);
    if (request.executorPrivateTrace) this.seenPrivateTraces.push(request.executorPrivateTrace);

    const response = this.llm.complete(this.prompt, {
      originalRequirement: request.originalRequirement,
      artifact: request.artifact,
      criteria: request.criteria,
    });
    return response.review;
  }

  check(item, artifact) {
    return checkItem(item, artifact);
  }

  description(checkId) {
    return issueDescription(checkId);
  }

  location(checkId) {
    return issueLocation(checkId);
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
        if (verbose) console.log("[Runtime] Only concrete issues are sent back to the Executor, not subjective judgments.");
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
  constructor(options = {}) {
    this.llm = options.llm ?? new MockLLM();
    this.prompt = options.prompt ?? defaultAgentPrompts().supervisor;
  }

  decompose(task) {
    this.llm.complete(this.prompt, { operation: "decompose", task });
    const outputFields = ["key_findings", "risks", "recommendations"];
    return {
      subtasks: [
        { id: "T1", topic: "Tool Use", worker: "tool_worker", scope: "tool-calling path, failure modes, permission boundaries", exclude: "do not analyze tool collaboration inside Memory or Multi-Agent systems", outputFields },
        { id: "T2", topic: "Memory", worker: "memory_worker", scope: "engineering tradeoffs among short-term memory, long-term memory, and retrieval memory", exclude: "do not analyze pure RAG retrieval-ranking details", outputFields },
        { id: "T3", topic: "Planning", worker: "planning_worker", scope: "plan-and-execute, dynamic replanning, stopping conditions", exclude: "do not analyze Multi-Agent dispatch strategies", outputFields },
        { id: "T4", topic: "Multi-Agent", worker: "multi_agent_worker", scope: "collaboration boundaries of Reviewer, Supervisor, and Parallel Specialists", exclude: "do not repeat single-Agent Tool Use mechanics", outputFields },
      ],
    };
  }

  synthesize(task, plan, results) {
    this.llm.complete(this.prompt, { operation: "synthesize", task, resultCount: results.length });
    const missingTopics = results.filter((result) => result.status !== "ok").map((result) => result.topic);
    const lines = [`# Summary report: ${task}`, ""];
    const seenFindings = new Set();
    for (const result of results) {
      lines.push(`## ${result.topic}`);
      if (result.status !== "ok") {
        lines.push(`- missing data: ${result.missingReason}`);
        lines.push("");
        continue;
      }
      for (const finding of result.findings) {
        if (!seenFindings.has(finding)) {
          lines.push(`- Finding: ${finding}`);
          seenFindings.add(finding);
        }
      }
      for (const risk of result.risks) lines.push(`- Risks: ${risk}`);
      for (const recommendation of result.recommendations) lines.push(`- Recommendations: ${recommendation}`);
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
    this.llm = options.llm ?? new MockLLM();
    this.prompt = options.prompt ?? defaultAgentPrompts()[name] ?? defaultAgentPrompts().research_worker;
    this.receivedSubtasks = [];
  }

  execute(subtask) {
    this.receivedSubtasks.push(subtask);
    this.llm.complete(this.prompt, { subtask });
    if (this.shouldFail) {
      return { subtaskId: subtask.id, worker: this.name, topic: subtask.topic, status: "failed", findings: [], risks: [], recommendations: [], missingReason: "worker_timeout" };
    }
    const library = {
      "Tool Use": [
        ["Tool allowlists are more reliable than prompt constraints", "Tool results must enter traceable observations"],
        ["Giving read and write tools to the same Agent amplifies misuse risk"],
        ["Register the minimal tool set per Agent and record tool_call_id"],
      ],
      Memory: [
        ["Long-term memory should go through retrieval and summarization before being inserted into context, not be inserted wholesale", "Memory writes need explicit trigger conditions"],
        ["Store user facts, task state, and preferences in separate stores"],
        ["Move Writetext"],
      ],
      Planning: [
        ["Plans need verifiable checkpoints, not just a natural-language list", "Dynamic replanning must have stopping conditions"],
        ["textcostexceed benefits"],
        ["Design plan items as executable and acceptable small steps"],
      ],
      "Multi-Agent": [
        ["Decomposition value comes from real differences in input, tools, goals, and acceptance criteria", "The merge stage must preserve conflicts and missing data instead of smoothing them over"],
        ["free-form conversational communication can make boundaries drift"],
        ["Start with Reviewer mode first, then expand to Supervisor or multiple specialists"],
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
  constructor(dimension, options = {}) {
    this.dimension = dimension;
    this.llm = options.llm ?? new MockLLM();
    this.prompt = options.prompt ?? defaultAgentPrompts()[`${dimension}_agent`] ?? defaultAgentPrompts().specialist_agent;
  }

  analyze(artifact, dimension) {
    this.llm.complete(this.prompt, { artifact, dimension });
    const findings = {
      correctness: [
        { id: "F1", dimension: "correctness", location: "checkout.py:18", problemType: "missing_validation", judgment: "problem", evidence: "amount can be negative", severity: "must_fix" },
        { id: "F2", dimension: "correctness", location: "checkout.py:33", problemType: "state_consistency", judgment: "problem", evidence: "there is no transaction boundary between inventory deduction and order creation", severity: "must_fix" },
      ],
      security: [
        { id: "F3", dimension: "security", location: "checkout.py:18", problemType: "missing_validation", judgment: "problem", evidence: "unvalidated amount may bypass limit rules", severity: "must_fix" },
        { id: "F4", dimension: "security", location: "checkout.py:41", problemType: "credential_exposure", judgment: "problem", evidence: "logs print payment_token", severity: "must_fix" },
        { id: "F5", dimension: "security", location: "checkout.py:55", problemType: "idempotency", judgment: "safe", evidence: "idempotency keys are generated server-side and the expiration window is reasonable", severity: "info" },
      ],
      performance: [
        { id: "F6", dimension: "performance", location: "checkout.py:27", problemType: "n_plus_one_query", judgment: "problem", evidence: "loop queries coupons one by one", severity: "should_fix" },
        { id: "F7", dimension: "performance", location: "checkout.py:55", problemType: "idempotency", judgment: "problem", evidence: "idempotency records lack an index and will slow writes during order peaks", severity: "should_fix" },
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

export function defaultAgentPrompts() {
  return {
    executor: {
      name: "executor",
      role: "proposal executor",
      systemPrompt: "You are the Executor Agent. Your job is to produce a deliverable plan based on the user's requirements,process only structured issues returned by the Reviewer, and do not read the Reviewer's private reasoning.",
      responseContract: "Return {output: markdown, privateTrace: string}",
      mustNot: ["do not declare the review passed by yourself", "do not write unverified assumptions as facts"],
    },
    reviewer: {
      name: "reviewer",
      role: "independent reviewer",
      systemPrompt: "You are the Reviewer Agent. Your job is to review only the final artifact and checklist,and provide pass/fail, evidence, severity, and actionable recommendations for each item.",
      responseContract: "Return ReviewResponse: {verdict, checks[], issues[]}",
      mustNot: ["Do not read Executor private_trace", "do not modify the artifact itself"],
    },
    supervisor: {
      name: "supervisor",
      role: "task orchestrator",
      systemPrompt: "You are the Supervisor Agent. Your job is to decompose tasks and define scope/exclude for each subtask,and preserve missing data and conflicts during summarization.",
      responseContract: "Return SupervisorPlan or SupervisorResult",
      mustNot: ["do not do specialist research for Workers", "do not hide failed Workers"],
    },
    research_worker: {
      name: "research_worker",
      role: "topic research Worker",
      systemPrompt: "You are a Research Worker. You only process your assigned topic and return structured fields for key_findings, risks,and recommendations.",
      responseContract: "Return WorkerResult",
      mustNot: ["do not analyze areas excluded by exclude", "do not output free-form prose"],
    },
    specialist_agent: {
      name: "specialist_agent",
      role: "single-dimension specialist",
      systemPrompt: "You are a Specialist Agent. Analyze the same input only from the specified dimension and output mergeable findings,do not make final judgments for other dimensions.",
      responseContract: "Return SpecialistResult",
      mustNot: ["do not automatically resolve cross-dimension conflicts", "do not expand beyond the focus dimension"],
    },
    tool_worker: {
      name: "tool_worker",
      role: "Tool Use topic Worker",
      systemPrompt: "You only study the tool-calling path, failure modes, and permission boundaries.",
      responseContract: "Return WorkerResult",
      mustNot: ["do notanalysis Memory text Multi-Agent mediumtext"],
    },
    memory_worker: {
      name: "memory_worker",
      role: "Memory topic Worker",
      systemPrompt: "You only study engineering tradeoffs among short-term memory, long-term memory, and retrieval memory.",
      responseContract: "Return WorkerResult",
      mustNot: ["do notanalysistext RAG text"],
    },
    planning_worker: {
      name: "planning_worker",
      role: "Planning topic Worker",
      systemPrompt: "You only study plan-and-execute, dynamic replanning, and stopping conditions.",
      responseContract: "Return WorkerResult",
      mustNot: ["do notanalysismany Agent text"],
    },
    multi_agent_worker: {
      name: "multi_agent_worker",
      role: "Multi-Agent topic Worker",
      systemPrompt: "You only study collaboration boundaries of Reviewer, Supervisor, and Parallel Specialists.",
      responseContract: "Return WorkerResult",
      mustNot: ["do nottext Agent Tool Use text"],
    },
    correctness_agent: {
      name: "correctness_agent",
      role: "correctness specialist",
      systemPrompt: "You only check logic errors, boundary conditions, exception handling, and state consistency.",
      responseContract: "Return SpecialistResult",
      mustNot: ["do not analyze security vulnerabilities or performance bottlenecks"],
    },
    security_agent: {
      name: "security_agent",
      role: "security specialist",
      systemPrompt: "You only check injection risks, secret leakage, permission boundary violations, and sensitive data exposure.",
      responseContract: "Return SpecialistResult",
      mustNot: ["do not analyze ordinary logic errors or performance bottlenecks"],
    },
    performance_agent: {
      name: "performance_agent",
      role: "performance specialist",
      systemPrompt: "You only check time complexity, I/O bottlenecks, indexes, and caching strategy.",
      responseContract: "Return SpecialistResult",
      mustNot: ["do not analyze correctness or security impact"],
    },
  };
}

function renderApiPlan(fixed) {
  const apiLine = fixed.has("C1") ? "12: input: string, max_length: 256" : "12: input: string";
  const configLine = fixed.has("C2") ? '8: api_key: "${API_KEY}"' : '8: api_key: "sk-demo-plaintext"';
  const permissionLine = fixed.has("C3") ? "3-5: roles: reader, writer, admin" : "3-5: roles: admin";
  const dependencyLine = fixed.has("C4") ? "requirements.txt: fastapi==0.111.0" : "requirements.txt: fastapi>=0.111";
  return [
    "# API Module Technical Plan",
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

function buildReviewResponse(criteria, artifact) {
  const checks = [];
  const issues = [];
  for (const item of criteria) {
    const result = checkItem(item, artifact);
    checks.push(result);
    if (!result.passed) {
      issues.push({
        id: item.id,
        description: issueDescription(item.id),
        location: issueLocation(item.id),
        severity: item.severity,
        suggestion: result.suggestion ?? "Fill missing constraints according to review items",
      });
    }
  }
  return { verdict: issues.length === 0 ? "approved" : "rejected", checks, issues };
}

function checkItem(item, artifact) {
  if (item.id === "C1") {
    const passed = artifact.includes("max_length: 256");
    return {
      checkId: item.id,
      passed,
      evidence: passed ? "api_schema.yaml:12 contains max_length" : "api_schema.yaml:12 Missing max_length",
      suggestion: passed ? null : "Add max_length: 256 to the input parameter",
    };
  }
  if (item.id === "C2") {
    const passed = artifact.includes("${API_KEY}") && !artifact.includes("sk-demo-plaintext");
    return {
      checkId: item.id,
      passed,
      evidence: passed ? "config.yaml:8 uses environment variables" : "config.yaml:8 contains plaintext api_key",
      suggestion: passed ? null : "Use the ${API_KEY} environment variable",
    };
  }
  if (item.id === "C3") {
    const passed = artifact.includes("reader, writer, admin");
    return {
      checkId: item.id,
      passed,
      evidence: passed ? "permissions.py:3-5 distinguishes reader/writer/admin" : "permissions.py:3-5 only has the admin role",
      suggestion: passed ? null : "Split reader and writer roles",
    };
  }
  if (item.id === "C4") {
    const passed = artifact.includes("fastapi==0.111.0");
    return {
      checkId: item.id,
      passed,
      evidence: passed ? "requirements.txt uses == pinned versions" : "requirements.txt uses >=, versions are not pinned",
      suggestion: passed ? null : "Use == to pin dependency versions",
    };
  }
  return { checkId: item.id, passed: false, evidence: "not_found", suggestion: "Add verifiable evidence" };
}

function issueDescription(checkId) {
  return {
    C1: "/api/data MissingInput length limit",
    C2: "API key stored in plaintext",
    C3: "Permission model is missing read/write separation",
    C4: "Third-party dependencies are not pinned",
  }[checkId] ?? "Unknown review item failed";
}

function issueLocation(checkId) {
  return {
    C1: "api_schema.yaml:12",
    C2: "config.yaml:8",
    C3: "permissions.py:3-5",
    C4: "requirements.txt",
  }[checkId] ?? "unknown";
}

export function defaultCriteria() {
  return [
    { id: "C1", check: "Input length limit", howToVerify: "Check whether the input parameter of /api/data declares max_length", severity: "must_fix" },
    { id: "C2", check: "secret management", howToVerify: "Check whether the config example uses environment variables instead of plaintext keys", severity: "must_fix" },
    { id: "C3", check: "permission model", howToVerify: "Check whether reader and writer roles are separated", severity: "must_fix" },
    { id: "C4", check: "dependency pinning", howToVerify: "Check whether dependencies use == pinned versions", severity: "should_fix" },
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
    { name: "correctness", agent: "correctness_agent", focus: "logic errors, boundary conditions, exception handling, state consistency", exclude: "textanalysistext" },
    { name: "security", agent: "security_agent", focus: "injection risks, secret leakage, permission boundary violations, sensitive data exposure", exclude: "textanalysistexterrortext" },
    { name: "performance", agent: "performance_agent", focus: "time complexity, I/O bottlenecks, indexes, caching strategy", exclude: "textanalysistext" },
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
    "Write a technical plan for the API module，and review it from a security perspective",
    defaultCriteria()
  );
  console.log("\nReviewer final status:", reviewerResult.status);

  const supervisorResult = new SupervisorPattern(new DemoSupervisorAgent(), defaultWorkers()).run(
    "Research four mainstream directions in Agent architecture"
  );
  console.log(supervisorResult.finalReport);

  const specialistsResult = new ParallelSpecialists(defaultSpecialists()).run("checkout.py code snippet", defaultDimensions());
  for (const conflict of specialistsResult.conflicts) {
    console.log(`Conflict: ${conflict.location} ${conflict.problemType} -> ${conflict.judgments.join(",")}`);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
