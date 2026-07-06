"""课程四工具机制示例：工具定义、参数校验、权限、审计和 Observation 处理。"""

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
    """统一工具返回结构。

    course 03 里工具直接返回 `{status, summary, content, error}` 字典。
    course 04 保留同样的外部结构，但用一个小对象集中构造成功/失败返回，
    避免每个工具自己随意拼错误格式，导致模型下一轮无法稳定理解。
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
        """构造结构化错误。

        `retryable`、`suggested_action` 和 `needs_user` 是给下一轮 LLM 决策用的：
        它们告诉模型这个错误能否重试、应该怎么修正、是否需要用户介入。
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
    """工具的完整定义。

    课程三只把函数 docstring 暴露给模型；课程四把工具定义显式拆开：
    - `description` 说明适用/不适用场景，帮助模型选工具。
    - `parameters` 是简化版 JSON Schema，帮助 Runtime 校验参数。
    - `risk_level` 和 `idempotent` 给权限与重试策略使用。
    - `handler` 才是真正执行动作的函数。
    """

    name: str
    description: str
    parameters: Dict[str, Any]
    handler: ToolHandler
    risk_level: str = "low"
    idempotent: bool = True
    max_retries: int = 0

    def to_context(self) -> Dict[str, Any]:
        """返回注入 LLM 上下文的安全工具视图。

        注意这里不暴露 `handler`，模型只能看到工具说明和 Schema，不能直接执行。
        真正执行必须经过 `execute_tool_call()`。
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "risk_level": self.risk_level,
            "idempotent": self.idempotent,
        }


class ToolRegistry:
    """工具注册表。

    Registry 解决两个问题：
    1. Runtime 可以通过工具名找到实际定义和 handler。
    2. Context Assembly 可以统一生成给模型看的工具列表。
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
    """Deny-first 权限策略：未显式允许的工具一律拒绝。"""

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
    """执行完整工具链路。

    这是课程四相对课程三最关键的变化：Agent loop 不再直接调用函数。
    模型输出的 tool call 必须依次经过：
    1. 工具名检查
    2. 工具存在性检查
    3. arguments 结构检查
    4. Schema 参数校验
    5. Deny-first 权限检查
    6. handler 执行与幂等重试
    7. Observation 整形
    8. 审计日志记录
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
            "缺少工具名 tool_name",
            suggested_action="请从可用工具列表中选择一个 tool_name",
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
            "工具不存在: %s" % tool_name,
            suggested_action="检查工具名，或从可用工具列表中重新选择",
        ).to_dict()
        _audit(audit_log, tool_name, arguments, "lookup", "denied", observation)
        return observation

    # arguments must be an object. The model may occasionally output a string, array, or null; the runtime
    # must intercept that before execution instead of leaking exceptions into tool handlers.
    if not isinstance(arguments, dict):
        observation = ToolResult.failure(
            "invalid_arguments",
            "工具参数必须是 JSON object",
            suggested_action="重新生成 arguments 对象",
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
            "工具 '%s' 没有执行权限" % tool.name,
            suggested_action="请求用户授权，或选择已授权的低风险工具",
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
                suggested_action="稍后重试，或缩小查询范围",
            ).to_dict()
            observation["retry_count"] = attempts
            _audit(audit_log, tool_name, arguments, "execution", "error", observation)
            return observation
        except Exception as exc:
            observation = ToolResult.failure(
                type(exc).__name__,
                str(exc),
                retryable=False,
                suggested_action="检查参数和工具实现",
            ).to_dict()
            observation["retry_count"] = attempts
            _audit(audit_log, tool_name, arguments, "execution", "error", observation)
            return observation


def build_tool_registry(workspace: Path, max_context_chars: int = 1200) -> ToolRegistry:
    """构造示例工具集。

    这里故意只放 3 个工具，便于学习者观察每个工具定义字段如何影响行为：
    - read_file: 低风险、幂等、可重试。
    - write_file: 中风险、非幂等、需要显式授权。
    - list_files: 低风险、幂等，用于 file_not_found 后的恢复路径。
    """
    workspace = Path(workspace)

    def read_file(path: str) -> Observation:
        """读取 workspace 内文件。

        工具内部仍然要做路径边界检查。即使外层有 Schema 和权限，路径越界这种
        资源级风险也必须由工具自身兜底。
        """
        try:
            target = _resolve_workspace_path(workspace, path)
        except ValueError as exc:
            return ToolResult.failure(
                "path_not_allowed",
                str(exc),
                suggested_action="请选择 workspace 内的相对路径",
                needs_user=True,
            ).to_dict()
        if not target.exists():
            return ToolResult.failure(
                "file_not_found",
                "未找到文件: %s" % path,
                suggested_action="使用 list_files 查看可用文件，或请用户确认路径",
                needs_user=True,
            ).to_dict()
        if not target.is_file():
            return ToolResult.failure("not_a_file", "路径不是文件: %s" % path).to_dict()
        content = target.read_text(encoding="utf-8")
        return ToolResult.success(
            "读取到 %d 个字符: %s" % (len(content), path),
            {"content": content, "path": path, "total_chars": len(content)},
        ).to_dict()

    def write_file(path: str, content: str) -> Observation:
        """写入 workspace 内文件。

        这是中风险工具：写入本身在 handler 里很简单，但是否允许写入应该由
        `PermissionPolicy` 在执行前判断。
        """
        target = _resolve_workspace_path(workspace, path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return ToolResult.success("已写入 %d 个字符: %s" % (len(content), path), {"path": path}).to_dict()

    def list_files() -> Observation:
        """列出 workspace 文件。

        这个工具用于错误恢复：当 read_file 返回 file_not_found 时，模型可以
        先列出可用文件，再请求用户确认或改用正确路径。
        """
        files = [str(path.relative_to(workspace)) for path in workspace.rglob("*") if path.is_file()]
        return ToolResult.success("找到 %d 个文件" % len(files), {"files": sorted(files)}).to_dict()

    return ToolRegistry(
        [
            ToolDefinition(
                name="read_file",
                description=(
                    "读取 workspace 中的本地文件。适用于用户给出明确文件路径并要求查看、总结或搜索内容时。"
                    "不要用于搜索互联网、不要读取 workspace 外部路径。"
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "workspace 内相对路径，例如 data/notes.md"}
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
                    "向 workspace 写入 UTF-8 文本文件。适用于用户明确要求保存结果时。"
                    "不要用于删除、覆盖未确认的重要文件；写入动作需要权限。"
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "workspace 内输出路径"},
                        "content": {"type": "string", "description": "要写入的文本内容"},
                    },
                    "required": ["path", "content"],
                },
                handler=write_file,
                risk_level="medium",
                idempotent=False,
            ),
            ToolDefinition(
                name="list_files",
                description="列出 workspace 内文件。适用于文件名不确定或 read_file 返回 file_not_found 后。",
                parameters={"type": "object", "properties": {}, "required": []},
                handler=list_files,
                risk_level="low",
                idempotent=True,
            ),
        ],
        max_context_chars=max_context_chars,
    )


def _validate_arguments(tool: ToolDefinition, arguments: Dict[str, Any]) -> Optional[Observation]:
    """根据工具参数 Schema 做最小校验。

    示例只实现课程需要的必填、未知字段和基础类型检查。真实系统可以接入
    `jsonschema`、Pydantic 或 Zod 等库来支持 enum、minimum、format 等规则。
    """
    schema = tool.parameters
    required = schema.get("required", [])
    properties = schema.get("properties", {})
    missing = [name for name in required if name not in arguments]
    if missing:
        return ToolResult.failure(
            "missing_required",
            "缺少必填参数: %s" % ", ".join(missing),
            suggested_action="请补充参数: %s" % ", ".join(missing),
        ).to_dict()

    for name, value in arguments.items():
        prop = properties.get(name)
        if prop is None:
            return ToolResult.failure(
                "unknown_argument",
                "未知参数: %s" % name,
                suggested_action="只传入 Schema 中声明的参数",
            ).to_dict()
        expected_type = prop.get("type")
        if expected_type == "string" and not isinstance(value, str):
            return ToolResult.failure("type_error", "参数 '%s' 应为 string" % name).to_dict()
        if expected_type == "integer" and not isinstance(value, int):
            return ToolResult.failure("type_error", "参数 '%s' 应为 integer" % name).to_dict()
    return None


def _shape_observation(raw: Observation, tool: ToolDefinition, arguments: Dict[str, Any], max_chars: int) -> Observation:
    """把工具原始结果整理成适合注入 LLM 上下文的 Observation。

    课程三里工具结果原样进入 state/history。课程四增加了上下文预算：
    如果读取到很长的文本，只给模型 preview 和 `full_content_ref`，完整内容留在
    工具结果或外部资源中，避免下一轮上下文被长文本挤爆。
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
    """把模型生成的路径限制在 workspace 内。

    这是工具层的安全边界：模型可能生成 `../` 或绝对路径，Runtime 不能信任。
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
    """记录工具链路的关键节点。

    审计日志不是给模型看的完整 Trace，而是给开发者/系统看的安全记录：
    哪个工具、什么参数、在哪个阶段被允许或拒绝、最终错误码是什么。
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
