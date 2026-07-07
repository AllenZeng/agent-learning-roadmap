# Chapter 6: Reflection: A Feedback-Driven Decision Loop

[Back to Course 5](./course-05-01-scenario-enhancement.md) | [Previous Chapter](./course-05-05-planning.md) | [Next Chapter: Human-in-the-loop: When an Agent Should Not Decide Alone](./course-05-07-human-in-the-loop.md)

## Chapter Contents

- [6.1 The agent saw the error and kept going](#61-the-agent-saw-the-error-and-kept-going)
- [6.2 Self-Refine and Reflexion](#62-self-refine-and-reflexion)
- [6.3 Reflection needs feedback signals](#63-reflection-needs-feedback-signals)
- [6.4 Trigger, classify, decide, stop](#64-trigger-classify-decide-stop)
  - [6.4.1 Scenario: reflection requirements for a knowledge assistant](#641-scenario-reflection-requirements-for-a-knowledge-assistant)
  - [6.4.2 Trigger signals](#642-trigger-signals)
  - [6.4.3 Feedback classification](#643-feedback-classification)
  - [6.4.4 Handling strategies](#644-handling-strategies)
  - [6.4.5 Stop conditions](#645-stop-conditions)
  - [6.4.6 Summary: the core decisions in reflection](#646-summary-the-core-decisions-in-reflection)
- [6.5 When reflection is unnecessary](#65-when-reflection-is-unnecessary)
- [Runnable Example](#runnable-example)

---

## 6.1 The agent saw the error and kept going

Return to the knowledge assistant from 1.1. It now has Planning, so the four release-preparation steps are no longer skipped. But when it reaches the "run tests" step, the tool returns:

```text
TypeError: Cannot read properties of undefined (reading 'files')
```

The agent sees the error. Then what does it do? It continues writing the changelog and eventually reports: "Release preparation is complete."

This is not a tool problem. It is not a Planning problem. It is not a Memory problem. It is a more basic missing capability: **the agent does not have a closed loop for "see feedback signal -> stop the current path -> classify the signal -> decide the next step."** It treated the TypeError as just another observation, like file content that should be recorded, instead of a signal that required action.

Think of driving a car. A red warning light appears on the dashboard. A driver with reflection would pull over, inspect the situation, and decide whether to continue, slow down, fix the issue, or call roadside assistance. A driver without reflection, like a bare LLM loop, glances at the light, writes "14:32 red light appeared" into the log, and keeps driving at 120 km/h.

The same failure appears in knowledge QA. The agent writes, "According to Chapter 3 of Software Engineering Practice..." But when you check the source, that sentence is not in Chapter 3 at all. The agent has no citation-verification step. It is not retrieving a real citation; it is generating text that looks like a citation. The format is convincing, the page number is precise, and the source may still be imaginary.

The root issue is this: **the agent lacks a decision mechanism triggered by feedback signals.** It does not say, "Wait, the test failed. Should I retry, degrade gracefully, request authorization, hand this to a human, or stop?" It simply keeps generating the next token.

> **A common question: did Course 4 not already return tool errors to the model?**
>
> Yes. Course 4's tool-error mechanism converts tool execution failures, such as invalid parameters, timeouts, and permission errors, into structured `ToolResult` observations that are injected into the next model turn. But there is a crucial distinction: **tool errors solve "make the model see the error"; reflection solves "force the system to stop and decide what to do after seeing feedback."** The first is a passive information channel. The second is an active control loop.
>
> They sit at different layers of the system:
>
> - **The tool-error mechanism runs at the execution layer.** Its job is to make the failure of a single tool call structured and understandable. Once the model receives that error, the tool layer does not decide what happens next. The model can still treat `ToolResult(status="error", ...)` as normal text, store it in state, and continue with the next Planning step. That is exactly what happened when the agent saw the TypeError and continued writing the changelog. The signal was delivered, but no response was enforced.
> - **The reflection mechanism runs at the control layer.** Its job is to detect feedback signals in the runtime, interrupt the current task flow, and enter a loop of classify -> decide -> handle -> validate or stop. This is not the model's "introspection." It is an engineering mechanism in the runtime, with explicit trigger conditions and hard stop conditions.
>
> Back to the driving analogy: the tool-error mechanism is the red warning light on the dashboard. Reflection is the driver's response routine: "red light -> pull over -> inspect -> decide whether to continue, slow down, fix it, or call for help." The light can be on while the driver ignores it. That is the default behavior of a bare LLM, because an LLM is fundamentally a token generator. Its default action is "continue generating," not "stop and verify whether the previous step was correct." Reflection inserts a system-level control branch: `if signal -> stop and decide`.
>
> So reflection is not a model capability problem. It is a runtime engineering pattern. Course 4's tool-error mechanism and this chapter's reflection mechanism both live in the runtime, but they have different roles: **tool errors are signal sources; reflection is the response policy.** One reports the problem. The other catches it and decides what happens next.

## 6.2 Self-Refine and Reflexion

The idea that an LLM can "reflect on its own output" went through several important stages.

**March 2023: Self-Refine (Madaan et al.).** The paper proposed a simple and effective loop: generate -> give feedback -> revise. The same LLM performs each step. It first produces a draft, then critiques that draft, then revises based on the critique. This improves many tasks, including writing and code generation. But it has a major weakness: **the feedback comes entirely from the model itself, without an external validation signal.** A flawed first draft can lead the model to give itself feedback that sounds reasonable but points in the wrong direction.

**June 2023: Reflexion (Shinn et al.).** The key improvement was the introduction of **external validation signals**. The model no longer relies only on self-evaluation. It analyzes real execution results, such as failed tests, compiler errors, and API responses, to understand what went wrong. Reflexion turns "reflection" from a generation trick into an environment-feedback loop: try -> observe the real result -> analyze the failure -> store the lesson -> retry. This is more reliable than Self-Refine because it has an external anchor.

**From late 2023 onward, reflection moved from research idea to engineering practice.** The important shift is that reflection is no longer treated as "the model's ability to introspect." It is designed as a **runtime mechanism with trigger conditions and stop conditions**. What signals trigger the loop? Test failures, schema validation failures, user rejection. When should the loop stop? Maximum retries, cost limits, repeated identical feedback.

## 6.3 Reflection needs feedback signals

Reflection is often misunderstood as "ask the model to check its own work." That is like asking a student to grade their own exam. The student might check carefully, or they might tick every answer and hand it in. You cannot know which happened.

When a model says "I checked it," that sentence is still just generated text. It comes from the same mechanism that generated "the citation is from Chapter 3." **Self-evaluation and the original answer share the same source of hallucination.**

A better reflection loop relies on external feedback signals: from the system, from tools, or from users. It should not rely on the model's own judgment.

| Feedback signal | Knowledge-assistant example | Why it is more reliable than model self-evaluation |
|---|---|---|
| JSON Schema validation failure | The agent outputs `{"tool": "search"}`, but the schema requires `tool_name` | Schema validation is deterministic: a field exists or it does not; a type matches or it does not |
| Tool parameter error | `search_notes(query="", limit=500)` -> `Error: limit must be 1-100` | This is the tool's actual return value, not the model's guess about whether the parameters are valid |
| Unit test failure | After modifying `session_manager.py`, 3 of 10 tests fail assertions | The test framework provides expected and actual values; the result is reproducible |
| Citation verification failure | The agent claims "the notes say Memory has three guard layers," but the source text only contains two | The source text is objective evidence: the phrase is retrieved or it is not |
| User rejection | The user says, "No, I want a checklist, not a code review report" | The user knows their own intent; the model can only infer it |
| Permission failure | `cat /etc/shadow` -> `Permission denied` | The operating system returned the permission error; the model did not infer it |

In other words, reflection is not a fixed step where the system "reflects after every action." It is a **decision loop triggered by external signals**. No signal, no reflection. A signal arrives, the loop starts.

To design the loop, answer four questions. These are the backbone of section 6.4:

- When should reflection be triggered? -> 6.4.2 Trigger signals
- What evidence should reflection inspect? -> 6.4.3 Feedback classification
- What should the system do after a trigger? -> 6.4.4 Handling strategies
- When should the system stop? -> 6.4.5 Stop conditions

## 6.4 Trigger, classify, decide, stop

A controllable reflection mechanism can be split into four steps:

```text
Trigger signal
  -> feedback classification / evidence analysis
  -> choose handling strategy
  -> retry, degrade, hand off, or stop
```

Before going into each step, we need a concrete reference scenario.

### 6.4.1 Scenario: reflection requirements for a knowledge assistant

Return to the knowledge assistant from 1.1. It now has RAG, so it can search notes. It has Memory, so it can remember preferences. It has Planning, so it can organize multi-step tasks. But when it encounters failure, it still lacks a closed loop:

- **Code-analysis scenario:** The user gives the agent a piece of code and asks it to find bugs. The agent returns an analysis, but one of the API method names it cites does not exist. The model invented it. The agent does not notice that "this API does not exist."
- **Notes QA scenario:** The agent answers, "According to your notes, the Memory module implements three guard layers in `src/memory/write.py`." The user checks the file and finds only two. The agent has no reverse citation check. It generated text that looks like a path.
- **Release-preparation scenario:** The agent follows its planned release workflow. The test step fails with a TypeError. It records the error in state, then continues writing the changelog. It lacks the reflex arc: see feedback -> stop current path -> classify -> decide next step.

The reflection system has four design constraints:

- Triggers must come from external signals, such as failed tests, schema validation failures, or user rejection. They must not come from model self-evaluation.
- If the system chooses automatic handling, it must validate the result again. "I handled it" is not enough.
- There must be hard stop conditions: retry count, cost limit, repeated identical feedback.
- The handling process should be visible to the user but not noisy. The user should know "the agent detected a feedback signal and is handling it"; they do not need 200 lines of trace output.

With this scenario in mind, we can examine each part of the loop.

### 6.4.2 Trigger signals

Reflection is not "think again after every step." That wastes tokens and slows the system down. Triggering should be **passive and based on external signals**. If a signal arrives, trigger reflection. If no signal arrives, continue normally.

This sounds simple, but the implementation details matter. What counts as a signal? Does a TypeError printed to stdout count? Does a vague user message like "not quite right" count? What about a warning returned by a tool when the status is still success? There is no universal answer. It depends on your system, your tools, and your users.

Before answering those questions, build a classification framework for feedback signals: which channels can produce abnormal feedback, what action each feedback type should trigger, and, just as importantly, what the exceptions are.

The table below uses the knowledge assistant as the running example. Notice the "exceptions that should not trigger reflection" column. False positives are as dangerous as missed triggers.

| Trigger signal | Knowledge-assistant example | Handling action | Exception that should not trigger this path |
|---|---|---|---|
| Invalid output format | JSON is missing a required field; schema validation returns `required field 'tool_name' missing` | Regenerate the structured output and fill the missing field | The tool definition itself changed, such as a new API version; update the schema instead of regenerating |
| Tool parameter error | `search_notes(query="", limit=500)` returns `limit must be 1-100` | Fix the parameter, such as `limit=500` -> `limit=50`, then retry | The parameter is valid but rejected due to rate limiting; wait and retry instead of changing the parameter |
| Tool execution failure | `git log` returns `fatal: not a git repository` | Classify the feedback: this is an environment issue, not a parameter issue; skip the step and notify the user | A network timeout should usually be retried, not skipped |
| Test failure | `test_memory_cleanup` fails: expected `cleaned`, got `pending` | Locate the failing assertion, analyze the logic, fix the code, rerun tests | If the test database is not running, the environment is broken; do not modify application code |
| Citation mismatch | The agent says "Memory has three guard layers," but the source only has two | Retrieve the source again, compare it, correct the unsupported claim, and cite the real source | Empty retrieval may mean the note was deleted; tell the user instead of searching forever |
| User rejection | The user says, "No, I want a checklist, not a code review report" | Update the goal interpretation and regenerate output that matches the user's intent | If the user only says "not good enough" without direction, ask a clarifying question instead of guessing |
| Repeated failure | The same test fails three times with the same feedback | Stop, preserve the failure context, and request human intervention | - |

**Design principles for trigger signals:**

- **External first:** test failure > schema validation failure > tool error code > user rejection > model self-evaluation. Model self-evaluation should be a last resort, and only when there is a clear checkable standard, such as "the output must contain three items."
- **Signals must be specific:** "something went wrong" is not enough. "TypeError at line 42: cannot read 'files' of undefined" is useful. Specific feedback enables specific decisions.
- **Do not repeat the same trigger indefinitely:** if the same error has already gone through reflection, handling, validation, and failure twice, the third occurrence should not start the same handling path again. It should trigger stop-and-report.

Common failures at this stage are missed triggers and false triggers:

| Failure | Typical cause | Fix |
|---|---|---|
| The agent sees an error and continues | The trigger only checks for an `error` field, but the TypeError appeared in stdout | Watch multiple channels: exit code, stderr, exception patterns in output, and return-value schema validation |
| Normal output is treated as failure | The tool returns `{status: "ok", warnings: 3}`, and the system treats any warning as an error | Distinguish errors from warnings; warnings should not trigger reflection unless they accumulate or cross a configured threshold |
| Every step triggers reflection and latency explodes | A four-step release task adds "reflect after execution" to every step, causing 12 LLM calls | Trigger only on external feedback signals; normal steps should not enter reflection |
| User rejection is treated as a format error | The user says "this is wrong"; the system reruns JSON schema validation, passes it, and reports "format is correct" | User rejection is its own trigger. It should cause goal reinterpretation, not format revalidation |

### 6.4.3 Feedback classification

A trigger tells the system, "stop and inspect this." It does not tell the system whether to retry, fix, degrade, hand off, or stop. Before deciding the next step, the system must classify the feedback. Different feedback types require different handling strategies. If you treat a tool parameter error as a goal-understanding error, the agent will move further in the wrong direction.

A practical way to classify feedback is to ask three questions:

- **Is the root cause inside or outside the agent?** Hallucinated API names are internal. Network timeouts are external.
- **Can the system handle this automatically, or can it only skip/report?** Invalid parameters can often be fixed. Missing permissions usually require reporting or authorization.
- **What must change to handle it: prompt, tool, context, or control flow?** Changing the prompt will not fix the use of the wrong tool.

The table below applies these questions to common knowledge-assistant failures. Pay close attention to the boundaries between types. A wrong classification can be more harmful than no classification.

| Feedback type | Knowledge-assistant example | Recognition pattern | Handling strategy |
|---|---|---|---|
| Goal misunderstanding | The user says "check my code," but the agent returns a full code-review report with scoring and a template; the user rejects it | The output structure does not match the user's expected task; user says "that is not what I wanted" | Reinterpret the user's intent; ask for confirmation if needed |
| Missing context | The agent cites `memory.load()`, but that method does not exist; it remembered a similar API from another framework | Hallucinated references, nonexistent APIs, invented facts | Retrieve the actual API docs or source notes and replace the hallucinated content with grounded evidence |
| Wrong tool selection | The user asks about local notes on Memory, but the agent uses web search instead of local note search | The tool category is wrong; returned results come from the wrong knowledge domain | Select the tool based on task intent; annotate tools with clear usage scenarios |
| Tool parameter error | `search_notes(query="", limit=500)` -> `limit must be 1-100` | The tool returns a clear parameter-validation error | Fix the parameter; if rules are complex, declare them in the tool definition |
| External environment error | `git log` -> `fatal: not a git repository`; network timeout; disk full | The error comes from an external system; retry may not help | For unrecoverable errors, skip and notify; for recoverable errors such as timeouts, wait and retry |
| Output format error | JSON is missing required fields; a generated checklist is not Markdown | Schema validation fails; output structure violates the expected format | Regenerate structured output and strengthen format constraints in the prompt |
| Permission denied | `cat /etc/shadow` -> `Permission denied` | The OS or API returns a permission error | Do not retry blindly; request authorization or degrade to an allowed alternative |
| Insufficient result quality | The generated changelog has only 3 lines and covers 2 of 5 commits | Format passes, but content is incomplete; user says it is too shallow | Add content and strengthen acceptance criteria, such as "cover every feat and fix commit" |

**Classification is not a one-time decision.** If handling fails, classify again. The first classification may have been wrong, or the root cause may be upstream. For example, a "tool parameter error" may have been caused by a prior goal misunderstanding that led the agent to choose the wrong tool.

Common classification traps:

| Failure | Typical cause | Fix |
|---|---|---|
| Treating hallucination as a tool error | The agent cites a nonexistent API, classifies it as a tool parameter problem, and repeatedly changes parameters | First verify whether the referenced entity exists: API name, file path, function name. If not, classify as missing context and retrieve evidence |
| Treating environment failure as code failure | Tests fail because the database is not running, and the agent starts changing code | Separate external/uncontrollable failures from internal/fixable failures; do not edit code for broken environments |
| Classifying too broadly | Every failure becomes "tool execution failed" and receives the same "retry" action | At minimum, distinguish retryable, fixable, and unrecoverable failures |

### 6.4.4 Handling strategies

After classification, the system chooses a handling strategy. Handling does not always mean "fix the problem." It may mean changing the input, switching tools, adding context, waiting and retrying, degrading, requesting authorization, handing off to a human, or stopping. The key is not "try to make it work"; the key is **make the correct next control decision based on the feedback signal.**

Before looking at the strategies, understand three ways handling commonly fails:

- **Nothing actually changes.** The system regenerates with the same prompt. The only difference is randomness, so the same failure is likely.
- **The direction is wrong.** The system treats hallucination as a parameter problem and keeps changing search parameters, even though the entity does not exist.
- **The handling scope is too large.** A parameter is wrong, but the system changes the tool, prompt, and context together, introducing new variables and making the failure harder to diagnose.

Good handling is like traffic control: turn around when needed, slow down when needed, stop when needed. Not every case should be driven into the repair shop.

| Feedback type | Handling strategy | Knowledge-assistant action | How to validate afterward |
|---|---|---|---|
| Goal misunderstanding | Rewrite the prompt and add constraints | After user rejection, add: "Do not generate a code-review report format; output only issues and suggestions" | Ask the user to confirm the regenerated output |
| Missing context | Retrieve more evidence | Search notes for the real method name and replace the hallucinated API reference | Check each citation against the retrieved source text |
| Wrong tool selection | Switch tools | Replace web search with `search_local_notes` | Confirm that returned results come from the correct knowledge source |
| Tool parameter error | Adjust tool parameters | `limit=500` -> `limit=50`; `query=""` -> a meaningful query | Tool returns success and non-empty results |
| External environment error | Degrade if unrecoverable | If `git log` fails because the directory is not a Git repo, switch to manual commit-range input and notify the user | Not applicable; user takes over the missing environment input |
| Output format error | Regenerate with stronger format constraints | Add `Required fields: tool_name, args, reason` to the prompt | Schema validation passes |
| Permission denied | Request authorization or degrade | Ask the user for permission or propose an allowed alternative | Retry only after user authorization |
| Insufficient result quality | Add content and acceptance criteria | If changelog covers only 2 of 5 commits, require coverage of every `feat` and `fix` commit | Check acceptance criteria item by item |

**Design principles for handling strategies:**

- **Automatic fixes must change the input.** If the system only "tries again," the only new factor is randomness. A real fix changes the prompt, parameters, tool choice, context, or control flow.
- **The scope of the change should match the root cause.** Bad parameter? Change the parameter. Wrong tool? Switch tools. Permission denied? Request authorization or degrade. Over-handling introduces noise.
- **The handling strategy can fail.** If validation still fails after handling, do not keep patching the same strategy. Reclassify the feedback, or stop and request human intervention.

### 6.4.5 Stop conditions

Stop conditions are the safety valve of reflection. Without them, reflection is not "intelligent recovery"; it is a silent infinite loop. Stop conditions must be hard-coded. The model should not decide by itself that it is "probably enough."

| Stop condition | Suggested threshold | Behavior when triggered | Why it must be hard-coded |
|---|---|---|---|
| Maximum retries | 3 attempts for the same automatic handling path | Stop automatic handling, preserve the last failure, request human intervention | On the fourth or fifth attempt, the model may still say "this should work now" |
| Maximum cost | $1.00 total reflection cost for one task | Stop automatic handling and return the best current result | The model does not know how much money the loop has spent |
| Maximum elapsed time | 60 seconds from first reflection trigger | Stop automatic handling and return the last available result | The user is waiting; one failed test should not turn release preparation into a five-minute task |
| Same feedback repeated | 2 identical post-handling feedback messages | Stop with "the handling strategy did not change the failure; root-cause classification may be wrong" | Identical feedback means the strategy missed the root cause; continuing becomes random search |
| Feedback escalation | Recoverable feedback becomes unrecoverable, such as timeout -> disk full | Stop automatic handling and report that the environment has degraded | Escalation means the situation is becoming less safe for automatic action |
| Insufficient feedback signal | Validator only returns "failed" with no useful detail | Stop and request more detailed feedback | Otherwise the model will invent a plausible cause and act on a guess |

These stop conditions are connected by OR. If any one condition is met, stop. In practice, "same feedback repeated" often fires first, followed by maximum retries. Cost and time limits are usually fallback guards for extreme cases.

Common failures at this stage:

| Failure | Typical cause | Fix |
|---|---|---|
| The same feedback is handled five times | The strategy did not change the input, but each LLM output is slightly different, so the system thinks it is making progress | Compare strategy, prompt, parameters, and feedback; if the same input path produces the same feedback twice, change strategy or stop |
| Cost silently exceeds budget | Each reflection call costs $0.02, but a task triggers 15 reflection turns | Update a cumulative cost counter after every LLM call; hard-stop when the budget is exceeded |
| The model leads the process in the wrong direction | During "error analysis," the model invents a plausible but wrong cause, such as "maybe this is a time-zone issue" | Allow analysis to cite only concrete facts from external signals: error lines, error codes, return values |

The skeleton of a reflection loop looks like this. The critical points are: triggers come from external signals, and stop conditions are enforced by code.

```python
# Reflection loop: trigger only on external feedback, always enforce stop boundaries
def reflection_loop(
    action: callable,       # action to execute: generate code, answer a question, etc.
    validate: callable,     # external validator: run tests, check schema, verify citations
    max_retries: int = 3,   # hard upper bound
    cost_budget: float = 1.0  # cost limit in dollars
) -> dict:
    """Run an action with a reflection loop."""
    cost_spent = 0
    last_error = None

    for attempt in range(max_retries):
        # 1. Execute the action
        result = action(
            previous_error=last_error,  # inject the previous failure into context
            attempt=attempt
        )
        cost_spent += result.cost

        # 2. External validation, not model self-evaluation
        validation = validate(result.output)

        if validation.passed:
            return {"status": "success", "output": result.output,
                    "attempts": attempt + 1, "cost": cost_spent}

        # 3. Classify feedback and prepare the next handling context
        last_error = {
            "type": classify_feedback(validation),  # schema_error | test_failure | tool_error | ...
            "message": validation.message,
            "evidence": validation.evidence,      # concrete error line, cited source text, etc.
            "suggested_action": validation.suggestion
        }

        # 4. Check stop conditions
        if cost_spent > cost_budget:
            return {"status": "stopped", "reason": "cost_limit",
                    "last_error": last_error}
        if last_error["type"] == "same_error" and attempt >= 2:
            return {"status": "stopped", "reason": "repeated_failure",
                    "last_error": last_error}

    return {"status": "stopped", "reason": "max_retries_exceeded",
            "last_error": last_error}

# Example: code modification with test-driven reflection
result = reflection_loop(
    action=lambda prev_err, attempt: llm_generate_code(
        task="fix the bug in user_service.py",
        test_failure=prev_err["evidence"] if prev_err else None
    ),
    validate=lambda code: run_tests(code),  # external test framework, not the LLM
    max_retries=3
)
```

> **Design note:** `validate` must be an external validator: running tests, checking schemas, or comparing citations against source text. It must not be "ask the model to look again." `action` receives `previous_error` as a handling signal, but only factual evidence should be injected: error text, failing test name, expected and actual values. Do not inject the model's own self-evaluation as evidence.

### 6.4.6 Summary: the core decisions in reflection

| Stage | Core decision in the knowledge-assistant scenario | What failure looks like |
|---|---|---|
| Trigger signal (6.4.2) | Which external signals trigger reflection? What should the validator check? | TypeError is ignored as a normal observation; warnings falsely trigger reflection |
| Feedback classification (6.4.3) | What type of feedback is this? Is the category specific enough to guide handling? | Hallucination is treated as a tool parameter error; the agent keeps changing parameters for an API that does not exist |
| Handling strategy (6.4.4) | Should the next step be retry, fix, degrade, hand off, or stop? | The same prompt is rerun with only random variation; the handling scope is too broad and changes the tool unnecessarily |
| Stop conditions (6.4.5) | Where are the hard limits? How many repeated feedback events are allowed? | The same feedback is processed five times, and the system mistakes random output variation for progress |

Three themes run through the whole loop:

1. **Validation must be externalized.** The reliability of reflection depends on the reliability of the validator. If `validate()` means "ask the LLM to check itself," the loop is the model playing chess against itself while also acting as referee. Test frameworks, schema validators, source-text comparison, and user rejection are the external anchors that keep reflection from becoming self-deception.
2. **Classification comes before handling; root cause comes before symptoms.** Seeing "test failed" and immediately rerunning the task is not reflection. It is hope. Effective handling requires knowing why it failed: bad code logic or broken test environment? Nonexistent API or valid API with invalid parameters? One wrong classification can waste the entire recovery loop.
3. **Stop conditions are safety valves and must not be delegated to the model.** The model has no instinct for "it is time to stop." On the fifth attempt, it may still confidently say, "This should work now." Maximum retries, cost limits, and repeated-feedback detection must be hard-coded and enforced at runtime.

Return to the opening failure: the agent saw a TypeError and kept writing the changelog. In the knowledge-assistant scenario, this did not happen because the agent was "not smart enough." It happened because the system lacked a decision loop triggered by external feedback. Reflection is not "make the model reflect." It is **a runtime mechanism for detect feedback -> classify -> decide -> handle -> validate or stop**. Triggers come from external signals. Validators come from external systems. Stop conditions come from hard-coded boundaries. The model only proposes the next candidate action based on facts; it does not decide whether it should continue.

## 6.5 When reflection is unnecessary

Complex reflection is unnecessary in these cases:

- The output can be handled directly with deterministic rules.
- Failure cost is low, and a simple rerun is cheaper.
- There is no external feedback signal, so the model cannot know whether it is wrong.
- The task is highly latency-sensitive.
- The task is high-risk and requires human or rule-based verification; model self-evaluation is not a substitute.

A practical rule:

```text
If there is a clear feedback signal, and automatic handling costs less than failure, reflection is worth adding.
If you are only asking the model to "think again," it usually is not.
```

> **The story is not finished.** Reflection lets the agent choose a next step based on feedback. After a test failure, it can analyze the cause and choose retry, fix, degrade, or stop. But one stop condition is "request human intervention." When automatic handling no longer converges, human judgment becomes the final safety valve.
>
> "Request human intervention" sounds simple, but the design is full of traps. When should the agent ask, and when should it handle the issue itself? Ask too often, and users get annoyed. Ask too rarely, and users stop trusting the system. What information should the agent show so the user can make the right decision in three seconds? That is the next chapter's topic: Human-in-the-loop, and how to design the boundary between people and agents when the agent should not decide alone.
>
> Looking further ahead, there is an even deeper issue. Some tasks cannot be solved by "one human plus one agent." If you ask an agent to write a security plan and then ask the same agent to review it, it may say, "No obvious issues." A human reviewer may find three security risks immediately. Why? Because creators and reviewers need different perspectives, different context, and different evaluation standards. That is the final enhancement capability in this course: Multi-Agent. One agent writes; another watches.

---

## Runnable Example

After studying this chapter, run the local Reflection example for Course 5, section 05-06:

- [Course 5 05-06 Reflection Example](../examples/course-05-06-reflection/README.md)

The example uses the knowledge-assistant scenario and provides both Python and Node.js versions. It demonstrates four stages of reflection:

- V0: no reflection; observe the full process where the agent ignores feedback
- V1: schema validation failure -> regenerate
- V2: tool parameter error -> classify -> fix parameters -> retry
- V3: test failure -> locate the failing assertion -> fix code or stop

It also includes a complete reflection loop: trigger -> classify -> decide -> handle -> validate or stop. The example shows stop-condition behavior as well: repeated identical feedback -> hard stop.

The reflection loop in the example is a teaching implementation, not a production framework. `validate` uses deterministic functions to simulate external validators. Handling strategies are hard-coded by feedback type rather than generated dynamically by an LLM. Cost is simulated. But the core skeleton is complete: external signal triggers, feedback classification, handling strategies that change input or control flow, and hard-coded stop conditions. Those pieces remain the same in real systems.

```bash
# Python version
cd examples/course-05-06-reflection/python
python3 reflection_demo.py

# Node.js version
cd examples/course-05-06-reflection/nodejs
node reflection_demo.mjs
```

### Chapter Summary

Reflection is not "make the model think again." It is a runtime mechanism for "detect feedback -> classify -> decide -> handle -> validate or stop." Three ideas matter most:

**Validation must be externalized.** Reflection is only as reliable as its validator. If `validate()` means "ask the LLM to check itself," the whole loop is self-deception: the model is both player and referee. Tests, schemas, source-text comparison, and user rejection are the anchors that make the loop trustworthy. Model self-evaluation and the original answer share the same hallucination source.

**Classification comes before handling; root cause comes before symptoms.** Seeing "test failed" and running the same step again is not reflection. Effective handling requires knowing why the failure occurred: code logic or test environment, nonexistent API or bad API parameter. If automatic handling is used, it must change the input, such as prompt, parameter, tool choice, or context. If the system cannot fix the issue, it should degrade, hand off, or stop.

**Stop conditions are safety valves and cannot be left to the model.** The model has no built-in sense of "time to stop." It may confidently claim the fifth attempt will work. Maximum retries, repeated-feedback limits, and cost ceilings must be hard-coded and enforced at runtime. Stop conditions are OR conditions: if any one is met, stop. A reflection loop without stop conditions is more dangerous than no reflection loop at all.

---
