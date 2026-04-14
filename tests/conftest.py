from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

FIXTURE_DIR = ROOT / "fixtures" / "html"


@pytest.fixture(scope="session")
def fixture_paths() -> list[Path]:
    return sorted(FIXTURE_DIR.glob("*.html"))
