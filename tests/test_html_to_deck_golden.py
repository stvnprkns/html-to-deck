from __future__ import annotations

import json
import os
from pathlib import Path

from html_to_deck.pipeline.orchestrator import HtmlToDeckPipeline
from html_to_deck.types import PipelineInput, SourceKind

SNAPSHOT_PATH = Path(__file__).parent / "snapshots" / "html_to_deck_output.json"


def test_html_to_deck_fixture_output_golden(tmp_path: Path, fixture_paths: list[Path]) -> None:
    actual: dict[str, dict] = {}
    pipeline = HtmlToDeckPipeline.default()

    for fixture in fixture_paths:
        output = tmp_path / f"{fixture.stem}.json"
        pipeline.run(PipelineInput(source=fixture, source_kind=SourceKind.FILE), output)
        actual[fixture.stem] = json.loads(output.read_text(encoding="utf-8"))

    payload = json.dumps(actual, indent=2, sort_keys=True)
    if os.getenv("UPDATE_SNAPSHOTS") == "1":
        SNAPSHOT_PATH.write_text(payload + "\n", encoding="utf-8")

    expected = SNAPSHOT_PATH.read_text(encoding="utf-8").strip()
    assert payload == expected
