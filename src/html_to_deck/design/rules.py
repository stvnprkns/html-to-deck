"""Apply hierarchy, spacing, emphasis, and contrast rules."""

from __future__ import annotations

from dataclasses import replace

from ..schema.ir import DeckDocument


def apply_design_rules(deck: DeckDocument, layouts: dict[int, str]) -> DeckDocument:
    """Attach layout pattern hints to slides without mutating source deck."""

    slides = [
        replace(
            slide,
            layout_hint=slide.layout_hint or layouts.get(index),
            pattern=slide.pattern or layouts.get(index),
        )
        for index, slide in enumerate(deck.slides)
    ]
    return replace(deck, slides=slides)
