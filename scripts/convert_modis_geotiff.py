"""
Convert GEE-exported MODIS GeoTIFFs (per year) to pipeline-ready CSV.

Each GeoTIFF has bands named: N_YYYYMMDD (NDVI), E_YYYYMMDD (EVI), Q_YYYYMMDD (qa_ok).
Output CSV has columns: date, pixel_id, evi, ndvi, quality

Usage:
  python scripts/convert_modis_geotiff.py --input data/raw/modis_gee/ --output data/raw/modis_observations.csv
"""
from __future__ import annotations

import argparse
import glob
import os
import re
from pathlib import Path
from typing import List, Tuple

import numpy as np

BandInfo = Tuple[str, str, int, int]  # (date_str, band_type, band_idx, actual_idx)


def parse_bands(filename: str | Path) -> List[BandInfo]:
    """Parse band names from a GeoTIFF using GDAL."""
    from osgeo import gdal
    ds = gdal.Open(str(filename))
    if ds is None:
        raise RuntimeError(f"Cannot open: {filename}")

    n_bands = ds.RasterCount
    metadata = ds.GetMetadata()

    bands = []
    for i in range(1, n_bands + 1):
        band = ds.GetRasterBand(i)
        desc = band.GetDescription() or f"Band_{i}"
        # Expected format: N_20240101 or E_20240101 or Q_20240101
        match = re.match(r'^([NEQ])_(\d{8})$', desc)
        if match:
            btype, date_str = match.groups()
            date_str = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
            bands.append((date_str, btype, i, i))
        else:
            # Try reading from metadata
            bands.append((f"unknown_{i}", desc[:1] if desc else "X", i, i))

    ds = None
    return bands


def convert_geotiff_to_csv(
    tiff_path: str | Path,
    output_dir: str | Path,
    chunk_size: int = 1000,
) -> List[Path]:
    """Convert a multi-band GeoTIFF to per-date CSV files."""
    from osgeo import gdal
    import csv

    ds = gdal.Open(str(tiff_path))
    if ds is None:
        raise RuntimeError(f"Cannot open: {tiff_path}")

    n_bands = ds.RasterCount
    n_cols = ds.RasterXSize
    n_rows = ds.RasterYSize
    geotransform = ds.GetGeoTransform()

    # Parse all bands
    bands_by_date: dict[str, dict[str, int]] = {}
    for i in range(1, n_bands + 1):
        band = ds.GetRasterBand(i)
        desc = band.GetDescription() or f"Band_{i}"
        match = re.match(r'^([NEQ])_(\d{8})$', desc)
        if match:
            btype, date_str_raw = match.groups()
            date_str = f"{date_str_raw[:4]}-{date_str_raw[4:6]}-{date_str_raw[6:8]}"
            if date_str not in bands_by_date:
                bands_by_date[date_str] = {}
            bands_by_date[date_str][btype] = i

    print(f"File: {Path(tiff_path).name}")
    print(f"  Size: {n_cols} x {n_rows}, {n_bands} bands")
    print(f"  Dates found: {len(bands_by_date)}")

    # For each unique date, extract N, E, Q triplet and write CSV
    output_paths = []
    lat_res = geotransform[5]
    lon_res = geotransform[1]
    origin_y = geotransform[3]

    for date_str, band_map in sorted(bands_by_date.items()):
        n_idx = band_map.get("N")
        e_idx = band_map.get("E")
        q_idx = band_map.get("Q")
        if n_idx is None or e_idx is None:
            continue

        ndvi_band = ds.GetRasterBand(n_idx)
        evi_band = ds.GetRasterBand(e_idx)
        qa_band = ds.GetRasterBand(q_idx) if q_idx else None

        # Process in chunks
        out_csv = Path(output_dir) / f"modis_{date_str.replace('-', '')}.csv"
        rows_written = 0

        with open(out_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "pixel_id", "evi", "ndvi", "quality"])

            for row_start in range(0, n_rows, chunk_size):
                n_rows_chunk = min(chunk_size, n_rows - row_start)
                ndvi_data = ndvi_band.ReadAsArray(0, row_start, n_cols, n_rows_chunk)
                evi_data = evi_band.ReadAsArray(0, row_start, n_cols, n_rows_chunk)
                qa_data = qa_band.ReadAsArray(0, row_start, n_cols, n_rows_chunk) if qa_band else np.ones_like(ndvi_data)

                # Mask nodata
                mask = (ndvi_data != ndvi_band.GetNoDataValue()) & (evi_data != evi_band.GetNoDataValue())
                if np.issubdtype(ndvi_data.dtype, np.floating):
                    mask = mask & ~np.isnan(ndvi_data) & ~np.isnan(evi_data)

                rows, cols = np.where(mask)
                for r, c in zip(rows, cols):
                    # Scale: MODIS values are int16 × 0.0001
                    ndvi_val = float(ndvi_data[r, c]) * 0.0001
                    evi_val = float(evi_data[r, c]) * 0.0001
                    qa_val = int(qa_data[r, c]) if qa_data is not None else 1
                    pixel_id = f"p{row_start + r:05d}c{c:05d}"
                    writer.writerow([date_str, pixel_id, evi_val, ndvi_val, qa_val])
                    rows_written += 1

        size_mb = out_csv.stat().st_size / 1024 / 1024
        print(f"  {date_str}: {rows_written} rows, {size_mb:.1f} MB -> {out_csv.name}")
        output_paths.append(out_csv)

    ds = None
    return output_paths


def merge_all_csv(input_dir: str | Path, output_csv: str | Path) -> Path:
    """Merge all per-date CSVs into one file."""
    import pandas as pd

    csv_files = sorted(glob.glob(str(Path(input_dir) / "modis_20*.csv")))
    if not csv_files:
        raise FileNotFoundError(f"No modis CSV files found in {input_dir}")

    print(f"Merging {len(csv_files)} CSV files...")
    frames = []
    for f in csv_files:
        try:
            df = pd.read_csv(f, dtype={"pixel_id": str, "quality": int})
            frames.append(df)
        except Exception as e:
            print(f"  Skipping {Path(f).name}: {e}")

    merged = pd.concat(frames, ignore_index=True)
    output = Path(output_csv)
    output.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(output, index=False)
    print(f"Merged: {len(merged)} rows -> {output}")
    return output


def main():
    p = argparse.ArgumentParser(description="Convert GEE GeoTIFF to pipeline CSV")
    p.add_argument("--input", "-i", required=True,
                   help="Directory containing GEE-exported GeoTIFFs")
    p.add_argument("--output", "-o", default="data/raw/modis_observations.csv",
                   help="Output CSV path")
    p.add_argument("--merge-only", action="store_true",
                   help="Only merge existing CSVs (skip GeoTIFF conversion)")
    args = p.parse_args()

    try:
        from osgeo import gdal
    except ImportError:
        print("GDAL not found. Install it:")
        print("  pip install gdal")
        print("  OR download from https://www.gisinternals.com/release.php")
        return

    input_dir = Path(args.input)

    if not args.merge_only:
        tiff_files = sorted(input_dir.glob("modis_obs_*.tif"))
        if not tiff_files:
            tiff_files = sorted(input_dir.glob("*.tif"))
        if not tiff_files:
            print(f"No GeoTIFF files found in {input_dir}")
            return

        print(f"Found {len(tiff_files)} GeoTIFF files")
        temp_dir = input_dir / "_csv_parts"
        temp_dir.mkdir(exist_ok=True)

        for tiff_path in tiff_files:
            out_paths = convert_geotiff_to_csv(tiff_path, temp_dir)
            if out_paths:
                print(f"  -> {len(out_paths)} CSVs created")

    # Merge all CSVs
    csv_dir = input_dir / "_csv_parts"
    if csv_dir.exists() and list(csv_dir.glob("modis_*.csv")):
        merge_all_csv(csv_dir, args.output)
    else:
        merge_all_csv(input_dir, args.output)

    print(f"\nDone. Output: {args.output}")


if __name__ == "__main__":
    main()