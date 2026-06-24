/**
 * 最小 Agent Runtime 使用的本地工具实现。
 *
 * 工具刻意保持为普通函数。它们不决定 Agent 下一步做什么，只执行受边界约束的操作，
 * 并返回结构化 Observation，供 Runtime 写入状态。
 */
const fs = require("node:fs");
const path = require("node:path");

function success(summary, content = null) {
  // 构造统一的成功 Observation。
  return { status: "success", summary, content, error: null };
}

function error(code, message) {
  // 构造统一的失败 Observation。
  return { status: "error", summary: message, content: null, error: { code, message } };
}

function resolveWorkspacePath(workspace, requestedPath) {
  // 把相对路径限制在示例工作区内，避免工具越界访问。
  const workspaceRoot = path.resolve(workspace);
  const target = path.resolve(workspaceRoot, requestedPath);
  if (target !== workspaceRoot && !target.startsWith(workspaceRoot + path.sep)) {
    throw new Error("path is outside the example workspace");
  }
  return target;
}

function buildTools(workspace) {
  // 创建绑定到指定工作区的工具集合。
  function readFile({ path: filePath }) {
    try {
      const target = resolveWorkspacePath(workspace, filePath);
      if (!fs.existsSync(target)) {
        return error("file_not_found", `未找到文件: ${filePath}`);
      }
      if (!fs.statSync(target).isFile()) {
        return error("not_a_file", `路径不是文件: ${filePath}`);
      }
      const content = fs.readFileSync(target, "utf8");
      return success(`读取到 ${content.length} 个字符: ${filePath}`, content);
    } catch (err) {
      return error("path_not_allowed", err.message);
    }
  }
  readFile.description = "Read a UTF-8 text file from the workspace. Args: path.";

  function writeFile({ path: filePath, content }) {
    try {
      const target = resolveWorkspacePath(workspace, filePath);
      fs.mkdirSync(path.dirname(target), { recursive: true });
      fs.writeFileSync(target, content, "utf8");
      return success(`已写入 ${content.length} 个字符: ${filePath}`, { path: filePath });
    } catch (err) {
      return error("path_not_allowed", err.message);
    }
  }
  writeFile.description = "Write UTF-8 text into a workspace file. Args: path, content.";

  /**
   * Search query in text and return matching lines.
   *
   * 教学简化：text 由调用方传入（通常来自 readFile 的结果），
   * 让学习者看到"先读文件，再对内容搜索"的完整决策链。生产环境中
   * 可改为 searchFile(query, path) 让工具内部处理文件读取。
   */
  function searchText({ query, text }) {
    const matches = [];
    text.split(/\r?\n/).forEach((line, index) => {
      if (line.toLowerCase().includes(query.toLowerCase())) {
        matches.push({ line: index + 1, text: line });
      }
    });
    return success(`找到 ${matches.length} 条匹配`, matches);
  }
  searchText.description = "Search query in text and return matching lines. Args: query, text. 教学简化：text 由调用方传入，让学习者看到完整决策链。";

  return {
    read_file: readFile,
    write_file: writeFile,
    search_text: searchText,
  };
}

module.exports = { buildTools, success, error };
