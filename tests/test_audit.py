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


def test_audit_flags_image_backed_diagram_without_exception():
    designed = {
        "stage": "design",
        "fixture_id": "unit",
        "slides": [
            {
                "id": "slide-1",
                "title": "Architecture data flow",
                "body": "System interaction diagram",
                "body_metadata": {
                    "visual_intent": "diagram",
                    "block_type": "image",
                    "diagram_source": "bitmap",
                },
            }
        ],
    }

    audit = audit_deck(designed)

    assert any(issue["rule"] == "diagram_should_be_code" for issue in audit["issues"])


def test_audit_does_not_flag_code_spec_diagram():
    designed = {
        "stage": "design",
        "fixture_id": "unit",
        "slides": [
            {
                "id": "slide-1",
                "title": "Architecture data flow",
                "body": "Code-defined diagram",
                "body_metadata": {
                    "visual_intent": "diagram",
                    "block_type": "image",
                    "diagram_source": "code_spec",
                },
            }
        ],
    }

    audit = audit_deck(designed)

    assert all(issue["rule"] != "diagram_should_be_code" for issue in audit["issues"])
