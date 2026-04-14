from html_to_deck_v1.pipeline import apply_design, apply_layout, build_narrative, extract_content, ingest_html, map_to_slides


def test_design_stage_applies_theme(fixture_paths):
    for path in fixture_paths:
        designed = apply_design(apply_layout(map_to_slides(build_narrative(extract_content(ingest_html(path))))))
        assert designed["stage"] == "design"
        assert {slide["theme"] for slide in designed["slides"]} == {"v1-light"}
