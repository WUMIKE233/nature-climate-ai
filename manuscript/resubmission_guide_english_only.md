# Ecological Indicators Resubmission Guide (English Only)

> Manuscript: Interpretable Discovery of Lagged Climate Precursors for Vegetation-Index Stress across Australia
> Author: Zhuoxian Wu

---

## STEP 0: Before You Start - Fix Your EM Profile

1. Login to [editorialmanager.com/ecolind](https://www.editorialmanager.com/ecolind/)
2. Click your name in top-right corner -> "Update My Information"
3. Make sure ALL fields are in English:
   - First/Given Name: **Zhuoxian**
   - Middle Name: (leave empty)
   - Last/Family Name: **Wu**
   - Degree: (leave empty or "Ph.D.")
   - Institution: **Guangdong Neusoft Institute of Technology**
   - Department: **School of Computer Science and Technology**
   - City: **Foshan**
   - Country: **China**
4. Save

---

## STEP 1: Submit New Manuscript

Click "Submit New Manuscript" (NOT "Edit Submission" or "Revise").

---

## STEP 2: Article Type Selection

Select: **Research Paper**

---

## STEP 3: Attach Files

Upload these files IN ORDER:

| # | Item Type (select from dropdown) | File to Upload |
|:--:|------|------|
| 1 | Manuscript | `W:\Nature\manuscript\manuscript_remote_sensing_revised.docx` |
| 2 | Cover Letter | `W:\Nature\manuscript\cover_letter_ecological_indicators.md` |
| 3 | Highlights | `W:\Nature\manuscript\highlights_ecological_indicators.md` |
| 4 | Figure | `W:\Nature\figures\generated\fig1_study_domain.png` |
| 5 | Figure | `W:\Nature\figures\generated\fig2_stress_events.png` |
| 6 | Figure | `W:\Nature\figures\generated\fig3_precursor_discovery.png` |
| 7 | Figure | `W:\Nature\figures\generated\fig4_model_performance.png` |
| 8 | Figure | `W:\Nature\figures\generated\fig5_spatial_transfer.png` |
| 9 | Figure | `W:\Nature\figures\generated\figS1_threshold_sensitivity.png` |

For each Figure, add a description:
- Figure 1: "Study domain and data coverage across Australia"
- Figure 2: "Spatial distribution of vegetation-stress events (2000-2025)"
- Figure 3: "Climate precursor discovery: point-biserial correlation ranking"
- Figure 4: "Predictive validation: precision, recall, and false-alarm ratio"
- Figure 5: "Spatial transfer: leave-one-region-out validation"
- Figure S1: "Threshold sensitivity analysis (5th-20th percentile)"

---

## STEP 4: General Information / Article Title

### Section: Title

**COPY AND PASTE THIS EXACTLY:**

Title: Interpretable Discovery of Lagged Climate Precursors for Vegetation-Index Stress across Australia

### Section: Abstract

**COPY AND PASTE THIS EXACTLY (all one paragraph):**

Satellite vegetation records now span multiple decades, yet the extent to which lagged climate anomalies can serve as interpretable early-warning precursors of vegetation stress - and the limits of such precursors - remains poorly quantified at continental scale. Here we construct a reproducible discovery framework that aligns 26 years (2000-2025) of quality-filtered MODIS vegetation-index anomalies with ERA5-Land climate reanalysis on a unified 0.25-degree grid across Australia. Vegetation-stress events are defined from pixel-level EVI anomaly climatologies, and 20 lagged climate predictors spanning soil moisture, vapour pressure deficit (VPD), temperature, precipitation, and surface radiation at lead times of 16 to 64 days are evaluated. Soil-moisture deficit and VPD excess emerge as the dominant precursor signals, with the strongest separation between stress and non-stress conditions occurring at 16-32 day lead times. However, even the best-performing single climate precursor (VPD at 16-day lag) achieves only modest precision (0.055) while detecting 61% of stress events on held-out years, and spatial transfer of precursor signals across 20 grid-defined regions exhibits substantial inter-regional variability. A shuffled-lag placebo test and threshold-sensitivity analysis confirm the robustness of the discovered patterns, while comparison against a simple persistence baseline - which achieves precision of 0.659 and recall of 0.661 - reveals that knowledge of a pixel's recent stress history outperforms any single climate variable. The persistence baseline achieves a skill score of 0.660 (SS = (F1 - F1_majority) / (1 - F1_majority)), substantially exceeding the best climate-only precursor (VPD family, skill score 0.115). These results indicate that climate precursors are useful for identifying elevated risk conditions but are insufficient for precise stress-event prediction without vegetation-memory and ecological-context information. The analysis framework is fully reproducible: all data exports, preprocessing scripts, model configurations, and validation outputs are version-controlled on a shared spatial grid and archived with a permanent DOI.

### Section: Keywords

**COPY AND PASTE THIS EXACTLY:**

MODIS; ERA5-Land; vegetation index; climate precursor; vapour pressure deficit; soil moisture; early warning; Australia; spatial grid alignment; false alarm ratio

---

## STEP 5: Additional Information

Answer these questions:

- **Has this manuscript been submitted previously to this journal?** -> Select **No** (even though it was, this is technically a new submission)
- **Has this manuscript been published or submitted elsewhere?** -> No
- **Number of figures**: 6 (5 main + S1)
- **Number of tables**: 2
- **Number of words**: approximately 8000

Other Yes/No questions: Answer truthfully (all should be "No" for a new submission)

---

## STEP 6: Comments

**COPY AND PASTE THIS EXACTLY for Cover Letter:**


Dear Editors,

I am pleased to submit our manuscript titled "Interpretable Discovery of Lagged Climate Precursors for Vegetation-Index Stress across Australia" for consideration for publication in Ecological Indicators.

This manuscript develops and validates a suite of ecological indicators for satellite-observed vegetation stress - including a persistence-based stress-recurrence indicator, climate-anomaly precursor indicators at multiple lead times (16-64 days), and an F1-based skill score framework for comparing early-warning indicator performance. The study systematically evaluates the sensitivity, specificity, and spatial transferability of these indicators across the Australian continent using 26 years of MODIS vegetation indices and ERA5-Land climate reanalysis on a unified 0.25-degree shared grid.

Key ecological indicators and findings:
1. Soil-moisture deficit and VPD excess at 16-32 day lead times are the dominant climate precursor indicators.
2. A persistence indicator achieves F1=0.660, substantially exceeding the best climate-only precursor (VPD family, F1=0.115).
3. Climate-only precursor indicators generate false-alarm ratios exceeding 0.94, and machine learning reduces this to approximately 0.81.
4. Spatial transfer of indicator signals across 20 grid regions is modest, with region-level precision rarely exceeding 0.12.

The full indicator construction, validation, and evaluation pipeline is publicly available on GitHub with a permanent Zenodo DOI (10.5281/zenodo.14882001).

The manuscript has not been published previously and is not under consideration elsewhere. We are submitting under the subscription (no-fee) publishing option.

Thank you for considering our manuscript.

Sincerely,
Zhuoxian Wu
Guangdong Neusoft Institute of Technology
Email: wum2371@gmail.com


---

## STEP 7: Manuscript Data / Author Information

### Corresponding Author:

| Field | Value |
|-------|-------|
| First/Given Name | **Zhuoxian** |
| Last/Family Name | **Wu** |
| Email | **wum2371@gmail.com** |
| Institution | **Guangdong Neusoft Institute of Technology** |
| Department | **School of Computer Science and Technology** |
| City | **Foshan** |
| Country | **China** |
| Corresponding Author | **YES (check the box)** |

### Contributor Roles (CRediT):

Check ALL of the following:
- Conceptualization
- Data curation
- Formal analysis
- Investigation
- Methodology
- Software
- Validation
- Visualization
- Writing - original draft
- Writing - review & editing

---

## STEP 8: Classifications

Select 5 classifications relevant to:
- Remote sensing
- Vegetation indices
- Climate indicators
- Ecological modeling
- Environmental monitoring

---

## STEP 9: Research Data

- **Data availability**: "Data will be made available on request" OR paste: https://doi.org/10.5281/zenodo.14882001
- **Repository**: Zenodo
- **Data type**: Original data

---

## STEP 10: Preprint

- **Share on SSRN?**: Select **No**

---

## STEP 11: Publishing Option

- Select: **Subscription (No open access)** -> EUR 0

---

## STEP 12: Ethics, Copyright, Declarations

- Funding: "This research received no external funding."
- Competing interests: "The author declares no competing interests."
- All other checkboxes: Confirm as appropriate

---

## STEP 13: FINAL STEP - Build PDF and Approve

1. After all sections are complete, click **"Build PDF for My Approval"**
2. Wait for PDF to generate (may take 1-2 minutes)
3. Click the PDF link to review
4. Verify: no Chinese characters anywhere, all figures appear correctly
5. Click **"Approve Submission"**
6. You will see a confirmation page with the new Manuscript Number
7. You will receive a confirmation email

---

## WARNING: DO NOT DO THIS

- Do NOT type or paste any Chinese characters in any field
- Do NOT include "Wu Zhuoxian" or "Zhuoxian Wu" with Chinese characters in parentheses
- Do NOT select Open Access (select Subscription instead)
- Do NOT click "Approve" until you have reviewed the PDF

## IF YOU SEE CHINESE ANYWHERE

If any page shows Chinese text, STOP. Do not approve. Take a screenshot and share it with me.

---

*Guide prepared 2026-06-08 for clean resubmission.*
