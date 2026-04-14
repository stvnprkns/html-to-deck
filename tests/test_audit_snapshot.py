import json
import os
import unittest
from pathlib import Path

from audit.engine import run_audit_on_final_deck_spec
from audit.models import DeckSpec, SlideClaim, SlideSpec


class AuditSnapshotTest(unittest.TestCase):
    def test_final_deck_audit_snapshot(self) -> None:
        deck = DeckSpec(
            slides=[
                SlideSpec(
                    id="s1",
                    title="Q2 pipeline coverage",
                    takeaway="Pipeline quality improved but conversion risk remains",
                    communication_job="inform+decide",
                    text_blocks=["word " * 120],
                    pattern_signature="metric_then_chart",
                    claims=[SlideClaim("Coverage reached 3.2x", has_evidence=True, provenance="CRM export")],
                ),
                SlideSpec(
                    id="s2",
                    title="Customer wins this month",
                    takeaway="Three enterprise logos validated pricing power",
                    communication_job="inform",
                    text_blocks=["Highlights and logos."],
                    pattern_signature="metric_then_chart",
                    claims=[SlideClaim("Enterprise ACV increased 18%", has_evidence=False, provenance=None)],
                ),
                SlideSpec(
                    id="s3",
                    title="Execution next steps",
                    takeaway="Focus on onboarding to reduce churn",
                    communication_job="align",
                    text_blocks=["Owners and milestones."],
                    pattern_signature="metric_then_chart",
                    claims=[SlideClaim("Onboarding cut churn 2 points", has_evidence=True, provenance="CS analysis")],
                ),
            ]
        )

        report = run_audit_on_final_deck_spec(deck)
        payload = json.dumps(report.to_dict(), indent=2, sort_keys=True)

        snapshot_path = Path(__file__).parent / "snapshots" / "final_deck_audit_report.json"
        if os.getenv("UPDATE_SNAPSHOTS") == "1":
            snapshot_path.write_text(payload + "\n", encoding="utf-8")

        expected = snapshot_path.read_text(encoding="utf-8").strip()
        self.assertEqual(expected, payload)


if __name__ == "__main__":
    unittest.main()
