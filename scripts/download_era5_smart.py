"""ERA5 smart download – 4 times daily single-levels only (with soil moisture), to E:/Nature_ERA5.

Key optimizations vs download_era5.py:
- 4 time steps/day instead of 24 → ~6x smaller
- ERA5 single-levels only: swvl1+swvl2 included → no ERA5-Land needed
- Output to E:/Nature_ERA5\ (E drive, 291 GB free)
- Resume: skips existing files
- Estimated ~180 GB total for 2000-2025 (26 years)
"""
import cdsapi
import os
import time
from pathlib import Path

OUTPUT_DIR = Path(os.environ.get("ERA5_OUTPUT_DIR", "E:/Nature_ERA5"))
START_YEAR = int(os.environ.get("ERA5_START_YEAR", "2000"))
END_YEAR = int(os.environ.get("ERA5_END_YEAR", "2025"))
DRY_RUN = os.environ.get("ERA5_DRY_RUN", "0").strip().lower() in {"1", "true", "yes"}

TIME_STEPS = ["00:00", "06:00", "12:00", "18:00"]

ERA5_DATASET = "reanalysis-era5-single-levels"
ERA5_VARIABLES = [
    "2m_temperature",
    "2m_dewpoint_temperature",
    "surface_net_solar_radiation",
    "total_precipitation",
    "volumetric_soil_water_layer_1",
    "volumetric_soil_water_layer_2",
]


def _parse_months(value):
    if not value:
        return None
    return [int(part.strip()) for part in value.split(",") if part.strip()]


SELECTED_MONTHS = _parse_months(os.environ.get("ERA5_MONTHS"))


def _has_cds_credentials():
    if os.environ.get("CDSAPI_URL") and os.environ.get("CDSAPI_KEY"):
        return True
    return (Path.home() / ".cdsapirc").exists()


OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

if not DRY_RUN:
    if not _has_cds_credentials():
        print("CDS API credentials not found.")
        raise SystemExit(2)
    client = cdsapi.Client(
        url=os.environ.get("CDSAPI_URL", None),
        key=os.environ.get("CDSAPI_KEY", None),
    )
else:
    client = None

months = SELECTED_MONTHS if SELECTED_MONTHS else list(range(1, 13))
total = len(range(START_YEAR, END_YEAR + 1)) * len(months)
success = skipped = failed = 0
est_total_gb = total * 0.55

print(f"ERA5 SMART: {START_YEAR}-{END_YEAR}, {total} files")
print(f"  Time steps: {len(TIME_STEPS)}/day, Variables: {len(ERA5_VARIABLES)}")
print(f"  Output: {OUTPUT_DIR.resolve()}  Est total: ~{est_total_gb:.0f} GB")
if DRY_RUN:
    print("  DRY RUN: no requests submitted.")

for year in range(START_YEAR, END_YEAR + 1):
    for month in months:
        yr, mo = str(year), f"{month:02d}"
        fname = f"era5_single_{yr}{mo}.nc"
        fpath = OUTPUT_DIR / fname

        if fpath.exists():
            print(f"SKIP {fname} (exists)")
            skipped += 1
            continue

        print(f"REQ {yr}-{mo} ... ", end="", flush=True)

        if DRY_RUN:
            print(f"WOULD_DOWNLOAD -> {fname}")
            continue

        try:
            result = client.retrieve(ERA5_DATASET, {
                "product_type": ["reanalysis"],
                "variable": ERA5_VARIABLES,
                "year": [yr],
                "month": [mo],
                "day": [f"{d:02d}" for d in range(1, 32)],
                "time": TIME_STEPS,
                "data_format": "netcdf",
            })
            result.download(str(fpath))
            mb = fpath.stat().st_size / (1024 * 1024)
            print(f"OK ({mb:.0f} MB)")
            success += 1
        except Exception as e:
            print(f"FAIL: {e}")
            failed += 1
        time.sleep(0.3)

print(f"\nDone: {success} ok, {skipped} skipped, {failed} failed")

