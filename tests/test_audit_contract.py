from __future__ import annotations

import json
from pathlib import Path

from html_to_deck.audit import run_quality_checks
from html_to_deck.renderers import JsonDeckRenderer
from html_to_deck.schema.ir import DeckDocument, Slide, SlideIntent

SNAPSHOT_PATH = Path(__file__).parent / "snapshots" / "canonical_audit_report.json"


def _build_audit_fixture_deck() -> DeckDocument:
    return DeckDocument(
        deck_type="report",
        slides=[
            Slide(
                intent=SlideIntent.CONTENT,
                title="Q2 metrics",
                bullets=["word " * 120],
                metadata={"communication_job": "inform+decide"},
            ),
            Slide(
                intent=SlideIntent.CONTENT,
                title="Architecture flow",
                bullets=["Diagram currently exported as image"],
                metadata={
                    "visual_intent": "diagram",
                    "block_type": "image",
                    "diagram_source": "bitmap",
                    "claims": [{"text": "Latency dropped", "has_evidence": False, "provenance": None}],
                },
            ),
        ],
    )


def test_audit_report_snapshot_shape() -> None:
    report = run_quality_checks(_build_audit_fixture_deck())
    actual = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    expected = SNAPSHOT_PATH.read_text(encoding="utf-8").strip()
    assert actual == expected


def test_audit_severity_controls_blocker_flag() -> None:
    critical_report = run_quality_checks(
        DeckDocument(
            deck_type="report",
            slides=[
                Slide(
                    intent=SlideIntent.CONTENT,
                    title="Claim without proof",
                    bullets=["Need citation"],
                    metadata={"claims": [{"text": "x", "has_evidence": False, "provenance": None}]},
                )
            ],
        )
    )
    assert critical_report.has_blockers is True

    low_only_report = run_quality_checks(
        DeckDocument(deck_type="report", slides=[Slide(intent=SlideIntent.CONTENT, title="Clean", bullets=["ok"])])
    )
    assert low_only_report.has_blockers is False


def test_json_renderer_emits_audit_payload() -> None:
    deck = DeckDocument(deck_type="report", slides=[Slide(intent=SlideIntent.CONTENT, title="Title", bullets=["A"])])
    payload = json.loads(JsonDeckRenderer().render(deck, run_quality_checks(deck)))

    assert "audit" in payload
    assert set(payload["audit"]) == {"has_blockers", "counts_by_severity", "warning_count", "warnings"}
