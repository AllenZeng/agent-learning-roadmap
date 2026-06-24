"""最小 Agent Runtime 使用的本地工具实现。

工具刻意保持为普通函数。它们不决定 Agent 下一步做什么，只执行受边界约束的操作，
并返回结构化 Observation，供 Runtime 写入状态。
"""

from pathlib import Path
from typing import Any, Callable, Dict, List


Tool = Callable[..., Dict[str, Any]]


def success(summary: str, content: Any = None) -> Dict[str, Any]:
    """构造统一的成功 Observation。"""
    return {"status": "success", "summary": summary, "content": content, "error": None}


def error(code: str, message: str) -> Dict[str, Any]:
    """构造统一的失败 Observation。"""
    return {"status": "error", "summary": message, "content": None, "error": {"code": code, "message": message}}


def _resolve_workspace_path(workspace: Path, path: str) -> Path:
    """把相对路径限制在示例工作区内，避免工具越界访问。"""
    target = (workspace / path).resolve()
    workspace_root = workspace.resolve()
    if not str(target).startswith(str(workspace_root)):
        raise ValueError("path is outside the example workspace")
    return target


def build_tools(workspace: Path) -> Dict[str, Tool]:
    """创建绑定到指定工作区的工具集合。"""
    workspace = Path(workspace)

    def read_file(path: str) -> Dict[str, Any]:
        """Read a UTF-8 text file from the workspace. Args: path."""
        try:
            target = _resolve_workspace_path(workspace, path)
        except ValueError as exc:
            return error("path_not_allowed", str(exc))
        if not target.exists():
            return error("file_not_found", "未找到文件: %s" % path)
        if not target.is_file():
            return error("not_a_file", "路径不是文件: %s" % path)
        content = target.read_text(encoding="utf-8")
        return success("读取到 %d 个字符: %s" % (len(content), path), content)

    def write_file(path: str, content: str) -> Dict[str, Any]:
        """Write UTF-8 text into a workspace file. Args: path, content."""
        try:
            target = _resolve_workspace_path(workspace, path)
        except ValueError as exc:
            return error("path_not_allowed", str(exc))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return success("已写入 %d 个字符: %s" % (len(content), path), {"path": path})

    def search_text(query: str, text: str) -> Dict[str, Any]:
        """Search query in text and return matching lines. Args: query, text.

        教学简化：text 由调用方传入（通常来自 read_file 的结果），
        让学习者看到"先读文件，再对内容搜索"的完整决策链。生产环境中
        可改为 search_file(query, path) 让工具内部处理文件读取。
        """
        matches: List[Dict[str, Any]] = []
        for line_number, line in enumerate(text.splitlines(), start=1):
            if query.lower() in line.lower():
                matches.append({"line": line_number, "text": line})
        return success("找到 %d 条匹配" % len(matches), matches)

    return {"read_file": read_file, "write_file": write_file, "search_text": search_text}
