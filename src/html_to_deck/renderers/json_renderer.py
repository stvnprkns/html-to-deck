"""First isolated target renderer: canonical schema to JSON string."""

from __future__ import annotations

import json
from typing import Any

from ..audit import AuditReport
from ..schema.ir import DeckDocument


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
                        "metadata": slide.metadata,
                    }
                    for slide in deck.slides
                ],
                "layouts": {str(idx): pattern for idx, pattern in deck.layouts.items()},
                "audit": {"issue_count": len(deck.audit_issues), "issues": deck.audit_issues},
            },
            indent=2,
        )
