"""GEE MODIS GeoTIFF -> CSV converter using band-level vectorized reads.

Supports two band-naming conventions:
  - New shared-grid:  N_YYYYMMDD (NDVI),  E_YYYYMMDD (EVI),  Q_YYYYMMDD (qa_ok)
  - Old legacy:       0_2001_01_01_NDVI  etc.
"""
import rasterio, numpy as np, re, csv, os, argparse
from pathlib import Path

BAND_PATTERN_NEW = re.compile(r"^([NEQ])_(\d{4})(\d{2})(\d{2})$")
BAND_PATTERN_OLD = re.compile(r"^(\d+)_(\d{4})_(\d{2})_(\d{2})_(NDVI|EVI|qa_ok)$")


def parse_gee_bands(ds):
    dates = []
    seen = set()
    for i in range(ds.count):
        desc = ds.descriptions[i] or ""
        m = BAND_PATTERN_NEW.match(desc)
        if m and m.group(1) == "N":
            dstr = f"{m.group(2)}-{m.group(3)}-{m.group(4)}"
            if dstr not in seen:
                seen.add(dstr)
                dates.append((dstr, i + 1, i + 2, i + 3))
            continue
        m = BAND_PATTERN_OLD.match(desc)
        if m and m.group(5) == "NDVI":
            dstr = f"{m.group(2)}-{m.group(3)}-{m.group(4)}"
            if dstr not in seen:
                seen.add(dstr)
                dates.append((dstr, i + 1, i + 2, i + 3))
    return dates


def convert_all(tifs, output_path, scale=0.0001):
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    total_rows = 0
    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "pixel_id", "evi", "ndvi", "qa_ok"])
        for tif in tifs:
            with rasterio.open(tif) as ds:
                h, w = ds.height, ds.width
                dates = parse_gee_bands(ds)
                if not dates:
                    print(f"  No dates in {tif.name}")
                    continue
                print(f"  {tif.name}: {len(dates)} dates, {w}x{h}")
                for date_str, n_idx, e_idx, q_idx in dates:
                    ndvi = ds.read(n_idx).flatten() * scale
                    evi = ds.read(e_idx).flatten() * scale
                    qa = ds.read(q_idx).flatten()
                    for idx in range(h * w):
                        row, col = divmod(idx, w)
                        pid = f"p{row:05d}c{col:05d}"
                        writer.writerow([date_str, pid, f"{evi[idx]:.4f}", f"{ndvi[idx]:.4f}", f"{qa[idx]:.0f}"])
                        total_rows += 1
    size_mb = os.path.getsize(out) / 1048576
    print(f"Done: {out} ({total_rows} rows, {size_mb:.1f} MB)")
    return total_rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", "-i", help="Input dir or single TIF")
    p.add_argument("--output", "-o", default="data/raw/modis_observations.csv")
    p.add_argument("--dir", default="data/raw/modis_gee")
    args = p.parse_args()
    input_path = Path(args.input) if args.input else Path(args.dir)
    if input_path.is_file():
        tifs = [input_path]
    elif input_path.is_dir():
        tifs = sorted(input_path.glob("modis_obs_*.tif"))
    else:
        print(f"Nothing at {input_path}"); return
    if not tifs:
        print("No TIFs found"); return
    print(f"Converting {len(tifs)} GeoTIFFs...")
    convert_all(tifs, args.output)

if __name__ == "__main__":
    main()
