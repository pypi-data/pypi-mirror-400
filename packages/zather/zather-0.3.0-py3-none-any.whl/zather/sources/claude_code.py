"""
Claude Code session parsing (~/.claude/projects).
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from zather.trajectory import Trajectory, TrajectoryEvent, TrajectoryMeta


def _claude_projects_dir() -> Path:
    return Path.home() / ".claude" / "projects"


def _path_to_project_dir(path: Path) -> str:
    return str(path).replace("/", "-").replace("\\", "-")


def _find_project_dir(project_path: Path) -> Optional[Path]:
    projects_dir = _claude_projects_dir()
    project_name = _path_to_project_dir(project_path.resolve())
    direct = projects_dir / project_name
    if direct.exists():
        return direct
    if not projects_dir.exists():
        return None
    for d in projects_dir.iterdir():
        if d.is_dir() and str(project_path) in d.name.replace("-", "/"):
            return d
    return None


def list_claude_sessions(project_path: Path, *, limit: int = 20) -> list[str]:
    project_dir = _find_project_dir(project_path)
    if not project_dir:
        return [f"No Claude Code project dir found for: {project_path}"]

    sessions: list[tuple[float, str]] = []
    for f in project_dir.glob("*.jsonl"):
        if not f.name.startswith("agent-") and f.stat().st_size > 0:
            sessions.append((f.stat().st_mtime, f.stem))
    sessions.sort(reverse=True)

    out: list[str] = []
    for mtime, sid in sessions[:limit]:
        out.append(f"{sid}  ({datetime.fromtimestamp(mtime).isoformat(timespec='seconds')})")
    return out


def load_claude_trajectory(
    *,
    project_path: Path,
    session_id: Optional[str],
    max_events: int,
    max_chars: int,
    since: Optional[str] = None,
    until: Optional[str] = None,
    redact: bool = True,
) -> Trajectory:
    project_dir = _find_project_dir(project_path)
    if not project_dir:
        raise FileNotFoundError(f"No Claude Code project dir found for: {project_path}")

    if session_id is None:
        # pick most recent non-agent file
        candidates = [
            f
            for f in project_dir.glob("*.jsonl")
            if not f.name.startswith("agent-") and f.stat().st_size > 0
        ]
        if not candidates:
            raise FileNotFoundError(f"No Claude Code sessions found in: {project_dir}")
        candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        session_id = candidates[0].stem

    session_file = project_dir / f"{session_id}.jsonl"
    if not session_file.exists():
        raise FileNotFoundError(f"Session file not found: {session_file}")

    from zather.utils import parse_iso_timestamp, redact_secrets, ts_in_range

    since_dt = parse_iso_timestamp(since)
    until_dt = parse_iso_timestamp(until)

    tool_outputs_by_id: dict[str, str] = {}
    discovered_cwd: Optional[str] = None
    started_at: Optional[str] = None

    # Pass 1: collect tool outputs and basic metadata.
    with session_file.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue

            ts = data.get("timestamp")
            if started_at is None and ts:
                started_at = ts
            if discovered_cwd is None and data.get("cwd"):
                discovered_cwd = str(data.get("cwd"))

            if not ts_in_range(ts, since_dt, until_dt):
                continue

            msg = data.get("message") or {}
            role = msg.get("role")
            content = msg.get("content")

            # Tool results sometimes arrive as role=user blocks with type=tool_result
            if isinstance(content, list):
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") == "tool_result":
                        tool_use_id = block.get("tool_use_id") or ""
                        out_text = _extract_text_from_blocks(block.get("content"))
                        if tool_use_id and out_text:
                            tool_outputs_by_id[str(tool_use_id)] = out_text[:max_chars]

    meta = TrajectoryMeta(
        source="claude",
        session_id=session_id,
        cwd=discovered_cwd or str(project_path.resolve()),
        started_at=started_at,
    )
    events: list[TrajectoryEvent] = []
    idx = 0

    # Pass 2: build the event stream.
    with session_file.open() as f:
        for line in f:
            if idx >= max_events:
                break
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue

            ts = data.get("timestamp")
            if not ts_in_range(ts, since_dt, until_dt):
                continue

            msg = data.get("message") or {}
            role = msg.get("role")
            content = msg.get("content")

            if role == "user":
                text = _extract_text_from_blocks(content)
                if text:
                    if redact:
                        text = redact_secrets(text)
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
                continue

            if role != "assistant":
                continue

            if not isinstance(content, list):
                continue

            for block in content:
                if idx >= max_events:
                    break
                if not isinstance(block, dict):
                    continue
                btype = block.get("type")
                if btype == "text":
                    text = block.get("text", "")
                    if text:
                        if redact:
                            text = redact_secrets(text)
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
                elif btype == "thinking":
                    thinking = block.get("thinking", "")
                    if thinking:
                        if redact:
                            thinking = redact_secrets(thinking)
                        events.append(
                            TrajectoryEvent(
                                idx=idx,
                                timestamp=ts,
                                actor="assistant",
                                kind="reasoning",
                                summary=_truncate_one_line(thinking, 200),
                                detail=_truncate(thinking, max_chars),
                            )
                        )
                        idx += 1
                elif btype == "tool_use":
                    tool_name = str(block.get("name") or "tool")
                    tool_input = block.get("input") or {}
                    tool_use_id = str(block.get("id") or "")
                    tool_input_text = json.dumps(tool_input, ensure_ascii=False)
                    if redact:
                        tool_input_text = redact_secrets(tool_input_text)
                    summary = f"{tool_name} { _truncate_one_line(tool_input_text, 180)}"

                    tool_input_detail = json.dumps(tool_input, indent=2, ensure_ascii=False)
                    if redact:
                        tool_input_detail = redact_secrets(tool_input_detail)
                    detail_lines = [tool_input_detail[:max_chars]]
                    tool_out = tool_outputs_by_id.get(tool_use_id)
                    if tool_out:
                        detail_lines.append("")
                        detail_lines.append("# tool_result")
                        out_text = tool_out
                        if redact:
                            out_text = redact_secrets(out_text)
                        detail_lines.append(_truncate(out_text, max_chars))
                    events.append(
                        TrajectoryEvent(
                            idx=idx,
                            timestamp=ts,
                            actor="tool",
                            kind="tool_use",
                            summary=summary,
                            detail="\n".join(detail_lines).strip(),
                        )
                    )
                    idx += 1

    return Trajectory(meta=meta, events=events)


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
                if block.get("type") in {"text", "input_text", "output_text"}:
                    parts.append(str(block.get("text") or ""))
        return "\n".join(p for p in parts if p)
    if isinstance(content, dict):
        if content.get("type") in {"text", "input_text", "output_text"}:
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
