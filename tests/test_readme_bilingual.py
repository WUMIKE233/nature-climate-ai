from pathlib import Path


def test_readme_is_bilingual() -> None:
    text = Path("README.md").read_text(encoding="utf-8")
    assert "## English" in text
    assert "## 中文" in text
    assert any("\u4e00" <= character <= "\u9fff" for character in text)


def test_data_readme_is_bilingual() -> None:
    text = Path("data/README.md").read_text(encoding="utf-8")
    assert "## English" in text
    assert "## 中文" in text
