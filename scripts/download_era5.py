"""ERA5 data download script — run from your own terminal, no timeout limits."""
import cdsapi
import os
import time
from pathlib import Path

OUTPUT_DIR = Path("data/raw/era5")
START_YEAR = int(os.environ.get("ERA5_START_YEAR", "2000"))
END_YEAR = int(os.environ.get("ERA5_END_YEAR", "2025"))
DRY_RUN = os.environ.get("ERA5_DRY_RUN", "0").strip().lower() in {"1", "true", "yes"}


def _parse_months(value: str | None) -> list[int] | None:
    if not value:
        return None
    return [int(part.strip()) for part in value.split(",") if part.strip()]


def _has_cds_credentials() -> bool:
    if os.environ.get("CDSAPI_URL") and os.environ.get("CDSAPI_KEY"):
        return True
    return (Path.home() / ".cdsapirc").exists()


SELECTED_MONTHS = _parse_months(os.environ.get("ERA5_MONTHS"))

ERA5_DATASET = "reanalysis-era5-single-levels"
ERA5_VARIABLES = [
    "2m_temperature", "2m_dewpoint_temperature",
    "surface_net_solar_radiation", "total_precipitation",
]
ERA5_LAND_DATASET = "reanalysis-era5-land"
ERA5_LAND_VARIABLES = [
    "volumetric_soil_water_layer_1", "volumetric_soil_water_layer_2",
]

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
client = None
if not DRY_RUN:
    if not _has_cds_credentials():
        print("CDS API credentials not found.")
        print("Set CDSAPI_URL/CDSAPI_KEY or create ~/.cdsapirc, then rerun this script.")
        raise SystemExit(2)
    if os.environ.get("CDSAPI_URL") and os.environ.get("CDSAPI_KEY"):
        client = cdsapi.Client(url=os.environ["CDSAPI_URL"], key=os.environ["CDSAPI_KEY"])
    else:
        client = cdsapi.Client()
months = SELECTED_MONTHS if SELECTED_MONTHS else list(range(1, 13))
total = len(range(START_YEAR, END_YEAR + 1)) * len(months) * 2
count = success = skipped = failed = 0

print(f"Downloading ERA5 {START_YEAR}-{END_YEAR}, {total} files to {OUTPUT_DIR.resolve()}")
if DRY_RUN:
    print("DRY RUN: no CDS requests will be submitted.")

for year in range(START_YEAR, END_YEAR + 1):
    for month in months:
        yr, mo = str(year), f"{month:02d}"
        for ds_name, ds_id, vars_ in [
            ("ERA5", ERA5_DATASET, ERA5_VARIABLES),
            ("ERA5-Land", ERA5_LAND_DATASET, ERA5_LAND_VARIABLES),
        ]:
            count += 1
            fname = f"era5_{'single' if 'Land' not in ds_name else 'land'}_{yr}{mo}.nc"
            fpath = OUTPUT_DIR / fname
            if fpath.exists():
                print(f"[{count}/{total}] SKIP {fname}")
                skipped += 1; continue
            print(f"[{count}/{total}] {ds_name} {yr}-{mo} ... ", end="", flush=True)
            if DRY_RUN:
                print(f"WOULD_DOWNLOAD {fname}")
                continue
            try:
                result = client.retrieve(ds_id, {
                    "product_type": ["reanalysis"], "variable": vars_,
                    "year": [yr], "month": [mo],
                    "day": [f"{d:02d}" for d in range(1, 32)],
                    "time": [f"{h:02d}:00" for h in range(24)],
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
