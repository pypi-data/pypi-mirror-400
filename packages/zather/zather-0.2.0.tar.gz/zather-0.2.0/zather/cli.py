"""
CLI for zather.
"""

import argparse
import sys
from pathlib import Path

from zather.generate import build_path_pack
from zather.sources.claude_code import list_claude_sessions
from zather.sources.codex_cli import list_codex_sessions


def _add_common_build_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--out",
        "-o",
        type=Path,
        required=True,
        help="Output markdown path pack file",
    )
    parser.add_argument(
        "--prompt",
        type=Path,
        default=Path(__file__).resolve().parent / "prompts" / "path_pack.yaml",
        help="Path to prompt YAML template",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Override model in prompt YAML (e.g. gpt-5-mini)",
    )
    parser.add_argument(
        "--backend",
        choices=["auto", "wbal", "openai"],
        default="auto",
        help="LLM backend for generation (default: auto)",
    )
    parser.add_argument(
        "--max-events",
        type=int,
        default=250,
        help="Max number of trajectory events to include",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=1500,
        help="Max characters per captured tool output/text chunk",
    )
    parser.add_argument(
        "--since",
        type=str,
        default=None,
        help="Only include events at/after this ISO timestamp (e.g. 2026-01-07T20:04:00Z)",
    )
    parser.add_argument(
        "--until",
        type=str,
        default=None,
        help="Only include events at/before this ISO timestamp (e.g. 2026-01-07T20:10:00Z)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not call the LLM; write the rendered prompts to --out for inspection",
    )
    parser.add_argument(
        "--no-redact",
        action="store_true",
        help="Disable basic secret redaction (not recommended)",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="zather - generate Path Packs from agent sessions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command")

    list_parser = subparsers.add_parser("list", help="List sessions")
    list_parser.add_argument(
        "--source",
        choices=["claude", "codex"],
        required=True,
        help="Session source to list",
    )
    list_parser.add_argument(
        "--project",
        "-p",
        type=Path,
        default=Path.cwd(),
        help="Project path (for Claude Code listing)",
    )
    list_parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Max sessions to show",
    )

    build_parser = subparsers.add_parser("build", help="Build a Path Pack")
    build_parser.add_argument(
        "--source",
        choices=["claude", "codex"],
        required=True,
        help="Session source to parse",
    )
    build_parser.add_argument(
        "--project",
        "-p",
        type=Path,
        default=Path.cwd(),
        help="Project path (Claude Code only)",
    )
    build_parser.add_argument(
        "--session",
        "-s",
        type=str,
        default=None,
        help="Session ID (Claude Code or Codex CLI)",
    )
    build_parser.add_argument(
        "--session-file",
        type=Path,
        default=None,
        help="Explicit Codex CLI session JSONL file path",
    )
    _add_common_build_args(build_parser)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "list":
        if args.source == "claude":
            for session in list_claude_sessions(args.project, limit=args.limit):
                print(session)
        else:
            for session in list_codex_sessions(limit=args.limit):
                print(session)
        return

    if args.command == "build":
        build_path_pack(
            source=args.source,
            project_path=args.project,
            session_id=args.session,
            codex_session_file=args.session_file,
            out_path=args.out,
            prompt_path=args.prompt,
            model_override=args.model,
            backend=args.backend,
            max_events=args.max_events,
            max_chars=args.max_chars,
            since=args.since,
            until=args.until,
            dry_run=args.dry_run,
            redact=not args.no_redact,
        )
        print(f"Wrote: {args.out}", file=sys.stderr)
        return


if __name__ == "__main__":
    main()
