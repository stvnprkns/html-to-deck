"""Small public API for converting HTML sources to deck output without importing stage internals."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from .audit import AuditReport
from .pipeline.orchestrator import HtmlToDeckPipeline
from .renderers import HtmlDeckRenderer
from .schema.ir import DeckDocument
from .types import PipelineInput, PipelineOutput, SourceKind

HtmlLayout = Literal["fullscreen", "embed"]


def convert(
    source: str | Path,
    output_path: str | Path,
    *,
    source_kind: SourceKind = SourceKind.FILE,
    format: Literal["auto", "json", "html"] = "auto",
    theme: str = "default",
    tokens_css: str | None = None,
    extra_css: str | None = None,
    layout: HtmlLayout = "fullscreen",
    show_audit_badge: bool = True,
    show_source_link: bool = True,
) -> PipelineOutput:
    """Run the full pipeline and write ``output_path``.

    ``format`` ``auto`` picks HTML vs JSON from the file extension (``.html`` / ``.htm`` → HTML).
    """
    out = Path(output_path)
    if format == "auto":
        pipeline = HtmlToDeckPipeline.from_output_path(
            out,
            html_theme=theme,
            html_tokens_css=tokens_css,
            html_extra_css=extra_css,
            html_layout=layout,
            html_show_audit_badge=show_audit_badge,
            html_show_source_link=show_source_link,
        )
    elif format == "html":
        pipeline = HtmlToDeckPipeline(
            renderer=HtmlDeckRenderer(
                theme=theme,
                tokens_css=tokens_css,
                extra_css=extra_css,
                layout=layout,
                show_audit_badge=show_audit_badge,
                show_source_link=show_source_link,
            )
        )
    else:
        pipeline = HtmlToDeckPipeline.default()

    return pipeline.run(PipelineInput(source=source, source_kind=source_kind), out)


def render_html_string(
    deck: DeckDocument,
    audit_report: AuditReport | None = None,
    *,
    theme: str = "default",
    tokens_css: str | None = None,
    extra_css: str | None = None,
    layout: HtmlLayout = "fullscreen",
    show_audit_badge: bool = True,
    show_source_link: bool = True,
) -> str:
    """Render an in-memory ``DeckDocument`` to HTML (no filesystem I/O)."""
    renderer = HtmlDeckRenderer(
        theme=theme,
        tokens_css=tokens_css,
        extra_css=extra_css,
        layout=layout,
        show_audit_badge=show_audit_badge,
        show_source_link=show_source_link,
    )
    return renderer.render(deck, audit_report if audit_report is not None else AuditReport(warnings=[]))
