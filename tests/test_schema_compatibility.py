from __future__ import annotations

import json

from html_to_deck.renderers import HtmlDeckRenderer, JsonDeckRenderer
from html_to_deck.schema.ir import DeckDocument, Slide, SlideIntent


def test_json_renderer_backward_compatible_with_minimal_slide() -> None:
    deck = DeckDocument(
        deck_type="narrative",
        slides=[Slide(intent=SlideIntent.CONTENT, title="Legacy Title", bullets=["Legacy bullet"])],
    )

    payload = json.loads(JsonDeckRenderer().render(deck))

    assert payload == {
        "deck_type": "narrative",
        "slides": [
            {
                "intent": "content",
                "title": "Legacy Title",
                "bullets": ["Legacy bullet"],
            }
        ],
    }


def test_renderers_serialize_extended_slide_fields_safely() -> None:
    slide = Slide(
        intent=SlideIntent.CONTENT,
        title="Roadmap",
        bullets=["A", "B"],
        body="Plain body",
        notes='Keep <confidential> "notes"',
        metadata={"block_type": "figure", "unsafe": "<script>alert(1)</script>"},
        evidence=["SRE report", "Perf trace"],
        source_refs=["https://example.com/a", "doc://internal"],
        layout_hint="two-column",
        pattern="split-hero",
    )
    deck = DeckDocument(deck_type="narrative", slides=[slide])

    payload = json.loads(JsonDeckRenderer().render(deck))
    assert payload["slides"][0]["body"] == "Plain body"
    assert payload["slides"][0]["notes"] == 'Keep <confidential> "notes"'
    assert payload["slides"][0]["metadata"]["unsafe"] == "<script>alert(1)</script>"
    assert payload["slides"][0]["layout_hint"] == "two-column"
    assert payload["slides"][0]["pattern"] == "split-hero"

    html = HtmlDeckRenderer().render(deck)
    assert "Notes:" in html
    assert "&lt;confidential&gt;" in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "layout=two-column" in html
    assert "pattern=split-hero" in html
