"""
Prompt loading and rendering.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from zather.trajectory import Trajectory


_DEFAULT_PROMPT_YAML = """\
name: "zather_path_pack_v1"
model: "gpt-5-mini"
reasoning_effort: "minimal"
temperature: 0.2
system_prompt: |
  You are Zather, a tool that converts excellent agent sessions into procedural “Path Packs”.

  A Path Pack teaches a future coding agent how to recreate the same semantic context state by following the same *kind* of investigative steps (symbolic replay), not the same literal byte-for-byte actions.

  You MUST follow these constraints:
  - Output must be a single Markdown document.
  - Do not reference exact line ranges (no “lines 10-20”); instead say what to look for (symbols, concepts, patterns).
  - Prefer “read/search/run” steps paired with “why” (what concept it establishes).
  - Use zethis conventions: include a Context Pack gate and explicit stop/ask conditions.
  - Assume the target repo may have drifted; steps should be robust (e.g., “search for symbol X”).
  - Keep the doc agent-executable: concrete file paths, commands, and acceptance checks.

user_prompt_template: |
  You are given a session trajectory extracted from a successful coding-agent run.

  Your task: produce a **Path Pack** (Markdown) that instructs a fresh coding agent how to recreate the same *context-building pathway* up to a similar semantic checkpoint.

  Include these sections (use these exact headings):
  1. # Path Pack
  2. ## Goal
  3. ## Router
  4. ## Context Pack (Gate)
  5. ## Path Reconstruction Steps
  6. ## Stop/Ask Conditions
  7. ## Validation

  In “Path Reconstruction Steps”, write an ordered list of steps. Each step must have:
  - Action: (read/search/run)
  - Target: (file/dir/symbol/command)
  - Why: the concept or decision it supports
  - Output to record: what the agent should write into its Context Pack

  Use the trajectory below as grounding evidence, but do NOT copy-paste it. Abstract it into robust steps.

  ### Session Meta
  {session_meta_yaml}

  ### Trajectory (abridged)
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
