# Figure plan

## Main figures

### Fig. 1: Global study design and data/model pipeline

Purpose: show the full evidence chain from public data to validated precursor discovery.

Panels:

- ERA5/ERA5-Land climate variables and MODIS EVI/NDVI records.
- MODIS quality filtering and vegetation-anomaly construction.
- Vegetation-stress event definition.
- Lagged climate-feature construction.
- Model training, interpretation and validation design.

Evidence required: data coverage diagnostics, event counts and workflow outputs.

### Fig. 2: Discovered precursor patterns and regions

Purpose: present only validated climate precursor states.

Panels:

- Global map of precursor strength or event probability.
- Lead-time response curves for key variables.
- Regional or biome-level attribution summary.
- Example stress-event timelines.

Evidence required: attribution stability, spatial validation and uncertainty intervals.

### Fig. 3: Predictive and attribution validation versus baselines

Purpose: show that the AI framework adds validated value beyond standard indices and simpler models.

Panels:

- Precision-recall or ROC curves for temporal holdout.
- Leave-region-out validation metrics.
- Calibration plots.
- Ablation study for compound-variable groups.

Evidence required: held-out predictions, baseline outputs, confidence intervals and permutation tests.

### Fig. 4: Ecosystem/FLUXNET validation and mechanism interpretation

Purpose: connect satellite-defined vegetation stress to independent ecosystem-function observations.

Panels:

- FLUXNET site map.
- GPP or latent heat anomalies during predicted stress windows.
- Plant functional type or climate-zone stratification.
- Mechanistic diagram grounded in validated variables.

Evidence required: FLUXNET collocation, site-level anomaly analysis and uncertainty estimates.

## Extended Data figures

- Extended Data Fig. 1: sensitivity to EVI versus NDVI and event thresholds.
- Extended Data Fig. 2: spatial transfer across continents, biomes or climate zones.
- Extended Data Fig. 3: missingness and MODIS quality-filtering diagnostics.
- Extended Data Fig. 4: model hyperparameter and compute-budget sensitivity.
- Extended Data Fig. 5: regions where the discovered precursors fail or are ambiguous.
