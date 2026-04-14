"""First isolated target renderer: canonical schema to JSON string."""

from __future__ import annotations

import json

from ..schema.models import DeckDocument


class JsonDeckRenderer:
    def render(self, deck: DeckDocument) -> str:
        return json.dumps(
            {
                "deck_type": deck.deck_type,
                "slides": [
                    {
                        "intent": slide.intent.value,
                        "title": slide.title,
                        "bullets": slide.bullets,
                    }
                    for slide in deck.slides
                ],
            },
            indent=2,
        )
