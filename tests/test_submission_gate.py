from nature_climate_ai.submission_gate import evaluate_submission_gate


def test_submission_gate_blocks_unverified_manuscript() -> None:
    report = evaluate_submission_gate(
        "manuscript/nature_article_draft.md",
        "evidence/registry.yaml",
    )
    assert not report.ready
    assert any("RESULT_REQUIRED" in reason for reason in report.reasons)
    assert any("evidence items" in reason for reason in report.reasons)
