"""First isolated target renderer: canonical schema to JSON string."""

from __future__ import annotations

import json

from ..schema.ir import DeckDocument


class JsonDeckRenderer:
    def render(self, deck: DeckDocument) -> str:
        return json.dumps(
            {
                "deck_type": deck.deck_type,
                "source_href": deck.source_href,
                "slides": [
                    {
                        "intent": slide.intent.value,
                        "title": slide.title,
                        "layout": slide.layout,
                        "bullets": slide.bullets,
                        "metadata": slide.metadata,
                    }
                    for slide in deck.slides
                ],
                "audit": {
                    "issue_count": len(deck.audit_issues),
                    "issues": deck.audit_issues,
                },
            },
            indent=2,
        )
