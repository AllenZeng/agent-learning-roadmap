/**
 * 最小 Agent 示例的 LLM 适配层。
 *
 * ScriptedLLM 让离线演示和测试具备确定性。
 * openAIResponsesLLM 展示真实模型调用边界：输入是组装后的上下文，输出必须是
 * Runtime 可解析的一条 JSON 决策。
 */
class ScriptedLLM {
  constructor(decisions, options = {}) {
    this.decisions = [...decisions];
    this.calls = [];
    this.delayMs = options.delayMs;
    this.sleep = options.sleep || sleep;
  }

  async call(context) {
    const callContext = { ...context };
    if (this.delayMs) {
      const latencyMs = this.delayMs();
      callContext.simulatedLatencyMs = latencyMs;
      await this.sleep(latencyMs);
    }
    this.calls.push(callContext);
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

function randomDemoLatencyMs() {
  return 1000 + Math.floor(Math.random() * 2001);
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function openAIResponsesLLM(context) {
  /**
   * 调用 OpenAI Responses API，并解析模型返回的 JSON 决策。
   *
   * 教学简化：这里直接把整个 context 序列化为 JSON 放进 user message，
   * 让学习者一眼看清传给 LLM 的完整上下文结构。生产环境中应该将 context
   * 的各个字段分别映射到 system prompt、user message、tool definitions 的
   * 对应位置，避免重复传递 tools 定义和完整 history 造成 token 浪费。
   */
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

module.exports = { ScriptedLLM, openAIResponsesLLM, randomDemoLatencyMs };
