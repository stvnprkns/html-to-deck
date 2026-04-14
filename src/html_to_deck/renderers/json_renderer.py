"""First isolated target renderer: canonical schema to JSON string."""

from __future__ import annotations

import json
from typing import Any

from ..schema.ir import DeckDocument, Slide


class JsonDeckRenderer:
    def render(self, deck: DeckDocument) -> str:
        return json.dumps(
            {
                "deck_type": deck.deck_type,
                "slides": [self._serialize_slide(slide) for slide in deck.slides],
            },
            indent=2,
        )

    @staticmethod
    def _serialize_slide(slide: Slide) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "intent": slide.intent.value,
            "title": slide.title,
            "bullets": list(slide.bullets),
        }

        if slide.body is not None:
            payload["body"] = slide.body
        if slide.notes is not None:
            payload["notes"] = slide.notes
        if slide.metadata:
            payload["metadata"] = dict(slide.metadata)
        if slide.evidence:
            payload["evidence"] = list(slide.evidence)
        if slide.source_refs:
            payload["source_refs"] = list(slide.source_refs)
        if slide.layout_hint is not None:
            payload["layout_hint"] = slide.layout_hint
        if slide.pattern is not None:
            payload["pattern"] = slide.pattern

        return payload
