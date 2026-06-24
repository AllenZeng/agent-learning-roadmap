"""最小 Agent 示例的 LLM 适配层。

``ScriptedLLM`` 让离线演示和测试具备确定性。
``openai_responses_llm`` 展示真实模型调用边界：输入是组装后的上下文，输出必须是
Runtime 可解析的一条 JSON 决策。
"""

import json
import os
import random
import time
import urllib.error
import urllib.request
from typing import Any, Callable, Dict, Iterable, List, Optional


class ScriptedLLM:
    """用于测试和离线演示的确定性 LLM 替身。"""

    def __init__(
        self,
        decisions: Iterable[Dict[str, Any]],
        delay_seconds: Optional[Callable[[], float]] = None,
        sleep_fn: Callable[[float], None] = time.sleep,
    ):
        self._decisions: List[Dict[str, Any]] = list(decisions)
        self.calls: List[Dict[str, Any]] = []
        self._delay_seconds = delay_seconds
        self._sleep_fn = sleep_fn

    def __call__(self, context: Dict[str, Any]) -> Dict[str, Any]:
        call_context = dict(context)
        if self._delay_seconds is not None:
            latency = self._delay_seconds()
            call_context["simulated_latency_seconds"] = latency
            self._sleep_fn(latency)
        self.calls.append(call_context)
        if not self._decisions:
            return {"type": "fail", "thought": "No scripted decision remains.", "reason": "script_exhausted"}
        return self._decisions.pop(0)


def random_demo_latency_seconds() -> float:
    """模拟真实 LLM 调用的 1-3 秒响应耗时。"""
    return random.uniform(1, 3)


def openai_responses_llm(context: Dict[str, Any]) -> Dict[str, Any]:
    """调用 OpenAI Responses API，并解析模型返回的 JSON 决策。

    教学简化：这里直接把整个 context 序列化为 JSON 放进 user message，
    让学习者一眼看清传给 LLM 的完整上下文结构。生产环境中应该将 context
    的各个字段分别映射到 system prompt、user message、tool definitions 的
    对应位置，避免重复传递 tools 定义和完整 history 造成 token 浪费。
    """
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
