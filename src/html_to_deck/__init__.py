"""html_to_deck package.

The package is structured as a stage-based pipeline with a strict boundary:
renderers consume canonical schema models and must not import extraction or
narrative internals directly.
"""

from .pipeline.orchestrator import HtmlToDeckPipeline

__all__ = ["HtmlToDeckPipeline"]
