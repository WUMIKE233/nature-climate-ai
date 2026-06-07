"""Audit whether GEE MODIS and ERA5 GeoTIFF exports share one pixel grid."""
from __future__ import annotations

import argparse
import csv
import glob
from pathlib import Path

import rasterio


GRID_KEYS = ("crs", "width", "height", "transform")


def _dataset_row(label: str, path: Path) -> dict[str, str | int | float]:
    with rasterio.open(path) as src:
        transform = src.transform
        return {
            "dataset": label,
            "path": path.as_posix(),
            "crs": str(src.crs),
            "width": src.width,
            "height": src.height,
            "band_count": src.count,
            "transform": repr(transform),
            "pixel_width": float(transform.a),
            "pixel_height": float(transform.e),
            "left": float(src.bounds.left),
            "bottom": float(src.bounds.bottom),
            "right": float(src.bounds.right),
            "top": float(src.bounds.top),
        }


def _same_grid(left: dict[str, str | int | float], right: dict[str, str | int | float]) -> bool:
    return all(left[key] == right[key] for key in GRID_KEYS)


def _all_same_grid(rows: list[dict[str, str | int | float]]) -> bool:
    if len(rows) < 2:
        return False
    reference = rows[0]
    return all(_same_grid(reference, row) for row in rows[1:])


def _has_both_sources(rows: list[dict[str, str | int | float]]) -> bool:
    labels = {str(row["dataset"]) for row in rows}
    return {"MODIS_GEE", "ERA5_GEE"}.issubset(labels) or {"MODIS_GEE_REFERENCE", "ERA5_GEE_REFERENCE"}.issubset(labels)


def _audit_passes(rows: list[dict[str, str | int | float]]) -> bool:
    return _has_both_sources(rows) and _all_same_grid(rows)


def _collect_rows(label: str, explicit_path: str | None, pattern: str | None) -> list[dict[str, str | int | float]]:
    if pattern:
        paths = [Path(path) for path in sorted(glob.glob(pattern))]
    elif explicit_path:
        paths = [Path(explicit_path)]
    else:
        paths = []
    return [_dataset_row(label, path) for path in paths]


def render_report(rows: list[dict[str, str | int | float]], output_csv: Path) -> str:
    status = "PASS_SHARED_GRID" if _audit_passes(rows) else "FAIL_GRID_MISMATCH"
    lines = [
        "# GEE grid-alignment audit",
        "",
        f"Status: {status}",
        "",
        f"CSV: {output_csv.as_posix()}",
        "",
        "This audit checks whether MODIS and ERA5 GEE GeoTIFF exports use the same pixel grid. Identical `pixel_id` strings are only scientifically meaningful when CRS, shape and transform match.",
        "",
        "dataset | crs | width | height | pixel_width | pixel_height | bounds",
        "--- | --- | ---: | ---: | ---: | ---: | ---",
    ]
    for row in rows:
        bounds = f"{row['left']}, {row['bottom']}, {row['right']}, {row['top']}"
        lines.append(
            f"{row['dataset']} | {row['crs']} | {row['width']} | {row['height']} | {row['pixel_width']} | {row['pixel_height']} | {bounds}"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
        ]
    )
    if status == "PASS_SHARED_GRID":
        lines.append("All audited rasters share one grid, so row-column `pixel_id` joins are geometrically valid for these files.")
    else:
        lines.extend(
            [
                "The two reference rasters do not share one grid. Joining MODIS and ERA5 by row-column `pixel_id` is not a valid scientific spatial alignment for manuscript evidence.",
                "",
                "Required repair: re-export or reproject one data source so both products use the same CRS, transform, bounds and resolution before rebuilding anomalies, climate features, model data and validation artifacts.",
            ]
        )
    lines.extend(
        [
            "",
            "## 中文审阅说明",
            "",
            "本审计用于确认 MODIS 与 ERA5 的 GEE 导出是否处在同一个像元网格上。若 CRS、行列数或 transform 不一致，即使 `pixel_id` 字符串相同，也不能直接相连作为论文证据。",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--modis", default="data/raw/modis_gee/modis_obs_2001.tif")
    parser.add_argument("--era5", default="data/raw/era5_gee/era5_16day_2001.tif")
    parser.add_argument("--modis-glob", default=None, help="Optional glob for all MODIS GEE GeoTIFFs")
    parser.add_argument("--era5-glob", default=None, help="Optional glob for all ERA5 GEE GeoTIFFs")
    parser.add_argument("--csv", default="data/metadata/gee_grid_alignment_audit.csv")
    parser.add_argument("--report", default="data/metadata/gee_grid_alignment_audit.md")
    args = parser.parse_args()

    if args.modis_glob or args.era5_glob:
        rows = [
            *_collect_rows("MODIS_GEE", None, args.modis_glob),
            *_collect_rows("ERA5_GEE", None, args.era5_glob),
        ]
    else:
        rows = [
            *_collect_rows("MODIS_GEE_REFERENCE", args.modis, None),
            *_collect_rows("ERA5_GEE_REFERENCE", args.era5, None),
        ]
    if len(rows) < 2:
        raise SystemExit("Need at least one MODIS and one ERA5 raster to audit.")

    csv_path = Path(args.csv)
    report_path = Path(args.report)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    report_path.write_text(render_report(rows, csv_path), encoding="utf-8")
    print(f"Wrote grid-alignment CSV: {csv_path}")
    print(f"Wrote grid-alignment report: {report_path}")
    if not _audit_passes(rows):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
