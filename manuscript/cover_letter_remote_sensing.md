> **Archived: superseded by cover_letter_ecological_indicators.md**

﻿# Cover Letter

**Journal**: Remote Sensing (MDPI)
**Manuscript Title**: Interpretable Discovery of Lagged Climate Precursors for Vegetation-Index Stress across Australia
**Author**: Zhuoxian Wu (吴卓宪), Guangdong Neusoft Institute of Technology

---

Dear Editors,

I am pleased to submit our manuscript titled "Interpretable Discovery of Lagged Climate Precursors for Vegetation-Index Stress across Australia" for consideration for publication in *Remote Sensing*.

**What this paper does**: We construct and validate a reproducible, grid-aligned framework that systematically discovers climate precursor signals for satellite-observed vegetation stress across the Australian continent at 0.25° spatial resolution using 26 years (2000–2025) of MODIS vegetation indices and ERA5-Land climate reanalysis. The study enforces identical pixel grids for MODIS and ERA5 data through an automated audit before any analysis proceeds—a simple but critical methodological safeguard that eliminates a pervasive source of spatial misalignment in large-scale remote-sensing studies. Quality filtering is performed on native-resolution MODIS pixels prior to spatial aggregation, ensuring that QA information is properly handled before resampling.

**Key findings**: (1) Soil-moisture deficit and vapour-pressure-deficit (VPD) excess at 16–32 day lead times are the dominant precursor signals for vegetation-index stress; (2) a simple persistence baseline (knowing whether a pixel experienced stress in the previous 16-day window) achieves precision 0.66 and recall 0.66, outperforming all single-variable climate thresholds on precision with a skill score of 0.660 (SS = (F1 − F1_majority) / (1 − F1_majority)), approximately six times that of the best climate-only precursor (VPD family, 0.115); (3) even the best-performing climate precursor (VPD at 16-day lag) detects 61% of stress events but generates a false-alarm ratio of 0.94; (4) while Random Forest and XGBoost classifiers improve recall to ~0.79 and precision to ~0.19, their false-alarm ratios still exceed 0.80, and the persistence baseline remains the strongest predictor overall; (5) spatial transfer of precursor signals across 20 held-out regions is modest, and latitude-zone stratification reveals stronger climate–vegetation coupling in Australia's subtropical interior. The core conclusion is not that VPD or soil moisture precede vegetation stress—which is ecologically expected—but rather that climate-only precursors, even when combined non-linearly through machine learning, are useful for identifying elevated risk conditions yet generate unacceptably high false-alarm rates for operational stress-event prediction without vegetation-memory and ecological-context information. All climatologies were estimated exclusively from the training period (2000–2018) to prevent information leakage from the temporal holdout set.

**Why Remote Sensing**: The manuscript aligns closely with the scope of *Remote Sensing*, which covers the intersection of satellite remote sensing, environmental monitoring, and data-driven analysis of Earth observation products. The study makes extensive use of MODIS reflectance-based vegetation indices and ERA5-Land climate variables, all processed on a rigorously validated shared spatial grid, with full reproducibility through version-controlled code and publicly archived data exports. We believe the readership of *Remote Sensing*—researchers working at the interface of satellite data, climate reanalysis, and ecological applications—will find the framework, methodology, and findings directly relevant.

**Novelty and significance**: Three aspects distinguish this work. First, the shared-grid methodology with automated audit provides a transferable template for any study that merges satellite vegetation products with gridded climate data. Second, the systematic comparison against persistence and machine-learning baselines reveals that the apparent predictive skill of climate thresholds largely reflects temporal autocorrelation in vegetation stress, a finding with direct implications for the design of satellite-based early-warning systems. Third, the full analysis pipeline—from Google Earth Engine data export through quality filtering, anomaly computation, feature construction, validation, and figure generation—is publicly available on GitHub with a permanent DOI, enabling direct reproduction and extension to other regions.

The manuscript has not been published previously and is not under consideration elsewhere. All authors have approved the manuscript and agree with its submission to *Remote Sensing*.

Thank you for considering our manuscript. I look forward to your response.

Sincerely,

Zhuoxian Wu
Guangdong Neusoft Institute of Technology
Email: wum2371@gmail.com
GitHub: https://github.com/WUMIKE233/nature-climate-ai
Release DOI: 10.5281/zenodo.14882001
