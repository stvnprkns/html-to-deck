"""Helpers for writing deterministic snapshot artifacts in tests."""

from __future__ import annotations

from pathlib import Path


def write_snapshot(path: str | Path, content: str) -> Path:
    """Write a text snapshot with normalized trailing newline.

    Returns the written path to make assertions easy in tests.
    """

    snapshot_path = Path(path)
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)

    normalized = content.rstrip("\n") + "\n"
    snapshot_path.write_text(normalized, encoding="utf-8")
    return snapshot_path


def write_json_snapshot(path: str | Path, rendered_json: str) -> Path:
    """Write renderer output into a JSON artifact for snapshot assertions."""

    return write_snapshot(path, rendered_json)
