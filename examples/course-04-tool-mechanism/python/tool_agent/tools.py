"""Course 04 tool mechanism example: tool definitions, argument validation, permissions, auditing, and Observation processing."""

from dataclasses import dataclass
from pathlib import Path
from time import monotonic
from typing import Any, Callable, Dict, Iterable, List, Optional, Set


# Observation is the tool result shown to the model. It is not the raw return value;
# it is a runtime-processed decision brief: success includes a summary and necessary
# data, while failure includes an error code and suggested next action.
Observation = Dict[str, Any]

# Tools in this example are still ordinary functions. Course 04 focuses on adding
# runtime mechanics around ordinary functions: definitions, validation,
# permissions, auditing, and result processing.
ToolHandler = Callable[..., Observation]


@dataclass
class ToolResult:
    """Normalized tool return structure.

    In course 03, tools directly return a `{status, summary, content, error}` dictionary.
    Course 04 keeps the same external structure but uses a small object to centralize success and failure construction,
    so each tool does not invent its own error format and confuse the model on the next turn.
    """

    status: str
    summary: str
    content: Any = None
    error: Optional[Dict[str, Any]] = None

    @classmethod
    def success(cls, summary: str, content: Any = None) -> "ToolResult":
        return cls(status="success", summary=summary, content=content, error=None)

    @classmethod
    def failure(
        cls,
        code: str,
        message: str,
        retryable: bool = False,
        suggested_action: str = "",
        needs_user: bool = False,
    ) -> "ToolResult":
        """Build a structured error.

        `retryable`, `suggested_action`, and `needs_user` are for the next LLM decision:
        they tell the model whether the error can be retried, how to correct it, and whether user input is needed.
        """
        return cls(
            status="error",
            summary=message,
            content=None,
            error={
                "code": code,
                "message": message,
                "retryable": retryable,
                "suggested_action": suggested_action,
                "needs_user": needs_user,
            },
        )

    def to_dict(self) -> Observation:
        return {"status": self.status, "summary": self.summary, "content": self.content, "error": self.error}


@dataclass
class ToolDefinition:
    """Complete tool definition.

    Course 03 only exposes function docstrings to the model; course 04 explicitly separates tool definitions:
    - `description` explains applicable and non-applicable cases to help the model choose tools.
    - `parameters` is a simplified JSON Schema that helps the runtime validate arguments.
    - `risk_level` and `idempotent` are used by permission and retry policies.
    - `handler` is the function that actually performs the action.
    """

    name: str
    description: str
    parameters: Dict[str, Any]
    handler: ToolHandler
    risk_level: str = "low"
    idempotent: bool = True
    max_retries: int = 0

    def to_context(self) -> Dict[str, Any]:
        """Return the safe tool view injected into LLM context.

        Note that `handler` is not exposed here; the model only sees tool descriptions and Schema and cannot execute directly.
        Actual execution must go through `execute_tool_call()`.
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "risk_level": self.risk_level,
            "idempotent": self.idempotent,
        }


class ToolRegistry:
    """Tool registry.

    The registry solves two problems:
    1. The runtime can find the actual definition and handler by tool name.
    2. Context Assembly can generate a unified tool list for the model.
    """

    def __init__(self, tools: Iterable[ToolDefinition], max_context_chars: int = 1200):
        self._tools = {tool.name: tool for tool in tools}
        # Maximum character budget before tool results enter context. Larger results become preview + ref,
        # so long files or logs are not pushed directly into the next LLM context.
        self.max_context_chars = max_context_chars

    def get(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def to_context_tools(self) -> List[Dict[str, Any]]:
        return [tool.to_context() for tool in self._tools.values()]


class PermissionPolicy:
    """Deny-first permission policy: reject any tool that is not explicitly allowed."""

    def __init__(self, allowed_tools: Optional[Set[str]] = None):
        self.allowed_tools = set(allowed_tools or set())

    def check(self, tool: ToolDefinition, arguments: Dict[str, Any]) -> bool:
        # The example policy authorizes only by tool name. Real systems usually also check user, resource scope,
        # paths or IDs in arguments, risk level, and whether human confirmation already exists.
        return tool.name in self.allowed_tools


def execute_tool_call(
    decision: Dict[str, Any],
    registry: ToolRegistry,
    permissions: PermissionPolicy,
    audit_log: Optional[List[Dict[str, Any]]] = None,
) -> Observation:
    """Execute the full tool path.

    This is the key change from course 03 to course 04: the Agent loop no longer calls functions directly.
    A model-produced tool call must pass through these steps in order:
    1. Tool-name check
    2. Tool existence check
    3. Argument structure check
    4. Schema argument validation
    5. Deny-first permission check
    6. Handler execution and idempotent retry
    7. Observation shaping
    8. Audit log recording
    """
    audit_log = audit_log if audit_log is not None else []
    requested_tool_name = decision.get("tool_name")
    arguments = decision.get("arguments", {})

    # Pylance/pyright infers `dict.get()` as `Any | None`. Narrow it to a
    # non-empty string before calling `registry.get(name: str)`, which also
    # lets the model receive a clearer missing_tool_name error.
    if not isinstance(requested_tool_name, str) or not requested_tool_name:
        observation = ToolResult.failure(
            "missing_tool_name",
            "Missing tool name: tool_name",
            suggested_action="Choose a tool_name from the available tool list",
        ).to_dict()
        _audit(audit_log, "", arguments, "validation", "denied", observation)
        return observation

    tool_name = requested_tool_name

    # Check the registry first instead of calling a function directly from a dict, so missing tools can return structured errors
    # and record the failure in audit_log.
    tool = registry.get(tool_name)
    if tool is None:
        observation = ToolResult.failure(
            "tool_not_found",
            "Tool does not exist: %s" % tool_name,
            suggested_action="Check the tool name or choose again from the available tool list",
        ).to_dict()
        _audit(audit_log, tool_name, arguments, "lookup", "denied", observation)
        return observation

    # arguments must be an object. The model may occasionally output a string, array, or null; the runtime
    # must intercept that before execution instead of leaking exceptions into tool handlers.
    if not isinstance(arguments, dict):
        observation = ToolResult.failure(
            "invalid_arguments",
            "Tool arguments must be a JSON object",
            suggested_action="Regenerate the arguments object",
        ).to_dict()
        _audit(audit_log, tool_name, arguments, "validation", "denied", observation)
        return observation

    # Schema validation runs before permission checks, so basic issues like missing arguments or type errors are not misreported as
    # permission problems, making root causes easier to debug.
    validation_error = _validate_arguments(tool, arguments)
    if validation_error:
        _audit(audit_log, tool_name, arguments, "validation", "denied", validation_error)
        return validation_error

    # Deny-first: tools are not executable by default unless allowed. This matters especially for medium-risk tools like write_file,
    # because even plausible model-generated arguments must be allowed uniformly by the runtime.
    if not permissions.check(tool, arguments):
        observation = ToolResult.failure(
            "permission_denied",
            "Tool '%s' is not permitted" % tool.name,
            suggested_action="Ask the user for authorization or choose an authorized low-risk tool",
            needs_user=True,
        ).to_dict()
        _audit(audit_log, tool_name, arguments, "permission", "denied", observation)
        return observation

    attempts = 0
    started_at = monotonic()
    while True:
        try:
            # Only here is the tool actually executed. All earlier steps only check whether it should be executed.
            raw = tool.handler(**arguments)
            # Raw tool results are not always suitable for the next context; this step applies truncation,
            # references, and metadata enrichment.
            observation = _shape_observation(raw, tool, arguments, registry.max_context_chars)
            observation["retry_count"] = attempts
            observation["duration_ms"] = int((monotonic() - started_at) * 1000)
            _audit(audit_log, tool_name, arguments, "execution", "allowed", observation)
            return observation
        except TimeoutError as exc:
            # Retry only idempotent tools. Read-file and query tools can usually be retried; write, send, and order-placement
            # tools with side effects should not be retried automatically.
            if tool.idempotent and attempts < tool.max_retries:
                attempts += 1
                continue
            observation = ToolResult.failure(
                "timeout",
                str(exc),
                retryable=tool.idempotent and attempts < tool.max_retries,
                suggested_action="Retry later or narrow the query scope",
            ).to_dict()
            observation["retry_count"] = attempts
            _audit(audit_log, tool_name, arguments, "execution", "error", observation)
            return observation
        except Exception as exc:
            observation = ToolResult.failure(
                type(exc).__name__,
                str(exc),
                retryable=False,
                suggested_action="Check arguments and the tool implementation",
            ).to_dict()
            observation["retry_count"] = attempts
            _audit(audit_log, tool_name, arguments, "execution", "error", observation)
            return observation


def build_tool_registry(workspace: Path, max_context_chars: int = 1200) -> ToolRegistry:
    """Build the example tool set.

    This intentionally includes only three tools so learners can observe how each tool-definition field affects behavior:
    - read_file: low risk, idempotent, retryable。
    - write_file: medium risk, non-idempotent, requires explicit authorization。
    - list_files: low risk, idempotent, used as the recovery path after file_not_found。
    """
    workspace = Path(workspace)

    def read_file(path: str) -> Observation:
        """Read a file inside the workspace.

        Tools must still perform path-boundary checks internally. Even with outer Schema and permissions, out-of-bounds paths are
        resource-level risks that each tool must guard against itself.
        """
        try:
            target = _resolve_workspace_path(workspace, path)
        except ValueError as exc:
            return ToolResult.failure(
                "path_not_allowed",
                str(exc),
                suggested_action="Choose a relative path inside the workspace",
                needs_user=True,
            ).to_dict()
        if not target.exists():
            return ToolResult.failure(
                "file_not_found",
                "File not found: %s" % path,
                suggested_action="Use list_files to view available files or ask the user to confirm the path",
                needs_user=True,
            ).to_dict()
        if not target.is_file():
            return ToolResult.failure("not_a_file", "Path is not a file: %s" % path).to_dict()
        content = target.read_text(encoding="utf-8")
        return ToolResult.success(
            "Read %d characters: %s" % (len(content), path),
            {"content": content, "path": path, "total_chars": len(content)},
        ).to_dict()

    def write_file(path: str, content: str) -> Observation:
        """Write a file inside the workspace.

        This is a medium-risk tool: the write itself is simple in the handler, but whether writing is allowed should be decided by
        `PermissionPolicy` before execution.
        """
        target = _resolve_workspace_path(workspace, path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return ToolResult.success("Wrote %d characters: %s" % (len(content), path), {"path": path}).to_dict()

    def list_files() -> Observation:
        """List workspace files.

        This tool is for error recovery: when read_file returns file_not_found, the model can
        list available files first, then ask the user for confirmation or switch to the correct path.
        """
        files = [str(path.relative_to(workspace)) for path in workspace.rglob("*") if path.is_file()]
        return ToolResult.success("Found %d files" % len(files), {"files": sorted(files)}).to_dict()

    return ToolRegistry(
        [
            ToolDefinition(
                name="read_file",
                description=(
                    "Read a local file in the workspace. Use when the user gives an explicit file path and asks to view, summarize, or search content."
                    "Do not use for internet search or paths outside the workspace."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Relative path inside the workspace, for example data/notes.md"}
                    },
                    "required": ["path"],
                },
                handler=read_file,
                risk_level="low",
                idempotent=True,
                max_retries=1,
            ),
            ToolDefinition(
                name="write_file",
                description=(
                    "Write a UTF-8 text file into the workspace. Use when the user explicitly asks to save results."
                    "Do not use to delete files or overwrite unconfirmed important files; write actions require permission."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Output path inside the workspace"},
                        "content": {"type": "string", "description": "Text content to write"},
                    },
                    "required": ["path", "content"],
                },
                handler=write_file,
                risk_level="medium",
                idempotent=False,
            ),
            ToolDefinition(
                name="list_files",
                description="List files inside the workspace. Use when the file name is uncertain or after read_file returns file_not_found.",
                parameters={"type": "object", "properties": {}, "required": []},
                handler=list_files,
                risk_level="low",
                idempotent=True,
            ),
        ],
        max_context_chars=max_context_chars,
    )


def _validate_arguments(tool: ToolDefinition, arguments: Dict[str, Any]) -> Optional[Observation]:
    """Perform minimal validation based on the tool argument Schema.

    The example implements only required-field, unknown-field, and basic type checks needed by the course. Real systems can integrate
    libraries such as `jsonschema`, Pydantic, or Zod to support rules like enum, minimum, and format.
    """
    schema = tool.parameters
    required = schema.get("required", [])
    properties = schema.get("properties", {})
    missing = [name for name in required if name not in arguments]
    if missing:
        return ToolResult.failure(
            "missing_required",
            "Missing required argument: %s" % ", ".join(missing),
            suggested_action="Please provide arguments: %s" % ", ".join(missing),
        ).to_dict()

    for name, value in arguments.items():
        prop = properties.get(name)
        if prop is None:
            return ToolResult.failure(
                "unknown_argument",
                "Unknown argument: %s" % name,
                suggested_action="Pass only arguments declared in the Schema",
            ).to_dict()
        expected_type = prop.get("type")
        if expected_type == "string" and not isinstance(value, str):
            return ToolResult.failure("type_error", "Argument '%s' must be a string" % name).to_dict()
        if expected_type == "integer" and not isinstance(value, int):
            return ToolResult.failure("type_error", "Argument '%s' must be an integer" % name).to_dict()
    return None


def _shape_observation(raw: Observation, tool: ToolDefinition, arguments: Dict[str, Any], max_chars: int) -> Observation:
    """Shape raw tool results into Observations suitable for injection into LLM context.

    In course 03, tool results entered state/history as-is. Course 04 adds a context budget:
    If a read returns very long text, the model only gets preview and `full_content_ref`; the full content stays in
    the tool result or an external resource so the next context is not flooded with long text.
    """
    if raw.get("status") != "success":
        return raw
    content = raw.get("content")
    if not isinstance(content, dict) or "content" not in content:
        return raw
    text = content["content"]
    if not isinstance(text, str) or len(text) <= max_chars:
        return raw
    half = max_chars // 2
    return {
        "status": "success",
        "summary": raw["summary"],
        "content_truncated": True,
        "preview": text[:half] + "\n... [truncated] ...\n" + text[-half:],
        "full_content_ref": content.get("path") or arguments.get("path"),
        "total_chars": len(text),
        "error": None,
    }


def _resolve_workspace_path(workspace: Path, path: str) -> Path:
    """Restrict model-generated paths to the workspace.

    This is the tool-layer safety boundary: the model may generate `../` or absolute paths, and the runtime cannot trust them.
    """
    target = (workspace / path).resolve()
    root = workspace.resolve()
    if target != root and not str(target).startswith(str(root) + "/"):
        raise ValueError("path is outside the example workspace")
    return target


def _audit(
    audit_log: List[Dict[str, Any]],
    tool_name: str,
    arguments: Any,
    stage: str,
    result: str,
    observation: Observation,
) -> None:
    """Record key points in the tool path.

    The audit log is not a full Trace for the model; it is a safety record for developers and systems:
    which tool, which arguments, at which stage it was allowed or rejected, and the final error code.
    """
    audit_log.append(
        {
            "tool_name": tool_name,
            "arguments": arguments,
            "stage": stage,
            "result": result,
            "status": observation.get("status"),
            "error_code": (observation.get("error") or {}).get("code"),
        }
    )
