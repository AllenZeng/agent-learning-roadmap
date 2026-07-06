#!/usr/bin/env python3
"""
Course 05-06 Reflection example

An interactive REPL，text Reflection text：
  - V0：no reflection — Agent saw TypeError textcontinue execution
  - V1：format fix — Schema textfailedtext
  - V2：tool error handling — wrong argumenttriggerclassificationcompared withProcessingdecision
  - V3：test-driven handling — textNext stepdecision

Usage:
    python reflection_demo.py

In REPL mediumyou can:
  - text V0 medium Agent ignoreerrortext
  - text V1-V3 textaddtextProcessingtext
  - text，text Reflection looptext
"""

import sys
import os
from dataclasses import dataclass, field
from typing import Callable, Optional
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════
# Base types
# ═══════════════════════════════════════════════════════════════════════════

class ValidationStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"


@dataclass
class ActionResult:
    """Agent textResult"""
    output: str
    cost: float = 0.0
    attempt: int = 0


@dataclass
class ValidationResult:
    """External validatorstextResult（not model self-evaluation！)"""
    passed: bool
    message: str = ""
    evidence: str = ""
    error_type: str = ""  # schema_error | tool_param_error | test_failure | context_missing | env_error


@dataclass
class ReflectionResult:
    """texttimestext Reflection loopResult"""
    status: str  # success | stopped
    output: str = ""
    attempts: int = 0
    cost: float = 0.0
    reason: str = ""
    trace: list = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════
# Mock scenario data
# ═══════════════════════════════════════════════════════════════════════════

# Mock note content (used for citation validation)
MOCK_NOTES = {
    "agent-memory-mechanism.md": """
## Write decisions and forgetting mechanisms

Memory text session data is managed by MemoryStore managed。
expired session data is managed by decay() Inevery time start_session text，text _purge_old_records()。

Writetext src/memory/write.py mediumtext：
1. capacity guard：when store size exceeds max_size textrejectWrite
2. TTL text：when key text ttl textWrite

Note：Memory text clear_expired() method。expiration cleanuptext、passive。
""",
    "session-manager.md": """
## Session Manager API

session_manager.py text cleanup text session。
text MemoryStore.decay() trigger cascading cleanup，instead of directly operating on _store dictionary。

errortext（do nottext)：
    def cleanup(self):
        for sid in list(self._sessions.keys()):
            if self._sessions[sid].expired:
                del self._sessions[sid]  # Bypasses the cleanup logic in decay()!

text：
    def cleanup(self):
        self.memory_store.decay()  # Trigger the full expiration cleanup path
"""
}

# Mock test-suite results
MOCK_TEST_PASS = """============================= test session starts ==============================
collected 10 items

tests/test_memory.py ..........                                          [100%]

============================== 10 passed in 1.23s ==============================
"""

MOCK_TEST_FAIL = """============================= test session starts ==============================
collected 10 items

tests/test_memory.py ........F.                                          [100%]

=================================== FAILURES ===================================
______________________ test_memory_cleanup_on_session_end ______________________

    def test_memory_cleanup_on_session_end():
        mem = MemoryStore()
        mem.start_session("test")
        mem.write({"key": "value"})
        mem.end_session()
>       assert len(mem._store) == 0
E       AssertionError: assert 1 == 0
E        +  where 1 = len({'session:test': {'key': 'value'}})

tests/test_memory.py:28: AssertionError
========================= 1 failed, 9 passed in 1.45s =========================
"""

# "Correct code" and "wrong code" for V3
CORRECT_CLEANUP_CODE = '''
def cleanup(self):
    """clean expired session"""
    self.memory_store.decay()
'''

BUGGY_CLEANUP_CODE = '''
def cleanup(self):
    """clean expired session"""
    for sid in list(self._sessions.keys()):
        if self._sessions[sid].expired:
            del self._sessions[sid]
'''


# ═══════════════════════════════════════════════════════════════════════════
# External validators (note: these are external systems, not LLM self-evaluation!)
# ═══════════════════════════════════════════════════════════════════════════

def validate_json_schema(output: str) -> ValidationResult:
    """V1: JSON Schema text — deterministic rule check"""
    required_fields = ["tool_name", "args", "reason"]
    missing = [f for f in required_fields if f not in output]
    if missing:
        return ValidationResult(
            passed=False,
            message=f"Schema textfailed：Missingtext {', '.join(missing)}",
            evidence=f"textmediumtext: {[k for k in ['tool_name','args','reason'] if k in output]}",
            error_type="schema_error"
        )
    return ValidationResult(passed=True, message="Schema validation passed")


def validate_tool_params(params: dict) -> ValidationResult:
    """V2: tool argument validation — check whether arguments are within the valid range"""
    if "limit" in params:
        limit = params["limit"]
        if not isinstance(limit, int) or limit < 1 or limit > 100:
            return ValidationResult(
                passed=False,
                message=f"wrong argument：limit must be between 1-100 and，current value {limit}",
                evidence=f"tool returned: Error: limit must be 1-100 (got {limit})",
                error_type="tool_param_error"
            )
    if "query" in params:
        query = params["query"]
        if not query or not isinstance(query, str) or query.strip() == "":
            return ValidationResult(
                passed=False,
                message="wrong argument：query cannot be empty",
                evidence="tool returned: Error: query parameter is required and must be non-empty",
                error_type="tool_param_error"
            )
    return ValidationResult(passed=True, message="argument validation passed")


def validate_citation(output: str, notes: dict) -> ValidationResult:
    """V4: citation validation — textmediumtextknowledge basemediumFoundtext"""
    # Extract referenced API/entity names from output
    import re
    # Find references like `memory.clear_expired()`
    api_pattern = re.findall(r'`(\w+\.\w+)\(\)`', output)
    # Also find references of the form "API 'xxx'"
    named_pattern = re.findall(r"API '(\w+\.\w+)'", output)

    all_refs = set(api_pattern + named_pattern)

    for ref in all_refs:
        found = False
        for note_name, note_content in notes.items():
            if ref in note_content:
                found = True
                break
        if not found:
            return ValidationResult(
                passed=False,
                message=f"citation validationfailed：'{ref}' InnotesmediumtextFound",
                evidence=f"search './notes/' all files under，'{ref}' 0 matches",
                error_type="context_missing"
            )

    return ValidationResult(passed=True, message="text")


def validate_tests(code: str) -> ValidationResult:
    """V3: test-driven validation — run external test framework"""
    # Simulation: check whether the code uses the correct API
    if "memory_store.decay()" in code:
        return ValidationResult(passed=True, message="All tests passed (10/10)")
    elif "del self._sessions" in code:
        return ValidationResult(
            passed=False,
            message="test failed: test_memory_cleanup_on_session_end — AssertionError: assert 1 == 0",
            evidence=MOCK_TEST_FAIL,
            error_type="test_failure"
        )
    return ValidationResult(
        passed=False,
        message="test failed: textnonetext",
        evidence="SyntaxError: invalid syntax at line 3",
        error_type="test_failure"
    )


def validate_env_check(action_name: str) -> ValidationResult:
    """environment check — simulate external environment validation（such as git repo whether exists)"""
    if action_name == "git_log" and "--not-a-repo" in os.getcwd():
        return ValidationResult(
            passed=False,
            message="toolExecution failed: git log → fatal: not a git repository",
            evidence="fatal: not a git repository (or any of the parent directories): .git",
            error_type="env_error"
        )
    return ValidationResult(passed=True)


# ═══════════════════════════════════════════════════════════════════════════
# Feedback classifier
# ═══════════════════════════════════════════════════════════════════════════

def classify_feedback(validation: ValidationResult) -> str:
    """textResultclassificationtext"""
    return validation.error_type


# ═══════════════════════════════════════════════════════════════════════════
# Reflection loop - core implementation
# ═══════════════════════════════════════════════════════════════════════════

def reflection_loop(
    action: Callable[[Optional[dict], int], ActionResult],
    validate: Callable[[str], ValidationResult],
    max_retries: int = 3,
    cost_budget: float = 1.0,
    verbose: bool = True,
) -> ReflectionResult:
    """
    with Reflection execution loop。

    key design：
    - validate textExternal validators（tests、schema、citation comparison)，not model self-evaluation
    - textcorrection，textInput（prompt/arguments/context)，not just rerun
    - stopping conditions are hard-coded，not decided by the model
    """
    cost_spent = 0.0
    last_error = None
    trace = []

    for attempt in range(max_retries):
        # 1. Execute action (inject facts from the previous failure)
        result = action(last_error, attempt)
        cost_spent += result.cost
        trace.append(f"[attempt {attempt + 1}] executecomplete，cost ${result.cost:.2f}")

        # 2. External validation (not model self-evaluation!)
        validation = validate(result.output)
        trace.append(f"[attempt {attempt + 1}] validation: {'✅ pass' if validation.passed else '❌ ' + validation.message}")

        if validation.passed:
            if verbose:
                print(f"\n  ✅ Reflection success！rank {attempt + 1} timestext")
                print(f"     textcost: ${cost_spent:.3f}，text: {attempt + 1}")
            return ReflectionResult(
                status="success",
                output=result.output,
                attempts=attempt + 1,
                cost=cost_spent,
                trace=trace
            )

        # 3. Classify the failure and prepare the next handling context
        error_type = classify_feedback(validation)
        last_error = {
            "type": error_type,
            "message": validation.message,
            "evidence": validation.evidence,
        }
        trace.append(f"[attempt {attempt + 1}] textclassification: {error_type}")

        # 4. Stopping-condition check
        # 4a. Cost limit
        if cost_spent > cost_budget:
            trace.append(f"[stop] costover limit: ${cost_spent:.2f} > ${cost_budget:.2f}")
            if verbose:
                print(f"\n  🛑 costtext: ${cost_spent:.2f} > ${cost_budget:.2f}")
            return ReflectionResult(
                status="stopped", reason="cost_limit",
                attempts=attempt + 1, cost=cost_spent,
                output=result.output, trace=trace
            )

        # 4b. Same feedback repeats (feedback type and evidence are identical after handling)
        if attempt >= 1:
            # Simplified detection: if the same feedback type appears twice in a row, treat it as repeated feedback
            trace.append(f"[stop] same feedback repeated ({error_type})，already tried {attempt + 1} times")
            if verbose:
                print(f"\n  🛑 same feedback repeated stop: {error_type} has appeared consecutively {attempt + 1} times")
                print("     ProcessingtextfailedResult，textclassificationerror")
            return ReflectionResult(
                status="stopped", reason="repeated_failure",
                attempts=attempt + 1, cost=cost_spent,
                output=result.output, trace=trace
            )

        if verbose:
            print(f"  🔄 rank {attempt + 1} timesfailed ({error_type})，Processingtextretry...")
            print(f"     evidence: {validation.evidence[:100]}...")

    # Exceeded maximum retry count
    trace.append(f"[stop] Exceeded maximum retry count ({max_retries})")
    if verbose:
        print(f"\n  🛑 Exceeded maximum retry count: {max_retries}")
    return ReflectionResult(
        status="stopped", reason="max_retries_exceeded",
        attempts=max_retries, cost=cost_spent,
        output=result.output if 'result' in dir() else "", trace=trace
    )


# ═══════════════════════════════════════════════════════════════════════════
# Display helpers
# ═══════════════════════════════════════════════════════════════════════════

CHECK = "✅"
CROSS = "❌"
GEAR = "⚙️"
BULB = "💡"
STOP = "🛑"
LOOP = "🔄"


def print_header():
    print("\n" + "=" * 64)
    print("  Reflection — decision loop example based on feedback")
    print("=" * 64)
    print()
    print("  Scenario：knowledge assistant Agent textmediumtext Reflection performance")
    print()
    print("  Demo options:")
    print("    0 — V0 no reflection：Agent saw TypeError，continues writing changelog")
    print("    1 — V1 format fix：Schema textfailed → regenerate")
    print("    2 — V2 tool error handling：wrong argument → classification → decision → retrytext")
    print("    3 — V3 test-driven handling：test failed → locate assertion → correctiontext")
    print("    4 — full Reflection loop：trigger→classification→decision→Processing→verify or stop")
    print("    5 — stopping condition triggered：same feedback repeated → hard stop")
    print("    6 — comparison summary")
    print("    q — Exit")
    print()


def section(title: str):
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")


# ═══════════════════════════════════════════════════════════════════════════
# Demo scenarios
# ═══════════════════════════════════════════════════════════════════════════

def demo_v0_no_reflection():
    """
    V0：no reflection — Agent saw TypeError textcontinue execution。

    Corresponds to course 6.1：Agent text"Run tests"text TypeError，
    textitMove errortext Observation records it，then continues writing changelog。
    """
    section("V0：no reflection — Agent sawerror，text")

    print("""
  Scenario：releasetext。Agent text"Run tests"this step。

  [14:00] Agent Execute: npm test
  [14:01] text:
    TypeError: Cannot read properties of undefined (reading 'files')
        at runTests (test_runner.js:42:18)

  Agent textthistext。ittext？""")

    input("\n  [text Enter text Agent text...]")

    print("""
  Agent text"thought":
    "textcomplete。text TypeError。
     this may be a test environment issue。
     textMove ittextmedium。"

  Agent text:
    1. InStatusmediumtext: "tests: complete（text)"
    2. continue executionNext step: "Prepare changelog"
    3. final report: "✅ releasetextCompleted"

  ┌─────────────────────────────────────────────────────────────┐
  │ Problem：Agent Missing"text→classification→decision→Processingtext"text  │
  │                                                             │
  │ text，text Planning Problem，text Memory Problem。      │
  │ This is Reflection text。                                     │
  │                                                             │
  │ Analogy：dashboard red light turns on，the driver glances at it，writes in the log               │
  │       "14:32 text"，then continues at 120km/h forward。         │
  └─────────────────────────────────────────────────────────────┘
""")


def demo_v1_format_fix():
    """
    V1：format fix — Schema textfailedtext。

    Corresponds to course 6.4.2-6.4.4：Schema textfailed → textclassification → regenerate。
    """
    section("V1：format fix — Schema textfailed → regenerate")

    print("""
  Scenario：Agent text JSON，text tool_name、args、reason text。

  text Reflection starting point——text"making the model reflect on content quality"，
  but checking output format with deterministic rules。""")

    input("\n  [Press Enter to execute...]")

    # Simulate first attempt: missing field
    bad_output = '{"tool": "search_notes", "query": "memory cleanup"}'
    print(f"\n  Agent rank 1 timestext: {bad_output}")
    print(f"  Schema text: tool_name, args, reason text")

    def action_v1(prev_error, attempt):
        if attempt == 0:
            # First attempt: missing field
            return ActionResult(
                output='{"tool": "search_notes", "query": "memory cleanup"}',
                cost=0.01
            )
        else:
            # After correction: fill the missing field
            return ActionResult(
                output='{"tool_name": "search_notes", "args": {"query": "memory cleanup"}, "reason": "usertext memory text"}',
                cost=0.01
            )

    result = reflection_loop(
        action=action_v1,
        validate=validate_json_schema,
        max_retries=3,
        verbose=True
    )

    print(f"\n  📋 Reflection Result: {result.status}")
    print(f"     text: {result.output}")
    print(f"     attempt count: {result.attempts}，cost: ${result.cost:.3f}")

    print("""
  💡 Key points:
     - Schema text——text/does not exist，text
     - do nottext"text"——text，textusertext
     - This is Reflection text：text、text、texterror
""")


def demo_v2_tool_error_fix():
    """
    V2：tool error handling — wrong argumenttriggerclassificationcompared withProcessingdecision。

    Corresponds to course 6.4.2-6.4.4：tool returnedwrong argument → classification → textcorrectiontextretry。
    """
    section("V2：tool error handling — wrong argument → classification → decision")

    print("""
  Scenario：Agent call search_notes searchnotes，text。

  text Memory text，text query text、limit text。""")

    input("\n  [Press Enter to execute...]")

    bad_params = '{"tool_name": "search_notes", "args": {"query": "", "limit": 500}, "reason": "text memory text"}'
    print(f"\n  Agent rank 1 timescall: {bad_params}")

    def action_v2(prev_error, attempt):
        if attempt == 0:
            # First attempt: wrong argument
            return ActionResult(
                output='search_notes(query="", limit=500) → Error: limit must be 1-100',
                cost=0.02
            )
        elif attempt == 1:
            # Correction: change the argument value
            return ActionResult(
                output='search_notes(query="memory cleanup decay", limit=20) → Found 3 textResult',
                cost=0.02
            )

    def validate_v2(output: str) -> ValidationResult:
        if "Error: limit must be" in output:
            return ValidationResult(
                passed=False,
                message="wrong argument: limit=500 text",
                evidence="tool returned: Error: limit must be 1-100 (got 500)",
                error_type="tool_param_error"
            )
        if "Found" in output and "Result" in output:
            return ValidationResult(passed=True, message="textsuccess")
        return ValidationResult(
            passed=False,
            message="query cannot be empty",
            evidence="tool returned: Error: query parameter is required",
            error_type="tool_param_error"
        )

    result = reflection_loop(
        action=action_v2,
        validate=validate_v2,
        max_retries=3,
        verbose=True
    )

    print(f"\n  📋 Reflection Result: {result.status}")
    print(f"     attempt count: {result.attempts}，cost: ${result.cost:.3f}")

    print("""
  💡 Key points:
     - textclassificationtextProcessingtext：wrong argument→text，do nottext
     - textcorrectiontextInput：limit=500→20, query=""→"memory cleanup decay"
     - textretry（text)、textcorrection（wrong argument)、text（Permission denied)
""")


def demo_v3_test_driven_fix():
    """
    V3：test-driven handling — textNext stepdecision。

    Corresponds to course 6.4.2-6.4.5：test failed → textclassification → Processingtext → text。
    """
    section("V3：test-driven handling — test failed → text → correctiontext")

    print("""
  Scenario：Agent fix session_manager.py text cleanup method，text bug。

  Agent text decay() text，text _store dictionary。
  textthisProblem。""")

    input("\n  [Press Enter to execute...]")

    print(f"\n  Agent rank 1 timestext:")
    print(f"  {BUGGY_CLEANUP_CODE}")

    def action_v3(prev_error, attempt):
        if attempt == 0:
            return ActionResult(output=BUGGY_CLEANUP_CODE, cost=0.03)
        else:
            # Correction: use the correct API
            return ActionResult(output=CORRECT_CLEANUP_CODE, cost=0.03)

    result = reflection_loop(
        action=action_v3,
        validate=validate_tests,
        max_retries=3,
        verbose=True
    )

    print(f"\n  📋 Reflection Result: {result.status}")
    print(f"     after correctiontext: {result.output.strip()}")
    print(f"     attempt count: {result.attempts}，cost: ${result.cost:.3f}")

    print("""
  💡 Key points:
     - validate text，text"text LLM text"
     - after correctiontext——"text"text
     - text（text、text)，correctiontext
""")


def demo_full_reflection_loop():
    """
    full Reflection loop：text。

    Corresponds to course 6.4.6 text。
    """
    section("full Reflection loop：trigger→classification→decision→Processing→verify or stop")

    print("""
  Scenario：usertext Agent analysistextmediumtext bug。Agent textdoes not existtext API。

  text 6.4.6 text——Agent invented memory.clear_expired()，
  textthistext。""")

    input("\n  [Press Enter to execute...]")

    print("""
  [10:00] user："textProcessing session text，text。"

  Agent（rank 1 timesattempt)：
    "text session_manager.py text cleanup methodmedium。text
     memory.clear_expired()，textthis API In Memory modulemediumdoes not exist——
     text API text memory.remove_expired_sessions()。"
""")

    def action_citation(prev_error, attempt):
        if attempt == 0:
            # Hallucinated output: invented clear_expired()
            return ActionResult(
                output="text session_manager.py text cleanup methodmedium。text "
                       "`memory.clear_expired()`，textthis API In Memory modulemediumdoes not exist——"
                       "text API text `memory.remove_expired_sessions()`。",
                cost=0.02
            )
        else:
            # After correction: correct reference based on retrieval results
            return ActionResult(
                output="text session_manager.py text cleanup methodmedium。notestext Memory "
                       "textexpiration cleanuptext `decay()` → `_purge_old_records()` complete "
                       "[source: agent-memory-mechanism.md §Write decisions and forgetting mechanisms]。"
                       "text session_manager text cleanup text session text "
                       "decay()，textskip。",
                cost=0.02
            )

    result = reflection_loop(
        action=action_citation,
        validate=lambda output: validate_citation(output, MOCK_NOTES),
        max_retries=3,
        verbose=True
    )

    print(f"\n  📋 Reflection Result: {result.status}")
    print(f"     text: {result.output[:120]}...")
    print(f"     attempt count: {result.attempts}，cost: ${result.cost:.3f}")

    print("""
  💡 Key points:
     - text：validate() Return passed=false text
     - classificationtextProcessingtext：text→contextmissing→text
     - textcorrectiontextInput：rank 2 times prompt mediumtext
     - Processingtext：text"text"
""")


def demo_stop_conditions():
    """
    text：same feedback repeated → hard stop。

    Corresponds to course 6.4.5：text。
    """
    section("stopping condition triggered：same feedback repeated → hard stop")

    print("""
  Scenario：Agent text JSON textMissing tool_name text。

  rank 1 times：text tool_name
  rank 2 times：text tool_name（ProcessingtextInput，text prompt)
  → stopping condition triggered：same feedback repeated

  text，Agent textProcessing。""")

    input("\n  [Press Enter to execute...]")

    # Always return output missing tool_name (simulates ineffective handling)
    def action_stuck(prev_error, attempt):
        output = '{"tool": "search_notes", "args": {"query": "test"}}'
        return ActionResult(output=output, cost=0.01)

    result = reflection_loop(
        action=action_stuck,
        validate=validate_json_schema,
        max_retries=3,
        verbose=True
    )

    print(f"\n  📋 Reflection Result: {result.status}")
    print(f"     stopreason: {result.reason}")
    for t in result.trace:
        print(f"     {t}")

    print("""
  💡 Key points:
     - text——textrank 5 timesProcessingtext"this timetext"
     - text OR text：text
     - text（schema_error)，texterrorcharacterstext
     - textProcessingtextInput，texttimestext——text
""")


def demo_summary():
    """comparison summary"""
    section("Reflection text")

    print("""
  ┌──────────┬──────────────────────┬──────────────────────────────┐
  │ text     │ text               │ text                  │
  ├──────────┼──────────────────────┼──────────────────────────────┤
  │ V0 no reflection│ failedtext          │ text  │
  │ V1 text  │ Schema text+regenerate  │ text              │
  │ V2 tool  │ arguments/text/textclassificationProcessing│ tool callingtext                │
  │ V3 tests  │ test failed→text→Processingdecision│ text                │
  │ V4 text  │ knowledge basetext     │ textconfidence                │
  └──────────┴──────────────────────┴──────────────────────────────┘

  text：

  1. text
     Reflection textconfidencetextconfidence。
     → text、Schema text、text、usertext
     → text"text LLM text"

  2. classificationtextProcessing，text
     saw"test failed"text——This is not Reflection，text。
     → text"textfailed"：text？text？text？
     → textcorrectiontextInput，text prompt

  3. text，text
     text"text"text。
     → maximumretry 3 times、text 2 timestext、costtext $1
     → text，text

  ───────────────────────────────────────────────────────────────

  text Reflection：
     - textcorrection
     - failedcosttextlow，text
     - text（text)
     - text

  text：
    "text，textProcessingcostlowtextfailedcost，Reflection text。
     text'text'，text。"
""")


# ═══════════════════════════════════════════════════════════════════════════
# Main REPL
# ═══════════════════════════════════════════════════════════════════════════

DEMOS = {
    "0": ("V0 no reflection", demo_v0_no_reflection),
    "1": ("V1 format fix", demo_v1_format_fix),
    "2": ("V2 tool error handling", demo_v2_tool_error_fix),
    "3": ("V3 test-driven handling", demo_v3_test_driven_fix),
    "4": ("full Reflection loop", demo_full_reflection_loop),
    "5": ("stopping condition triggered", demo_stop_conditions),
    "6": ("comparison summary", demo_summary),
}


def main():
    print_header()

    while True:
        try:
            choice = input("  Please choosetext (0-6, q Exit): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Goodbye!")
            break

        if choice.lower() == "q":
            print("  Goodbye!")
            break

        if choice in DEMOS:
            name, fn = DEMOS[choice]
            fn()
            print(f"\n  ── {name} text ──")
            print("  （text：choose 6 text，q Exit)")
        else:
            print(f"  nonetext '{choice}'。pleaseInput 0-6 text q Exit。")


if __name__ == "__main__":
    main()
