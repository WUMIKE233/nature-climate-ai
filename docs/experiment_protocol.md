# Experiment protocol

## Experiment IDs

Use stable experiment IDs so manuscript claims can be traced to artifacts:

- `E00_data_qc`: data availability, missingness and quality-filter diagnostics.
- `E01_event_catalogue`: MODIS vegetation-stress event construction.
- `E02_climate_features`: ERA5/ERA5-Land anomaly and lag-feature construction.
- `E03_modeling_dataset`: supervised model dataset assembly.
- `E04_baselines`: climatology, linear models, drought/heat indices and tree baselines.
- `E05_ai_discovery`: interpretable spatiotemporal precursor discovery.
- `E06_temporal_holdout`: 2021-2025 temporal holdout validation.
- `E07_spatial_holdout`: leave-biome or leave-continent-out validation.
- `E08_predictive_validation`: synthesis of baseline, temporal-holdout and spatial-holdout metrics.
- `E09_fluxnet_validation`: independent ecosystem-function validation.
- `E10_sensitivity`: event-threshold, index, lag-window and masking sensitivity.

## Artifact rule

Every experiment must write:

- a machine-readable result file,
- a short human-readable summary,
- a command log,
- and the config hash or full config snapshot.

For `E00_data_qc`, run:

```powershell
python -m nature_climate_ai.cli manuscript-format-audit --manuscript manuscript/nature_article_draft.md --journal nature --output results/submission/manuscript_format_audit.md
python -m nature_climate_ai.cli generate-figure-assets --config config/study.yaml --output-dir figures/generated --manifest figures/generated/figure_manifest.csv --report figures/generated/figure_generation_report.md
python -m nature_climate_ai.cli data-access-plan --config config/study.yaml --manifest data/metadata/data_access_manifest.csv --report data/metadata/data_access_plan.md
python -m nature_climate_ai.cli e00-data-qc --output results/qc/e00_data_qc_report.md
```

These commands record current readiness and should remain `NOT_READY` until the manuscript has evidence-backed claims and real provider access and data metadata are confirmed.

For `E01_event_catalogue`, run:

```powershell
python -m nature_climate_ai.cli modis-quality-filter --input data/raw/modis_observations.csv --output data/interim/modis_quality_filtered.csv --report results/qc/modis_quality_filter_report.md
python -m nature_climate_ai.cli modis-anomalies --input data/interim/modis_quality_filtered.csv --output data/processed/modis_anomalies.csv --report results/qc/modis_anomaly_qc_report.md
python -m nature_climate_ai.cli e01-event-catalogue --input data/processed/modis_anomalies.csv --output-dir results/stress_events
```

If the input is missing, the command writes only a readiness report. If the input exists, it writes the evidence artifacts required by `stress_event_catalogue` in `evidence/registry.yaml`.

For `E02_climate_features`, run:

```powershell
python -m nature_climate_ai.cli era5-climate-features --input data/interim/era5_composite_climate.csv --output data/processed/climate_lag_features.csv --report results/qc/era5_climate_feature_report.md
```

This command creates the climate-side model features required before baseline or AI precursor-discovery experiments can run.

For `E03_modeling_dataset`, run:

```powershell
python -m nature_climate_ai.cli modeling-dataset --climate data/processed/climate_lag_features.csv --events results/stress_events/event_catalogue_summary.csv --anomalies data/processed/modis_anomalies.csv --output data/processed/modeling_dataset.csv --report results/qc/modeling_dataset_report.md
```

This command creates a shared supervised dataset for baseline and AI models.

For `E04_baselines`, run:

```powershell
python -m nature_climate_ai.cli baseline-evaluation --input data/processed/modeling_dataset.csv --output results/validation/baseline_metrics.csv --report results/validation/baseline_comparison.md
```

Baseline results are comparators only; they do not establish any AI-discovery claim.

For `E05_ai_discovery`, run the first interpretable precursor-discovery pass:

```powershell
python -m nature_climate_ai.cli precursor-discovery --input data/processed/modeling_dataset.csv --attribution results/modeling/feature_attribution_table.csv --lag-response results/modeling/lag_response_summary.csv --report results/modeling/precursor_discovery_report.md
```

These outputs are candidate discoveries only and must be validated before manuscript use.

For `E06_temporal_holdout`, run:

```powershell
python -m nature_climate_ai.cli temporal-holdout-validation --modeling data/processed/modeling_dataset.csv --candidates results/modeling/feature_attribution_table.csv --output results/validation/temporal_holdout_metrics.csv --report results/validation/temporal_holdout_report.md
```

Temporal holdout results are necessary but not sufficient for predictive validation.

For `E07_spatial_holdout`, run:

```powershell
python -m nature_climate_ai.cli spatial-holdout-validation --modeling data/processed/modeling_dataset.csv --candidates results/modeling/feature_attribution_table.csv --output results/validation/spatial_holdout_metrics.csv --report results/validation/spatial_holdout_report.md --region-col region
```

Spatial holdout results are necessary to support transfer or generalization claims.

For `E08_predictive_validation`, run:

```powershell
python -m nature_climate_ai.cli predictive-validation-summary --baseline results/validation/baseline_metrics.csv --temporal results/validation/temporal_holdout_metrics.csv --spatial results/validation/spatial_holdout_metrics.csv --output results/validation/predictive_validation_summary.csv --report results/validation/predictive_validation_summary.md
python -m nature_climate_ai.cli uncertainty-audit --baseline results/validation/baseline_metrics.csv --temporal results/validation/temporal_holdout_metrics.csv --spatial results/validation/spatial_holdout_metrics.csv --output results/validation/uncertainty_intervals.csv --report results/validation/uncertainty_audit.md
```

These commands summarize predictive evidence and initial uncertainty intervals but do not by themselves establish superiority over baselines. Matched comparisons, spatial-temporal resampling and ecological validation are still required before manuscript promotion.

For `E09_fluxnet_validation`, run:

```powershell
python -m nature_climate_ai.cli fluxnet-validation --fluxnet data/processed/fluxnet_anomalies.csv --windows results/fluxnet/predicted_stress_windows.csv --output results/fluxnet/site_anomaly_metrics.csv --report results/fluxnet/validation_summary.md
```

FLUXNET validation is independent ecological support and must be interpreted with data-policy and site-representativeness limits.

## Promotion rule

No experiment result can be promoted into the manuscript until its matching evidence item in `evidence/registry.yaml` is complete.

## Negative results

If a model or precursor fails to generalize, keep the result. Nature/Science reviewers will expect the paper to distinguish broad mechanisms from regional artifacts.
