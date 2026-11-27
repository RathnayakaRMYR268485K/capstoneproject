# Milestone 2 - Technical Checkpoint Report
**Project:** Dengue Surveillance, Geospatial Risk Analysis and Predictive Dashboard for Sri Lanka
**Student:** R. M. Y. R. Rathnayaka (268485K)   **Code/system link:** <add repo URL>   **Demo video:** <add link>

## 1. Progress summary
Data collected and preprocessed; EDA complete; baseline and improved forecasting implemented with rolling-origin
back-testing; K-means clustering; system architecture defined; dashboard prototype built.

## 2. Data collection
* **Source:** Epidemiology Unit, Ministry of Health - Weekly Epidemiological Reports, compiled in the open `denguedatahub` R package (district-level weekly suspected dengue cases).
* **Window:** latest 48 complete months in the file (<fill: start - end>), 25 districts, <fill> rows raw.
* **Scope change to document:** the project definition specifies 160 electoral divisions. Published surveillance counts are by district / MOH area, and MOH areas do not align with electoral divisions, so Milestone 2 works at **district level (25)**. Proposed path to finer resolution: MOH-area data from the WERs plus a MOH-to-electoral-division crosswalk, or area-weighted allocation (state the assumption). Agree this change with your supervisor.
* **Population:** 2012 Census (DCS). Age-group breakdown, rainfall and temperature: <not yet integrated / status>.

## 3. Preprocessing (src/preprocess.py)
Table from `outputs/data_quality_report.json`: raw rows, unmapped names, bad dates, missing/negative values, duplicates, imputed district-months. Steps: name standardisation, Kalmunai->Ampara, de-duplication, complete weekly grid, mid-week month assignment, complete-month filter, 48-month window, flagged interpolation, incidence per 100k.

## 4. Exploratory data analysis
Insert figures 01-06 and `eda_district_summary.csv`. Discuss: trend and yearly totals, W-shaped seasonality (monsoon-linked), Western Province share, high-incidence districts, lag-12 autocorrelation, zero-inflation in low-burden districts. <Write findings from YOUR real outputs.>

## 5. Methods
* **Baseline:** seasonal naive (same month last year).
* **Improved:** pooled direct multi-horizon Random Forest on log1p cases; features: lags 0/1/2/5/11, rolling means 3/6/12, seasonal lag aligned to target month, district level, month sin/cos; one model per horizon (1, 3, 6, 12). Optional national SARIMA(1,0,1)(0,1,0)12.
* **Evaluation:** expanding-window rolling-origin back-test from month 24; MAE, RMSE, MAPE (zeros excluded from MAPE); 80% intervals from empirical back-test residuals (log scale) with coverage check.
* **Clustering:** K-means on standardised, log-scaled profile features; k by silhouette, elbow as cross-check.

## 6. Results
Insert `model_comparison_MAE.csv`, `model_metrics.csv`, `interval_coverage.csv`, figure 07, cluster table. Report honestly where the improved model does/does not beat the baseline and how accuracy degrades with horizon.

## 7. System architecture
Insert `docs/architecture.png`. Built: CSV store, pipeline, Streamlit dashboard. Planned: PostgreSQL/PostGIS, FastAPI, Prophet/LSTM, rainfall predictors.

## 8. Risks, limitations, next steps
Under-reporting and suspected-vs-confirmed definition; district-level resolution; 48-month depth limits seasonal learning (seek 2006+ data for training and keep 48 months for the surveillance view); fixed 2012 population; interval coverage on short back-test; steps to Milestone 3.
