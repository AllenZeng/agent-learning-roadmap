"""Local tool implementations used by the minimal Agent runtime.

Tools are intentionally kept as ordinary functions. They do not decide the agent's next action; they only perform bounded operations
and return structured Observations for the runtime to write into state.
"""

from pathlib import Path
from typing import Any, Callable, Dict, List


Tool = Callable[..., Dict[str, Any]]


def success(summary: str, content: Any = None) -> Dict[str, Any]:
    """Build a normalized success Observation."""
    return {"status": "success", "summary": summary, "content": content, "error": None}


def error(code: str, message: str) -> Dict[str, Any]:
    """Build a normalized failure Observation."""
    return {"status": "error", "summary": message, "content": None, "error": {"code": code, "message": message}}


def _resolve_workspace_path(workspace: Path, path: str) -> Path:
    """Constrain relative paths to the example workspace to prevent out-of-bounds tool access."""
    target = (workspace / path).resolve()
    workspace_root = workspace.resolve()
    if not str(target).startswith(str(workspace_root)):
        raise ValueError("path is outside the example workspace")
    return target


def build_tools(workspace: Path) -> Dict[str, Tool]:
    """Create a tool set bound to the specified workspace."""
    workspace = Path(workspace)

    def read_file(path: str) -> Dict[str, Any]:
        """Read a UTF-8 text file from the workspace. Args: path."""
        try:
            target = _resolve_workspace_path(workspace, path)
        except ValueError as exc:
            return error("path_not_allowed", str(exc))
        if not target.exists():
            return error("file_not_found", "File not found: %s" % path)
        if not target.is_file():
            return error("not_a_file", "Path is not a file: %s" % path)
        content = target.read_text(encoding="utf-8")
        return success("Read %d characters: %s" % (len(content), path), content)

    def write_file(path: str, content: str) -> Dict[str, Any]:
        """Write UTF-8 text into a workspace file. Args: path, content."""
        try:
            target = _resolve_workspace_path(workspace, path)
        except ValueError as exc:
            return error("path_not_allowed", str(exc))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return success("Wrote %d characters: %s" % (len(content), path), {"path": path})

    def search_text(query: str, text: str) -> Dict[str, Any]:
        """Search query in text and return matching lines. Args: query, text.

        Teaching simplification: text is passed by the caller, usually from read_file,
        so learners can see the full decision chain of reading a file before searching its content. In production,
        this could become search_file(query, path) so the tool handles file reading internally.
        """
        matches: List[Dict[str, Any]] = []
        for line_number, line in enumerate(text.splitlines(), start=1):
            if query.lower() in line.lower():
                matches.append({"line": line_number, "text": line})
        return success("Found %d matches" % len(matches), matches)

    return {"read_file": read_file, "write_file": write_file, "search_text": search_text}
