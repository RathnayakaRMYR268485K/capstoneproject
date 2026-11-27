"""Static mock-up of the planned interactive dashboard (risk-map view), drawn from the real outputs.
Writes outputs/figures/08_dashboard_mockup.png. Usage: python dashboard_mockup.py [District]"""
import sys
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, FancyBboxPatch, Circle
from matplotlib.colors import Normalize
from matplotlib import cm
from config import PROC, OUT, FIG
from geo import load_districts, polling_division_points, POLLING_DIVISIONS

SEL = sys.argv[1] if len(sys.argv) > 1 else "Colombo"
NAVY, INK, MUTED, LINE, PANEL, ACCENT = "#14213d", "#1f2937", "#6b7280", "#d1d5db", "#f7f8fa", "#2563eb"
plt.rcParams.update({"font.family": "DejaVu Sans"})

d = pd.read_csv(PROC / "monthly_district.csv", parse_dates=["month"])
cl = pd.read_csv(OUT / "district_clusters.csv").set_index("district")
fc = pd.read_csv(OUT / "forecasts.csv", parse_dates=["target_month"])
month = d.month.max()
cur = d[d.month == month].set_index("district")
dist = load_districts()
pds = polling_division_points(dist)

W, H = 16, 10
fig = plt.figure(figsize=(W, H), dpi=150)
fig.patch.set_facecolor("white")
def box(x, y, w, h, fc="white", ec=LINE, r=0.006, lw=1):
    fig.add_artist(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                  transform=fig.transFigure, fc=fc, ec=ec, lw=lw, zorder=-5))
def t(x, y, s, **k):
    k.setdefault("color", INK); k.setdefault("fontsize", 10)
    fig.text(x, y, s, transform=fig.transFigure, **k)

# ---- header + tabs
fig.add_artist(plt.Rectangle((0, 0.93), 1, 0.07, transform=fig.transFigure, fc=NAVY))
t(0.015, 0.956, "Sri Lanka Dengue Surveillance Dashboard", color="white", fontsize=17, weight="bold")
t(0.985, 0.956, f"Data: Epidemiology Unit WER · Dec 2021 – {month:%b %Y}", color="#c7d2fe", fontsize=9.5, ha="right")
for i, (tab, on) in enumerate([("Risk map", 1), ("Trends", 0), ("Clusters", 0), ("Forecast", 0)]):
    x = 0.015 + i * 0.085
    box(x, 0.885, 0.078, 0.034, fc=ACCENT if on else PANEL, ec=ACCENT if on else LINE)
    t(x + 0.039, 0.897, tab, ha="center", fontsize=10.5, color="white" if on else INK, weight="bold" if on else None)

# ---- left filter panel
box(0.015, 0.06, 0.19, 0.81, fc=PANEL)
y = 0.835
t(0.028, y, "FILTERS", fontsize=9, color=MUTED, weight="bold")
def dropdown(label, value, y):
    t(0.028, y, label, fontsize=9.5, color=MUTED)
    box(0.028, y - 0.042, 0.164, 0.032, fc="white")
    t(0.036, y - 0.031, value, fontsize=10.5)
    t(0.183, y - 0.032, "▾", fontsize=11, color=MUTED)
dropdown("Month", f"{month:%B %Y}", y - 0.035)
dropdown("District (click map or choose)", f"{SEL}", y - 0.115)
t(0.028, y - 0.19, "Colour districts by", fontsize=9.5, color=MUTED)
for j, (lab, on) in enumerate([("Incidence per 100,000", 1), ("Reported cases", 0), ("Risk tier (K-means)", 0)]):
    yy = y - 0.222 - j * 0.03
    t(0.029, yy - 0.002, "●" if on else "○", fontsize=13, color=ACCENT if on else MUTED)
    t(0.045, yy, lab, fontsize=10)
t(0.028, y - 0.335, "Map layers", fontsize=9.5, color=MUTED)
for j, lab in enumerate(["District boundaries (25)", "Polling divisions (160)", "District labels"]):
    yy = y - 0.367 - j * 0.03
    box(0.029, yy - 0.002, 0.011, 0.017, fc=ACCENT, ec=ACCENT, r=0.002)
    t(0.0316, yy + 0.0005, "✓", fontsize=8, color="white", weight="bold")
    t(0.045, yy, lab, fontsize=10)
# legend
vmax = float(np.ceil(cur.incidence_per_100k.max() / 10) * 10)
norm, cmap = Normalize(0, vmax), plt.get_cmap("YlOrRd")
t(0.028, y - 0.485, f"Incidence per 100,000 ({month:%b %Y})", fontsize=9.5, color=MUTED)
lax = fig.add_axes([0.028, y - 0.52, 0.164, 0.018], zorder=5)
lax.imshow(np.linspace(0, 1, 256)[None, :], aspect="auto", cmap=cmap); lax.set_yticks([])
lax.set_xticks([0, 127, 255]); lax.set_xticklabels(["0", f"{vmax/2:.0f}", f"{vmax:.0f}"], fontsize=8.5)
for s in lax.spines.values(): s.set_visible(False)
t(0.031, y - 0.585, "●", fontsize=8, color="#111827")
t(0.045, y - 0.583, "Polling division (indicative", fontsize=9)
t(0.045, y - 0.604, "position, data pending)", fontsize=9)
box(0.029, y - 0.643, 0.011, 0.017, fc="none", ec=ACCENT, lw=2.2, r=0.002)
t(0.045, y - 0.640, "Selected district", fontsize=9)
t(0.028, 0.09, "Mock-up of the planned interactive\ndashboard, drawn from real data.", fontsize=8.5, color=MUTED, linespacing=1.4)

# ---- map
ax = fig.add_axes([0.215, 0.06, 0.43, 0.81], zorder=5)
ax.set_facecolor("#eaf2fb")
for name, rings in dist.items():
    inc = cur.loc[name, "incidence_per_100k"]
    for r in rings:
        ax.add_patch(Polygon(r, closed=True, fc=cmap(norm(inc)), ec="white", lw=0.7, zorder=1))
for r in dist[SEL]:
    ax.add_patch(Polygon(r, closed=True, fc="none", ec=ACCENT, lw=2.6, zorder=4))
P = pd.DataFrame(pds, columns=["district", "pd", "lon", "lat"])
ax.scatter(P.lon, P.lat, s=9, c="#111827", edgecolor="white", lw=0.4, zorder=5)
for name, rings in dist.items():
    big = max(rings, key=len); c = big.mean(0)
    if name in ("Colombo", "Gampaha"): c = c + np.array([0.12 if name == "Colombo" else 0.0, 0])
    ax.text(c[0], c[1], name, fontsize=6.8, ha="center", va="center", zorder=6, color=INK,
            weight="bold" if name == SEL else None,
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.65))
ax.set_xlim(79.45, 82.05); ax.set_ylim(5.85, 9.9); ax.set_aspect("equal")
ax.set_xticks([]); ax.set_yticks([])
for s in ax.spines.values(): s.set_color(LINE)
# zoom controls + tooltip
for k, s in enumerate(["+", "−"]):
    ax.text(0.965, 0.965 - k * 0.045, s, transform=ax.transAxes, ha="center", va="center", fontsize=13,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=LINE))
sx, sy = max(dist[SEL], key=len).mean(0)
ax.annotate(f"{SEL}\n{int(cur.loc[SEL,'cases']):,} cases · {cur.loc[SEL,'incidence_per_100k']:.1f}/100k\n"
            f"{POLLING_DIVISIONS[SEL]} polling divisions",
            (sx, sy), xytext=(79.48, 6.02), fontsize=8.5, zorder=7, color=INK,
            bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=ACCENT, lw=1.2),
            arrowprops=dict(arrowstyle="-", color=ACCENT, lw=1.2))
ax.text(0.015, 0.012, "Boundaries: geoBoundaries (CC BY 4.0)", transform=ax.transAxes, fontsize=7, color=MUTED)

# ---- right detail panel
x0 = 0.66
box(x0, 0.06, 0.325, 0.81, fc=PANEL)
t(x0 + 0.015, 0.835, "SELECTED DISTRICT", fontsize=9, color=MUTED, weight="bold")
t(x0 + 0.015, 0.795, f"{SEL}", fontsize=20, weight="bold")
c0 = cl.loc[SEL]
t(x0 + 0.015, 0.77, f"{d[d.district==SEL].province.iloc[0]} Province · Risk {c0.risk_tier}", fontsize=10, color=MUTED)
hist = d[d.district == SEL].set_index("month")
kp = [(f"{int(cur.loc[SEL,'cases']):,}", f"Cases, {month:%b %Y}"),
      (f"{cur.loc[SEL,'incidence_per_100k']:.1f}", "Incidence /100k"),
      (f"{int(hist.cases.sum()):,}", "Cases, 48 months")]
for i, (v, lab) in enumerate(kp):
    bx = x0 + 0.015 + i * 0.1
    box(bx, 0.66, 0.092, 0.085)
    t(bx + 0.008, 0.705, v, fontsize=15, weight="bold")
    t(bx + 0.008, 0.675, lab, fontsize=8.2, color=MUTED)
# sparkline
t(x0 + 0.015, 0.625, "Monthly cases, last 48 months", fontsize=9.5, color=MUTED)
sax = fig.add_axes([x0 + 0.03, 0.47, 0.28, 0.145], zorder=5)
sax.fill_between(hist.index, hist.cases, color=ACCENT, alpha=0.15); sax.plot(hist.index, hist.cases, color=ACCENT, lw=1.6)
sax.tick_params(labelsize=7.5, colors=MUTED); sax.set_facecolor("white")
for s in ["top", "right"]: sax.spines[s].set_visible(False)
for s in ["left", "bottom"]: sax.spines[s].set_color(LINE)
# forecast table
t(x0 + 0.015, 0.415, "Random Forest forecast (80% interval)", fontsize=9.5, color=MUTED)
f = fc[fc.district == SEL].sort_values("horizon")
for i, (_, r) in enumerate(f.iterrows()):
    yy = 0.38 - i * 0.034
    t(x0 + 0.02, yy, f"{r.target_month:%b %Y}", fontsize=10)
    t(x0 + 0.13, yy, f"{r.forecast:,.0f}", fontsize=10, weight="bold")
    t(x0 + 0.2, yy, f"{r.lower80:,.0f} – {r.upper80:,.0f}", fontsize=10, color=MUTED)
# polling-division list
t(x0 + 0.015, 0.225, f"Polling divisions in {SEL}: {POLLING_DIVISIONS[SEL]}", fontsize=9.5, color=MUTED)
box(x0 + 0.015, 0.085, 0.295, 0.13, fc="white")
t(x0 + 0.025, 0.18, "Shown as points on the map. Case counts by", fontsize=9.2)
t(x0 + 0.025, 0.155, "polling division are not published, so these", fontsize=9.2)
t(x0 + 0.025, 0.13, "points have no values yet. Positions are", fontsize=9.2)
t(x0 + 0.025, 0.105, "indicative (spread evenly inside the district).", fontsize=9.2)

fig.savefig(FIG / "08_dashboard_mockup.png", dpi=150)
print("wrote", FIG / "08_dashboard_mockup.png", "| PD points:", len(pds))
