"""最小 Agent 示例的 LLM 适配层。

``ScriptedLLM`` 让离线演示和测试具备确定性。
``openai_responses_llm`` 展示真实模型调用边界：输入是组装后的上下文，输出必须是
Runtime 可解析的一条 JSON 决策。
"""

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, Iterable, List


class ScriptedLLM:
    """用于测试和离线演示的确定性 LLM 替身。"""

    def __init__(self, decisions: Iterable[Dict[str, Any]]):
        self._decisions: List[Dict[str, Any]] = list(decisions)
        self.calls: List[Dict[str, Any]] = []

    def __call__(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self.calls.append(context)
        if not self._decisions:
            return {"type": "fail", "thought": "No scripted decision remains.", "reason": "script_exhausted"}
        return self._decisions.pop(0)


def openai_responses_llm(context: Dict[str, Any]) -> Dict[str, Any]:
    """调用 OpenAI Responses API，并解析模型返回的 JSON 决策。"""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for real LLM mode")

    model = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
    payload = {
        "model": model,
        "input": [
            {"role": "system", "content": context["system"]},
            {
                "role": "user",
                "content": (
                    "请基于以下 Agent 运行时上下文输出下一步 JSON 决策：\n"
                    + json.dumps(context, ensure_ascii=False, indent=2, default=str)
                ),
            },
        ],
    }
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": "Bearer %s" % api_key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError("OpenAI API request failed: %s %s" % (exc.code, body))

    text = data.get("output_text")
    if not text:
        text = _extract_output_text(data)
    if not text:
        raise ValueError("OpenAI response did not contain output_text")
    return json.loads(text)


def _extract_output_text(data: Dict[str, Any]) -> str:
    parts: List[str] = []
    for item in data.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in ("output_text", "text"):
                parts.append(content.get("text", ""))
    return "".join(parts).strip()
