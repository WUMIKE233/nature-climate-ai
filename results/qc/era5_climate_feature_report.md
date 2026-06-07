# ERA5 climate lag-feature QC report

Status: COMPLETE_FOR_INPUT_DATA

This report summarizes lagged climate-feature generation for the supplied aggregated ERA5/ERA5-Land table. It does not certify provider access, global coverage or correct hourly-to-composite aggregation.

- Input table: data/interim/era5_composite_climate.csv

## Summary

metric | value
--- | ---
input_rows | 11721996
valid_rows_before_climatology_filter | 6446440
output_rows | 7287280
dropped_rows | 5275556
unique_units | 10780
variables | 2m_temperature,total_precipitation,soil_moisture,surface_net_solar_radiation,vapour_pressure_deficit
lead_times_days | 16,32,48,64
min_climatology_samples | 2
date_min | 2000-01-24
date_max | 2026-02-28

## Manuscript-use warning

Do not use these features as manuscript evidence until ERA5/ERA5-Land request parameters, aggregation windows, spatial alignment and leakage checks are documented.
