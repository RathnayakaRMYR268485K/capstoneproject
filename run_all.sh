#!/bin/sh
# Full pipeline. Prereq: data/raw/srilanka_weekly_dengue.csv (see scripts/01_export_dengue_csv.R)
set -e
cd "$(dirname "$0")/src"
python3 preprocess.py && python3 eda.py && python3 clustering.py && python3 forecast.py && python3 dashboard_mockup.py
echo "Done. Launch dashboard:  cd .. && streamlit run app.py"
