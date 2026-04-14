"""First isolated target renderer: canonical schema to JSON string."""

from __future__ import annotations

import json

from ..audit import AuditReport
from ..schema.ir import DeckDocument


class JsonDeckRenderer:
    def render(self, deck: DeckDocument, audit_report: AuditReport | None = None) -> str:
        payload: dict[str, object] = {
            "deck_type": deck.deck_type,
            "slides": [
                {
                    "intent": slide.intent.value,
                    "title": slide.title,
                    "bullets": slide.bullets,
                }
                for slide in deck.slides
            ],
        }
        if audit_report is not None:
            payload["audit"] = audit_report.to_dict()
        return json.dumps(payload, indent=2)
