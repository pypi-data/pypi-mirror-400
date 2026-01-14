"""
ZatherEnv - Environment for Path Pack generation.

The environment's job is to package data for the agent.
It holds the trajectory, prompt config, and output path.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, Optional

from wbal import Environment

from zather.prompting import PromptConfig, load_prompt_config, render_prompt
from zather.sources.claude_code import load_claude_trajectory
from zather.sources.codex_cli import load_codex_trajectory
from zather.trajectory import Trajectory


class ZatherEnv(Environment):
    """
    Environment for zather Path Pack generation.

    Packages the trajectory data and prompt configuration for the agent.
    The agent reads from this environment and uses the submit_path_pack tool
    to write the output.
    """

    # Data
    trajectory: Trajectory | None = None
    prompt_config: PromptConfig | None = None

    # Paths
    output_path: Path | None = None

    # Rendered prompts (populated by load())
    system_prompt: str = ""
    user_prompt: str = ""

    # Environment description for the agent
    env: str = "You are generating a Path Pack from an agent session trajectory."

    @classmethod
    def load(
        cls,
        *,
        source: Literal["claude", "codex"],
        project_path: Path = Path.cwd(),
        session_id: Optional[str] = None,
        codex_session_file: Optional[Path] = None,
        output_path: Path,
        prompt_path: Path,
        model_override: Optional[str] = None,
        max_events: int = 250,
        max_chars: int = 1500,
        since: Optional[str] = None,
        until: Optional[str] = None,
        redact: bool = True,
    ) -> "ZatherEnv":
        """
        Load trajectory and prompts, returning a configured environment.

        This is the main factory method for creating a ZatherEnv.
        """
        # Load trajectory from source
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

        # Load prompt config
        prompt_config = load_prompt_config(prompt_path)
        if model_override:
            prompt_config.model = model_override

        # Render prompts
        system_prompt, user_prompt = render_prompt(prompt_config, trajectory)

        # Create task description
        task = f"Generate a Path Pack from the {source} session trajectory."

        return cls(
            trajectory=trajectory,
            prompt_config=prompt_config,
            output_path=output_path,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            task=task,
        )

    def get_initial_messages(self) -> list[dict[str, Any]]:
        """
        Get the initial messages for the agent.

        Returns system prompt + user prompt as the conversation start.
        """
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self.user_prompt},
        ]

    def observe(self) -> str:
        """Return observable state of the environment."""
        if self.trajectory:
            return (
                f"Trajectory loaded: {len(self.trajectory.events)} events from "
                f"{self.trajectory.meta.source} session {self.trajectory.meta.session_id}"
            )
        return "No trajectory loaded"
