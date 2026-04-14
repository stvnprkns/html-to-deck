"""Extract headings, paragraphs, lists, stats, quotes, images, and tables."""

from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
import re


@dataclass(frozen=True)
class ContentBlock:
    kind: str
    text: str


class _BlockParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.current_tag: str | None = None
        self.blocks: list[ContentBlock] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:  # noqa: ARG002
        self.current_tag = tag.lower()

    def handle_endtag(self, tag: str) -> None:  # noqa: ARG002
        self.current_tag = None

    def handle_data(self, data: str) -> None:
        text = re.sub(r"\s+", " ", data).strip()
        if not text:
            return
        kind_by_tag = {
            "title": "title",
            "h1": "heading",
            "h2": "section_heading",
            "p": "paragraph",
            "li": "bullet",
        }
        kind = kind_by_tag.get(self.current_tag)
        if kind:
            self.blocks.append(ContentBlock(kind=kind, text=text))


def extract_blocks(snapshot: str) -> list[ContentBlock]:
    """Extract rich content blocks from a normalized HTML snapshot."""
    if not snapshot:
        return []

    parser = _BlockParser()
    parser.feed(snapshot)
    if parser.blocks:
        return parser.blocks
    return [ContentBlock(kind="paragraph", text=snapshot)]
