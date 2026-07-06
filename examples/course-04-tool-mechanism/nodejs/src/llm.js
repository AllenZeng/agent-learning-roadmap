/**
 * LLM adapter layer for the minimal Agent example.
 *
 * ScriptedLLM makes offline demos and tests deterministic.
 * deepSeekChatLLM demonstrates the real model-call boundary: input is the assembled context, and output must be
 * one JSON decision that the runtime can parse.
 */
const DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions";
const DEFAULT_DEEPSEEK_MODEL = "deepseek-v4";

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

async function deepSeekChatLLM(context) {
  /**
   * Call the DeepSeek Chat Completions API and parse the JSON decision returned by the model.
   *
   * Teaching simplification: serialize the whole context as JSON directly into the user message,
   * so learners can see the full context structure passed to the LLM at a glance. In production, context
   * fields should be mapped separately to the system prompt, user message, and tool definitions
   * to avoid wasting tokens by repeatedly passing tool definitions and full history.
   */
  const apiKey = process.env.DEEPSEEK_API_KEY;
  if (!apiKey) {
    throw new Error("DEEPSEEK_API_KEY is required for real LLM mode");
  }

  const response = await fetch(DEEPSEEK_API_URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: process.env.DEEPSEEK_MODEL || DEFAULT_DEEPSEEK_MODEL,
      messages: [
        { role: "system", content: context.system },
        {
          role: "user",
          content: `Output the next JSON decision based on the following Agent runtime context:
\n${JSON.stringify(context, null, 2)}`,
        },
      ],
    }),
  });

  if (!response.ok) {
    throw new Error(`DeepSeek API request failed: ${response.status} ${await response.text()}`);
  }

  const data = await response.json();
  const text = extractChatMessageText(data);
  if (!text) {
    throw new Error("DeepSeek response did not contain choices[0].message.content");
  }
  return JSON.parse(text);
}

function extractChatMessageText(data) {
  const content = data.choices?.[0]?.message?.content;
  return typeof content === "string" ? content.trim() : "";
}

const openAIResponsesLLM = deepSeekChatLLM;

module.exports = { ScriptedLLM, deepSeekChatLLM, openAIResponsesLLM, randomDemoLatencyMs };
