"""
Unified trajectory representation for Claude Code and Codex CLI sessions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal, Optional

import yaml


@dataclass(frozen=True)
class TrajectoryMeta:
    source: Literal["claude", "codex"]
    session_id: str
    cwd: Optional[str] = None
    started_at: Optional[str] = None
    notes: dict[str, Any] = field(default_factory=dict)

    def to_yaml(self) -> str:
        return yaml.safe_dump(
            {
                "source": self.source,
                "session_id": self.session_id,
                "cwd": self.cwd,
                "started_at": self.started_at,
                "notes": self.notes,
            },
            sort_keys=False,
        ).strip()


@dataclass(frozen=True)
class TrajectoryEvent:
    idx: int
    timestamp: Optional[str]
    actor: Literal["user", "assistant", "tool"]
    kind: str
    summary: str
    detail: str | None = None


@dataclass
class Trajectory:
    meta: TrajectoryMeta
    events: list[TrajectoryEvent]

    def to_markdown(self) -> str:
        lines: list[str] = []
        for event in self.events:
            header = f"- [{event.idx}] {event.actor}/{event.kind}: {event.summary}"
            lines.append(header)
            if event.detail:
                lines.append("")
                lines.append("  ```")
                lines.append(event.detail)
                lines.append("  ```")
        return "\n".join(lines).strip()


def iso_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

