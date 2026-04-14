from html_to_deck.pipeline.v1_compat import build_narrative, extract_content, ingest_html


def test_narrative_stage_builds_story_beats(fixture_paths):
    for path in fixture_paths:
        narrative = build_narrative(extract_content(ingest_html(path)))
        assert narrative["stage"] == "narrative"
        assert narrative["story"]["title"]
        assert all("id" in beat and "label" in beat for beat in narrative["story"]["beats"])
