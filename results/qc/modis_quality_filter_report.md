# MODIS quality-filtering QC report

Status: COMPLETE_FOR_INPUT_DATA

This report summarizes quality filtering for the supplied MODIS observation table. It does not certify product collection, global coverage or provider-policy compliance.

- Input table: data/raw/modis_observations.csv

## Summary

metric | value
--- | ---
input_rows | 22267872
valid_core_rows | 12832691
output_rows | 11608373
dropped_rows | 10659499
unique_units | 10766
quality_source | qa_ok
date_min | 2000-02-18
date_max | 2025-12-27

## Manuscript-use warning

Do not use this filtered table as manuscript evidence until the MODIS product collection, QA bit interpretation, spatial domain and temporal coverage have been independently reviewed.
