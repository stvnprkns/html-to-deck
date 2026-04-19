from __future__ import annotations

from pathlib import Path

from html_to_deck.audit import AuditReport
from html_to_deck.pipeline.orchestrator import HtmlToDeckPipeline
from html_to_deck.renderers import HtmlDeckRenderer
from html_to_deck.schema.ir import DeckDocument, Slide, SlideImage, SlideIntent
from html_to_deck.types import PipelineInput, SourceKind


def test_portfolio_theme_includes_warm_background_and_fonts() -> None:
    deck = DeckDocument(
        deck_type="article_story",
        slides=[Slide(intent=SlideIntent.TITLE, title="Hello", bullets=["One"])],
    )
    html = HtmlDeckRenderer(theme="portfolio").render(deck, AuditReport(warnings=[]))
    assert "data-theme=\"portfolio\"" in html
    assert "#faf9f7" in html or "--page-bg: #faf9f7" in html
    assert "Instrument+Serif" in html or "fonts.googleapis.com" in html


def test_default_theme_preserves_midnight_palette() -> None:
    deck = DeckDocument(
        deck_type="article_story",
        slides=[Slide(intent=SlideIntent.TITLE, title="Hello", bullets=["One"])],
    )
    html = HtmlDeckRenderer(theme="default").render(deck, AuditReport(warnings=[]))
    assert "data-theme=\"default\"" in html
    assert "#0b1020" in html


def test_extra_css_is_injected_into_style_block() -> None:
    deck = DeckDocument(
        deck_type="article_story",
        slides=[Slide(intent=SlideIntent.TITLE, title="T", bullets=["x"])],
    )
    html = HtmlDeckRenderer(theme="default", extra_css=".deck { outline: 2px solid lime; }").render(deck, AuditReport(warnings=[]))
    assert "outline: 2px solid lime" in html


def test_pipeline_html_output_contains_figure_for_img_fixture(tmp_path: Path) -> None:
    source = tmp_path / "with-img.html"
    source.write_text(
        """<!doctype html><html><body>
<h1>Demo</h1>
<h2>Screen</h2>
<p>Caption text.</p>
<p><img src="shot.png" width="800" height="450" alt="UI screenshot"></p>
</body></html>""",
        encoding="utf-8",
    )
    out = tmp_path / "deck.html"
    HtmlToDeckPipeline.from_output_path(out).run(
        PipelineInput(source=source, source_kind=SourceKind.FILE),
        out,
    )
    html = out.read_text(encoding="utf-8")
    assert 'class="slide-figure"' in html
    assert 'src="shot.png"' in html
    assert 'width="800"' in html
    assert 'height="450"' in html


def test_cli_theme_portfolio_flag(tmp_path: Path) -> None:
    import os
    import subprocess
    import sys

    src = tmp_path / "in.html"
    src.write_text("<html><body><h1>T</h1><p>x</p></body></html>", encoding="utf-8")
    out = tmp_path / "out.html"
    root = Path(__file__).resolve().parents[1]
    env = {**os.environ, "PYTHONPATH": str(root / "src")}
    subprocess.run(
        [
            sys.executable,
            "-m",
            "html_to_deck.cli",
            "--input",
            str(src),
            "--output",
            str(out),
            "--format",
            "html",
            "--theme",
            "portfolio",
            "--audit-output",
            "none",
        ],
        cwd=root,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "portfolio" in out.read_text(encoding="utf-8")
