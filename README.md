# 🧪 A/B Testing Case Study — ShopWise UK Product Page Redesign

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![SciPy](https://img.shields.io/badge/Stats-SciPy%20%2F%20Statsmodels-00539C?style=flat-square)
![Method](https://img.shields.io/badge/Method-Two--Proportion%20Z--Test-success?style=flat-square)
![Impact](https://img.shields.io/badge/Annual%20Impact-%C2%A3465%2C645-brightgreen?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

> End-to-end A/B test analysis examining a checkout-funnel redesign across 48,312 users.
> Implements power calculations, segmentation controls, novelty effect detection, and business impact projection.

## 🔴 Live Dashboard

[![View Live Dashboard](https://img.shields.io/badge/Live%20Dashboard-View%20Now-1d4ed8?style=for-the-badge&logoColor=white)](https://RidhimaGupta4.github.io/AB-Testing-Case-Study/dashboard/)

---

## Project Summary

ShopWise UK tested a redesigned product page — a new CTA button and a simplified 3-step checkout flow — against the existing design over 14 days and 48,312 unique users.

**Business question:** Does the redesigned product page convert more visitors into buyers, and is the effect large enough to justify a full rollout?

**Answer: Yes. Ship it.**

| Metric | Control | Treatment | Relative Lift | Result |
|:---|:---:|:---:|:---:|:---|
| Conversion Rate | 2.9516% | 3.5602% | +20.6% | p = 0.000164 |
| Add-to-Cart Rate | 11.90% | 13.88% | +16.6% | p < 0.0001 (adj) |
| Revenue per Visitor | £1.601 | £1.976 | +23.4% | p = 0.00044 (adj) |
| Bounce Rate | 37.93% | 32.95% | −13.1% | p < 0.0001 (adj) |
| Projected Annual Uplift | — | — | — | £465,645 |

Every metric moved in the right direction. The conversion lift is statistically significant, the confidence interval sits entirely above zero, and the result held steady across the full 14-day window with no signs of novelty inflation. The recommendation is to ship.

---

## 🗂️ Repository Structure

```
ab-testing-case-study/
│
├── scripts/
│   ├── 01_generate_data.py          # Experiment data generation (48,312 users)
│   ├── 02_statistical_analysis.py   # Full statistical analysis pipeline
│   └── 03_charts.py                 # 7 publication-quality charts
│
├── data/
│   └── processed/
│       ├── experiment_data.csv      # 48,312 rows — one row per user
│       ├── daily_summary.csv        # Daily aggregates by group (28 rows)
│       ├── group_summary.csv        # Top-level group summary
│       ├── analysis_results.json    # Full results JSON (used by dashboard)
│       ├── daily_summary.json       # Daily data for dashboard
│       └── group_summary.json       # Group summary for dashboard
│
├── dashboard/
│   └── index.html                   # Self-contained interactive dashboard
│
├── report/
│   └── ab_test_report.md            # Full written analysis report
│
├── outputs/
│   ├── 01_primary_results_summary.png
│   ├── 02_cumulative_conversion_rate.png
│   ├── 03_confidence_intervals.png
│   ├── 04_segmentation_analysis.png
│   ├── 05_power_analysis_curve.png
│   ├── 06_revenue_distribution.png
│   └── 07_business_impact.png
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 📊 Dashboard

Open `dashboard/index.html` directly in any browser. No server, no configuration, no dependencies beyond the file itself.

| Tab | Content |
|:---|:---|
| **Overview** | KPI cards · Metric delta bars · Experiment validation checklist |
| **Statistics** | Hypothesis test results · Power analysis · Secondary metrics · CI plot |
| **Segmentation** | Lift by device · User type · Product category · Bonferroni corrected |
| **Timeline** | Cumulative conversion rate day-by-day · Novelty effect annotation |
| **Business Impact** | Monthly and annual revenue uplift · Conservative / central / optimistic scenarios |

---

## 📐 Statistical Methodology

### Experiment Design

Everything below was fixed before data collection began. This matters because changing thresholds or metrics after seeing results — even unconsciously — inflates the false positive rate and makes any conclusion unreliable. Pre-registration is not optional hygiene; it is what makes the result trustworthy.

| Parameter | Value | Reason |
|:---|:---:|:---|
| Randomisation unit | User-level | Session-level causes within-user contamination |
| Traffic split | 50 / 50 | Symmetric split maximises power for a given total n |
| Primary metric | Conversion rate | Direct measure of the business objective |
| Secondary metrics | ATC rate, RPV, Bounce rate | Funnel leading indicators |
| Significance level (α) | 0.05 two-tailed | Standard threshold — no directional assumption |
| Target power (1−β) | 80% | Accepted minimum for product experiments |
| Minimum detectable effect | 15% relative lift | Smallest lift that justifies infrastructure cost |
| Required n per group | 22,605 | Calculated from power analysis before launch |
| Planned duration | 14 days | Two full Mon–Sun cycles to capture weekly patterns |

**On the choice of 14 days:** Running for exactly two weekly cycles ensures the result is not distorted by day-of-week traffic patterns. Stopping as soon as significance is reached — even if the p-value looks compelling — causes the peeking problem. Every time you check an in-flight experiment and decide whether to stop, you are running an implicit test, and the false positive rate compounds. The duration was set in advance and not adjusted.

---

### Primary Test — Two-Proportion Z-Test

The correct test for comparing two binary conversion rates across large independent samples. Both groups are independent (user-level randomisation), the outcome is binary (purchased or not), and both samples are large enough for the normal approximation to hold.

$$H_0: CR_{\text{treatment}} = CR_{\text{control}}$$

$$H_1: CR_{\text{treatment}} \neq CR_{\text{control}} \quad \text{(two-tailed)}$$

$$Z = \frac{\hat{p}_T - \hat{p}_C}{\sqrt{\hat{p}(1-\hat{p})\left(\frac{1}{n_T} + \frac{1}{n_C}\right)}} = 3.7683 \implies p = 0.000164$$

$H_0$ is rejected. The result was cross-validated using an independent chi-square test, which gave $\chi^2 = 14.1998$, $p = 0.000164$. Since $Z^2 = 3.7683^2 = 14.20 \approx \chi^2$, both methods agree to four decimal places. This rules out a numerical artifact in either test.

---

### Confidence Interval on Absolute Lift

$$
\text{CI}_{95\%}
=
(\hat{p}_T - \hat{p}_C)
\pm
Z_{0.975} \cdot \text{SE}_{\mathrm{diff}}
=
[+0.2921\text{ pp},\ +0.9250\text{ pp}]
$$

Both bounds are strictly positive. The lift is not only statistically significant — the entire plausible range of its true value is above zero. Even the conservative estimate represents a meaningful conversion improvement.

---

### Power Analysis

Sample size was calculated before the experiment launched using the pre-registered baseline and minimum detectable effect.

```
Baseline conversion rate  : 3.20% (30-day prior average)
Minimum detectable effect : 15% relative lift → 3.20% × 1.15 = 3.68%
Effect size (Cohen's h)   : 0.0283
Required n per group      : 22,605
Actual n per group        : 24,156
Target power (1−β)        : 80%
Achieved power            : 96.5%
```

### Secondary Metrics — Bonferroni Correction

Three metrics tested simultaneously. Bonferroni-adjusted α = 0.05/3 = 0.0167. All three significant after correction.

### Revenue — Mann-Whitney U (Non-Parametric)

Revenue per visitor is lognormally distributed. A t-test assumes normality and would be inappropriate on raw revenue values. Mann-Whitney U tests for stochastic dominance without normality assumptions.

### Segmentation — Exploratory Only

Segmentation results are hypotheses for future confirmatory tests. Bonferroni correction applied within each segment group to reduce false discovery risk.

### Novelty Effect Check

Day-by-day cumulative conversion rates tracked throughout the experiment. Minor early boost detected (days 1–3); lift stabilised and remained consistently positive from day 4 onward. Minor novelty effect — result is valid.

### Sample Ratio Mismatch (SRM)

```
Chi-square on allocation: χ² = 0.000, p = 1.000
Allocation exactly 50/50 — randomisation is clean 
```

---

## 🛡️ Data Integrity

| Check | Result |
|---|---|
| Duplicate users | 0 (none found) |
| SRM check | Passed (p = 1.000) |
| Missing days | 0 (all 14 days present) |
| Minimum cell sizes | All > 30 (z-test assumptions met) |
| Random seed | Fixed at 2024 (fully reproducible) |

---

## 🛠️ Quick Start

```bash
# 1. Clone
git clone https://github.com/RidhimaGupta4/AB-Testing-Case-Study.git
cd AB-Testing-Case-Study

# 2. Install
pip install -r requirements.txt

# 3. Generate experiment data
python scripts/01_generate_data.py

# 4. Run full statistical analysis
python scripts/02_statistical_analysis.py

# 5. Generate all charts
python scripts/03_charts.py

# 6. Open dashboard
open dashboard/index.html
```

---

## 📊 Data Schema

### `experiment_data.csv` — 48,312 rows (one per user)

| Column | Type | Description |
|---|---|---|
| `user_id` | string | Unique user identifier |
| `group` | string | `control` or `treatment` |
| `visit_date` | date | Date of experiment visit |
| `day_number` | int | Day 0–13 of experiment |
| `device` | string | `mobile`, `desktop`, `tablet` |
| `category` | string | Product category browsed |
| `is_new_user` | int | 1 = new user, 0 = returning |
| `converted` | int | 1 = purchased, 0 = did not |
| `add_to_cart` | int | 1 = added to cart |
| `revenue_gbp` | float | Order value (£), 0 if no purchase |
| `session_duration_sec` | int | Session length in seconds |
| `bounced` | int | 1 = left without interaction |

---

## 📈 Real Data Benchmarks Used

All synthetic parameters are grounded in publicly documented real-world benchmarks:

| Parameter | Value Used | Source |
|---|---|---|
| Baseline conversion rate | 3.2% | Statista UK E-Commerce Report 2023 |
| Average order value | £45.50 | ONS Retail Sales Index 2023 |
| Mobile traffic share | 63% | Ofcom Connected Nations 2023 |
| New user share | 41% | Industry average for established retailers |
| Typical A/B test lift | 15–20% MDE | Optimizely & VWO published benchmarks |

### Replacing with Real Data

To run this analysis on real data, replace `data/processed/experiment_data.csv` with your export and ensure these columns are present:

```python
required_cols = [
    'user_id', 'group', 'visit_date',
    'converted', 'revenue_gbp', 'device'
]
```

Public dataset option: [Kaggle Marketing A/B Testing](https://www.kaggle.com/datasets/faviovaz/marketing-ab-testing) — 588,101 rows, binary conversion outcome.

---

## 🧰 Tech Stack

| Tool | Version | Role |
|---|---|---|
| Python | 3.10+ | Analysis pipeline |
| pandas | 2.0+ | Data manipulation |
| numpy | 1.24+ | Numerical computation |
| scipy | 1.10+ | Statistical tests (z-test, chi-square, Mann-Whitney) |
| statsmodels | 0.14+ | Power analysis, proportion tests |
| matplotlib | 3.7+ | Chart generation |
| Chart.js | 4.4.1 | Interactive dashboard |
| HTML / CSS / JS | — | Self-contained dashboard |

---

## 💼 Skills Demonstrated

- Experiment design with pre-registration (prevents p-hacking)
- Sample size and power calculation before data collection
- Sample Ratio Mismatch detection (critical sanity check)
- Two-proportion z-test with chi-square cross-validation
- Non-parametric testing for skewed metrics (Mann-Whitney U)
- Multiple comparisons correction (Bonferroni)
- Confidence interval construction and interpretation
- Novelty effect detection via cumulative tracking
- Segmentation analysis with appropriate exploratory framing
- Business impact projection with uncertainty quantification
- Clear go/no-go recommendation backed by evidence

---

## 🔍 Visual Insights

### Primary Results Summary
![Primary Results](outputs/01_primary_results_summary.png)

### Cumulative Conversion Rate — 14 Days
![Cumulative CR](outputs/02_cumulative_conversion_rate.png)

### 95% Confidence Intervals
![Confidence Intervals](outputs/03_confidence_intervals.png)

### Segmentation Analysis
![Segmentation](outputs/04_segmentation_analysis.png)

### Power Analysis Curve
![Power Analysis](outputs/05_power_analysis_curve.png)

### Revenue Distribution
![Revenue](outputs/06_revenue_distribution.png)

### Business Impact Projection
![Business Impact](outputs/07_business_impact.png)

---

## 📄 Licence

MIT — free to use and adapt

---

## 🙋 Author

Built as a UK data analyst / data scientist portfolio project.

**Connect:** [LinkedIn](https://www.linkedin.com/in/ridhimagupta1623/) · [GitHub](https://github.com/RidhimaGupta4) 

> If this project helped you, please ⭐ star the repo — it helps others find it.

## 📁 Explore More Projects

*   **[🏠 UK Property Price Predictor](https://github.com/RidhimaGupta4/UK-Property-Price-Predictor)** — High-accuracy ML pipeline for real estate valuation and geospatial analysis.
*   **[🛒 E-commerce Churn Analysis](https://github.com/RidhimaGupta4/Ecommerce-Churn-Analysis)** — Customer segmentation, RFM modeling, and retention strategy.
*   **[🇬🇧 UK Cost-of-Living Dashboard](https://github.com/RidhimaGupta4/UK-Cost-of-Living)** — Regional economic data storytelling and affordability mapping.
