from __future__ import annotations

import json
from pathlib import Path

from html_to_deck.audit.checks import MAX_BULLETS_PER_SLIDE, MAX_WORDS_PER_SLIDE, run_quality_checks
from html_to_deck.extract.blocks import extract_blocks
from html_to_deck.layout.patterns import choose_layout_patterns
from html_to_deck.narrative.inference import infer_storyline
from html_to_deck.pipeline.orchestrator import _chunk_bullets_for_clarity
from html_to_deck.schema.ir import DeckDocument, Slide, SlideIntent


def test_extraction_richness_captures_multiple_block_kinds() -> None:
    html = """
    <html><head><title>Case Study: Growth</title></head><body>
    <h1>Reducing Churn</h1>
    <h2>Challenge</h2>
    <p>Activation dropped after onboarding changes.</p>
    <ul><li>Trial conversion dipped.</li><li>Support volume increased.</li></ul>
    </body></html>
    """
    blocks = extract_blocks(html)

    kinds = {block.kind for block in blocks}
    assert {"title", "heading", "section_heading", "paragraph", "bullet"}.issubset(kinds)


def test_narrative_classification_uses_content_signals() -> None:
    blocks = extract_blocks(
        "<html><body><h1>Case Study</h1><h2>Challenge</h2><h2>Outcome</h2><p>Results improved.</p></body></html>"
    )
    storyline = infer_storyline(blocks)
    assert storyline.deck_type == "case_study"
    assert storyline.narrative_arc == "problem-solution-results"


def test_mapping_split_logic_respects_bullet_and_word_budgets() -> None:
    bullets = ["one two three four five six seven"] * 20
    chunks = _chunk_bullets_for_clarity(bullets)

    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= MAX_BULLETS_PER_SLIDE
        assert sum(len(item.split()) for item in chunk) <= MAX_WORDS_PER_SLIDE


def test_layout_selection_prefers_hero_then_content_then_closing() -> None:
    deck = DeckDocument(
        deck_type="report_summary",
        slides=[
            Slide(intent=SlideIntent.TITLE, title="Q4 Report", bullets=["Revenue up"]),
            Slide(intent=SlideIntent.CONTENT, title="Details", bullets=["a", "b", "c", "d"]),
            Slide(intent=SlideIntent.SUMMARY, title="Summary", bullets=["Next step"]),
        ],
    )

    layouts = choose_layout_patterns(deck)
    assert layouts == {0: "hero", 1: "cards_grid", 2: "closing"}


def test_regression_empty_deck_and_missing_metadata_are_audited() -> None:
    empty_deck = DeckDocument(deck_type="summary", slides=[], source_href=None)
    issues = run_quality_checks(empty_deck)
    assert "Deck has no slides" in issues

    non_empty_missing_meta = DeckDocument(
        deck_type="summary",
        slides=[Slide(intent=SlideIntent.CONTENT, title="Only", bullets=["one"])],
        source_href=None,
    )
    missing_meta_issues = run_quality_checks(non_empty_missing_meta)
    assert "Deck metadata missing source_href" in missing_meta_issues


def test_regression_single_slide_collapse_is_flagged() -> None:
    deck = DeckDocument(
        deck_type="summary",
        slides=[Slide(intent=SlideIntent.CONTENT, title="Only", bullets=["single slide output"])],
        source_href="https://example.com",
    )

    issues = run_quality_checks(deck)
    assert "Deck collapsed to a single slide" in issues


def test_quality_metrics_are_within_limits_for_fixture_outputs(tmp_path: Path, fixture_paths: list[Path]) -> None:
    from html_to_deck.pipeline.orchestrator import HtmlToDeckPipeline
    from html_to_deck.types import PipelineInput

    pipeline = HtmlToDeckPipeline.default()
    for fixture in fixture_paths:
        output = tmp_path / f"{fixture.stem}.json"
        pipeline.run(PipelineInput(source=fixture, is_file=True), output)
        payload = json.loads(output.read_text(encoding="utf-8"))

        assert len(payload["slides"]) >= 2
        for slide in payload["slides"]:
            assert len(slide["bullets"]) <= MAX_BULLETS_PER_SLIDE
            assert sum(len(bullet.split()) for bullet in slide["bullets"]) <= MAX_WORDS_PER_SLIDE
        assert payload["audit"]["issue_count"] == 0
