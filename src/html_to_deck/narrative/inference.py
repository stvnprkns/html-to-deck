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
        return Storyline(deck_type="empty", narrative_arc="No source content available")

    corpus = " ".join(block.text.lower() for block in blocks)
    if "case study" in corpus or "challenge" in corpus or "outcome" in corpus:
        return Storyline(deck_type="case_study", narrative_arc="challenge → intervention → outcome")
    if "report" in corpus or "highlights" in corpus or "risks" in corpus:
        return Storyline(deck_type="report_summary", narrative_arc="performance → highlights → risks")
    if "problem" in corpus and "solution" in corpus:
        return Storyline(deck_type="landing_page_narrative", narrative_arc="problem → solution → proof")
    return Storyline(deck_type="article_story", narrative_arc="context → turning point → takeaway")
