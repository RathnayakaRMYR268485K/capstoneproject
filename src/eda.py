"""Step 3 - Exploratory data analysis. Reads data/processed/monthly_district.csv, writes figures + summary tables."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from config import *

def run():
    d = pd.read_csv(PROC / "monthly_district.csv", parse_dates=["month"])
    nat = d.groupby("month")["cases"].sum()
    # 1 national trend + 12-month rolling mean
    fig, ax = plt.subplots(figsize=(10, 3.8))
    ax.plot(nat.index, nat.values, marker="o", ms=3, label="Monthly cases")
    ax.plot(nat.index, nat.rolling(12, min_periods=6).mean(), lw=2, label="12-month rolling mean")
    ax.set(title="National monthly dengue cases", ylabel="Cases"); ax.legend(); fig.tight_layout()
    fig.savefig(FIG / "01_national_trend.png", dpi=150); plt.close(fig)
    # 2 seasonality by calendar month (each year as a line)
    s = nat.to_frame("cases"); s["year"] = s.index.year; s["m"] = s.index.month
    piv = s.pivot_table(index="m", columns="year", values="cases")
    fig, ax = plt.subplots(figsize=(8, 3.8)); piv.plot(ax=ax, marker="o", ms=3)
    ax.set(title="Seasonality: cases by calendar month", xlabel="Month", ylabel="Cases"); fig.tight_layout()
    fig.savefig(FIG / "02_seasonality.png", dpi=150); plt.close(fig)
    # 3 district x month heatmap (log scale for readability)
    hm = d.pivot(index="district", columns="month", values="cases")
    hm = hm.loc[hm.sum(axis=1).sort_values(ascending=False).index]
    fig, ax = plt.subplots(figsize=(11, 6))
    im = ax.imshow(np.log1p(hm.values), aspect="auto", cmap="YlOrRd")
    ax.set_yticks(range(len(hm))); ax.set_yticklabels(hm.index, fontsize=7)
    ticks = list(range(0, hm.shape[1], 6)); ax.set_xticks(ticks)
    ax.set_xticklabels([hm.columns[i].strftime("%Y-%m") for i in ticks], rotation=45, fontsize=7)
    fig.colorbar(im, label="log(1+cases)"); ax.set_title("District x month dengue cases"); fig.tight_layout()
    fig.savefig(FIG / "03_district_heatmap.png", dpi=150); plt.close(fig)
    # 4 top districts + provincial share
    tot = d.groupby("district")["cases"].sum().sort_values(ascending=False)
    inc = d.groupby("district")["incidence_per_100k"].sum().sort_values(ascending=False)
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.5))
    tot.head(12)[::-1].plot.barh(ax=axs[0], title="Top 12 districts by total cases")
    inc.head(12)[::-1].plot.barh(ax=axs[1], title="Top 12 by cumulative incidence /100k (2012 pop.)")
    fig.tight_layout(); fig.savefig(FIG / "04_top_districts.png", dpi=150); plt.close(fig)
    # 5 autocorrelation of national series
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ac = [nat.autocorr(l) for l in range(1, 25)]
    ax.bar(range(1, 25), ac); ax.axhline(0, c="k", lw=.5)
    ax.set(title="National autocorrelation (lags 1-24 months)", xlabel="Lag", ylabel="ACF"); fig.tight_layout()
    fig.savefig(FIG / "05_acf.png", dpi=150); plt.close(fig)
    # 6 summary tables
    prov = d.groupby("province")["cases"].sum(); prov_share = (prov / prov.sum() * 100).round(1)
    summary = pd.DataFrame({
        "total_cases": tot, "share_pct": (tot / tot.sum() * 100).round(2),
        "mean_monthly": d.groupby("district")["cases"].mean().round(1),
        "max_monthly": d.groupby("district")["cases"].max(),
        "cum_incidence_per_100k": inc.round(1)}).loc[tot.index]
    summary.to_csv(OUT / "eda_district_summary.csv")
    prov_share.to_csv(OUT / "eda_province_share.csv")
    yearly = nat.groupby(nat.index.year).sum(); yearly.to_csv(OUT / "eda_yearly_totals.csv")
    zeros = (d.cases == 0).mean() * 100
    print(f"Months: {nat.shape[0]} | total {int(nat.sum()):,} | zero district-months {zeros:.1f}%")
    print(yearly.to_string()); print(prov_share.sort_values(ascending=False).to_string())

if __name__ == "__main__":
    run()
