"""
Minimal OpenAI wrapper for generating Path Packs.
"""

from __future__ import annotations

import os
from typing import Any, Optional

from openai import OpenAI


def openai_generate_markdown(
    *,
    model: str,
    reasoning_effort: Optional[str],
    temperature: float,
    system_prompt: str,
    user_prompt: str,
) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    client = OpenAI(api_key=api_key)

    kwargs: dict[str, Any] = {
        "model": model,
        "input": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
    }

    if reasoning_effort:
        kwargs["reasoning"] = {"effort": reasoning_effort}

    response = client.responses.create(**kwargs)
    text = getattr(response, "output_text", None)
    if isinstance(text, str) and text.strip():
        return text
    return _fallback_extract_output_text(response)


def _fallback_extract_output_text(response: Any) -> str:
    try:
        output = getattr(response, "output", None) or response.get("output")  # type: ignore[attr-defined]
    except Exception:
        output = None
    if not output:
        return ""

    parts: list[str] = []
    for item in output:
        itype = getattr(item, "type", None) or (item.get("type") if isinstance(item, dict) else None)
        if itype != "message":
            continue
        content = getattr(item, "content", None) or (item.get("content") if isinstance(item, dict) else None)
        if not content:
            continue
        for block in content:
            btype = getattr(block, "type", None) or (block.get("type") if isinstance(block, dict) else None)
            if btype == "output_text":
                txt = getattr(block, "text", None) or (block.get("text") if isinstance(block, dict) else None)
                if txt:
                    parts.append(str(txt))
    return "\n".join(parts).strip()
