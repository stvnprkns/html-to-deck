from __future__ import annotations

import json
from pathlib import Path

from html_to_deck.pipeline.v1_compat import run_pipeline


SNAPSHOT_DIR = Path(__file__).parent / "snapshots"


def _load_snapshot(name: str) -> dict:
    return json.loads((SNAPSHOT_DIR / name).read_text(encoding="utf-8"))


def test_canonical_ir_snapshot(fixture_paths):
    actual = {path.stem: run_pipeline(path)["canonical_ir"] for path in fixture_paths}
    expected = _load_snapshot("canonical_ir.json")
    assert actual == expected


def test_final_deck_json_snapshot(fixture_paths):
    actual = {path.stem: run_pipeline(path)["deck_json"] for path in fixture_paths}
    expected = _load_snapshot("deck_json.json")
    assert actual == expected


def test_audit_report_snapshot(fixture_paths):
    actual = {path.stem: run_pipeline(path)["audit"] for path in fixture_paths}
    expected = _load_snapshot("audit_report.json")
    assert actual == expected
