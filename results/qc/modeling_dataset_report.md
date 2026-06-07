# Modeling dataset QC report

Status: COMPLETE_FOR_INPUT_DATA

This report summarizes assembly of the supervised model dataset from lagged climate features and vegetation-stress events. It does not certify that upstream data cover the full study domain.

- Climate features: data/processed/climate_lag_features.csv
- Event catalogue: results/stress_events/event_catalogue_summary.csv

## Summary

metric | value
--- | ---
climate_feature_rows | 7287280
event_catalogue_rows | 155644
output_rows | 7287280
positive_labels | 503743
negative_labels | 6783537
unique_units | 10780
anomaly_columns_added | 2
region_source | derived_from_pixel_id_grid_blocks_row30_col40
region_count | 20
date_min | 2000-01-24
date_max | 2026-02-28

## Manuscript-use warning

Do not use this model dataset as manuscript evidence until upstream MODIS and ERA5 evidence items are complete and leakage checks are documented.
