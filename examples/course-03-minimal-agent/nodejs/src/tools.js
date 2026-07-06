/**
 * Local tool implementations used by the minimal Agent runtime.
 *
 * Tools are intentionally kept as ordinary functions. They do not decide the agent's next action; they only perform bounded operations
 * and return structured Observations for the runtime to write into state.
 */
const fs = require("node:fs");
const path = require("node:path");

function success(summary, content = null) {
  // Build a normalized success Observation.
  return { status: "success", summary, content, error: null };
}

function error(code, message) {
  // Build a normalized failure Observation.
  return { status: "error", summary: message, content: null, error: { code, message } };
}

function resolveWorkspacePath(workspace, requestedPath) {
  // Constrain relative paths to the example workspace to prevent out-of-bounds tool access.
  const workspaceRoot = path.resolve(workspace);
  const target = path.resolve(workspaceRoot, requestedPath);
  if (target !== workspaceRoot && !target.startsWith(workspaceRoot + path.sep)) {
    throw new Error("path is outside the example workspace");
  }
  return target;
}

function buildTools(workspace) {
  // Create a tool set bound to the specified workspace.
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
   * Teaching simplification: text is passed by the caller, usually from readFile,
   * so learners can see the full decision chain of reading a file before searching its content. In production,
   * this could become searchFile(query, path) so the tool handles file reading internally.
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
