from pathlib import Path


STRATEGY_DOCS = (
    "docs/nature_claim_strategy.md",
    "docs/editorial_significance_rationale.md",
    "docs/known_risks_and_mitigation.md",
    "docs/validation_design.md",
    "docs/model_interpretability_plan.md",
    "docs/robustness_and_falsification_plan.md",
    "docs/data_ethics_and_licensing.md",
    "docs/target_journal_decision_tree.md",
    "docs/minimum_publishable_evidence_slice.md",
)


def test_strategy_docs_exist_and_keep_claims_evidence_gated() -> None:
    for raw_path in STRATEGY_DOCS:
        path = Path(raw_path)
        text = path.read_text(encoding="utf-8")
        assert path.exists()
        assert "中文" in text
        lower = text.lower()
        assert any(term in lower for term in ("result", "evidence", "validation", "hypotheses", "pilot"))


def test_minimum_evidence_slice_defines_stop_rules() -> None:
    text = Path("docs/minimum_publishable_evidence_slice.md").read_text(encoding="utf-8")

    assert "Stop rules" in text
    assert "Pilot Fig. 1" in text
    assert "Pilot Fig. 2" in text
    assert "Pilot Fig. 3" in text
