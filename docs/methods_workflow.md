# Methods workflow

## 1. Data acquisition

Acquire public data through official provider channels and record exact versions, date ranges, request parameters and access dates.

- ERA5/ERA5-Land: atmospheric and land-surface climate variables.
- MODIS MOD13/MYD13: EVI, NDVI and quality flags.
- FLUXNET: GPP, latent heat and meteorological variables for independent validation.
- Run `data-access-plan` before downloading data so source-specific requirements, expected local artifacts and unresolved access placeholders are recorded.

## 2. Preprocessing

- Harmonize temporal resolution to the MODIS compositing interval.
- Apply MODIS quality flags before anomaly estimation.
- Use `modis-quality-filter` to generate `data/interim/modis_quality_filtered.csv` from imported MODIS observations.
- Regrid or aggregate climate variables to the working grid.
- Construct pixel-level or region-level climatologies.
- Compute anomalies without using held-out future information.
- Use `modis-anomalies` to generate `data/processed/modis_anomalies.csv` from a quality-filtered MODIS table.

## 3. Event definition

- Define primary stress events from EVI anomalies below the configured percentile.
- Require persistence for at least two compositing periods.
- Use NDVI as a secondary sensitivity analysis.
- Store event masks separately from model features to prevent leakage.
- Generate the event catalogue with `e01-event-catalogue` only after MODIS quality filtering has been completed and documented.

## 4. Feature construction

- Build lagged climate features for all configured lead windows.
- Include temperature, precipitation, soil moisture, radiation and vapour-pressure deficit.
- Keep feature construction deterministic and record all transformations.
- Use `era5-climate-features` to generate `data/processed/climate_lag_features.csv` from an ERA5/ERA5-Land table already aggregated and aligned to the MODIS grid or study units.

## 5. Modelling

- Assemble `data/processed/modeling_dataset.csv` with `modeling-dataset` after climate features and the stress-event catalogue are available.
- Start with simple baselines before complex models.
- Run `baseline-evaluation` before AI discovery so any later model-improvement claim has a documented comparator.
- Run `precursor-discovery` to rank interpretable lagged climate features before training more complex models.
- Run `temporal-holdout-validation` to test ranked candidate features on held-out years before drafting prediction claims.
- Run `spatial-holdout-validation` to test whether ranked candidates transfer across regions or biomes.
- Run `predictive-validation-summary` to combine baseline, temporal-holdout and spatial-holdout metrics into one evidence artifact.
- Run `uncertainty-audit` to compute initial Wilson intervals from saved confusion-count metrics.
- Run `fluxnet-validation` to test whether predicted stress windows correspond to independent ecosystem-function anomalies.
- Compare climatology, linear/logistic models, tree-based models and standard climate indices.
- Use interpretable models or interpretation methods that can be tested for stability.

## 6. Validation

- Use the configured temporal holdout years.
- Use leave-biome or leave-continent-out spatial validation.
- Treat predictive-validation summaries as synthesis artifacts, not final claims, until uncertainty and ecological validation are complete.
- Estimate uncertainty with block bootstrap or comparable spatial-temporal resampling.
- Treat Wilson intervals as an initial event-metric audit; they do not account for spatial or temporal autocorrelation.
- Use FLUXNET for independent ecological validation where collocation is possible.

## 7. Manuscript promotion rule

A statement may move from `RESULT_REQUIRED` to final manuscript text only when it has:

- a saved result artifact,
- a corresponding figure, table or statistic,
- a documented validation path,
- and no unresolved data-access or quality-control issue.

## 8. Figure generation

- Run `generate-figure-assets` to create the Fig. 1 workflow schematic, figure manifest and figure-generation report.
- Treat Fig. 1 as a non-result schematic until data coverage and workflow outputs are complete.
- Do not generate Fig. 2-4 final panels until attribution, predictive validation and FLUXNET evidence exist.
