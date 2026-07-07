# Lesson IV: Tool mechanisms

## Introduction to the curriculum

Lesson 3 explains the smallest Agent closed ring:

```text
Agent = LLM decision-making + tool/environment interaction + state management + loop control
```

Course IV goes deep into the key links between "decision-making" and "implementation": **Tools/environment interface**.

For the first time, a lot of people are going to think that it's done with the model. In fact, if you run a few times on a real mission, you're gonna run into unexpected problems:

- While the model had a search tool, it produced a direct answer when it was time to check.
- The tool worked, but returned 5,000 line logs, the next round of context blasts, the model "forgets" the user's original instructions.
- The model creates an apparently rational file path, but that path is outside the workspace -- if Runtme doesn't stop, it reads the files that should not be read.
- The user said, "Send me an e-mail." `send_email` There was no confirmation of the recipient, no preview of the content — the user was in shock.

These problems are not caused by the lack of models. They are rooted in: **The tool call is not an isolated API request, but a running-time mechanism that needs to be carefully designed.**

Starting with the history of Function Calling mentioned in course II, the course opens up the tool to a complete link:

```text
LLM Decision → Tool Selection → Parameter Generation
 → Permission Check → Tool Execution
 → Observation / Feedback → State Update
```

Each step of the chain is likely to fail, and each step requires a corresponding mechanism. The goal of course IV is not to give you "access to more tools" but to understand how to use them as an **optional, implementable, manageable, reusable, auditable** system mechanism.

---

## Learning objectives

After this lesson, you will be able to:

1. **A complete tool to access links** -- Understanding each step from model decision-making to tool implementation to status update and its risks
2. **Design a clear definition of tools** -- Write a tool description and parameters that allow the model to understand precisely when to use and when not to use
3. **Diagnosis tool selection failed** — Distinguishing between non-use, non-use, wrong tool, miscalculation of parameters, repeated calls, and finding root causes
4. **Accomplishment tool execution and backfilling** — basic code mode for proofing, timeout, retrying, misstructured and summary of results
5. **Design Tool Permissions Policy** -- Control of high-risk actions using risk classification, Deny-first, minimum privileges, audit logs
6. **Designed Human-in-the-loop control points**  Clarify which tool actions must be identified, modified or taken over
7. **Distinguishing the positions of Function Calling, MCP, Tool and Skill** -- Clarifying which part of the tool chain they address separately
8. **Relaying duplicate tool combinations into Skill** -- Understanding mission experience, default processes, failed processing and reuse borders

---

## Contents

- [Introduction to the curriculum](#introduction-to-the-curriculum)
- [Learning objectives](#learning-objectives)
- [Chapter I: How to access the tool Agent](#chapter-i-how-to-access-the-tool-agent)
  - [1.1 Tool call is not a single API request](#11-tool-call-is-not-a-single-api-request)
  - [1.2 Tool access links](#12-tool-access-links)
  - [1.3 From Function Calling to Tool Mechanisms System](#13-from-function-calling-to-tool-mechanisms-system)
- [Chapter 2: Definition of Tools - let the model know what the tool is](#chapter-2-definition-of-tools---let-the-model-know-what-the-tool-is)
  - [2.1 Nature of tool definition](#21-nature-of-tool-definition)
  - [2.2 Toolname, description and parameters](#22-toolname-description-and-parameters)
  - [2.3 Return value structure and error structure](#23-return-value-structure-and-error-structure)
  - [2.4 Tool particle size: atoms vs combination](#24-tool-particle-size-atoms-vs-combination)
  - [2.5 Principles for the design of good tools](#25-principles-for-the-design-of-good-tools)
- [Chapter 3: Tool selection -- let the model know when to use it](#chapter-3-tool-selection----let-the-model-know-when-to-use-it)
  - [3.1 Three things about tool selection](#31-three-things-about-tool-selection)
  - [3.2 Three route methods](#32-three-route-methods)
  - [3.3 Candidate management: Do not hand over all tools to models](#33-candidate-management-do-not-hand-over-all-tools-to-models)
  - [3.4 Tool selection failed classification and debugging](#34-tool-selection-failed-classification-and-debugging)
- [Chapter 4: Implementation and Backfilling - Get the tool results into the next round](#chapter-4-implementation-and-backfilling---get-the-tool-results-into-the-next-round)
  - [4.1 Runtme is the real enforcer.](#41-runtme-is-the-real-enforcer)
  - [4.2 Parameter verification, overtime, retesting and thorium, etc.](#42-parameter-verification-overtime-retesting-and-thorium-etc)
  - [4.3 Misstructured](#43-misstructured)
  - [4.4 Result processing: summary, page break, cut-off and transfer of resources](#44-result-processing-summary-page-break-cut-off-and-transfer-of-resources)
  - [4.5 Operation: Providing a basis for the next round of decision-making](#45-how-to-shape-the-next-round-of-decision-making)
- [Chapter 5: Permissions and security - Make tools manageable](#chapter-5-permissions-and-security---make-tools-manageable)
  - [5.1 Why tool privileges are not optional](#51-why-tool-privileges-are-not-optional)
  - [5.2 Risk classification and default strategy](#52-risk-classification-and-default-strategy)
  - [5.3 Deny-first and minimum privileges](#53-deny-first-and-minimum-privileges)
  - [5.4 Progressive delegation of authority and audit log](#54-progressive-delegation-of-authority-and-audit-log)
- [Chapter 6: Human-in-the-loop - Engaging people in high-risk decision-making](#chapter-6-human-in-the-loop---engaging-people-in-high-risk-decision-making)
  - [6.1 Models should not decide everything alone.](#61-models-should-not-decide-everything-alone)
  - [6.2 Trigger conditions and mode of intervention](#62-trigger-conditions-and-mode-of-intervention)
  - [6.3 Identification of interfaces and feedback loops](#63-identification-of-interfaces-and-feedback-loops)
- [Chapter 7: MCP - Standardize access to tools](#chapter-7-mcp---standardize-access-to-tools)
  - [What happens when more tools are available?](#what-happens-when-more-tools-are-available)
  - [7.2 MCP and Function Calling](#72-mcp-and-function-calling)
  - [7.3 Tools / Resources / Prompts](#73-tools-resources-prompts)
  - [7.4 When MCP was introduced](#74-when-mcp-was-introduced)
- [Chapter 8: Skill - Remittance into a capability package](#chapter-8-skill---remittance-into-a-capability-package)
  - [8.1. From "rethinking" every time to "pack your experience."](#81-from-rethinking-every-time-to-pack-your-experience)
  - [8.2 Structure of Skill](#82-structure-of-skill)
  - [8.3 Skill vs Tool vs Workflow](#83-skill-vs-tool-vs-workflow)
- [After-school exercises](#after-school-exercises)
- [Acceptance and inspection standards](#acceptance-and-inspection-standards)
- [References](#references)
- Next class connect.

---

## Chapter I: How to access the tool Agent

### 1.1 Tool call is not a single API request

Think back on course two: Toolformer and Function Calling. Toolformer proves one thing: models can learn when to call API. Function Calling standardized this matter into an engineering interface: the model no longer produces "recommends you to check the database," but rather a structured one. `{"tool": "query_db", "arguments": {...}}` .

But there's an easily neglected jump. In the Function Calling design, the model is responsible only for **generating the call intent** -— the real implementer is Runtime. This division of labour means that there is a whole chain of engineering that needs to be addressed from the model's "I want to call this tool" to "the result of the tool goes back to the next round of decision-making."

Just look at the tool call as "Model Output Toolname → Program → API → Return Results" and leave out a few key questions:

- How do models know what tools?
- How do you know when to use the model and when not?
- How do you choose models when multiple tools can be useful?
- Are the parameters generated by the model credible? (It creates a non-existent file name?)
- What if the tools fail?
- What if the tool results are too long and the key information is squeezed out of the context?
- Tool actions have real world implications (mailing, deleting documents, filings), who approves them?
- How can the multiple tools often be used together to accomplish their tasks and sink into reusable models?

These questionnaires can't be solved by modeling -- they need systematic design at the Runtme level.

### 1.2 Tool access links

Open the tool. It's a seven-step link:

![Tools call the seven-step link.](../assets/course-04-tool-call-chain.svg)

This link can directly map the smallest closed ring of course three -- it's taking the "tools/environment interactions" in the closed circle.

### 1.3 From Function Calling to Tool Mechanisms System

Course 2 combusts the evolution of the tools to be used: Toolformer (2023.2) proves that models can learn to use tools → ChatGPT Plugins (2023.3) to transform "AI works" into a popular experience → Function Calling (2023.6) standardized interfaces for model generation tools to be used → MCP (2024) seeks to standardize the discovery and connection of tools.

Course 4 stands at these historical nodes, focusing on a question: **What mechanisms do you need to design when you really want models to be used in your own system?**

![Overview of the Tool Mechanisms System](../assets/course-04-tool-mechanism-map.svg)

---

## Chapter 2: Definition of Tools - let the model know what the tool is

### 2.1 Nature of tool definition

Tool definition is the only entry point for model understanding tools. The model doesn't know how it works inside your function, what's in your database, what's in your API. It just knows what you told it about.

The quality of the tool definition therefore directly determines the ceiling of the tool ' s call. Describes the fuzzy model hesitated or misused. Parameter binding missing → model free to use default values. The misformatted model gets a "failed" that doesn't know what to do next.

The tool definition answers six questions:

- What can this tool do?
- This tool can't do what?
- When should it be used? When should it not?
- What parameters do you need to use it? What is the meaning and constraints of each parameter?
- Return what when successful? What format?
- Return to what when you fail? What information is included to help with the next decision?

### 2.2 Toolname, description and parameters

A tool definition contains at least name, description and parameters Schema. The following is the definition of a JSON Schema tool in the Python code:

```python
TOOL_READ_FILE = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": (
            "Read UTF-8 text files under workspace."
            "Use this tool when the user requests to view, read, and check the contents of a file."
            "Note: Only documents under the workspace directory can be read, not system files or external paths."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to file relative to workspace, such as 'notes.md ' "
                }
            },
            "required": ["path"]
        }
    }
}
```

Design elements:

- **Specific name**, not called `do_task ` 、` helper ` 、 ` process` I don't know. Models create first impressions by name.
- **Description to describe applicable and not applicable scenarios**. It's more important than the argument statement -- the model decides whether it should be used, then how it should be used.
- **Parameters need to be typed, bound and illustrative.** Don't leave space for model guess.
- **Tool boundaries need to be clear** and multiple tool capabilities avoided. If `search_web ` and ` search_database` It's too much, and the models are randomly chosen.

Compare the quality differences of the two descriptions:

```python
# Bad description.— It's too vague to judge when to use it.
BAD_TOOL = {
    "name": "process_data",
    "description": "Processing data."
    "parameters": {"properties": {"input": {"type": "string"}}}
}

# Good description.— The scenes, boundaries and constraints were clarified
GOOD_TOOL = {
    "name": "summarize_document",
    "description": (
        "Summarize the contents of the text document as elements of a specified quantity. "
        "When the user requests 'summary', 'summary', 'computing points'."
        "Note: The content of the document needs to be obtained first through read_file, and do not call without it."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "Text content to summarize (usually returned from read_file)"
            },
            "num_points": {
                "type": "integer",
                "minimum": 1,
                "maximum": 10,
                "default": 5,
                "description": "Number of points summarized, 1-10, default 5"
            }
        },
        "required": ["content"]
    }
}
```

### 2.3 Return value structure and error structure

The return value of the tool also requires an agreed format. Models and Runtume can be difficult to handle if they succeed in returning to the natural language, if they fail, or if they fail.

Suggests a uniform structured return format. In Python:

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class ToolResult:
    """Unified tool return structure."""
    status: str                          # "success" | "error"
    summary: str                         # A short summary will be placed in the context
    data: Any | None = None              # Complete data, possibly longer
    error: dict[str, str] | None = None  # Error Details, only status="error" Time value

    @classmethod
    def success(cls, summary: str, data: Any = None) -> "ToolResult":
        return cls(status="success", summary=summary, data=data)

    @classmethod
    def error(cls, code: str, message: str,
              retryable: bool = False,
              suggested_action: str = "") -> "ToolResult":
        return cls(
            status="error",
            summary=message,
            error={
                "code": code,
                "message": message,
                "retryable": str(retryable).lower(),
                "suggested_action": suggested_action,
            }
        )
```

Core value of structured return: as seen in model `error.code == "file_not_found" ` and ` suggested_action`, so you can just give the next step of a targeted decision, instead of getting a vague "failed" and start guessing.

### 2.4 Tool particle size: atoms vs combination

Tool particle size is the most easily neglected but most influential design decision-making.

![toolparticle selection: Atoms vs combination](../assets/course-04-atomic-vs-composite.svg)

### 2.5 Principles for the design of good tools

Taken together, good tools usually have these characteristics:

- **Atomic**: a tool to do a sort of clear action. Do not read_files and e-mail a tool.
- **Description is the document**: Tool description is the main or even the only document for the model understanding tool.
- **Boundary clarity**: a clear statement of when and when to use. The latter is as important as the former.
- **Structural returns**: Both successes and failures have uniform formats, and errors include codes, reasons and recommendations.
- **Retestability clear**: Tell the model if it fails "This one can try again" or "This one won't try again".
- **The side effects are controllable**: Actions such as writing, deleting, sending, paying must be controlled with permission and cannot be automatically executed by default.
- **Observable**: parameters, results, time-consuming per call are recorded.

---

## Chapter 3: Tool selection -- let the model know when to use it

### 3.1 Three things about tool selection

The tool selection essentially answers three questions at one decision point:

```text
When do you use the tools? → What tool? → How do you fill the parameters?
```

Any one of these three steps is wrong, and the tool will fail. And the root cause of the error is often not "no model" but tool definition, context or route design.

For example, users say:

```text
Please summarize the content of notes.md.
```

Correct behaviour and possible errors:

```text
Correct: read_file("notes.md") → Get Content → Return Summary
Error 1: Make a "summation" without reading the file.← Should I use it?
Error 2:search_web("notes.md")← Wrong selection tool (boundary confusion)
Error 3: read_file ("note.md")← Error filling arguments (one less s)
Error 4: read_file again after success← Repeated calls (lack of progress judgement)
```

### 3.2 Three route methods

Look at a problem that is common in a real system: the first week of Agent's access tool, only `read_file ` 、` search_web ` 、 ` calculator` Three tools, models are usually selected well. Two months later, the list of tools became 40: document reading and writing, code searches, web searches, database queries, e-mails, creation worksheets, deployments, rollbacks, refunds, user information queries. At this point in time, if all the tools are inserted in the context once and for all, and the model "do what you want" will significantly increase the number of errors.

The problem is not just the wrong model. The more tools, the more they describe the context in which they are used; the more similar tools, the blurring of borders; and the more high-risk and low-risk tools mix, the more control of authority becomes dangerous. The vehicle route in the production system, the core is not "mixed smart enough" but:

```text
Within what scope should the system let the model make decisions?
```

There are usually three ways to achieve the choice of tools, the core difference being "who has the right to make decisions". 

**Modalities I: Model ownership**. Inserts a list of tools into the context to allow the model to determine which to call and which to call.

**Mode II: Rules route**. The tool is determined by code based on input characteristics.

**Mode III: Mixed route**. The rules reduce the pool of candidates first, and models are selected in the pool.

In practice, hybrid routes are the most common production option: **systems are reduced in scope and models are refined.**

![Three ways to compare](../assets/course-04-three-routing-methods.svg)

### 3.3 Candidate management: Do not hand over all tools to models

What tools should models see at this stage? **In some scenarios, a model should not determine whether to call a tool:**

**The scene of the tool should be mandatory**: the user needs to search for real-time data, the user needs to read documents, the user needs to accurately calculate and the user needs to verify the external environment. If tools are not adapted, the model is expected to generate a reasonable but unverifiable answer in memory or language mode.

**The use of the tool should be prohibited**: the user is just chatting or conceptual interpretation, the user requests ultra vires action, the current task has been completed and the high-risk action has not been confirmed. If tools are transferred at this time, resources are wasted or there are security risks.

Most of the cases, except for mandatory and prohibited ones, should go into candidate screening rather than handing over all tools to models.

#### Progressive disclosure: first to the catalogue, then to the details

In the practice of Claude Code/Agent Skills, there is a useful idea: **progressive disclosure**. Its core is not a particular document format, but a context management principle:

```text
Don't reveal all the details at first.
Exposure index.
When the model is judged relevant, the specification is loaded.
When you really want to perform, read a deep document, example or script.
```

Putting this idea into a tool mechanism can be divided into three layers:

![Progressive disclosure: three-layer tool information model](../assets/course-04-progressive-disclosure.svg)

This solved two problems. First, save the context: an Agent can have many tools, but the current rotation does not need to carry all the tools. Second, the reduction of interference: the model is chosen only between tools relevant to the current mission and is not induced by unrelated tools.

#### How to screen the tool with mixed route

Can not get folder: %s: %s A more reliable router will look at seven categories of context at the same time:

- **Intent**: is the user searching, writing, computing, searching, executing orders, or requesting confirmation?
- **Mandate phase**: currently in the phase of exploration, reading, analysis, modification, validation, submission or end?
- **Scope of resources**: tasks related to local documents, current projects, external web pages, databases, or third parties API?
- **User privileges**: current users have read, write, execute, production environment privileges?
- **Risk level**: is the tool read-only, reversible, irreversible, external side effects, or high-risk operation?
- **Context evidence**: Is current information sufficient? Do you need to read real files, query real-time data or validate environments?
- **Historical trajectory**: What was just called? Has it failed? Is the same no progress tool being repeated?

A specific example:

```text
User request: See how the tools are written in notes.md.

The context determines that:
- Intent: Read+ Analysis
- Stage: Explore / Read
- Resource range: local documents
- Permission: readable, not written
- Risk: low risk, read-only
- Evidence: Real documents must be read and cannot be summed up.

Candidates:
- read_file
- list_files(If the file path is not clear)

Filtered tools:
- write_file(Other Organiser
- search_web(Other Organiser
- send_email(It's irrelevant and has external side effects)
- deploy_project(It's irrelevant and high risk)
```

This is when the model is not freely chosen among dozens of tools, but is focused on a very small candidate: "The path is clear, so call directly." `read_file` ."

The most important conclusion in this section is that **the tool route does not give the choice to the model in its entirety, but rather to the choice of the power layer.** The system determines the range of candidates, the model is semantically judged within the range and Runtime performs permissions and parameters validation before execution. The more tools and risks, the more candidate management and progressive disclosure should be used.

### 3.4 Tool selection failed classification and debugging

Do not change the Prompt only when the tool selection is wrong. Question of locating first by type:

| Type of failure | Performance | Common Roots | Debug direction |
|---|---|---|---|
| I don't think so. | We need to check the data without changing the tools. | The tool description is weak. The model doesn't know it can do this. | Use scene in enhanced description |
| I shouldn't have used it. | We'll also search the API | Tool description is too seductive, or Prompt is not constrained | Add "no" to the description. |
| Error Selection Tool | It's a page search. | Tool boundaries overlap and descriptions are too similar | Distinguishing the use of scenarios for two tools |
| Wrong argument | Filename, ID make-up | Parameters are not limited enough, or context information is missing | Strengthen Schema binding + check if the context contains the required parameters |
| Repeat Call | There's no new result with the same tool. | Lack of circulation control and judgement on progress | Repeat at Runtme level |

A specific debugging case:

```text
Question: The user says, "Look at what's written for me.md."

Root analysis:
1. Check Context— models received list of tables, including read_file and search_web
2. Check Tool Description— read_file The description just says "Read a file" and doesn't say it's different from "search_web"
3. Check semantic boundaries— The description of both tools is not clear on their respective application/disapplicability scenarios and the model cannot be effectively distinguished

Restoration:
- read_file Add in the description: "Use this tool when the user has specified a specific filename, such as 'read notes.md'."
- search_web Add the following to the description: "When users request extensive, up-to-date information. Do not read local files specified by the user."
```

Principles for the selection of debugging tools: **Discrete the problem of the definition of tools before adjusting Prompt and finally doubt the capacity of the model.**

---

## Chapter 4: Implementation and Backfilling - Get the tool results into the next round

### 4.1 Runtme is the real enforcer.

Models are generated tool call, which does not mean that tools have been implemented. The model just says, "I want to call read_file, the parameter is notes.md." It's Runtme that really reads the file, processes the error, formats the result.

Runtme's role in the tool implementation chain:

```python
execute_tool_call(tool_name, arguments, tools, permissions, logger):
    # 1. Verify tool exists → return a tool_not_found error
    # 2. Validation parameters (requirements, types, constraints) → Unable to pass returns specific verification error
    # 3. Check permissions (deny priority, default rejection) → Returns if failed
    # 4. Record audit logs (who, what tools, what parameters, what time)
    # 5. Implementation tool → Successful return result, abnormal return structural error (with retryable tag)
```

This is the concrete expression of the core principles of Curriculum III at the tool level: **Model decision-making, Runtime implementation.**

The model should not have the opportunity to bypass the permission check, nor should it decide for itself that "not to read the document."

### 4.2 Parameter verification, overtime, retesting and thorium, etc.

The verification of the pre-implementation parameters is the first line of defence to intercept errors:

```python
validate_params(tool_name, arguments, tools):
    # 1. Read required and properties from tools
    # 2. Walk Through List → Missing returns missing required error
    # 3. Iterate over arguments → check type matches (integer cannot pass string)
    # → Check enum bounds (values must be allowed)
    # 4. Return None, any failed return structural error
```

The implementation of tools also requires time-out and retry protection. Core model:

```python
# Timeout: each tool sets an implementation time frame, timeout is interrupted
# Retry: retrying only for the idempotent operations (read_files)✓,Send Mail✗),exponential backoff
# Both are applied uniformly through decorators or intermediates, not within tool functions

@timeout(30s)
@retry(max=2, backoff=exponential)
query_database(sql) → Read-only queries, et cetera → Safe Retry

@timeout(10s)
send_email(to, subject, body) → Non-prescriptive → No retry, prevent duplicates.
```

Key findings of the re-test strategy: **Is this operation consistent?** Read the file → to try again. Check the database (read-only) and try again. Sending an email can not simply retry (possibly repeat). The creation of an order cannot simply be repeated (possibly double deduction).

### 4.3 Misstructured

When tools fail, the quality of the information returned determines the quality of the next decision of the model.

Compare two errors to return:

```python
# Shit: I don't know what to do with this.
"Error: failed"

# Okay. The model will determine the next step.
{
  "status": "error",
  "error": {
    "code": "permission_denied",
    "message": "The file '/etc/passwd' is not within the permitted workspace',
    "retryable": false,
    "suggested_action": "Select the file under the workspace directory to retry."
  }
}
```

Structural error contains at least five fields: error code (%2) `code ` ), readable information (` message ` Whether to try again () ` retryable ` ), recommend next steps ( ` suggested_action ` ) Whether user intervention is required ( ` needs_user` ) I don't know. These five fields allow the model to make valid judgements in the next round, rather than making wild speculations about the word "failed".

### 4.4 Result processing: summary, page break, cut-off and transfer of resources

The result of the tool is often long - searching returns 20 pages, database returns 1,000 records, files with 100,000 words and test logs with thousands of lines. All of them would blow up windows and key information would be flooded.

| Methodology | Apply scene |
|---|---|
| Summary | Results long but critical information (search, API response) |
| Page Break | Results list long, step by step (database query) |
| Cut | Head and tail only (logs, long files) |
| Transfer of resources | Original result written to temporary file, model takes reference path |
| Structured extraction | Only fields, error codes, matches from the result |

### 4.5 How to shape the next round of decision-making

The four previous sections described how the tools were implemented and how the results were handled. But there's one key question that didn't go on: **When the tool results returned to the model, how did the model "use" it?**

Observation has a very special position in the utility connection-- It is the end point of the previous round (the tool is implemented) and the starting point of the next round (the model is based on it for decision-making). This dual identity determines the quality of the design of the Observation directly affecting the quality of the operation of the entire ring.

#### 4.5.1 The essence of Observation: providing a basis for the next round of decision-making

Let's start with a specific comparison. Let's assume the model is switched. `read_file("notes.md")`, file does not exist.

**Bad Observation:**

```text
Error: failed
```

The model gets this, and it doesn't know if the file doesn't exist, it doesn't have enough privileges, the disk is full or the network is broken. It can only guess. Wrong guess, wrong next move, wrong user sees Agent in gibberish. 

**Good Observation:**

```json
{
  "status": "error",
  "error": {
    "code": "file_not_found",
    "message": "'notes.md' does not exist in workspace.",
    "retryable": false,
    "suggested_action": "Please confirm the file path, or use list_files to view available files in the workspace."
  }
}
```

When the model gets this, it makes a reasonable judgment immediately:

```python
Thought: File does not exist. I should list the documents under the workspace so that users can see what options are available.
Action: list_files()
Observation: ["notes.txt", "readme.md", "src/"]
Thought: No notes.md, but there's one notes.txt, probably the user miscarded the file name.
Action: ask_user("No notes.md, but notes.txt. You mean this file??")
```

This contrast illustrates the central design principle of Observation: **Observation is not reporting on what happened, but is providing the basis for the next round of decision-making.** It should allow models to judge what to do next without speculation.

#### 4.5.2 Four dimensions of the Observation design

- **Dimension I: Information integrity.**
- **Dimension II: Structural consistency.**
- **Dimension Three: Context Perceptions.**
- **Dimension IV: Modelability.**

![Four dimensions of the Observation design](../assets/course-04-observation-four-dimensions.svg)

#### 4.5.3 Common Observation design errors

| Error | Performance | Consequences | Rehabilitation |
|---|---|---|---|
| **Too brief** | Only return `"ok" ` or ` "failed"` | The model can't judge the next step. | Returns structured state code, summary and context tips |
| **Too long** | Fill in all 5000 line logs | The context is broken, the key information before the model forgets. | Summary/cut with 4.4 outcome-processing strategy |
| **Malformed format** | Each tool returns in a different format | Models need to adapt to new formats and increase the probability of error. | Harmonization `{status, summary, data, error}` Structure |
| **Lack of context** | Just report "Find 3 results", not what it is, not the mission. | Models don't know what these results mean. | Add `context_hint` Fields |
| **Make a mistake about empty results** | `search` No match found, boom, return error | The model thinks the tools are broken, maybe they're changed or abandoned. | Distinguishing between tool failure and tool failure without matching. |
| **Error code doesn't make any difference** | All errors returned. `"error"` | The model doesn't know if it's a temporary failure or a permanent error. | Use ` retryable` Field Identification |

---

## Chapter 5: Permissions and security - Make tools manageable

### 5.1 Why tool privileges are not optional

Once a tool is called to influence the outside world, access and security will change from "first day to first day." Agent may perform dangerous operations: read private files, write or delete files, query user data, send messages, modify configuration, create orders, trigger payments, publish content.

The problem with these operations is not that the model has bad intentions, but that the model does not understand the consequences. It's not about "this operation deletes user data for three years," but it's about "the next token, based on probability distribution, may be Delete."

### 5.2 Risk classification and default strategy

Risk classification of tools first:

```python
Risk level (from low to high):
  L1 READ_ONLY_LOW   — Read public information, search_web pages → auto(Auto-execution)
  L2 READ_ONLY_MED   — Read user files, query databases → auto
  L3 WRITE_LOW       — Write drafts, generate local temporary files → confirm(Prior to implementation)
  L4 WRITE_HIGH      — Modify user files, update database records → confirm
  L5 DANGEROUS       — Delete, Pay, Publish, Online Configuration → deny(Default Ban)
```

Risk classification is not once and for all. It will also be judged in relation to operational objects (delegate temporary files vs delete production data), scope of operations (modify a field vs modify the entire table), and user authorization levels.

### 5.3 Deny-first and minimum privileges

There are only two core principles of competence design:

```text
Deny-first:Default refusal, explicitly allowed.
Minimum permission: Only the smallest tool, minimum data, minimum field required by Agent for the current task.
```

Code realization:

```python
PermissionChecker:
    rules = []   # Rule list, Deny priority above allow

    allow(tool, condition=None)   # Add permitted rules
    deny(tool, condition=None)    # Add rejection rule

    check(tool_name, arguments):
        for rule in rules:
            if rule is deny and match(rule, tool_name, arguments):
                return False          # Hit, Danny. → Direct refusal
        for rule in rules:
            if rule is allow and match(rule, tool_name, arguments):
                return True           # All right. → Allow
        return False                  # I didn't get hit. → Default Rejection

# Configure Example
checker.allow("read_file", path in "workspace/")
checker.deny("read_file",  path contains "secrets")
checker.allow("write_file", path in "workspace/output/")
checker.deny("delete_file")               # Total prohibition
checker.deny("send_email")
# Unlisted Tools → Default Rejection
```

The main point of this design is that **deny has priority over allow, and non-listed tools are defaulted.** This clears the security boundaries of the access strategy -- you don't have to worry about "if there's a dangerous tool missing," because automatics that are not listed are useless.

### 5.4 Progressive delegation of authority and audit log

Agent products should not start with a large number of permanent privileges for users. A progressive mandate is more legitimate:

- Low-risk read-only actions can be implemented automatically.
- Medium-risk actions require confirmation, and the user can choose "Remember this session".
- High-risk movements need to be identified every time and are not allowed to be remembered.
- Users can withdraw authorized permissions at any time.

The audit log is the basis for the tool to call security - there's no log, and you can't check the problem:

```json
{
  "timestamp": "2026-06-30T10:42:18Z",
  "user_id": "user_123",
  "task_id": "task_20260630_001",
  "tool_call_id": "call_0007",
  "tool_name": "write_file",
  "arguments": {
    "path": "output/summary.md",
    "content_preview": "Course 4 Tool Mechanism Summary...",
    "content_sha256": "9f86d081884c7d659a2feaa0c55ad015"
  },
  "risk_level": "WRITE_LOW",
  "permission": {
    "result": "confirmed_by_user",
    "policy": "confirm_on_first_write",
    "confirmed_by": "user_123",
    "confirmed_at": "2026-06-30T10:42:21Z",
    "remember_scope": "session"
  },
  "execution": {
    "result": "success",
    "duration_ms": 184,
    "error": null
  }
}
```

Each of the audit logs answers: who, when, in which task, what tools to adjust, what parameters, the results of the authority check, who confirmed, and the results of the implementation. This is not only a compliance requirement, but also a basis for debugging and user trust.

---

## Chapter 6: Human-in-the-loop - Engaging people in high-risk decision-making

### 6.1 Models should not decide everything alone.

The tool mechanism comes here, and a key control point needs to be covered: **What action models can make their own decisions, and what actions must be identified by humans?**

The answer is that when the consequences of an action are irreversible, affect the true user or the model itself is not sufficiently confident, human beings should be drawn into the cycle.

Human-in-the-loop is not "Agent's temporary patch when it has insufficient capacity", but **the structural control points in the tool mechanisms**. It recognizes the fundamental fact that the model does not understand the consequences and that the ultimate responsibility lies with the person.

### 6.2 Trigger conditions and mode of intervention

Common trigger conditions:

- High-risk actions (deleted, paid, published, sent).
- The model itself indicates uncertainty (low confidence decision-making).
- Permissions are insufficient but may be authorized by the user.
- The action is irrevocable.
- Parameters are ambiguous, models in "guess."

User intervention is not just a "yes/no" choice. Complete interventions include confirmation of execution, rejection of action, modification of parameters, editing of plans, requests for interpretation, taking over of execution, rollback of results and additional information.

### 6.3 Identification of interfaces and feedback loops

When a high-risk action is confirmed, the presentation information must include, at a minimum, what the action is, the target, the scope of the impact, the parameters, whether it can be revoked, how it will be addressed after failure, and why the Agent recommendation is implemented. Users need to have enough context to judge, not just a "allowable" button.

User feedback must return to Agent status:

```python
handle_user_feedback(state, feedback):
    # Writing user feedback to state, influencing the next round of decision-making
    state.user_feedback = feedback
    state.history.append({step, type: "user_feedback", feedback})

    if feedback.type == "rejected":
        # User Refuse → Record the reason, and the model adjusts its policy to the next round.
        state.context_hint = "The previous round was rejected because:{reason}"
    elif feedback.type == "modified":
        # User modified arguments → Re-execut with modified parameters
        state.pending_action = {tool, arguments: modified_args}
    return state
```

If user feedback does not enter the state, the next round of Agent will make the same decision based on the old context and triggers the same confirmation again — the user will feel that he or she is repeatedly drawn to a system without memory.

---

## Chapter 7: MCP - Standardize access to tools

### What happens when more tools are available?

The preceding chapters assume that you manually defined and registered the tool in the code. This is fine when the number of tools is low (3-10). However, as the number of tools grows and the sources diversify, new problems arise:

- Each tool is accessed differently (REST API, gRPC, database connection, local functions).
- Tool description formats are not uniform (some with OpenAPI, some with custom JSON, some without documents).
- Tools need to be dynamically discovered (this tool is available today and may be offline tomorrow).
- Different Agent or applications require reuse of the same set of tools, but each requires an integrated code.

It's like buying every appliance requires a redecoration of the plug — unsustainable.

### 7.2 MCP and Function Calling

MCP (Model Context Protocol, published by Anthropic in 2024) solves the problem of "standardizing access to tools". The key to understanding its location is to separate MCP from Function Calling:

| Concept | Issues addressed | Layer |
|---|---|---|
| Function Calling | The model says, "What function do I call, what parameters?" | Model interface layer |
| MCP | How tool services are found, described, called and reused | Tool Access Layer |

They are not competitive relationships, but a relationship: MCP Server Exposure Tool, Agent Runtme discovers and calls the tool through these standard interfaces, then converts the tool description into a model Function Calling format that can be understood by the model, and Runtme actually implements through the MCP protocol after model decision-making.

### 7.3 Tools / Resources / Prompts

MCP defines three core objects. The following is a complete MCP Server definition example of what they are:

```python
# MCP Server Example of definition: a "document management" service

server = Server("file_manager")

# 1. Tools — Executable Actions (with name, description, parameters Schema)
@server.tool()
def read_file(path: str) -> str:
    """Reads text files under workspace. Use when the user specifies a specific filename. """

@server.tool()
def search_files(query: str, path: str) -> list:
    """Search file contents when the user asks whether a file contains X."""

# 2. Resources — Readable data resources (read-only, accessed through URI)
@server.resource("docs://{name}")
def get_document(name: str) -> str: ...

@server.resource("config://app")
def get_app_config() -> dict: ...

# 3. Prompts — Reusable reminder template (task level, load as required)
@server.prompt()
def code_review_template(diff: str) -> str:
    """Code review template defining review dimensions and output format."""

# Start: Two modes of transmission
server.run(transport="stdio")   # Local subprocess, suitable for developing debugging
server.run(transport="http")    # HTTP + SSE,Fit to a production environment, multiple Agent sharing
```

This example shows the full picture of MCP Server. Note the choice of two modes of transmission:

- **stdio**: Server is initiated as a sub-process to communicate with Client through standard input output. Fits to single machine development - simple, network configuration is not required, but Server life cycle binds the Client process.
- **HTTP/SSE**: Server runs as an independent HTTP service, Client is remotely connected by HTTP + Server-Sent Events. Fits to a production environment - Server can deploy independently, extend horizontally and be shared by multiple Agents.
- **Tools** ( `read_file ` 、 ` search_files` ): Agent can call an enforceable action. Each Tool has a name, description and parameters Schema (auto-generated by type note). Corresponding to the definition of tools discussed earlier in this course - MCP places the definition and implementation in the same Server.
- **Resources** ( `docs://{name}` 、 ` config://app `):Agent can read data resources. Tool executes action, source exposure data. Resources is read-only -- Agent can do it. ` docs://readme` This URI reads the document, but cannot modify it.
- **Prompts**( `code_review_template`): A reusable reminder template. The difference with System Prompt is that Prompt is at **task level** — Agent is loaded on demand when dealing with a given task, not always in context.

For Agent developers, MCP is worth turning "access to a new tool" from "writing an integrated code" to "connecting a MCP Server". This Server can be independently deployed, independently updated, shared by multiple Agents -- just like the editor connects to any language grammatical service through LSP.

#### 7.3.1 MCP Clinic: How to connect and call on the Agent side

Server defines the tool, and Clarent is responsible for discovery, connection and call. The following is an example of the use of MCP Client in Argentina:

```python
# MCP Client Core responsibilities: connectivity → Found → Registration → Call

class MCPToolProvider:
    clients: dict   # server_name → Client Connection
    tools: dict     # tool_name → {schema, callable}

    # ── Two modes of transmission──
    connect_stdio(name, command, args):
        # Commencing local subprocesses and communicating via standard input
        # Application: single machine development, zero network configuration

    connect_http(name, url):
        # Connect remote HTTP Server to maintain channel via SSE
        # Application: Server independent deployment, multiple Agent sharing

    # ── Two forms of registration──
    discover_and_register(server, client):
        # Link to call list tools() automatically discovered, dynamically registered
        # Advantages: Clint does not need to change the code after the Server update tool

    register_static(server, url, tool_defs):
        # Advance Declaration Tool Schema, lazy conect (connection only when first called)
        # Advantages: Start without reliance on Server Online

    # ── Call──
    call_tool(server, tool, args):
        # Call remote tool via MCP protocol to return to uniform format results

# ── Use in Agent Loop──
provider = MCPToolProvider()
provider.connect_stdio("file_manager", "python", ["mcp_server.py"])
provider.connect_http("weather", "http://tools.internal:8090/sse")

# Merge all tools into Unified Calling Schema → The model sees a uniform list.
all_tools = {provider.tools, local_tools}
```

This Clit example shows the complete way MCP works in Agent: **Two modes of transmission:**

- `connect_stdio`: Start local sub-processes and output communications through standard input. Suitable to develop debug-zero network configuration.
- `connect_http `: Connect remote HTTP Server (passed) `/sse ` End creates the Server-Sent Events Channel. Fit to a production environment - Server can be deployed independently, shared by multiple Agents, and scaled up independently.

**Two forms of registration:**

- **Dynamic finding** ( ` _discover_and_register `): Contact Server after call ` list_tools()` Automatically obtains a list of tools. Clint does not need to change the code after Server adds the tool. The disadvantage is to connect to Server to know what tools there are.
- **Static declaration** `register_static`: When you register, you clearly state "what tools this Server provides", and the model immediately sees Schema, the actual MCP connection is delayed until the first call. Fits to a tool list stable, or to a view that Server may temporarily not be available - Agent does not have to wait for all Servers to be ready at startup.

**Common bottom principle:** Regardless of the mode of transmission or registration, the model will always see a uniform Faction Calling format. MCP's role is to standardize "access", not to change the interactive models of models and tools.

### 7.4 When MCP was introduced

scene suitable for introduction of MCP:

- The tool comes from a variety of external services, each with a different mode of access.
- Multiple Agents or applications require reuse of the same set of tools.
- Tools need dynamic detection and hot updating.
- The team hopes that the tool service will be deployed and maintained independently.

**No need for** MCP scene:

- Only 2-3 local functions. That's what you're doing in class three and this class.
- Instrument boundaries are not stable and definitions are frequently adjusted.
- You're still learning the smallest loop, and you shouldn't introduce protocol layers.

The goal of introducing MCP in this class is not to get you into an MCP system immediately, but to let you know where it is and what it solves -- you know which direction to go when the number of tools changes from five to 50 a day.

---

## Chapter 8: Skill - Remittance into a capability package

### 8.1. From "rethinking" every time to "pack your experience."

Suppose you found out that Agent was always following this pattern in the code review mission:

```text
1. Read
2. Type of change judged (new/modified/deleted)
3. Document-by-document check for potential bug
4. Check if test coverage is sufficient
5. If the change involves a key path, run the relevant test
6. Organize review output by severity
```

Every mission model has to re-think these steps, waste Token, and occasionally miss the steps. That is the problem that Skill is going to solve: **Stable combination of tools and step experiences are packaged into reusable capability modules.**

Tool addresses "what can you do?" (reading files, running tests). Skill solves "how to do a type of job" (code review, document summary, data analysis). The relationship is like the screwdriver and the furniture assembly instructions. The former are tools, the latter tell you what tools, what sequences, how to deal with problems.

### 8.2 Structure of Skill

A Skill usually contains the following:

```python
CODE_REVIEW_SKILL = {
    name: "code_review"
    description: ""Check git diff, check bug, security, test cover and code quality."
    when_to_use: "User requests review, review code, check PR"
    when_not_to_use: "When the user asks what the code means, asks for a new code."
    tools_needed: [read_file, run_shell, search_text]

    recommended_steps:
        1. git diff → Get changes
        2. Type and scope of changes (additional/modified/deleted, which modules are involved)
        3. file-by-fileread_file → Check logical changes and boundary conditions
        4. search_text → Check Test Overwrite
        5. run_shell → Run key tests (only when changes involve key paths)
        6. Organisation by severity: Cristical> Major > Minor > Suggestion

    failure_handling:
        git_diff_empty → "Tell the user no change. Confirm branch."
        test_not_found → "The tag lacks test cover and does not block the process."
        diff_too_large → ""Summary and review in sequence."

    disabled_scenarios:
        - Not in directory without guit repository
        - Not used to review binary files
}
```

Skill is not a fixed process - the model can determine whether the recommended steps are fully followed or adjusted to the context. The key difference between this and Workflow is that Workflow is "you have to go in this order," and Skyll is "you should go in this way, but you can judge if you need to adjust."

### 8.3 Skill vs Tool vs Workflow

The three are easily confused and compared:

| Concept | Nature | Who decides to execute it? | Examples |
|---|---|---|---|
| Tool | Atomic Actions | Runtime execution, model selection | `read_file ` 、 ` run_tests` |
| Skill | Reusable mission capability kit | Models decide whether to use them, how to adjust them | Code review, document summary |
| Workflow | Fixed implementation process | System preset, cannot skip | Submitted for approval |

Skyll's border: it should make Agent more efficient, but not out of control for users and developers. If Skill hides a large number of invisible operations (e.g. quietly modified documents, silent notifications) it becomes a black box trap.

## After-school exercises

### Practice I: Design 5 tool definitions

Extension of 5 tools for the smallest Agent of course three. Each tool is written: toolname, description (including applicable and non-applicable scenarios), parameters Schema (type, constraint, default value), return value structure (success and failure), risk level.

### Practice II: Failed to select analytical tools

Design 5 user missions to judge which tools the model may fail to select and write the debug direction. At least cover: no, no, no, no, no.

### Practice III: Tool implementer to achieve access checks

Reference to codes 4.1 and 5.3 to achieve a structured version with parameters, permission checks, time overruns and errors `execute_tool_call` function. Configure Deny-first permission policy for at least 4 tools.

### Practice Four: Design a Skyll

Select a common task (code review, document summary, data analysis, competitive research) to design a complete Skill definition. Contains recommended steps, failed processing, disabled borders.

### Practice 5: Design Human-in-the-loop nodes

For the "Agent Generates and Sends Client Mail" scenario, the confirmation node is designed: when to trigger, to display what information, how the user can modify, how to continue after rejection.

---

## Runable Example

Following the completion of this course of practice, an example of a tool mechanism for running course IV can be found:

- [Example of a tool mechanism for course 4](../examples/course-04-tool-mechanism/README.md)

The example is based on the smallest Agent closed ring of course 3, which complements the tool definition, Schema, Deny-first permission policy, tool implementer, structured error, cut-off of results, re-testing, etc., and auditing logs. The examples provide two versions, Python and Node.js, which allow for an understanding of how Runtime uses the tool into a controlled mechanism.

---

## Acceptance and inspection standards

- [ ] I can draw a tool to call a full link and point to typical failure points in tool selection, parameter generation, execution, Observation, State Update.
- [ ] I can define tools for a real mission, including description, parameters Schema, return structure, risk level and applicable boundary.
- [ ] I can select the failure of the diagnostic tool, distinguishing between the definition of the tool, candidate route, missing context or miscalculation of the model.
- [ ] I can achieve a controlled tool implementer that covers the verification of parameters, Deny-first privileges, overtime, error structure, summary of results and audit logs.
- [ ] I can explain what MCP, Tool, Skill, Workflow and Human-in-the-loop address and choose the appropriate mechanism in the specific scene.

---

## References

- OpenAI Function Calling

<https://platform.openai.com/docs/guides/function-calling>

- Anthropic Tool Use

<https://docs.anthropic.com/en/docs/agents-and-tools/tool-use>

- Model Context Protocol

<https://modelcontextprotocol.io/>

- Anthropic Building Effective Agents

<https://www.anthropic.com/engineering/building-effective-agents>
