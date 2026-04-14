from html_to_deck_v1.pipeline import extract_content, ingest_html


def test_extract_stage_emits_meta_and_content(fixture_paths):
    for path in fixture_paths:
        extracted = extract_content(ingest_html(path))
        assert extracted["stage"] == "extract"
        assert extracted["meta"]["title"]
        assert extracted["meta"]["primary_heading"]
        assert isinstance(extracted["content"]["paragraphs"], list)
