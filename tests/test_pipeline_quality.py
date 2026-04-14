from __future__ import annotations

import json
from pathlib import Path

from extract.block_extractors import extract_blocks
from extract.models import SourceBlock
from html_to_deck.audit.checks import MAX_BULLETS_PER_SLIDE, MAX_WORDS_PER_SLIDE, run_quality_checks
from html_to_deck.pipeline.orchestrator import HtmlToDeckPipeline
from html_to_deck.schema.ir import DeckDocument, Slide, SlideIntent
from html_to_deck.types import PipelineInput
from layout.pattern_selector import choose_layout_pattern
from narrative.infer import infer_deck_narrative
from narrative.models import SlideIntent as NarrativeSlideIntent
from pipeline.map_to_slides import map_to_slide_intents


def test_extraction_richness_captures_structured_blocks() -> None:
    source = """# Quarterly review
- ARR grew 18%
| Region | ARR |
| --- | --- |
| NA | 5.1M |
```mermaid
flowchart TD
A-->B
```
"""

    blocks = extract_blocks(source)
    block_types = {block.block_type for block in blocks}

    assert {"heading", "list", "table", "diagram_spec"}.issubset(block_types)


def test_narrative_classification_prefers_sales_pitch_for_sales_language() -> None:
    blocks = [
        SourceBlock(block_type="paragraph", text="Customer value and market pricing improved ROI", confidence=0.9),
    ]

    narrative = infer_deck_narrative(blocks)

    assert narrative.deck_type == "sales_pitch"
    assert narrative.confidence > 0


def test_mapping_split_logic_splits_overloaded_sections() -> None:
    blocks = [
        SourceBlock(block_type="paragraph", text="word " * 25, confidence=0.9),
        SourceBlock(block_type="paragraph", text="word " * 25, confidence=0.9),
        SourceBlock(block_type="paragraph", text="word " * 25, confidence=0.9),
    ]
    narrative = infer_deck_narrative(blocks)

    intents = map_to_slide_intents(blocks, narrative)

    assert len(intents) >= 2
    assert all(intent.overload_score <= 1.0 for intent in intents)


def test_layout_selection_uses_overload_fallback() -> None:
    intent = NarrativeSlideIntent(
        communication_job="report_performance",
        section="performance",
        supporting_block_ids=[0, 1],
        overload_score=1.4,
    )

    choice = choose_layout_pattern(intent)

    assert choice.pattern == "title_and_bullets"


def test_regression_empty_deck_single_slide_and_missing_metadata() -> None:
    empty_deck = DeckDocument(deck_type="summary", slides=[], source_href=None)
    assert "Deck has no slides" in run_quality_checks(empty_deck)

    collapsed_deck = DeckDocument(
        deck_type="summary",
        slides=[Slide(intent=SlideIntent.CONTENT, title="Only", bullets=["One"])],
        source_href="https://example.com",
    )
    collapsed_issues = run_quality_checks(collapsed_deck)
    assert "Deck collapsed to a single slide" in collapsed_issues

    missing_meta_deck = DeckDocument(
        deck_type="summary",
        slides=[
            Slide(
                intent=SlideIntent.CONTENT,
                title="Metadata",
                bullets=["Missing source metadata should be caught"],
            )
        ],
        source_href=None,
    )
    assert "Deck metadata missing source_href" in run_quality_checks(missing_meta_deck)


def test_quality_metrics_for_fixture_outputs(tmp_path: Path, fixture_paths: list[Path]) -> None:
    pipeline = HtmlToDeckPipeline.default()

    for fixture in fixture_paths:
        output = tmp_path / f"{fixture.stem}.json"
        pipeline.run(PipelineInput(source=fixture, is_file=True), output)
        payload = json.loads(output.read_text(encoding="utf-8"))

        assert len(payload["slides"]) >= 1

        deck = DeckDocument(
            deck_type=payload["deck_type"],
            source_href="file://fixture",
            slides=[
                Slide(
                    intent=SlideIntent(slide["intent"]),
                    title=slide["title"],
                    bullets=slide["bullets"],
                )
                for slide in payload["slides"]
            ],
        )

        issues = run_quality_checks(deck)
        assert "Deck has no slides" not in issues
        assert "Deck metadata missing source_href" not in issues
        for index, slide in enumerate(deck.slides, start=1):
            if len(slide.bullets) > MAX_BULLETS_PER_SLIDE:
                assert f"slide-{index} exceeds bullet budget" in issues
            if sum(len(bullet.split()) for bullet in slide.bullets) > MAX_WORDS_PER_SLIDE:
                assert f"slide-{index} exceeds word budget" in issues
