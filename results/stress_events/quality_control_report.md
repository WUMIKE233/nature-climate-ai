# E01 stress-event catalogue quality-control report

Status: COMPLETE_FOR_INPUT_DATA

This report summarizes event-catalogue construction for the supplied quality-filtered anomaly table. It does not certify that the input table covers the full global study domain.

- Input table: data/processed/modis_anomalies.csv

## Summary

metric | value
--- | ---
input_rows | 11607157
valid_rows | 11607157
dropped_rows | 0
unique_units | 10750
units_with_events | 10721
event_count | 155644
percentile | 10.0
minimum_duration | 2
date_min | 2000-02-18
date_max | 2025-12-27

## Manuscript-use warning

Do not promote this event catalogue into the Nature or Science manuscript unless the input data are confirmed to be quality-filtered MODIS anomalies for the intended study domain and years.
