"""
ZatherAgent - Agent for generating Path Packs.

The agent's job is to interact with the data and produce output.
It uses the environment's trajectory data and writes the Path Pack.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field
from wbal import LM, Agent, GPT5MiniTester, tool

from zather.environment import ZatherEnv


class ZatherAgent(Agent):
    """
    Agent for generating Path Packs from session trajectories.

    Uses GPT5MiniTester (gpt-5-mini with minimal reasoning) by default.
    The agent receives the trajectory via the environment's initial messages
    and uses submit_path_pack to write the final output.
    """

    env: ZatherEnv
    lm: LM = Field(default_factory=GPT5MiniTester)

    # Track if we've submitted
    _submitted: bool = False

    @property
    def stopCondition(self) -> bool:
        """Stop when we've submitted the path pack."""
        return self._submitted

    def perceive(self) -> None:
        """
        Set up initial messages from the environment.

        Only populates messages on the first step (when empty).
        """
        if not self.messages:
            self.messages = self.env.get_initial_messages()

    @tool
    def submit_path_pack(self, content: str) -> str:
        """
        Submit the final Path Pack content.

        Call this tool when you have finished generating the Path Pack.
        The content will be written to the output file.

        Args:
            content: The complete Path Pack markdown content.

        Returns:
            Confirmation message.
        """
        if self.env.output_path is None:
            return "Error: No output path configured"

        self.env.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.env.output_path.write_text(content)
        self._submitted = True
        return f"Path Pack saved to {self.env.output_path}"

    def reset(self, clear_messages: bool = False) -> None:
        """Reset agent state."""
        super().reset(clear_messages=clear_messages)
        self._submitted = False


def build_path_pack(
    *,
    env: ZatherEnv,
    dry_run: bool = False,
) -> str | None:
    """
    Build a Path Pack using the ZatherAgent.

    Args:
        env: Configured ZatherEnv with trajectory and prompts loaded.
        dry_run: If True, just write the prompts without calling the LLM.

    Returns:
        The generated Path Pack content, or None if dry_run.
    """
    if dry_run:
        # Write prompts for inspection
        if env.output_path:
            env.output_path.parent.mkdir(parents=True, exist_ok=True)
            env.output_path.write_text(
                "\n".join(
                    [
                        "# Zather Dry Run",
                        "",
                        "## System Prompt",
                        "```text",
                        env.system_prompt.strip(),
                        "```",
                        "",
                        "## User Prompt",
                        "```text",
                        env.user_prompt.strip(),
                        "```",
                        "",
                    ]
                )
            )
        return None

    # Create and run the agent
    agent = ZatherAgent(env=env)
    agent.run()

    # Return the content if it was written
    if env.output_path and env.output_path.exists():
        return env.output_path.read_text()

    return None
