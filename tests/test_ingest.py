from html_to_deck.pipeline.v1_compat import ingest_html


def test_ingest_stage_reads_fixture(fixture_paths):
    for path in fixture_paths:
        out = ingest_html(path)
        assert out["stage"] == "ingest"
        assert out["document"].fixture_id == path.stem
        assert "<html" in out["document"].html.lower()
