"""Thin CLI for running the html_to_deck pipeline end-to-end."""

from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline.orchestrator import HtmlToDeckPipeline
from .types import PipelineInput


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert HTML into slide-deck output")
    parser.add_argument("--input", required=True, help="Input HTML file path")
    parser.add_argument("--output", required=True, help="Output file path")
    parser.add_argument(
        "--format",
        choices=("auto", "json", "html"),
        default="auto",
        help="Renderer format. auto infers from output extension.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    output_path = Path(args.output)
    if args.format == "auto":
        pipeline = HtmlToDeckPipeline.from_output_path(output_path)
    elif args.format == "html":
        from .renderers import HtmlDeckRenderer

        pipeline = HtmlToDeckPipeline(renderer=HtmlDeckRenderer())
    else:
        pipeline = HtmlToDeckPipeline.default()

    result = pipeline.run(PipelineInput(source=Path(args.input), is_file=True), output_path)
    print(result.output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
