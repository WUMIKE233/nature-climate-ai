from __future__ import annotations

import csv
import io
import struct
import zipfile
import zlib
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


REQUIRED_DAILY_VARIABLES = ("GPP_NT_VUT_REF", "LE_F_MDS", "TA_F", "SW_IN_F", "VPD_F")
LOCAL_FILE_HEADER_SIGNATURE = b"PK\x03\x04"


@dataclass(frozen=True)
class FluxnetRawAuditResult:
    rows: pd.DataFrame
    total_archives: int
    archives_with_daily_fluxmet: int
    archives_with_required_variables: int
    output_csv: Path
    output_report: Path

    @property
    def status(self) -> str:
        if self.total_archives == 0:
            return "NOT_READY"
        if self.archives_with_required_variables == self.total_archives:
            return "READY_FOR_ANOMALY_PREPROCESSING"
        return "PARTIAL_VARIABLE_COVERAGE"


def _site_id_from_name(path: Path) -> str:
    parts = path.name.split("_")
    if len(parts) >= 2:
        return parts[1]
    return path.stem


def _daily_fluxmet_member(members: list[zipfile.ZipInfo]) -> zipfile.ZipInfo | None:
    candidates = [
        member
        for member in members
        if "_FLUXMET_DD_" in member.filename and member.filename.lower().endswith(".csv")
    ]
    if not candidates:
        return None
    return sorted(candidates, key=lambda member: member.filename)[0]


def _csv_header_from_zip(archive: zipfile.ZipFile, member: zipfile.ZipInfo) -> list[str]:
    with archive.open(member, "r") as handle:
        text = handle.readline().decode("utf-8-sig", errors="replace")
    return next(csv.reader([text]))


def _decompress_local_member(payload: bytes, compression_method: int) -> bytes:
    if compression_method == 0:
        return payload
    if compression_method == 8:
        return zlib.decompress(payload, -zlib.MAX_WBITS)
    raise ValueError(f"Unsupported ZIP compression method: {compression_method}")


def read_local_zip_member(path: Path, member_name: str) -> bytes:
    with path.open("rb") as handle:
        while True:
            signature = handle.read(4)
            if not signature:
                raise FileNotFoundError(member_name)
            if signature != LOCAL_FILE_HEADER_SIGNATURE:
                raise FileNotFoundError(member_name)

            header = handle.read(26)
            if len(header) < 26:
                raise FileNotFoundError(member_name)
            (
                _version,
                flags,
                compression_method,
                _mod_time,
                _mod_date,
                _crc32,
                compressed_size,
                _uncompressed_size,
                name_length,
                extra_length,
            ) = struct.unpack("<HHHHHIIIHH", header)
            name = handle.read(name_length).decode("utf-8", errors="replace")
            handle.seek(extra_length, io.SEEK_CUR)

            if flags & 0x08:
                raise ValueError(f"Unsupported ZIP data-descriptor member: {name}")

            payload = handle.read(compressed_size)
            if len(payload) < compressed_size:
                raise EOFError(f"Truncated ZIP member: {name}")
            if name == member_name:
                return _decompress_local_member(payload, compression_method)


def _daily_header_from_local_zip(path: Path) -> tuple[str, int, list[str]] | None:
    with path.open("rb") as handle:
        while True:
            signature = handle.read(4)
            if not signature:
                return None
            if signature != LOCAL_FILE_HEADER_SIGNATURE:
                return None

            header = handle.read(26)
            if len(header) < 26:
                return None
            (
                _version,
                flags,
                compression_method,
                _mod_time,
                _mod_date,
                _crc32,
                compressed_size,
                uncompressed_size,
                name_length,
                extra_length,
            ) = struct.unpack("<HHHHHIIIHH", header)
            name = handle.read(name_length).decode("utf-8", errors="replace")
            handle.seek(extra_length, io.SEEK_CUR)

            if flags & 0x08:
                return None

            if "_FLUXMET_DD_" not in name or not name.lower().endswith(".csv"):
                handle.seek(compressed_size, io.SEEK_CUR)
                continue

            payload = handle.read(compressed_size)
            if len(payload) < compressed_size:
                return None
            decoded = _decompress_local_member(payload, compression_method)
            first_line = decoded.splitlines()[0].decode("utf-8-sig", errors="replace")
            return name, uncompressed_size, next(csv.reader([first_line]))


def _bad_zip_issue(path: Path, exc: Exception) -> tuple[str, str]:
    with path.open("rb") as handle:
        prefix = handle.read(32)
    stripped = prefix.lstrip()
    if stripped.lower().startswith(b"<!doctype") or stripped.lower().startswith(b"<html"):
        return "NOT_ZIP_PAYLOAD", "Downloaded file appears to be an HTML page, not a ZIP archive"
    if prefix.startswith(LOCAL_FILE_HEADER_SIGNATURE):
        return "TRUNCATED_NO_DAILY_MEMBER", "ZIP is truncated before a readable FLUXMET_DD member"
    return "BAD_ZIP", str(exc)


def audit_fluxnet_archive(path: Path, required_variables: tuple[str, ...] = REQUIRED_DAILY_VARIABLES) -> dict[str, str | int]:
    row: dict[str, str | int] = {
        "archive": path.as_posix(),
        "site_id": _site_id_from_name(path),
        "bytes": path.stat().st_size,
        "zip_status": "UNTESTED",
        "daily_member": "",
        "daily_member_bytes": 0,
        "required_variables_present": "",
        "missing_required_variables": ",".join(required_variables),
        "issue": "",
    }
    try:
        with zipfile.ZipFile(path) as archive:
            bad_member = archive.testzip()
            if bad_member:
                row["zip_status"] = "BAD_ZIP"
                row["issue"] = f"First corrupt member: {bad_member}"
                return row

            row["zip_status"] = "OK"
            member = _daily_fluxmet_member(archive.infolist())
            if member is None:
                row["issue"] = "No FLUXMET_DD CSV member found"
                return row

            header = set(_csv_header_from_zip(archive, member))
            present = tuple(variable for variable in required_variables if variable in header)
            missing = tuple(variable for variable in required_variables if variable not in header)
            row["daily_member"] = member.filename
            row["daily_member_bytes"] = member.file_size
            row["required_variables_present"] = ",".join(present)
            row["missing_required_variables"] = ",".join(missing)
            row["issue"] = "" if not missing else "Missing required daily variables"
            return row
    except zipfile.BadZipFile as exc:
        try:
            daily = _daily_header_from_local_zip(path)
        except Exception as local_exc:
            row["zip_status"] = "BAD_ZIP"
            row["issue"] = f"{exc}; local header fallback failed: {local_exc}"
            return row
        if daily is None:
            status, issue = _bad_zip_issue(path, exc)
            row["zip_status"] = status
            row["issue"] = issue
            return row

        member_name, member_size, header = daily
        header_set = set(header)
        present = tuple(variable for variable in required_variables if variable in header_set)
        missing = tuple(variable for variable in required_variables if variable not in header_set)
        row["zip_status"] = "TRUNCATED_BUT_DAILY_READABLE"
        row["daily_member"] = member_name
        row["daily_member_bytes"] = member_size
        row["required_variables_present"] = ",".join(present)
        row["missing_required_variables"] = ",".join(missing)
        row["issue"] = "" if not missing else "Missing required daily variables"
        return row


def audit_fluxnet_raw_archives(
    input_dir: str | Path,
    output_csv: str | Path,
    output_report: str | Path,
    required_variables: tuple[str, ...] = REQUIRED_DAILY_VARIABLES,
) -> FluxnetRawAuditResult:
    root = Path(input_dir)
    archives = sorted(root.glob("*.zip"))
    rows = [audit_fluxnet_archive(path, required_variables) for path in archives]
    frame = pd.DataFrame(rows)

    csv_path = Path(output_csv)
    report_path = Path(output_report)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(csv_path, index=False)

    if frame.empty:
        daily_count = 0
        required_count = 0
    else:
        daily_count = int((frame["daily_member"].astype(str) != "").sum())
        required_count = int((frame["missing_required_variables"].astype(str) == "").sum())

    result = FluxnetRawAuditResult(
        rows=frame,
        total_archives=len(archives),
        archives_with_daily_fluxmet=daily_count,
        archives_with_required_variables=required_count,
        output_csv=csv_path,
        output_report=report_path,
    )
    report_path.write_text(render_fluxnet_raw_audit_report(result, input_dir, required_variables), encoding="utf-8")
    return result


def render_fluxnet_raw_audit_report(
    result: FluxnetRawAuditResult,
    input_dir: str | Path,
    required_variables: tuple[str, ...] = REQUIRED_DAILY_VARIABLES,
) -> str:
    lines = [
        "# FLUXNET raw archive audit",
        "",
        f"Status: {result.status}",
        "",
        f"Input directory: {Path(input_dir).as_posix()}",
        f"CSV: {result.output_csv.as_posix()}",
        "",
        "metric | value",
        "--- | ---:",
        f"total_archives | {result.total_archives}",
        f"archives_with_daily_fluxmet | {result.archives_with_daily_fluxmet}",
        f"archives_with_required_variables | {result.archives_with_required_variables}",
        "",
        "Required daily variables:",
        "",
        *[f"- `{variable}`" for variable in required_variables],
        "",
    ]
    if not result.rows.empty:
        problematic = result.rows[
            (~result.rows["zip_status"].isin(("OK", "TRUNCATED_BUT_DAILY_READABLE")))
            | (result.rows["daily_member"].astype(str) == "")
            | (result.rows["missing_required_variables"].astype(str) != "")
        ]
        if not problematic.empty:
            lines.extend(["## Archives needing review", "", "site_id | zip_status | issue | missing_required_variables", "--- | --- | --- | ---"])
            for _, row in problematic.head(30).iterrows():
                lines.append(
                    f"{row['site_id']} | {row['zip_status']} | {row['issue']} | {row['missing_required_variables']}"
                )
            if len(problematic) > 30:
                lines.append(f"... {len(problematic) - 30} more rows")
            lines.append("")
    lines.extend(
        [
            "## Manuscript-use warning",
            "",
            "This audit only verifies local archive readability and daily FLUXMET variable presence. It does not compute flux anomalies, validate site representativeness, or justify manuscript mechanism claims.",
            "",
            "## 中文审阅说明",
            "",
            "本审计只检查 FLUXNET 站点 zip 是否可读，以及日尺度 FLUXMET 文件是否包含 GPP、LE、TA、SW_IN、VPD 等变量。它还没有生成通量异常，也不能作为论文生态验证结果。",
        ]
    )
    return "\n".join(lines) + "\n"
