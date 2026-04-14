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

    corpus = " ".join(block.text.lower() for block in blocks)
    if any(token in corpus for token in ("case study", "challenge", "outcome")):
        return Storyline(deck_type="case_study", narrative_arc="problem-solution-results")
    if any(token in corpus for token in ("report", "q4", "arr", "retention", "risk")):
        return Storyline(deck_type="report_summary", narrative_arc="metrics-risks-actions")
    if any(token in corpus for token in ("problem", "solution", "proof", "launch", "meet")):
        return Storyline(deck_type="landing_page_narrative", narrative_arc="problem-solution-proof")
    if any(token in corpus for token in ("background", "turning point", "revival")):
        return Storyline(deck_type="article_story", narrative_arc="context-shift-outcome")
    return Storyline(deck_type="summary", narrative_arc="linear")
