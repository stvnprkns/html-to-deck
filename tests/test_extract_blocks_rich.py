from __future__ import annotations

from html_to_deck.extract.blocks import extract_blocks


def test_extracts_heading_and_paragraph_with_metadata() -> None:
    blocks = extract_blocks("# Title\n\nBody copy here.")

    assert [b.block_type for b in blocks] == ["heading", "paragraph"]
    assert blocks[0].text == "Title"
    assert blocks[0].metadata["level"] == 1
    assert blocks[0].metadata["confidence_score"] == 0.98
    assert blocks[1].text == "Body copy here."
    assert blocks[1].metadata["confidence_score"] == 0.9


def test_merges_mixed_list_markers_and_exposes_items_count() -> None:
    source = "- one\n* two\n1. three\n\nnext"

    blocks = extract_blocks(source)

    assert [b.block_type for b in blocks] == ["list", "paragraph"]
    assert blocks[0].metadata["items"] == ["one", "two", "three"]
    assert blocks[0].metadata["count"] == 3


def test_extracts_table_and_table_metadata() -> None:
    source = "| Name | Value |\n| --- | --- |\n| A | 10 |\n| B | 20 |"

    blocks = extract_blocks(source)

    assert len(blocks) == 1
    assert blocks[0].block_type == "table"
    assert blocks[0].metadata["columns"] == 2
    assert blocks[0].metadata["rows"] == [["Name", "Value"], ["A", "10"], ["B", "20"]]


def test_malformed_table_falls_back_to_paragraph() -> None:
    source = "| Name | Value |\n| --- | --- |\n| broken |"

    blocks = extract_blocks(source)

    assert len(blocks) == 1
    assert blocks[0].block_type == "paragraph"
    assert "| broken |" in blocks[0].text


def test_extracts_fenced_diagram_spec() -> None:
    source = "```mermaid\nflowchart TD\nA-->B\n```"

    blocks = extract_blocks(source)

    assert len(blocks) == 1
    assert blocks[0].block_type == "diagram_spec"
    assert blocks[0].metadata["diagram_language"] == "mermaid"
    assert blocks[0].metadata["source_format"] == "fenced_code"


def test_unclosed_fence_falls_back_to_paragraph() -> None:
    source = "```mermaid\nflowchart TD\nA-->B"

    blocks = extract_blocks(source)

    assert len(blocks) == 1
    assert blocks[0].block_type == "paragraph"
    assert "```mermaid" in blocks[0].text


def test_external_image_becomes_warning() -> None:
    blocks = extract_blocks("![alt](https://example.com/image.png)")

    assert len(blocks) == 1
    assert blocks[0].block_type == "warning"
    assert blocks[0].metadata["audit_tag"] == "reject_external_image_reference"
    assert blocks[0].metadata["src"] == "https://example.com/image.png"


def test_deterministic_order_index_and_block_ids() -> None:
    blocks = extract_blocks("## A\n\npara\n- x")

    assert [b.order_index for b in blocks] == [0, 1, 2]
    assert [b.block_id for b in blocks] == ["block-0000", "block-0001", "block-0002"]
