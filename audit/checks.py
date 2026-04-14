from __future__ import annotations

from .models import AuditWarning, DeckSpec

_MAX_TEXT_WORDS = 110
_IMAGE_LIKE_BLOCK_TYPES = {
    "image",
    "image_with_caption",
    "figure",
    "diagram_image",
    "screenshot",
}


def run_all_checks(deck: DeckSpec) -> list[AuditWarning]:
    warnings: list[AuditWarning] = []
    warnings.extend(_check_too_much_text(deck))
    warnings.extend(_check_mixed_communication_jobs(deck))
    warnings.extend(_check_title_takeaway_alignment(deck))
    warnings.extend(_check_evidence_and_provenance(deck))
    warnings.extend(_check_pattern_rhythm(deck))
    warnings.extend(_check_diagram_should_be_code(deck))
    return warnings


def _check_too_much_text(deck: DeckSpec) -> list[AuditWarning]:
    out: list[AuditWarning] = []
    for slide in deck.slides:
        words = sum(len(block.split()) for block in slide.text_blocks)
        if words > _MAX_TEXT_WORDS:
            out.append(
                AuditWarning(
                    slide_id=slide.id,
                    check="too_much_text_per_slide",
                    severity="medium",
                    confidence=0.88,
                    actionable=f"Trim to ~{_MAX_TEXT_WORDS} words or split this into two slides.",
                )
            )
    return out


def _check_mixed_communication_jobs(deck: DeckSpec) -> list[AuditWarning]:
    out: list[AuditWarning] = []
    for slide in deck.slides:
        jobs = {token.strip().lower() for token in slide.communication_job.split("+") if token.strip()}
        if len(jobs) > 1:
            out.append(
                AuditWarning(
                    slide_id=slide.id,
                    check="mixed_communication_jobs",
                    severity="high",
                    confidence=0.86,
                    actionable="Use one primary communication job per slide (inform, persuade, decide, or align).",
                )
            )
    return out


def _check_title_takeaway_alignment(deck: DeckSpec) -> list[AuditWarning]:
    out: list[AuditWarning] = []
    for slide in deck.slides:
        title_tokens = {t.lower() for t in slide.title.split() if len(t) > 3}
        takeaway_tokens = {t.lower() for t in slide.takeaway.split() if len(t) > 3}
        overlap = len(title_tokens & takeaway_tokens)
        baseline = max(1, min(len(title_tokens), len(takeaway_tokens)))
        if overlap / baseline < 0.3:
            out.append(
                AuditWarning(
                    slide_id=slide.id,
                    check="weak_title_takeaway_alignment",
                    severity="medium",
                    confidence=0.73,
                    actionable="Rewrite title to mirror the core takeaway using shared keywords.",
                )
            )
    return out


def _check_evidence_and_provenance(deck: DeckSpec) -> list[AuditWarning]:
    out: list[AuditWarning] = []
    for slide in deck.slides:
        missing = [claim for claim in slide.claims if not claim.has_evidence or not claim.provenance]
        if missing:
            out.append(
                AuditWarning(
                    slide_id=slide.id,
                    check="missing_evidence_or_provenance",
                    severity="critical",
                    confidence=0.94,
                    actionable="Attach evidence and citation provenance for each explicit claim.",
                )
            )
    return out


def _check_pattern_rhythm(deck: DeckSpec) -> list[AuditWarning]:
    out: list[AuditWarning] = []
    streak = 0
    previous = None
    for slide in deck.slides:
        if slide.pattern_signature == previous:
            streak += 1
        else:
            streak = 0
        if streak >= 2:
            out.append(
                AuditWarning(
                    slide_id=slide.id,
                    check="inconsistent_pattern_rhythm",
                    severity="low",
                    confidence=0.77,
                    actionable="Introduce a variation in slide pattern rhythm every 2-3 slides.",
                )
            )
        previous = slide.pattern_signature
    return out


def _check_diagram_should_be_code(deck: DeckSpec) -> list[AuditWarning]:
    out: list[AuditWarning] = []
    for slide in deck.slides:
        metadata = slide.body_metadata
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
                    slide_id=slide.id,
                    check="diagram_should_be_code",
                    severity="high",
                    confidence=0.91,
                    actionable=(
                        "Use a code-spec diagram (or add body_metadata.diagram_exception=true "
                        "with justification) instead of an image-backed diagram."
                    ),
                )
            )
    return out
