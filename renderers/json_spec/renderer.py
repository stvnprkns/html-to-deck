"""Pure JSON renderer target for canonical DeckSpec objects."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from deckspec import DeckSpec


_FLOAT_PRECISION = Decimal("0.000001")


def _normalize_value(value: Any) -> Any:
    """Normalize values to deterministic, JSON-friendly primitives.

    - Dict keys are sorted recursively.
    - Sequence order is preserved.
    - Floats are quantized to 6 decimal places.
    - Negative zero is normalized to positive zero.
    """

    if is_dataclass(value):
        value = asdict(value)

    if isinstance(value, dict):
        return {key: _normalize_value(value[key]) for key in sorted(value)}

    if isinstance(value, list):
        return [_normalize_value(item) for item in value]

    if isinstance(value, tuple):
        return [_normalize_value(item) for item in value]

    if isinstance(value, float):
        quantized = Decimal(str(value)).quantize(_FLOAT_PRECISION, rounding=ROUND_HALF_UP)
        normalized = float(quantized)
        if normalized == 0.0:
            return 0.0
        return normalized

    return value


def render(deck: DeckSpec) -> str:
    """Render a canonical DeckSpec as deterministic JSON.

    The renderer is intentionally pure and contains no extraction, narrative
    inference, or layout-decision logic.
    """

    normalized = _normalize_value(deck)
    return json.dumps(
        normalized,
        sort_keys=True,
        indent=2,
        separators=(",", ": "),
        ensure_ascii=False,
    ) + "\n"
