# Interpretable Discovery of Lagged Climate Precursors for Vegetation-Index Stress across Australia

Zhuoxian Wu (吴卓宪)

Guangdong Neusoft Institute of Technology / 广东东软学院 NUIT

---

## Abstract

Satellite vegetation records now span multiple decades, yet the extent to which lagged climate anomalies can serve as interpretable early-warning precursors of vegetation stress—and the limits of such precursors—remains poorly quantified at continental scale. Here we construct a reproducible discovery framework that aligns 26 years (2000–2025) of quality-filtered MODIS vegetation-index anomalies with ERA5-Land climate reanalysis on a unified 0.25° grid across Australia. Vegetation-stress events are defined from pixel-level EVI anomaly climatologies, and 20 lagged climate predictors spanning soil moisture, vapour pressure deficit (VPD), temperature, precipitation, and surface radiation at lead times of 16 to 64 days are evaluated. Soil-moisture deficit and VPD excess emerge as the dominant precursor signals, with the strongest separation between stress and non-stress conditions occurring at 16–32 day lead times. However, even the best-performing single climate precursor (VPD at 16-day lag) achieves only modest precision (0.055) while detecting 61% of stress events on held-out years, and spatial transfer of precursor signals across 20 grid-defined regions exhibits substantial inter-regional variability. A shuffled-lag placebo test and threshold-sensitivity analysis confirm the robustness of the discovered patterns, while comparison against a simple persistence baseline—which achieves precision of 0.659 and recall of 0.661—reveals that knowledge of a pixel''s recent stress history outperforms any single climate variable. The persistence baseline achieves a skill score of 0.660 (SS = (F1 − F1_majority) / (1 − F1_majority)), substantially exceeding the best climate-only precursor (VPD family, skill score 0.115). These results indicate that climate precursors are useful for identifying elevated risk conditions but are insufficient for precise stress-event prediction without vegetation-memory and ecological-context information. The analysis framework is fully reproducible: all data exports, preprocessing scripts, model configurations, and validation outputs are version-controlled on a shared spatial grid and archived with a permanent DOI.

**Keywords**: MODIS; ERA5-Land; vegetation index; climate precursor; vapour pressure deficit; soil moisture; early warning; Australia; spatial grid alignment; false alarm ratio

---

## 1. Introduction

Terrestrial ecosystems modulate carbon, water, and energy exchanges at continental to global scales, but their capacity to do so is increasingly disrupted by compound climate extremes [1,2]. Heatwaves, droughts, and elevated atmospheric water demand can interact nonlinearly, transforming short meteorological anomalies into persistent vegetation stress that reduces gross primary productivity, alters surface energy partitioning, and, in severe cases, triggers widespread mortality [3,4]. Satellite vegetation indices from the Moderate Resolution Imaging Spectroradiometer (MODIS) now provide more than two decades of near-daily observations of canopy greenness [5,6], and when combined with multi-decadal climate reanalysis products such as ERA5-Land [7], these records permit systematic examination of the climate conditions that precede satellite-observed vegetation stress.

Current operational drought and heat-stress monitoring relies predominantly on single-variable indices such as the Standardized Precipitation-Evapotranspiration Index (SPEI) or temperature-percentile thresholds [8]. These indices provide essential situational awareness but typically describe stress after it has accumulated, rather than identifying the specific multi-variable precursor states that elevate the probability of vegetation stress at sub-seasonal lead times. Recent work has demonstrated that machine-learning methods can improve sub-seasonal drought forecasting [9,10], but three gaps persist. First, many studies treat satellite vegetation indices and reanalysis climate data as if they share a common spatial grid, when in practice their native projections and resolutions differ—a misalignment that can produce spurious spatial correlations. Second, discovered climate precursors are rarely compared against simple temporal baselines such as the persistence of a previous stress event, making it difficult to assess whether the precursor adds value beyond temporal autocorrelation. Third, the spatial transferability of discovered precursors—whether a signal learned in one region holds in another—is seldom tested with the same rigour as temporal holdout.

Here we address these gaps with an interpretable discovery framework that (1) defines vegetation-stress events from quality-filtered, gridded MODIS EVI anomalies on a unified 0.25-degree grid, (2) constructs lagged climate features from ERA5-Land at leads of 16, 32, 48, and 64 days, (3) ranks candidate precursors by their ability to discriminate stress from non-stress conditions, (4) systematically evaluates the discovered patterns against temporal holdout, spatial holdout, a persistence baseline, single-variable climate thresholds, and a shuffled-lag placebo test, and (5) assesses sensitivity to the stress-threshold definition. A central methodological requirement is that MODIS and ERA5 data must reside on the same pixel grid before any analysis proceeds—an automated grid-alignment audit verifies this condition for every exported file.

## 2. Materials and Methods

### 2.1 Data Sources and Shared-Grid Preprocessing

MODIS Terra (MOD13Q1 v061) and Aqua (MYD13Q1 v061) 16-day vegetation-index products were accessed via Google Earth Engine [11] and exported as GeoTIFF files on a unified 0.25-degree geographic grid (EPSG:4326) spanning 109.75°E–150.25°E, 40.25°S–10.00°S (162 × 121 pixels). The MODIS products natively use a sinusoidal projection at approximately 250 m resolution; the GEE export pipeline reprojects both MODIS and ERA5 data to the shared grid at export time. Quality filtering was performed within GEE using the VI Quality (SummaryQA) bitmask prior to spatial aggregation: only MODIS pixels satisfying the QA criteria were retained, and grid-cell EVI/NDVI values were aggregated to the 0.25° grid using the mean of valid observations (ee.Reducer.mean()). ERA5 continuous fields were resampled using bilinear interpolation. The QA criteria were: MODLAND QA bits 0–1 ≤ 1, VI usefulness bits 2–5 ≤ 11, aerosol quantity bits 6–7 ≤ 1, adjacent cloud detected (bit 8) = 0, mixed cloud (bit 10) = 0, possible snow/ice (bit 14) = 0, possible shadow (bit 15) = 0. The pre-computed binary quality flag qa_ok was exported as a separate band for each observation date.

ERA5-Land hourly climate reanalysis [7] was accessed via the same GEE instance and exported on the identical spatial grid at 16-day compositing resolution. For each 16-day window (23 windows per year, matching the MODIS MOD13Q1/MYD13Q1 composite schedule with day-of-year starts at 1, 17, 33, …, 353), window means were computed for 2 m temperature (K), dewpoint temperature (K), volumetric soil water layer 1 (m³/m³), and volumetric soil water layer 2 (m³/m³); window sums were computed for total precipitation (m) and surface net solar radiation (J/m²). VPD (kPa) was computed in GEE from the window-mean temperature and dewpoint temperature using the Magnus formula: es = 0.6108 × exp(17.27 × Tc / (Tc + 237.3)), ea = 0.6108 × exp(17.27 × Td / (Td + 237.3)), VPD = max(0, es – ea), where Tc and Td are in degrees Celsius. Soil moisture was defined as the mean of layers 1 and 2 after window averaging. Twenty-six annual GeoTIFF files were produced for MODIS (2000–2025) and 26 for ERA5 (2000–2025).

### 2.2 Grid-Alignment Audit

An automated audit script verified that all 52 exported GeoTIFF files share identical CRS (EPSG:4326), affine transform ([0.25, 0, 109.75, 0, –0.25, –10.00]), width (162 pixels), and height (121 pixels). The audit must return PASS_SHARED_GRID before any downstream merging or analysis is permitted. This step ensures that pixel identifiers of the form p{row}c{col} carry consistent spatial meaning across the MODIS and ERA5 datasets.

### 2.3 Vegetation Anomaly and Event Definition

EVI and NDVI values exported by GEE as scaled integers (0–10,000) were converted to physical units using the MODIS scale factor (0.0001). Pixel-level EVI day-of-year climatologies (mean and standard deviation) were computed exclusively from the training period (2000–2018), ensuring that no information from the temporal holdout set (2019–2025) entered anomaly computation. For each observation, the EVI anomaly was defined as the departure from the pixel''s day-of-year climatological mean. Observations falling below the pixel-level 10th percentile of the anomaly distribution were considered candidate stress observations. A vegetation-stress event was defined at any pixel where the EVI anomaly fell below the 10th percentile for at least two consecutive 16-day compositing periods. Anomaly computation was repeated for NDVI as a secondary sensitivity check. Threshold sensitivity was assessed by repeating the event catalogue at the 5th, 10th, 15th, and 20th anomaly percentiles. A leakage-sensitivity analysis comparing training-only climatologies with full-period climatologies confirmed that the difference is negligible (mean EVI anomaly difference < 0.005), and the training-only version is used throughout the main analysis. The full-period climatology option is available through the --climatology-yrs flag in the analysis CLI as a sensitivity check.

### 2.4 Climate Precursor Features

For each 16-day compositing window, anomaly values for all five climate variables were computed relative to the pixel-level climatology, then shifted to lead times of 16, 32, 48, and 64 days before the stress-observation window. Negative lead-time values (future information relative to the target observation) were excluded. This procedure produced 20 lagged anomaly features (5 variables × 4 lead times). Dewpoint temperature was used only in the VPD calculation and was not included as a separate predictor.

### 2.5 Model Evaluation and Baselines

Candidate precursors were ranked by the absolute value of the point-biserial correlation between each lagged climate anomaly and the binary stress-event label. Baseline models were implemented as follows: (1) majority-class predictor (always predict non-stress); (2) training-set prevalence; (3) persistence of the previous event at the same pixel (predict stress if the previous 16-day window at the same pixel contained a stress event); (4) single-variable threshold classifiers using the training-set median as the decision boundary for each of the 20 lagged features; (5) variable-family threshold classifiers combining all four lead times for a single variable (VPD-only, temperature-only, precipitation-only, soil-moisture-only) using the training-set family median; and (6) a compound heat–drought threshold classifier combining temperature features with precipitation and soil-moisture features.

Primary evaluation metrics were precision (positive predictive value), recall (sensitivity), false-alarm ratio (false positives / total predicted positives), F1-score, and PR-AUC. A skill score SS = (S − S_majority) / (1 − S_majority) was used for baseline comparison, where S denotes the evaluation metric (F1-score in the main analysis); SS = 0 indicates performance equal to the majority baseline and SS = 1 corresponds to perfect classification. All metrics were reported separately for training and holdout sets. We emphasise that for imbalanced event-detection problems with low base rates (~7%), accuracy is dominated by the majority class; precision, recall, and false-alarm ratio at the pixel–window level are the primary metrics of interest.

### 2.6 Machine-Learning Models

To assess whether non-linear models improve upon single-variable climate thresholds, Random Forest (100 estimators, max depth = 10, balanced class weights proportional to inverse training-set prevalence) and XGBoost (100 estimators, max depth = 6, scale\_pos\_weight set to the inverse of the training-set positive rate, learning rate = 0.1) classifiers were trained on the full training set using all 20 lagged climate anomaly features. No hyperparameter tuning was performed beyond class balancing; default scikit-learn and XGBoost parameters were used otherwise. SHAP (SHapley Additive exPlanations) values were computed using TreeExplainer on a stratified random sample of 5,000 holdout observations (balanced across stress and non-stress classes) to rank feature contributions. Both models were evaluated on the temporal holdout set (2019–2025) using the same metrics as the threshold-based baselines. No early stopping or calibration was applied.

### 2.7 Temporal and Spatial Validation

Temporal holdout reserved the most recent 20% of years (2019–2025) for evaluation. All anomaly thresholds, climatologies, and model parameters were estimated from the training period (2000–2018). Spatial holdout used a leave-one-region-out design across 20 contiguous regions derived from the regular grid structure by grouping adjacent pixel rows and columns into blocks of approximately equal size. For each held-out region, models were trained on the remaining 19 regions and evaluated on the held-out region.

### 2.7 Robustness Checks

A shuffled-lag placebo test randomly permuted the lag assignments of climate features (while preserving the feature value distributions) and compared the resulting point-biserial correlations against the true values. Threshold sensitivity was assessed by repeating the event catalogue at anomaly percentiles of 5%, 10%, 15%, and 20%. All random seeds were fixed (seed = 42) to ensure reproducibility.

### 2.8 Use of AI-Assisted Tools

AI-assisted coding and language tools (OpenAI Codex, GPT-5) were used to support code refactoring, pipeline automation, and manuscript editing. All scientific analyses, methodological decisions, result interpretation, and final text were verified and approved by the author. No AI-generated content was included without human review.

## 3. Results

### 3.1 Vegetation-Stress Event Catalogue

We analysed 22,267,872 MODIS vegetation-index observations from Terra (MOD13Q1 v061) and Aqua (MYD13Q1 v061) 16-day composite products spanning 2000–2025 across the Australian continent. Strict quality filtering using the MODIS VI Quality bitmask retained 11,608,373 observations (52.1%) across 10,766 terrestrial 0.25-degree grid cells. Pixel-level EVI day-of-year climatologies were computed from the quality-filtered record, and negative anomalies exceeding the 10th percentile that persisted for at least two consecutive 16-day compositing periods were flagged as vegetation-stress events (Figure 2). This procedure yielded 1,438,750 anomaly records and a modelling-eligible sample of 7,287,280 rows, of which 503,743 (6.9%) carried positive stress-event labels.

### 3.2 Climate Precursor Features

Twenty lagged climate predictors were constructed from ERA5-Land hourly reanalysis, aggregated into the same 16-day compositing windows as the MODIS data: 2 m temperature, total precipitation, soil moisture (mean of volumetric soil water layers 1 and 2), surface net solar radiation, and VPD (computed in GEE from window-mean temperature and dewpoint temperature). Anomalies were computed relative to each pixel''s 26-year climatology and shifted to lead times of 16, 32, 48, and 64 days, producing 20 lagged anomaly features. All features were aligned to vegetation observations without using future information relative to each observation row.

### 3.3 Discovery of Precursor Signals

Feature-attribution analysis ranked all 20 lagged climate predictors by their absolute point-biserial correlation with the binary stress-event label (Figure 3). Soil-moisture deficit at 16-day lag was the strongest single predictor (|r| = 0.210), followed by soil moisture at 32-day lag (|r| = 0.206) and VPD excess at 32-day lag (|r| = 0.163). The predictive signal decayed monotonically with increasing lead time: soil-moisture correlation dropped from 0.210 at 16 days to 0.169 at 64 days, and VPD correlation dropped from 0.163 at 32 days to 0.144 at 64 days. Stress-event windows were characterised by soil-moisture anomalies approximately 0.03 units below climatology and VPD anomalies approximately 0.30 kPa above climatology relative to non-stress windows.

### 3.4 Predictive Validation against Baselines

We evaluated the discovered precursor signals against a suite of baselines on a temporal holdout comprising the most recent 20% of years (Figure 4). The persistence baseline—predicting a stress event whenever the previous 16-day window contained a stress event at the same pixel—achieved precision of 0.659 and recall of 0.661, yielding an F1-based skill score of 0.660 relative to the majority-class baseline and establishing a strong temporal benchmark. The majority-class baseline (always predict non-stress) achieved accuracy of 0.962, reflecting a stress-event prevalence of approximately 3.8% in the holdout set (lower than the full-period prevalence of 6.9% reported in Section 3.1).

Among single-variable threshold models, VPD at 16-day lag achieved the highest recall on held-out years (0.609) but with precision of only 0.055 and a false-alarm ratio of 0.945. A multi-lag VPD family model combining all four lead times improved recall to 0.737 at the cost of slightly lower precision (0.062). Soil-moisture deficit at 16-day lag achieved recall of 0.181 and precision of 0.014. Temperature-based and precipitation-based thresholds performed substantially worse than VPD and soil moisture across all lead times. Compound heat–drought thresholds combining temperature and moisture variables achieved recall of 0.693, comparable to the VPD family model, but with precision of only 0.049. All climate-threshold models exhibited skill scores substantially below that of the persistence baseline (best climate SS = 0.115 vs. persistence SS = 0.660), reflecting the trade-off between higher recall and far lower precision relative to the simple temporal-autocorrelation benchmark.

### 3.5 Spatial Transfer and Robustness

Spatial holdout validation across 20 contiguous grid-defined regions tested whether precursor–stress relationships discovered in some regions transfer to held-out regions (Figure 5). Mean spatial-holdout recall for VPD at 16-day lag was 0.618 (range 0.537–0.676 across regions), and mean precision was 0.092. Soil-moisture deficit showed more variable spatial transfer (mean recall 0.167, range 0.143–0.239 across regions). The VPD signal transferred more consistently than soil moisture or temperature, suggesting that atmospheric moisture demand is a more spatially coherent precursor of vegetation-index stress than surface soil moisture in the Australian domain.

A shuffled-lag placebo test confirmed that the observed precursor associations exceed random noise. Threshold-sensitivity analysis across the 5th to 20th anomaly percentiles showed that the ranking of precursor candidates was stable, although absolute performance metrics varied with the chosen threshold.


### 3.6 Machine-Learning Model Comparison

To assess whether non-linear machine-learning (ML) models can improve upon single-variable climate thresholds, we trained Random Forest (100 estimators, max depth = 10, balanced class weights) and XGBoost (100 estimators, max depth = 6, scale-positive-weight, learning rate = 0.1) classifiers on the full 5,282,200-row training set using all 20 lagged climate anomaly features. Models were evaluated on the 2,005,080-row temporal holdout set (2019–2025). The persistence baseline and the best single-variable threshold (VPD at 16-day lag) are included for comparison (Table 1).

**Table 1.** Performance of ML models versus baseline predictors on the temporal holdout set.

| Model | Precision | Recall | False Alarm Ratio |
|-------|:---------:|:------:|:------------------:|
| VPD 16d (single-variable threshold) | 0.055 | 0.609 | 0.945 |
| Persistence (previous event) | 0.659 | 0.661 | 0.341 |
| Random Forest (100 trees) | 0.185 | 0.797 | 0.815 |
| XGBoost (100 trees) | 0.191 | 0.791 | 0.809 |

Both ML models substantially improved recall relative to the best single-variable threshold (from 0.609 to ~0.79), detecting approximately 80% of vegetation-stress events. Precision improved by a factor of 3.4 (from 0.055 to ~0.19), and the false-alarm ratio decreased from 0.945 to ~0.81. Nevertheless, the persistence baseline retained the highest precision (0.659), and all climate-based models—including the ML classifiers—exhibited false-alarm ratios exceeding 0.80, confirming that climate-only predictors, even when combined non-linearly, generate many false positives relative to observed stress events.

SHAP (SHapley Additive exPlanations) analysis of the XGBoost model on a 5,000-row holdout sample identified soil-moisture anomaly at 16-day lag as the dominant feature (SHAP importance = 0.519), followed by soil moisture at 32-day lag (0.370), 64-day lag (0.279), and 48-day lag (0.209). Vapour-pressure-deficit anomaly at 16-day lag ranked fifth (0.153), confirming that soil-moisture deficits are the most informative features for the ML model, consistent with the point-biserial correlation ranking.

### 3.7 Latitude-Zone Stratification

To evaluate whether predictive performance varies across climate zones, we stratified the holdout set into three latitude bands corresponding to broad climatic regions of Australia: North (tropical, ~10–20°S), Central (subtropical, ~20–30°S), and South (temperate, ~30–40°S). Separate XGBoost models were trained and evaluated for each zone (Table 2).

**Table 2.** XGBoost performance by latitude zone on the temporal holdout set.

| Zone | Samples | Stress Rate | Precision | Recall | FAR |
|------|:-------:|:-----------:|:---------:|:------:|:---:|
| North (~10–20°S, tropical) | 445,842 | 6.3% | 0.180 | 0.864 | 0.820 |
| Central (~20–30°S, subtropical) | 1,064,850 | 8.6% | 0.199 | 0.797 | 0.801 |
| South (~30–40°S, temperate) | 494,388 | 6.2% | 0.181 | 0.682 | 0.819 |

The central subtropical zone—which encompasses much of Australia''s arid and semi-arid interior—exhibited the highest precision (0.199) and lowest false-alarm ratio (0.801), consistent with stronger climate–vegetation coupling in water-limited ecosystems. The northern tropical zone achieved the highest recall (0.864) but with lower precision, suggesting that climate stress signals are widespread but less specific in tropical savanna regions. The southern temperate zone showed the lowest recall (0.682), indicating that vegetation stress in cooler, energy-limited systems may be driven by non-climatic factors (e.g., frost, fire) to a greater extent than in water-limited regions.

## 4. Discussion

Our results establish that interpretable climate precursor signals can be systematically discovered from satellite vegetation records and reanalysis data on a unified spatial grid. The dominant precursor signals—soil-moisture deficit and VPD excess at 16–32 day lead times—are consistent with known ecohydrological mechanisms [12,13], and the decay of predictive signal with increasing lead time suggests that the actionable precursor window in this domain is approximately two to four weeks.

Three findings carry particular implications for satellite-based vegetation stress early warning. First, the persistence baseline is strikingly strong: knowledge of whether a pixel experienced stress in the previous 16-day window already captures two-thirds of future stress events, achieving an F1-based skill score of 0.660—approximately six times that of the best climate-only precursor (VPD family, 0.115). This reflects the slow recovery of water-limited ecosystems after drought onset and implies that any proposed climate-based early-warning system must be benchmarked against persistence to demonstrate added value beyond temporal autocorrelation. Second, the false-alarm ratio of even the best single-variable climate precursor exceeds 0.94: VPD thresholds that detect 61% of stress events also flag approximately 41% of non-stress windows as potential precursors, meaning that over nine in ten positive predictions are false alarms. This trade-off between sensitivity and specificity may be irreducible for purely climate-driven precursors—many vegetation-stress events have non-climatic drivers (fire, disease, land-use change, insect outbreaks) that no climate precursor can anticipate, and the converse case (elevated VPD that does not produce visible canopy stress) may reflect vegetation acclimation, species-specific drought tolerance, or sub-pixel heterogeneity in land cover. Third, the spatial transferability of the VPD signal, while stronger than that of soil moisture and temperature, remains modest, with region-level precision rarely exceeding 0.12. This finding suggests that region-specific calibration or the inclusion of land-cover, soil-type, and plant-functional-type information is likely necessary for operational deployment.

Several limitations should be acknowledged. Our analysis is restricted to the Australian continent, where semi-arid ecosystems dominate and climate–vegetation coupling may be stronger than in energy-limited or disturbance-dominated biomes. Quality filtering of MODIS observations removes cloudy, smoky, and aerosol-contaminated periods, which systematically excludes observations during active fire seasons and monsoon periods when vegetation stress may be most acute. Our stress-event definition relies on a fixed EVI anomaly percentile; alternative definitions based on absolute EVI thresholds, cumulative-deficit approaches, or multi-sensor composites may yield different event catalogues. Latitude-zone stratification is a coarse proxy for climate regime; future work should incorporate aridity indices, MODIS land-cover classes (MCD12Q1), and plant functional type information for ecologically informed stratification. FLUXNET site-level ecosystem-function validation was designed into the pipeline but could not be completed within this study; its inclusion would strengthen the ecological interpretation of the discovered precursor states.

The broader contribution of this work is the reproducible, grid-aligned methodology rather than any single precursor claim. By requiring that MODIS and ERA5 data share one pixel grid before analysis proceeds, we eliminate a subtle but pervasive source of spatial misalignment that affects large-scale remote-sensing studies. The full analysis pipeline—from GEE data export through quality filtering, anomaly computation, feature construction, baseline comparison, validation, and figure generation—is version-controlled and archived with a permanent DOI. The core finding is not that VPD or soil moisture precede vegetation stress, which is ecologically expected, but rather that climate-only precursors, while capturing a majority of stress events, generate unacceptably high false-alarm ratios for operational early warning. This finding refocuses attention toward integrating vegetation-memory, land-cover, and ecological-context information as necessary complements to climate-based precursors.

## 5. Conclusions

This study presents a reproducible, grid-aligned framework for discovering climate precursors of satellite-observed vegetation stress across Australia. Using 26 years of MODIS EVI anomalies and ERA5-Land climate reanalysis on a unified 0.25-degree grid, we demonstrate that soil-moisture deficit and VPD excess at 16–32 day lead times are the dominant precursor signals. However, single-variable climate thresholds generate false-alarm ratios exceeding 0.94 and achieve skill scores (best: VPD family, 0.115) far below that of the persistence baseline (0.660). Spatial transfer of precursor signals across 20 grid-defined regions is modest, with region-level precision rarely exceeding 0.12 for the best-performing VPD precursor.

These findings carry two implications for satellite-based vegetation stress early warning. First, any proposed climate-based early-warning system must be evaluated against a simple persistence baseline to demonstrate added value beyond temporal autocorrelation. Second, climate-only precursors, while useful for identifying elevated risk conditions, are insufficient for precise stress-event prediction without integrating vegetation-memory, land-cover type, soil properties, and other ecological-context information. The shared-grid methodology and publicly archived analysis pipeline provide a transferable template for extending this framework to other regions, biomes, and satellite data products.

---

## References

1. Reichstein, M.; Camps-Valls, G.; Stevens, B.; Jung, M.; Denzler, J.; Carvalhais, N.; Prabhat. Deep learning and process understanding for data-driven Earth system science. *Nature* **2019**, *566*, 195–204. DOI: 10.1038/s41586-019-0912-1.

2. Seneviratne, S.I.; Corti, T.; Davin, E.L.; Hirschi, M.; Jaeger, E.B.; Lehner, I.; Orlowsky, B.; Teuling, A.J. Investigating soil moisture–climate interactions in a changing climate: A review. *Earth-Sci. Rev.* **2010**, *99*, 125–161. DOI: 10.1016/j.earscirev.2010.02.004.

3. Allen, C.D.; Breshears, D.D.; McDowell, N.G. On underestimation of global vulnerability to tree mortality and forest die-off from hotter drought in the Anthropocene. *Ecosphere* **2015**, *6*, art129. DOI: 10.1890/ES15-00203.1.

4. McDowell, N.G.; Sapes, G.; Pivovaroff, A.; Adams, H.D.; Allen, C.D.; Anderegg, W.R.L.; Arend, M.; Breshears, D.D.; Brodribb, T.; Choat, B.; et al. Mechanisms of woody-plant mortality under rising drought, CO2 and vapour pressure deficit. *Nat. Rev. Earth Environ.* **2022**, *3*, 294–308. DOI: 10.1038/s43017-022-00272-1.

5. Huete, A.; Didan, K.; Miura, T.; Rodriguez, E.P.; Gao, X.; Ferreira, L.G. Overview of the radiometric and biophysical performance of the MODIS vegetation indices. *Remote Sens. Environ.* **2002**, *83*, 195–213. DOI: 10.1016/S0034-4257(02)00096-2.

6. Didan, K. MOD13Q1 v061: MODIS/Terra Vegetation Indices 16-Day L3 Global 250 m SIN Grid. NASA LP DAAC, 2015. DOI: 10.5067/MODIS/MOD13Q1.061.

7. Muñoz-Sabater, J.; Dutra, E.; Agustí-Panareda, A.; Albergel, C.; Arduini, G.; Balsamo, G.; Boussetta, S.; Choulga, M.; Harrigan, S.; Hersbach, H.; et al. ERA5-Land: A state-of-the-art global reanalysis dataset for land applications. *Earth Syst. Sci. Data* **2021**, *13*, 4349–4383. DOI: 10.5194/essd-13-4349-2021.

8. Hao, Z.; Singh, V.P. Drought characterization from a multivariate perspective: A review. *J. Hydrol.* **2015**, *527*, 668–678. DOI: 10.1016/j.jhydrol.2015.05.031.

9. Shen, C.; Appling, A.P.; Gentine, P.; Bandai, T.; Gupta, H.; Tartakovsky, A.; Baity-Jesi, M.; Fenicia, F.; Kifer, D.; Li, L.; et al. Differentiable modelling to unify machine learning and physical models for geosciences. *Nat. Rev. Earth Environ.* **2023**, *4*, 552–567. DOI: 10.1038/s43017-023-00450-9.

10. Barnes, E.A.; Hurrell, J.W.; Ebert-Uphoff, I.; Anderson, C.; Anderson, D. Indicator patterns of forced change learned by an artificial neural network. *J. Adv. Model. Earth Syst.* **2020**, *12*, e2020MS002165. DOI: 10.1029/2020MS002165.

11. Gorelick, N.; Hancher, M.; Dixon, M.; Ilyushchenko, S.; Thau, D.; Moore, R. Google Earth Engine: Planetary-scale geospatial analysis for everyone. *Remote Sens. Environ.* **2017**, *202*, 18–27. DOI: 10.1016/j.rse.2017.06.031.

12. Grossiord, C.; Buckley, T.N.; Cernusak, L.A.; Novick, K.A.; Poulter, B.; Siegwolf, R.T.W.; Sperry, J.S.; McDowell, N.G. Plant responses to rising vapor pressure deficit. *New Phytol.* **2020**, *226*, 1550–1566. DOI: 10.1111/nph.16485.

13. Zhou, S.; Williams, A.P.; Lintner, B.R.; Berg, A.M.; Gentine, P. Large and persistent soil carbon losses from the 2011 Texas drought. *Nat. Geosci.* **2019**, *12*, 943–949. DOI: 10.1038/s41561-019-0460-1.

14. Pastorello, G.; Trotta, C.; Canfora, E.; Chu, H.; Christianson, D.; Cheah, Y.W.; Poindexter, C.; Chen, J.; Elbashandy, A.; Humphrey, M.; et al. The FLUXNET2015 dataset and the ONEFlux processing pipeline for eddy covariance data. *Sci. Data* **2020**, *7*, 225. DOI: 10.1038/s41597-020-0534-3.

---

## Supplementary Materials

Figure S1: Threshold sensitivity analysis showing the relationship between anomaly percentile threshold and stress-event count. The full analysis pipeline code is archived on GitHub (https://github.com/WUMIKE233/nature-climate-ai) with Zenodo DOI 10.5281/zenodo.14882001. The shared-grid GeoTIFF exports and analysis-ready CSV tables are available from the corresponding author upon reasonable request.

## Author Contributions

Conceptualization, methodology, software, formal analysis, data curation, writing—original draft preparation, writing—review and editing: Z.W. The author has read and agreed to the published version of the manuscript.

## Funding

This research received no external funding.

## Data Availability Statement

MODIS MOD13Q1 and MYD13Q1 products are publicly available through the NASA Land Processes Distributed Active Archive Center (LP DAAC). ERA5-Land hourly data are publicly available through the Copernicus Climate Data Store (CDS). Both datasets were accessed and processed via Google Earth Engine. Analysis code is version-controlled at https://github.com/WUMIKE233/nature-climate-ai and archived on Zenodo (DOI: 10.5281/zenodo.14882001). The shared-grid GeoTIFF exports and analysis-ready CSV tables are available from the corresponding author upon reasonable request.

## Conflicts of Interest

The author declares no conflicts of interest.

---

*Manuscript prepared for submission to Remote Sensing (MDPI). v3, polished 2026-06-08.*
