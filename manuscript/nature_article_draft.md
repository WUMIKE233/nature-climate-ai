# Interpretable discovery of lagged climate precursors for vegetation-index stress across Australia

吴卓宪 (Zhuoxian Wu)

广东东软学院 NUIT / Guangdong Neusoft Institute of Technology

---

## Abstract

Terrestrial vegetation stress driven by compound climate extremes is increasingly visible in satellite records, yet the extent to which lagged climate anomalies can serve as early-warning precursors—and the limits of such precursors—remain poorly quantified at continental scale. Here we construct an interpretable discovery framework that aligns 26 years of quality-filtered MODIS vegetation-index anomalies with ERA5-Land climate reanalysis on a unified 0.25° grid across Australia (2000–2025). We define vegetation-stress events from pixel-level EVI anomaly climatologies and evaluate 20 lagged climate predictors spanning soil moisture, vapour pressure deficit (VPD), temperature, precipitation and surface radiation at lead times of 16 to 64 days. Soil-moisture deficit and VPD excess are the dominant precursor signals, with the strongest separation between stress and non-stress conditions occurring at 16–32 day lead times. However, even the best-performing climate precursor (VPD at 16-day lag) achieves only modest precision (0.055) despite detecting 61% of stress events on held-out years, and spatial transfer of precursor signals across 20 grid-defined regions reveals substantial inter-regional variability. A shuffled-lag placebo test and threshold-sensitivity analysis confirm the robustness of the discovered patterns, while comparison against a simple persistence baseline—which achieves precision and recall of 0.66—demonstrates that knowing a pixel`s recent stress history is a stronger predictor than any single climate variable. These results indicate that climate precursors are useful for identifying elevated risk conditions but are insufficient for precise stress-event prediction without vegetation-memory and ecological-context information. The analysis framework is fully reproducible, with all data exports, preprocessing scripts, model configurations and validation outputs version-controlled and aligned to a single shared spatial grid.

---

## Main text

### Introduction

Terrestrial ecosystems modulate carbon, water and energy exchanges at continental to global scales, but their capacity to do so is increasingly disrupted by compound climate extremes[1,2]. Heatwaves, droughts and elevated atmospheric water demand can interact nonlinearly, transforming short meteorological anomalies into persistent vegetation stress that reduces gross primary productivity, alters surface energy partitioning and, in severe cases, triggers widespread mortality[3,4]. Satellite vegetation indices from the Moderate Resolution Imaging Spectroradiometer (MODIS) now provide more than two decades of near-daily observations of canopy greenness[5,6], and when combined with multi-decadal climate reanalysis products such as ERA5-Land[7], these records permit systematic examination of the climate conditions that precede satellite-observed vegetation stress.

Current operational drought and heat-stress monitoring relies predominantly on single-variable indices such as the Standardized Precipitation-Evapotranspiration Index (SPEI) or temperature-percentile thresholds[8]. These indices provide essential situational awareness but typically describe stress after it has accumulated, rather than identifying the specific multi-variable precursor states that elevate the probability of vegetation stress at sub-seasonal lead times. Recent work has demonstrated that machine-learning methods can improve sub-seasonal drought forecasting[9,10], but three gaps persist. First, many studies treat satellite vegetation indices and reanalysis climate data as if they share a common spatial grid, when in practice their native projections and resolutions differ—a misalignment that can produce spurious spatial correlations. Second, studies often report predictive performance without systematically comparing discovered precursors against simple temporal baselines such as the persistence of a previous stress event. Third, the spatial transferability of discovered precursors—whether a signal learned in one region holds in another—is rarely tested with the same rigour as temporal holdout.

Here we address these gaps with an interpretable discovery framework that (1) defines vegetation-stress events from quality-filtered, gridded MODIS EVI anomalies on a unified 0.25° grid, (2) constructs lagged climate features from ERA5-Land at leads of 16, 32, 48 and 64 days, (3) ranks candidate precursors by their ability to discriminate stress from non-stress conditions, (4) systematically evaluates the discovered patterns against temporal holdout, spatial holdout, a persistence baseline, single-variable climate thresholds and a shuffled-lag placebo test, and (5) assesses sensitivity to the stress-threshold definition. A central methodological requirement is that MODIS and ERA5 data must reside on the same pixel grid before any analysis proceeds—an automated grid-alignment audit verifies this condition for every exported file.

### Results

#### Vegetation-stress event catalogue

We analysed 22,267,872 MODIS vegetation-index observations from Terra (MOD13Q1 v061) and Aqua (MYD13Q1 v061) 16-day composite products spanning 2000–2025 across the Australian continent (109.75°E–150.25°E, 40.25°S–10.00°S). Strict quality filtering using the MODIS VI Quality bitmask (MODLAND QA ≤ 1, VI usefulness ≤ 11, low aerosol, no cloud, no snow/ice, no shadow) retained 11,608,373 observations (52.1%) across 10,766 terrestrial 0.25° grid cells. Pixel-level EVI day-of-year climatologies were computed from the quality-filtered record, and negative anomalies exceeding the 10th percentile that persisted for at least two consecutive 16-day compositing periods were flagged as vegetation-stress events (Fig. 2). This procedure yielded 1,438,750 anomaly records and a modelling-eligible sample of 7,287,280 rows, of which 503,743 (6.9%) carried positive stress-event labels.

#### Climate precursor features

Twenty lagged climate predictors were constructed from ERA5-Land hourly reanalysis, aggregated into the same 16-day compositing windows as the MODIS data: 2 m temperature, total precipitation, soil moisture (mean of volumetric soil water layers 1 and 2), surface net solar radiation, and vapour pressure deficit (VPD, computed in GEE from window-mean temperature and dewpoint temperature using the Magnus formula). Anomalies were computed relative to each pixel`s 26-year climatology and shifted to lead times of 16, 32, 48 and 64 days, producing 20 lagged anomaly features (5 variables × 4 lead times). All features were aligned to vegetation observations without using future information relative to each observation row.

#### Discovery of precursor signals

Feature-attribution analysis ranked all 20 lagged climate predictors by their absolute point-biserial correlation with the binary stress-event label (Fig. 3). Soil-moisture deficit at 16-day lag was the strongest single predictor (|r| = 0.210), followed by soil moisture at 32-day lag (|r| = 0.206) and VPD excess at 32-day lag (|r| = 0.163). The predictive signal decayed monotonically with increasing lead time: soil-moisture correlation dropped from 0.210 at 16 days to 0.169 at 64 days, and VPD correlation dropped from 0.163 at 32 days to 0.144 at 64 days. Stress-event windows were characterised by soil-moisture anomalies approximately 0.03 units below climatology and VPD anomalies approximately 0.30 kPa above climatology relative to non-stress windows.

#### Predictive validation against baselines

We evaluated the discovered precursor signals against a suite of baselines on a temporal holdout comprising the most recent 20% of years (Fig. 4). The persistence baseline—predicting a stress event whenever the previous 16-day window contained a stress event at the same pixel—achieved precision of 0.659 and recall of 0.661, establishing a strong temporal benchmark. The majority-class baseline (always predict non-stress) achieved accuracy of 0.962, reflecting the low base rate of stress events.

Among single-variable threshold models using the training-set median as the decision boundary, VPD at 16-day lag achieved the highest recall on held-out years (0.609) but with precision of only 0.055. A multi-lag VPD family model combining all four lead times improved recall to 0.737 but at the cost of slightly lower precision (0.062). Soil-moisture deficit at 16-day lag achieved recall of 0.181 and precision of 0.014, indicating that soil-moisture anomalies are more specific but far less sensitive signals than VPD. Temperature-based and precipitation-based thresholds performed substantially worse than VPD and soil moisture across all lead times. Compound heat–drought thresholds combining temperature and moisture variables achieved recall of 0.693, comparable to the VPD family model, but with precision of only 0.049.

#### Spatial transfer and robustness

Spatial holdout validation across 20 contiguous grid-defined regions tested whether precursor–stress relationships discovered in some regions transfer to held-out regions (Fig. 5). Mean spatial-holdout recall for VPD at 16-day lag was 0.618 (range 0.537–0.676 across regions), and mean precision was 0.092. Soil-moisture deficit showed more variable spatial transfer (mean recall 0.167, range 0.143–0.239 across regions). The VPD signal transferred more consistently than soil moisture or temperature, suggesting that atmospheric moisture demand is a more spatially coherent precursor of vegetation-index stress than surface soil moisture in the Australian domain.

A shuffled-lag placebo test in which climate feature lags were randomly permuted and the resulting correlations compared against true values confirmed that the observed precursor associations exceed random noise. Threshold-sensitivity analysis across the 5th to 20th anomaly percentiles showed that the ranking of precursor candidates was stable, although absolute performance metrics varied with the chosen threshold.

### Discussion

Our results establish that interpretable climate precursor signals can be systematically discovered from satellite vegetation records and reanalysis data on a unified spatial grid. The dominant precursor signals—soil-moisture deficit and VPD excess at 16–32 day lead times—are consistent with known ecohydrological mechanisms[11,12], and the decay of predictive signal with increasing lead time suggests that the precursor window for actionable warning is approximately two to four weeks in this domain.

Three findings carry particular implications for early-warning applications. First, the persistence baseline is surprisingly strong: knowing whether a pixel experienced stress in the previous 16-day window already captures two-thirds of future stress events, and no climate threshold model surpasses this simple benchmark on precision. This reflects the slow recovery of water-limited ecosystems after drought onset and implies that any climate-based early-warning system must be evaluated against persistence to demonstrate added value. Second, the false-alarm rate of even the best single-variable precursor is high: VPD thresholds that detect 61% of stress events also flag approximately 41% of non-stress windows as potential precursors. This trade-off between sensitivity and specificity may be irreducible for purely climate-driven precursors—many vegetation-stress events have non-climatic drivers (fire, disease, land-use change, insect outbreaks) that no climate precursor can anticipate, and the opposite case (elevated VPD that does not produce visible canopy stress) may reflect vegetation acclimation, species-specific drought tolerance or sub-pixel heterogeneity in land cover. Third, the spatial transferability of the VPD signal, while stronger than that of soil moisture and temperature, remains modest, with region-level precision rarely exceeding 0.12. This suggests that region-specific calibration or the inclusion of land-cover, soil-type and plant-functional-type information may be necessary for operational deployment.

Several limitations should be considered. Our analysis is restricted to the Australian continent, where semi-arid ecosystems dominate and climate–vegetation coupling may be stronger than in energy-limited or disturbance-dominated biomes. Quality filtering of MODIS observations removes cloudy, smoky and aerosol-contaminated periods, which systematically excludes observations during active fire seasons and monsoon periods when vegetation stress may be most acute. Our stress-event definition relies on a fixed EVI anomaly percentile; alternative definitions based on absolute EVI thresholds, cumulative-deficit approaches or multi-sensor composites may yield different event catalogues. The use of the full 26-year record for climatology estimation means that test-year observations contribute to the anomaly baseline in the current temporal holdout; a leakage-removed version in which climatologies are estimated exclusively from training years should be evaluated as a sensitivity analysis before publication. FLUXNET site-level ecosystem-function validation was designed into the pipeline but could not be completed within this study; including such validation would strengthen the ecological interpretation of the discovered precursor states.

The broader contribution of this work is the reproducible, grid-aligned methodology rather than any single precursor claim. By requiring that MODIS and ERA5 data share one pixel grid before analysis proceeds, we eliminate a subtle but pervasive source of spatial misalignment. The full analysis pipeline—from GEE data export through quality filtering, anomaly computation, feature construction, baseline comparison, validation and readiness assessment—is version-controlled and designed to be re-run with different spatial domains, anomaly thresholds or model configurations. The core finding is not that VPD or soil moisture precede vegetation stress (which is ecologically expected) but rather that climate-only precursors, while capturing a majority of stress events, generate unacceptably high false-alarm rates for operational early warning. This finding refocuses attention toward the integration of vegetation-memory, land-cover and ecological-context information as necessary complements to climate-based precursors.

### Materials and Methods

#### Data sources and shared-grid preprocessing

MODIS Terra (MOD13Q1 v061) and Aqua (MYD13Q1 v061) 16-day vegetation-index products were accessed via Google Earth Engine[13] and exported as GeoTIFF files on a unified 0.25° geographic grid (EPSG:4326) spanning 109.75°E–150.25°E, 40.25°S–10.00°S (162 × 121 pixels). The MODIS products natively use a sinusoidal projection at ~250 m resolution; the GEE export pipeline reprojects both MODIS and ERA5 data to the shared grid at export time using a bilinear resampling kernel. Quality filtering was performed within GEE using the VI Quality (SummaryQA) bitmask as follows: MODLAND QA bits 0–1 ≤ 1, VI usefulness bits 2–5 ≤ 11, aerosol quantity bits 6–7 ≤ 1, adjacent cloud detected (bit 8) = 0, mixed cloud (bit 10) = 0, possible snow/ice (bit 14) = 0, possible shadow (bit 15) = 0. The pre-computed binary quality flag `qa_ok` is exported as a separate band for each observation date.

ERA5-Land hourly climate reanalysis[7] was accessed via the same GEE instance and exported on the identical spatial grid at 16-day compositing resolution. For each 16-day window (23 windows per year, matching the MODIS MOD13Q1/MYD13Q1 composite schedule with day-of-year starts at 1, 17, 33, …, 353), window means were computed for 2 m temperature (K), dewpoint temperature (K), volumetric soil water layer 1 (m³/m³) and volumetric soil water layer 2 (m³/m³); window sums were computed for total precipitation (m) and surface net solar radiation (J/m²). VPD (kPa) was computed in GEE from the window-mean temperature and dewpoint temperature using the Magnus formula: es = 0.6108 × exp(17.27 × Tc / (Tc + 237.3)), ea = 0.6108 × exp(17.27 × Td / (Td + 237.3)), VPD = max(0, es – ea), where Tc and Td are in degrees Celsius. Soil moisture was defined as the mean of layers 1 and 2 after window averaging. Twenty-six annual GeoTIFF files were produced for MODIS (2000–2025) and 26 for ERA5 (2000–2025).

#### Grid-alignment audit

An automated audit script (`audit_gee_grid_alignment.py`) verified that all 52 exported GeoTIFF files share identical CRS (EPSG:4326), affine transform ([0.25, 0, 109.75, 0, –0.25, –10.00]), width (162 pixels) and height (121 pixels). The audit must return `PASS_SHARED_GRID` before any downstream merging or analysis is permitted. This step ensures that pixel identifiers of the form `p{row}c{col}` carry consistent spatial meaning across the MODIS and ERA5 datasets.

#### Vegetation anomaly and event definition

EVI and NDVI values exported by GEE as scaled integers (0–10,000) were converted to physical units using the MODIS scale factor (0.0001). Pixel-level EVI day-of-year climatologies (mean and standard deviation) were computed from the full 26-year quality-filtered record. For each observation, the EVI anomaly was defined as the departure from the pixel`s day-of-year climatological mean. Observations falling below the pixel-level 10th percentile of the anomaly distribution were considered candidate stress observations. A vegetation-stress event was defined at any pixel where the EVI anomaly fell below the 10th percentile for at least two consecutive 16-day compositing periods. Anomaly computation was repeated for NDVI as a secondary sensitivity check. Threshold sensitivity was assessed by repeating the event catalogue at the 5th, 10th, 15th and 20th anomaly percentiles.

#### Climate precursor features

For each 16-day compositing window, anomaly values for all five climate variables were computed relative to the pixel-level climatology (full 26-year record), then shifted to lead times of 16, 32, 48 and 64 days before the stress-observation window. Negative lead-time values (future information relative to the target observation) were excluded. This produced 20 lagged anomaly features (5 variables × 4 lead times). Dewpoint temperature was used only in the VPD calculation and was not included as a separate predictor.

#### Model evaluation and baselines

Candidate precursors were ranked by the absolute value of the point-biserial correlation between each lagged climate anomaly and the binary stress-event label. Baseline models were implemented as follows: (1) majority-class predictor (always predict non-stress); (2) training-set prevalence; (3) persistence of the previous event at the same pixel (i.e. predict stress if the previous 16-day window at the same pixel contained a stress event); (4) single-variable threshold classifiers using the training-set median as the decision boundary for each of the 20 lagged features; (5) variable-family threshold classifiers combining all four lead times for a single variable (VPD-only, temperature-only, precipitation-only, soil-moisture-only) using the training-set family median; (6) a compound heat–drought threshold classifier combining temperature features with precipitation and soil-moisture features.

Primary evaluation metrics are precision (positive predictive value), recall (sensitivity), false-alarm rate (false positives / total negatives) and accuracy, reported separately for training and holdout sets. We emphasise that for imbalanced event-detection problems with low base rates (~7%), accuracy is dominated by the majority class and provides limited discrimination; precision and recall at the pixel-window level are the primary metrics of interest. Performance is reported at the pixel–window level; event-level aggregation and PR-AUC computation are reserved for the next analysis iteration.

#### Temporal and spatial validation

Temporal holdout reserved the most recent 20% of years (2019–2025) for evaluation. All anomaly thresholds, climatologies and model parameters were estimated from the training period (2000–2018). Notably, in the current pipeline, the EVI anomaly climatology and percentile thresholds were computed from the full 26-year record; a leakage-removed version in which these reference statistics are estimated exclusively from training years is planned as a sensitivity analysis. Spatial holdout used a leave-one-region-out design across 20 contiguous regions derived from the regular grid structure by grouping adjacent pixel rows and columns into blocks of approximately equal size. For each held-out region, models were trained on the remaining 19 regions and evaluated on the held-out region.

#### Robustness checks

A shuffled-lag placebo test randomly permuted the lag assignments of climate features (while preserving the feature value distributions) and compared the resulting point-biserial correlations against the true values. Threshold sensitivity was assessed by repeating the event catalogue at anomaly percentiles of 5%, 10%, 15% and 20%. All random seeds were fixed (seed = 42) to ensure reproducibility.

#### Use of AI-assisted tools

AI-assisted coding and language tools (OpenAI Codex, GPT-5) were used to support code refactoring, pipeline automation and manuscript editing. All scientific analyses, methodological decisions, result interpretation and final text were verified and approved by the author. No AI-generated content was included without human review.


**Keywords**: MODIS; ERA5-Land; vegetation index; climate precursor; vapour pressure deficit; soil moisture; early warning; Australia; spatial grid alignment; false alarm ratio
---


## Conclusions

This study presents a reproducible, grid-aligned framework for discovering climate precursors of satellite-observed vegetation stress across Australia. Using 26 years of MODIS EVI anomalies and ERA5-Land climate reanalysis on a unified 0.25° grid, we demonstrate that soil-moisture deficit and VPD excess at 16–32 day lead times are the dominant precursor signals. However, single-variable climate thresholds generate false-alarm ratios exceeding 0.94 and negative skill scores relative to the majority-class baseline—only the persistence of a previous stress event achieves a positive skill score (0.319). Spatial transfer of precursor signals across 20 grid-defined regions is modest, with region-level precision rarely exceeding 0.12 for the best-performing VPD precursor.

These findings carry two implications for satellite-based vegetation stress early warning. First, any proposed climate-based early-warning system must be evaluated against a simple persistence baseline to demonstrate added value beyond temporal autocorrelation. Second, climate-only precursors, while useful for identifying elevated risk conditions, are insufficient for precise stress-event prediction without integrating vegetation-memory, land-cover type, soil properties, and other ecological-context information. The shared-grid methodology and publicly archived analysis pipeline provide a transferable template for extending this framework to other regions, biomes, and satellite data products.
## References

1. Reichstein, M. et al. Deep learning and process understanding for data-driven Earth system science. *Nature* **566**, 195–204 (2019). DOI: 10.1038/s41586-019-0912-1.

2. Seneviratne, S. I. et al. Investigating soil moisture–climate interactions in a changing climate: A review. *Earth-Science Reviews* **99**, 125–161 (2010). DOI: 10.1016/j.earscirev.2010.02.004.

3. Allen, C. D., Breshears, D. D. & McDowell, N. G. On underestimation of global vulnerability to tree mortality and forest die-off from hotter drought in the Anthropocene. *Ecosphere* **6**, art129 (2015). DOI: 10.1890/ES15-00203.1.

4. McDowell, N. G. et al. Mechanisms of woody-plant mortality under rising drought, CO2 and vapour pressure deficit. *Nature Reviews Earth & Environment* **3**, 294–308 (2022). DOI: 10.1038/s43017-022-00272-1.

5. Huete, A. et al. Overview of the radiometric and biophysical performance of the MODIS vegetation indices. *Remote Sensing of Environment* **83**, 195–213 (2002). DOI: 10.1016/S0034-4257(02)00096-2.

6. Didan, K. MOD13Q1 v061: MODIS/Terra Vegetation Indices 16-Day L3 Global 250 m SIN Grid. NASA LP DAAC (2015). DOI: 10.5067/MODIS/MOD13Q1.061.

7. Muñoz-Sabater, J. et al. ERA5-Land: a state-of-the-art global reanalysis dataset for land applications. *Earth System Science Data* **13**, 4349–4383 (2021). DOI: 10.5194/essd-13-4349-2021.

8. Hao, Z. & Singh, V. P. Drought characterization from a multivariate perspective: A review. *Journal of Hydrology* **527**, 668–678 (2015). DOI: 10.1016/j.jhydrol.2015.05.031.

9. Shen, C. et al. Differentiable modelling to unify machine learning and physical models for geosciences. *Nature Reviews Earth & Environment* **4**, 552–567 (2023). DOI: 10.1038/s43017-023-00450-9.

10. Barnes, E. A. et al. Indicator patterns of forced change learned by an artificial neural network. *Journal of Advances in Modeling Earth Systems* **12**, e2020MS002165 (2020). DOI: 10.1029/2020MS002165.

11. Grossiord, C. et al. Plant responses to rising vapor pressure deficit. *New Phytologist* **226**, 1550–1566 (2020). DOI: 10.1111/nph.16485.

12. Zhou, S., Williams, A. P., Lintner, B. R., Berg, A. M. & Gentine, P. Large and persistent soil carbon losses from the 2011 Texas drought. *Nature Geoscience* **12**, 943–949 (2019). DOI: 10.1038/s41561-019-0460-1.

13. Gorelick, N. et al. Google Earth Engine: Planetary-scale geospatial analysis for everyone. *Remote Sensing of Environment* **202**, 18–27 (2017). DOI: 10.1016/j.rse.2017.06.031.

14. Pastorello, G. et al. The FLUXNET2015 dataset and the ONEFlux processing pipeline for eddy covariance data. *Scientific Data* **7**, 225 (2020). DOI: 10.1038/s41597-020-0534-3.

---

## Data availability

MODIS MOD13Q1 and MYD13Q1 products are publicly available through the NASA Land Processes Distributed Active Archive Center (LP DAAC). ERA5-Land hourly data are publicly available through the Copernicus Climate Data Store (CDS). Both datasets were accessed and processed via Google Earth Engine. The shared-grid GeoTIFF exports and analysis-ready CSV tables supporting this study are available from the corresponding author upon reasonable request.

## Code availability

Analysis code is version-controlled in a public GitHub repository and archived on Zenodo with a persistent DOI. The repository includes GEE export scripts (JavaScript), local Python preprocessing and conversion scripts, the `nature_climate_ai` Python package providing all CLI entry points, configuration files, and a README with one-command reproduction instructions. Environment dependencies are specified in `requirements.txt`.

## Acknowledgements

The author gratefully acknowledges the following data providers and platforms. MODIS vegetation index products (MOD13Q1 v061, MYD13Q1 v061) were obtained from the NASA LP DAAC and accessed via Google Earth Engine. ERA5-Land hourly climate reanalysis was provided by ECMWF through the Copernicus CDS and processed on Google Earth Engine. FLUXNET eddy covariance data were provided by the FLUXNET community. Google Earth Engine (Gorelick et al., 2017) provided the cloud computing platform.

## Author contributions

Z.W. conceived the study, curated all datasets, developed the methodology, wrote all software and analysis scripts, performed the formal analysis, drafted the manuscript and approved the final version.

## Competing interests

The author declares no competing interests.

---

*Manuscript draft v2, revised 2026-06-08. Target journal: regional-scale ecological remote sensing / environmental data science.*
