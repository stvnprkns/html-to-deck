from __future__ import annotations

from pathlib import Path

import pytest

from html_to_deck.ingest.loader import load_html, normalize_snapshot
from html_to_deck.types import SourceKind


def test_load_html_from_file(tmp_path: Path) -> None:
    source = tmp_path / "fixture.html"
    source.write_text("<html><body><p>From file</p></body></html>", encoding="utf-8")

    assert "From file" in load_html(source, source_kind=SourceKind.FILE)


def test_load_html_from_string() -> None:
    html = "<html><body><p>From string</p></body></html>"

    assert load_html(html, source_kind=SourceKind.HTML_STRING) == html


def test_load_html_from_url_disabled_by_default() -> None:
    with pytest.raises(ValueError, match="disabled"):
        load_html("https://example.com/source.html", source_kind=SourceKind.URL)


def test_load_html_from_url_with_retry(monkeypatch) -> None:
    monkeypatch.setenv("HTML_TO_DECK_ENABLE_URL_INGEST", "true")
    monkeypatch.setenv("HTML_TO_DECK_URL_MAX_RETRIES", "2")
    calls = {"count": 0}

    class _Response:
        headers = {"Content-Type": "text/html; charset=utf-8"}

        def read(self) -> bytes:
            return b"<html><body><p>Fetched</p></body></html>"

        def __enter__(self) -> "_Response":
            return self

        def __exit__(self, *_args: object) -> None:
            return None

    def _fake_urlopen(*_args: object, **_kwargs: object) -> _Response:
        calls["count"] += 1
        if calls["count"] < 2:
            raise TimeoutError("timeout")
        return _Response()

    monkeypatch.setattr("html_to_deck.ingest.loader.urlopen", _fake_urlopen)

    html = load_html("https://example.com/source.html", source_kind=SourceKind.URL)
    assert "Fetched" in html
    assert calls["count"] == 2


def test_normalize_snapshot_is_deterministic_and_excludes_script_style() -> None:
    dirty = """
        <HTML>\n<body>\n<h1>  Hello   world </h1>\n<script>var x = 1;</script>\n<style>.a{color:red;}</style>\n<p>Line\n break</p>\n</body>\n</HTML>
    """

    normalized = normalize_snapshot(dirty)

    assert normalized == "<html><body><h1>Hello world</h1><p>Line break</p></body></html>"
