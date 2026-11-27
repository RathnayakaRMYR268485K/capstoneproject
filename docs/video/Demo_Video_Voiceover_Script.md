# Milestone 2 demo video – voice-over script

Video: `Milestone2_Demo_Video_Dengue_Dashboard.mp4` (4 min 33 s, 1920×1080, silent).
Read each part while its slide is on screen. At a calm pace each part fits its time slot.

| Time | Slide | What to say |
|---|---|---|
| 0:00–0:09 | Title | Hello, I'm R. M. Y. R. Rathnayaka. This is Milestone 2 of my capstone: a dengue surveillance, risk analysis and forecasting dashboard for Sri Lanka. |
| 0:09–0:25 | Problem and aim | Dengue is a major health burden in Sri Lanka, with over 205,000 reported cases in the last four years. Health officers need to know where risk is high and when cases will rise. My aim is one dashboard that combines clean data, risk clusters and forecasts. |
| 0:25–0:45 | Architecture | The system has four layers: data sources, ETL and storage, analytics, and the dashboard. The R export, Python pipeline, CSV store and Streamlit dashboard are built. The grey parts, PostGIS, a REST API and climate data, are planned. |
| 0:45–1:07 | Data and scope | The data comes from the Epidemiology Unit's weekly reports, through the denguedatahub package: about 25,800 weekly rows from 2006 to 2025. I use the latest 48 complete months. The planned 160 polling-division map could not be built, because dengue data is only published by district, but the dashboard already marks all 160 divisions as points. |
| 1:07–1:29 | Preprocessing | Preprocessing standardises district names, merges Kalmunai into Ampara, validates dates and counts, completes the weekly grid and converts weeks to months. The quality report shows no missing, negative or duplicate values, and no imputed months. |
| 1:29–1:43 | EDA: trend | Monthly cases ranged from about 1,750 to almost 13,000. The biggest outbreak was in December 2023 and January 2024. |
| 1:43–1:57 | EDA: seasonality | Peaks follow the two monsoons, mid-year and December–January, but their size changes a lot from year to year. |
| 1:57–2:11 | EDA: districts | Colombo, Gampaha and Kandy have the most cases every month. Western Province has 36 percent of all cases. |
| 2:11–2:25 | EDA: incidence | Per head of population, Jaffna has the highest risk, driven by a large outbreak in January 2024. |
| 2:25–2:47 | Clustering | I grouped districts with K-means using five features. The silhouette score was best at six clusters. Jaffna is the highest tier, and Colombo, Gampaha, Ratnapura and Monaragala form a high, rising tier. |
| 2:47–3:05 | Methods | The baseline repeats the same month last year. The improved model is a Random Forest, one per horizon, using recent lags, rolling averages and seasonality. Both are tested with a rolling-origin back-test, so no future data leaks in. |
| 3:05–3:31 | Results | The Random Forest cuts national error by 43 percent at one month ahead, and by 22 to 28 percent at three and six months. At 12 months it is not better yet, because there are too few training examples. Training on the full 2006 to 2025 history is the planned fix. |
| 3:31–3:49 | Dashboard | This is the dashboard design: a Sri Lanka map coloured by incidence, filters on the left, and details of the selected district on the right. |
| 3:49–4:09 | Map detail | Users click a district, here Colombo, to see its cases, incidence, risk tier, trend and forecast. The black points are the 160 polling divisions, with the correct number in each district, ready for division-level data. |
| 4:09–4:27 | Code and next steps | All code is on GitHub. The pipeline runs in about 30 seconds with run_all. Next, I will train on longer history, add rainfall and temperature, and move to PostGIS and an API. |
| 4:27–4:33 | Thank you | Thank you for watching. |

## Adding your voice (Windows, free)
1. Open **Clipchamp** (built into Windows 11) → **Create a new video** → import the MP4.
2. Click **Record & create → Audio** (or record on your phone and import it), and read the script above.
3. Drag the audio under the video, line it up, then **Export → 1080p**.
