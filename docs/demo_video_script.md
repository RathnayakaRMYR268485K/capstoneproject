# Demo video script (target 5:30, hard limit 6:00)
| Time | Show | Say |
|---|---|---|
| 0:00-0:30 | Title slide | Project, problem (no single tool for where/when dengue will rise), aim, what Milestone 2 covers |
| 0:30-1:15 | `docs/architecture.png` | Walk left to right: sources -> ETL -> store -> analytics -> dashboard. Mention what's built vs planned (PostGIS, FastAPI) |
| 1:15-2:15 | Terminal: `Rscript ...`, `python src/preprocess.py`; open `data_quality_report.json` | 48-month window, districts, missing/duplicate handling, imputation flags, Kalmunai->Ampara merge |
| 2:15-3:15 | Figures 01-05 | National W-shaped seasonality, Western Province share, top districts, heatmap, autocorrelation at lag 12 |
| 3:15-3:45 | Figure 06 + clusters table | Elbow/silhouette -> chosen k; interpret clusters |
| 3:45-4:45 | `model_comparison_MAE.csv`, figure 07 | Baseline = seasonal naive; improved = Random Forest (lags, rolling means, seasonality). Rolling-origin back-test; report MAE/RMSE/MAPE honestly, incl. horizons where it does not beat the baseline |
| 4:45-5:30 | Live dashboard: map -> trends -> forecast tab | 1/3/6/12-month forecasts with 80% intervals |
| 5:30-6:00 | Slide | Next steps: electoral-division mapping, rainfall predictors, Prophet/LSTM, PostGIS + API, usability testing |
