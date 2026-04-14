"""Public package API entry points.

Using a dedicated API module avoids frequent merge conflicts in top-level
`__init__.py` while keeping a stable import for consumers.
"""

from .pipeline.orchestrator import HtmlToDeckPipeline

__all__ = ["HtmlToDeckPipeline"]
