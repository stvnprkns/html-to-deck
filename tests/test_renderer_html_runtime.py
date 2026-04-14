from __future__ import annotations

from pathlib import Path

from html_to_deck.pipeline.orchestrator import HtmlToDeckPipeline
from html_to_deck.renderers import HtmlDeckRenderer, JsonDeckRenderer
from html_to_deck.schema.ir import DeckDocument, Slide, SlideIntent


def test_html_renderer_outputs_runtime_controls() -> None:
    deck = DeckDocument(
        deck_type="narrative",
        slides=[
            Slide(intent=SlideIntent.TITLE, title="Q2 Plan", bullets=["Goal", "Scope"]),
            Slide(intent=SlideIntent.CONTENT, title="Milestones", bullets=["Build", "Launch"]),
        ],
    )

    html = HtmlDeckRenderer().render(deck)

    assert "<article class=\"slide\" id=\"slide-1\">" in html
    assert "data-next" in html
    assert "data-progress" in html
    assert "ArrowRight" in html


def test_pipeline_from_output_path_selects_html_renderer() -> None:
    assert isinstance(HtmlToDeckPipeline.from_output_path(Path("deck.html")).renderer, HtmlDeckRenderer)
    assert isinstance(HtmlToDeckPipeline.from_output_path(Path("deck.json")).renderer, JsonDeckRenderer)
