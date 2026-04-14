from html_to_deck_v1.pipeline import build_narrative, extract_content, ingest_html, map_to_slides


def test_mapping_stage_creates_slide_sequence(fixture_paths):
    for path in fixture_paths:
        mapped = map_to_slides(build_narrative(extract_content(ingest_html(path))))
        assert mapped["stage"] == "mapping"
        assert mapped["slides"][0]["kind"] == "title"
        assert all(slide["id"].startswith("slide-") for slide in mapped["slides"])
