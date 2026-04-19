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
    assert "#faf9f7" in html or "--deck-bg:" in html
    assert "Instrument+Serif" in html or "fonts.googleapis.com" in html


def test_default_theme_preserves_midnight_palette() -> None:
    deck = DeckDocument(
        deck_type="article_story",
        slides=[Slide(intent=SlideIntent.TITLE, title="Hello", bullets=["One"])],
    )
    html = HtmlDeckRenderer(theme="default").render(deck, AuditReport(warnings=[]))
    assert "data-theme=\"default\"" in html
    assert "#0b1020" in html
    assert "--deck-bg:" in html


def test_extra_css_is_injected_into_style_block() -> None:
    deck = DeckDocument(
        deck_type="article_story",
        slides=[Slide(intent=SlideIntent.TITLE, title="T", bullets=["x"])],
    )
    html = HtmlDeckRenderer(theme="default", extra_css=".deck { outline: 2px solid lime; }").render(deck, AuditReport(warnings=[]))
    assert "outline: 2px solid lime" in html


def test_tokens_css_precedes_theme_in_style_block() -> None:
    deck = DeckDocument(
        deck_type="article_story",
        slides=[Slide(intent=SlideIntent.TITLE, title="T", bullets=["x"])],
    )
    html = HtmlDeckRenderer(
        theme="default",
        tokens_css="/*TOKENS_FIRST*/",
        extra_css="/*EXTRA_LAST*/",
    ).render(deck, AuditReport(warnings=[]))
    pos_tok = html.index("/*TOKENS_FIRST*/")
    pos_deck = html.index("--deck-bg:")
    pos_extra = html.index("/*EXTRA_LAST*/")
    assert pos_tok < pos_deck < pos_extra


def test_embed_layout_adds_class_and_data_layout() -> None:
    deck = DeckDocument(
        deck_type="article_story",
        slides=[Slide(intent=SlideIntent.TITLE, title="Hello", bullets=["One"])],
    )
    html = HtmlDeckRenderer(theme="default", layout="embed").render(deck, AuditReport(warnings=[]))
    assert "deck--embed" in html
    assert 'data-layout="embed"' in html


def test_hide_audit_and_source_flags() -> None:
    deck = DeckDocument(
        deck_type="article_story",
        source_href="https://example.com/page.html",
        slides=[Slide(intent=SlideIntent.TITLE, title="T", bullets=["x"])],
    )
    html = HtmlDeckRenderer(show_audit_badge=False, show_source_link=False).render(deck, AuditReport(warnings=[]))
    assert "data-audit-summary" not in html
    assert "data-source-link" not in html


def test_meta_description_from_slides() -> None:
    deck = DeckDocument(
        deck_type="article_story",
        slides=[
            Slide(intent=SlideIntent.TITLE, title="Alpha", bullets=["First bullet"]),
            Slide(intent=SlideIntent.CONTENT, title="Beta", bullets=[]),
        ],
    )
    html = HtmlDeckRenderer().render(deck, AuditReport(warnings=[]))
    assert 'name="description"' in html
    assert "Alpha" in html and "First bullet" in html


def test_api_convert_writes_html(tmp_path: Path) -> None:
    from html_to_deck import convert

    src = tmp_path / "in.html"
    src.write_text("<html><body><h1>H</h1><p>x</p></body></html>", encoding="utf-8")
    out = tmp_path / "deck.html"
    convert(src, out, theme="portfolio", layout="embed", show_audit_badge=False, show_source_link=False)
    text = out.read_text(encoding="utf-8")
    assert "deck--embed" in text
    assert "data-audit-summary" not in text


def test_api_render_html_string() -> None:
    from html_to_deck import render_html_string

    deck = DeckDocument(
        deck_type="article_story",
        slides=[Slide(intent=SlideIntent.TITLE, title="T", bullets=["b"])],
    )
    html = render_html_string(deck)
    assert "slide-1" in html and "T" in html


def test_cli_version_flag() -> None:
    import os
    import subprocess
    import sys

    root = Path(__file__).resolve().parents[1]
    env = {**os.environ, "PYTHONPATH": str(root / "src")}
    proc = subprocess.run(
        [sys.executable, "-m", "html_to_deck.cli", "--version"],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert proc.stdout.strip().endswith("1.0.0") or "1.0.0" in proc.stdout


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
