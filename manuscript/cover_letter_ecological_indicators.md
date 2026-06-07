# Cover Letter

**Journal**: Ecological Indicators (Elsevier)
**Manuscript Title**: Interpretable Discovery of Lagged Climate Precursors for Vegetation-Index Stress across Australia
**Author**: Zhuoxian Wu, Guangdong Neusoft Institute of Technology

---

Dear Editors,

I am pleased to submit our manuscript titled "Interpretable Discovery of Lagged Climate Precursors for Vegetation-Index Stress across Australia" for consideration for publication in *Ecological Indicators*.

**Fit with Ecological Indicators**: This manuscript develops and validates a suite of ecological indicators for satellite-observed vegetation stress?including a persistence-based stress-recurrence indicator, climate-anomaly precursor indicators at multiple lead times (16?64 days), and an F1-based skill score framework for comparing early-warning indicator performance. The study systematically evaluates the sensitivity, specificity, and spatial transferability of these indicators across the Australian continent using 26 years of MODIS vegetation indices and ERA5-Land climate reanalysis. The work directly addresses the journal's scope of "integrating monitoring and assessment of ecological indicators with management practice" by providing a reproducible, grid-aligned framework that can be transferred to other regions and satellite data products.

**What this paper does**: We construct a reproducible framework that enforces identical pixel grids for MODIS and ERA5 data through an automated audit before any analysis proceeds?a methodological safeguard that eliminates spatial misalignment, a pervasive source of error in large-scale ecological remote-sensing studies. Vegetation-stress events are defined from pixel-level EVI anomaly climatologies, and 20 lagged climate predictors spanning soil moisture, vapour pressure deficit (VPD), temperature, precipitation, and surface radiation at leads of 16?64 days are systematically ranked as stress precursor indicators.

**Key ecological indicators and findings**:
1. Soil-moisture deficit and VPD excess at 16?32 day lead times are the dominant climate precursor indicators for vegetation-index stress across Australia, with the predictive signal decaying monotonically with increasing lead time.
2. A simple persistence indicator?whether a pixel experienced stress in the previous 16-day window?achieves precision of 0.659 and recall of 0.661 (F1 = 0.660), substantially exceeding the best climate-only precursor (VPD family, F1 = 0.115).
3. Even the best single-variable climate indicator (VPD at 16-day lag) generates a false-alarm ratio of 0.945, meaning that over nine in ten positive predictions are false alarms.
4. Machine-learning models (Random Forest, XGBoost) improve recall to ~0.79 and precision to ~0.19, but false-alarm ratios remain above 0.80, and the persistence indicator remains the strongest single predictor.
5. Spatial transfer of indicator signals across 20 grid-defined regions is modest, with region-level precision rarely exceeding 0.12, and latitude-zone stratification reveals stronger climate?vegetation coupling in Australia's subtropical interior.

**Novelty and significance**: Three aspects distinguish this work as an ecological indicators contribution. First, the shared-grid methodology with automated audit provides a transferable template for any study that constructs ecological indicators from satellite vegetation products and gridded climate data?an approach that directly addresses indicator reproducibility and comparability, which are central concerns of *Ecological Indicators*. Second, the systematic comparison of climate-only precursor indicators against a simple persistence baseline reveals that the apparent predictive value of climate thresholds largely reflects temporal autocorrelation in vegetation stress?a finding with direct implications for the design and evaluation of satellite-based ecological early-warning indicators. Third, the full indicator construction, validation, and evaluation pipeline is publicly available on GitHub with a permanent DOI, enabling direct reproduction and extension to other regions, biomes, and satellite data products.

The manuscript has not been published previously and is not under consideration elsewhere. All authors have approved the manuscript and agree with its submission to *Ecological Indicators*. We are submitting under the subscription (no-fee) publishing option.

Thank you for considering our manuscript. I look forward to your response.

Sincerely,

Zhuoxian Wu
Guangdong Neusoft Institute of Technology
Email: wum2371@gmail.com
GitHub: https://github.com/WUMIKE233/nature-climate-ai
Release DOI: 10.5281/zenodo.14882001
