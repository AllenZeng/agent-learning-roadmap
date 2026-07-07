# Chapter 6: Reflection: A closed loop for feedback-based decision-making

[Return Course Five Document](./course-05-01-scenario-enhancement.md) | [Previous Chapter](./course-05-05-planning.md) | [Next chapter: Human-in-the-loop - when Agent should not decide for himself](./course-05-07-human-in-the-loop.md)

## Table of contents of this chapter

- [6.1 Wrong, but keep going down.](#61-wrong-but-keep-going-down)
- [6.2 Self-Refine and Reflexion](#62-self-refine-and-reflexion)
- [6.3 Reflection must rely on feedback signals](#63-reflection-must-rely-on-feedback-signals)
- [6.4 Trigger, classification, decision-making, cessation](#64-trigger-classification-decision-making-cessation)
  - [6.4.1 scene setting: Reflection needs of knowledge assistants](#641-scene-setting-reflection-needs-of-knowledge-assistants)
  - [6.4.2 Trigger signal](#642-trigger-signal)
  - [6.4.3 Feedback classification](#643-feedback-classification)
  - [6.4.4 Processing strategies](#644-processing-strategies)
  - [6.4.5 Conditions for cessation](#645-conditions-for-cessation)
  - [6.4.6 Summary: Review of core decision-making](#646-summary-review-of-core-decision-making)
- [6.5 When not required](#65-when-not-required)
- [Runable Example](#runable-example)

---

## 6.1 Wrong, but keep going down.

Back to 1.1. Agent now has Planning, the four steps of release are no longer missing. But when it comes to running tests:

```text
TypeError: Cannot read properties of undefined (reading 'files')

```

Agent saw this wrong output. And then what did it do? It goes on to write changelog, final report "Is ready for release."

It's not about tools, it's not about Planning, it's not about memory. This is a more fundamental flaw: **Agent lacks a closed loop to "see feedback signal → stop the current path → judge type → decide next."** It saw TypeError, but it treated that output as the same as reading the contents of the document, a message that needs to be recorded, not a signal that needs to be processed.

For example, you drive a red warning light on your dashboard. Reflecting has opportunities to pull over, open the hood, check questions, decide whether to fix it or call a trailer. Drivers without Reflection -- nudity LLM -- just looked at the warning light, wrote "14:32 red light in the log," and continued at 120 km/h.

Change to knowledge quiz. Agent gave a quote: "On the basis of chapter 3 of Software Engineering Practice..." but you looked at the original text and found that it was not in chapter 3. Agent didn't do the "reference check" step, it generated the reference by creating the "like quote" text -- It's like a man writing a paper with a reference to memory, in the correct format, with a precise page number, but the article doesn't exist.

The essence of these problems is that **Agent lacks a decision-making mechanism triggered by feedback signals.** It doesn't say, "Wait, the test failed. I should try again, downgrade, ask for authorization, transfer, or stop?" It only continues to produce the next Token.

> **A common question: Isn't the Tool mechanism of course 4 already feeding the error back to the model?** >
> Yes, Tool's anomaly mechanism in course 4 does structure the error in the tool's execution (parametric failure, time overtime, inadequate privileges, etc.) `ToolResult`, as Observation injects the next round of context. But here's the key difference: **Tool the anomaly solves "Let the model see the error," and Reflection solves "The system has to stop to decide the next step when it sees the feedback."** The former is a passive information channel, while the latter is an active control loop.
>
> The two are completely different in the structure of the system:
>
> - **Tool Aberrant Operating Executive Level** -- Its function is to structure and understandable access to the top and bottom sections of the failed information that individual tools call for. But what happens next when the model receives this wrong message, the Tool mechanism doesn't matter. It's a perfect model. `ToolResult(status="error",...)` As a normal text recorded in the state, continue Planning's next step - this is what Agent, who saw TypeError at the beginning of this section, continued to write changelog. The Tool mechanism transmits the signal, but it does not guarantee that the signal is responding correctly.
> - **Reflection mechanism operating on the control level** -- Its role is to break the current task flow and enter the control circuit "Classification decision-making for processing validation or discontinuation" when feedback signals are detected in Runte. This circuit is not a model of self-saving capacity, but a set of engineering mechanisms in Runtme with hard-coding triggers and stop conditions.
>
> Back to the example of driving: Tool's anomaly is the red warning light on the dashboard -- it's on, the message's on. Reflection is the driver's full reflection -- "The red light is on the side of the car to check the message and decide whether to continue, drive slowly, fix itself, or call the trailer." Warning lights are on, but the driver doesn't care. Continue at 120 km/hour. It's exactly the naked LLM default, because the LLM is essentially a token generator, and its default action is "continue to generate the next token", not "stop checking the last token right." Reflecting is the problem of "drivers ignoring." It's forced one at the system level. `if signal -> stop and decide` Control branch.
>
> So, Reflecting is not a modeling problem, it's a Runtme level engineering project. The Tool Aberrant Mechanism of Session 4 and the Reflection Mechanism of this Chapter are all running in Runte, but the division of labour is different - **Tool Aberration is a signal source, Reflection is a response to signals.** One's in charge of reporting, one's in charge of driving.

## 6.2 Self-Refine and Reflexion

The idea of LLM "reflecting its own output" went through several key points: **March 2023, Self-Refine (Madaan et al.).** The paper presented a simple but effective process: Generating feedback and correction. Each step allows the same LLM to be completed - first output, then feedback to itself, then modification based on feedback. This process has been significantly enhanced in terms of tasks such as writing, code generation, etc. Its fatal weakness, however, is that **feedback comes entirely from the model itself, without external validation signals.** A wrong first draft could lead to a model offering itself a bunch of seemingly reasonable but totally wrong feedback. **June 2023, Reflexion (Shinn et al.).** The breakthrough in this work is the introduction of **external validation signals** — the model is no longer "self-evaluated" but rather the model's determination of what went wrong on the basis of the real results of the execution (testing failed, compiler miscalculated, API returned). Reflexion upgrades "reflection" from a production strategy to an enhanced learning cycle based on environmental feedback: try to watch the real results → analyse the reasons for failure → document experience → try again. It's much more reliable than Self-Refine because it has an external anchor. Late 2023 to date, Reflection has moved from academic concepts to engineering practice. **The key shift is that Reflecting is no longer considered "the self-saving capacity of the model" but is designed as a system mechanism** with trigger and cessation conditions in Runtme. What is the signal of the trigger condition (failure of testing, failure of Schema verification, rejection by the user) and what is the condition of cessation (maximum number of retests, maximum cost, repetition of the same feedback).

## 6.3 Reflection must rely on feedback signals

Reflection is easily misinterpreted as "let the model examine itself". It's like having a student grade his exam -- he's probably going to check it carefully, or he's just picking up every question and handing it over. You don't know what kind.

The model itself says "I checked" doesn't mean it's really reliable. The sentence itself is also a token sequence -- the model uses the same mechanism when it comes to it and when it comes to "citing from Chapter 3". **Self-evaluation outputs share the same source of hallucinations as original outputs.** Better, Reflection should rely on external feedback -- from systems, from tools, from users, but not from models' own "judgements":

| Feedback signal | Specific examples of knowledge assistants | Why is it more reliable than a model self-assessment? |
|---|---|---|
| JSON Schema verification failed | Agent Output `{"tool": "search"} ` But schema requests ` tool_name` Required | Schema verification is the certainty rule - field exists/does not exist, type matches/non-matching - no blurry space |
| Tool Return Parameter Error | `search_notes(query="", limit=500) ` → ` Error: limit must be 1-100` | The real return value of the tool is not a model "like" parameter, is it? |
| Unit Test Failed | It's fixed. `session_manager.py` Post-run test, 3/10 test cases claiming failure | Test frame output of specific expected and actual values - this is reversible, definitive |
| Reference verification failed | Agent said, "Memoory has three layers of guards," but only two floors were found after searching the original. | The original is an objective text -- not a model "Remember" yes, but a search. |
| User Rejected | The user said, "No, I want checklist, not code review." | Users know their intentions. Models don't know what users think. |
| Permission check denied. | `cat /etc/shadow ` → ` Permission denied` | The operating system returned the error of permission -- not a model to judge "I may not have permission." |

In other words, Reflecting is not a fixed step ( "Rethinking every step"), but a closed decision loop **triggered by external signals.** It doesn't start without a signal. It doesn't start until it gets there.

There are four questions to be answered — questions that are the main lines of action of Section 6.4:

- When does it trigger reflection?
- What evidence does reflection depend on?
- What happens after the trigger? 6.4.4 Processing strategy
- When should we stop?

## 6.4 Trigger, classification, decision-making, cessation

A control program can be divided into four steps:

```text
触发信号
  -> 反馈分类 / 证据分析
  -> 决定处理策略
  -> 重试、降级、转人工或停止

```

But before going deep, there is a specific frame of reference.

### 6.4.1 scene setting: Reflection needs of knowledge assistants

Return to 1.1 intellectual assistants. It now has RAG (can check notes), Memory (can remember preferences), Planning (can organize multistep missions). However, it still lacks a closed ring when it encounters a failure:

- **Code analysis scene**: User posted a code to Agent to find bug. Agent output the results of the analysis, but the API method name quoted in it does not exist -- the model itself. Agent won't find himself "this API doesn't exist".
- **Note Questions and Answers**:Agent Answers "According to your notes, the writing logic of the Memoory module is `src/memory/write.py` Three layers of guards have been achieved." The user went through that file and found only two layers. Agent didn't "reference reverse verification" -- it generated references that generated text that looked like a path.
- **Present scene**: Agent executes Planning release process, running test failed (TypeError). It records the wrong output in the state, and then -- go on writing changelog. It lacks a reflection arc "seeing feedback to stop the current path classification and decide on the next step."

Reflection system design constraints:

- The trigger must come from an external signal (test failure, failure of schema verification, rejection by the user) and not from the model self-assessment.
- If you choose automatic processing, you have to revalidate it, not "do it."
- There must be a hard stop — the number of retests, the maximum cost, the same feedback repeated.
- The process is visible to the user, but it doesn't talk -- the user needs to know "Agent found a feedback signal and is processing it," but it doesn't need to see 200 lines.

With this scene, we're moving on. Each step is demonstrated by the specific failure of the knowledge assistant.

### 6.4.2 Trigger signal

Reflection is not "rethinking every step of the way" -- it's wasteful token and slow to respond. The trigger should be **passive and based on external signals**. The signal's only triggered, not without it.

But this principle is simple, and it's all in detail. What do you mean, "the signal"? TypeError in stdout? Did the user say "unsatisfactory"? Tool returns warning, but isn't the error count? There are no standard answers to these questions — depending on your scene, your tools, your users. But before you answer them, you need to establish a classification framework **for feedback signals**: which channels may generate unusual feedback, what actions each feedback should trigger, and — equally important — what are the "exceptions" for each feedback (if not triggered).

The table below provides an example of knowledge assistants, covering seven trigger signals. Note the "exception that should not be triggered" column — it's as important as the "trigger condition". Error triggers are as dangerous as leak triggers.

In the case of knowledge assistants, commonly triggered signals and their corresponding handling actions:

| Trigger signal. | Specific examples of knowledge assistants | Process Action | Exceptions that should not be triggered |
|---|---|---|---|
| Invalid output format | JSON missing required fields, Schema verifying returns `required field 'tool_name' missing` | Recreate structured output, complete missing fields | The problem with format is that the definition of the tool itself has changed (e.g. the new API) - at this time it needs to be updated, rather than regenerated |
| Tool Parameter Error | Call `search_notes(query="", limit=500) ` Back ` limit must be 1-100` | Amending Parameters (Limit=500→Limit=50), retrying | Parameter values per se are correct but are rejected by restricted flow - they should not be changed and should wait to try again |
| Tool execution failed | `git log ` Back ` fatal: not a git repository` | Type of feedback analysed: This is an environmental problem (non-recoverability), not a parameter problem - - Skip this step and notify the user. | Network overtime failed - try again instead of skipping |
| Test failed | `test_memory_cleanup ` The assertion failed, excepted ` cleaned ` got ` pending` | Positioning failure asserted analysis code logical correction rerun test | Test environment per se (e.g. test database not started) - code should not be amended |
| Reference mismatch | Agent says, "Memoory has three layers of guards," but the original is only two. | Retrieving the original version of the false assertion in the correction answer indicates that the conclusion is based on section 2 of note A. | The search results were empty not because the reference was wrong, but because the notes were deleted — users should be informed, not repeated. |
| User Rejected | The user said, "No, I want a checklist, not a code review." | Update target understanding to regenerate output consistent with user intent | Users say "unsatisfactory" but don't point in the direction -- ask first, not guess. |
| Continuous failure | The same test failed three times and the feedback was identical | Stop recording failed context request manual intervention | — |

**Design principles for trigger signals**:

- **External priority**: test failed > Schema failed > tool returned error code > user rejected > model self-assessment. Model self-assessment is used as a last resort only where there are clear verification criteria (e.g. "Check if the output contains three elements").
- **Specifically**: Not "typError at line 42: cannot read 'files' of undefined". Specific signals can produce effective handling decisions.
- **The same signal does not repeat the trigger**: if the same error has been "reflectively processed to verify again" twice, the third should not trigger the same treatment path — it should trigger "stop and report".

The failure of this link is focused on "The Trigger doesn't trigger" and "The Trigger shouldn't trigger chaos":

| Failed performance | Typical cause | Treatment |
|---|---|---|
| Agent saw the error but continued. | The trigger condition only binds the "tool returner field", but TypeError is a stdout output, no error field | Trigger condition covers multiple signal channels: exit code, stderr, output abnormal pattern matching, return value schema verification |
| Normal output miscalculated as failure | Tool returns `{status: "ok", warnings: 3} ` The system is only checked.` status!= "ok"` But ignoring is not equal to error | Distinguishing error and warning;warning does not trigger reflection, but draws user attention after accumulation to a certain number |
| Each step triggers reflection leading to a delayed explosion. | Each of the four steps adds "post-implementation reflection" and one release is ready to run 12 LLM calls (4 execution + 4 analysis + 4 processing) | Trigger only when external feedback signals are available; normal steps do not trigger reflection |
| User rejected as formatting error | The user says "incorrect" and the system triggers the JSON schema recheck (passed) and then reports "outputs correct" - no real feedback from the user. | The user's rejection is an independent trigger signal, which should trigger a re-understanding of the target, not a re-checking of the format |

### 6.4.3 Feedback classification

The trigger signal tells Reflect that "it needs to stop and judge", but does not tell it to try again, fix, downgrade, transfer or stop. Before deciding on the next step, it is important to classify — different types of feedback require completely different treatment strategies. Treating "tool parameter error" as "target error" will only make Agent go further and further in the wrong direction.

How? A practical entry point is to ask three questions:

- **Wrong root is inside Agent or outside?** (the illusion is internal, the network is external)
- **Is the error self-processable or can only skip/report?** (parameters can be changed by error and not enough authority to report)
- **What needs to be changed if it is to be addressed — prompt, tools, context, or control flow?** (changed prompt will not solve the problem of using the wrong tool)

These three questions are used below to examine the eight types of feedback experienced by knowledge assistants. Each type of feedback gives identifiers and corresponding treatment strategies - but more importantly, attention is paid to the margin of error **between the types of feedback** (see table of common traps below), as classification errors are more dangerous than non-classification:

| Type of feedback | Specific examples of knowledge assistants | Identification | Processing policy |
|---|---|---|---|
| Wrong target understanding. | The user said, "Check the code for me." | Output structure does not match user expectations; user feedback "I don't want this." | Reunderstanding user intent and seek confirmation if necessary |
| Context Missing | API method quoted by Agent First Name `memory.load()` It doesn't exist -- it's seen a similar approach in training data, but it's another framework. | Psychic output (coding references, non-existent API, fictional data) | Additional Retrieval - Check for actual API documents or original notes in the knowledge base |
| Tool selection error | The user asked, "What's my note about memory?" | Wrong type of tool used; the result returned does not match the user ' s expected field | Re-select the tool according to its purpose; mark the applicable scene in the tool register |
| Tool Parameter Error | `search_notes(query="", limit=500) ` → ` limit must be 1-100` | Tool returns error verification of clear parameters | Amending parameter values; if parameters are complex, declare binding in tool definitions |
| External context error | `git log ` → ` fatal: not a git repository`;network timeout; disk full | Error from external system rather than Agent itself; retrying cannot be solved | Not recover skipping and notifying users; can restore (network timeout) waiting to try again |
| Output format error | JSON missing required fields; generated checklist not Markdown format | Schema verification failed; output structure does not match predefined format | recreate structured output;enhanced format constraints in prompt |
| Insufficient Permissions | `cat /etc/shadow ` → ` Permission denied` | Error returning permissions to operating system or API | Do not try again - inform users of lack of permission, request authorization or downgrade |
| Results of poor quality | Agent generated changelog with only 3 rows, covering 2/5 numbers | The output was formatted but incomplete; user feedback was "too simple." | Supplement; add acceptance criteria (e.g. "changelog must cover allfeat and fix part") |

**Classifications are not one-off**. If a round of treatment still fails, it needs to be reclassified — it may be the first time that the classification is wrong, or it may be due to upstream (e.g. "tool parameter error" actually led to the choice of an undesired tool because "target misperception". **Common trap for classification**:

| Failed performance | Typical cause | Treatment |
|---|---|---|
| It's a tool error. | Agent quoted a non-existent API, classified as "tool parameter error" and re-engineered the parameters over and over again -- but the problem is not a parameter, it's this API that doesn't exist. | Check first whether the entity cited exists (API name, file path, function name) and there is no supplementary search by classified "missing context" |
| Consider environmental error as a code error | The test failed because the database was not activated. | Distinguishing between "external uncontrollable" and "internally reversible" -- no code for environmental problems. |
| It's too rough to handle it. | All failures are classified as "tool failure" and are handled in a single "retry" format. | Distinguishing at least three categories: retry (network timeout), fixability (parameter error), non-recoverability (lack of privileges, lack of environment) |

### 6.4.4 Processing strategies

Once the classification is completed, the next step is to decide on the strategy to be followed. Processing does not amount to amendment; it may be amending input, changing tools, filling context, waiting for retesting, downgrading, requesting authorization, transferring labour, or simply stopping. The key is not to fix the problem, but to make the right next control decision based on feedback. But before looking at concrete solutions, understand the three failures of "dealing with".

- First: **Nothing changed** — the same prompt was regenerated, the only change was random seeds, and the result was probably wrong.
- Second: **Wrong direction** — Misperception is treated as a parameter error and re-adapts the search parameters, but the problem is not one at all.
- Third: **the scope of processing is too large** - the wrong parameters are replaced by tools and prompt to introduce new variables, making it more difficult to locate the problem.

Good coping strategies are like traffic diversion: Turn around, slow down, stop, stop, not always drive into the maintenance plant. Let's see what kind of treatment is needed for each of the eight categories:

| Type of feedback | Processing policy | Operations of knowledge assistants | How to Verify After Processing |
|---|---|---|---|
| Wrong target understanding. | Rewrite hints, add constraints | Add "Do not generate code review report format, only output questions and recommendations" to the programt when the user rejects it | Confirm user after regenerated |
| Context Missing | Additional Search | API method created by Agent to retrieve the module's actual method name in the notes and replace the hallucinogenic reference with the search result | Checks article by article whether the references can be found in the notes |
| Tool selection error | Change Tools | WebSearch `search_local_notes` | Check if the tool returns from the correct knowledge Source |
| Tool Parameter Error | Adjust tool parameters | `limit=500 ` → ` limit=50 ` ， ` query=""` Complete Query Word | Tool returns successful status code and results are not empty |
| External context error | Unrecoverable demotion | `git log` Failed to manually specify a range notification user "because it's not in the guit repository, it's manual" | N/A (taken over by users after skipping) |
| Output format error | Regenerated + Enhanced format bounds | JSON Missing Fields Add to Prompt `Required fields: tool_name, args, reason` | Schema Validation |
| Insufficient Permissions | Request user authorization or downgrade | `Permission denied ` Application to user ` sudo` Competences or suggested alternatives | Re-enforce when user confirms authorization |
| Results of poor quality | Additional + Enhanced acceptance standards | Changelog only over 2/5 committee to add in prompt `必须检查 git log --oneline 中的所有 feat 和 fix commit` | Article-by-article inspection of acceptance and inspection standards |

**The design principles of the treatment strategy**:

- **If automatic fixes are selected, the input** must be changed: if only "try again", the only change is random seeds. The corrective action requires changes in prompt, parameters, tool selection or context - to make the second attempt and the first substantive.
- **Process ranges to match the root causes of the error**: the parameters are changed wrongly, not with tools. The tool is changed by mistake and does not re-understand the user ' s intentions. Do not try again and again when the authority is insufficient, but rather request authorization or demotion. Overprocessing introduces new variables, making problems more difficult to locate.
- **The treatment strategy itself may fail**: if post-treatment certification is still not passed, do not continue to patch around the same strategy — this can easily become an infinite cycle. It should be reclassified (perhaps for the first time correctly) or stop and request manual intervention.

### 6.4.5 Conditions for cessation

The stop condition is the safety valve for Reflection. Without it, Reflecting is not "smart processing," but "silent death cycle". The conditions for stopping must be coded hard, and the model can't decide by itself.

| Conditions for discontinuation | Proposal for thresholds | Conduct at Trigger | Why do you have to code hard? |
|---|---|---|---|
| Maximum number of retries | 3 times (automatic processing of the same error) | Stop processing automatically, keep the last failed result and request manual intervention | The model would still say, "This time it should be right" at the fourth and fifth treatments -- it doesn't have the instinct that it should stop." |
| Maximum cost | $1.00 (total cost of individual assignments) | Stop autoprocessing and return the current optimal result | The model doesn't know how much it cost. Money. |
| Maximum time-consuming | 60 seconds (time starting with the first trigger) | Stop autoprocessing, last result before timeout as output | The user's waiting. We can't let a test fail to get the release ready for 5 minutes. |
| Same feedback repeated | 2 (full consistency of post-processing feedback) | Stop auto-processing, "The treatment strategy hasn't changed the result, probably due to a classification error." | If the same feedback still emerges after processing, it means that there is no root cause of the treatment strategy - continuing to process is randomly moving. |
| Feedback Upgrade | Recoverable feedback does not restore feedback (e.g. network overtime becomes disk full) | Stop autoprocessing. "The feedback type has been upgraded and is not suitable to continue autoprocessing." | Upgrading of feedback means that the environment is degraded, and further damage may result from continued automatic operation |
| Lack of effective feedback signal | The external certifier returns insufficient information to locate the root cause (e.g. only "failed" for no specific reason) | Stop auto-processing, "The feedback signal is not enough to generate an effective processing strategy, requesting more detailed feedback." | Models are made up for a reason that sounds reasonable and then dealt with -- but not on the basis of speculation. |

**The relationship between the conditions of cessation**: they are OR relations — any one of the conditions met ceases. The first trigger is usually the "same feedback repeats" (as in the 2nd-3rd treatment), followed by the "maximum number of retries" (3 times), with costs and time limits rarely triggered in normal missions — they are the bottom line to prevent extreme situations.

The failure of this segment is focused on "The Time to Stop":

| Failed performance | Typical cause | Treatment |
|---|---|---|
| Same feedback processed 5 times | The processing policy did not change the input (only regenerated the same prompt), but each LLM random output was slightly different, and the system thought it was progressing. | Test whether the treatment strategy is the same as the previous one; if the same prompt+ parameter produces the same feedback 2 times, 3 must change the strategy or stop |
| The costs are quietly exceeded. | Every call to LLM for "classification" and "generation processing policy", single 0.02, but a task triggers 15 times | Accumulated cost counter updated after each LLM call, exceeding $1 hard stop |
| The process is being led by a model. | The model created a rational but wrong root factor in "analyzing error" (e.g. "test failure may be due to time zone problems"), and then created a treatment strategy around this error root. | Error analysis only allows the reference to specific facts in external signals (miscounting, error code, return value) and does not allow models to speculate "what may be the reason" |

Reflecting the core skeleton of the cycle - the key is that the trigger must come from an external signal and the stop condition must be coded hard:

```python
# Reflection 循环：只在有外部反馈信号时触发，永远设置停止边界
def reflection_loop(
    action: callable,       # 执行动作（生成代码、回答问题等）
    validate: callable,     # 外部验证器（运行测试、检查 schema、校验引用）
    max_retries: int = 3,   # 硬上限
    cost_budget: float = 1.0  # 成本上限（美元）
) -> dict:
    """带 Reflection 的执行循环"""
    cost_spent = 0
    last_error = None

    for attempt in range(max_retries):
        # 1. 执行动作
        result = action(
            previous_error=last_error,  # 把上次失败原因注入上下文
            attempt=attempt
        )
        cost_spent += result.cost

        # 2. 外部验证（不是模型自评！）
        validation = validate(result.output)

        if validation.passed:
            return {"status": "success", "output": result.output,
                    "attempts": attempt + 1, "cost": cost_spent}

        # 3. 分类反馈，准备下一轮处理上下文
        last_error = {
            "type": classify_feedback(validation),  # schema_error | test_failure | tool_error | ...
            "message": validation.message,
            "evidence": validation.evidence,      # 具体报错行、引用原文等
            "suggested_action": validation.suggestion
        }

        # 4. 停止条件检查
        if cost_spent > cost_budget:
            return {"status": "stopped", "reason": "cost_limit",
                    "last_error": last_error}
        if last_error["type"] == "same_error" and attempt >= 2:
            return {"status": "stopped", "reason": "repeated_failure",
                    "last_error": last_error}

    return {"status": "stopped", "reason": "max_retries_exceeded",
            "last_error": last_error}

# 使用示例：代码修改 + 测试驱动的 Reflection
result = reflection_loop(
    action=lambda prev_err, attempt: llm_generate_code(
        task="fix the bug in user_service.py",
        test_failure=prev_err["evidence"] if prev_err else None
    ),
    validate=lambda code: run_tests(code),  # 外部测试框架，不是 LLM
    max_retries=3
)

```

> **Design elements**: `validate ` It has to be an external certifier -- running tests, checking schema, comparing the original text, not "let the model look again." ` action ` Received ` previous_error` As a handling signal, but only into facts (misrepresentation, failure test name) and not into model self-evaluation.

### 6.4.6 Summary: Review of core decision-making

| Link | Core decision-making (knowledge assistant scene) | Wrong behavior. |
|---|---|---|
| Trigger signal (6.4.2) | What external signals trigger? | TypeError is ignored as normal; normal warning is triggered by error |
| Feedback classification (6.4.3) | What kind of feedback? Is the particle size enough to guide the process? | The illusion is used as a tool parameter error, adjusting the parameters repeatedly but API does not exist |
| Processing strategy (6.4.4) | Should the next steps be retried, amended, downgraded, manual transfers or stopped? | It's just a rerun of the same prompt, the only change is random seeds; the process is too big, even the tools are changed. |
| Conditions for cessation (6.4.5) | Where is the hard ceiling? How many times has the same feedback stopped? | Same feedback processing 5 times, each LLM random output slightly different, the system thinks "in progress" |

**Three main lines through the entire link:**

1. **Validation must be externalized**: The credibility of Reflection depends entirely on the credibility of the certification. If `validate()` It's "let LLM examine itself," and that whole Reflection loop is that LLM is playing chess with itself -- judges and chess players are the same person. Test Frame, Schema Verify, Reference Original Comparison, User Rejected - These external anchorages are the basis of Reflection not becoming self-deception.
2. **Categorization before treatment, root before symptoms**: rerun when you see "test failure" — it's not Reflection, it's prayer. Effective handling requires knowing "why fail": is the code logic wrong or is the test environment broken? Did you quote an API that did not exist or an API that existed but was wrong? A misclassification is a waste of time.
3. **The condition is the safety valve, which cannot be given to the model**: the model does not have the instinct that "it should stop" -- it still says with confidence at the fifth treatment, "this time it should be right." Maximum number of re-tests, maximum cost, same feedback testing - these must be coded hard and must be enforced while running.

Turning back to the question at the beginning of this chapter -- Agent saw TypeError and kept writing about changelog. Take the example of knowledge assistants: not because Agent was "not smart enough" but because he lacked a decision-making loop triggered by external signals. The essence of Reflection is not to "get the model rethinking" but to create in Runtme a system mechanism for "testing feedback and cataloguing decision-making to validate or stop". Trigger comes from an external signal, certifier from an external system, stop condition from a hard code -- the model's only responsible for producing the next candidate, not for judging whether or not it should continue.

## 6.5 When not required

Reflection:

- The output can be dealt with directly by means of certainty rules.
- Failure costs are low and simple reruns are cheaper.
- Without external feedback, the model is unable to determine whether it is wrong or not.
- Mandates are very sensitive to delays.
- High-risk tasks require manual or rule validation, and model self-assessment is not a substitute.

Practical judgement:

```text
如果有明确反馈信号，并且自动处理成本低于失败成本，Reflection 值得引入。
如果只是让模型”再想想”，通常不值得。

```

> **The story is not over.** Reflecting allows Agent to learn to decide on the next step based on feedback, analyse the reasons for the failure and choose to retest, amend, downgrade or stop. However, one of the conditions for the cessation of Reflection is the “request for manual intervention” - the final safety valve is judged when automatic disposal is no longer possible.
>
> However, the words “request for manual intervention” are simple and are all pits: what is to be asked, and what is to be dealt with? It's too frequent to ask, too few to be afraid. What information do you show the user when asked so he can make the right decision in three seconds? This is the next chapter of the Human-in-the-loop problem -- how to design people's interface with Agent when Agent should not decide for himself.
>
> And looking back, you'll find that there's a deeper problem: there's some tasks that can be solved, not "letting one work with one person." You let Agent write a security plan and let it examine itself -- it says, "No obvious problems." You looked at it as a human being and found three security hazards. Why? Because “creatives” and “reviewers” require different perspectives, different contexts and different criteria for judgement. That's the last kind of empowerment Multi-Agent to solve: one person writes codes, another person stares.

---

## Runable Example

After this chapter is completed, you can compare the local Reflection example of running course 5 05-06:

- [Course 5 05-06 Reflection Example](../examples/course-05-06-reflection/README.md)

The example shows four iterative phases of Reflection around the knowledge assistant scene: V0 (no reflection, observation of the full process of Agent neglecting feedback), V1 (Schema verification failed to recreate), V2 (tool parameter misclassification retry), V3 (test failure correction assertion). They also include a complete Reflection cycle (triggering classification tectonic validation or suspension) and a cessation condition trigger demonstration (the same feedback repeats a hard stop).

The Reflection loop in the example is a teaching achievement, not a complete production framework: Validate simulates an external certifier with a definitive function, processing policy is generated by hard encoding according to the type of feedback rather than LLM dynamic, and costs are modelled. However, it presents a complete picture of the core skeletons of Reflection — external signal triggers, feedback classification, processing strategies to change input or control streams, stop condition hard coding — which remain unchanged in the real system.

```bash
# Python 版本
cd examples/course-05-06-reflection/python
python3 reflection_demo.py

# Node.js 版本
cd examples/course-05-06-reflection/nodejs
node reflection_demo.mjs

```

### Summary of this chapter

The essence of Reflecting is not to "get the model rethinking" but to create a systematic mechanism in Runtme to "test the feedback and sort the decision-making process to validate or stop". Three main lines running through the chapter: **Validation must be externalized.** The credibility of Reflection depends entirely on the credibility of the certifier. If `validate()` It's "Let LLM examine itself," and that whole Reflection loop is that LLM is playing chess with itself -- judges and chess players are the same person. Test Frame, Schema Verify, Reference Original Comparison, User Rejected - These external anchorages are the basis of Reflection not becoming self-deception. Model self-evaluation outputs and original outputs share the same source of hallucinations. **Classification precedes treatment and is rooted in symptoms.** Seeing "test failure" run again — it's not reflection, it's prayer. Effective processing requires knowing “why fail”: is the code logic wrong or is the test environment broken? Did you quote an API that did not exist or an API that existed but was wrong? To fix the illusion as a tool parameter is to make Agent go further and further in the wrong direction. If an automatic correction is selected, the processing policy must change the input (prompt, parameter, tool selection or context) rather than simply rerun; if not, it should be downgraded, transferred or stopped. **The condition of cessation is the safety valve and cannot be left to the model.** The model does not have the instinct that it should stop - it will still say with confidence at the fifth treatment: “This time it should be right”. Maximum three retries, same feedback, two stops, maximum cost $1 — these must be hard coded and enforced while running. The condition of cessation is an OR relationship, and any satisfaction will stop. Reflection loop without conditions is more dangerous than no Reflection.

---
