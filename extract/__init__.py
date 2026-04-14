"""Content extraction package for source-to-slide pipeline."""

from .block_extractors import extract_blocks
from .models import SourceBlock

__all__ = ["extract_blocks", "SourceBlock"]
