"""
Codex CLI session parsing (~/.codex/sessions/*.jsonl).
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from zather.trajectory import Trajectory, TrajectoryEvent, TrajectoryMeta


def _codex_sessions_root() -> Path:
    return Path.home() / ".codex" / "sessions"


def list_codex_sessions(*, limit: int = 20) -> list[str]:
    root = _codex_sessions_root()
    if not root.exists():
        return [f"No Codex sessions dir found: {root}"]

    files = sorted(
        root.glob("**/*.jsonl"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    out: list[str] = []
    for f in files[:limit]:
        sid, cwd, ts = _peek_codex_meta(f)
        mtime = datetime.fromtimestamp(f.stat().st_mtime).isoformat(timespec="seconds")
        out.append(f"{sid or f.name}  ({mtime})  cwd={cwd or 'unknown'}  file={f}")
    return out


def load_codex_trajectory(
    *,
    session_id: Optional[str],
    session_file: Optional[Path],
    max_events: int,
    max_chars: int,
    since: Optional[str] = None,
    until: Optional[str] = None,
    redact: bool = True,
) -> Trajectory:
    if session_file is None:
        if session_id is None:
            raise ValueError("Provide --session or --session-file for source=codex")
        session_file = _find_codex_session_file(session_id)
    session_file = Path(session_file).expanduser().resolve()
    if not session_file.exists():
        raise FileNotFoundError(f"Codex session file not found: {session_file}")

    sid, cwd, started_at = _peek_codex_meta(session_file)
    meta = TrajectoryMeta(
        source="codex",
        session_id=sid or (session_id or session_file.stem),
        cwd=cwd,
        started_at=started_at,
        notes={"session_file": str(session_file)},
    )

    events: list[TrajectoryEvent] = []
    idx = 0
    tool_calls: dict[str, dict[str, Any]] = {}
    recent_user_texts: list[str] = []
    recent_reasoning_texts: list[str] = []

    from zather.utils import parse_iso_timestamp, redact_secrets, ts_in_range

    since_dt = parse_iso_timestamp(since)
    until_dt = parse_iso_timestamp(until)

    with session_file.open() as f:
        for raw in f:
            if idx >= max_events:
                break
            raw = raw.strip()
            if not raw:
                continue
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue

            ts = data.get("timestamp")
            if not ts_in_range(ts, since_dt, until_dt):
                continue
            etype = data.get("type")
            payload = data.get("payload") or {}

            if etype == "event_msg":
                ptype = payload.get("type")
                if ptype == "user_message":
                    text = str(payload.get("message") or "")
                    if text:
                        if redact:
                            text = redact_secrets(text)
                        if any(text == prev for prev in recent_user_texts[-5:]):
                            continue
                        events.append(
                            TrajectoryEvent(
                                idx=idx,
                                timestamp=ts,
                                actor="user",
                                kind="message",
                                summary=_truncate_one_line(text, 200),
                                detail=_truncate(text, max_chars),
                            )
                        )
                        idx += 1
                        recent_user_texts.append(text)
                elif ptype == "agent_reasoning":
                    text = str(payload.get("text") or "")
                    if text:
                        if redact:
                            text = redact_secrets(text)
                        if any(text == prev for prev in recent_reasoning_texts[-5:]):
                            continue
                        events.append(
                            TrajectoryEvent(
                                idx=idx,
                                timestamp=ts,
                                actor="assistant",
                                kind="reasoning",
                                summary=_truncate_one_line(text, 200),
                                detail=_truncate(text, max_chars),
                            )
                        )
                        idx += 1
                        recent_reasoning_texts.append(text)
                continue

            if etype != "response_item":
                continue

            ptype = payload.get("type")
            if ptype == "message":
                role = payload.get("role")
                text = _extract_text_from_blocks(payload.get("content"))
                if redact and text:
                    text = redact_secrets(text)
                if role == "assistant" and text:
                    events.append(
                        TrajectoryEvent(
                            idx=idx,
                            timestamp=ts,
                            actor="assistant",
                            kind="message",
                            summary=_truncate_one_line(text, 200),
                            detail=_truncate(text, max_chars),
                        )
                    )
                    idx += 1
                elif role == "user" and text:
                    if any(text == prev for prev in recent_user_texts[-5:]):
                        continue
                    events.append(
                        TrajectoryEvent(
                            idx=idx,
                            timestamp=ts,
                            actor="user",
                            kind="message",
                            summary=_truncate_one_line(text, 200),
                            detail=_truncate(text, max_chars),
                        )
                    )
                    idx += 1
                    recent_user_texts.append(text)
            elif ptype == "function_call":
                call_id = str(payload.get("call_id") or "")
                name = str(payload.get("name") or "tool")
                args_raw = payload.get("arguments") or ""
                args_text = str(args_raw)
                try:
                    args_obj = json.loads(args_text) if args_text else {}
                except Exception:
                    args_obj = {"raw": args_text}
                if redact:
                    try:
                        args_obj = json.loads(redact_secrets(json.dumps(args_obj, ensure_ascii=False)))
                    except Exception:
                        pass
                tool_calls[call_id] = {"name": name, "args": args_obj}
                summary = f"{name} { _truncate_one_line(json.dumps(args_obj, ensure_ascii=False), 180)}"
                events.append(
                    TrajectoryEvent(
                        idx=idx,
                        timestamp=ts,
                        actor="tool",
                        kind="tool_call",
                        summary=summary,
                        detail=_truncate(json.dumps(args_obj, indent=2, ensure_ascii=False), max_chars),
                    )
                )
                idx += 1
            elif ptype == "function_call_output":
                call_id = str(payload.get("call_id") or "")
                output = str(payload.get("output") or "")
                if redact and output:
                    output = redact_secrets(output)
                tool = tool_calls.get(call_id, {})
                name = str(tool.get("name") or "tool")
                summary = f"{name} result { _truncate_one_line(output, 180)}"
                events.append(
                    TrajectoryEvent(
                        idx=idx,
                        timestamp=ts,
                        actor="tool",
                        kind="tool_result",
                        summary=summary,
                        detail=_truncate(output, max_chars),
                    )
                )
                idx += 1
            elif ptype == "reasoning":
                summary_blocks = payload.get("summary") or []
                text = _extract_text_from_blocks(summary_blocks)
                if text:
                    if redact:
                        text = redact_secrets(text)
                    if any(text == prev for prev in recent_reasoning_texts[-5:]):
                        continue
                    events.append(
                        TrajectoryEvent(
                            idx=idx,
                            timestamp=ts,
                            actor="assistant",
                            kind="reasoning",
                            summary=_truncate_one_line(text, 200),
                            detail=_truncate(text, max_chars),
                        )
                    )
                    idx += 1
                    recent_reasoning_texts.append(text)

    return Trajectory(meta=meta, events=events)


def _find_codex_session_file(session_id: str) -> Path:
    root = _codex_sessions_root()
    matches = sorted(
        root.glob(f"**/*{session_id}*.jsonl"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not matches:
        raise FileNotFoundError(f"No Codex session file found for session id: {session_id}")
    return matches[0]


def _peek_codex_meta(path: Path) -> tuple[Optional[str], Optional[str], Optional[str]]:
    try:
        with path.open() as f:
            first = f.readline().strip()
        data = json.loads(first)
        if data.get("type") != "session_meta":
            return None, None, None
        payload = data.get("payload") or {}
        return payload.get("id"), payload.get("cwd"), payload.get("timestamp")
    except Exception:
        return None, None, None


def _extract_text_from_blocks(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                btype = block.get("type")
                if btype in {"output_text", "input_text", "summary_text", "text"}:
                    parts.append(str(block.get("text") or ""))
        return "\n".join(p for p in parts if p)
    if isinstance(content, dict):
        btype = content.get("type")
        if btype in {"output_text", "input_text", "summary_text", "text"}:
            return str(content.get("text") or "")
    return ""


def _truncate(text: str, max_chars: int) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def _truncate_one_line(text: str, max_chars: int) -> str:
    collapsed = " ".join(text.split())
    return _truncate(collapsed, max_chars)
