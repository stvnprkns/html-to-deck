from pathlib import Path


def test_v1_pipeline_is_shim_only():
    """Guard against introducing independent stage logic in two trees."""
    shim_path = Path("src/html_to_deck_v1/pipeline.py")
    text = shim_path.read_text(encoding="utf-8")

    assert "from html_to_deck.pipeline.v1_compat import (" in text
    assert "def " not in text, "v1 pipeline must remain a thin import shim"
    assert "class " not in text, "v1 pipeline must remain a thin import shim"
