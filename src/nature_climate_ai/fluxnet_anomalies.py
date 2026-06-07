from __future__ import annotations

import io
import zipfile
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .fluxnet_raw import read_local_zip_member


FLUXNET_VALUE_COLUMNS = ("GPP_NT_VUT_REF", "LE_F_MDS", "TA_F", "SW_IN_F", "VPD_F")
OUTPUT_COLUMN_MAP = {
    "GPP_NT_VUT_REF": "gpp",
    "LE_F_MDS": "le",
    "TA_F": "ta",
    "SW_IN_F": "sw_in",
    "VPD_F": "vpd",
}


@dataclass(frozen=True)
class FluxnetAnomalyPreprocessResult:
    anomalies: pd.DataFrame
    qc: dict[str, int | str]


def _read_daily_member(archive_path: Path, member_name: str, zip_status: str) -> pd.DataFrame:
    columns = ["TIMESTAMP", *FLUXNET_VALUE_COLUMNS]
    if zip_status == "OK":
        with zipfile.ZipFile(archive_path) as archive:
            with archive.open(member_name) as handle:
                return pd.read_csv(handle, usecols=columns)

    payload = read_local_zip_member(archive_path, member_name)
    return pd.read_csv(io.BytesIO(payload), usecols=columns)


def _site_anomalies(frame: pd.DataFrame, site_id: str, min_climatology_samples: int) -> pd.DataFrame:
    working = frame.copy()
    working["site_id"] = site_id
    working["date"] = pd.to_datetime(working["TIMESTAMP"].astype(str), format="%Y%m%d", errors="coerce")
    for column in FLUXNET_VALUE_COLUMNS:
        working[column] = pd.to_numeric(working[column], errors="coerce")
        working.loc[working[column] <= -9990, column] = pd.NA
    working = working.dropna(subset=["date"]).copy()
    working["day_of_year"] = working["date"].dt.dayofyear

    grouped = working.groupby(["site_id", "day_of_year"], sort=False)
    output = working[["site_id", "date", "day_of_year"]].copy()
    for source, prefix in OUTPUT_COLUMN_MAP.items():
        output[prefix] = working[source]
        output[f"{prefix}_climatology"] = grouped[source].transform("mean")
        output[f"{prefix}_climatology_samples"] = grouped[source].transform("count")
        output[f"{prefix}_anomaly"] = output[prefix] - output[f"{prefix}_climatology"]

    sample_columns = [f"{prefix}_climatology_samples" for prefix in OUTPUT_COLUMN_MAP.values()]
    output = output[(output[sample_columns] >= min_climatology_samples).any(axis=1)].copy()
    return output.sort_values(["site_id", "date"])


def preprocess_fluxnet_anomalies(
    audit_csv: str | Path,
    min_climatology_samples: int = 2,
) -> FluxnetAnomalyPreprocessResult:
    audit = pd.read_csv(audit_csv)
    usable = audit[
        (audit["daily_member"].astype(str) != "")
        & (audit["missing_required_variables"].fillna("").astype(str) == "")
        & (audit["zip_status"].isin(["OK", "TRUNCATED_BUT_DAILY_READABLE"]))
    ].copy()

    frames: list[pd.DataFrame] = []
    failed_sites = 0
    for _, row in usable.iterrows():
        try:
            daily = _read_daily_member(Path(row["archive"]), row["daily_member"], row["zip_status"])
            frames.append(_site_anomalies(daily, row["site_id"], min_climatology_samples))
        except Exception:
            failed_sites += 1

    anomalies = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    qc = {
        "audit_rows": int(len(audit)),
        "usable_archive_rows": int(len(usable)),
        "sites_processed": int(anomalies["site_id"].nunique()) if not anomalies.empty else 0,
        "failed_sites": int(failed_sites),
        "output_rows": int(len(anomalies)),
        "min_climatology_samples": int(min_climatology_samples),
        "date_min": anomalies["date"].min().date().isoformat() if not anomalies.empty else "NA",
        "date_max": anomalies["date"].max().date().isoformat() if not anomalies.empty else "NA",
    }
    return FluxnetAnomalyPreprocessResult(anomalies=anomalies, qc=qc)


def render_fluxnet_anomaly_report(result: FluxnetAnomalyPreprocessResult, audit_csv: str | Path) -> str:
    status = "COMPLETE_FOR_READABLE_ARCHIVES" if not result.anomalies.empty else "NOT_READY"
    lines = [
        "# FLUXNET anomaly preprocessing report",
        "",
        f"Status: {status}",
        "",
        f"Raw archive audit: {Path(audit_csv).as_posix()}",
        "",
        "metric | value",
        "--- | ---",
    ]
    for key, value in result.qc.items():
        lines.append(f"{key} | {value}")
    lines.extend(
        [
            "",
            "## Method note",
            "",
            "Daily FLUXMET variables were converted to site-level day-of-year anomalies using only archives whose daily FLUXMET member and required variables were readable. Missing FLUXNET values encoded as -9999 were treated as missing.",
            "",
            "## Manuscript-use warning",
            "",
            "This is a pilot preprocessing artifact for readable local FLUXNET archives. It does not prove ecosystem validation and does not include model-predicted stress windows.",
            "",
            "## 中文审阅说明",
            "",
            "本报告把可读 FLUXNET 日尺度 FLUXMET 文件转换为站点逐日异常。它只覆盖当前可读站点，不代表所有 111 个站点都可用，也不能直接作为论文生态验证结论。",
        ]
    )
    return "\n".join(lines) + "\n"


def run_fluxnet_anomaly_preprocess_command(
    audit_csv: str | Path,
    output_path: str | Path,
    report_path: str | Path,
    min_climatology_samples: int = 2,
) -> tuple[bool, Path]:
    output = Path(output_path)
    report = Path(report_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)

    if not Path(audit_csv).exists():
        report.write_text(
            "# FLUXNET anomaly preprocessing readiness report\n\nStatus: NOT_READY\n\nExpected raw archive audit is missing.\n",
            encoding="utf-8",
        )
        return False, report

    result = preprocess_fluxnet_anomalies(audit_csv, min_climatology_samples=min_climatology_samples)
    if not result.anomalies.empty:
        result.anomalies.to_csv(output, index=False)
    report.write_text(render_fluxnet_anomaly_report(result, audit_csv), encoding="utf-8")
    return not result.anomalies.empty, report
