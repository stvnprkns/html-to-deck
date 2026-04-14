from html_to_deck.pipeline.v1_compat import apply_layout, build_narrative, extract_content, ingest_html, map_to_slides


def test_layout_stage_applies_layout_contract(fixture_paths):
    for path in fixture_paths:
        layouted = apply_layout(map_to_slides(build_narrative(extract_content(ingest_html(path)))))
        assert layouted["stage"] == "layout"
        assert layouted["slides"][0]["layout"] == "hero"
        assert all("layout" in slide for slide in layouted["slides"])
