# Temporal holdout validation report

Status: COMPLETE_FOR_INPUT_DATA

This report evaluates ranked precursor candidates on the configured temporal holdout. It does not establish full predictive validation without spatial holdout and uncertainty analysis.

- Modeling dataset: data/processed/modeling_dataset.csv
- Candidate table: results/modeling/feature_attribution_table.csv

## Summary

metric | value
--- | ---
modeling_rows | 7287280
candidate_rows | 20
selected_features | 10
train_rows | 5885880
holdout_rows | 1401400
holdout_range | 2021-2025

## Manuscript-use warning

Do not claim predictive improvement until temporal holdout, spatial holdout, baseline comparison and uncertainty estimates are all complete.
