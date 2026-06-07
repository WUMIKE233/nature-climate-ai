# Data-source access notes

Checked date: 2026-06-04

Before downloading any public data, run:

```powershell
python -m nature_climate_ai.cli data-access-plan --config config/study.yaml --manifest data/metadata/data_access_manifest.csv --report data/metadata/data_access_plan.md
```

This creates the project-wide access manifest and records unresolved placeholders for human review.

## ERA5 / ERA5-Land

Official source: https://climate.copernicus.eu/climate-reanalysis

Current interpretation:

- ERA5 provides hourly atmospheric, land-surface and related variables through the Copernicus Climate Data Store.
- ERA5 is available on 0.25 degree regular latitude-longitude grids and is extended forward with a short delay.
- ERA5-Land is a land-surface dataset at finer spatial resolution and is also available through the Climate Data Store.

Project implication:

- Record exact CDS dataset IDs, request payloads, variables, date ranges and access dates before using any climate variable in the manuscript.

## MODIS vegetation indices

Official source: https://modis.gsfc.nasa.gov/data/dataprod/mod13.php

Current interpretation:

- MODIS vegetation-index products provide NDVI and EVI on 16-day intervals.
- MODIS VI compositing uses product quality-assurance information to remove low-quality pixels.
- The project must record product collection, Terra/Aqua product IDs and quality-flag interpretation before anomaly estimation.

Project implication:

- MODIS quality filtering is a manuscript-critical step, not a minor preprocessing detail.

## FLUXNET

Official source: https://fluxnet.org/data/fluxnet2015-dataset/

Current interpretation:

- FLUXNET2015 includes data-quality-control and processing-pipeline improvements and points users to the data policy for usage and acknowledgement requirements.
- The FLUXNET2015 page states that FLUXNET2015 is outdated for latest data and points to FLUXNET Shuttle for the latest data route.
- FLUXNET2015 is distributed under Tier 1 and Tier 2 policies. Tier 1 is more open; Tier 2 is more restrictive and covers all site-years.

Project implication:

- The manuscript should not simply say "FLUXNET" without specifying dataset/version, Tier policy, site-years, redistribution limits and required acknowledgements.
