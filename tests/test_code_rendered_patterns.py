from html_to_deck_v1.pipeline import apply_layout, build_narrative, map_to_slides


def _extracted_with_structured(*, diagrams: list[str], tables: list[str], stats: list[str]) -> dict:
    return {
        "stage": "extract",
        "fixture_id": "structured-fixture",
        "meta": {
            "title": "Structured Source",
            "primary_heading": "Structured Source",
            "section_headings": ["Context"],
        },
        "content": {
            "paragraphs": ["Summary"],
            "bullets": [],
            "structured": {
                "diagrams": diagrams,
                "tables": tables,
                "stats": stats,
            },
        },
    }


def test_mapping_uses_code_rendered_patterns_for_structured_sources():
    narrative = build_narrative(
        _extracted_with_structured(diagrams=["flow"], tables=["table"], stats=["42"])
    )
    mapped = map_to_slides(narrative)
    patterns = {slide.get("pattern") for slide in mapped["slides"]}

    assert "MERMAID_DIAGRAM" in patterns
    assert "TABLE_FROM_DATA" in patterns
    assert "CHART_FROM_SERIES" in patterns
    assert "image_with_caption" not in patterns


def test_layout_uses_code_layouts_for_code_rendered_patterns():
    narrative = build_narrative(
        _extracted_with_structured(diagrams=["flow"], tables=["table"], stats=["42"])
    )
    mapped = map_to_slides(narrative)
    layouted = apply_layout(mapped)
    layouts_by_pattern = {slide.get("pattern"): slide["layout"] for slide in layouted["slides"] if slide.get("pattern")}

    assert layouts_by_pattern["MERMAID_DIAGRAM"] == "code-mermaid"
    assert layouts_by_pattern["TABLE_FROM_DATA"] == "code-table"
    assert layouts_by_pattern["CHART_FROM_SERIES"] == "code-chart"
