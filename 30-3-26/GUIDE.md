# From Folder to Submission — Step-by-Step Guide

This guide walks you through everything needed to go from this folder to a complete, submitted assignment. Follow the steps in order.

---

## What You're Starting With

```
30-3-26/
├── Dataset.csv              ← the data
├── analysis.R               ← the full R script (all sections A–G)
├── report.md                ← written report (needs R output filled in)
├── slides.md                ← presentation slides (copy-paste into PowerPoint)
├── requirements.txt         ← Python packages
├── venv/                    ← Python virtual environment
└── STA 2030_Assignment 2.docx  ← original assignment brief
```

## What You Need to Produce

| Deliverable | Format | Source |
|---|---|---|
| Written report | PDF | `report.md` → export to PDF |
| R script | `.R` file | `analysis.R` (already done) |
| Presentation slides | PowerPoint `.pptx` | `slides.md` → build in PowerPoint |

---

## Step 1 — Install R and RStudio

If you don't have R installed:

1. Download **R** from https://cran.r-project.org → choose your OS → install
2. Download **RStudio** from https://posit.co/download/rstudio-desktop → install

> RStudio is the editor. R is the engine. You need both.

---

## Step 2 — Install R Packages

Open RStudio, then in the **Console** (bottom-left panel), paste and run:

```r
install.packages(c("tidyverse", "ggplot2", "car", "dunn.test"))
```

Wait for it to finish. You only need to do this once.

---

## Step 3 — Run the R Script

1. In RStudio, go to **File → Open File** and open `analysis.R` from this folder
2. Set the working directory to this folder — in the Console run:
   ```r
   setwd("C:/Users/Admin/Documents/gift/30-3-26")
   ```
   Or in RStudio: **Session → Set Working Directory → To Source File Location**
3. Click **Source** (top-right of the script editor) or press `Ctrl + Shift + Enter`

**What happens:**
- All statistical output prints to the Console
- 10 PNG figures are saved into this folder (`fig1_age_distribution.png` through `fig10_knowledge_density.png`)

> If you get an error about a missing package, run `install.packages("packagename")` in the Console.

---

## Step 4 — Copy R Output into the Report

Open `report.md` in any text editor (VS Code works great).

In several places the report says things like:
> *(Exact values from R output: `summary(aov(...))`)*

Replace those placeholders with the **actual numbers from your R Console output**. Key spots to update:

| Section | What to copy from R |
|---|---|
| C — ANOVA table | The full table from `summary(anova_model)` — SS, MS, F, p-value |
| C — Levene's test | F-value and p-value from `leveneTest()` output |
| C — Shapiro-Wilk | p-values per sub-county from `by(df$Knowledge_After, ...)` |
| D — Chi-square exact values | χ², df, p-value from each `chisq.test()` output |
| E — Mann-Whitney | W statistic and p-value from `wilcox.test()` for clinic visits |

For most other numbers (means, CIs, Wilcoxon, proportions) the report already has the correct values — just verify they match your output.

---

## Step 5 — Export the Report to PDF

You have three options, pick whichever is easiest:

### Option A — VS Code (recommended)
1. Install the **Markdown PDF** extension in VS Code
   - Press `Ctrl + Shift + X` → search "Markdown PDF" → install
2. Open `report.md` in VS Code
3. Right-click anywhere in the file → **Markdown PDF: Export (pdf)**
4. A PDF is saved in the same folder automatically

### Option B — Pandoc (command line)
If you have Pandoc installed:
```bash
pandoc report.md -o report.pdf --pdf-engine=wkhtmltopdf
```

### Option C — Word then Save as PDF
1. Copy all the text from `report.md`
2. Paste into a new Word document
3. Fix the formatting manually (headings, tables, bold)
4. **File → Save As → PDF**

> Tables in markdown look like `|col|col|` — in Word you'll need to reformat them as actual Word tables for a clean look.

---

## Step 6 — Build the PowerPoint

Open `slides.md` in any text editor. Each slide is separated by `---` and labeled `## Slide N: Title`.

**Process:**
1. Open PowerPoint → New Presentation
2. Choose a clean theme (dark blue header + white body works well)
3. For each slide in `slides.md`:
   - Add a new slide in PowerPoint
   - Copy the content under the `## Slide N` heading
   - Paste into the slide and format (heading → title box, bullets → body box)
4. Insert the PNG figures where the slides mention *(See Fig X)*:
   - **Slide 5** → insert `fig4_vaccination_rates.png`
   - **Slide 6** → insert `fig2_knowledge_histogram.png` or `fig10_knowledge_density.png`
   - **Slide 8** → insert `fig8_anova_subcounty.png`
   - **Slide 9** → insert `fig9_vaccination_income.png`

**12 slides total** — the last slide is your conclusion/recommendation.

> Tip: Use PowerPoint's **Insert → Pictures → This Device** to add the PNG files.

---

## Step 7 — Final Check Before Submitting

Go through this checklist:

### Report PDF
- [ ] All section headings present (A through G)
- [ ] Every test shows: H₀, H₁, test statistic, p-value, decision, interpretation
- [ ] R output numbers match what's in the report
- [ ] Tables are formatted properly (not raw markdown `|` characters)
- [ ] Figures are referenced (e.g., "See Fig 4")
- [ ] Section G has clear, stat-backed recommendations

### R Script
- [ ] `analysis.R` runs from top to bottom with no errors
- [ ] Working directory is set at the top (or note to set it manually)
- [ ] All 10 figures generate successfully

### PowerPoint
- [ ] 12 slides, all readable
- [ ] At least 4 figures inserted
- [ ] Key numbers visible (the CI values, p-values, percentage changes)
- [ ] Group name / course info on title slide

### Submission
- [ ] Report exported as **PDF** (not Word, not markdown)
- [ ] File named clearly e.g. `STA2030_Assignment2_[YourName].pdf`
- [ ] You are submitting **individually** even though it's a group assignment
- [ ] No content is identical to another group's submission

---

## Quick Reference — Key Results

In case you need to sanity-check your R output against expected values:

| Metric | Expected Value |
|---|---|
| Mean Knowledge Gain | ~2.73 points |
| 95% CI for gain | (2.23, 3.23) |
| Vaccination Before | 39.33% |
| Vaccination After | 65.00% |
| ANOVA p-value (knowledge by sub-county) | ~0.88 (not significant) |
| Wilcoxon p-value (knowledge gain) | < 0.000001 |
| Chi-sq GoF p-value (Satisfaction) | ~0.955 (uniform) |
| Awareness × Gender p-value | ~0.89 (independent) |
| Vaccination × Income p-value | ~0.25 (independent) |

If your R output is significantly different from these, double-check that `Dataset.csv` loaded correctly (should be 300 rows, 12 columns).

---

## If Something Breaks

**R script errors:**
- `could not find function "ggplot"` → run `library(ggplot2)` or reinstall the package
- `object 'df' not found` → you skipped a line; run the script from the top
- `no applicable method` → check that column names in the script match `Dataset.csv` exactly

**PDF export issues:**
- VS Code Markdown PDF not working → try Option C (Word)
- Tables look broken in PDF → reformat as proper Word tables before exporting

**Missing figures in PowerPoint:**
- Figures only exist after running `analysis.R` — make sure Step 3 completed fully
- Check this folder for `fig1_*.png` through `fig10_*.png`
