"""Select layout patterns based on canonical slide intent."""

from __future__ import annotations

from ..schema.ir import DeckDocument


def choose_layout_patterns(deck: DeckDocument) -> dict[int, str]:
    return {i: slide.intent.value for i, slide in enumerate(deck.slides)}
