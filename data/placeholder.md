# data/

This folder contains all data used in the experiment analysis.

## Structure
```
├── data/
│   └── processed/
│       ├── experiment_data.csv      # 48,312 rows — one row per user
│       ├── daily_summary.csv        # Daily aggregates by group (28 rows)
│       ├── group_summary.csv        # Top-level group summary
│       ├── analysis_results.json    # Full results JSON (used by dashboard)
│       ├── daily_summary.json       # Daily data for dashboard
│       └── group_summary.json       # Group summary for dashboard
```

## How to generate all files

```bash
# Step 1 — generates all CSV and JSON files
python scripts/01_generate_data.py

# Step 2 — generates analysis_results.json
python scripts/02_statistical_analysis.py
```

## Data source

All data is synthetically generated using real-world UK e-commerce benchmarks:

| Benchmark | Value | Source |
|---|---|---|
| Baseline conversion rate | 3.2% | Statista UK E-Commerce Report 2023 |
| Average order value | £45.50 | ONS Retail Sales Index 2023 |
| Mobile traffic share | 63% | Ofcom Connected Nations 2023 |
| New user share | 41% | Industry average for established retailers |

To replace with real data, swap `experiment_data.csv` with your own export and ensure these columns are present: `user_id`, `group`, `visit_date`, `converted`, `revenue_gbp`, `device`.
