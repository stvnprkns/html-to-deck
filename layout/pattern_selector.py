from __future__ import annotations

from dataclasses import dataclass

from narrative.models import SlideIntent


@dataclass(frozen=True)
class LayoutChoice:
    pattern: str
    rationale: str


LAYOUT_RULES: dict[str, tuple[str, ...]] = {
    "orient": ("title_with_supporting_points", "hero_statement"),
    "report_performance": ("kpi_grid", "chart_with_takeaway", "title_and_bullets"),
    "surface_risks": ("risk_matrix", "two_column_risks_mitigations", "title_and_bullets"),
    "drive_alignment": ("timeline_next_steps", "checklist", "title_and_bullets"),
    "frame_problem": ("problem_statement", "evidence_bullets"),
    "present_solution": ("solution_blueprint", "before_after", "title_and_bullets"),
    "build_trust": ("proof_points", "testimonial_quote", "title_and_bullets"),
    "explain_offer": ("package_tiers", "comparison_table", "title_and_bullets"),
    "call_to_action": ("single_cta", "timeline_next_steps"),
    "describe_approach": ("process_steps", "swimlane", "title_and_bullets"),
    "sequence_plan": ("roadmap", "gantt_simple", "title_and_bullets"),
    "justify_investment": ("investment_breakdown", "kpi_grid", "title_and_bullets"),
    "request_decision": ("decision_log", "single_cta", "title_and_bullets"),
    "define_question": ("question_hypothesis", "title_and_bullets"),
    "explain_method": ("method_flow", "title_and_bullets"),
    "present_findings": ("findings_grid", "chart_with_takeaway", "title_and_bullets"),
    "interpret_findings": ("implication_tree", "title_and_bullets"),
    "propose_actions": ("prioritized_actions", "timeline_next_steps", "title_and_bullets"),
    "inform": ("title_and_bullets",),
}

OVERLOAD_FALLBACKS: tuple[str, ...] = ("title_and_bullets", "section_header")


def choose_layout_pattern(intent: SlideIntent) -> LayoutChoice:
    options = LAYOUT_RULES.get(intent.communication_job, LAYOUT_RULES["inform"])
    if intent.overload_score > 1.0:
        return LayoutChoice(pattern=OVERLOAD_FALLBACKS[0], rationale="Overloaded intent uses highest-clarity fallback")

    return LayoutChoice(pattern=options[0], rationale=f"Primary pattern for communication job '{intent.communication_job}'")
