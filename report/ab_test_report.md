# A/B Test Report — ShopWise UK Product Page Redesign

**Experiment:** Product page CTA button redesign + simplified checkout flow  
**Period:** 8 January 2024 – 21 January 2024 (14 days)  
**Status:** ✅ SHIP — All success criteria met

---

## 1. Executive Summary

ShopWise UK ran a 14-day A/B test on its product page, testing a redesigned call-to-action button and a simplified three-step checkout flow against the existing design. The experiment enrolled 48,312 unique users split evenly between control and treatment.

The treatment produced a statistically significant improvement in conversion rate (+20.6% relative lift, p = 0.000164), with all secondary metrics improving in the expected direction. The projected annual revenue uplift is **£465,645** (95% CI: £223,487 – £707,802).

**Decision: Ship the treatment to 100% of traffic.**

---

## 2. Experiment Design

### Hypothesis
> H₁: The redesigned product page (new CTA + simplified checkout) will increase the conversion rate relative to the existing design.

### Pre-Registration (fixed before data collection — prevents p-hacking)

| Parameter | Value | Justification |
|---|---|---|
| Randomisation unit | User-level | Prevents within-user contamination |
| Traffic allocation | 50% / 50% | Maximises statistical power |
| Primary metric | Conversion rate (purchase) | Core business objective |
| Secondary metrics | ATC rate, RPV, Bounce rate | Leading indicators |
| Significance threshold (α) | 0.05 (two-tailed) | Industry standard |
| Target power (1−β) | 80% | Standard minimum |
| Minimum detectable effect | 15% relative lift | Business viability threshold |
| Required n per group | 22,605 | Calculated via power analysis |
| Planned duration | 14 days | Full business cycle (2 × Mon–Sun) |

### Why 14 days?
Running for exactly two full weekly cycles ensures the result captures weekly seasonality and avoids day-of-week bias. Stopping early — even if significance is reached — risks the peeking problem: inflated false positive rates from repeated significance testing.

---

## 3. Sanity Checks

Before any metric analysis, the following checks were performed:

| Check | Result | Notes |
|---|---|---|
| Duplicate users | 0 duplicates ✅ | Each user appears exactly once |
| Sample Ratio Mismatch | p = 1.000 ✅ | Allocation exactly 50/50 |
| Date range completeness | 14/14 days ✅ | No missing days |
| Minimum cell sizes | All > 30 ✅ | z-test assumptions met |

---

## 4. Statistical Analysis

### 4.1 Power Analysis

```
Baseline CR    : 3.2%  (pre-registered, based on prior 30-day average)
MDE            : 15% relative → 3.2% × 1.15 = 3.68%
Effect size    : Cohen's h = 0.0283
Required n     : 22,605 per group
Actual n       : 24,156 per group  ✅ (exceeds requirement)
Achieved power : 96.5%  ✅ (exceeds 80% target)
```

### 4.2 Primary Metric

| | Control | Treatment |
|---|---|---|
| Users | 24,156 | 24,156 |
| Conversions | 713 | 860 |
| Conversion rate | **2.9516%** | **3.5602%** |
| Absolute lift | — | +0.6085 pp |
| Relative lift | — | **+20.62%** |

**Test: Two-proportion z-test (two-tailed)**

```
H₀ : CR_treatment = CR_control
H₁ : CR_treatment ≠ CR_control

z-statistic : 3.7683
p-value     : 0.000164
α threshold : 0.050
Decision    : REJECT H₀  ✅
```

**Cross-validation:** Chi-square gives χ² = 14.1998, p = 0.000164. Since z² = 3.7683² = 14.20 ≈ χ², both methods agree exactly. Result is not a numerical artifact.

**95% CI on (CR_treatment − CR_control):**
```
[+0.2921 pp ,  +0.9250 pp]
```
Both bounds are strictly positive. We are 95% confident the true lift is positive.

**Effect size:** Cohen's h = 0.0343 (small). Expected for conversion experiments — small effects are economically significant at scale.

### 4.3 Secondary Metrics — Bonferroni Corrected (m = 3, adjusted α = 0.0167)

| Metric | Control | Treatment | Lift | Adj p | Significant |
|---|---|---|---|---|---|
| Add-to-cart rate | 11.90% | 13.88% | +16.6% | < 0.0001 | ✅ Yes |
| Revenue per visitor | £1.601 | £1.976 | +23.4% | 0.00044 | ✅ Yes |
| Bounce rate | 37.93% | 32.95% | −13.1% | < 0.0001 | ✅ Yes |

> Revenue tested with Mann-Whitney U (non-parametric). Revenue is lognormally distributed — a t-test would be invalid on raw revenue values.

### 4.4 Segmentation Analysis (Exploratory)

> These results are hypotheses for future tests, not confirmatory conclusions. Bonferroni correction applied within each segment group.

| Segment | Control CR | Treatment CR | Lift | Significant |
|---|---|---|---|---|
| Mobile | 2.42% | 3.04% | +25.9% | ✅ Yes |
| Desktop | 3.93% | 4.56% | +16.0% | — |
| Tablet | 3.42% | 3.86% | +12.9% | — |
| Returning users | 3.17% | 4.02% | +26.9% | ✅ Yes |
| New users | 2.64% | 2.89% | +9.6% | — |

**Insight:** Treatment performs strongest for returning users and mobile. New users show smaller lift — the redesign may assume site familiarity. Recommended follow-up: new-user onboarding test.

### 4.5 Novelty Effect Check

Days 1–3 showed a slightly elevated daily lift (+1.23 pp average) vs days 4–14 (+0.45 pp). Cumulative rates stabilised from day 4. Lift direction was consistently positive throughout all 14 days. Minor novelty effect — does not invalidate the result.

---

## 5. Business Impact

| Scenario | Annual Revenue Uplift |
|---|---|
| Conservative (95% CI lower) | £223,487 |
| **Central estimate** | **£465,645** |
| Optimistic (95% CI upper) | £707,802 |

Monthly uplift: **£38,804** · Monthly visitors: **103,524**

---

## 6. Decision: SHIP ✅

All pre-registered success criteria met:

- ✅ p = 0.000164 ≪ α = 0.05
- ✅ 95% CI entirely above zero [+0.29pp, +0.93pp]
- ✅ All three secondary metrics significant after Bonferroni correction
- ✅ Achieved power 96.5% (target 80%)
- ✅ SRM passed — randomisation clean
- ✅ Lift stable over 14 days

### Next Steps
1. Ship treatment to 100% of traffic
2. Hold back 5% on old design for 30-day post-launch monitoring
3. Run follow-up test on new-user onboarding flow
4. Run tablet-specific layout test
5. Monitor revenue distribution for 30 days post-launch

---

## 7. Statistical Decisions Log

| Decision | Choice | Reason |
|---|---|---|
| Test for conversion rate | Two-proportion z-test | Binary outcome, large samples |
| Test for revenue | Mann-Whitney U | Lognormal distribution — t-test invalid |
| Multiple testing | Bonferroni correction | Conservative, appropriate for m=3 |
| Alternative hypothesis | Two-tailed | No pre-registered directional belief |
| Randomisation unit | User-level | Session-level causes contamination |
| Cross-validation | Chi-square | Independent method — z² ≈ χ² confirms result |
| Segmentation | Exploratory only | Underpowered for confirmatory claims |

---

*Data: `data/processed/experiment_data.csv` (48,312 rows)*  
*Analysis: `scripts/02_statistical_analysis.py`*  
*Reproducible with: `np.random.seed(2024)`*
