from pathlib import Path

from nature_climate_ai.reproducibility import (
    audit_environment,
    run_reproducibility_audit_command,
    write_command_manifest,
    write_compute_budget,
    write_environment_yml,
    write_requirements_lock,
    write_seed_manifest,
)


def test_audit_environment_records_core_packages() -> None:
    audit = audit_environment()

    assert audit.python_version[0].isdigit()
    assert "python" in audit.executable.lower()
    assert "numpy" in audit.package_versions
    assert audit.ready


def test_write_command_manifest_records_submission_gate(tmp_path: Path) -> None:
    output = write_command_manifest(tmp_path / "command_manifest.csv")
    text = output.read_text(encoding="utf-8")

    assert "submission-gate" in text
    assert "expected_current_status" in text


def test_reproducibility_support_files_are_written(tmp_path: Path) -> None:
    audit = audit_environment()
    environment = write_environment_yml(tmp_path / "environment.yml", audit)
    lock = write_requirements_lock(tmp_path / "requirements-lock.txt", audit)
    seeds = write_seed_manifest(tmp_path / "random_seed_manifest.yaml")
    compute = write_compute_budget(tmp_path / "compute_budget.md")

    assert "name: nature-climate-ai" in environment.read_text(encoding="utf-8")
    assert "numpy==" in lock.read_text(encoding="utf-8")
    assert "global_seed" in seeds.read_text(encoding="utf-8")
    assert "中文审阅说明" in compute.read_text(encoding="utf-8")


def test_reproducibility_audit_command_writes_outputs(tmp_path: Path) -> None:
    audit, report, manifest = run_reproducibility_audit_command(
        report_path=tmp_path / "environment_report.md",
        command_manifest_path=tmp_path / "command_manifest.csv",
        environment_yml_path=tmp_path / "environment.yml",
        requirements_lock_path=tmp_path / "requirements-lock.txt",
        seed_manifest_path=tmp_path / "random_seed_manifest.yaml",
        compute_budget_path=tmp_path / "compute_budget.md",
    )

    assert audit.ready
    assert report.exists()
    assert manifest.exists()
    assert (tmp_path / "environment.yml").exists()
    assert (tmp_path / "requirements-lock.txt").exists()
    assert (tmp_path / "random_seed_manifest.yaml").exists()
    assert (tmp_path / "compute_budget.md").exists()
    report_text = report.read_text(encoding="utf-8")
    assert "Reproducibility environment audit" in report_text
    assert "中文审阅说明" in report_text
    assert "random_seed_manifest.yaml" in report_text
