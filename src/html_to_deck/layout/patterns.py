"""Select layout patterns based on canonical slide intent."""

from __future__ import annotations

from ..schema.ir import DeckDocument, SlideIntent


def choose_layout_patterns(deck: DeckDocument) -> dict[int, str]:
    layouts: dict[int, str] = {}
    for i, slide in enumerate(deck.slides):
        if slide.intent == SlideIntent.TITLE:
            layouts[i] = "hero"
        elif slide.intent == SlideIntent.SUMMARY:
            layouts[i] = "closing"
        elif len(slide.bullets) >= 4:
            layouts[i] = "cards_grid"
        else:
            layouts[i] = "two_column_comparison"
    return layouts
