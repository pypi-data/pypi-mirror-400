from pathlib import Path

from zather.prompting import load_prompt_config, render_prompt
from zather.trajectory import Trajectory, TrajectoryEvent, TrajectoryMeta


def test_load_prompt_config_falls_back_when_missing(tmp_path: Path) -> None:
    missing = tmp_path / "missing.yaml"
    cfg = load_prompt_config(missing)
    assert cfg.name
    assert cfg.model
    assert isinstance(cfg.temperature, float)
    assert cfg.system_prompt
    assert "{trajectory_markdown}" in cfg.user_prompt_template


def test_render_prompt_injects_trajectory() -> None:
    cfg = load_prompt_config(Path("__definitely_missing__.yaml"))
    traj = Trajectory(
        meta=TrajectoryMeta(source="codex", session_id="s", cwd="/tmp"),
        events=[
            TrajectoryEvent(
                idx=0,
                timestamp="2026-01-01T00:00:00Z",
                actor="user",
                kind="message",
                summary="hi",
                detail="hi",
            )
        ],
    )
    system_prompt, user_prompt = render_prompt(cfg, traj)
    assert "Path Pack" in user_prompt
    assert "source:" in user_prompt
    assert "user/message" in user_prompt
    assert system_prompt.strip()
