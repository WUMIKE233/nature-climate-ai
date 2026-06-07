from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


ERA5_LICENCE_URLS = {
    "reanalysis-era5-single-levels": "https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=download#manage-licences",
    "reanalysis-era5-land": "https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land?tab=download#manage-licences",
}


@dataclass(frozen=True)
class DownloadLogRow:
    source: str
    status: str
    local_path: str
    remote_id: str
    size_bytes: int
    sha256: str
    timestamp: str
    message: str


@dataclass(frozen=True)
class DownloadStatusReport:
    log_path: Path
    rows: tuple[DownloadLogRow, ...]
    missing_log: bool = False

    @property
    def status(self) -> str:
        if self.missing_log:
            return "NO_LOG"
        if not self.rows:
            return "NO_DOWNLOAD_ATTEMPTS"
        if self.success_count:
            return "READY_FOR_QC"
        if self.licence_blocked_count:
            return "BLOCKED_BY_LICENSE"
        if self.failed_count:
            return "FAILED"
        return "NOT_READY"

    @property
    def ready_for_qc(self) -> bool:
        return self.status == "READY_FOR_QC"

    @property
    def success_count(self) -> int:
        return sum(row.status == "success" for row in self.rows)

    @property
    def failed_count(self) -> int:
        return sum(row.status == "failed" for row in self.rows)

    @property
    def skipped_count(self) -> int:
        return sum(row.status == "skipped" for row in self.rows)

    @property
    def licence_blocked_count(self) -> int:
        return sum(_is_licence_block(row) for row in self.rows)

    @property
    def total_size_bytes(self) -> int:
        return sum(row.size_bytes for row in self.rows)


def _parse_int(value: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _is_licence_block(row: DownloadLogRow) -> bool:
    message = row.message.lower()
    return "required licences not accepted" in message or "required licence" in message


def _dataset_from_remote_id(remote_id: str) -> str:
    return remote_id.split("/", 1)[0]


def read_download_log(log_path: str | Path) -> DownloadStatusReport:
    path = Path(log_path)
    if not path.exists():
        return DownloadStatusReport(log_path=path, rows=(), missing_log=True)

    rows: list[DownloadLogRow] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(
                DownloadLogRow(
                    source=row.get("source", ""),
                    status=row.get("status", ""),
                    local_path=row.get("local_path", ""),
                    remote_id=row.get("remote_id", ""),
                    size_bytes=_parse_int(row.get("size_bytes", "0")),
                    sha256=row.get("sha256", ""),
                    timestamp=row.get("timestamp", ""),
                    message=row.get("message", ""),
                )
            )
    return DownloadStatusReport(log_path=path, rows=tuple(rows))


def render_download_status(report: DownloadStatusReport) -> str:
    lines = [
        "# ERA5 download status",
        "",
        f"Status: {report.status}",
        f"Log: {report.log_path.as_posix()}",
        "",
        "metric | value",
        "--- | ---:",
        f"attempt_rows | {len(report.rows)}",
        f"success_count | {report.success_count}",
        f"failed_count | {report.failed_count}",
        f"skipped_count | {report.skipped_count}",
        f"licence_blocked_count | {report.licence_blocked_count}",
        f"total_size_bytes | {report.total_size_bytes}",
        "",
    ]

    if report.missing_log:
        lines.extend(
            [
                "## Next action",
                "",
                "- Run a one-month ERA5 dry run, then a one-month real download after CDS credentials and licences are configured.",
            ]
        )
    elif report.ready_for_qc:
        lines.extend(
            [
                "## Next action",
                "",
                "- Run checksum audit and E00 data QC, then expand the download window only after the smoke-test files are verified.",
            ]
        )
        if report.failed_count:
            lines.extend(
                [
                    "",
                    "## Historical failed attempts",
                    "",
                    f"- {report.failed_count} earlier failed attempts remain in the log for provenance; successful local files are now available for QC.",
                ]
            )
    elif report.licence_blocked_count:
        datasets = sorted({_dataset_from_remote_id(row.remote_id) for row in report.rows if _is_licence_block(row)})
        lines.extend(["## Licence actions", "", "dataset | licence link", "--- | ---"])
        for dataset in datasets:
            lines.append(f"{dataset} | {ERA5_LICENCE_URLS.get(dataset, 'Check provider portal')}")
        lines.extend(
            [
                "",
                "## Next action",
                "",
                "- Accept the listed CDS dataset licences in the Copernicus Climate Data Store, then rerun the one-month download smoke test.",
            ]
        )
    elif report.failed_count:
        lines.extend(
            [
                "## Failed attempts",
                "",
                "remote_id | local_path | timestamp | message",
                "--- | --- | --- | ---",
            ]
        )
        for row in report.rows:
            if row.status == "failed":
                message = " ".join(row.message.split())[:240]
                lines.append(f"{row.remote_id} | {row.local_path} | {row.timestamp} | {message}")
    else:
        lines.extend(["## Next action", "", "- Review the download log before expanding the data request."])

    lines.extend(
        [
            "",
            "## Recent rows",
            "",
            "status | remote_id | local_path | size_bytes | timestamp",
            "--- | --- | --- | ---: | ---",
        ]
    )
    for row in report.rows[-10:]:
        lines.append(f"{row.status} | {row.remote_id} | {row.local_path} | {row.size_bytes} | {row.timestamp}")

    lines.extend(
        [
            "",
            "## 中文审阅说明",
            "",
            "本报告只解释 ERA5/ERA5-Land 下载日志，不代表数据质量检查或论文证据已经完成。若状态为 BLOCKED_BY_LICENSE，需要先在 CDS 接受对应数据集许可；若状态为 READY_FOR_QC，下一步仍需校验文件、记录校验和并运行数据质量检查。",
        ]
    )
    return "\n".join(lines) + "\n"


def run_download_status_command(log_path: str | Path, output_path: str | Path) -> tuple[DownloadStatusReport, Path]:
    report = read_download_log(log_path)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_download_status(report), encoding="utf-8")
    return report, output
