from html_to_deck.pipeline.v1_compat import (
    apply_design,
    apply_layout,
    audit_deck,
    build_narrative,
    extract_content,
    ingest_html,
    map_to_slides,
    render_json,
)


def test_renderer_outputs_v1_deck_json(fixture_paths):
    for path in fixture_paths:
        designed = apply_design(apply_layout(map_to_slides(build_narrative(extract_content(ingest_html(path))))))
        deck = render_json(designed, audit_deck(designed))
        assert deck["deck_version"] == "v1"
        assert deck["fixture_id"] == path.stem
        assert "slides" in deck and "audit" in deck
