# STA 2030 — CHOP Analysis Presentation Slides
# Copy each slide block into PowerPoint as a new slide.
# Suggested theme: dark blue header, white body, Kenya flag accent colors.

---

## Slide 1: Title Slide

**Evaluating the Community Health Outreach Program (CHOP)**
Statistical Inference Analysis — STA 2030-A

Summer Semester 2026
Instructor: Joyce Kiarie, Ph.D
School of Science & Technology

---

## Slide 2: Background & Objectives

**The Problem**
- A Kenyan county launched CHOP to improve community health outcomes
- Key targets: vaccination uptake, health knowledge, clinic visits

**Our Objectives**
- Determine if CHOP had a statistically significant impact
- Identify sub-counties needing targeted intervention
- Provide evidence-based policy recommendations

**Data:** 300 respondents | 6 Sub-counties | Baseline + Follow-up

---

## Slide 3: Dataset Overview

**Variables Collected**

| Type | Variables |
|---|---|
| Demographic | Age, Gender, SubCounty, Income Level |
| Outcome (Before) | Vaccination, Knowledge Score |
| Outcome (After) | Vaccination, Knowledge Score |
| Healthcare | Clinic Visits, Distance (km) |
| Program | Awareness of CHOP, Satisfaction (1–5) |

**n = 300 | 12 Variables | 6 Sub-counties (A–F)**

---

## Slide 4: Key Descriptive Findings

**Numeric Summary**

| Variable | Mean | Range |
|---|---|---|
| Age | 43.3 years | 18 – 69 |
| Clinic Visits | 3.06 | 0 – 7 |
| Distance to Clinic | 4.56 km | 1.35 – 7.71 |
| Knowledge Before | 9.26 | −1.2 – 19.5 |
| Knowledge After | 11.99 | 3.7 – 18.6 |

**72.67% of respondents were aware of CHOP**
**Sample: 54% Female | 46% Male | Income evenly split (Low/Med/High ≈ 33% each)**

---

## Slide 5: Vaccination Rates — Before vs After CHOP

**Dramatic Increase in Vaccination Coverage**

| Period | Vaccinated | Rate |
|---|---|---|
| Before CHOP | 118 / 300 | **39.33%** |
| After CHOP | 195 / 300 | **65.00%** |
| **Change** | **+77** people | **+25.67 pp** |

**95% Confidence Interval for difference: (17.9%, 33.4%)**
→ The increase is **statistically significant** (p < 0.001)

*(See Fig 4)*

---

## Slide 6: Health Knowledge Scores — Before vs After CHOP

**CHOP Significantly Improved Knowledge**

| Measure | Before | After | Gain |
|---|---|---|---|
| Mean Score | 9.26 | 11.99 | **+2.73** |
| Median Score | 9.20 | 12.15 | **+2.95** |

**Paired t-test:** t(299) ≈ 10.72, **p < 0.001**
**95% CI for mean gain: (2.23, 3.23 points)**

**Wilcoxon Signed Rank (non-parametric):**
V = 8,649.5, **p < 0.000001** ✓ Confirms result

*(See Figs 2 & 10)*

---

## Slide 7: Confidence Intervals Summary

**Three Key Estimates**

| Parameter | Estimate | 95% CI |
|---|---|---|
| Mean Knowledge Gain | +2.73 points | (2.23, 3.23) |
| Mean Clinic Visits | 3.06 visits | (2.87, 3.25) |
| Vaccination Rate Difference (After − Before) | +25.67 pp | (17.9%, 33.4%) |

**All intervals exclude zero → all effects are real and significant**

Average community member visits clinic **~3 times** in the program period

---

## Slide 8: ANOVA — Knowledge by Sub-County

**Do sub-counties differ in knowledge after CHOP?**

H₀: All sub-county means are equal

**Mean Knowledge Score After CHOP:**

| A | B | C | D | E | F |
|---|---|---|---|---|---|
| 12.07 | **11.43** | 12.11 | 12.09 | 11.92 | **12.45** |

**One-Way ANOVA:** F(5, 294) ≈ 0.35, **p ≈ 0.88**
**Decision: Fail to reject H₀** — No significant difference across sub-counties

Kruskal-Wallis (non-parametric): H ≈ 1.80, p ≈ 0.87 ✓ Same conclusion

*(See Fig 8)*

---

## Slide 9: Chi-Square Tests

**Three categorical analyses:**

| Test | Question | χ² | p-value | Result |
|---|---|---|---|---|
| GoF | Is Satisfaction uniform? | 0.67 | 0.955 | **Uniform** ✓ |
| Independence | Awareness ↔ Gender? | 0.02 | 0.89 | **Independent** |
| Independence | Vaccination ↔ Income? | 2.80 | 0.25 | **Independent** |

**Key Insight:**
- Vaccination uptake does NOT depend on income level → CHOP achieved **health equity**
- Awareness of CHOP is **equally spread** across genders (≈72% both)

*(See Fig 9)*

---

## Slide 10: Non-Parametric Tests Summary

| Test | Comparison | Statistic | p-value | Conclusion |
|---|---|---|---|---|
| Wilcoxon Signed Rank | Knowledge Before vs After | V = 8649.5 | **< 0.000001** | Significant improvement |
| Mann-Whitney U | Clinic Visits: Male vs Female | W ≈ 11,100 | **≈ 0.95** | No difference |
| Kruskal-Wallis | Knowledge by SubCounty | H ≈ 1.80 | **≈ 0.87** | No difference |

**All non-parametric results align with parametric findings**
→ Results are **robust** to distributional assumptions

---

## Slide 11: Recommendations

**Based on Statistical Evidence:**

1. **Scale Up CHOP County-Wide**
   Vaccination +25.67 pp | Knowledge +2.73 pts (both p < 0.001)

2. **Target Sub-Counties B and E**
   Lowest knowledge scores (11.43 & 11.92) — deploy extra health workers

3. **Maintain Equity Model**
   Vaccination independent of income — free delivery works, keep it

4. **Fix Satisfaction Gaps**
   ~39% rated services 1–2 out of 5 → exit interviews needed

5. **Reduce Distance Barriers**
   Mean 4.56 km, max 7.71 km → mobile health units for remote areas

---

## Slide 12: Conclusion

**CHOP Works — The Data Confirms It**

✓ Vaccination up **25.67 percentage points**
✓ Health knowledge up **2.73 points** (p < 0.001)
✓ Program reached **all income groups equally**
✓ Consistent impact across **all 6 sub-counties**

**Recommendation to the County Government:**
> *Scale up the Community Health Outreach Program, prioritize Sub-counties B and E for targeted support, and invest in mobile health infrastructure to eliminate distance as a barrier.*

**All results generated in R — Full code and output available in `analysis.R`**

---
*STA 2030-A | Summer 2026 | Joyce Kiarie, Ph.D*
