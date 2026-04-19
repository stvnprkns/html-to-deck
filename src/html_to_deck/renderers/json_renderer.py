"""First isolated target renderer: canonical schema to JSON string."""

from __future__ import annotations

import json
from typing import Any

from ..audit import AuditReport
from ..schema.ir import DeckDocument, SlideImage


class JsonDeckRenderer:
    def render(self, deck: DeckDocument, audit_report: AuditReport | None = None) -> str:
        audit_payload: dict[str, Any]
        if audit_report is not None:
            audit_payload = audit_report.to_dict()
        else:
            audit_payload = {"issue_count": len(deck.audit_issues), "issues": deck.audit_issues}

        return json.dumps(
            {
                "deck_type": deck.deck_type,
                "slides": [
                    {
                        "intent": slide.intent.value,
                        "title": slide.title,
                        "bullets": slide.bullets,
                        "figures": [_figure_dict(f) for f in slide.figures],
                        "metadata": slide.metadata,
                    }
                    for slide in deck.slides
                ],
                "layouts": {str(idx): pattern for idx, pattern in deck.layouts.items()},
                "audit": audit_payload,
            },
            indent=2,
        )


def _figure_dict(fig: SlideImage) -> dict[str, Any]:
    return {
        "src": fig.src,
        "alt": fig.alt,
        "width": fig.width,
        "height": fig.height,
    }
