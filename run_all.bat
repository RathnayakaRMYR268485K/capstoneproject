@echo off
REM Full pipeline (Windows). Prereq: data\raw\srilanka_weekly_dengue.csv
cd /d "%~dp0src"
python preprocess.py || exit /b 1
python eda.py || exit /b 1
python clustering.py || exit /b 1
python forecast.py || exit /b 1
echo Done. Launch dashboard:  cd .. ^&^& streamlit run app.py
