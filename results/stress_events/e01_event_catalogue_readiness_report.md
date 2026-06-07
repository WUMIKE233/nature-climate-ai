# E01 stress-event catalogue readiness report

Status: NOT_READY

Expected input table: data/processed/modis_anomalies.csv

The event-catalogue command did not create manuscript evidence artifacts because the input anomaly table is missing.

Required input columns:

- `date`: MODIS composite date.
- `pixel_id`: stable pixel, site or region identifier.
- `evi_anomaly`: quality-filtered EVI anomaly.

Optional next step: generate a small pilot table after MODIS access is confirmed, then rerun `e01-event-catalogue`.
