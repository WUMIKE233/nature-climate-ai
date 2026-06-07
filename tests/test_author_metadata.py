from pathlib import Path

import yaml

from nature_climate_ai.author_metadata import audit_author_metadata, run_author_metadata_audit_command


def test_author_metadata_template_is_not_ready() -> None:
    audit = audit_author_metadata("manuscript/author_metadata.yaml")

    assert not audit.ready
    assert any(issue.issue == "pending_author_input" for issue in audit.issues)


def test_complete_author_metadata_is_ready(tmp_path: Path) -> None:
    metadata = tmp_path / "author_metadata.yaml"
    metadata.write_text(
        yaml.safe_dump(
            {
                "status": "complete",
                "corresponding_author": {
                    "name": "Jane Doe",
                    "email": "jane@example.org",
                    "affiliation": "Example University",
                },
                "authors": [
                    {
                        "name": "Jane Doe",
                        "affiliation": "Example University",
                        "contribution": "Conceptualization and writing",
                    }
                ],
                "contributions": {
                    "conceptualization": "Jane Doe",
                    "data_curation": "Jane Doe",
                    "formal_analysis": "Jane Doe",
                    "methodology": "Jane Doe",
                    "software": "Jane Doe",
                    "writing_original_draft": "Jane Doe",
                    "writing_review_editing": "Jane Doe",
                },
                "acknowledgements": "No additional acknowledgements.",
                "funding": "No external funding.",
                "competing_interests": "The authors declare no competing interests.",
                "data_policy_confirmed_by": "Jane Doe",
                "submission_approval": {
                    "all_authors_approved": True,
                    "not_under_consideration_elsewhere": True,
                },
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    audit = audit_author_metadata(metadata)

    assert audit.ready
    assert audit.issues == ()


def test_author_metadata_audit_command_writes_outputs(tmp_path: Path) -> None:
    metadata = tmp_path / "author_metadata.yaml"
    metadata.write_text("status: PENDING_AUTHOR_INPUT\n", encoding="utf-8")

    audit, report, csv_output = run_author_metadata_audit_command(
        metadata_path=metadata,
        output_path=tmp_path / "author_metadata_audit.md",
        csv_path=tmp_path / "author_metadata_status.csv",
    )

    assert not audit.ready
    assert report.exists()
    assert csv_output.exists()
    assert "Author metadata audit" in report.read_text(encoding="utf-8")
    assert "field,issue,value" in csv_output.read_text(encoding="utf-8")
