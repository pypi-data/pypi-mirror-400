"""
Minimal OpenAI wrapper for generating Path Packs.
"""

from __future__ import annotations

import os
import re
from typing import Any, Optional

from openai import OpenAI


def openai_generate_markdown(
    *,
    model: str,
    reasoning_effort: Optional[str],
    temperature: float,
    system_prompt: str,
    user_prompt: str,
    backend: str = "auto",
) -> str:
    backend = (backend or "auto").lower()
    if backend not in {"auto", "wbal", "openai"}:
        raise ValueError(f"Unknown backend: {backend}")

    if backend in {"auto", "wbal"}:
        try:
            return _wbal_generate_markdown(
                model=model,
                reasoning_effort=reasoning_effort,
                temperature=temperature,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
        except ImportError:
            if backend == "wbal":
                raise
        except Exception:
            if backend == "wbal":
                raise

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
    }
    if temperature is not None:
        kwargs["temperature"] = float(temperature)

    if reasoning_effort:
        kwargs["reasoning"] = {"effort": reasoning_effort}

    response = _responses_create_with_fallback(client.responses.create, kwargs)
    text = getattr(response, "output_text", None)
    if isinstance(text, str) and text.strip():
        return text
    return _fallback_extract_output_text(response)


def _wbal_generate_markdown(
    *,
    model: str,
    reasoning_effort: Optional[str],
    temperature: float,
    system_prompt: str,
    user_prompt: str,
) -> str:
    """
    WBAL-backed generation path.

    We intentionally keep it tool-free: it's just an LM invocation that returns markdown.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    try:
        from wbal.lm import LM as WBALLM  # noqa: F401
    except Exception as e:  # pragma: no cover
        raise ImportError("WBAL is not installed") from e

    # Importing wbal ensures we reuse the same OpenAI client conventions + Weave deps,
    # but we still do our own param-fallback handling.
    from wbal.lm import LM as WBALLM

    class ZatherWBALResponsesLM(WBALLM):
        model: str
        reasoning_effort: Optional[str] = None
        temperature: Optional[float] = None
        client: OpenAI

        def observe(self) -> str:  # type: ignore[override]
            return f"ZatherWBALResponsesLM(model={self.model})"

        def invoke(  # type: ignore[override]
            self,
            messages: list[dict[str, Any]],
            tools: list[dict[str, Any]] | None = None,
            mcp_servers: list[dict[str, Any]] | None = None,
        ) -> Any:
            kwargs: dict[str, Any] = {"model": self.model, "input": messages}
            if self.temperature is not None:
                kwargs["temperature"] = float(self.temperature)
            if self.reasoning_effort:
                kwargs["reasoning"] = {"effort": self.reasoning_effort}
            if tools or mcp_servers:
                combined = list(tools) if tools else []
                if mcp_servers:
                    combined.extend(mcp_servers)
                kwargs["tools"] = combined
            return _responses_create_with_fallback(self.client.responses.create, kwargs)

    lm = ZatherWBALResponsesLM(
        model=model,
        reasoning_effort=reasoning_effort,
        temperature=float(temperature) if temperature is not None else None,
        client=OpenAI(api_key=api_key),
    )
    response = lm.invoke(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
    text = getattr(response, "output_text", None)
    if isinstance(text, str) and text.strip():
        return text
    return _fallback_extract_output_text(response)

def _responses_create_with_fallback(create_fn: Any, kwargs: dict[str, Any]) -> Any:
    """
    Call `client.responses.create(**kwargs)` but retry once if the API rejects a parameter.

    Some models (e.g. GPT-5 family) reject `temperature`. We detect OpenAI's standard error
    string: `Unsupported parameter: 'temperature' ...` and remove the offending top-level
    kwarg, then retry once.
    """
    attempt_kwargs = dict(kwargs)
    for _attempt in range(2):
        try:
            return create_fn(**attempt_kwargs)
        except Exception as e:
            message = str(e)
            match = re.search(r"Unsupported parameter: '([^']+)'", message)
            if not match:
                raise

            param = match.group(1)
            if param in attempt_kwargs:
                attempt_kwargs.pop(param, None)
                continue
            if param.startswith("reasoning"):
                attempt_kwargs.pop("reasoning", None)
                continue
            raise


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
