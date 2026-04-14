from __future__ import annotations

from .checks import run_all_checks
from .models import AuditReport, DeckSpec


def run_audit_on_final_deck_spec(final_deck_spec: DeckSpec) -> AuditReport:
    """Run complete audit suite against the final assembled deck spec."""

    return AuditReport(warnings=run_all_checks(final_deck_spec))
