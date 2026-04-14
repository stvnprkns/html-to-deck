"""Stage 7: target-specific renderers.

Boundary rule: renderer modules may depend on `schema` and shared `types`,
not on `extract` or `narrative` internals.
"""

from .json_renderer import JsonDeckRenderer

__all__ = ["JsonDeckRenderer"]
