from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline import run_pipeline, stable_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Run html-to-deck v1 pipeline")
    parser.add_argument("html_path", type=Path, help="Path to input HTML fixture")
    args = parser.parse_args()

    artifacts = run_pipeline(args.html_path)
    print(stable_json(artifacts["deck_json"]))


if __name__ == "__main__":
    main()
