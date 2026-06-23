/**
 * 最小 Agent 示例的 LLM 适配层。
 *
 * ScriptedLLM 让离线演示和测试具备确定性。
 * openAIResponsesLLM 展示真实模型调用边界：输入是组装后的上下文，输出必须是
 * Runtime 可解析的一条 JSON 决策。
 */
class ScriptedLLM {
  constructor(decisions) {
    this.decisions = [...decisions];
    this.calls = [];
  }

  async call(context) {
    this.calls.push(context);
    if (this.decisions.length === 0) {
      return {
        type: "fail",
        thought: "No scripted decision remains.",
        reason: "script_exhausted",
      };
    }
    return this.decisions.shift();
  }
}

async function openAIResponsesLLM(context) {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    throw new Error("OPENAI_API_KEY is required for real LLM mode");
  }

  const response = await fetch("https://api.openai.com/v1/responses", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: process.env.OPENAI_MODEL || "gpt-4.1-mini",
      input: [
        { role: "system", content: context.system },
        {
          role: "user",
          content: `请基于以下 Agent 运行时上下文输出下一步 JSON 决策：\n${JSON.stringify(context, null, 2)}`,
        },
      ],
    }),
  });

  if (!response.ok) {
    throw new Error(`OpenAI API request failed: ${response.status} ${await response.text()}`);
  }

  const data = await response.json();
  const text = data.output_text || extractOutputText(data);
  if (!text) {
    throw new Error("OpenAI response did not contain output_text");
  }
  return JSON.parse(text);
}

function extractOutputText(data) {
  return (data.output || [])
    .flatMap((item) => item.content || [])
    .filter((content) => content.type === "output_text" || content.type === "text")
    .map((content) => content.text || "")
    .join("")
    .trim();
}

module.exports = { ScriptedLLM, openAIResponsesLLM };
