"""
Agent runner for executing Path Packs and capturing session logs.

This module handles feeding a Path Pack to Codex CLI (or Claude Code)
and capturing the resulting session log for comparison.
"""

import json
import os
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import weave


@dataclass
class RunResult:
    """Result of running a Path Pack through an agent."""

    session_file: str
    exit_code: int
    duration_seconds: float
    error: Optional[str] = None


class AgentRunner:
    """
    Runs Path Packs through Codex CLI and captures the resulting session.

    The runner:
    1. Creates a temporary workspace that mirrors the original project
    2. Feeds the Path Pack as the initial prompt to Codex CLI
    3. Captures the new session JSONL file
    4. Returns the session for comparison with the original
    """

    def __init__(
        self,
        agent: str = "codex",
        model: str = "gpt-4.1",
        timeout_seconds: int = 300,
        sandbox: str = "read-only",
    ):
        self.agent = agent
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.sandbox = sandbox

    @weave.op
    def run(
        self,
        path_pack: str,
        target_cwd: str,
        capture_dir: Optional[str] = None,
    ) -> RunResult:
        """
        Run a Path Pack through the agent and capture the session.

        Args:
            path_pack: The Path Pack markdown content to feed to the agent.
            target_cwd: The working directory for the agent (should match original).
            capture_dir: Directory to save captured session. If None, uses temp dir.

        Returns:
            RunResult with the session file path and execution info.
        """
        if self.agent != "codex":
            raise NotImplementedError(f"Agent '{self.agent}' not yet supported")

        return self._run_codex(path_pack, target_cwd, capture_dir)

    def _run_codex(
        self,
        path_pack: str,
        target_cwd: str,
        capture_dir: Optional[str],
    ) -> RunResult:
        """Run Path Pack through Codex CLI."""
        import re

        # Create capture directory if needed (for saving the prompt)
        if capture_dir:
            capture_path = Path(capture_dir)
            capture_path.mkdir(parents=True, exist_ok=True)
        else:
            capture_path = Path(tempfile.mkdtemp(prefix="zather_eval_"))

        # Write the Path Pack to a temp file for the prompt
        prompt_file = capture_path / "path_pack_prompt.md"
        prompt_file.write_text(path_pack)

        # Build the Codex CLI command
        # Use `codex exec` for non-interactive execution
        cmd = [
            "codex",
            "exec",
            "--model",
            self.model,
            "--sandbox",
            self.sandbox,
            path_pack,  # The prompt
        ]

        start_time = time.time()
        session_id = None

        try:
            result = subprocess.run(
                cmd,
                cwd=target_cwd,
                timeout=self.timeout_seconds,
                capture_output=True,
                text=True,
            )
            exit_code = result.returncode

            # Parse session ID from codex output
            # Codex prints: "session id: 019ba05d-de70-7131-9f6f-2c8d3b4eda13"
            output = result.stdout + result.stderr
            match = re.search(r"session id: ([0-9a-f-]+)", output)
            if match:
                session_id = match.group(1)

            error = result.stderr if result.returncode != 0 else None

        except subprocess.TimeoutExpired:
            exit_code = -1
            error = f"Timeout after {self.timeout_seconds} seconds"

        except Exception as e:
            exit_code = -1
            error = str(e)

        duration = time.time() - start_time

        # Find the session file using the session ID
        session_file = None
        if session_id:
            session_file = self._find_codex_session(session_id)

        return RunResult(
            session_file=session_file or "",
            exit_code=exit_code,
            duration_seconds=duration,
            error=error,
        )

    def _find_codex_session(self, session_id: str) -> Optional[str]:
        """Find a codex session file by its ID."""
        codex_home = Path.home() / ".codex" / "sessions"
        if not codex_home.exists():
            return None

        # Search for session file containing the ID
        for session_file in codex_home.rglob("*.jsonl"):
            if session_id in session_file.name:
                return str(session_file)

        return None


def load_session_events(session_file: str) -> list[dict[str, Any]]:
    """Load events from a session JSONL file."""
    events = []
    with open(session_file) as f:
        for line in f:
            if line.strip():
                events.append(json.loads(line))
    return events


def extract_trajectory_summary(session_file: str) -> dict[str, Any]:
    """
    Extract a summary of the trajectory from a session file.

    Returns metrics like:
    - Number of tool calls
    - Types of tools used
    - Number of user/assistant turns
    - Total tokens used
    """
    events = load_session_events(session_file)

    tool_calls = []
    user_messages = 0
    assistant_messages = 0
    total_input_tokens = 0
    total_output_tokens = 0

    for event in events:
        event_type = event.get("type")
        payload = event.get("payload", {})

        if event_type == "event_msg":
            msg_type = payload.get("type")
            if msg_type == "user_message":
                user_messages += 1
            elif msg_type == "token_count":
                info = payload.get("info") or {}
                usage = info.get("last_token_usage") or {}
                total_input_tokens += usage.get("input_tokens", 0)
                total_output_tokens += usage.get("output_tokens", 0)

        elif event_type == "response_item":
            item_type = payload.get("type")
            if item_type == "function_call":
                tool_calls.append(payload.get("name", "unknown"))
            elif item_type == "message":
                role = payload.get("role")
                if role == "assistant":
                    assistant_messages += 1

    # Count tool types
    tool_types = {}
    for tool in tool_calls:
        tool_types[tool] = tool_types.get(tool, 0) + 1

    return {
        "num_tool_calls": len(tool_calls),
        "tool_types": tool_types,
        "user_messages": user_messages,
        "assistant_messages": assistant_messages,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "total_tokens": total_input_tokens + total_output_tokens,
    }
