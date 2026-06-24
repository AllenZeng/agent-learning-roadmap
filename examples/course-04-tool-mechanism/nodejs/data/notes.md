# Course 04 Notes

Tool use is not a single function call. It is a runtime chain:

LLM Decision -> Tool Selection -> Parameter Generation -> Permission Check -> Tool Execution -> Observation -> State Update

## Core mechanisms

1. Tool definitions need clear descriptions, parameter schemas, risk levels, and boundaries.
2. The Runtime validates required fields, types, and unknown arguments before execution.
3. Deny-first permissions reject tools that are not explicitly allowed.
4. Only idempotent tools should be retried after transient failures.
5. Long tool results should be summarized, truncated, or converted into resource references.
6. Audit logs record tool name, arguments, validation, permission, and execution results.

## Engineering principles

- The model proposes tool calls; the Runtime executes them.
- Tool errors should include code, retryable, suggestedAction, and needsUser.
- Risky actions need explicit permission or human confirmation.
