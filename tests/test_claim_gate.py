from pathlib import Path

from nature_climate_ai.claim_gate import inspect_manuscript


def test_manuscript_remains_evidence_gated() -> None:
    report = inspect_manuscript(Path("manuscript/nature_article_draft.md"))
    assert report.result_placeholders > 0
