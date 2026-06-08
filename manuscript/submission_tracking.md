# Submission Tracking / ????

> **Manuscript ID**: ECOIND-D-26-01217
> **Target Journal**: Ecological Indicators (Elsevier)
> **Status**: Submitted to Journal (June 8, 2026, 10:14 CST)

---

## Manuscript Details / ????

| Field | Value |
|-------|-------|
| Title | Interpretable Discovery of Lagged Climate Precursors for Vegetation-Index Stress across Australia |
| Article Type | Research Paper |
| Corresponding Author | Zhuoxian Wu (???) |
| Email | wum2371@gmail.com |
| Institution (correct) | Guangdong Neusoft Institute of Technology, Foshan, Guangdong, China |
| Institution (in EM) | Neusoft Institute of Guangdong School of Computer Science and Technology ?? needs correction |
| Open Access | Selected (APC: EUR 3,670, charged only if accepted) |
| Data Repository | Zenodo (DOI: 10.5281/zenodo.14882001) |
| GitHub | https://github.com/WUMIKE233/nature-climate-ai v1.0-rs |
| Preprint | Not shared via SSRN |

---

## Submission Materials / ?????

| # | Material | Status |
|:--:|------|:--:|
| 1 | Manuscript (DOCX) | ? Uploaded |
| 2 | Highlights | ? Uploaded |
| 3 | Declaration of Competing Interests | ? None declared |
| 4 | Title, Abstract, Keywords | ? Entered manually |
| 5 | Author Details | ? Entered |
| 6 | Contributor Roles (CRediT) | ? All roles selected |
| 7 | Classifications (5) | ? Selected |
| 8 | Research Data (Zenodo DOI) | ? Linked |
| 9 | Ethics / Copyright / Acknowledgements | ? Confirmed |

---

## Status Tracking / ????

| Date | Status | Notes |
|------|--------|-------|
| 2026-06-08 10:14 | **Submitted to Journal** | Initial submission complete |
| ? | With Editor | ? Pending |
| ? | Under Review | ? Pending |
| ? | Required Reviews Completed | ? Pending |
| ? | Decision in Process | ? Pending |
| ? | Revise / Accept / Reject | ? Pending |

---

## Institution Name Issue / ?????

EM system shows: `Neusoft Institute of Guangdong School of Computer Science and Technology`

Correct name: `Guangdong Neusoft Institute of Technology, Foshan, Guangdong, China`

**Action**: Correct during revision/proof stage. Do not submit a correction now unless editorial office requests it.

---

## Key Results Summary / ??????

| Metric | Value |
|--------|:--:|
| Observations (raw ? QC filtered) | 22.3M ? 11.6M (52.1%) |
| Modeling dataset | 7.3M rows, 503K positive (6.9%) |
| Best single precursor | Soil moisture 16d lag, \|r\|=0.210 |
| Best climate F1 | VPD family, 0.115 |
| Persistence F1 | 0.660 |
| Persistence skill score | 0.660 |
| XGBoost precision | 0.191 |
| XGBoost recall | 0.791 |
| XGBoost FAR | 0.809 |

---

## Anticipated Reviewer Questions / ??????

### 1. Why only Australia?
> Australia provides a strong continental-scale testbed with diverse aridity gradients and strong climate-vegetation coupling. The study is designed as a reproducible regional framework that can be transferred to other continents in future work.

### 2. Why no FLUXNET / GPP / SIF validation?
> This study focuses on satellite-observed vegetation-index stress rather than ecosystem carbon-flux stress. FLUXNET validation was designed into the pipeline but could not be completed. MODIS GPP or SIF validation is planned for the next phase.

### 3. Why is precision so low for climate-only models?
> This is a core finding: climate-only precursors are useful for risk screening but insufficient for precise event prediction. Low precision reflects non-climatic disturbance, vegetation acclimation, and sub-pixel heterogeneity.

### 4. Why is persistence baseline stronger than climate models?
> Vegetation stress is temporally autocorrelated due to slow ecological recovery. Persistence is a necessary benchmark, not a competitor. Climate models quantify precursor risk alongside vegetation-memory information.

### 5. What is the novelty as an ecological indicator paper?
> (1) Shared-grid audit framework ensuring spatial alignment; (2) Systematic comparison of climate precursor indicators against persistence baseline; (3) F1-based skill score framework for indicator evaluation; (4) Full reproducibility with version-controlled pipeline and DOI.

---

## Post-Submission TODO / ?????

| # | Task | Priority |
|:--:|------|:--:|
| 1 | Monitor EM for status changes | High |
| 2 | Fix institution name on first opportunity | Medium |
| 3 | Consider switching from OA to Subscription to avoid EUR 3,670 APC | Medium |
| 4 | Prepare FLUXNET data for Phase 2 | Low |
| 5 | Consider MODIS GPP or SIF as supplementary validation | Low |

---

## File Inventory / ??????

```
W:\Nature\manuscript\
??? manuscript_remote_sensing_revised.docx  ? Uploaded
??? highlights_ecological_indicators.md     ? Uploaded
??? cover_letter_ecological_indicators.md
??? recommended_reviewers.md
??? author_metadata.yaml
??? submission_walkthrough_ecological_indicators.md
??? submission_checklist_ecological_indicators.md
??? submission_tracking.md                  ? THIS FILE
??? nature_article_revised.md
??? nature_article_revised_chinese.md

W:\Nature\figures\generated\
??? fig1_study_domain.png
??? fig2_stress_events.png
??? fig3_precursor_discovery.png
??? fig4_model_performance.png
??? fig5_spatial_transfer.png
??? figS1_threshold_sensitivity.png
```

---

*Tracking document created 2026-06-08. Update as status changes.*
