from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


MODIS_HDF_PATTERN = re.compile(
    r"^(?P<product>MOD13Q1|MYD13Q1)\.A(?P<year>\d{4})(?P<doy>\d{3})\.(?P<tile>h\d{2}v\d{2})\.(?P<collection>\d{3})\.(?P<production>\d+)\.hdf$"
)
DEFAULT_PHASE1_TILES = ("h31v11", "h29v12", "h32v10", "h32v12")
DEFAULT_PRODUCTS = ("MOD13Q1", "MYD13Q1")


@dataclass(frozen=True)
class ModisRawInventoryResult:
    rows: pd.DataFrame
    output_csv: Path
    output_report: Path
    expected_granules: int
    found_expected_granules: int
    suspicious_files: int

    @property
    def status(self) -> str:
        if self.found_expected_granules == 0:
            return "NOT_READY"
        if self.suspicious_files:
            return "NEEDS_REVIEW"
        if self.found_expected_granules < self.expected_granules:
            return "PARTIAL_DOWNLOAD"
        return "READY_FOR_RAW_MODIS_PREPROCESSING"


def _file_signature(path: Path) -> str:
    with path.open("rb") as handle:
        prefix = handle.read(32).lstrip()
    if prefix.lower().startswith(b"<!doctype") or prefix.lower().startswith(b"<html"):
        return "HTML"
    if prefix.startswith(b"\x0e\x03\x13\x01") or prefix.startswith(b"\x89HDF"):
        return "HDF_LIKE"
    return prefix[:8].hex().upper()


def scan_modis_raw_files(root: str | Path) -> pd.DataFrame:
    rows: list[dict[str, str | int]] = []
    for path in sorted(Path(root).rglob("*.hdf")):
        match = MODIS_HDF_PATTERN.match(path.name)
        signature = _file_signature(path)
        row: dict[str, str | int] = {
            "path": path.as_posix(),
            "file_name": path.name,
            "bytes": path.stat().st_size,
            "signature": signature,
            "parse_status": "PARSED" if match else "UNPARSED_FILENAME",
            "product": "",
            "year": "",
            "doy": "",
            "tile": "",
            "collection": "",
            "issue": "",
        }
        if match:
            row.update(match.groupdict())
            if signature == "HTML":
                row["issue"] = "Downloaded HTML page instead of HDF data"
            elif path.stat().st_size < 1000:
                row["issue"] = "Suspiciously small HDF file"
        else:
            row["issue"] = "File name does not match expected MOD13Q1/MYD13Q1 pattern"
        rows.append(row)
    return pd.DataFrame(rows)


def expected_phase1_granules(
    start_year: int,
    end_year: int,
    products: tuple[str, ...] = DEFAULT_PRODUCTS,
    tiles: tuple[str, ...] = DEFAULT_PHASE1_TILES,
) -> int:
    years = end_year - start_year + 1
    doy_slots = len(range(1, 367, 16))
    return years * doy_slots * len(products) * len(tiles)


def run_modis_raw_inventory_command(
    input_dir: str | Path,
    output_csv: str | Path,
    output_report: str | Path,
    start_year: int = 2001,
    end_year: int = 2025,
) -> ModisRawInventoryResult:
    frame = scan_modis_raw_files(input_dir)
    csv_path = Path(output_csv)
    report_path = Path(output_report)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(csv_path, index=False)

    expected = expected_phase1_granules(start_year, end_year)
    suspicious = 0 if frame.empty else int((frame["issue"].astype(str) != "").sum())
    found_expected = 0
    if not frame.empty:
        valid = frame[
            (frame["parse_status"] == "PARSED")
            & (frame["product"].isin(DEFAULT_PRODUCTS))
            & (frame["tile"].isin(DEFAULT_PHASE1_TILES))
            & (pd.to_numeric(frame["year"], errors="coerce").between(start_year, end_year))
            & (frame["collection"] == "061")
        ]
        found_expected = int(len(valid))

    result = ModisRawInventoryResult(
        rows=frame,
        output_csv=csv_path,
        output_report=report_path,
        expected_granules=expected,
        found_expected_granules=found_expected,
        suspicious_files=suspicious,
    )
    report_path.write_text(render_modis_raw_inventory_report(result, input_dir, start_year, end_year), encoding="utf-8")
    return result


def render_modis_raw_inventory_report(
    result: ModisRawInventoryResult,
    input_dir: str | Path,
    start_year: int,
    end_year: int,
) -> str:
    lines = [
        "# MODIS raw inventory",
        "",
        f"Status: {result.status}",
        "",
        f"Input directory: {Path(input_dir).as_posix()}",
        f"CSV: {result.output_csv.as_posix()}",
        "",
        "metric | value",
        "--- | ---:",
        f"raw_hdf_files | {len(result.rows)}",
        f"phase1_expected_granules | {result.expected_granules}",
        f"phase1_found_expected_granules | {result.found_expected_granules}",
        f"suspicious_files | {result.suspicious_files}",
        f"year_start | {start_year}",
        f"year_end | {end_year}",
        "",
    ]
    if not result.rows.empty:
        grouped = result.rows.groupby(["product", "year", "tile"], dropna=False).size().reset_index(name="count")
        lines.extend(["## Coverage snapshot", "", "product | year | tile | count", "--- | --- | --- | ---:"])
        for _, row in grouped.head(50).iterrows():
            lines.append(f"{row['product']} | {row['year']} | {row['tile']} | {row['count']}")
        if len(grouped) > 50:
            lines.append(f"... {len(grouped) - 50} more rows")
        lines.append("")
    lines.extend(
        [
            "## Manuscript-use warning",
            "",
            "This inventory only counts local raw MODIS HDF files and basic filename/signature checks. It does not decode science datasets, apply quality flags, or certify vegetation-stress evidence.",
            "",
            "## 中文审阅说明",
            "",
            "本清单只统计本地 MODIS HDF 原始文件，并做基础文件名和文件头检查。它尚未解码 NDVI/EVI 科学数据集，也没有应用质量位筛选，不能作为植被胁迫事件证据。",
        ]
    )
    return "\n".join(lines) + "\n"
