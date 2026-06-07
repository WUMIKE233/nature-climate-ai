# E00 data QC report

Status: NOT_READY

This report checks whether public data access and local data metadata are ready for analysis. It does not download data, validate credentials or certify provider-policy compliance.

## Study scope

- Target journal: Nature
- Working title: AI-guided discovery of climate precursors for global vegetation stress
- Spatial scope: global vegetated land
- MODIS years: 2001-2025
- ERA5 years: 2000-2025

## Public data-source readiness

source | provider | access status | variables/products
--- | --- | --- | ---
era5 | Copernicus Climate Data Store | PENDING_ACCESS_CONFIRMATION | 2m_temperature, total_precipitation, soil_moisture, surface_net_solar_radiation, vapour_pressure_deficit
modis | NASA MODIS | PENDING_ACCESS_CONFIRMATION | NDVI, EVI
fluxnet | FLUXNET | PENDING_ACCESS_CONFIRMATION | GPP_NT_VUT_REF, LE_F_MDS, TA_F, SW_IN_F, VPD_F

## Local data inventory

- Candidate local data files found: 6
- Candidate local data size: 9987258101 bytes

path | bytes
--- | ---
data/interim/era5_composite_climate.csv | 3706
data/processed/climate_lag_features.csv | 6373
data/raw/era5/cds_33d64ced25227315b2ee7a5bce17ecaa/era5_land_200001_swvl.nc | 5575391446
data/raw/era5/cds_8c5868ad2f6b9db27f57ebaaeb460755/data_stream-oper_stepType-accum.nc | 1349739662
data/raw/era5/cds_8c5868ad2f6b9db27f57ebaaeb460755/data_stream-oper_stepType-instant.nc | 2240033330
data/raw/era5/era5_land_200001.nc | 822083584

## Metadata placeholder-token counts

file | data_access_token | author_token | result_token
--- | ---: | ---: | ---:
none | 0 | 0 | 0

## Evidence registry status

- Complete evidence items: 0/18
- E00 can move forward only after pending access notes are replaced by verified provider-access notes and QC artifacts.

## Blocking actions

- Confirm Copernicus CDS access and record ERA5/ERA5-Land request parameters.
- Confirm NASA MODIS access route, product collection and quality-bit rules.
- Confirm FLUXNET dataset/version, Tier policy and redistribution/citation requirements.
- Populate local or remote data pointers and rerun this report.
