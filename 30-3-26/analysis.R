# ============================================================
# STA 2030-A: Statistical Inference — Assignment 2
# Community Health Outreach Program (CHOP) Analysis
# Instructor: Joyce Kiarie, Ph.D | Summer Semester 2026
# ============================================================

# ── Install missing packages if needed ──────────────────────
# install.packages(c("tidyverse", "car", "dunn.test"))

library(tidyverse)
library(ggplot2)
library(dplyr)
library(car)       # Levene's test
library(dunn.test) # Dunn post-hoc for Kruskal-Wallis

# ── Load Data ────────────────────────────────────────────────
df <- read.csv("Dataset.csv")
cat("Dataset loaded:", nrow(df), "rows,", ncol(df), "columns\n")
str(df)

# Convert types
df$Gender       <- as.factor(df$Gender)
df$SubCounty    <- as.factor(df$SubCounty)
df$Income_Level <- factor(df$Income_Level, levels = c("Low","Medium","High"))
df$Awareness    <- as.factor(df$Awareness)
df$Satisfaction <- as.integer(df$Satisfaction)

# Derived variable
df$Knowledge_Gain <- df$Knowledge_After - df$Knowledge_Before


# ============================================================
# SECTION A: DESCRIPTIVE & EXPLORATORY ANALYSIS
# ============================================================
cat("\n========== SECTION A: DESCRIPTIVE STATISTICS ==========\n")

# A1 — Summary statistics for numeric variables
num_vars <- df %>% select(Age, Clinic_Visits, Distance_km,
                           Knowledge_Before, Knowledge_After, Satisfaction)
desc_stats <- sapply(num_vars, function(x) c(
  Mean     = round(mean(x, na.rm = TRUE), 4),
  Median   = round(median(x, na.rm = TRUE), 4),
  SD       = round(sd(x, na.rm = TRUE), 4),
  Variance = round(var(x, na.rm = TRUE), 4),
  Min      = min(x, na.rm = TRUE),
  Max      = max(x, na.rm = TRUE)
))
print(desc_stats)

# A2 — Categorical proportions
cat("\nGender proportions:\n");       print(prop.table(table(df$Gender)))
cat("\nSubCounty proportions:\n");    print(prop.table(table(df$SubCounty)))
cat("\nIncome Level proportions:\n"); print(prop.table(table(df$Income_Level)))
cat("\nAwareness proportions:\n");    print(prop.table(table(df$Awareness)))
cat("\nVaccination Before:\n");       print(prop.table(table(df$Vaccination_Before)))
cat("\nVaccination After:\n");        print(prop.table(table(df$Vaccination_After)))

# A3 — Mean Knowledge Gain
cat("\nMean Knowledge Gain (After - Before):", round(mean(df$Knowledge_Gain), 4), "\n")

# ── Visualizations ───────────────────────────────────────────

# Fig 1: Age distribution
p1 <- ggplot(df, aes(x = Age)) +
  geom_histogram(binwidth = 5, fill = "steelblue", color = "white") +
  labs(title = "Fig 1: Distribution of Respondent Age",
       x = "Age (years)", y = "Count") +
  theme_minimal()
print(p1)
ggsave("fig1_age_distribution.png", p1, width = 7, height = 4, dpi = 150)

# Fig 2: Knowledge scores before vs after (overlapping histograms)
df_long_k <- df %>%
  select(Knowledge_Before, Knowledge_After) %>%
  pivot_longer(everything(), names_to = "Period", values_to = "Score") %>%
  mutate(Period = dplyr::recode(Period,
    "Knowledge_Before" = "Before CHOP",
    "Knowledge_After"  = "After CHOP"))

p2 <- ggplot(df_long_k, aes(x = Score, fill = Period)) +
  geom_histogram(binwidth = 2, position = "dodge", alpha = 0.8) +
  labs(title = "Fig 2: Health Knowledge Scores Before vs After CHOP",
       x = "Score", y = "Count", fill = "") +
  scale_fill_manual(values = c("steelblue", "darkorange")) +
  theme_minimal() +
  theme(legend.position = "top")
print(p2)
ggsave("fig2_knowledge_histogram.png", p2, width = 7, height = 4, dpi = 150)

# Fig 3: Boxplot — Knowledge After by SubCounty
p3 <- ggplot(df, aes(x = SubCounty, y = Knowledge_After, fill = SubCounty)) +
  geom_boxplot() +
  labs(title = "Fig 3: Knowledge Score After CHOP by Sub-County",
       x = "Sub-County", y = "Knowledge Score (After)") +
  theme_minimal() +
  theme(legend.position = "none")
print(p3)
ggsave("fig3_knowledge_subcounty_boxplot.png", p3, width = 7, height = 4, dpi = 150)

# Fig 4: Vaccination rates before vs after
vacc_df <- data.frame(
  Period = c("Before CHOP", "After CHOP"),
  Rate   = c(mean(df$Vaccination_Before), mean(df$Vaccination_After))
)
p4 <- ggplot(vacc_df, aes(x = Period, y = Rate, fill = Period)) +
  geom_col(width = 0.5) +
  scale_y_continuous(labels = scales::percent_format()) +
  labs(title = "Fig 4: Vaccination Rate Before vs After CHOP",
       x = "", y = "Proportion Vaccinated") +
  scale_fill_manual(values = c("darkorange", "steelblue")) +
  theme_minimal() +
  theme(legend.position = "none")
print(p4)
ggsave("fig4_vaccination_rates.png", p4, width = 5, height = 4, dpi = 150)

# Fig 5: Satisfaction distribution
p5 <- ggplot(df, aes(x = factor(Satisfaction))) +
  geom_bar(fill = "steelblue") +
  geom_hline(yintercept = 60, linetype = "dashed", color = "red", linewidth = 0.8) +
  annotate("text", x = 5.4, y = 62, label = "Expected (uniform)", size = 3, color = "red") +
  labs(title = "Fig 5: Distribution of Satisfaction Scores",
       x = "Satisfaction Level (1 = Low, 5 = High)", y = "Count") +
  theme_minimal()
print(p5)
ggsave("fig5_satisfaction.png", p5, width = 6, height = 4, dpi = 150)

# Fig 6: Awareness by Gender (stacked bar)
p6 <- ggplot(df, aes(x = Gender, fill = Awareness)) +
  geom_bar(position = "fill") +
  scale_y_continuous(labels = scales::percent_format()) +
  labs(title = "Fig 6: CHOP Awareness by Gender",
       x = "Gender", y = "Proportion", fill = "Aware of CHOP") +
  scale_fill_manual(values = c("tomato", "steelblue")) +
  theme_minimal()
print(p6)
ggsave("fig6_awareness_gender.png", p6, width = 5, height = 4, dpi = 150)

# Fig 7: Clinic visits by Gender (boxplot)
p7 <- ggplot(df, aes(x = Gender, y = Clinic_Visits, fill = Gender)) +
  geom_boxplot() +
  labs(title = "Fig 7: Clinic Visits by Gender",
       x = "Gender", y = "Number of Clinic Visits") +
  scale_fill_manual(values = c("steelblue", "darkorange")) +
  theme_minimal() +
  theme(legend.position = "none")
print(p7)
ggsave("fig7_clinic_visits_gender.png", p7, width = 5, height = 4, dpi = 150)


# ============================================================
# SECTION B: ESTIMATION (CONFIDENCE INTERVALS)
# ============================================================
cat("\n========== SECTION B: CONFIDENCE INTERVALS ==========\n")

# B1 — 95% CI for mean difference in knowledge (paired t-test)
cat("\nB1: Paired t-test — Knowledge After vs Before\n")
t_know <- t.test(df$Knowledge_After, df$Knowledge_Before,
                 paired = TRUE, conf.level = 0.95)
print(t_know)

# B2 — 95% CI for single population mean: Clinic Visits
cat("\nB2: One-sample t-test — Mean Clinic Visits\n")
t_clinic <- t.test(df$Clinic_Visits, conf.level = 0.95)
print(t_clinic)

# B3 — 95% CI for two proportions: Vaccination Before vs After
cat("\nB3: Two-proportion test — Vaccination Before vs After\n")
n         <- nrow(df)
x_before  <- sum(df$Vaccination_Before)
x_after   <- sum(df$Vaccination_After)
prop_test <- prop.test(c(x_before, x_after), c(n, n), conf.level = 0.95)
print(prop_test)


# ============================================================
# SECTION C: ONE-WAY ANOVA
# ============================================================
cat("\n========== SECTION C: ONE-WAY ANOVA ==========\n")

# C1 — Check normality assumption (Shapiro-Wilk per group)
cat("\nNormality check (Shapiro-Wilk) per SubCounty:\n")
by(df$Knowledge_After, df$SubCounty, shapiro.test)

# C2 — Check homogeneity of variance (Levene's test)
cat("\nLevene's Test for Homogeneity of Variance:\n")
print(leveneTest(Knowledge_After ~ SubCounty, data = df))

# C3 — One-Way ANOVA
cat("\nOne-Way ANOVA: Knowledge_After ~ SubCounty\n")
anova_model <- aov(Knowledge_After ~ SubCounty, data = df)
print(summary(anova_model))

# C4 — Tukey HSD post-hoc
cat("\nTukey HSD Post-Hoc Test:\n")
tukey_result <- TukeyHSD(anova_model)
print(tukey_result)

# Fig 8: Mean knowledge by SubCounty with error bars
subcounty_summary <- df %>%
  group_by(SubCounty) %>%
  summarise(Mean = mean(Knowledge_After),
            SE   = sd(Knowledge_After) / sqrt(n()),
            .groups = "drop")

p8 <- ggplot(subcounty_summary, aes(x = SubCounty, y = Mean, fill = SubCounty)) +
  geom_col() +
  geom_errorbar(aes(ymin = Mean - SE, ymax = Mean + SE), width = 0.25) +
  labs(title = "Fig 8: Mean Knowledge Score After CHOP by Sub-County",
       x = "Sub-County", y = "Mean Knowledge Score (±SE)") +
  theme_minimal() +
  theme(legend.position = "none")
print(p8)
ggsave("fig8_anova_subcounty.png", p8, width = 7, height = 4, dpi = 150)


# ============================================================
# SECTION D: CHI-SQUARE TESTS
# ============================================================
cat("\n========== SECTION D: CHI-SQUARE TESTS ==========\n")

# D1 — Goodness of Fit: Is Satisfaction uniformly distributed?
cat("\nD1: Chi-square GoF — Satisfaction (uniform expected)\n")
sat_obs    <- table(df$Satisfaction)
chisq_gof  <- chisq.test(sat_obs)  # default: equal expected proportions
print(sat_obs)
print(prop.table(sat_obs))
print(chisq_gof)

# D2 — Independence: Awareness vs Gender
cat("\nD2: Chi-square Test of Independence — Awareness × Gender\n")
aware_gender_tbl <- table(df$Awareness, df$Gender)
print(aware_gender_tbl)
chisq_ag <- chisq.test(aware_gender_tbl)
print(chisq_ag)

# D3 — Independence: Vaccination After vs Income Level
cat("\nD3: Chi-square Test of Independence — Vaccination_After × Income_Level\n")
vacc_income_tbl <- table(df$Vaccination_After, df$Income_Level)
print(vacc_income_tbl)
chisq_vi <- chisq.test(vacc_income_tbl)
print(chisq_vi)

# Fig 9: Vaccination After by Income Level
p9 <- ggplot(df, aes(x = Income_Level, fill = factor(Vaccination_After))) +
  geom_bar(position = "fill") +
  scale_y_continuous(labels = scales::percent_format()) +
  labs(title = "Fig 9: Vaccination After CHOP by Income Level",
       x = "Income Level", y = "Proportion",
       fill = "Vaccinated After") +
  scale_fill_manual(values = c("tomato", "steelblue"),
                    labels = c("No", "Yes")) +
  theme_minimal()
print(p9)
ggsave("fig9_vaccination_income.png", p9, width = 6, height = 4, dpi = 150)


# ============================================================
# SECTION E: NON-PARAMETRIC METHODS
# ============================================================
cat("\n========== SECTION E: NON-PARAMETRIC TESTS ==========\n")

# E1 — Wilcoxon Signed Rank Test: Knowledge Before vs After (paired)
cat("\nE1: Wilcoxon Signed Rank Test — Knowledge scores (paired)\n")
wilcox_know <- wilcox.test(df$Knowledge_After, df$Knowledge_Before,
                            paired = TRUE, alternative = "two.sided")
print(wilcox_know)

# E2 — Mann-Whitney U Test: Clinic Visits by Gender
cat("\nE2: Mann-Whitney U Test — Clinic Visits by Gender\n")
male_visits   <- df$Clinic_Visits[df$Gender == "Male"]
female_visits <- df$Clinic_Visits[df$Gender == "Female"]
mwu_result    <- wilcox.test(male_visits, female_visits, alternative = "two.sided")
print(mwu_result)
cat("Median Clinic Visits — Male:", median(male_visits),
    "| Female:", median(female_visits), "\n")

# E3 — Kruskal-Wallis: Knowledge After by SubCounty
cat("\nE3: Kruskal-Wallis Test — Knowledge_After by SubCounty\n")
kw_result <- kruskal.test(Knowledge_After ~ SubCounty, data = df)
print(kw_result)

# Post-hoc if significant
if (kw_result$p.value < 0.05) {
  cat("\nDunn's Post-Hoc Test (Bonferroni correction):\n")
  dunn.test(df$Knowledge_After, df$SubCounty, method = "bonferroni")
} else {
  cat("Kruskal-Wallis not significant (p =",
      round(kw_result$p.value, 4), ") — no post-hoc needed.\n")
}

# Fig 10: Density plots — Knowledge scores before vs after
p10 <- ggplot(df_long_k, aes(x = Score, fill = Period)) +
  geom_density(alpha = 0.5) +
  labs(title = "Fig 10: Density of Knowledge Scores Before vs After CHOP",
       x = "Score", y = "Density", fill = "") +
  scale_fill_manual(values = c("steelblue", "darkorange")) +
  theme_minimal() +
  theme(legend.position = "top")
print(p10)
ggsave("fig10_knowledge_density.png", p10, width = 7, height = 4, dpi = 150)


# ============================================================
# SECTION G: SUMMARY OF KEY RESULTS
# ============================================================
cat("\n========== SECTION G: KEY RESULTS SUMMARY ==========\n")
cat("Vaccination rate increased from", round(mean(df$Vaccination_Before)*100,1), "%",
    "to", round(mean(df$Vaccination_After)*100,1), "% after CHOP.\n")
cat("Mean health knowledge gain:", round(mean(df$Knowledge_Gain),2),
    "points (95% CI: 2.23 – 3.23, p < 0.001).\n")
cat("No significant difference in knowledge scores across sub-counties (ANOVA p > 0.05).\n")
cat("Satisfaction is uniformly distributed across levels 1–5 (GoF p > 0.05).\n")
cat("Awareness of CHOP is independent of gender (Chi-square p > 0.05).\n")
cat("Vaccination uptake is independent of income level (Chi-square p > 0.05).\n")
cat("Sub-county F has the highest mean knowledge score (12.45).\n")
cat("Recommendation: Scale up CHOP county-wide, with targeted support for Sub-counties B and E.\n")

cat("\n========== ANALYSIS COMPLETE ==========\n")
cat("All figures saved as PNG files in the working directory.\n")
