from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal

Severity = Literal["low", "medium", "high", "critical"]


@dataclass(frozen=True)
class DesignContext:
    """A compact view of slide design facts used by validator rules."""

    slide_id: str
    heading_level_count: int
    used_whitespace_ratio: float
    emphasis_token_count: int
    body_contrast_ratio: float
    pattern_signature: str


@dataclass(frozen=True)
class DesignIssue:
    slide_id: str
    rule: str
    severity: Severity
    confidence: float
    message: str
    remediation: str


_MIN_WHITESPACE_RATIO = 0.22
_MAX_EMPHASIS_TOKENS = 4
_MIN_BODY_CONTRAST = 4.5
_MAX_HIERARCHY_LEVELS = 3


def check_design_rules(slides: Iterable[DesignContext]) -> list[DesignIssue]:
    """Apply designer-informed rules for hierarchy, spacing, emphasis and rhythm."""

    issues: list[DesignIssue] = []
    last_pattern: str | None = None
    pattern_streak = 0

    for slide in slides:
        if slide.heading_level_count > _MAX_HIERARCHY_LEVELS:
            issues.append(
                DesignIssue(
                    slide_id=slide.slide_id,
                    rule="visual_hierarchy",
                    severity="medium",
                    confidence=0.87,
                    message="Too many hierarchy levels reduce scannability.",
                    remediation="Limit each slide to at most three heading levels and consolidate minor labels.",
                )
            )

        if slide.used_whitespace_ratio < _MIN_WHITESPACE_RATIO:
            issues.append(
                DesignIssue(
                    slide_id=slide.slide_id,
                    rule="spacing_breathing_room",
                    severity="high",
                    confidence=0.9,
                    message="Content density leaves too little breathing room.",
                    remediation="Increase margins or split dense regions into an additional slide.",
                )
            )

        if slide.emphasis_token_count > _MAX_EMPHASIS_TOKENS:
            issues.append(
                DesignIssue(
                    slide_id=slide.slide_id,
                    rule="emphasis_restraint",
                    severity="medium",
                    confidence=0.82,
                    message="Too many emphasis tokens compete for attention.",
                    remediation="Keep one primary emphasis and one secondary cue per slide.",
                )
            )

        if slide.body_contrast_ratio < _MIN_BODY_CONTRAST:
            issues.append(
                DesignIssue(
                    slide_id=slide.slide_id,
                    rule="contrast_readability",
                    severity="high",
                    confidence=0.95,
                    message="Body text contrast is below readability thresholds.",
                    remediation="Use darker foreground or lighter background to reach at least 4.5:1 contrast.",
                )
            )

        if last_pattern == slide.pattern_signature:
            pattern_streak += 1
        else:
            pattern_streak = 0

        if pattern_streak >= 2:
            issues.append(
                DesignIssue(
                    slide_id=slide.slide_id,
                    rule="repetition_with_variation",
                    severity="low",
                    confidence=0.76,
                    message="Consecutive slides repeat the same pattern without variation.",
                    remediation="Alternate layout emphasis (e.g., evidence-first vs takeaway-first) every 2-3 slides.",
                )
            )

        last_pattern = slide.pattern_signature

    return issues
