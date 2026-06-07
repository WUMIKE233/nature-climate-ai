"""
GEE MODIS MOD13Q1/MYD13Q1 export for Nature climate/ecology project.

Exports quality-filtered NDVI/EVI at 0.25-degree resolution as GeoTIFF
(one file per year), plus a local converter to CSV for the pipeline.

Requirements:
  1. Google Earth Engine account: https://earthengine.google.com/signup/
  2. First run opens a browser for GEE authentication.
  3. Google Drive for export destination (files appear there).

Usage:
  python scripts/export_modis_gee.py --auth          # first time only
  python scripts/export_modis_gee.py --year 2001      # test one year
  python scripts/export_modis_gee.py --start 2001 --end 2025  # full run
"""
from __future__ import annotations

import argparse
import os
import sys
import time

import ee

# ── Quality filter ─────────────────────────────────────────────────
# Same logic as modis_quality.py:mod13_vi_quality_ok
# Bits: 0-1 MODLAND_QA, 2-5 VI_usefulness, 6-7 aerosol,
#        8 adj_cloud, 10 mixed_cloud, 14 snow_ice, 15 shadow


def add_quality_mask(image: ee.Image) -> ee.Image:
    """Add qa_ok band (0/1) using SummaryQA bitfield from MOD13Q1/MYD13Q1."""
    qa = image.select("SummaryQA")
    modland = qa.bitwiseAnd(3)
    vi_use = qa.rightShift(2).bitwiseAnd(15)
    aerosol = qa.rightShift(6).bitwiseAnd(3)
    adj_cloud = qa.rightShift(8).bitwiseAnd(1)
    mixed_cloud = qa.rightShift(10).bitwiseAnd(1)
    snow_ice = qa.rightShift(14).bitwiseAnd(1)
    shadow = qa.rightShift(15).bitwiseAnd(1)

    ok = (modland.lte(1)
          .And(vi_use.lte(11))
          .And(aerosol.lte(1))
          .And(adj_cloud.eq(0))
          .And(mixed_cloud.eq(0))
          .And(snow_ice.eq(0))
          .And(shadow.eq(0)))
    return image.addBands(ok.rename("qa_ok").uint8())


def export_year_geotiff(year: int, drive_folder: str, scale_deg: float = 0.25) -> str | None:
    """Export one year of MODIS as a merged quality-filtered GeoTIFF.

    Returns task ID string or None if nothing to export.
    """
    print(f"\n--- Year {year} ---")

    # Load and filter MOD13Q1 + MYD13Q1
    mod = (ee.ImageCollection("MODIS/061/MOD13Q1")
           .filterDate(f"{year}-01-01", f"{year+1}-01-01")
           .map(add_quality_mask)
           .select(["NDVI", "EVI", "qa_ok"]))
    myd = (ee.ImageCollection("MODIS/061/MYD13Q1")
           .filterDate(f"{year}-01-01", f"{year+1}-01-01")
           .map(add_quality_mask)
           .select(["NDVI", "EVI", "qa_ok"]))

    combined = mod.merge(myd)
    count = combined.size().getInfo()
    print(f"  Images: {count}")

    if count == 0:
        print(f"  No images for {year}, skipping.")
        return None

    # Convert to bands: one band per image-date
    # Band names: NDVI_YYYYMMDD, EVI_YYYYMMDD, qa_YYYYMMDD
    img_list = combined.toList(count)

    def to_bands(i):
        i = ee.Number(i)
        img = ee.Image(img_list.get(i))
        date_str = ee.Date(img.get("system:time_start")).format("YYYYMMdd")
        ndvi = img.select("NDVI").rename(ee.String("N_").cat(date_str))
        evi = img.select("EVI").rename(ee.String("E_").cat(date_str))
        qa = img.select("qa_ok").rename(ee.String("Q_").cat(date_str))
        return ndvi.addBands(evi).addBands(qa)

    stacked = ee.ImageCollection(ee.List.sequence(0, count - 1).map(to_bands)).toBands()

    # Reproject to target resolution (0.25 deg ~= 27780m at equator)
    scale_m = int(scale_deg * 111320)
    reprojected = stacked.reproject(crs="EPSG:4326", scale=scale_m)

    # Export as GeoTIFF to Google Drive
    task_name = f"modis_{year}"
    task = ee.batch.Export.image.toDrive(
        image=reprojected.toFloat(),
        description=task_name,
        folder=drive_folder,
        fileNamePrefix=f"modis_obs_{year}",
        scale=scale_m,
        crs="EPSG:4326",
        maxPixels=1e10,
        fileFormat="GeoTIFF",
    )
    task.start()
    print(f"  Task submitted: {task_name}")
    print(f"  Monitor: https://code.earthengine.google.com/tasks")
    return task_name


def main():
    p = argparse.ArgumentParser(description="Export MODIS data via GEE")
    p.add_argument("--auth", action="store_true", help="Authenticate with GEE")
    p.add_argument("--year", type=int, help="Export a single year")
    p.add_argument("--start", type=int, default=2001, help="Start year")
    p.add_argument("--end", type=int, default=2025, help="End year")
    p.add_argument("--drive-folder", default="Nature_MODIS_Export",
                   help="Google Drive folder name")
    p.add_argument("--scale", type=float, default=0.25,
                   help="Output resolution in degrees")
    args = p.parse_args()

    if args.auth:
        print("Starting GEE authentication...")
        ee.Authenticate()
        ee.Initialize()
        print("Done. You can now run exports.")
        return

    try:
        ee.Initialize()
    except ee.EEException:
        print("GEE not authenticated. Run 'python scripts/export_modis_gee.py --auth' first.")
        sys.exit(1)

    print(f"GEE initialized. Project: {ee.String(ee.data.getCloudProject()).getInfo()}")
    print(f"Drive folder: {args.drive_folder}")
    print(f"Resolution: {args.scale} degrees")

    if args.year:
        years = [args.year]
    else:
        years = list(range(args.start, args.end + 1))

    print(f"Years: {years[0]}-{years[-1]} ({len(years)} total)")
    print(f"\nExporting as GeoTIFF (one file per year)...")
    print(f"After export, download from Google Drive to: data/raw/modis_gee/")
    print(f"Then run: python scripts/convert_modis_geotiff.py")

    for year in years:
        try:
            export_year_geotiff(year, args.drive_folder, args.scale)
            time.sleep(1)  # avoid rate limits
        except Exception as e:
            print(f"  ERROR for {year}: {e}")

    print(f"\nAll tasks submitted!")
    print(f"Check https://code.earthengine.google.com/tasks for progress.")
    print(f"Files will appear in Google Drive > {args.drive_folder}")


if __name__ == "__main__":
    main()