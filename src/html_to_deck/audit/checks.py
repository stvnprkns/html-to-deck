"""Audit deck coherence and quality constraints."""

from __future__ import annotations

from .models import AuditReport, AuditWarning
from ..schema.ir import DeckDocument

_MAX_TEXT_WORDS = 110
_IMAGE_LIKE_BLOCK_TYPES = {
    "image",
    "image_with_caption",
    "figure",
    "diagram_image",
    "screenshot",
}


def run_quality_checks(deck: DeckDocument) -> AuditReport:
    warnings: list[AuditWarning] = []
    if not deck.slides:
        warnings.append(
            AuditWarning(
                slide_id="deck",
                check="deck_has_no_slides",
                severity="critical",
                confidence=0.99,
                actionable="Generate at least one slide before rendering outputs.",
            )
        )
    warnings.extend(_check_too_much_text(deck))
    warnings.extend(_check_mixed_communication_jobs(deck))
    warnings.extend(_check_evidence_and_provenance(deck))
    warnings.extend(_check_diagram_should_be_code(deck))
    return AuditReport(warnings=warnings)


def _check_too_much_text(deck: DeckDocument) -> list[AuditWarning]:
    out: list[AuditWarning] = []
    for index, slide in enumerate(deck.slides, start=1):
        text_parts = [slide.title, *slide.bullets]
        words = sum(len(part.split()) for part in text_parts)
        if words > _MAX_TEXT_WORDS:
            out.append(
                AuditWarning(
                    slide_id=f"slide-{index}",
                    check="too_much_text_per_slide",
                    severity="medium",
                    confidence=0.88,
                    actionable=f"Trim to ~{_MAX_TEXT_WORDS} words or split this into two slides.",
                )
            )
    return out


def _check_mixed_communication_jobs(deck: DeckDocument) -> list[AuditWarning]:
    out: list[AuditWarning] = []
    for index, slide in enumerate(deck.slides, start=1):
        communication_job = str(slide.metadata.get("communication_job", ""))
        jobs = {token.strip().lower() for token in communication_job.split("+") if token.strip()}
        if len(jobs) > 1:
            out.append(
                AuditWarning(
                    slide_id=f"slide-{index}",
                    check="mixed_communication_jobs",
                    severity="high",
                    confidence=0.86,
                    actionable="Use one primary communication job per slide (inform, persuade, decide, or align).",
                )
            )
    return out


def _check_evidence_and_provenance(deck: DeckDocument) -> list[AuditWarning]:
    out: list[AuditWarning] = []
    for index, slide in enumerate(deck.slides, start=1):
        claims = slide.metadata.get("claims")
        if not isinstance(claims, list):
            continue

        missing = [
            claim
            for claim in claims
            if isinstance(claim, dict)
            and (not claim.get("has_evidence") or not claim.get("provenance"))
        ]
        if missing:
            out.append(
                AuditWarning(
                    slide_id=f"slide-{index}",
                    check="missing_evidence_or_provenance",
                    severity="critical",
                    confidence=0.94,
                    actionable="Attach evidence and citation provenance for each explicit claim.",
                )
            )
    return out


def _check_diagram_should_be_code(deck: DeckDocument) -> list[AuditWarning]:
    """Warn when diagram intent is delivered as an image block without exception."""

    out: list[AuditWarning] = []
    for index, slide in enumerate(deck.slides, start=1):
        metadata = slide.metadata
        block_type = str(metadata.get("block_type", "")).lower()
        visual_intent = str(metadata.get("visual_intent", "")).lower()
        diagram_source = str(metadata.get("diagram_source", "")).lower()

        is_diagram_intent = visual_intent == "diagram" or bool(metadata.get("diagram_intent"))
        uses_image_like_block = block_type in _IMAGE_LIKE_BLOCK_TYPES
        has_explicit_exception = bool(metadata.get("diagram_exception"))
        is_code_spec_diagram = diagram_source in {"code_spec", "code-spec", "dsl"}

        if is_diagram_intent and uses_image_like_block and not is_code_spec_diagram and not has_explicit_exception:
            out.append(
                AuditWarning(
                    slide_id=f"slide-{index}",
                    check="diagram_should_be_code",
                    severity="high",
                    confidence=0.91,
                    actionable=(
                        "Use a code-spec diagram (or add metadata.diagram_exception=true "
                        "with justification) instead of an image-backed diagram."
                    ),
                )
            )
    return out
