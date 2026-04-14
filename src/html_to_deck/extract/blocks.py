"""Extraction stage public API."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ContentBlock:
    kind: str
    text: str


def extract_blocks(snapshot: str) -> list[ContentBlock]:
    """Extract semantic blocks from HTML or markdown-like snapshots."""

    if not snapshot:
        return []

    from .parsers import extract_semantic_blocks

    return extract_semantic_blocks(snapshot)
