"""Data download module for ERA5, MODIS, and FLUXNET public datasets.

Each downloader checks for required credentials before attempting access.
Credentials are NEVER stored in the repository — they must be provided
via environment variables or provider-standard config files.
"""
from __future__ import annotations

import csv
import hashlib
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import load_study_config

logger = logging.getLogger(__name__)


def _sha256_hex(path: Path) -> str:
    """Return SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _ensure_dir(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


@dataclass(frozen=True)
class DownloadLogEntry:
    source: str
    status: str
    local_path: str
    remote_id: str
    size_bytes: int
    sha256: str
    timestamp: str
    message: str


def _write_download_log(entries: list[DownloadLogEntry], path: Path) -> Path:
    _ensure_dir(path)
    fieldnames = list(DownloadLogEntry.__dataclass_fields__)
    file_exists = path.exists()
    with path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        for entry in entries:
            writer.writerow(entry.__dict__)
    return path


ERA5_CDS_DATASET = "reanalysis-era5-single-levels"
ERA5_LAND_CDS_DATASET = "reanalysis-era5-land"

ERA5_VARIABLES = [
    "2m_temperature",
    "2m_dewpoint_temperature",
    "surface_net_solar_radiation",
    "total_precipitation",
]

ERA5_LAND_VARIABLES = [
    "volumetric_soil_water_layer_1",
    "volumetric_soil_water_layer_2",
]
ERA5_DATASET_SELECTIONS = ("single", "land", "both")


def _selected_era5_requests(selection: str) -> tuple[tuple[str, str, list[str], str], ...]:
    if selection not in ERA5_DATASET_SELECTIONS:
        raise ValueError(f"Unsupported ERA5 dataset selection: {selection}")
    requests = []
    if selection in {"single", "both"}:
        requests.append(("single", ERA5_CDS_DATASET, ERA5_VARIABLES, "era5_single"))
    if selection in {"land", "both"}:
        requests.append(("land", ERA5_LAND_CDS_DATASET, ERA5_LAND_VARIABLES, "era5_land"))
    return tuple(requests)


def _check_cds_credentials() -> bool:
    """Return True if CDS API credentials appear to be configured."""
    rc_path = Path.home() / ".cdsapirc"
    if rc_path.exists():
        return True
    if os.environ.get("CDSAPI_URL") and os.environ.get("CDSAPI_KEY"):
        return True
    return False


def _cds_client():
    """Lazy-import cdsapi so the module is importable without it installed."""
    import cdsapi
    return cdsapi.Client()


def _make_era5_request(
    client,
    dataset: str,
    variables: list[str],
    year: str,
    month: str,
    output_path: Path,
    area: list[float] | None = None,
) -> DownloadLogEntry:
    """Submit a single ERA5 monthly request via CDS API."""
    request = {
        "product_type": ["reanalysis"],
        "variable": variables,
        "year": [year],
        "month": [month],
        "day": [f"{d:02d}" for d in range(1, 32)],
        "time": [f"{h:02d}:00" for h in range(24)],
        "data_format": "netcdf",
    }
    if area is not None:
        request["area"] = area

    output_path = _ensure_dir(output_path)
    print(f"REQUEST {dataset} {year}-{month} -> {output_path}", flush=True)
    try:
        client.retrieve(dataset, request).download(str(output_path))
        size = output_path.stat().st_size
        digest = _sha256_hex(output_path)
        print(f"SUCCESS {dataset} {year}-{month} {size} bytes", flush=True)
        return DownloadLogEntry(
            source="era5",
            status="success",
            local_path=str(output_path),
            remote_id=f"{dataset}/{year}/{month}",
            size_bytes=size,
            sha256=digest,
            timestamp=datetime.now().isoformat(),
            message=f"Downloaded {chr(44).join(variables)}",
        )
    except Exception as exc:
        print(f"FAILED {dataset} {year}-{month}: {exc}", flush=True)
        return DownloadLogEntry(
            source="era5",
            status="failed",
            local_path=str(output_path),
            remote_id=f"{dataset}/{year}/{month}",
            size_bytes=0,
            sha256="",
            timestamp=datetime.now().isoformat(),
            message=str(exc),
        )


def download_era5(
    years: list[int],
    months: list[int] | None = None,
    output_dir: str | Path = "data/raw/era5",
    log_path: str | Path = "data/metadata/era5_download_log.csv",
    area: list[float] | None = None,
    dataset_selection: str = "both",
) -> tuple[int, int, int, Path]:
    """Download ERA5 single-level + ERA5-Land variables from CDS.

    Returns (success_count, skipped_count, failed_count, log_path).
    """
    if months is None:
        months = list(range(1, 13))
    selected_requests = _selected_era5_requests(dataset_selection)

    if not _check_cds_credentials():
        msg = (
            "CDS API credentials not found.\n"
            "Set up ~/.cdsapirc or environment variables CDSAPI_URL / CDSAPI_KEY.\n"
            "Instructions: https://cds.climate.copernicus.eu/api-how-to"
        )
        logger.error(msg)
        return (0, 0, 0, Path(log_path))

    client = _cds_client()
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    entries: list[DownloadLogEntry] = []
    success = skipped = failed = 0

    for year in years:
        for month in months:
            yr_str = str(year)
            mo_str = f"{month:02d}"

            for _label, dataset, variables, prefix in selected_requests:
                output_path = out_dir / f"{prefix}_{yr_str}{mo_str}.nc"
                if output_path.exists():
                    skipped += 1
                    logger.info("Skipping existing: %s", output_path)
                    print(f"SKIP existing {output_path}", flush=True)
                else:
                    entry = _make_era5_request(
                        client, dataset, variables, yr_str, mo_str, output_path, area
                    )
                    entries.append(entry)
                    if entry.status == "success":
                        success += 1
                    else:
                        failed += 1
                    time.sleep(0.5)

    log = _write_download_log(entries, Path(log_path))
    logger.info(
        "ERA5 download complete: %d success, %d skipped, %d failed",
        success, skipped, failed,
    )
    return (success, skipped, failed, log)


MODIS_PRODUCTS = ["MOD13Q1", "MYD13Q1"]


def _check_earthdata_credentials() -> bool:
    """Return True if NASA Earthdata credentials appear configured."""
    netrc_path = Path.home() / ".netrc"
    if netrc_path.exists():
        content = netrc_path.read_text(errors="ignore")
        if "urs.earthdata.nasa.gov" in content:
            return True
    if os.environ.get("EARTHDATA_USERNAME") and os.environ.get("EARTHDATA_PASSWORD"):
        return True
    return False


def _earthaccess_auth():
    """Lazy-import and authenticate with earthaccess."""
    import earthaccess
    return earthaccess.login(strategy="interactive", persist=True)


def download_modis(
    years: list[int],
    products: list[str] | None = None,
    tiles: list[str] | None = None,
    output_dir: str | Path = "data/raw/modis",
    log_path: str | Path = "data/metadata/modis_download_log.csv",
) -> tuple[int, int, int, Path]:
    """Download MODIS vegetation-index products via NASA Earthdata.

    Uses earthaccess to search and download MOD13Q1/MYD13Q1 granules.
    If tiles is None, attempts global download (may be very large).

    Returns (success_count, skipped_count, failed_count, log_path).
    """
    if products is None:
        products = MODIS_PRODUCTS

    if not _check_earthdata_credentials():
        msg = (
            "NASA Earthdata credentials not found.\n"
            "Set up ~/.netrc with urs.earthdata.nasa.gov entry, or set\n"
            "EARTHDATA_USERNAME / EARTHDATA_PASSWORD environment variables.\n"
            "Instructions: https://www.earthdata.nasa.gov/eosdis/"
            "science-system-description/eosdis-components/earthdata-login"
        )
        logger.error(msg)
        return (0, 0, 0, Path(log_path))

    try:
        auth = _earthaccess_auth()
    except Exception as exc:
        logger.error("Earthdata authentication failed: %s", exc)
        return (0, 0, 0, Path(log_path))

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    entries: list[DownloadLogEntry] = []
    success = skipped = failed = 0

    for product in products:
        for year in years:
            date_range = (f"{year}-01-01", f"{year}-12-31")
            try:
                results = auth.search_data(
                    short_name=product,
                    temporal=date_range,
                )
            except Exception as exc:
                logger.warning("Search failed for %s %s: %s", product, year, exc)
                entries.append(DownloadLogEntry(
                    source="modis",
                    status="failed",
                    local_path="",
                    remote_id=f"{product}/{year}",
                    size_bytes=0,
                    sha256="",
                    timestamp=datetime.now().isoformat(),
                    message=f"Search error: {exc}",
                ))
                failed += 1
                continue

            if not results:
                logger.info("No granules found for %s %s", product, year)
                continue

            for granule in results:
                granule_name = granule.get("umm", {}).get("GranuleUR", str(granule))
                local_file = out_dir / f"{granule_name}.hdf"
                if local_file.exists():
                    skipped += 1
                    logger.info("Skipping existing: %s", local_file)
                    continue

                try:
                    files = auth.download(granule, str(out_dir))
                    for f in files:
                        fp = Path(f)
                        size = fp.stat().st_size
                        digest = _sha256_hex(fp)
                        entries.append(DownloadLogEntry(
                            source="modis",
                            status="success",
                            local_path=str(fp),
                            remote_id=granule_name,
                            size_bytes=size,
                            sha256=digest,
                            timestamp=datetime.now().isoformat(),
                            message="Downloaded",
                        ))
                        success += 1
                except Exception as exc:
                    entries.append(DownloadLogEntry(
                        source="modis",
                        status="failed",
                        local_path=str(local_file),
                        remote_id=granule_name,
                        size_bytes=0,
                        sha256="",
                        timestamp=datetime.now().isoformat(),
                        message=str(exc),
                    ))
                    failed += 1

    log = _write_download_log(entries, Path(log_path))
    logger.info(
        "MODIS download complete: %d success, %d skipped, %d failed",
        success, skipped, failed,
    )
    return (success, skipped, failed, log)


def fluxnet_download_instructions() -> str:
    """Return step-by-step instructions for FLUXNET data access."""
    return """
FLUXNET Data Download Instructions
===================================

FLUXNET data requires explicit policy acceptance and cannot be downloaded
automatically. Follow these steps:

1. Visit https://fluxnet.org/data/fluxnet2015-dataset/
   (or the current FLUXNET data portal for newer releases)

2. Review and accept the FLUXNET data policy (Tier 1 or Tier 2).
   - Tier 1: open-access sites, fewer usage restrictions.
   - Tier 2: all sites, more restrictive redistribution terms.

3. Download the site-level CSV files for your target variables:
   - GPP_NT_VUT_REF (gross primary productivity)
   - LE_F_MDS (latent heat)
   - TA_F (air temperature)
   - SW_IN_F (incoming shortwave radiation)
   - VPD_F (vapour pressure deficit)

4. Place the downloaded files in:
   data/raw/fluxnet/

5. Update data/metadata/fluxnet_policy_review.md with:
   - Dataset version and DOI
   - Policy tier accepted
   - Site list
   - Citation requirements
   - Redistribution limits

6. Run the FLUXNET preprocessing pipeline to generate
   data/processed/fluxnet_anomalies.csv

After completing these steps, run:
   nature-climate-ai fluxnet-validation
""".strip()


def run_era5_download_command(
    config_path: str | Path,
    output_dir: str | Path,
    log_path: str | Path,
    year_start: int | None = None,
    year_end: int | None = None,
    dry_run: bool = False,
    months: list[int] | None = None,
    dataset_selection: str = "both",
) -> tuple[int, int, int, Path]:
    """CLI wrapper that reads config to get year range."""
    config = load_study_config(config_path)
    temporal = config.get("temporal_domain", {})
    era5_years = temporal.get("era5_years", [2000, 2025])

    if year_start is not None:
        y0 = year_start
    else:
        y0 = era5_years[0] if isinstance(era5_years, list) else 2000
    if year_end is not None:
        y1 = year_end
    else:
        y1 = era5_years[1] if isinstance(era5_years, list) else 2025

    years = list(range(y0, y1 + 1))
    selected_requests = _selected_era5_requests(dataset_selection)

    if dry_run:
        selected_months = months if months is not None else list(range(1, 13))
        total_requests = len(years) * len(selected_months) * len(selected_requests)
        print(f"DRY RUN: Would download ERA5 data for {y0}-{y1} ({len(years)} years)")
        print(f"  Total CDS API requests: {total_requests}")
        print(f"  Dataset selection: {dataset_selection}")
        print(f"  Months: {','.join(str(month) for month in selected_months)}")
        print(f"  Output directory: {output_dir}")
        print(f"  Log path: {log_path}")
        print()
        print("Credentials check:")
        if _check_cds_credentials():
            print("  CDS API credentials FOUND")
        else:
            print("  CDS API credentials NOT FOUND - set up ~/.cdsapirc first")
        return (0, 0, 0, Path(log_path))

    return download_era5(
        months=months,
        years=years,
        output_dir=output_dir,
        log_path=log_path,
        dataset_selection=dataset_selection,
    )


def run_modis_download_command(
    config_path: str | Path,
    output_dir: str | Path,
    log_path: str | Path,
    year_start: int | None = None,
    year_end: int | None = None,
    tiles: str | None = None,
    dry_run: bool = False,
) -> tuple[int, int, int, Path]:
    """CLI wrapper for MODIS download."""
    config = load_study_config(config_path)
    temporal = config.get("temporal_domain", {})
    modis_years = temporal.get("modis_years", [2001, 2025])

    if year_start is not None:
        y0 = year_start
    else:
        y0 = modis_years[0] if isinstance(modis_years, list) else 2001
    if year_end is not None:
        y1 = year_end
    else:
        y1 = modis_years[1] if isinstance(modis_years, list) else 2025

    years = list(range(y0, y1 + 1))
    tile_list = tiles.split(",") if tiles else None

    if dry_run:
        print(f"DRY RUN: Would download MODIS data for {y0}-{y1} ({len(years)} years)")
        print(f"  Products: MOD13Q1, MYD13Q1")
        if tile_list:
            print(f"  Tiles: {tile_list}")
        else:
            print("  Tiles: ALL (global — this will be very large!)")
        print(f"  Output directory: {output_dir}")
        print(f"  Log path: {log_path}")
        print()
        print("Credentials check:")
        if _check_earthdata_credentials():
            print("  NASA Earthdata credentials FOUND")
        else:
            print("  NASA Earthdata credentials NOT FOUND — set up ~/.netrc first")
        return (0, 0, 0, Path(log_path))

    return download_modis(
        years=years,
        output_dir=output_dir,
        log_path=log_path,
    )
