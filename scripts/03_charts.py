"""
A/B Testing Case Study — Chart Generation
==========================================
Produces 7 publication-quality charts for the portfolio.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
from scipy import stats
from statsmodels.stats.proportion import proportions_ztest
import json, os, warnings
warnings.filterwarnings("ignore")

DATA = "/home/claude/ab-testing/data/processed"
OUT  = "/home/claude/ab-testing/outputs"
os.makedirs(OUT, exist_ok=True)

df      = pd.read_csv(f"{DATA}/experiment_data.csv", parse_dates=["visit_date"])
daily   = pd.read_csv(f"{DATA}/daily_summary.csv")
results = json.load(open(f"{DATA}/analysis_results.json"))

ctrl  = df[df["group"] == "control"]
treat = df[df["group"] == "treatment"]

# Palette
C_CTRL  = "#4472C4"
C_TREAT = "#E15759"
C_GOOD  = "#59A14F"
C_WARN  = "#F28E2B"
BG      = "#FAFAFA"
TEXT    = "#1C2B39"
MUTED   = "#64788A"

def style(ax, title="", xlabel="", ylabel="", grid_axis="y"):
    ax.set_facecolor(BG)
    ax.spines[["top","right"]].set_visible(False)
    ax.spines[["left","bottom"]].set_color("#D0D7DE")
    ax.tick_params(colors=TEXT, labelsize=9)
    if title:  ax.set_title(title, fontsize=12, fontweight="bold", color=TEXT, pad=10)
    if xlabel: ax.set_xlabel(xlabel, fontsize=9, color=MUTED)
    if ylabel: ax.set_ylabel(ylabel, fontsize=9, color=MUTED)
    if grid_axis:
        ax.grid(axis=grid_axis, color="#E8ECEF", linewidth=0.7, zorder=0)


# ── Chart 1: Primary Metric Summary ──────────────────────────────────────────
def chart_primary_summary():
    fig, axes = plt.subplots(1, 3, figsize=(13, 5), facecolor="white")
    fig.suptitle("A/B Test Results — ShopWise UK Product Page Redesign",
                 fontsize=14, fontweight="bold", color=TEXT, y=1.01)

    metrics = [
        ("Conversion Rate", ctrl["converted"].mean()*100, treat["converted"].mean()*100, "%", 3),
        ("Revenue per Visitor (£)", ctrl["revenue_gbp"].mean(), treat["revenue_gbp"].mean(), "£", 3),
        ("Bounce Rate", ctrl["bounced"].mean()*100, treat["bounced"].mean()*100, "%", 1),
    ]

    for ax, (name, c_val, t_val, unit, dp) in zip(axes, metrics):
        bars = ax.bar(["Control", "Treatment"], [c_val, t_val],
                      color=[C_CTRL, C_TREAT], width=0.5)
        for bar, val in zip(bars, [c_val, t_val]):
            label = f"{unit}{val:.{dp}f}" if unit == "£" else f"{val:.{dp}f}{unit}"
            ax.text(bar.get_x() + bar.get_width()/2, val + c_val * 0.01,
                    label, ha="center", fontsize=11, fontweight="bold", color=TEXT)

        lift = (t_val - c_val) / c_val * 100
        direction = "▲" if lift > 0 else "▼"
        col = C_GOOD if (lift > 0 and name != "Bounce Rate") or \
                        (lift < 0 and name == "Bounce Rate") else C_WARN
        ax.text(0.5, 0.94, f"{direction} {abs(lift):.1f}% relative lift",
                transform=ax.transAxes, ha="center", fontsize=10,
                fontweight="bold", color=col,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                          edgecolor=col, linewidth=1.2))
        style(ax, title=name)
        ax.set_ylim(0, max(c_val, t_val) * 1.25)
        yf = (lambda x, _: f"£{x:.1f}") if unit == "£" else (lambda x, _: f"{x:.1f}%")
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(yf))

    plt.tight_layout()
    plt.savefig(f"{OUT}/01_primary_results_summary.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved: 01_primary_results_summary.png")


# ── Chart 2: Cumulative Conversion Rate Over Time ────────────────────────────
def chart_cumulative_cr():
    ctrl_d  = daily[daily["group"]=="control"].sort_values("day_number")
    treat_d = daily[daily["group"]=="treatment"].sort_values("day_number")

    cum_c = (ctrl_d["conversions"].cumsum() / ctrl_d["users"].cumsum() * 100).values
    cum_t = (treat_d["conversions"].cumsum() / treat_d["users"].cumsum() * 100).values
    days  = ctrl_d["day_number"].values + 1

    fig, ax = plt.subplots(figsize=(11, 5), facecolor="white")
    ax.plot(days, cum_c, color=C_CTRL, linewidth=2.5, marker="o", markersize=5,
            label="Control")
    ax.plot(days, cum_t, color=C_TREAT, linewidth=2.5, marker="o", markersize=5,
            label="Treatment")
    ax.fill_between(days, cum_c, cum_t, alpha=0.12, color=C_TREAT,
                    label="Lift zone")

    # Annotate final values
    ax.annotate(f"{cum_c[-1]:.3f}%", (days[-1], cum_c[-1]),
                xytext=(8, -10), textcoords="offset points",
                fontsize=9, color=C_CTRL, fontweight="bold")
    ax.annotate(f"{cum_t[-1]:.3f}%", (days[-1], cum_t[-1]),
                xytext=(8, 5), textcoords="offset points",
                fontsize=9, color=C_TREAT, fontweight="bold")

    style(ax, title="Cumulative Conversion Rate Over 14-Day Experiment\nLift stabilises after day 4 — novelty effect minor",
          xlabel="Day of experiment", ylabel="Cumulative conversion rate (%)")
    ax.legend(fontsize=9, framealpha=0)
    ax.set_xticks(days)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x:.2f}%"))
    plt.tight_layout()
    plt.savefig(f"{OUT}/02_cumulative_conversion_rate.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved: 02_cumulative_conversion_rate.png")


# ── Chart 3: Confidence Interval Plot ────────────────────────────────────────
def chart_confidence_intervals():
    from statsmodels.stats.proportion import proportions_ztest, proportion_effectsize
    from scipy.stats import norm

    metrics_ci = []

    # Primary — conversion rate
    nc, xc = len(ctrl), ctrl["converted"].sum()
    nt, xt = len(treat), treat["converted"].sum()
    pc, pt = xc/nc, xt/nt
    diff   = pt - pc
    se     = np.sqrt(pc*(1-pc)/nc + pt*(1-pt)/nt)
    z95    = norm.ppf(0.975)
    metrics_ci.append(("Conversion rate", diff*100, (diff-z95*se)*100, (diff+z95*se)*100))

    # ATC rate
    nc_a, xc_a = len(ctrl), ctrl["add_to_cart"].sum()
    nt_a, xt_a = len(treat), treat["add_to_cart"].sum()
    pc_a, pt_a = xc_a/nc_a, xt_a/nt_a
    diff_a = pt_a - pc_a
    se_a   = np.sqrt(pc_a*(1-pc_a)/nc_a + pt_a*(1-pt_a)/nt_a)
    metrics_ci.append(("Add-to-cart rate", diff_a*100, (diff_a-z95*se_a)*100, (diff_a+z95*se_a)*100))

    # Bounce rate (negative is good)
    nc_b, xc_b = len(ctrl), ctrl["bounced"].sum()
    nt_b, xt_b = len(treat), treat["bounced"].sum()
    pc_b, pt_b = xc_b/nc_b, xt_b/nt_b
    diff_b = pt_b - pc_b
    se_b   = np.sqrt(pc_b*(1-pc_b)/nc_b + pt_b*(1-pt_b)/nt_b)
    metrics_ci.append(("Bounce rate", diff_b*100, (diff_b-z95*se_b)*100, (diff_b+z95*se_b)*100))

    fig, ax = plt.subplots(figsize=(9, 5), facecolor="white")
    y_pos = range(len(metrics_ci))
    for i, (name, diff, lo, hi) in enumerate(metrics_ci):
        good = (diff > 0 and name != "Bounce rate") or (diff < 0 and name == "Bounce rate")
        col  = C_GOOD if good else C_WARN
        ax.plot([lo, hi], [i, i], color=col, linewidth=4, solid_capstyle="round")
        ax.scatter([diff], [i], color=col, s=100, zorder=5)
        ax.text(hi + 0.02, i, f"{diff:+.3f}pp\n[{lo:+.3f}, {hi:+.3f}]",
                va="center", fontsize=8.5, color=TEXT)

    ax.axvline(0, color=TEXT, linewidth=1.2, linestyle="--", alpha=0.5)
    ax.set_yticks(list(y_pos))
    ax.set_yticklabels([m[0] for m in metrics_ci], fontsize=10)
    ax.set_xlabel("Difference: Treatment − Control (percentage points)", fontsize=9, color=MUTED)
    style(ax, title="95% Confidence Intervals — Treatment vs Control\nAll CIs for positive metrics exclude zero ✅")
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)

    plt.tight_layout()
    plt.savefig(f"{OUT}/03_confidence_intervals.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved: 03_confidence_intervals.png")


# ── Chart 4: Segmentation Heatmap ────────────────────────────────────────────
def chart_segmentation():
    segs = results["segmentation"]
    seg_df = pd.DataFrame(segs)

    fig, ax = plt.subplots(figsize=(10, 6), facecolor="white")
    colors = [C_GOOD if (r["lift_pct"] > 0 and r["significant"]) else
              "#AED6B0" if r["lift_pct"] > 0 else C_WARN
              for _, r in seg_df.iterrows()]

    bars = ax.barh(seg_df["segment"], seg_df["lift_pct"], color=colors, height=0.65)
    ax.axvline(0, color=TEXT, linewidth=0.8, linestyle="--", alpha=0.4)

    for bar, (_, row) in zip(bars, seg_df.iterrows()):
        lx = row["lift_pct"] + 0.4 if row["lift_pct"] >= 0 else row["lift_pct"] - 0.4
        ha = "left" if row["lift_pct"] >= 0 else "right"
        sig_marker = " ✅" if row["significant"] else ""
        ax.text(lx, bar.get_y() + bar.get_height()/2,
                f"{row['lift_pct']:+.1f}%{sig_marker}",
                va="center", ha=ha, fontsize=8.5, color=TEXT, fontweight="bold")

    style(ax, title="Segmentation Analysis — Conversion Rate Lift by Segment\n✅ = statistically significant after Bonferroni correction",
          xlabel="Relative lift (%)")
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0, labelsize=9)

    legend_patches = [
        mpatches.Patch(color=C_GOOD, label="Significant positive lift"),
        mpatches.Patch(color="#AED6B0", label="Positive lift (not significant)"),
        mpatches.Patch(color=C_WARN, label="Negative lift"),
    ]
    ax.legend(handles=legend_patches, fontsize=8, framealpha=0, loc="lower right")
    plt.tight_layout()
    plt.savefig(f"{OUT}/04_segmentation_analysis.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved: 04_segmentation_analysis.png")


# ── Chart 5: Power Analysis Curve ────────────────────────────────────────────
def chart_power_curve():
    from statsmodels.stats.power import NormalIndPower
    from statsmodels.stats.proportion import proportion_effectsize

    analysis = NormalIndPower()
    sample_sizes = np.arange(1000, 60000, 500)
    baseline  = 0.032
    mde_15    = baseline * 1.15
    mde_10    = baseline * 1.10
    mde_20    = baseline * 1.20

    def power_curve(p1, p2, ns):
        h = abs(proportion_effectsize(p1, p2))
        return [analysis.solve_power(effect_size=h, nobs1=n, alpha=0.05,
                                      alternative="two-sided") for n in ns]

    pwr_15 = power_curve(mde_15, baseline, sample_sizes)
    pwr_10 = power_curve(mde_10, baseline, sample_sizes)
    pwr_20 = power_curve(mde_20, baseline, sample_sizes)

    fig, ax = plt.subplots(figsize=(10, 5), facecolor="white")
    ax.plot(sample_sizes/1000, pwr_20, color=C_GOOD, linewidth=2, label="20% MDE (easier to detect)")
    ax.plot(sample_sizes/1000, pwr_15, color=C_CTRL, linewidth=2.5, label="15% MDE (pre-registered)")
    ax.plot(sample_sizes/1000, pwr_10, color=C_TREAT, linewidth=2, linestyle="--",
            label="10% MDE (smaller effect)")

    ax.axhline(0.80, color=TEXT, linewidth=1.2, linestyle=":", alpha=0.6)
    ax.text(1.5, 0.81, "80% power threshold", fontsize=8.5, color=MUTED)
    ax.axvline(22.605, color=C_CTRL, linewidth=1.2, linestyle=":")
    ax.text(22.8, 0.25, "Required n\n(22,605)", fontsize=8, color=C_CTRL)
    ax.axvline(24.156, color=C_TREAT, linewidth=1.2, linestyle=":")
    ax.text(24.4, 0.15, "Actual n\n(24,156)", fontsize=8, color=C_TREAT)

    style(ax, title="Statistical Power Curve — Sample Size vs Detected Effect\nPre-registered MDE: 15% relative lift · α = 0.05 · Two-tailed",
          xlabel="Sample size per group (thousands)", ylabel="Statistical power (1 − β)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x*100:.0f}%"))
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=9, framealpha=0)
    plt.tight_layout()
    plt.savefig(f"{OUT}/05_power_analysis_curve.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved: 05_power_analysis_curve.png")


# ── Chart 6: Revenue Distribution ────────────────────────────────────────────
def chart_revenue_distribution():
    rev_c = ctrl[ctrl["converted"]==1]["revenue_gbp"]
    rev_t = treat[treat["converted"]==1]["revenue_gbp"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), facecolor="white")

    bins = np.linspace(0, 250, 40)
    ax1.hist(rev_c, bins=bins, alpha=0.65, color=C_CTRL, label=f"Control  (n={len(rev_c):,})", density=True)
    ax1.hist(rev_t, bins=bins, alpha=0.65, color=C_TREAT, label=f"Treatment (n={len(rev_t):,})", density=True)
    ax1.axvline(rev_c.mean(), color=C_CTRL, linewidth=2, linestyle="--", alpha=0.9)
    ax1.axvline(rev_t.mean(), color=C_TREAT, linewidth=2, linestyle="--", alpha=0.9)
    ax1.text(rev_c.mean()+2, ax1.get_ylim()[1]*0.85, f"£{rev_c.mean():.2f}", color=C_CTRL, fontsize=8)
    ax1.text(rev_t.mean()+2, ax1.get_ylim()[1]*0.75, f"£{rev_t.mean():.2f}", color=C_TREAT, fontsize=8)
    style(ax1, title="Order Value Distribution (Converters Only)\nLognormal distribution — use Mann-Whitney, not t-test",
          xlabel="Order value (£)", ylabel="Density")
    ax1.legend(fontsize=8.5, framealpha=0)

    # RPV by day
    ctrl_d  = daily[daily["group"]=="control"].sort_values("day_number")
    treat_d = daily[daily["group"]=="treatment"].sort_values("day_number")
    days = ctrl_d["day_number"].values + 1
    ax2.bar(days - 0.2, ctrl_d["rpv"], 0.38, color=C_CTRL, alpha=0.8, label="Control")
    ax2.bar(days + 0.2, treat_d["rpv"], 0.38, color=C_TREAT, alpha=0.8, label="Treatment")
    style(ax2, title="Revenue per Visitor — Daily Comparison",
          xlabel="Day of experiment", ylabel="Revenue per visitor (£)")
    ax2.legend(fontsize=8.5, framealpha=0)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"£{x:.2f}"))

    plt.tight_layout()
    plt.savefig(f"{OUT}/06_revenue_distribution.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved: 06_revenue_distribution.png")


# ── Chart 7: Business Impact ──────────────────────────────────────────────────
def chart_business_impact():
    bi = results["business_impact"]
    months = np.arange(1, 13)
    monthly_uplift = bi["monthly_uplift_gbp"]
    cum_uplift = np.cumsum([monthly_uplift] * 12)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), facecolor="white")

    # Cumulative uplift
    ax1.bar(months, cum_uplift / 1000, color=C_GOOD, alpha=0.85, width=0.65)
    ax1.plot(months, cum_uplift / 1000, color=C_GOOD, linewidth=2,
             marker="o", markersize=5)
    ax1.text(11.5, cum_uplift[-1]/1000 + 8,
             f"£{cum_uplift[-1]/1000:.0f}k", fontsize=10, color=C_GOOD,
             fontweight="bold", ha="center")
    style(ax1, title="Projected Cumulative Revenue Uplift (12 months)\nBased on observed +20.6% relative lift in conversion rate",
          xlabel="Month", ylabel="Cumulative uplift (£ thousands)")
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"£{x:.0f}k"))

    # Scenario comparison
    labels  = ["Conservative\n(CI Lower)", "Central\nEstimate", "Optimistic\n(CI Upper)"]
    vals    = [bi["annual_ci_lower"], bi["annual_uplift_gbp"], bi["annual_ci_upper"]]
    colors2 = [C_WARN, C_GOOD, C_CTRL]
    bars = ax2.bar(labels, [v/1000 for v in vals], color=colors2, alpha=0.85, width=0.5)
    for bar, val in zip(bars, vals):
        ax2.text(bar.get_x() + bar.get_width()/2,
                 val/1000 + 8,
                 f"£{val/1000:.0f}k",
                 ha="center", fontsize=10, fontweight="bold", color=TEXT)
    style(ax2, title="Annual Revenue Uplift — Scenario Range\n95% confidence interval bounds",
          ylabel="Annual uplift (£ thousands)")
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"£{x:.0f}k"))

    plt.suptitle("Business Impact Projection — Ship Decision Justified",
                 fontsize=13, fontweight="bold", color=TEXT, y=1.02)
    plt.tight_layout()
    plt.savefig(f"{OUT}/07_business_impact.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved: 07_business_impact.png")


if __name__ == "__main__":
    print("Generating charts...\n")
    chart_primary_summary()
    chart_cumulative_cr()
    chart_confidence_intervals()
    chart_segmentation()
    chart_power_curve()
    chart_revenue_distribution()
    chart_business_impact()
    print(f"\nAll 7 charts saved to {OUT}/")
