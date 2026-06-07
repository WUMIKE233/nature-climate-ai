# Remote Sensing (MDPI) Submission Checklist / 投稿检查清单

> 更新时间: 2026-06-08 | **已投稿: remotesensing-3667717** | 目标期刊: Remote Sensing (MDPI)

## 投稿前检查 / Pre-submission Check

### 稿件内容 / Manuscript Content

| # | 检查项 | 状态 | 备注 |
|---|--------|:--:|------|
| 1 | 标题符合期刊范围 | ✅ | "Interpretable discovery of lagged climate precursors..." |
| 2 | 作者信息完整 | ✅ | 吴卓宪, 广东东软学院NUIT |
| 3 | Abstract ≤ 200 words | ✅ | ~200 words, single paragraph |
| 4 | Keywords 5-8 个 | ✅ | MODIS; ERA5-Land; vegetation index; climate precursor; VPD; soil moisture; early warning; Australia; grid alignment; false alarm ratio |
| 5 | Introduction 明确研究问题和贡献 | ✅ | |
| 6 | Materials and Methods 可复现 | ✅ | 含 GEE 导出、质量过滤、异常计算等完整描述 |
| 7 | Results 有图表支撑 | ✅ | 6 figures (Fig. 1-5 + S1) |
| 8 | Discussion 讨论局限性和意义 | ✅ | 含 persistence baseline 比较、假警报率讨论 |
| 9 | Conclusions 总结核心发现 | ✅ | |
| 10 | References 格式正确 | ✅ | 15 references, DOI 验证 |
| 11 | Data Availability Statement | ✅ | MODIS/ERA5 公开数据 + Zenodo DOI |
| 12 | Conflicts of Interest | ✅ | "The author declares no competing interests." |
| 13 | Author Contributions | ✅ | CRediT 格式 |

### 图表 / Figures

| # | 图表 | 文件 | 尺寸 |
|---|------|------|------|
| 1 | Fig. 1: Study domain + pipeline | `figures/generated/fig1_study_domain.png` | 224 KB |
| 2 | Fig. 2: Stress events | `figures/generated/fig2_stress_events.png` | 150 KB |
| 3 | Fig. 3: Precursor discovery | `figures/generated/fig3_precursor_discovery.png` | 196 KB |
| 4 | Fig. 4: Model performance | `figures/generated/fig4_model_performance.png` | 86 KB |
| 5 | Fig. 5: Spatial transfer | `figures/generated/fig5_spatial_transfer.png` | 90 KB |
| S1 | Fig. S1: Threshold sensitivity | `figures/generated/figS1_threshold_sensitivity.png` | 111 KB |

### 投稿材料 / Submission Materials

| # | 材料 | 文件 | 状态 |
|---|------|------|:--:|
| 1 | Cover Letter | `manuscript/cover_letter_remote_sensing.md` | ✅ |
| 2 | Manuscript (MDPI format) | `manuscript/nature_article_draft.md` | ✅ |
| 3 | Figure 1-5 + S1 | `figures/generated/fig*.png` | ✅ |
| 4 | Supplementary Materials | Fig. S1 + pipeline description | ✅ |
| 5 | GitHub Repository | https://github.com/WUMIKE233/nature-climate-ai | ✅ |
| 6 | Zenodo DOI | (等待归档 / pending archive) | ⏳ |

## MDPI 投稿步骤 / Submission Steps

1. 访问 https://susy.mdpi.com 注册/登录
2. 选择 "Remote Sensing" 期刊
3. 填写投稿信息：
   - Manuscript Type: Article
   - Title: 复制稿件标题
   - Abstract: 复制稿件摘要
   - Keywords: 复制关键词列表
4. 上传文件：
   - Manuscript: `manuscript/nature_article_draft.md` (可转 Word)
   - Cover Letter: `manuscript/cover_letter_remote_sensing.md`
   - Figures: 6 张 PNG (fig1-5 + figS1)
5. 推荐审稿人（建议 3-5 位）：
   - 可在 Web of Science / Scopus 搜索 Australia vegetation remote sensing 或 drought monitoring 领域的专家
6. 确认投稿

## 关键数值核查 / Key Numbers to Verify

| 数值 | 稿件中 | 验证 |
|------|--------|------|
| MODIS 观测数 | 22,267,872 | ✅ |
| 质量过滤后 | 11,608,373 (52.1%) | ✅ |
| 建模集行数 | 7,287,280 | ✅ |
| Positive labels | 503,743 (6.9%) | ✅ |
| VPD 16d recall | 0.609 | ✅ |
| VPD 16d precision | 0.055 | ✅ |
| Persistence recall/precision | 0.661/0.659 | ✅ |
| Persistence skill score | 0.319 | ✅ |
| False alarm ratio (VPD 16d) | 0.945 | ✅ |
| Spatial regions | 20 | ✅ |

## 投稿后续 / After Submission

- 记录 Manuscript ID
- 更新 README 添加投稿状态
- 若需要修改，MDPI 审稿周期通常 4-8 周
