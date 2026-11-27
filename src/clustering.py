"""K-means clustering of districts by epidemiological profile (elbow + silhouette validation)."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from config import *

def features(d: pd.DataFrame) -> pd.DataFrame:
    rows = {}
    for dist, g in d.groupby("district"):
        s = g.sort_values("month").set_index("month")["cases"].astype(float)
        inc = g.sort_values("month")["incidence_per_100k"]
        m = s.groupby(s.index.month).mean()
        rows[dist] = {
            "mean_incidence_100k": inc.mean(),
            "volatility_cv": s.std() / (s.mean() + 1e-9),
            "peak_to_mean": s.max() / (s.mean() + 1e-9),
            "seasonal_amplitude": (m.max() - m.min()) / (m.mean() + 1e-9),
            "trend_slope_norm": np.polyfit(np.arange(len(s)), s.values, 1)[0] / (s.mean() + 1e-9),
        }
    return pd.DataFrame(rows).T

def run():
    d = pd.read_csv(PROC / "monthly_district.csv", parse_dates=["month"])
    F = features(d); X = StandardScaler().fit_transform(np.log1p(F.clip(lower=0)))
    ks = range(2, min(9, len(F)))
    inertia, sil = [], []
    for k in ks:
        km = KMeans(k, n_init=20, random_state=RANDOM_STATE).fit(X)
        inertia.append(km.inertia_); sil.append(silhouette_score(X, km.labels_))
    best = list(ks)[int(np.argmax(sil))]
    km = KMeans(best, n_init=20, random_state=RANDOM_STATE).fit(X)
    F["cluster"] = km.labels_
    order = F.groupby("cluster")["mean_incidence_100k"].mean().sort_values().index   # relabel low->high risk
    F["cluster"] = F["cluster"].map({c: i for i, c in enumerate(order)})
    F["risk_tier"] = F["cluster"].map(lambda c: f"Tier {c + 1} of {best}" + (" (lowest)" if c == 0 else " (highest)" if c == best - 1 else ""))
    F.round(3).to_csv(OUT / "district_clusters.csv", index_label="district")
    pd.DataFrame({"k": list(ks), "inertia": inertia, "silhouette": sil}).to_csv(OUT / "kmeans_validation.csv", index=False)
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.5))
    axs[0].plot(list(ks), inertia, "o-"); axs[0].set(title="Elbow", xlabel="k", ylabel="Inertia")
    axs[1].plot(list(ks), sil, "o-"); axs[1].axvline(best, c="r", ls="--"); axs[1].set(title="Silhouette", xlabel="k")
    fig.tight_layout(); fig.savefig(FIG / "06_kmeans_validation.png", dpi=150); plt.close(fig)
    print(f"Best k={best} (silhouette={max(sil):.3f})"); print(F.groupby("cluster").size().to_string())
    return F

if __name__ == "__main__":
    run()
