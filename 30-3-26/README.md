# STA 2030-A: Statistical Inference — Assignment 2
**Community Health Outreach Program (CHOP) Analysis**
Summer Semester 2026 | Instructor: Joyce Kiarie, Ph.D

---

## Folder Contents

| File | Description |
|---|---|
| `Dataset.csv` | Raw dataset — 300 respondents, 12 variables |
| `analysis.R` | Complete R script — all sections A–G |
| `report.md` | Full written report with statistics, tables, and interpretations |
| `slides.md` | Presentation slides (copy-paste ready for PowerPoint) |
| `STA 2030_Assignment 2.docx` | Original assignment brief from instructor |
| `requirements.txt` | Python package list (pandas, scipy, numpy) |
| `venv/` | Python virtual environment |
| `fig1_*.png … fig10_*.png` | Generated plots (created when you run `analysis.R`) |

---

## How to Run the R Script

### Requirements
- R (≥ 4.0) — download from https://cran.r-project.org
- RStudio (recommended) — download from https://posit.co

### Install R Packages (run once in R console)
```r
install.packages(c("tidyverse", "ggplot2", "car", "dunn.test"))
```

### Run the Analysis
1. Open RStudio
2. Set working directory to this folder:
   ```r
   setwd("C:/Users/Admin/Documents/gift/30-3-26")
   ```
3. Open `analysis.R` and click **Source** (or press Ctrl+Shift+Enter)
4. All output prints to the console; 10 PNG figures are saved to this folder

### Script Structure
| Section | What it does |
|---|---|
| A | Descriptive stats + 7 ggplot visualizations |
| B | Confidence intervals (paired t-test, one-sample t, two-proportion) |
| C | One-Way ANOVA + Levene's test + Tukey HSD post-hoc |
| D | Chi-square GoF + two independence tests |
| E | Wilcoxon Signed Rank + Mann-Whitney U + Kruskal-Wallis |
| G | Summary of key results printed to console |

---

## How to Use the Python Virtual Environment

The `venv/` folder contains a Python environment with pandas, scipy, and numpy for any supplementary data work.

### Activate (Windows Git Bash / terminal)
```bash
source venv/Scripts/activate
```

### Activate (Windows CMD)
```cmd
venv\Scripts\activate.bat
```

### Install packages (if not already installed)
```bash
pip install -r requirements.txt
```

### Deactivate when done
```bash
deactivate
```

### Run a Python analysis script
```bash
python your_script.py
```

---

## How to Use the Slides (slides.md → PowerPoint)

1. Open `slides.md` in any text editor or VS Code
2. Each slide is separated by `---` and labeled `## Slide N: Title`
3. **For each slide:**
   - Copy the content below the `## Slide N` heading
   - Paste into a new PowerPoint slide
   - Apply your group's theme/formatting
4. Insert the corresponding PNG figures (fig4, fig8, fig9, etc.) where noted
5. Suggested PowerPoint theme: dark blue header, white body text

---

## Submission Checklist

- [ ] Run `analysis.R` fully — all 10 figures generated
- [ ] Copy R output into `report.md` where marked *(See R output)*
- [ ] Export `report.md` to PDF (use Pandoc, VS Code Markdown PDF, or Word)
- [ ] Build PowerPoint from `slides.md`
- [ ] Attach `analysis.R` as the R script deliverable
- [ ] Each group member submits **individually** as a PDF
- [ ] Verify no identical code/text with other groups

---

## Key Results at a Glance

| Finding | Value | Significance |
|---|---|---|
| Vaccination rate increase | +25.67 pp (39% → 65%) | p < 0.001 |
| Knowledge score gain | +2.73 points | p < 0.001 |
| Sub-county difference (ANOVA) | F ≈ 0.35 | p ≈ 0.88 (NS) |
| Satisfaction distribution | χ² = 0.67 | p ≈ 0.955 (uniform) |
| Awareness × Gender | χ² ≈ 0.02 | p ≈ 0.89 (independent) |
| Vaccination × Income | χ² ≈ 2.80 | p ≈ 0.25 (independent) |
