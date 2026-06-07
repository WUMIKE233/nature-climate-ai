from pathlib import Path

from nature_climate_ai.public_release import audit_public_release, run_public_release_audit_command, scan_for_secret_patterns


def test_public_release_audit_reports_missing_git_repository(tmp_path: Path) -> None:
    audit = audit_public_release(tmp_path)

    assert not audit.ready
    assert any(issue.issue == "missing_git_repository" for issue in audit.issues)


def test_secret_scan_detects_assigned_high_risk_value(tmp_path: Path) -> None:
    path = tmp_path / "settings.env"
    path.write_text("API_KEY=" + "abcdefghijklmnopqrstuvwxyz" + "\n", encoding="utf-8")

    issues = scan_for_secret_patterns(tmp_path)

    assert len(issues) == 1
    assert issues[0].issue == "assigned_secret"


def test_secret_scan_ignores_policy_text(tmp_path: Path) -> None:
    path = tmp_path / "README.md"
    path.write_text("Do not store credentials, API keys, passwords or tokens in this repository.\n", encoding="utf-8")

    issues = scan_for_secret_patterns(tmp_path)

    assert issues == ()


def test_secret_scan_ignores_git_internal_files(tmp_path: Path) -> None:
    git_hooks = tmp_path / ".git" / "hooks"
    git_hooks.mkdir(parents=True)
    path = git_hooks / "pre-commit.py"
    path.write_text("API_KEY=" + "abcdefghijklmnopqrstuvwxyz" + "\n", encoding="utf-8")

    issues = scan_for_secret_patterns(tmp_path)

    assert issues == ()


def test_public_release_audit_command_writes_outputs(tmp_path: Path) -> None:
    audit, report, csv_output = run_public_release_audit_command(
        root=".",
        output_path=tmp_path / "public_release_audit.md",
        csv_path=tmp_path / "public_release_status.csv",
    )

    assert isinstance(audit.ready, bool)
    assert report.exists()
    assert csv_output.exists()
    assert "Public release audit" in report.read_text(encoding="utf-8")
    assert "category,path,issue,detail" in csv_output.read_text(encoding="utf-8")
