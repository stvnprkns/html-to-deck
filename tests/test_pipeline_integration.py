from __future__ import annotations

import json
from pathlib import Path

from html_to_deck.pipeline.orchestrator import HtmlToDeckPipeline
from html_to_deck.types import PipelineInput


def test_pipeline_generates_multiple_intent_driven_slides_from_fixtures(fixture_paths, tmp_path: Path) -> None:
    for fixture in fixture_paths:
        output = tmp_path / f"{fixture.stem}.json"
        HtmlToDeckPipeline.default().run(
            pipeline_input=PipelineInput(source=fixture, is_file=True),
            output_path=output,
        )

        payload = json.loads(output.read_text(encoding="utf-8"))

        assert len(payload["slides"]) >= 3
        intents = [slide["intent"] for slide in payload["slides"]]
        assert intents[0] == "title"
        assert "content" in intents
        assert all(slide["title"] != "Generated Slide" for slide in payload["slides"])


def test_pipeline_render_payload_includes_layout_and_audit_data(tmp_path: Path) -> None:
    html = """
    <html><head><title>Product Update</title></head><body>
      <h1>Product Update</h1>
      <p>We shipped a new onboarding flow.</p>
      <h2>Impact</h2>
      <p>Activation rose by 12 percent.</p>
    </body></html>
    """

    output = tmp_path / "deck.json"
    HtmlToDeckPipeline.default().run(
        pipeline_input=PipelineInput(source=html, is_file=False),
        output_path=output,
    )

    payload = json.loads(output.read_text(encoding="utf-8"))

    assert payload["layouts"]
    assert "audit" in payload
    assert {"issue_count", "issues"}.issubset(payload["audit"].keys())
    assert all("layout" in slide["metadata"] for slide in payload["slides"])
