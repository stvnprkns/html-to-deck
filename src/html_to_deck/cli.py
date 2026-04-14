"""Thin CLI for running the html_to_deck pipeline end-to-end."""

from __future__ import annotations

import argparse
import json
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
    parser.add_argument(
        "--audit-output",
        choices=("summary", "json", "none"),
        default="summary",
        help="Emit audit report as summary or JSON in stdout.",
    )
    return parser


def _format_audit_summary(audit_payload: dict[str, object]) -> str:
    counts = audit_payload["counts_by_severity"]
    assert isinstance(counts, dict)
    status = "BLOCKERS" if audit_payload["has_blockers"] else "OK"
    return (
        f"audit={status} "
        f"critical={counts.get('critical', 0)} "
        f"high={counts.get('high', 0)} "
        f"medium={counts.get('medium', 0)} "
        f"low={counts.get('low', 0)}"
    )


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

    audit_payload = result.audit_report.to_dict()
    if args.audit_output == "summary":
        print(_format_audit_summary(audit_payload))
    elif args.audit_output == "json":
        print(json.dumps(audit_payload, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
