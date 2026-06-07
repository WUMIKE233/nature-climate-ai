# MODIS anomaly-generation QC report

Status: COMPLETE_FOR_INPUT_DATA

This report summarizes anomaly generation for the supplied quality-filtered MODIS table. It does not certify global coverage or provider-policy compliance.

- Input table: data/interim/modis_quality_filtered.csv

## Summary

metric | value
--- | ---
input_rows | 11608373
rows_after_quality_filter | 11608373
valid_rows_before_climatology_filter | 11608373
output_rows | 11607157
dropped_rows | 1216
unique_units | 10750
min_climatology_samples | 2
date_min | 2000-02-18
date_max | 2025-12-27

## Manuscript-use warning

Do not use these anomalies as manuscript evidence until the input MODIS product collection, quality flags, temporal coverage and spatial domain have been verified.
