import json
from pathlib import Path

import pytest

from zather.sources import claude_code
from zather.sources.claude_code import load_claude_trajectory


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n")


def test_load_claude_trajectory_parses_tool_use_and_result(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Build a fake ~/.claude/projects structure.
    projects = tmp_path / "projects"
    projects.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(claude_code, "_claude_projects_dir", lambda: projects)

    repo = tmp_path / "repo"
    repo.mkdir()
    project_dir = projects / claude_code._path_to_project_dir(repo)
    project_dir.mkdir(parents=True, exist_ok=True)

    session_id = "sess-1"
    session_file = project_dir / f"{session_id}.jsonl"

    rows = [
        {
            "timestamp": "2025-12-17T04:59:14.298Z",
            "cwd": str(repo),
            "message": {"role": "user", "content": "do thing sk-abcdefghijklmnopqrstuvwxyz0123456789"},
        },
        {
            "timestamp": "2025-12-17T04:59:15.000Z",
            "cwd": str(repo),
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "text", "text": "ok"},
                    {"type": "tool_use", "id": "toolu_1", "name": "mcp__acp__Bash", "input": {"command": "ls"}},
                ],
            },
        },
        {
            "timestamp": "2025-12-17T04:59:16.000Z",
            "cwd": str(repo),
            "message": {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "toolu_1",
                        "content": [{"type": "text", "text": "Exit code: 0\nOutput: ok"}],
                    }
                ],
            },
        },
    ]
    _write_jsonl(session_file, rows)

    traj = load_claude_trajectory(
        project_path=repo,
        session_id=session_id,
        max_events=50,
        max_chars=500,
    )

    assert traj.meta.source == "claude"
    assert traj.meta.session_id == session_id
    assert traj.meta.cwd == str(repo)
    assert any(e.actor == "tool" and e.kind == "tool_use" for e in traj.events)

    # Redaction on by default.
    assert all("sk-abcdefghijklmnopqrstuvwxyz" not in (e.detail or "") for e in traj.events)


def test_load_claude_trajectory_respects_time_window(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    projects = tmp_path / "projects"
    projects.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(claude_code, "_claude_projects_dir", lambda: projects)

    repo = tmp_path / "repo"
    repo.mkdir()
    project_dir = projects / claude_code._path_to_project_dir(repo)
    project_dir.mkdir(parents=True, exist_ok=True)

    session_id = "sess-2"
    session_file = project_dir / f"{session_id}.jsonl"

    rows = [
        {"timestamp": "2025-12-17T04:59:14.000Z", "cwd": str(repo), "message": {"role": "user", "content": "a"}},
        {"timestamp": "2025-12-17T05:59:14.000Z", "cwd": str(repo), "message": {"role": "user", "content": "b"}},
    ]
    _write_jsonl(session_file, rows)

    traj = load_claude_trajectory(
        project_path=repo,
        session_id=session_id,
        max_events=50,
        max_chars=200,
        since="2025-12-17T05:00:00Z",
        until="2025-12-17T06:00:00Z",
    )

    assert [e.summary for e in traj.events if e.actor == "user"] == ["b"]
