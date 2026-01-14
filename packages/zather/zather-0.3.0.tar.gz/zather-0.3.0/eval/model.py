"""
Weave Model for zather Path Pack generation.

Calls the actual zather CLI - we're testing the real tool, not a reimplementation.
"""

import subprocess
import tempfile
from pathlib import Path
from typing import Any, Optional

import weave


class ZatherModel(weave.Model):
    """
    Weave Model that generates Path Packs by calling the zather CLI.

    This ensures we're evaluating the actual tool, not a separate implementation.
    """

    model: str = "gpt-4.1-mini"
    max_events: int = 250
    max_chars: int = 1500
    weave_project: str = "zather-tmp"  # Default weave project for tracking CLI calls

    @weave.op
    def predict(
        self,
        session_file: str,
        session_name: str,
        target_cwd: str,
    ) -> dict[str, Any]:
        """
        Generate a Path Pack by calling the zather CLI.

        Args:
            session_file: Path to the session JSONL file.
            session_name: Human-readable name for the session.
            target_cwd: Original working directory (passed through for scorer).

        Returns:
            Dictionary with path_pack and metadata for the scorer.
        """
        # Create temp file for output
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            out_path = Path(f.name)

        # Call the actual zather CLI via Python to ensure we use the installed package
        import sys

        cmd = [
            sys.executable,
            "-m",
            "zather.cli",
            "build",
            "--source",
            "codex",
            "--session-file",
            session_file,
            "--out",
            str(out_path),
            "--model",
            self.model,
            "--max-events",
            str(self.max_events),
            "--max-chars",
            str(self.max_chars),
        ]

        # Add weave tracking if project is configured
        if self.weave_project:
            cmd.extend(["--weave-project", self.weave_project])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            return {
                "path_pack": "",
                "path_pack_length": 0,
                "error": result.stderr,
                "session_file": session_file,
                "target_cwd": target_cwd,
                "session_name": session_name,
            }

        # Read the generated path pack
        path_pack = out_path.read_text()
        out_path.unlink()  # Clean up

        return {
            "path_pack": path_pack,
            "path_pack_length": len(path_pack),
            # Pass through for scorer
            "session_file": session_file,
            "target_cwd": target_cwd,
            "session_name": session_name,
        }


class ZatherDryRunModel(weave.Model):
    """
    Dry-run version that shows prompts without calling the LLM.
    Useful for debugging prompt templates.
    """

    max_events: int = 250
    max_chars: int = 1500
    weave_project: Optional[str] = None  # No tracking by default for dry-run

    @weave.op
    def predict(
        self,
        session_file: str,
        session_name: str,
        target_cwd: str,
    ) -> dict[str, Any]:
        """Generate dry-run output (prompts only, no LLM call)."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            out_path = Path(f.name)

        import sys

        cmd = [
            sys.executable,
            "-m",
            "zather.cli",
            "build",
            "--source",
            "codex",
            "--session-file",
            session_file,
            "--out",
            str(out_path),
            "--max-events",
            str(self.max_events),
            "--max-chars",
            str(self.max_chars),
            "--dry-run",
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            return {
                "dry_run_output": "",
                "error": result.stderr,
                "session_file": session_file,
                "target_cwd": target_cwd,
                "session_name": session_name,
            }

        dry_run_output = out_path.read_text()
        out_path.unlink()

        return {
            "dry_run_output": dry_run_output,
            "session_file": session_file,
            "target_cwd": target_cwd,
            "session_name": session_name,
        }
