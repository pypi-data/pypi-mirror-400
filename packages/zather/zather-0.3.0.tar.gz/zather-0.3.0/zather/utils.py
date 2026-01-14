"""
Shared helpers.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import re


def parse_iso_timestamp(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    raw = value.strip()
    try:
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        dt = datetime.fromisoformat(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def ts_in_range(ts: Optional[str], since: Optional[datetime], until: Optional[datetime]) -> bool:
    if since is None and until is None:
        return True
    dt = parse_iso_timestamp(ts)
    if dt is None:
        return False
    if since is not None and dt < since:
        return False
    if until is not None and dt > until:
        return False
    return True


_SECRET_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "sk-REDACTED"),
    (re.compile(r"(?i)(openai_api_key\s*[:=]\s*)(\S+)"), r"\1REDACTED"),
    (re.compile(r"(?i)(wandb_api_key\s*[:=]\s*)(\S+)"), r"\1REDACTED"),
    (re.compile(r"(?i)(anthropic_api_key\s*[:=]\s*)(\S+)"), r"\1REDACTED"),
]


def redact_secrets(text: str) -> str:
    if not text:
        return text
    redacted = text
    for pattern, repl in _SECRET_PATTERNS:
        redacted = pattern.sub(repl, redacted)
    return redacted
