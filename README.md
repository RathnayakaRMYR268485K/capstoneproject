# Dengue Surveillance, Geospatial Risk Analysis & Predictive Dashboard - Sri Lanka
Capstone (268485K, R. M. Y. R. Rathnayaka) - **Milestone 2: Technical Checkpoint**

Milestone 2 report: see `docs/` and the results in `outputs/` (real data, Dec 2021 - Nov 2025).

## Quick start
```bash
pip install -r requirements.txt
# 1. Collect data (needs internet + R) - exports ~20 years of weekly district-level cases
Rscript scripts/01_export_dengue_csv.R          # -> data/raw/srilanka_weekly_dengue.csv (no Java needed)
# 2. Run pipeline: preprocess -> EDA -> K-means -> baseline vs improved forecasting
sh run_all.sh          # Windows: run_all.bat
# 3. Dashboard
streamlit run app.py
```
The pipeline automatically keeps the **latest 48 complete months** available in the raw file.

## Layout
| Path | Purpose |
|---|---|
| `scripts/01_export_dengue_csv.R` | Data collection (Epidemiology Unit WER data via `denguedatahub`) |
| `src/preprocess.py` | Cleaning, name standardisation, de-dup, weekly->monthly, quality report |
| `src/eda.py` | EDA figures + summary tables |
| `src/clustering.py` | K-means (elbow + silhouette) |
| `src/forecast.py` | Seasonal-naive baseline, Random Forest (improved), optional SARIMA, rolling-origin back-test, 80% intervals |
| `app.py` | Streamlit dashboard (risk map, trends, clusters, forecasts) |
| `docs/architecture.{png,svg,dot}` | System architecture diagram |
| `docs/Milestone2_Report.md`, `docs/demo_video_script.md` | Report skeleton and 6-minute demo script |

## Known limitations (state these in your report)
* Public data is **district level (25 districts)**, not 160 electoral divisions. See report section 2.
* Population = 2012 Census, entered from memory: verify against DCS before citing.
* Weekly->monthly uses the mid-week date; districts' incidence uses fixed 2012 population.
* With 48 months, the 12-month model trains on few origins in early back-test folds.
* Outputs in `outputs/` are from the REAL data (Dec 2021 - Nov 2025). The dashboard (`app.py`) was not launched in the build sandbox (no Streamlit there).
