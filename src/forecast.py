"""Forecasting: baseline (seasonal naive) vs improved (pooled direct multi-horizon Random Forest, log scale)
with optional national SARIMA. Rolling-origin (expanding window) back-testing, MAE/RMSE/MAPE, 80% intervals."""
import warnings, json
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from config import *

MIN_T = 11          # first usable origin (needs 12 months of history)
FIRST_TEST = 23     # first back-test origin (>= 24 months of history)

def load_wide():
    d = pd.read_csv(PROC / "monthly_district.csv", parse_dates=["month"])
    return d.pivot(index="month", columns="district", values="cases").astype(float)

def make_features(L: np.ndarray, months: pd.DatetimeIndex, t: int, h: int) -> np.ndarray:
    """Features for origin t (uses data <= t only), target month t+h. L = log1p cases (T x D)."""
    tm = months[t].month + h; tm = (tm - 1) % 12 + 1
    D = L.shape[1]
    f = [L[t], L[t - 1], L[t - 2], L[t - 5], L[t - 11],
         L[t - 2:t + 1].mean(0), L[t - 5:t + 1].mean(0), L[t - 11:t + 1].mean(0),
         L[t + h - 12] if h <= 12 else L[t - 11],              # seasonal lag aligned with the target month
         L[:t + 1].mean(0),                                      # district level
         np.full(D, np.sin(2 * np.pi * tm / 12)), np.full(D, np.cos(2 * np.pi * tm / 12))]
    return np.column_stack(f)

def fit_rf(L, months, h, last_origin):
    X, y = [], []
    for s in range(MIN_T, last_origin - h + 1):               # target s+h must be known by last_origin
        X.append(make_features(L, months, s, h)); y.append(L[s + h])
    if not X: return None
    rf = RandomForestRegressor(n_estimators=200, min_samples_leaf=2, max_features=0.6,
                               random_state=RANDOM_STATE, n_jobs=-1)
    return rf.fit(np.vstack(X), np.concatenate(y))

def seasonal_naive(Y, t, h):
    return Y[t + h - 12]                                       # same calendar month last year

def metrics(a, p):
    a, p = np.asarray(a, float), np.asarray(p, float); m = a > 0
    return {"MAE": float(np.mean(np.abs(a - p))), "RMSE": float(np.sqrt(np.mean((a - p) ** 2))),
            "MAPE": float(np.mean(np.abs(a[m] - p[m]) / a[m]) * 100) if m.any() else np.nan,
            "n": int(a.size)}

def sarima_national(nat: pd.Series, t: int, h: int):
    try:
        from statsmodels.tsa.statespace.sarimax import SARIMAX
    except ImportError:
        return None
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fit = SARIMAX(np.log1p(nat.values[:t + 1]), order=(1, 0, 1), seasonal_order=(0, 1, 0, 12),
                          enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)
            return float(np.expm1(fit.forecast(h)[-1]))
    except Exception:
        return None

def backtest(Y: pd.DataFrame):
    months, Yv = Y.index, Y.values; L = np.log1p(Yv); T, D = Yv.shape
    rows, nat = [], Y.sum(axis=1)
    for h in HORIZONS:
        for t in range(FIRST_TEST, T - h):
            rf = fit_rf(L, months, h, t)
            p_rf = np.expm1(rf.predict(make_features(L, months, t, h))).clip(min=0)
            p_nv = seasonal_naive(Yv, t, h)
            p_sa = sarima_national(nat, t, h)
            for j, dist in enumerate(Y.columns):
                rows.append(dict(origin=months[t], target=months[t + h], horizon=h, district=dist,
                                 actual=Yv[t + h, j], seasonal_naive=p_nv[j], random_forest=p_rf[j]))
            rows.append(dict(origin=months[t], target=months[t + h], horizon=h, district="NATIONAL",
                             actual=Yv[t + h].sum(), seasonal_naive=p_nv.sum(), random_forest=p_rf.sum(),
                             sarima=p_sa))
    return pd.DataFrame(rows)

def evaluate(bt: pd.DataFrame):
    out = []
    for h, g in bt.groupby("horizon"):
        for level, sub in (("national", g[g.district == "NATIONAL"]), ("district", g[g.district != "NATIONAL"])):
            for model in ("seasonal_naive", "random_forest", "sarima"):
                if model not in sub or sub[model].isna().all(): continue
                s = sub.dropna(subset=[model]); out.append({"horizon": h, "level": level, "model": model,
                                                            **metrics(s.actual, s[model])})
    return pd.DataFrame(out)

def interval_factors(bt: pd.DataFrame, alpha=0.2):
    """Empirical (alpha/2, 1-alpha/2) quantiles of log(actual+1) - log(pred+1) per horizon & level."""
    f = {}
    for h, g in bt.groupby("horizon"):
        for level, sub in (("national", g[g.district == "NATIONAL"]), ("district", g[g.district != "NATIONAL"])):
            r = np.log1p(sub.actual) - np.log1p(sub.random_forest)
            f[(h, level)] = (float(np.quantile(r, alpha / 2)), float(np.quantile(r, 1 - alpha / 2)))
    return f

def coverage(bt, f):
    out = []
    for (h, level), (lo, hi) in f.items():
        sub = bt[(bt.horizon == h) & ((bt.district == "NATIONAL") == (level == "national"))]
        l = np.expm1(np.log1p(sub.random_forest) + lo); u = np.expm1(np.log1p(sub.random_forest) + hi)
        out.append({"horizon": h, "level": level, "coverage_80pct": float(((sub.actual >= l) & (sub.actual <= u)).mean())})
    return pd.DataFrame(out)

def final_forecast(Y, f):
    months, Yv = Y.index, Y.values; L = np.log1p(Yv); t = len(Y) - 1; rows = []
    for h in HORIZONS:
        rf = fit_rf(L, months, h, t)
        p = np.expm1(rf.predict(make_features(L, months, t, h))).clip(min=0)
        target = months[t] + pd.DateOffset(months=h)
        for j, dist in enumerate(Y.columns):
            lo, hi = f[(h, "district")]
            rows.append(dict(district=dist, horizon=h, target_month=target, forecast=p[j],
                             lower80=max(0, np.expm1(np.log1p(p[j]) + lo)), upper80=np.expm1(np.log1p(p[j]) + hi)))
        lo, hi = f[(h, "national")]; n = p.sum()
        rows.append(dict(district="NATIONAL", horizon=h, target_month=target, forecast=n,
                         lower80=max(0, np.expm1(np.log1p(n) + lo)), upper80=np.expm1(np.log1p(n) + hi)))
    return pd.DataFrame(rows)

def run():
    Y = load_wide()
    bt = backtest(Y); bt.to_csv(OUT / "backtest_predictions.csv", index=False)
    m = evaluate(bt); m.to_csv(OUT / "model_metrics.csv", index=False)
    f = interval_factors(bt); cov = coverage(bt, f); cov.to_csv(OUT / "interval_coverage.csv", index=False)
    fc = final_forecast(Y, f); fc.to_csv(OUT / "forecasts.csv", index=False)
    # improvement summary: RF vs baseline (MAE reduction %)
    piv = m.pivot_table(index=["level", "horizon"], columns="model", values="MAE")
    piv["rf_vs_naive_MAE_reduction_pct"] = (1 - piv["random_forest"] / piv["seasonal_naive"]) * 100
    piv.round(2).to_csv(OUT / "model_comparison_MAE.csv")
    # plot: national backtest, h=1 and h=6
    fig, axs = plt.subplots(1, 2, figsize=(12, 3.8))
    for ax, h in zip(axs, (1, 6)):
        g = bt[(bt.district == "NATIONAL") & (bt.horizon == h)].sort_values("target")
        ax.plot(g.target, g.actual, "k-o", ms=3, label="Actual")
        ax.plot(g.target, g.seasonal_naive, "--", label="Seasonal naive (baseline)")
        ax.plot(g.target, g.random_forest, "-", label="Random Forest (improved)")
        ax.set(title=f"National back-test, {h}-month horizon"); ax.legend(fontsize=7); ax.tick_params(axis="x", rotation=45, labelsize=7)
    fig.tight_layout(); fig.savefig(FIG / "07_backtest_national.png", dpi=150); plt.close(fig)
    print(m.pivot_table(index=["level", "horizon"], columns="model", values=["MAE", "MAPE"]).round(1).to_string())
    print(cov.round(2).to_string())
    return m

if __name__ == "__main__":
    run()
