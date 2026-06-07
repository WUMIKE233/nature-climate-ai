# Spatial holdout validation report

Status: COMPLETE_FOR_INPUT_DATA

This report evaluates ranked precursor candidates under leave-one-region-out validation. It does not establish full predictive validation without temporal holdout, baseline comparison and uncertainty analysis.

- Modeling dataset: data/processed/modeling_dataset.csv
- Candidate table: results/modeling/feature_attribution_table.csv

## Summary

metric | value
--- | ---
modeling_rows | 7287280
candidate_rows | 20
selected_features | 10
regions | 20
metric_rows | 200
region_column | region

## Manuscript-use warning

Do not claim spatial generalization until region definitions, spatial coverage, baseline comparisons and uncertainty estimates are complete.
