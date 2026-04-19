"""html-to-deck package."""

from .api import convert, render_html_string
from ._version import __version__

__all__ = ["__version__", "convert", "render_html_string"]
