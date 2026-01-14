import json
from pathlib import Path

from zather.sources.codex_cli import load_codex_trajectory


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n")


def test_load_codex_trajectory_parses_core_events(tmp_path: Path) -> None:
    session = tmp_path / "rollout.jsonl"
    rows = [
        {
            "timestamp": "2026-01-07T20:04:17.869Z",
            "type": "session_meta",
            "payload": {"id": "sess-1", "timestamp": "2026-01-07T20:04:17.846Z", "cwd": "/repo"},
        },
        {
            "timestamp": "2026-01-07T20:04:18.000Z",
            "type": "event_msg",
            "payload": {"type": "user_message", "message": "hello", "images": []},
        },
        {
            "timestamp": "2026-01-07T20:04:19.000Z",
            "type": "event_msg",
            "payload": {"type": "agent_reasoning", "text": "thinking..."},
        },
        {
            "timestamp": "2026-01-07T20:04:20.000Z",
            "type": "response_item",
            "payload": {"type": "function_call", "name": "shell_command", "arguments": "{\"command\":\"ls\"}", "call_id": "c1"},
        },
        {
            "timestamp": "2026-01-07T20:04:21.000Z",
            "type": "response_item",
            "payload": {"type": "function_call_output", "call_id": "c1", "output": "Exit code: 0\nOutput: ok"},
        },
        {
            "timestamp": "2026-01-07T20:04:22.000Z",
            "type": "response_item",
            "payload": {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "done"}]},
        },
    ]
    _write_jsonl(session, rows)

    traj = load_codex_trajectory(
        session_id=None,
        session_file=session,
        max_events=50,
        max_chars=500,
    )

    assert traj.meta.source == "codex"
    assert traj.meta.session_id == "sess-1"
    assert traj.meta.cwd == "/repo"
    assert len(traj.events) >= 5
    assert any(e.kind == "tool_call" for e in traj.events)
    assert any(e.kind == "tool_result" for e in traj.events)


def test_load_codex_trajectory_respects_time_window(tmp_path: Path) -> None:
    session = tmp_path / "rollout.jsonl"
    rows = [
        {
            "timestamp": "2026-01-07T20:04:17.869Z",
            "type": "session_meta",
            "payload": {"id": "sess-2", "timestamp": "2026-01-07T20:04:17.846Z", "cwd": "/repo"},
        },
        {
            "timestamp": "2026-01-07T20:04:18.000Z",
            "type": "event_msg",
            "payload": {"type": "user_message", "message": "a", "images": []},
        },
        {
            "timestamp": "2026-01-07T20:05:18.000Z",
            "type": "event_msg",
            "payload": {"type": "user_message", "message": "b", "images": []},
        },
    ]
    _write_jsonl(session, rows)

    traj = load_codex_trajectory(
        session_id=None,
        session_file=session,
        max_events=50,
        max_chars=500,
        since="2026-01-07T20:05:00Z",
        until="2026-01-07T20:06:00Z",
    )

    assert [e.summary for e in traj.events if e.actor == "user"] == ["b"]
