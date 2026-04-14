"""Extract headings, paragraphs, lists, stats, quotes, images, and tables."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ContentBlock:
    kind: str
    text: str


def extract_blocks(snapshot: str) -> list[ContentBlock]:
    """Minimal extractor placeholder."""
    if not snapshot:
        return []
    return [ContentBlock(kind="paragraph", text=snapshot)]
