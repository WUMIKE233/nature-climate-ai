"""Convert GEE-exported ERA5 16-day composite GeoTIFF files to CSV for the Nature pipeline.

Parses 16-day composite bands in two formats:
  - New shared-grid:  T_001, D_001, S_001 ...  (var_doy, year from filename)
  - Old legacy:       Y2000_D001_T  etc.       (year_doy_var)

Each window = 16 days (last window 13-14 days). Center date = DoY_start + 7.
Matches MODIS MOD13Q1 composite schedule exactly.

Output CSV columns: date, pixel_id, 2m_temperature, total_precipitation,
soil_moisture, surface_net_solar_radiation, vapour_pressure_deficit
"""
import rasterio
import numpy as np
import re
import csv
import os
import argparse
from pathlib import Path
from datetime import date, timedelta

# New shared-grid: T_001, D_001, S_001, U_001, P_001, R_001, V_001
BAND_PATTERN_NEW = re.compile(r"^([TSDURPV])_(\d{3})$")
# Old legacy: Y2000_D001_T, Y2000_D001_D, ...
BAND_PATTERN_OLD = re.compile(r"^Y(\d{4})_D(\d{3})_([TSDURPV])$")

VAR_MAP = {
    "T": "2m_temperature",
    "D": "2m_dewpoint_temperature",
    "R": "surface_net_solar_radiation",
    "P": "total_precipitation",
    "V": "vapour_pressure_deficit",
    "S": "volumetric_soil_water_layer_1",
    "U": "volumetric_soil_water_layer_2",
}

YEAR_FROM_FILENAME = re.compile(r"(\d{4})")


def doy_to_date(year: int, doy: int) -> str:
    """Convert year + day-of-year to YYYY-MM-DD string.
    Center of 16-day window = DoY_start + 7."""
    center_doy = doy + 7
    d = date(year, 1, 1) + timedelta(days=center_doy - 1)
    return d.isoformat()


def parse_gee_bands(ds):
    """Return (year, windows_dict) where windows = {doy: {code: band_idx}}."""
    windows = {}
    file_year = None
    for i in range(ds.count):
        desc = ds.descriptions[i] or ""
        # Try new shared-grid format: T_001
        m = BAND_PATTERN_NEW.match(desc)
        if m:
            code = m.group(1)
            doy = int(m.group(2))
            if doy not in windows:
                windows[doy] = {}
            windows[doy][code] = i + 1
            continue
        # Try old legacy format: Y2000_D001_T
        m = BAND_PATTERN_OLD.match(desc)
        if m:
            yr = int(m.group(1))
            doy = int(m.group(2))
            code = m.group(3)
            if file_year is None:
                file_year = yr
            if doy not in windows:
                windows[doy] = {}
            windows[doy][code] = i + 1
    return file_year, windows


def extract_year_from_filename(tif_path):
    m = YEAR_FROM_FILENAME.search(Path(tif_path).stem)
    return int(m.group(1)) if m else None


def convert_all(tifs, output_path):
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    var_cols = [
        "2m_temperature", "total_precipitation",
        "soil_moisture", "surface_net_solar_radiation",
        "vapour_pressure_deficit",
    ]
    total_rows = 0
    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "pixel_id"] + var_cols)
        for tif in tifs:
            with rasterio.open(tif) as ds:
                h, w = ds.height, ds.width
                year, windows = parse_gee_bands(ds)
                if not windows:
                    print(f"  No bands in {tif.name}")
                    continue
                if year is None:
                    year = extract_year_from_filename(tif)
                if year is None:
                    year = 2000
                print(f"  {tif.name}: {year}, {len(windows)} composites, {w}x{h}")
                for doy in sorted(windows.keys()):
                    date_str = doy_to_date(year, doy)
                    bi = windows[doy]
                    t_data  = ds.read(bi["T"]).flatten() if "T" in bi else None
                    p_data  = ds.read(bi["P"]).flatten() if "P" in bi else None
                    r_data  = ds.read(bi["R"]).flatten() if "R" in bi else None
                    v_data  = ds.read(bi["V"]).flatten() if "V" in bi else None
                    s_data  = ds.read(bi["S"]).flatten() if "S" in bi else None
                    u_data  = ds.read(bi["U"]).flatten() if "U" in bi else None
                    n = h * w
                    for idx in range(n):
                        row, col = divmod(idx, w)
                        pid = f"p{row:05d}c{col:05d}"
                        t_val = float(t_data[idx]) if t_data is not None and not np.isnan(t_data[idx]) else ""
                        p_val = float(p_data[idx]) if p_data is not None and not np.isnan(p_data[idx]) else ""
                        r_val = float(r_data[idx]) if r_data is not None and not np.isnan(r_data[idx]) else ""
                        v_val = float(v_data[idx]) if v_data is not None and not np.isnan(v_data[idx]) else ""
                        sv = float(s_data[idx]) if s_data is not None and not np.isnan(s_data[idx]) else None
                        uv = float(u_data[idx]) if u_data is not None and not np.isnan(u_data[idx]) else None
                        sm_val = f"{(sv + uv) / 2:.6f}" if sv is not None and uv is not None else ""
                        writer.writerow([date_str, pid, t_val, p_val, sm_val, r_val, v_val])
                        total_rows += 1
    size_mb = os.path.getsize(out) / 1048576
    print(f"Done: {out} ({total_rows} rows, {size_mb:.1f} MB)")
    return total_rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", "-i", help="Input dir or single TIF")
    p.add_argument("--output", "-o", default="data/interim/era5_composite_climate.csv")
    p.add_argument("--dir", default="data/raw/era5_gee")
    args = p.parse_args()
    input_path = Path(args.input) if args.input else Path(args.dir)
    if input_path.is_file():
        tifs = [input_path]
    elif input_path.is_dir():
        tifs = sorted(input_path.glob("era5_16day_*.tif"))
    else:
        print(f"Nothing at {input_path}"); return
    if not tifs:
        print("No TIFs found"); return
    print(f"Converting {len(tifs)} ERA5 GeoTIFFs...")
    convert_all(tifs, args.output)

if __name__ == "__main__":
    main()
