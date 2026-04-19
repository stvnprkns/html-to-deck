"""Thin CLI for running the html_to_deck pipeline end-to-end."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .pipeline.orchestrator import HtmlToDeckPipeline
from .renderers.themes import VALID_THEMES, normalize_theme_id
from .types import PipelineInput, SourceKind


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert HTML into slide-deck output")
    parser.add_argument("--input", required=True, help="Input source (file path, URL, or raw HTML)")
    parser.add_argument("--output", required=True, help="Output file path")
    parser.add_argument(
        "--source-kind",
        choices=tuple(kind.value for kind in SourceKind),
        default=SourceKind.FILE.value,
        help="Input source type.",
    )
    parser.add_argument(
        "--format",
        choices=("auto", "json", "html"),
        default="auto",
        help="Renderer format. auto infers from output extension.",
    )
    parser.add_argument(
        "--theme",
        choices=VALID_THEMES,
        default="default",
        help="Standalone HTML viewer theme (JSON output ignores this).",
    )
    parser.add_argument(
        "--extra-css",
        default=None,
        metavar="PATH",
        help="Optional CSS file appended after the theme stylesheet (HTML output only).",
    )
    parser.add_argument(
        "--audit-output",
        choices=("summary", "json", "none"),
        default="summary",
        help="Emit audit report as summary or JSON in stdout.",
    )
    return parser


def _load_extra_css(path_str: str | None) -> str | None:
    if not path_str:
        return None
    path = Path(path_str)
    return path.read_text(encoding="utf-8")


def main() -> int:
    args = build_parser().parse_args()
    output_path = Path(args.output)
    theme = normalize_theme_id(args.theme)
    extra_css = _load_extra_css(args.extra_css)

    if args.format == "auto":
        pipeline = HtmlToDeckPipeline.from_output_path(
            output_path,
            html_theme=theme,
            html_extra_css=extra_css,
        )
    elif args.format == "html":
        from .renderers import HtmlDeckRenderer

        pipeline = HtmlToDeckPipeline(renderer=HtmlDeckRenderer(theme=theme, extra_css=extra_css))
    else:
        pipeline = HtmlToDeckPipeline.default()

    source_kind = SourceKind(args.source_kind)
    source = Path(args.input) if source_kind is SourceKind.FILE else args.input
    result = pipeline.run(PipelineInput(source=source, source_kind=source_kind), output_path)
    print(result.output_path)

    if args.audit_output == "summary":
        print(result.audit_report.summary_line)
    elif args.audit_output == "json":
        print(json.dumps(result.audit_report.to_dict(), sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
