"""
Path Pack generation entrypoint.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal, Optional

from zather.prompting import PromptConfig, load_prompt_config, render_prompt
from zather.sources.claude_code import load_claude_trajectory
from zather.sources.codex_cli import load_codex_trajectory


def build_path_pack(
    *,
    source: Literal["claude", "codex"],
    project_path: Path,
    session_id: Optional[str],
    codex_session_file: Optional[Path],
    out_path: Path,
    prompt_path: Path,
    model_override: Optional[str],
    backend: str,
    max_events: int,
    max_chars: int,
    since: Optional[str],
    until: Optional[str],
    dry_run: bool,
    redact: bool,
) -> None:
    if source == "claude":
        trajectory = load_claude_trajectory(
            project_path=project_path,
            session_id=session_id,
            max_events=max_events,
            max_chars=max_chars,
            since=since,
            until=until,
            redact=redact,
        )
    else:
        trajectory = load_codex_trajectory(
            session_id=session_id,
            session_file=codex_session_file,
            max_events=max_events,
            max_chars=max_chars,
            since=since,
            until=until,
            redact=redact,
        )

    prompt_cfg: PromptConfig = load_prompt_config(prompt_path)
    if model_override:
        prompt_cfg.model = model_override

    system_prompt, user_prompt = render_prompt(prompt_cfg, trajectory)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    if dry_run:
        out_path.write_text(
            "\n".join(
                [
                    "# Zather Dry Run",
                    "",
                    "## System Prompt",
                    "```text",
                    system_prompt.strip(),
                    "```",
                    "",
                    "## User Prompt",
                    "```text",
                    user_prompt.strip(),
                    "```",
                    "",
                ]
            )
        )
        return

    from zather.lm import openai_generate_markdown

    markdown = openai_generate_markdown(
        model=prompt_cfg.model,
        reasoning_effort=prompt_cfg.reasoning_effort,
        temperature=prompt_cfg.temperature,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        backend=backend,
    )

    out_path.write_text(markdown)
