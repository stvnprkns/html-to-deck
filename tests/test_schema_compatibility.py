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

    assert payload["deck_type"] == "narrative"
    assert payload["layouts"] == {}
    assert payload["audit"]["issue_count"] == 0
    assert payload["audit"]["issues"] == []
    assert len(payload["slides"]) == 1
    slide = payload["slides"][0]
    assert slide["intent"] == "content"
    assert slide["title"] == "Legacy Title"
    assert slide["bullets"] == ["Legacy bullet"]
    assert slide["figures"] == []
    assert slide["metadata"] == {}


def test_renderers_escape_untrusted_strings_in_html() -> None:
    slide = Slide(
        intent=SlideIntent.CONTENT,
        title='Roadmap <script>alert(1)</script>',
        bullets=['<b>not bold in deck</b>', "normal"],
        metadata={"layout": "two-column"},
    )
    deck = DeckDocument(deck_type="narrative", slides=[slide])

    payload = json.loads(JsonDeckRenderer().render(deck))
    assert payload["slides"][0]["title"] == 'Roadmap <script>alert(1)</script>'
    assert "<b>" in payload["slides"][0]["bullets"][0]

    html = HtmlDeckRenderer().render(deck)
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "&lt;b&gt;not bold in deck&lt;/b&gt;" in html
    assert 'data-layout="two-column"' in html
