# Remote Sensing (MDPI) Submission Checklist

> 更新时间: 2026-06-08 | 目标期刊: Remote Sensing (MDPI)
> 稿件版本: v3-revised (已按审阅意见修正)

## 稿件内容 / Manuscript Content

| # | 检查项 | 状态 | 备注 |
|---|--------|:--:|------|
| 1 | 标题符合期刊范围 | ✅ | "Interpretable discovery of lagged climate precursors..." |
| 2 | 作者信息完整 | ✅ | 吴卓宪, 广东东软学院NUIT |
| 3 | Abstract 摘要完整 | ✅ | 涵盖 study design, key results, limitations |
| 4 | Keywords 5-10 个 | ✅ | MODIS; ERA5-Land; vegetation index; climate precursor; VPD; soil moisture; early warning; Australia; grid alignment; false alarm ratio |
| 5 | Introduction 明确研究问题 | ✅ | 三个研究空白 + 本研究如何填补 |
| 6 | Materials and Methods 可复现 | ✅ | v3 修正: training-only climatology, skill score 公式, MODIS QA 处理, ML 细节 |
| 7 | Results 有数据支撑 | ✅ | 6 个子节 (3.1–3.7), 2 个表 |
| 8 | Discussion 讨论局限性和意义 | ✅ | 含 persistence baseline, false-alarm, 空间转移讨论 |
| 9 | Conclusions 总结核心发现 | ✅ | |
| 10 | References 格式正确 | ✅ | 15 references, DOI 验证 |
| 11 | Supplementary Materials | ✅ | Fig. S1 + pipeline info |
| 12 | Data Availability Statement | ✅ | MODIS/ERA5 公开 + Zenodo DOI |
| 13 | Conflicts of Interest | ✅ | "The author declares no competing interests." |
| 14 | Author Contributions | ✅ | CRediT 格式 |
| 15 | AI-Assisted Tools 声明 | ✅ | Methods 2.8 |

## v3 修正记录 / Revision Log

| # | 修正项 | 说明 |
|---|--------|------|
| 1 | Climatology leakage | Methods 2.3: 统一为 training-only (2000–2018) |
| 2 | Skill score 公式 | Methods 2.5: SS = (F1 − F1_majority) / (1 − F1_majority) |
| 3 | Majority baseline accuracy | Results 3.4: holdout prevalence 3.8% vs 全期 6.9% |
| 4 | MODIS 重采样方法 | Methods 2.1: QA 过滤 → 空间聚合, ERA5 bilinear |
| 5 | ML 训练细节 | Methods 2.6: RF/XGBoost 参数, class weight, SHAP |
| 6 | 纬度分层限制 | Discussion: 承认 coarse proxy，建议 aridity/land-cover |
| 7 | 审阅版 DOCX | 已同步更新 |

## 图表 / Figures

| # | 图表 | 文件 | 大小 |
|---|------|------|------|
| 1 | Fig. 1: Study domain | `figures/generated/fig1_study_domain.png` | 224 KB |
| 2 | Fig. 2: Stress events | `figures/generated/fig2_stress_events.png` | 103 KB |
| 3 | Fig. 3: Precursor discovery | `figures/generated/fig3_precursor_discovery.png` | 151 KB |
| 4 | Fig. 4: Model performance | `figures/generated/fig4_model_performance.png` | 72 KB |
| 5 | Fig. 5: Spatial transfer | `figures/generated/fig5_spatial_transfer.png` | 88 KB |
| S1 | Fig. S1: Threshold sensitivity | `figures/generated/figS1_threshold_sensitivity.png` | 108 KB |

## 投稿材料 / Submission Materials

| # | 材料 | 文件 | 状态 |
|---|------|------|:--:|
| 1 | Cover Letter | `manuscript/cover_letter_remote_sensing.md` | ✅ 已更新 |
| 2 | Manuscript (Markdown) | `manuscript/nature_article_revised.md` | ✅ v3-revised |
| 3 | Manuscript (Review DOCX) | `manuscript/nature_review_manuscript.docx` | ✅ 已更新 |
| 4 | MDPI Template DOCX | `manuscript/manuscript_remote_sensing.docx` | ⚠️ 需用 MDPI 模板重新生成 |
| 5 | Figure 1–5 + S1 | `figures/generated/fig*.png` | ✅ 6 张 |
| 6 | GitHub Repository | https://github.com/WUMIKE233/nature-climate-ai | ✅ |
| 7 | Zenodo DOI | 10.5281/zenodo.14882001 | ⏳ 需更新归档 |

## MDPI 投稿步骤 / Submission Steps

1. 访问 https://susy.mdpi.com 注册/登录
2. 选择 "Remote Sensing" 期刊 → Article
3. 填写标题、摘要、关键词
4. 上传文件:
   - Manuscript (MDPI template DOCX / Word)
   - Cover Letter
   - Figures (可单独上传或嵌入)
   - Supplementary Materials (如有)
5. 推荐审稿人 (3–5 位)
6. 确认投稿 → 记录 Manuscript ID

## 投稿前待办 / Before Submission

| # | 待办 | 优先级 |
|---|------|:--:|
| 1 | 用 MDPI 模板从 revised MD 重新生成 DOCX | 高 |
| 2 | 更新 Zenodo 归档（包含最新代码） | 中 |
| 3 | 确认所有图表引用与实际文件一致 | 高 |
| 4 | 检查 MDPI 期刊: 是否有字数/图表限制 | 中 |
| 5 | 推荐审稿人列表 | 低 |

## 投稿后续 / After Submission

- 记录 Manuscript ID
- 更新 README 投稿状态
- MDPI 审稿周期通常 4–8 周
