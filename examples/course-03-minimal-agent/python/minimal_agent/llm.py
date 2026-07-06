"""LLM adapter layer for the minimal Agent example.

``ScriptedLLM`` makes offline demos and tests deterministic.
``deepseek_chat_llm`` demonstrates the real model-call boundary: input is the assembled context, and output must be
one JSON decision that the runtime can parse.
"""

import json
import os
import random
import time
import urllib.error
import urllib.request
from typing import Any, Callable, Dict, Iterable, List, Optional


class ScriptedLLM:
    """Deterministic LLM substitute for tests and offline demos."""

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
    """Simulate the 1-3 second response time of a real LLM call."""
    return random.uniform(1, 3)


DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEFAULT_DEEPSEEK_MODEL = "deepseek-v4-flash"


def deepseek_chat_llm(context: Dict[str, Any]) -> Dict[str, Any]:
    """Call the DeepSeek Chat Completions API and parse the JSON decision returned by the model.

    Teaching simplification: serialize the whole context as JSON directly into the user message,
    so learners can see the full context structure passed to the LLM at a glance. In production, context
    fields should be mapped separately to the system prompt, user message, and tool definitions
    to avoid wasting tokens by repeatedly passing tool definitions and full history.
    """
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY is required for real LLM mode")

    model = os.environ.get("DEEPSEEK_MODEL", DEFAULT_DEEPSEEK_MODEL)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": context["system"]},
            {
                "role": "user",
                "content": (
                    "Output the next JSON decision based on the following Agent runtime context:\n"
                    + json.dumps(context, ensure_ascii=False, indent=2, default=str)
                ),
            },
        ],
    }
    request = urllib.request.Request(
        DEEPSEEK_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": "Bearer %s" % api_key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError("DeepSeek API request failed: %s %s" % (exc.code, body))

    text = _extract_chat_message_text(data)
    if not text:
        raise ValueError("DeepSeek response did not contain choices[0].message.content")
    return json.loads(text)


def _extract_chat_message_text(data: Dict[str, Any]) -> str:
    choices = data.get("choices", [])
    if not choices:
        return ""
    message = choices[0].get("message", {})
    content = message.get("content", "")
    return content.strip() if isinstance(content, str) else ""


# Backward-compatible alias for older README snippets and imports.
openai_responses_llm = deepseek_chat_llm
