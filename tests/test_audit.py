from html_to_deck_v1.pipeline import (
    apply_design,
    apply_layout,
    audit_deck,
    build_narrative,
    extract_content,
    ingest_html,
    map_to_slides,
)


def test_audit_stage_generates_report(fixture_paths):
    for path in fixture_paths:
        audit = audit_deck(
            apply_design(apply_layout(map_to_slides(build_narrative(extract_content(ingest_html(path))))))
        )
        assert audit["stage"] == "audit"
        assert "issue_count" in audit
        assert isinstance(audit["issues"], list)
