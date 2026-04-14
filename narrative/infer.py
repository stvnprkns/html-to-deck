from __future__ import annotations

from collections import Counter

from extract.models import SourceBlock

from .models import DeckNarrative


DECK_TYPE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "executive_update": ("kpi", "status", "risk", "milestone", "progress", "quarter"),
    "sales_pitch": ("customer", "market", "value", "pricing", "roi", "solution"),
    "project_proposal": ("scope", "timeline", "budget", "deliverable", "team", "approach"),
    "research_summary": ("study", "method", "finding", "analysis", "data", "conclusion"),
}

SECTION_FLOW_BY_DECK_TYPE: dict[str, tuple[str, ...]] = {
    "executive_update": ("context", "performance", "risks", "next_steps"),
    "sales_pitch": ("problem", "solution", "proof", "offer", "close"),
    "project_proposal": ("problem", "approach", "plan", "investment", "decision"),
    "research_summary": ("question", "method", "findings", "implications", "actions"),
}


def infer_deck_narrative(blocks: list[SourceBlock]) -> DeckNarrative:
    text_blob = " ".join(block.text.lower() for block in blocks)
    scores = Counter()
    for deck_type, keywords in DECK_TYPE_KEYWORDS.items():
        scores[deck_type] = sum(text_blob.count(keyword) for keyword in keywords)

    if not scores:
        return DeckNarrative(deck_type="executive_update", confidence=0.0, sections=list(SECTION_FLOW_BY_DECK_TYPE["executive_update"]))

    deck_type, top_score = scores.most_common(1)[0]
    max_possible = max(1, len(DECK_TYPE_KEYWORDS[deck_type]))
    confidence = min(1.0, top_score / max_possible)

    sections = list(SECTION_FLOW_BY_DECK_TYPE.get(deck_type, SECTION_FLOW_BY_DECK_TYPE["executive_update"]))
    return DeckNarrative(deck_type=deck_type, confidence=confidence, sections=sections)
