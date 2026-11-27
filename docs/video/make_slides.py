"""Render 1920x1080 slides for the Milestone 2 demo video from the project's real outputs."""
import sys, json
sys.path.insert(0, "/home/claude/real/src")
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import Polygon, FancyBboxPatch
from config import PROC, OUT, FIG, ROOT
from geo import load_districts, POLLING_DIVISIONS

S = "/home/claude/video/slides/"
NAVY, INK, MUTED, ACCENT, LIGHT = "#14213d", "#1f2937", "#6b7280", "#2563eb", "#eef2ff"
plt.rcParams.update({"font.family": "DejaVu Sans"})
SCENES = []          # (filename, seconds)
TOTAL = 15


def base(title, n, kicker=""):
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100)
    fig.patch.set_facecolor("white")
    fig.add_artist(plt.Rectangle((0, 0.885), 1, 0.115, transform=fig.transFigure, fc=NAVY, zorder=-5))
    if kicker:
        fig.text(0.035, 0.955, kicker.upper(), color="#93c5fd", fontsize=15, weight="bold", va="center")
    fig.text(0.035, 0.915 if kicker else 0.94, title, color="white", fontsize=33, weight="bold", va="center")
    fig.text(0.965, 0.94, f"{n}/{TOTAL}", color="#c7d2fe", fontsize=16, ha="right", va="center")
    fig.add_artist(plt.Rectangle((0, 0), 1, 0.008, transform=fig.transFigure, fc="#e5e7eb", zorder=-5))
    fig.add_artist(plt.Rectangle((0, 0), n / TOTAL, 0.008, transform=fig.transFigure, fc=ACCENT, zorder=-4))
    fig.text(0.035, 0.03, "Dengue Surveillance, Risk Analysis & Forecasting Dashboard – Sri Lanka · Milestone 2",
             color=MUTED, fontsize=13)
    fig.text(0.965, 0.03, "R. M. Y. R. Rathnayaka (268485K)", color=MUTED, fontsize=13, ha="right")
    return fig


def bullets(fig, items, x=0.04, y=0.80, w=None, size=23, gap=0.085):
    for it in items:
        sub = it.startswith("  ")
        fig.text(x + (0.025 if sub else 0), y, ("–  " if sub else "•  ") + it.strip(),
                 fontsize=size - (3 if sub else 0), color=MUTED if sub else INK, va="top", wrap=True)
        y -= gap * (0.8 if sub else 1)
    return y


def img(fig, path, rect):
    ax = fig.add_axes(rect); ax.imshow(mpimg.imread(path)); ax.axis("off"); return ax


def save(fig, name, secs):
    fig.savefig(S + name, dpi=100); plt.close(fig); SCENES.append((name, secs))


d = pd.read_csv(PROC / "monthly_district.csv", parse_dates=["month"])
q = json.loads((OUT / "data_quality_report.json").read_text())
cl = pd.read_csv(OUT / "district_clusters.csv").set_index("district")
F = FIG

# 1 title
fig = plt.figure(figsize=(19.2, 10.8), dpi=100); fig.patch.set_facecolor(NAVY)
fig.text(0.07, 0.68, "MILESTONE 2 · TECHNICAL CHECKPOINT · WEEK 8", color="#93c5fd", fontsize=22, weight="bold")
fig.text(0.07, 0.55, "Dengue Surveillance, Geospatial Risk\nAnalysis & Predictive Dashboard", color="white",
         fontsize=52, weight="bold", va="center", linespacing=1.15)
fig.text(0.07, 0.40, "Sri Lanka · 25 districts · Dec 2021 – Nov 2025", color="#e0e7ff", fontsize=28)
fig.text(0.07, 0.20, "R. M. Y. R. Rathnayaka (268485K)", color="white", fontsize=26)
fig.text(0.07, 0.15, "github.com/RathnayakaRMYR268485K/capstoneproject", color="#93c5fd", fontsize=22)
save(fig, "01.png", 9)

# 2 problem
fig = base("Problem and aim", 2, "Introduction")
bullets(fig, ["Dengue is one of Sri Lanka's biggest public-health burdens:",
              "  205,509 reported cases in the last 48 months alone",
              "Health officers need to see WHERE risk is high and WHEN it will rise",
              "Aim: one dashboard that brings together",
              "  clean surveillance data and exploratory analysis",
              "  district risk clusters (K-means)",
              "  1, 3, 6 and 12-month case forecasts with uncertainty",
              "This milestone: data, EDA, baseline vs improved model, architecture, dashboard"],
        y=0.82, gap=0.092, size=25)
save(fig, "02.png", 16)

# 3 architecture
fig = base("System architecture", 3, "Design")
img(fig, ROOT / "docs/architecture.png", [0.02, 0.36, 0.96, 0.48])
bullets(fig, ["Sources → ETL & storage → analytics → dashboard",
              "Built now: R export, Python pipeline, CSV store, Streamlit dashboard",
              "Planned (grey): PostgreSQL/PostGIS, FastAPI REST API, rainfall & temperature"],
        y=0.31, gap=0.075, size=22)
save(fig, "03.png", 20)

# 4 data
fig = base("Data collection and scope", 4, "Data")
bullets(fig, ["Source: Epidemiology Unit, Ministry of Health – Weekly Epidemiological Reports",
              "  via the open denguedatahub R package (no Java needed in our export script)",
              f"Raw file: {q['raw_rows']:,} weekly rows, 2006 – week 52 of 2025, 26 health districts",
              f"Analysis window: latest 48 complete months ({pd.Timestamp(q['window_start']):%b %Y} – {pd.Timestamp(q['window_end']):%b %Y})",
              "Population: 2012 Census, used for incidence per 100,000",
              "Scope change: the 160 electoral (polling) division map could not be built",
              "  dengue data is collected and published only by district",
              "  the dashboard still marks all 160 divisions as points, ready for that data"],
        y=0.82, gap=0.088, size=24)
save(fig, "04.png", 22)

# 5 preprocessing
fig = base("Data preprocessing", 5, "Data")
bullets(fig, ["Standardise district names", "  e.g. Hambanthota → Hambantota",
              "Merge Kalmunai into Ampara", "Validate dates and case counts",
              "Complete the weekly grid", "Weekly → monthly (mid-week date)",
              "Keep latest 48 complete months", "Compute incidence per 100,000"],
        x=0.04, y=0.80, gap=0.085, size=24)
rows = [("Raw rows", f"{q['raw_rows']:,}"), ("Unrecognised names", q["unmapped_district_rows"]),
        ("Invalid dates", q["bad_date_rows"]), ("Missing / negative cases", f"{q['missing_cases']} / {q['negative_cases']}"),
        ("True duplicates", q["true_duplicate_rows"]), ("Kalmunai rows merged", q["kalmunai_rows_merged_into_ampara"]),
        ("Imputed months in window", q["imputed_district_months"]), ("Final table", "25 × 48 = 1,200 rows")]
fig.add_artist(FancyBboxPatch((0.56, 0.12), 0.40, 0.71, boxstyle="round,pad=0,rounding_size=0.01",
                              transform=fig.transFigure, fc=LIGHT, ec="none", zorder=-5))
fig.text(0.58, 0.79, "Data-quality report", fontsize=24, weight="bold", color=INK)
for i, (k, v) in enumerate(rows):
    y = 0.71 - i * 0.073
    fig.text(0.58, y, k, fontsize=21, color=INK); fig.text(0.94, y, str(v), fontsize=21, weight="bold", ha="right", color=INK)
save(fig, "05.png", 22)

# 6-9 EDA
eda = [("06.png", "01_national_trend.png", "EDA: national trend",
        "Monthly cases ranged from 1,754 (Sep 2022) to 12,955 (Jan 2024). 2023 was the outbreak year (73,678 cases)."),
       ("07.png", "02_seasonality.png", "EDA: seasonality",
        "Peaks follow the monsoons (Jun–Jul and Dec–Jan), but the size of the peak changes a lot from year to year."),
       ("08.png", "03_district_heatmap.png", "EDA: districts over time",
        "Colombo, Gampaha and Kandy carry the most cases every month. Western Province = 36.3% of all cases."),
       ("09.png", "04_top_districts.png", "EDA: where risk is highest",
        "By population, Jaffna is highest (2,492 cases per 100,000), driven by a 3,252-case outbreak in Jan 2024.")]
for i, (name, f, title, cap) in enumerate(eda):
    fig = base(title, 6 + i, "Exploratory data analysis")
    im = mpimg.imread(F / f); h, w = im.shape[:2]
    aw = 0.92; ah = min(0.66, aw * h / w * 19.2 / 10.8)
    aw = ah * w / h * 10.8 / 19.2
    img(fig, F / f, [(1 - aw) / 2, 0.19 + (0.66 - ah) / 2, aw, ah])
    fig.text(0.5, 0.115, cap, fontsize=23, ha="center", color=INK, wrap=True)
    save(fig, name, 14)

# 10 clustering (polygon map)
fig = base("District risk clusters (K-means)", 10, "Analytics")
img(fig, F / "06_kmeans_validation.png", [0.02, 0.50, 0.50, 0.34])
bullets(fig, ["5 features per district: incidence, volatility,", "  peak-to-mean, seasonality, trend",
              "k = 2 – 8 tested; best silhouette at k = 6 (0.428)", "Tier 6 (highest): Jaffna",
              "Tier 5: Colombo, Gampaha, Ratnapura, Monaragala", "  high incidence and rising trend"],
        x=0.04, y=0.46, gap=0.062, size=21)
ax = fig.add_axes([0.55, 0.06, 0.42, 0.80])
cols = ["#2b83ba", "#80bfab", "#c7e9ad", "#fdc980", "#f07c4a", "#d7191c"]
for name, rings in load_districts().items():
    for r in rings:
        ax.add_patch(Polygon(r, fc=cols[int(cl.loc[name, "cluster"])], ec="white", lw=0.8))
for c in range(6):
    ax.scatter([], [], s=200, c=cols[c], marker="s", label=f"Tier {c+1}" + (" (lowest)" if c == 0 else " (highest)" if c == 5 else ""))
ax.legend(loc="lower right", fontsize=14, frameon=False)
ax.set_xlim(79.45, 82.05); ax.set_ylim(5.85, 9.9); ax.set_aspect("equal"); ax.axis("off")
save(fig, "10.png", 22)

# 11 methods
fig = base("Baseline vs improved method", 11, "Forecasting")
fig.add_artist(FancyBboxPatch((0.04, 0.17), 0.43, 0.66, boxstyle="round,pad=0,rounding_size=0.01",
                              transform=fig.transFigure, fc="#f3f4f6", ec="none", zorder=-5))
fig.add_artist(FancyBboxPatch((0.53, 0.17), 0.43, 0.66, boxstyle="round,pad=0,rounding_size=0.01",
                              transform=fig.transFigure, fc=LIGHT, ec="none", zorder=-5))
fig.text(0.06, 0.77, "Baseline: seasonal naive", fontsize=27, weight="bold", color=INK)
bullets(fig, ["Forecast = same month last year", "Standard benchmark for", "  seasonal disease data", "No learning, no recent trend"],
        x=0.06, y=0.68, gap=0.085, size=23)
fig.text(0.55, 0.77, "Improved: Random Forest", fontsize=27, weight="bold", color=ACCENT)
bullets(fig, ["One model per horizon: 1, 3, 6, 12 months", "Pooled over 25 districts, log(1 + cases)",
              "Lags, 3/6/12-month means, seasonal lag,", "  month (sin/cos), district level",
              "Rolling-origin back-test (no leakage)", "MAE, RMSE, MAPE + 80% intervals"],
        x=0.55, y=0.68, gap=0.075, size=22)
save(fig, "11.png", 18)

# 12 results
fig = base("Results: Random Forest beats the baseline", 12, "Forecasting")
img(fig, F / "07_backtest_national.png", [0.03, 0.42, 0.94, 0.40])
tbl = [("Horizon", "Baseline MAE", "Random Forest MAE", "Change"), ("1 month", "2,808", "1,590", "−43%"),
       ("3 months", "2,361", "1,849", "−22%"), ("6 months", "2,493", "1,790", "−28%"), ("12 months", "2,305", "2,443", "+6%")]
for i, row in enumerate(tbl):
    y = 0.36 - i * 0.055
    for j, (x, v) in enumerate(zip([0.12, 0.33, 0.55, 0.78], row)):
        good = i > 0 and j == 3
        fig.text(x, y, v, fontsize=21, weight="bold" if i == 0 or good else None,
                 color=("#15803d" if v.startswith("−") else "#b91c1c") if good else INK)
fig.text(0.5, 0.065, "National MAE (cases/month). 12-month horizon: too few training examples yet – fix planned (train on 2006–2025).",
         fontsize=17, ha="center", color=MUTED)
save(fig, "12.png", 26)

# 13 dashboard mockup (full) and 14 zoom on map
fig = base("Dashboard: interactive Sri Lanka risk map", 13, "Dashboard")
img(fig, F / "08_dashboard_mockup.png", [0.06, 0.06, 0.88, 0.80])
save(fig, "13.png", 18)
fig = base("Select a district · 160 polling divisions marked", 14, "Dashboard")
im = mpimg.imread(F / "08_dashboard_mockup.png")
ax = fig.add_axes([0.02, 0.06, 0.50, 0.80]); ax.imshow(im[180:1420, 640:1430]); ax.axis("off")
bullets(fig, ["Districts coloured by incidence /100k", "Click a district (Colombo shown):",
              "  cases, incidence, risk tier, trend, forecast", "Black points = 160 polling divisions",
              "  correct count per district (Colombo 15)", "  no case data published at this level yet",
              "Filters: month, colour measure, map layers"],
        x=0.54, y=0.80, gap=0.085, size=23)
save(fig, "14.png", 20)

# 15 code + next steps
fig = base("Code, how to run, and next steps", 15, "Wrap-up")
fig.text(0.04, 0.79, "GitHub: github.com/RathnayakaRMYR268485K/capstoneproject", fontsize=24, weight="bold", color=ACCENT)
bullets(fig, ["R:  source(\"scripts/01_export_dengue_csv.R\")", "Windows:  run_all.bat  (≈30 s)", "Dashboard:  streamlit run app.py"],
        x=0.04, y=0.70, gap=0.075, size=22)
fig.text(0.04, 0.44, "Next (Milestone 3)", fontsize=25, weight="bold", color=INK)
bullets(fig, ["Train on 2006–2025 history to fix the 12-month horizon",
              "Add rainfall and temperature predictors; test SARIMA, Prophet, LSTM",
              "Polling-division data via MOH areas; PostGIS + FastAPI"],
        x=0.04, y=0.37, gap=0.075, size=22)
save(fig, "15.png", 18)

# end card
fig = plt.figure(figsize=(19.2, 10.8), dpi=100); fig.patch.set_facecolor(NAVY)
fig.text(0.5, 0.56, "Thank you", color="white", fontsize=60, weight="bold", ha="center")
fig.text(0.5, 0.44, "github.com/RathnayakaRMYR268485K/capstoneproject", color="#93c5fd", fontsize=26, ha="center")
save(fig, "16.png", 6)

pd.DataFrame(SCENES, columns=["file", "secs"]).to_csv(S + "scenes.csv", index=False)
print("slides:", len(SCENES), "total seconds:", sum(s for _, s in SCENES))
