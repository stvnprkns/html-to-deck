"""Audit deck coherence and quality constraints."""

from __future__ import annotations

from ..schema.models import DeckDocument


def run_quality_checks(deck: DeckDocument) -> list[str]:
    issues: list[str] = []
    if not deck.slides:
        issues.append("Deck has no slides")
    return issues
