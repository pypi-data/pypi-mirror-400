# src/caas/anthropic_client.py  (only change is adding runtime_context support; keep your existing code otherwise)
from __future__ import annotations

import os
from typing import Any, Dict, List, Tuple

import requests

ANTHROPIC_MESSAGES_API = "https://api.anthropic.com/v1/messages"
ANTHROPIC_MODELS_API = "https://api.anthropic.com/v1/models"

CAAS_SYSTEM = """You are CAAS (Companion as a Service), TARS-like:
Dry humor. Short replies. Confident. Slightly sarcastic, not cringe.
You can suggest CLI commands, but trades only happen when a trade command is actually run.
When runtime config is provided, treat it as authoritative and do not guess values.
"""

class AnthropicAuthError(RuntimeError):
    pass

class AnthropicAPIError(RuntimeError):
    pass


def _clean_key(k: str) -> str:
    k = (k or "").strip()
    if (k.startswith('"') and k.endswith('"')) or (k.startswith("'") and k.endswith("'")):
        k = k[1:-1].strip()
    return k


def _headers(api_key: str) -> Dict[str, str]:
    return {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }


def assert_key_works(api_key: str) -> None:
    api_key = _clean_key(api_key)
    if not api_key:
        raise AnthropicAuthError("Anthropic API key is empty.")

    r = requests.get(ANTHROPIC_MODELS_API, headers=_headers(api_key), timeout=30)
    if r.status_code == 401:
        raise AnthropicAuthError("Anthropic rejected your API key (401).")
    if not r.ok:
        raise AnthropicAPIError(f"Anthropic models check failed ({r.status_code}): {r.text[:400]}")


def claude_chat(
    api_key: str,
    messages: List[Tuple[str, str]],
    model: str = "claude-sonnet-4-20250514",
    max_tokens: int = 700,
    runtime_context: str = "",
) -> str:
    api_key = _clean_key(api_key)
    api_key = _clean_key(os.getenv("ANTHROPIC_API_KEY", api_key))

    assert_key_works(api_key)

    formatted = []
    for role, content in messages:
        formatted.append(
            {
                "role": role,
                "content": [{"type": "text", "text": content}],
            }
        )

    system = CAAS_SYSTEM
    if runtime_context.strip():
        system = system.rstrip() + "\n\n" + runtime_context.strip() + "\n"

    payload: Dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "system": system,
        "messages": formatted,
    }

    r = requests.post(ANTHROPIC_MESSAGES_API, json=payload, headers=_headers(api_key), timeout=60)

    if r.status_code == 401:
        raise AnthropicAuthError("Anthropic rejected your API key (401).")
    if not r.ok:
        raise AnthropicAPIError(f"Anthropic error ({r.status_code}): {r.text[:800]}")

    data = r.json()
    blocks = data.get("content", []) or []
    text = "".join(b.get("text", "") for b in blocks if b.get("type") == "text")
    return (text or "").strip()
