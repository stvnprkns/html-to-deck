from __future__ import annotations

import math
from dataclasses import dataclass

from extract.models import SourceBlock
from narrative.models import DeckNarrative, SlideIntent


COMMUNICATION_JOBS: dict[str, tuple[str, ...]] = {
    "context": ("orient",),
    "performance": ("report_performance",),
    "risks": ("surface_risks",),
    "next_steps": ("drive_alignment",),
    "problem": ("frame_problem",),
    "solution": ("present_solution",),
    "proof": ("build_trust",),
    "offer": ("explain_offer",),
    "close": ("call_to_action",),
    "approach": ("describe_approach",),
    "plan": ("sequence_plan",),
    "investment": ("justify_investment",),
    "decision": ("request_decision",),
    "question": ("define_question",),
    "method": ("explain_method",),
    "findings": ("present_findings",),
    "implications": ("interpret_findings",),
    "actions": ("propose_actions",),
}

MAX_BULLETS_PER_SLIDE = 6
MAX_WORDS_PER_SLIDE = 45


@dataclass(frozen=True)
class CandidateSlide:
    section: str
    block_ids: list[int]


def map_to_slide_intents(blocks: list[SourceBlock], narrative: DeckNarrative) -> list[SlideIntent]:
    candidates = _partition_blocks(blocks, narrative.sections)
    intents: list[SlideIntent] = []

    for candidate in candidates:
        indexed_blocks = [(block_id, blocks[block_id]) for block_id in candidate.block_ids]
        overload_score = _overload_score([block for _, block in indexed_blocks])
        communication_job = COMMUNICATION_JOBS.get(candidate.section, ("inform",))[0]

        if overload_score <= 1.0:
            intents.append(
                SlideIntent(
                    communication_job=communication_job,
                    section=candidate.section,
                    supporting_block_ids=candidate.block_ids,
                    overload_score=overload_score,
                )
            )
            continue

        split_groups = _split_for_clarity(indexed_blocks)
        for split_group in split_groups:
            block_ids = [block_id for block_id, _ in split_group]
            split_blocks = [block for _, block in split_group]
            intents.append(
                SlideIntent(
                    communication_job=communication_job,
                    section=candidate.section,
                    supporting_block_ids=block_ids,
                    overload_score=_overload_score(split_blocks),
                )
            )

    return intents


def _partition_blocks(blocks: list[SourceBlock], sections: list[str]) -> list[CandidateSlide]:
    if not sections:
        return [CandidateSlide(section="context", block_ids=list(range(len(blocks))))]

    partition_size = max(1, math.ceil(len(blocks) / len(sections)))
    slides: list[CandidateSlide] = []
    for i, section in enumerate(sections):
        start = i * partition_size
        if start >= len(blocks):
            break
        end = min(len(blocks), start + partition_size)
        slides.append(CandidateSlide(section=section, block_ids=list(range(start, end))))
    return slides


def _overload_score(blocks: list[SourceBlock]) -> float:
    word_count = sum(len(block.text.split()) for block in blocks)
    bullet_count = sum(len(block.metadata.get("items", [])) if block.block_type == "list" else 1 for block in blocks)
    return max(word_count / MAX_WORDS_PER_SLIDE, bullet_count / MAX_BULLETS_PER_SLIDE)


def _split_for_clarity(indexed_blocks: list[tuple[int, SourceBlock]]) -> list[list[tuple[int, SourceBlock]]]:
    groups: list[list[tuple[int, SourceBlock]]] = []
    current: list[tuple[int, SourceBlock]] = []
    for indexed_block in indexed_blocks:
        tentative = current + [indexed_block]
        if current and _overload_score([block for _, block in tentative]) > 1.0:
            groups.append(current)
            current = [indexed_block]
        else:
            current = tentative
    if current:
        groups.append(current)
    return groups
