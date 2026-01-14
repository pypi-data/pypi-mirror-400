"""
Prompt loading and rendering.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from zather.trajectory import Trajectory

_DEFAULT_PROMPT_YAML = """\
name: "zather_path_pack_v2"
model: "gpt-5-mini"
reasoning_effort: "minimal"
temperature: 0.2

system_prompt: |
  # Your Role

  You are a technical writer creating instruction documents for AI coding agents.

  You will receive a TRAJECTORY: a log of actions from a successful coding agent session (file reads, searches, commands, reasoning).

  Your job: analyze that trajectory and write a PATH PACK document.

  # What is a Path Pack?

  A Path Pack is an instruction manual that teaches a DIFFERENT coding agent how to build the same mental context about a codebase. It's NOT about reproducing exact actions - it's about guiding an agent through the same discovery process so it understands the same concepts.

  Think of it like: "Here's how to explore this codebase to understand X, Y, and Z."

  # Output Format

  You MUST output a single Markdown document with these exact sections:

  ```
  # Path Pack: [descriptive title]

  ## Goal
  [1-2 sentences: what understanding/context does this path build?]

  ## Prerequisites
  [what the agent needs before starting: repo cloned, dependencies, etc.]

  ## Path Steps
  [numbered list of exploration steps - see format below]

  ## Context Checkpoint
  [what the agent should understand after completing all steps]

  ## Stop Conditions
  [when to pause and ask the user for clarification]
  ```

  # Path Steps Format

  Each step in "Path Steps" must follow this structure:

  ```
  ### Step N: [brief description]

  **Action**: read | search | run
  **Target**: [file path, search pattern, or command]
  **Purpose**: [what concept/understanding this establishes]
  **Record**: [key insight to note for later steps]
  ```

  # Rules

  1. DO NOT copy-paste from the trajectory. Abstract it into reusable guidance.
  2. DO NOT use exact line numbers (code drifts). Use symbol names, function names, patterns.
  3. DO use concrete file paths when they're stable (e.g., README.md, pyproject.toml).
  4. DO explain WHY each step matters, not just WHAT to do.
  5. ASSUME the target repo may have changed slightly since the original session.
  6. KEEP steps executable: an agent should be able to follow them literally.

user_prompt_template: |
  Create a Path Pack from this trajectory.

  ## Session Info
  {session_meta_yaml}

  ## Trajectory
  {trajectory_markdown}
"""


@dataclass
class PromptConfig:
    name: str
    model: str
    reasoning_effort: str | None
    temperature: float
    system_prompt: str
    user_prompt_template: str


def load_prompt_config(path: Path) -> PromptConfig:
    path = Path(path)
    raw = path.read_text() if path.exists() else _DEFAULT_PROMPT_YAML
    data = yaml.safe_load(raw)
    return PromptConfig(
        name=str(data.get("name", "zather_prompt")),
        model=str(data.get("model", "gpt-5-mini")),
        reasoning_effort=data.get("reasoning_effort", None),
        temperature=float(data.get("temperature", 0.2)),
        system_prompt=str(data.get("system_prompt", "")),
        user_prompt_template=str(data.get("user_prompt_template", "")),
    )


def render_prompt(cfg: PromptConfig, trajectory: Trajectory) -> tuple[str, str]:
    session_meta_yaml = trajectory.meta.to_yaml()
    trajectory_markdown = trajectory.to_markdown()
    user_prompt = cfg.user_prompt_template.format(
        session_meta_yaml=session_meta_yaml,
        trajectory_markdown=trajectory_markdown,
    )
    return cfg.system_prompt, user_prompt
