from pathlib import Path
import sys

from html_to_deck.pipeline.v1_compat import extract_content, ingest_html

sys.path.append(str(Path(__file__).resolve().parents[1]))
from extract import extract_blocks


def test_extract_stage_emits_meta_and_content(fixture_paths):
    for path in fixture_paths:
        extracted = extract_content(ingest_html(path))
        assert extracted["stage"] == "extract"
        assert extracted["meta"]["title"]
        assert extracted["meta"]["primary_heading"]
        assert isinstance(extracted["content"]["paragraphs"], list)


def test_markdown_image_becomes_warning_not_image_block():
    blocks = extract_blocks("![alt text](https://example.com/diagram.png)")
    assert blocks[0].block_type != "image"
    assert blocks[0].block_type == "warning"
    assert blocks[0].metadata["audit_tag"] == "reject_external_image_reference"


def test_mermaid_fenced_block_becomes_structured_diagram_spec():
    source = """```mermaid
flowchart TD
  A-->B
```"""
    blocks = extract_blocks(source)
    assert blocks[0].block_type == "diagram_spec"
    assert "flowchart TD" in blocks[0].text
    assert blocks[0].metadata["diagram_language"] == "mermaid"
