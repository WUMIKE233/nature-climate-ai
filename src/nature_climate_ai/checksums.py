from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path

from .qc import DATA_EXTENSIONS


IGNORED_DATA_PARTS = {"metadata", "checksums"}
DEFAULT_CHUNK_SIZE = 1024 * 1024


@dataclass(frozen=True)
class ChecksumRow:
    path: str
    bytes: int
    algorithm: str
    checksum: str


@dataclass(frozen=True)
class ChecksumAudit:
    root: Path
    rows: tuple[ChecksumRow, ...]

    @property
    def ready(self) -> bool:
        return bool(self.rows)


def _is_checksum_candidate(path: Path, root: Path) -> bool:
    if not path.is_file():
        return False
    relative = path.relative_to(root)
    if any(part in IGNORED_DATA_PARTS for part in relative.parts):
        return False
    return path.suffix.lower() in DATA_EXTENSIONS or path.name.endswith(".zarr")


def compute_sha256(path: str | Path, chunk_size: int = DEFAULT_CHUNK_SIZE) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def audit_data_checksums(root: str | Path = "data") -> ChecksumAudit:
    root_path = Path(root)
    if not root_path.exists():
        return ChecksumAudit(root=root_path, rows=())

    rows: list[ChecksumRow] = []
    for path in sorted(root_path.rglob("*")):
        if not _is_checksum_candidate(path, root_path):
            continue
        rows.append(
            ChecksumRow(
                path=path.as_posix(),
                bytes=path.stat().st_size,
                algorithm="sha256",
                checksum=compute_sha256(path),
            )
        )
    return ChecksumAudit(root=root_path, rows=tuple(rows))


def write_checksum_csv(audit: ChecksumAudit, output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "bytes", "algorithm", "checksum"])
        writer.writeheader()
        for row in audit.rows:
            writer.writerow(row.__dict__)
    return output


def render_checksum_report(audit: ChecksumAudit, csv_path: str | Path) -> str:
    status = "READY_FOR_DATA_INVENTORY_REVIEW" if audit.ready else "NOT_READY"
    lines = [
        "# Data checksum audit",
        "",
        f"Status: {status}",
        f"Root: {audit.root.as_posix()}",
        f"CSV: {Path(csv_path).as_posix()}",
        "",
        "metric | value",
        "--- | ---",
        f"checksum_rows | {len(audit.rows)}",
        f"ignored_parts | {', '.join(sorted(IGNORED_DATA_PARTS))}",
        "",
        "## Interpretation",
        "",
        "This audit records SHA-256 checksums for local data files that can support later Data Availability and reproducibility statements. It does not verify provider credentials, data-use permissions or scientific quality control.",
        "",
        "## Files",
        "",
    ]
    if audit.rows:
        lines.extend(["path | bytes | algorithm | checksum", "--- | ---: | --- | ---"])
        for row in audit.rows[:100]:
            lines.append(f"{row.path} | {row.bytes} | {row.algorithm} | {row.checksum}")
        if len(audit.rows) > 100:
            lines.append(f"... | ... | ... | {len(audit.rows) - 100} additional files omitted from report")
    else:
        lines.append("- No checksumable data files found. Downloaded public data or generated intermediate artifacts are still required.")

    lines.extend(
        [
            "",
            "## 中文审阅说明",
            "",
            "本审计为本地数据文件生成 SHA-256 校验值，用于后续数据可用性和复现说明。它不会验证账号权限、数据政策合规性或科学质量控制；没有真实数据文件时应保持 NOT_READY。",
        ]
    )
    return "\n".join(lines) + "\n"


def run_checksum_audit_command(
    root: str | Path,
    output_path: str | Path,
    csv_path: str | Path,
) -> tuple[ChecksumAudit, Path, Path]:
    audit = audit_data_checksums(root)
    csv_output = write_checksum_csv(audit, csv_path)
    report_output = Path(output_path)
    report_output.parent.mkdir(parents=True, exist_ok=True)
    report_output.write_text(render_checksum_report(audit, csv_output), encoding="utf-8")
    return audit, report_output, csv_output
