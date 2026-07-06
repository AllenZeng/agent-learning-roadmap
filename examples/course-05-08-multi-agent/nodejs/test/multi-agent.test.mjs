import test from "node:test";
import assert from "node:assert/strict";

import {
  DemoExecutorAgent,
  DemoReviewerAgent,
  DemoSupervisorAgent,
  MockLLM,
  ParallelSpecialists,
  ReviewerPattern,
  SupervisorPattern,
  countAgentDifferences,
  defaultAgentPrompts,
  defaultCriteria,
  defaultDimensions,
  defaultSpecialists,
  defaultWorkers,
} from "../multi_agent_demo.mjs";

test("default agent prompts define roles and response contracts", () => {
  const prompts = defaultAgentPrompts();

  assert.match(prompts.executor.systemPrompt, /Executor Agent/);
  assert.match(prompts.reviewer.systemPrompt, /Reviewer Agent/);
  assert.match(prompts.reviewer.responseContract, /ReviewResponse/);
  assert.deepEqual(prompts.reviewer.mustNot.includes("Do not read Executor private_trace"), true);
});

test("agent configs have at least two real differences", () => {
  const executor = {
    name: "Executor",
    inputs: new Set(["requirement", "retrieved_notes", "draft_trace"]),
    tools: new Set(["search_notes", "write_file"]),
    goal: "Complete the technical plan",
    acceptance: "The plan covers business requirements",
  };
  const reviewer = {
    name: "Reviewer",
    inputs: new Set(["final_artifact", "security_criteria"]),
    tools: new Set(["read_file", "run_checklist"]),
    goal: "Find security issues",
    acceptance: "The review checklist passes item by item",
  };

  const differences = countAgentDifferences(executor, reviewer);

  assert.equal(differences.total, 4);
  assert.equal(differences.inputs, true);
  assert.equal(differences.tools, true);
  assert.equal(differences.goal, true);
  assert.equal(differences.acceptance, true);
});

test("reviewer finds specific issues before executor fixes them", () => {
  const result = new ReviewerPattern(new DemoExecutorAgent(), new DemoReviewerAgent(), { maxRounds: 2 }).run(
    "Write a technical plan for the API module",
    defaultCriteria(),
    { verbose: false }
  );

  assert.equal(result.status, "approved");
  assert.equal(result.reviewRounds, 2);
  assert.match(result.output, /max_length: 256/);
  assert.match(result.output, /\$\{API_KEY\}/);
  assert.equal(result.reviewTrace[0].issues.length, 4);
  assert.equal(result.reviewTrace[0].issues[0].location, "api_schema.yaml:12");
  assert.equal(result.reviewTrace[1].verdict, "approved");
});

test("reviewer pattern records mock llm calls with role prompts", () => {
  const llm = new MockLLM();
  const result = new ReviewerPattern(
    new DemoExecutorAgent({ llm }),
    new DemoReviewerAgent({ llm }),
    { maxRounds: 2 }
  ).run("Write a technical plan for the API module", defaultCriteria(), { verbose: false });

  assert.equal(result.status, "approved");
  assert.deepEqual(
    llm.calls.map((call) => call.agent),
    ["executor", "reviewer", "executor", "reviewer"]
  );
  assert.match(llm.calls[0].systemPrompt, /Executor Agent/);
  assert.match(llm.calls[1].systemPrompt, /Reviewer Agent/);
  assert.equal(Object.hasOwn(llm.calls[1].userPayload, "privateTrace"), false);
});

test("reviewer never receives executor private trace", () => {
  const reviewer = new DemoReviewerAgent();
  new ReviewerPattern(new DemoExecutorAgent(), reviewer, { maxRounds: 2 }).run(
    "Write a technical plan for the API module",
    defaultCriteria(),
    { verbose: false }
  );

  assert.deepEqual(reviewer.seenPrivateTraces, []);
  assert.equal(reviewer.reviewRequests[0].executorPrivateTrace, null);
});

test("unresolved issues stop as disputed after max rounds", () => {
  const result = new ReviewerPattern(
    new DemoExecutorAgent({ fixableIssueIds: new Set(["C1"]) }),
    new DemoReviewerAgent(),
    { maxRounds: 2 }
  ).run("Write a technical plan for the API module", defaultCriteria(), { verbose: false });

  assert.equal(result.status, "disputed");
  assert.equal(result.reviewRounds, 2);
  assert.deepEqual(
    result.unresolvedIssues.map((issue) => issue.id),
    ["C2", "C3", "C4"]
  );
  assert.equal(result.reason, "max_review_rounds");
});

test("supervisor decomposes into bounded subtasks with excludes", () => {
  const result = new SupervisorPattern(new DemoSupervisorAgent(), defaultWorkers()).run(
    "Research four mainstream directions in Agent architecture",
    { verbose: false }
  );

  assert.equal(result.status, "complete");
  assert.equal(result.plan.subtasks.length, 4);
  assert.equal(result.plan.subtasks.every((subtask) => subtask.exclude.length > 0), true);
  assert.equal(
    result.plan.subtasks.every((subtask) => subtask.outputFields.join(",") === "key_findings,risks,recommendations"),
    true
  );
  assert.match(result.finalReport, /## Tool Use/);
  assert.match(result.finalReport, /## Multi-Agent/);
});

test("supervisor marks worker failure as missing instead of hiding it", () => {
  const result = new SupervisorPattern(
    new DemoSupervisorAgent(),
    defaultWorkers({ failingWorker: "memory_worker" })
  ).run("Research four mainstream directions in Agent architecture", { verbose: false });

  assert.equal(result.status, "partial");
  assert.deepEqual(result.missingTopics, ["Memory"]);
  assert.match(result.finalReport, /missing data: worker_timeout/);
});

test("parallel specialists deduplicate same location and problem type", () => {
  const result = new ParallelSpecialists(defaultSpecialists()).run(
    "checkout.py code snippet",
    defaultDimensions(),
    { verbose: false }
  );

  const amountFindings = result.findings.filter(
    (finding) => finding.location === "checkout.py:18" && finding.problemType === "missing_validation"
  );
  assert.equal(amountFindings.length, 1);
  assert.deepEqual(amountFindings[0].dimensions, ["correctness", "security"]);
  assert.equal(amountFindings[0].severity, "must_fix");
});

test("parallel specialists preserve conflicts for human review", () => {
  const result = new ParallelSpecialists(defaultSpecialists()).run(
    "checkout.py code snippet",
    defaultDimensions(),
    { verbose: false }
  );

  assert.equal(result.conflicts.length, 1);
  assert.equal(result.conflicts[0].location, "checkout.py:55");
  assert.equal(result.conflicts[0].problemType, "idempotency");
  assert.deepEqual(result.conflicts[0].judgments, ["problem", "safe"]);
  assert.deepEqual(result.dimensionSummary, { correctness: 2, security: 3, performance: 2 });
});
