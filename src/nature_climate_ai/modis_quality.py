from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


DEFAULT_BAD_FLAG_COLUMNS = (
    "cloud",
    "adjacent_cloud",
    "mixed_cloud",
    "snow_ice",
    "shadow",
    "high_aerosol",
    "low_vi_usefulness",
    "bad_view_angle",
)


@dataclass(frozen=True)
class ModisQualityResult:
    filtered: pd.DataFrame
    qc: dict[str, int | str]


def validate_modis_observation_frame(
    frame: pd.DataFrame,
    date_col: str = "date",
    unit_col: str = "pixel_id",
    evi_col: str = "evi",
    ndvi_col: str = "ndvi",
) -> None:
    required = {date_col, unit_col, evi_col, ndvi_col}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"MODIS observation table is missing required columns: {sorted(missing)}")
    if frame.empty:
        raise ValueError("MODIS observation table is empty.")


def _bit_range(value: pd.Series, start: int, width: int) -> pd.Series:
    mask = (1 << width) - 1
    bits = (value.astype("int64").to_numpy() >> start) & mask
    return pd.Series(bits, index=value.index)


def mod13_vi_quality_ok(quality: pd.Series, max_vi_usefulness: int = 11) -> pd.Series:
    """Parse common MOD13/MYD13 VI Quality bits into a conservative keep mask.

    The expected integer field is the MODIS VI Quality layer. The logic keeps
    records with acceptable MODLAND QA, usable VI usefulness, low aerosol, no
    adjacent/mixed cloud, no snow/ice and no shadow. Exact product collection
    and bit interpretation must still be documented before manuscript use.
    """
    numeric = pd.to_numeric(quality, errors="coerce").fillna(-1).astype("int64")
    modland_qa = _bit_range(numeric, 0, 2)
    vi_usefulness = _bit_range(numeric, 2, 4)
    aerosol_quantity = _bit_range(numeric, 6, 2)
    adjacent_cloud = _bit_range(numeric, 8, 1)
    mixed_cloud = _bit_range(numeric, 10, 1)
    possible_snow_ice = _bit_range(numeric, 14, 1)
    possible_shadow = _bit_range(numeric, 15, 1)

    return (
        numeric.ge(0)
        & modland_qa.isin([0, 1])
        & vi_usefulness.le(max_vi_usefulness)
        & aerosol_quantity.le(1)
        & adjacent_cloud.eq(0)
        & mixed_cloud.eq(0)
        & possible_snow_ice.eq(0)
        & possible_shadow.eq(0)
    )


def compute_quality_filtered_modis(
    frame: pd.DataFrame,
    date_col: str = "date",
    unit_col: str = "pixel_id",
    evi_col: str = "evi",
    ndvi_col: str = "ndvi",
    vi_quality_col: str = "vi_quality",
    bad_flag_columns: tuple[str, ...] = DEFAULT_BAD_FLAG_COLUMNS,
    max_vi_usefulness: int = 11,
) -> ModisQualityResult:
    validate_modis_observation_frame(frame, date_col, unit_col, evi_col, ndvi_col)

    working = frame.copy()
    working[date_col] = pd.to_datetime(working[date_col], errors="coerce")
    working[evi_col] = pd.to_numeric(working[evi_col], errors="coerce")
    working[ndvi_col] = pd.to_numeric(working[ndvi_col], errors="coerce")
    valid_core = working.dropna(subset=[date_col, unit_col, evi_col, ndvi_col]).copy()

    if vi_quality_col in valid_core.columns:
        quality_ok = mod13_vi_quality_ok(valid_core[vi_quality_col], max_vi_usefulness=max_vi_usefulness)
        quality_source = vi_quality_col
    else:
        quality_ok, quality_source = _flag_or_fallback_quality(valid_core, bad_flag_columns)

    output = valid_core[quality_ok].copy()
    output["quality_ok"] = True
    filtered = output[[date_col, unit_col, evi_col, ndvi_col, "quality_ok"]].sort_values([unit_col, date_col])

    qc = {
        "input_rows": int(len(frame)),
        "valid_core_rows": int(len(valid_core)),
        "output_rows": int(len(filtered)),
        "dropped_rows": int(len(frame) - len(filtered)),
        "unique_units": int(filtered[unit_col].nunique()) if not filtered.empty else 0,
        "quality_source": quality_source,
        "date_min": filtered[date_col].min().date().isoformat() if not filtered.empty else "NA",
        "date_max": filtered[date_col].max().date().isoformat() if not filtered.empty else "NA",
    }
    return ModisQualityResult(filtered=filtered, qc=qc)



def _flag_or_fallback_quality(
    valid_core: pd.DataFrame, bad_flag_columns: tuple[str, ...]
) -> tuple[pd.Series, str]:
    quality_ok = pd.Series(True, index=valid_core.index)
    used_flags: list[str] = []
    for column in bad_flag_columns:
        if column in valid_core.columns:
            quality_ok &= ~valid_core[column].astype(bool)
            used_flags.append(column)
    # Accept qa_ok as a pre-computed binary good-quality flag (1 = good)
    if "qa_ok" in valid_core.columns:
        qa_series = pd.to_numeric(valid_core["qa_ok"], errors="coerce")
        quality_ok &= qa_series.fillna(0).eq(1)
        used_flags.append("qa_ok")
    quality_source = ",".join(used_flags) if used_flags else "none"
    return quality_ok, quality_source
def render_modis_quality_report(result: ModisQualityResult, input_path: str | Path) -> str:
    lines = [
        "# MODIS quality-filtering QC report",
        "",
        "Status: COMPLETE_FOR_INPUT_DATA",
        "",
        "This report summarizes quality filtering for the supplied MODIS observation table. It does not certify product collection, global coverage or provider-policy compliance.",
        "",
        f"- Input table: {Path(input_path).as_posix()}",
        "",
        "## Summary",
        "",
        "metric | value",
        "--- | ---",
    ]
    for key, value in result.qc.items():
        lines.append(f"{key} | {value}")
    lines.extend(
        [
            "",
            "## Manuscript-use warning",
            "",
            "Do not use this filtered table as manuscript evidence until the MODIS product collection, QA bit interpretation, spatial domain and temporal coverage have been independently reviewed.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_modis_quality_readiness_report(input_path: str | Path) -> str:
    return "\n".join(
        [
            "# MODIS quality-filtering readiness report",
            "",
            "Status: NOT_READY",
            "",
            f"Expected input table: {Path(input_path).as_posix()}",
            "",
            "The command did not generate `data/interim/modis_quality_filtered.csv` because the MODIS observation input table is missing.",
            "",
            "Required input columns:",
            "",
            "- `date`: MODIS composite date.",
            "- `pixel_id`: stable pixel, site or region identifier.",
            "- `evi`: EVI value.",
            "- `ndvi`: NDVI value.",
            "",
            "Quality inputs:",
            "",
            "- Preferred: `vi_quality`, the MODIS VI Quality integer layer.",
            "- Alternative: boolean bad-flag columns such as `cloud`, `snow_ice`, `shadow`, `high_aerosol`, `low_vi_usefulness`.",
        ]
    ) + "\n"


def run_modis_quality_command(
    input_path: str | Path,
    output_path: str | Path,
    report_path: str | Path,
    max_vi_usefulness: int = 11,
) -> tuple[bool, Path]:
    input_file = Path(input_path)
    output_file = Path(output_path)
    report_file = Path(report_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.parent.mkdir(parents=True, exist_ok=True)

    if not input_file.exists():
        report_file.write_text(render_modis_quality_readiness_report(input_file), encoding="utf-8")
        return False, report_file

    frame = pd.read_csv(input_file)
    result = compute_quality_filtered_modis(frame, max_vi_usefulness=max_vi_usefulness)
    result.filtered.to_csv(output_file, index=False)
    report_file.write_text(render_modis_quality_report(result, input_file), encoding="utf-8")
    return True, report_file
