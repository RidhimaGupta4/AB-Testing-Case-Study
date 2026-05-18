"""
A/B Testing Case Study — Data Generation
=========================================
Scenario: ShopWise UK (mid-size UK e-commerce) tests a redesigned
product-page CTA button + simplified checkout flow.

Real-world benchmarks used (all publicly documented):
  - UK e-commerce baseline conversion rate: 2.9–3.5%
    Source: Statista UK E-Commerce Report 2023
  - Average UK online order value: £43–£47
    Source: ONS Retail Sales Index 2023
  - Mobile share of UK e-commerce traffic: ~60–65%
    Source: Ofcom Connected Nations 2023
  - Typical detectable lift in enterprise A/B tests: 10–20%
    Source: Optimizely & VWO published benchmarks

Experiment Design (pre-registered):
  - Randomisation unit : user_id (user-level, not session-level)
  - Traffic split      : 50% control / 50% treatment
  - Primary metric     : Conversion rate (purchase within session)
  - Secondary metrics  : Revenue per visitor, Add-to-cart rate
  - Test duration      : 14 days (calculated from power analysis)
  - Minimum detectable effect (MDE): 15% relative lift
  - Statistical significance threshold: α = 0.05 (two-tailed)
  - Power              : 1 - β = 0.80

NOTE: To replace with real data, swap the CSV path in 02_statistical_analysis.py
with any real A/B test export. Recommended public dataset:
  Kaggle "Marketing A/B Testing" — 588k rows, binary conversion outcome
  https://www.kaggle.com/datasets/faviovaz/marketing-ab-testing
"""

import pandas as pd
import numpy as np
import json, os

np.random.seed(2024)  # Fixed seed — fully reproducible

# ── Experiment parameters (pre-registered before data collection) ─────────────
CONTROL_CR      = 0.032          # 3.2% baseline conversion (UK e-comm benchmark)
TREATMENT_CR    = 0.0378         # 3.78% → 18.1% relative lift
AVG_ORDER_VALUE = 45.50          # £45.50 average order value (ONS benchmark)
N_USERS         = 48_312         # Total users in 14-day window
TEST_DAYS       = 14
START_DATE      = pd.Timestamp("2024-01-08")   # Post-holiday, stable traffic

DEVICES    = ["mobile", "desktop", "tablet"]
DEVICE_W   = [0.63, 0.31, 0.06]               # Ofcom 2023

DEVICE_CR_MULTIPLIER = {          # Mobile converts lower than desktop (industry norm)
    "mobile":  0.78,
    "desktop": 1.28,
    "tablet":  0.94,
}

NEW_USER_SHARE   = 0.41           # 41% new users (realistic for established retailer)
TRAFFIC_BY_DOW   = [0.12, 0.13, 0.15, 0.15, 0.16, 0.16, 0.13]  # Mon–Sun

CATEGORIES = ["Electronics", "Clothing", "Home & Garden", "Sports", "Beauty"]
CAT_W      = [0.22, 0.30, 0.18, 0.15, 0.15]
CAT_AOV    = {                    # Category-level average order value
    "Electronics": 89.0,
    "Clothing":    38.5,
    "Home & Garden": 52.0,
    "Sports":      44.0,
    "Beauty":      29.5,
}


def assign_date(n_users, start_date, n_days, traffic_by_dow):
    """Assign visit dates weighted by day-of-week traffic pattern."""
    dates = []
    for d in range(n_days):
        day = start_date + pd.Timedelta(days=d)
        dow = day.weekday()
        n = int(n_users * traffic_by_dow[dow])
        dates.extend([day] * n)
    # Trim or pad to exact n_users
    np.random.shuffle(dates)
    return dates[:n_users]


def build_experiment_data():
    n = N_USERS

    # ── User-level assignment ─────────────────────────────────────────────────
    user_ids   = [f"USR{i:06d}" for i in range(1, n + 1)]
    groups     = np.where(np.arange(n) % 2 == 0, "control", "treatment")  # Strict alternation → clean 50/50
    np.random.shuffle(groups)      # Shuffle so assignment isn't sequential

    devices    = np.random.choice(DEVICES, size=n, p=DEVICE_W)
    is_new     = np.random.binomial(1, NEW_USER_SHARE, size=n).astype(bool)
    categories = np.random.choice(CATEGORIES, size=n, p=CAT_W)
    dates      = assign_date(n, START_DATE, TEST_DAYS, TRAFFIC_BY_DOW)

    # ── Conversion outcome ────────────────────────────────────────────────────
    # Base rate depends on group + device + (slight) novelty decay for treatment
    day_numbers = np.array([(d - START_DATE).days for d in dates])

    base_cr = np.where(groups == "control", CONTROL_CR, TREATMENT_CR)

    # Device multiplier
    dev_mult = np.array([DEVICE_CR_MULTIPLIER[d] for d in devices])

    # Novelty effect: treatment has a small decay in days 1–3, stabilises
    # This is realistic and we check for it in analysis
    novelty_mult = np.where(
        (groups == "treatment") & (day_numbers <= 2),
        1.12,   # Slight novelty boost early on
        1.0
    )

    # New-user effect: new users convert slightly less
    new_user_mult = np.where(is_new, 0.88, 1.06)

    effective_cr = np.clip(base_cr * dev_mult * novelty_mult * new_user_mult, 0, 1)
    converted    = np.random.binomial(1, effective_cr)

    # ── Revenue (only for converters) ────────────────────────────────────────
    aov_base  = np.array([CAT_AOV[c] for c in categories])
    # Revenue is lognormal around the AOV — realistic, skewed distribution
    revenue   = np.where(
        converted == 1,
        np.random.lognormal(mean=np.log(aov_base) - 0.08, sigma=0.55),
        0.0
    )

    # ── Add-to-cart (higher than conversion — not everyone who adds buys) ────
    atc_rate  = np.where(groups == "control", CONTROL_CR * 3.2, TREATMENT_CR * 3.1)
    atc_rate  = np.clip(atc_rate * dev_mult * new_user_mult, 0, 1)
    add_to_cart = np.maximum(converted, np.random.binomial(1, atc_rate))

    # ── Session duration (seconds) — treatment has slightly longer engagement ──
    base_duration = np.random.lognormal(mean=5.1, sigma=0.8, size=n)  # ~165 sec median
    treatment_boost = np.where(groups == "treatment", 1.06, 1.0)
    session_duration = np.round(base_duration * treatment_boost, 0)

    # ── Bounce (left without interaction) ────────────────────────────────────
    bounce_rate = np.where(groups == "control", 0.38, 0.33)  # Treatment reduces bounce
    bounced     = np.random.binomial(1, bounce_rate)

    df = pd.DataFrame({
        "user_id":          user_ids,
        "group":            groups,
        "visit_date":       [d.strftime("%Y-%m-%d") for d in dates],
        "day_number":       day_numbers,
        "device":           devices,
        "category":         categories,
        "is_new_user":      is_new.astype(int),
        "converted":        converted,
        "add_to_cart":      add_to_cart,
        "revenue_gbp":      revenue.round(2),
        "session_duration_sec": session_duration.astype(int),
        "bounced":          bounced,
    })

    return df


def build_daily_summary(df):
    """Daily aggregates — used for novelty effect and cumulative analysis."""
    daily = df.groupby(["day_number", "visit_date", "group"]).agg(
        users        = ("user_id", "count"),
        conversions  = ("converted", "sum"),
        atc          = ("add_to_cart", "sum"),
        revenue      = ("revenue_gbp", "sum"),
        bounces      = ("bounced", "sum"),
    ).reset_index()
    daily["conversion_rate"] = (daily["conversions"] / daily["users"] * 100).round(3)
    daily["atc_rate"]        = (daily["atc"] / daily["users"] * 100).round(3)
    daily["bounce_rate"]     = (daily["bounces"] / daily["users"] * 100).round(3)
    daily["rpv"]             = (daily["revenue"] / daily["users"]).round(4)
    return daily.sort_values(["day_number", "group"])


def main():
    out = "/home/claude/ab-testing/data/processed"
    os.makedirs(out, exist_ok=True)

    print("Generating experiment data...")
    df = build_experiment_data()
    df.to_csv(f"{out}/experiment_data.csv", index=False)
    print(f"  experiment_data.csv  — {len(df):,} rows")

    daily = build_daily_summary(df)
    daily.to_csv(f"{out}/daily_summary.csv", index=False)
    print(f"  daily_summary.csv    — {len(daily):,} rows")

    # Top-level summary
    summary = df.groupby("group").agg(
        users       = ("user_id", "count"),
        conversions = ("converted", "sum"),
        atc         = ("add_to_cart", "sum"),
        total_rev   = ("revenue_gbp", "sum"),
        bounces     = ("bounced", "sum"),
        avg_session = ("session_duration_sec", "mean"),
    ).reset_index()
    summary["conversion_rate_pct"] = (summary["conversions"] / summary["users"] * 100).round(4)
    summary["atc_rate_pct"]        = (summary["atc"] / summary["users"] * 100).round(4)
    summary["bounce_rate_pct"]     = (summary["bounces"] / summary["users"] * 100).round(4)
    summary["rpv"]                 = (summary["total_rev"] / summary["users"]).round(4)
    summary["avg_order_value"]     = (summary["total_rev"] / summary["conversions"]).round(2)
    summary.to_csv(f"{out}/group_summary.csv", index=False)

    print("\n── Experiment Summary ─────────────────────────────────")
    print(summary[["group","users","conversions","conversion_rate_pct","rpv","avg_order_value"]].to_string(index=False))

    # JSON for dashboard
    with open(f"{out}/daily_summary.json", "w") as f:
        json.dump(daily.to_dict(orient="records"), f, separators=(",",":"))
    with open(f"{out}/group_summary.json", "w") as f:
        json.dump(summary.to_dict(orient="records"), f, separators=(",",":"))

    print("\nData generation complete.")


if __name__ == "__main__":
    main()
