from __future__ import annotations

from pathlib import Path

from html_to_deck.audit import AuditReport
from html_to_deck.pipeline.orchestrator import HtmlToDeckPipeline
from html_to_deck.renderers import HtmlDeckRenderer, JsonDeckRenderer
from html_to_deck.schema.ir import DeckDocument, Slide, SlideIntent
from html_to_deck.types import PipelineInput, SourceKind


def test_html_renderer_outputs_runtime_controls() -> None:
    deck = DeckDocument(
        deck_type="narrative",
        source_href="https://example.com/source.html",
        slides=[
            Slide(intent=SlideIntent.TITLE, title="Q2 Plan", bullets=["Goal", "Scope"]),
            Slide(intent=SlideIntent.CONTENT, title="Milestones", bullets=["Build", "Launch"]),
        ],
    )

    html = HtmlDeckRenderer().render(deck, AuditReport(warnings=[]))

    assert 'id="slide-1"' in html and 'class="slide"' in html
    assert "data-next" in html
    assert "data-progress" in html
    assert "ArrowRight" in html
    assert "data-source-link" in html
    assert "🔗" in html
    assert "data-audit-summary" in html


def test_pipeline_from_output_path_selects_html_renderer() -> None:
    assert isinstance(HtmlToDeckPipeline.from_output_path(Path("deck.html")).renderer, HtmlDeckRenderer)
    assert isinstance(HtmlToDeckPipeline.from_output_path(Path("deck.json")).renderer, JsonDeckRenderer)


def test_pipeline_sets_source_href_for_file_input(tmp_path: Path) -> None:
    source = tmp_path / "input.html"
    source.write_text("<html><body><h1>Title</h1><p>One</p></body></html>", encoding="utf-8")
    output = tmp_path / "deck.html"

    HtmlToDeckPipeline.from_output_path(output).run(
        pipeline_input=PipelineInput(source=source, source_kind=SourceKind.FILE),
        output_path=output,
    )

    html = output.read_text(encoding="utf-8")
    assert "data-source-link" in html
    assert source.resolve().as_uri() in html


def test_pipeline_sets_sanitized_source_href_for_url_input(monkeypatch, tmp_path: Path) -> None:
    output = tmp_path / "deck.html"
    monkeypatch.setenv("HTML_TO_DECK_ENABLE_URL_INGEST", "1")

    class _Response:
        headers = {"Content-Type": "text/html; charset=utf-8"}

        def read(self) -> bytes:
            return b"<html><body>URL source</body></html>"

        def __enter__(self) -> "_Response":
            return self

        def __exit__(self, *_args: object) -> None:
            return None

    def _fake_urlopen(*_args: object, **_kwargs: object) -> _Response:
        return _Response()

    monkeypatch.setattr("html_to_deck.ingest.loader.urlopen", _fake_urlopen)

    HtmlToDeckPipeline.from_output_path(output).run(
        pipeline_input=PipelineInput(
            source="https://user:secret@example.com/report.html?x=1#top",
            source_kind=SourceKind.URL,
        ),
        output_path=output,
    )

    html = output.read_text(encoding="utf-8")
    assert "https://example.com/report.html?x=1" in html
    assert "secret" not in html
    assert "#top" not in html
