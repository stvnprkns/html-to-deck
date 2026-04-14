"""HTML loaders and DOM snapshot normalization."""

from __future__ import annotations

from pathlib import Path


def load_html(source: str | Path, is_file: bool = True) -> str:
    if is_file:
        return Path(source).read_text(encoding="utf-8")
    return str(source)


def normalize_snapshot(html: str) -> str:
    """Placeholder normalizer for deterministic downstream processing."""
    return "\n".join(line.strip() for line in html.splitlines() if line.strip())
