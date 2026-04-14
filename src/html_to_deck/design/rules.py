"""Apply hierarchy, spacing, emphasis, and contrast rules."""

from __future__ import annotations

from ..pipeline.stages import design_stage
from ..schema.ir import DeckDocument


def apply_design_rules(deck: DeckDocument, layouts: dict[int, str]) -> DeckDocument:
    """Apply visual design while honoring layout selections."""
    deck_with_layouts = DeckDocument(
        slides=deck.slides,
        deck_type=deck.deck_type,
        source_href=deck.source_href,
        layouts=layouts,
        audit_issues=deck.audit_issues,
    )
    return design_stage(deck_with_layouts)
