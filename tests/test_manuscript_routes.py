from pathlib import Path


def test_nature_and_science_routes_exist() -> None:
    assert Path("manuscript/nature_article_draft.md").exists()
    assert Path("manuscript/science_research_article_draft.md").exists()
    assert Path("manuscript/editorial_strategy.md").exists()


def test_both_routes_are_evidence_gated() -> None:
    nature = Path("manuscript/nature_article_draft.md").read_text(encoding="utf-8")
    science = Path("manuscript/science_research_article_draft.md").read_text(encoding="utf-8")
    assert "RESULT_REQUIRED" in nature
    assert "RESULT_REQUIRED" in science
