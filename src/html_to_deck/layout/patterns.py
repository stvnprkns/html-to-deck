"""Select layout patterns based on canonical slide intent."""

from __future__ import annotations

from ..schema.ir import DeckDocument, SlideIntent


def choose_layout_patterns(deck: DeckDocument) -> dict[int, str]:
    intent_to_layout = {
        SlideIntent.TITLE: "hero",
        SlideIntent.CONTENT: "content_split",
        SlideIntent.SUMMARY: "closing",
    }
    return {i: intent_to_layout.get(slide.intent, "content_split") for i, slide in enumerate(deck.slides)}
