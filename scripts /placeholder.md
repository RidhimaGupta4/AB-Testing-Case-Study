# scripts/

This folder contains all Python scripts for the full A/B testing pipeline.

| File | Purpose |
|---|---|
| `01_generate_data.py` | Generates 48,312-row experiment dataset with realistic UK e-commerce benchmarks — fixed random seed, fully reproducible |
| `02_statistical_analysis.py` | Full statistical pipeline — SRM check, power analysis, z-test, chi-square, Bonferroni correction, Mann-Whitney U, novelty effect, business impact |
| `03_charts.py` | Generates all 7 publication-quality PNG charts for the portfolio and README |

## How to run in order

```bash
python scripts/01_generate_data.py        # Step 1 — generate experiment data
python scripts/02_statistical_analysis.py # Step 2 — run full statistical analysis
python scripts/03_charts.py               # Step 3 — generate all charts
```

## Notes

- Run scripts **in order** — each step depends on outputs from the previous one
- All outputs land in `data/processed/` (CSVs + JSON) and `outputs/` (PNGs)
- Random seed is fixed at `np.random.seed(2024)` — every run produces identical results
- `02_statistical_analysis.py` also writes `analysis_results.json` which powers the live dashboard
- To swap in real data, replace `data/processed/experiment_data.csv` with your own export — see README for required column schema
