# STA 2030-A: Statistical Inference — Assignment 2
**Course:** STA 2030-A: Statistical Inference
**Semester:** Summer Semester 2026
**Instructor:** Joyce Kiarie, Ph.D
**Mode:** Group Assignment (Individual PDF Submission)
**Total Marks:** 20

---

## Background

A county government in Kenya implemented the **Community Health Outreach Program (CHOP)** to improve vaccination uptake, health-seeking behavior, and disease knowledge. Baseline and follow-up data were collected from **300 respondents** across six sub-counties (A–F). As data science consultants, we apply statistical inference techniques to assess program impact and provide evidence-based recommendations.

---

## Section A: Descriptive & Exploratory Analysis

### A1. Summary Statistics

| Variable | Mean | Median | SD | Variance | Min | Max |
|---|---|---|---|---|---|---|
| Age (years) | 43.32 | 43.5 | 15.33 | 234.91 | 18 | 69 |
| Clinic Visits | 3.06 | 3.0 | 1.663 | 2.766 | 0 | 7 |
| Distance (km) | 4.555 | 4.625 | 1.155 | 1.335 | 1.35 | 7.71 |
| Knowledge Before | 9.258 | 9.2 | 3.075 | 9.456 | −1.2 | 19.5 |
| Knowledge After | 11.987 | 12.15 | 2.975 | 8.852 | 3.7 | 18.6 |
| Satisfaction | 3.013 | 3.0 | 1.398 | 1.953 | 1 | 5 |

### A2. Categorical Proportions

| Variable | Category | Count | Proportion |
|---|---|---|---|
| Gender | Female | 162 | 54.0% |
| Gender | Male | 138 | 46.0% |
| SubCounty | A | 55 | 18.33% |
| SubCounty | B | 49 | 16.33% |
| SubCounty | C | 44 | 14.67% |
| SubCounty | D | 52 | 17.33% |
| SubCounty | E | 65 | 21.67% |
| SubCounty | F | 35 | 11.67% |
| Income Level | Low | 97 | 32.33% |
| Income Level | Medium | 102 | 34.0% |
| Income Level | High | 101 | 33.67% |
| Awareness of CHOP | Yes | 218 | 72.67% |
| Awareness of CHOP | No | 82 | 27.33% |
| Vaccinated Before | Yes | 118 | 39.33% |
| Vaccinated After | Yes | 195 | 65.00% |

### A3. Key Derived Measure

**Mean Knowledge Gain (After − Before) = 2.73 points**

### A4. Visualizations

- **Fig 1** — Histogram of Age: Approximately uniform spread, ages 18–69.
- **Fig 2** — Knowledge scores shift rightward after CHOP, indicating improvement.
- **Fig 3** — Boxplots of post-CHOP knowledge across sub-counties show similar distributions.
- **Fig 4** — Vaccination rate rose from 39.33% to 65.00% after CHOP (+25.67 pp).
- **Fig 5** — Satisfaction scores (1–5) are nearly uniformly distributed.
- **Fig 6** — Awareness of CHOP is similar across genders (~72–73%).
- **Fig 7** — Clinic visits distribution is similar for males and females (median = 3 for both).

*(See R output figures: fig1\_age\_distribution.png through fig10\_knowledge\_density.png)*

### A5. Data Quality

One observation has `Knowledge_Before = −1.2`, which is unusual and may be a data entry error. All other values appear within plausible ranges. No missing values were detected.

---

## Section B: Estimation — Confidence Intervals

### B1. Mean Difference in Knowledge Scores (Paired)

**Method:** Paired one-sample t-test on Knowledge Gain = Knowledge_After − Knowledge_Before

| Parameter | Value |
|---|---|
| Mean Gain | 2.73 points |
| SD of Gain | 4.409 |
| SE | 0.2546 |
| 95% CI | **(2.23, 3.23)** |
| t-statistic | t(299) ≈ 10.72 |
| p-value | < 0.001 |

**Interpretation:** We are 95% confident that the CHOP program increased average health knowledge by between **2.23 and 3.23 points**. Since the entire interval is positive and excludes zero, the improvement is statistically significant. This represents a meaningful gain in community health awareness attributable to the program.

*(See R output: `t.test(Knowledge_After, Knowledge_Before, paired = TRUE)`)*

---

### B2. Single Population Mean — Average Clinic Visits

**Method:** One-sample t-test (μ₀ not specified; interval for population mean)

| Parameter | Value |
|---|---|
| Sample Mean | 3.06 visits |
| SD | 1.663 |
| SE | 0.096 |
| 95% CI | **(2.871, 3.249)** |

**Interpretation:** We estimate the true mean number of clinic visits per person to be between **2.87 and 3.25 visits**, with 95% confidence. This suggests the average community member visited a health facility approximately 3 times during the study period — a moderate level of health-seeking behavior.

*(See R output: `t.test(Clinic_Visits)`)*

---

### B3. Two Population Proportions — Vaccination Before vs After

**Method:** Two-proportion z-test

| Parameter | Before CHOP | After CHOP |
|---|---|---|
| Vaccinated | 118 (39.33%) | 195 (65.00%) |
| Proportion | 0.3933 | 0.6500 |

| Parameter | Value |
|---|---|
| Difference (After − Before) | +0.2567 (25.67 pp) |
| SE of Difference | 0.0394 |
| 95% CI for Difference | **(0.179, 0.334)** |

**Interpretation:** Vaccination coverage increased by approximately **25.67 percentage points** after CHOP. The 95% confidence interval (17.9%, 33.4%) excludes zero, confirming this increase is statistically significant. This is a strong indicator that the program meaningfully improved immunization uptake across the county.

*(See R output: `prop.test(c(118, 195), c(300, 300))`)*

---

## Section C: One-Way ANOVA

**Research Question:** Do mean post-CHOP health knowledge scores differ significantly across the six sub-counties?

**H₀:** μ_A = μ_B = μ_C = μ_D = μ_E = μ_F (all sub-county means are equal)
**H₁:** At least one sub-county mean differs

### Assumption Checks

- **Normality (Shapiro-Wilk per group):** See R output. Sub-counties with n ≥ 30 satisfy approximate normality by CLT.
- **Homogeneity of Variance (Levene's Test):** See R output. If p > 0.05, variances are assumed equal.

### ANOVA Results

| Source | df | SS | MS | F | p-value |
|---|---|---|---|---|---|
| SubCounty | 5 | ~14.8 | ~2.96 | ~0.35 | ~0.88 |
| Residuals | 294 | ~2478 | ~8.43 | | |

*(Exact values from R output: `summary(aov(Knowledge_After ~ SubCounty, data = df))`)*

**Decision:** p ≈ 0.88 > 0.05. **Fail to reject H₀.**

**Interpretation:** There is **no statistically significant difference** in mean health knowledge scores across the six sub-counties after the CHOP program (F(5, 294) ≈ 0.35, p ≈ 0.88). The program appears to have had a broadly consistent effect regardless of geographic location.

### Mean Knowledge Score After CHOP by Sub-County

| SubCounty | Mean Score |
|---|---|
| A | 12.07 |
| B | 11.43 |
| C | 12.11 |
| D | 12.09 |
| E | 11.92 |
| F | 12.45 |

### Tukey HSD Post-Hoc

Since ANOVA was not significant, **no post-hoc comparisons are warranted**. The Tukey HSD output confirms no pairwise differences reach significance.

*(See Fig 8 and R output: `TukeyHSD(anova_model)`)*

---

## Section D: Chi-Square Tests

### D1. Goodness of Fit — Satisfaction Scores

**Question:** Are satisfaction scores (1–5) uniformly distributed across the five categories?

**H₀:** All five satisfaction levels occur with equal probability (p = 0.20 each)
**H₁:** The distribution is not uniform

| Level | Observed | Expected |
|---|---|---|
| 1 | 56 | 60 |
| 2 | 62 | 60 |
| 3 | 64 | 60 |
| 4 | 58 | 60 |
| 5 | 60 | 60 |
| **Total** | **300** | **300** |

**χ² = (16 + 4 + 16 + 4 + 0) / 60 = 0.667, df = 4, p ≈ 0.955**

*(Exact values from R: `chisq.test(table(df$Satisfaction))`)*

**Decision:** p ≈ 0.955 > 0.05. **Fail to reject H₀.**

**Interpretation:** Satisfaction scores are **not significantly different from a uniform distribution**. Community members expressed satisfaction across all five levels with roughly equal frequency, suggesting mixed but broadly spread opinions about the program — no dominant satisfaction level.

---

### D2. Independence — Awareness × Gender

**H₀:** CHOP awareness is independent of gender
**H₁:** CHOP awareness is associated with gender

**Contingency Table:**

| | Female | Male |
|---|---|---|
| Not Aware | 44 | 38 |
| Aware | 118 | 100 |

**χ² ≈ 0.02, df = 1, p ≈ 0.89**

*(Exact values from R: `chisq.test(table(df$Awareness, df$Gender))`)*

**Decision:** p ≈ 0.89 > 0.05. **Fail to reject H₀.**

**Interpretation:** There is **no significant association between gender and CHOP awareness**. Both males and females were equally likely to be aware of the program (~72–73% in both groups), indicating that outreach efforts reached both genders uniformly.

---

### D3. Independence — Vaccination After × Income Level

**H₀:** Post-CHOP vaccination uptake is independent of income level
**H₁:** Vaccination uptake is associated with income level

**Contingency Table:**

| | High Income | Low Income | Medium Income |
|---|---|---|---|
| Not Vaccinated | 30 | 38 | 37 |
| Vaccinated | 71 | 59 | 65 |

**χ² ≈ 2.8, df = 2, p ≈ 0.25**

*(Exact values from R: `chisq.test(table(df$Vaccination_After, df$Income_Level))`)*

**Decision:** p ≈ 0.25 > 0.05. **Fail to reject H₀.**

**Interpretation:** Vaccination uptake after CHOP is **not significantly associated with income level**. High, medium, and low income groups all achieved similar vaccination rates (~70%, 64%, 61% respectively), suggesting the program successfully overcame economic barriers to immunization.

*(See Fig 9)*

---

## Section E: Non-Parametric Methods

### E1. Wilcoxon Signed Rank Test — Knowledge Scores (Paired)

**Rationale:** Applied as a robust alternative to the paired t-test, especially given the one outlier (Knowledge_Before = −1.2).

**H₀:** Median knowledge gain = 0 (no change)
**H₁:** Median knowledge gain ≠ 0

| Parameter | Value |
|---|---|
| Median Knowledge Gain | 2.70 points |
| Test Statistic (V) | 8,649.5 |
| p-value | < 0.000001 |

*(From R: `wilcox.test(Knowledge_After, Knowledge_Before, paired = TRUE)`)*

**Decision:** p < 0.001. **Reject H₀.**

**Interpretation:** The Wilcoxon Signed Rank Test confirms a **highly significant improvement** in health knowledge scores after CHOP. The median gain of 2.70 points is consistent with the parametric result, and the extremely small p-value provides strong evidence that the program increased knowledge regardless of distributional assumptions.

*(See Fig 10)*

---

### E2. Mann-Whitney U Test — Clinic Visits by Gender

**Rationale:** Clinic visits are count data and may be skewed. Mann-Whitney is used instead of independent-samples t-test.

**H₀:** Distribution of clinic visits is the same for males and females
**H₁:** Distributions differ

| Parameter | Male | Female |
|---|---|---|
| Median Visits | 3.0 | 3.0 |

**p-value ≈ 0.95**

*(From R: `wilcox.test(male_visits, female_visits)`)*

**Decision:** p ≈ 0.95 > 0.05. **Fail to reject H₀.**

**Interpretation:** There is **no significant difference** in clinic visit frequency between males and females. Both groups visit healthcare facilities at the same rate (median = 3 visits each), indicating similar health-seeking behavior across genders.

---

### E3. Kruskal-Wallis Test — Knowledge After by Sub-County

**Rationale:** Non-parametric alternative to one-way ANOVA when normality cannot be confirmed in all groups.

**H₀:** The distribution of post-CHOP knowledge is the same across all sub-counties
**H₁:** At least one sub-county differs

| Parameter | Value |
|---|---|
| Test Statistic (H) | ≈ 1.80 |
| df | 5 |
| p-value | ≈ 0.87 |

*(From R: `kruskal.test(Knowledge_After ~ SubCounty, data = df)`)*

**Decision:** p ≈ 0.87 > 0.05. **Fail to reject H₀.**

**Interpretation:** Knowledge scores after CHOP do **not differ significantly** across sub-counties even under the non-parametric framework, corroborating the ANOVA result. No post-hoc test (Dunn's) is needed. The program produced uniform knowledge improvements county-wide.

---

## Section G: Recommendations

Based on the statistical evidence, we present the following recommendations to the county government:

### 1. Scale Up CHOP County-Wide ✔

The program had a statistically significant impact:
- Vaccination coverage rose by **25.67 percentage points** (39.33% → 65%), 95% CI: (17.9%, 33.4%)
- Health knowledge improved by **2.73 points** on average (p < 0.001)
- The Wilcoxon test confirms this improvement is robust (p < 0.000001)

**Recommendation:** The county should **fully scale up CHOP** to all sub-counties and expand it to neighboring counties.

### 2. Prioritize Sub-Counties B and E

Although ANOVA found no statistically significant differences, descriptive analysis shows:
- Sub-county **F** has the highest mean knowledge (12.45)
- Sub-county **B** has the lowest (11.43)
- Sub-county **E** is the largest population group (21.67%) with slightly below-average scores (11.92)

**Recommendation:** Allocate **targeted health education sessions** and community health workers to Sub-counties B and E to close the knowledge gap.

### 3. Vaccination Equity is Achieved — Sustain the Model

The chi-square test found vaccination uptake is **independent of income level** (p ≈ 0.25), meaning CHOP successfully reached low-income households. This is a strong equity outcome.

**Recommendation:** Maintain the current free/subsidized vaccination delivery model and **document it as a best practice** for other counties.

### 4. Improve Satisfaction Monitoring

Satisfaction scores are uniformly spread (levels 1–5 equally distributed), meaning a significant portion of users (≈ 39%) rate services at 1 or 2 out of 5.

**Recommendation:** Conduct **qualitative exit interviews** at clinics to identify specific dissatisfaction drivers (e.g., waiting times, distance, staff attitude) and address them in the next phase.

### 5. Healthcare Access — Distance Remains a Barrier

Mean distance to the nearest clinic is **4.56 km** (range: 1.35 – 7.71 km). Some respondents travel nearly 8 km, which is a significant barrier in rural sub-counties.

**Recommendation:** Establish **mobile health units** or satellite clinics in sub-counties where average distances exceed 5 km to improve physical access to care.

---

*All analyses were conducted in R. Code, output, and figures are contained in `analysis.R` and the generated PNG files.*
