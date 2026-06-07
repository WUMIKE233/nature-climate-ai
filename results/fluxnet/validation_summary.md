# FLUXNET ecosystem validation readiness report

Status: NOT_READY

The command did not generate FLUXNET validation metrics because required inputs are missing.

Required inputs:

- FLUXNET anomaly table: data/processed/fluxnet_anomalies.csv
- Predicted stress windows: results/fluxnet/predicted_stress_windows.csv

Required FLUXNET columns:

- `site_id`
- `date`
- `gpp_anomaly`
- optional `le_anomaly`

Required window columns:

- `site_id`
- `start_date`
- `end_date`

Missing inputs:

- data/processed/fluxnet_anomalies.csv
- results/fluxnet/predicted_stress_windows.csv
