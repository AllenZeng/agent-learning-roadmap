import test from "node:test";
import assert from "node:assert/strict";

import {
  DemoExecutorAgent,
  DemoReviewerAgent,
  ReviewerPattern,
  countAgentDifferences,
  defaultCriteria,
} from "../multi_agent_demo.mjs";

test("agent configs have at least two real differences", () => {
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

  assert.equal(differences.total, 4);
  assert.equal(differences.inputs, true);
  assert.equal(differences.tools, true);
  assert.equal(differences.goal, true);
  assert.equal(differences.acceptance, true);
});

test("reviewer finds specific issues before executor fixes them", () => {
  const executor = new DemoExecutorAgent();
  const reviewer = new DemoReviewerAgent();
  const pattern = new ReviewerPattern(executor, reviewer, { maxRounds: 2 });

  const result = pattern.run("写一份 API 模块技术方案", defaultCriteria(), { verbose: false });

  assert.equal(result.status, "approved");
  assert.equal(result.reviewRounds, 2);
  assert.match(result.output, /max_length: 256/);
  assert.match(result.output, /\$\{API_KEY\}/);
  assert.equal(result.reviewTrace[0].issues.length, 4);
  assert.equal(result.reviewTrace[0].issues[0].location, "api_schema.yaml:12");
  assert.equal(result.reviewTrace[1].verdict, "approved");
});

test("reviewer never receives executor private trace", () => {
  const executor = new DemoExecutorAgent();
  const reviewer = new DemoReviewerAgent();
  const pattern = new ReviewerPattern(executor, reviewer, { maxRounds: 2 });

  pattern.run("写一份 API 模块技术方案", defaultCriteria(), { verbose: false });

  assert.deepEqual(reviewer.seenPrivateTraces, []);
  assert.equal(reviewer.reviewRequests[0].executorPrivateTrace, null);
});

test("unresolved issues stop as disputed after max rounds", () => {
  const executor = new DemoExecutorAgent({ fixableIssueIds: new Set(["C1"]) });
  const reviewer = new DemoReviewerAgent();
  const pattern = new ReviewerPattern(executor, reviewer, { maxRounds: 2 });

  const result = pattern.run("写一份 API 模块技术方案", defaultCriteria(), { verbose: false });

  assert.equal(result.status, "disputed");
  assert.equal(result.reviewRounds, 2);
  assert.deepEqual(
    result.unresolvedIssues.map((issue) => issue.id),
    ["C2", "C3", "C4"]
  );
  assert.equal(result.reason, "max_review_rounds");
});
