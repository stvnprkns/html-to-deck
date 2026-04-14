"""Read/write helpers for pipeline snapshots and JSON outputs."""

from __future__ import annotations

from pathlib import Path


def write_output(payload: str, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(payload, encoding="utf-8")
    return output_path
