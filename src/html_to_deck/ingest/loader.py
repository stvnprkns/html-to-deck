"""HTML loaders and deterministic snapshot normalization."""

from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from ..types import SourceKind

_WHITESPACE_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class UrlFetchConfig:
    """URL ingestion controls with environment-safe defaults."""

    enabled: bool = False
    timeout_seconds: float = 5.0
    max_retries: int = 1
    retry_backoff_seconds: float = 0.2

    @classmethod
    def from_environment(cls) -> "UrlFetchConfig":
        enabled_raw = os.getenv("HTML_TO_DECK_ENABLE_URL_INGEST", "0").strip().lower()
        enabled = enabled_raw in {"1", "true", "yes", "on"}

        timeout_raw = os.getenv("HTML_TO_DECK_URL_TIMEOUT_SECONDS", "5.0").strip()
        retries_raw = os.getenv("HTML_TO_DECK_URL_MAX_RETRIES", "1").strip()
        backoff_raw = os.getenv("HTML_TO_DECK_URL_RETRY_BACKOFF_SECONDS", "0.2").strip()

        timeout = min(max(float(timeout_raw), 0.5), 30.0)
        retries = min(max(int(retries_raw), 0), 5)
        backoff = min(max(float(backoff_raw), 0.0), 5.0)

        return cls(enabled=enabled, timeout_seconds=timeout, max_retries=retries, retry_backoff_seconds=backoff)


class _NormalizingHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._ignored_tag_stack: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        normalized_tag = tag.lower()
        if normalized_tag in {"script", "style"}:
            self._ignored_tag_stack.append(normalized_tag)
            return
        if self._ignored_tag_stack:
            return

        normalized_attrs = "".join(
            f' {name.lower()}="{self._normalize_text(value or "")}"'
            for name, value in sorted(attrs, key=lambda item: item[0].lower())
        )
        self._parts.append(f"<{normalized_tag}{normalized_attrs}>")

    def handle_endtag(self, tag: str) -> None:
        normalized_tag = tag.lower()
        if self._ignored_tag_stack:
            if self._ignored_tag_stack[-1] == normalized_tag:
                self._ignored_tag_stack.pop()
            return
        self._parts.append(f"</{normalized_tag}>")

    def handle_data(self, data: str) -> None:
        if self._ignored_tag_stack:
            return
        normalized = self._normalize_text(data)
        if normalized:
            self._parts.append(normalized)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        normalized_tag = tag.lower()
        if normalized_tag in {"script", "style"} or self._ignored_tag_stack:
            return
        normalized_attrs = "".join(
            f' {name.lower()}="{self._normalize_text(value or "")}"'
            for name, value in sorted(attrs, key=lambda item: item[0].lower())
        )
        self._parts.append(f"<{normalized_tag}{normalized_attrs} />")

    @staticmethod
    def _normalize_text(value: str) -> str:
        return _WHITESPACE_RE.sub(" ", value).strip()

    def normalized_html(self) -> str:
        return "".join(self._parts)


def load_html(source: str | Path, source_kind: SourceKind = SourceKind.FILE) -> str:
    if source_kind is SourceKind.FILE:
        return _decode_html_bytes(Path(source).read_bytes())
    if source_kind is SourceKind.HTML_STRING:
        return str(source)
    if source_kind is SourceKind.URL:
        return _load_url(str(source), UrlFetchConfig.from_environment())

    raise ValueError(f"Unsupported source_kind: {source_kind}")


def _decode_html_bytes(payload: bytes, content_type: str | None = None) -> str:
    charset = None
    if content_type:
        for part in content_type.split(";"):
            key, _, value = part.strip().partition("=")
            if key.lower() == "charset" and value:
                charset = value.strip().strip('"\'')
                break

    encodings = [encoding for encoding in [charset, "utf-8-sig", "utf-8", "latin-1"] if encoding]
    for encoding in encodings:
        try:
            return payload.decode(encoding)
        except UnicodeDecodeError:
            continue
    return payload.decode("utf-8", errors="replace")


def _validate_http_url(url: str) -> str:
    parsed = urlsplit(url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"Unsupported URL source: {url}")
    return url


def _load_url(url: str, config: UrlFetchConfig) -> str:
    safe_url = _validate_http_url(url)
    if not config.enabled:
        raise ValueError("URL ingestion is disabled for this runtime environment")

    request = Request(safe_url, headers={"User-Agent": "html-to-deck/1.0"})

    last_error: Exception | None = None
    for attempt in range(config.max_retries + 1):
        try:
            with urlopen(request, timeout=config.timeout_seconds) as response:
                payload = response.read()
                content_type = response.headers.get("Content-Type")
                return _decode_html_bytes(payload, content_type=content_type)
        except (TimeoutError, URLError) as exc:  # pragma: no cover - exercised via monkeypatch
            last_error = exc
            if attempt >= config.max_retries:
                break
            if config.retry_backoff_seconds > 0:
                time.sleep(config.retry_backoff_seconds * (attempt + 1))

    raise RuntimeError(f"Failed to fetch URL source: {safe_url}") from last_error


def normalize_snapshot(html: str) -> str:
    """Normalize HTML into a deterministic representation."""
    parser = _NormalizingHTMLParser()
    parser.feed(html)
    parser.close()
    return parser.normalized_html()
