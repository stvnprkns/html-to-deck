"""Infer deck type and storyline from extracted blocks."""

from __future__ import annotations

from dataclasses import dataclass

from ..extract.blocks import ContentBlock


@dataclass(frozen=True)
class Storyline:
    deck_type: str
    narrative_arc: str


def infer_storyline(blocks: list[ContentBlock]) -> Storyline:
    if not blocks:
        return Storyline(deck_type="empty", narrative_arc="none")
    return Storyline(deck_type="summary", narrative_arc="linear")
