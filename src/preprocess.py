"""Step 2 - preprocessing: clean, standardise, validate, aggregate weekly -> monthly, keep last 48 complete months."""
import json, sys
import numpy as np, pandas as pd
from config import *

def load_raw(path=None):
    path = Path(path) if path else RAW / "srilanka_weekly_dengue.csv"
    if not path.exists():
        sys.exit(f"Missing {path}. Run scripts/01_export_dengue_csv.R first (see README).")
    return pd.read_csv(path)

def preprocess(df: pd.DataFrame):
    q = {"raw_rows": len(df)}
    df = df.copy()
    df.columns = [c.strip().lower().replace(".", "_") for c in df.columns]
    df["district"] = df["district"].map(lambda s: KEY2NAME.get(norm_key(s)))
    q["unmapped_district_rows"] = int(df["district"].isna().sum())
    df = df.dropna(subset=["district"])
    q["true_duplicate_rows"] = int(df.duplicated(["district", "start_date"]).sum())
    if MERGE_KALMUNAI_INTO_AMPARA:
        q["kalmunai_rows_merged_into_ampara"] = int((df["district"] == "Kalmunai").sum())
        df["district"] = df["district"].replace({"Kalmunai": "Ampara"})
    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
    df["end_date"] = pd.to_datetime(df["end_date"], errors="coerce")
    q["bad_date_rows"] = int(df["start_date"].isna().sum())
    df = df.dropna(subset=["start_date"])
    df["cases"] = pd.to_numeric(df["cases"], errors="coerce")
    q["missing_cases"] = int(df["cases"].isna().sum())
    q["negative_cases"] = int((df["cases"] < 0).sum())
    df.loc[df["cases"] < 0, "cases"] = np.nan
    key = ["district", "start_date"]
    q["district_weeks_summed_after_merge"] = int(df.duplicated(key).sum())
    df = df.groupby(key, as_index=False).agg(cases=("cases", "sum"), end_date=("end_date", "max"))
    weeks = pd.date_range(df.start_date.min(), df.start_date.max(), freq="7D")
    grid = pd.MultiIndex.from_product([sorted(df.district.unique()), weeks], names=key)
    wk = df.set_index(key).reindex(grid).reset_index()
    q["missing_district_weeks_after_grid"] = int(wk["cases"].isna().sum())
    wk["mid_date"] = wk["start_date"] + pd.Timedelta(days=3)      # week -> month by mid-week date
    wk["month"] = wk["mid_date"].dt.to_period("M").dt.to_timestamp()
    mo = wk.groupby(["district", "month"]).agg(cases=("cases", "sum"), n_weeks=("cases", "count")).reset_index()
    ok = mo.groupby("month")["n_weeks"].min()
    mo = mo[mo.month.isin(ok[ok >= 4].index)]                      # complete months only
    last = mo.month.max()
    first = last - pd.DateOffset(months=N_MONTHS - 1)
    mo = mo[(mo.month >= first) & (mo.month <= last)]
    full = pd.MultiIndex.from_product([sorted(mo.district.unique()), pd.date_range(first, last, freq="MS")],
                                      names=["district", "month"])
    mo = mo.set_index(["district", "month"]).reindex(full).reset_index()
    mo["imputed"] = mo["cases"].isna()
    q["imputed_district_months"] = int(mo["imputed"].sum())
    mo["cases"] = mo.groupby("district")["cases"].transform(lambda s: s.interpolate(limit_direction="both"))
    mo["cases"] = mo["cases"].round().clip(lower=0).astype(int)
    mo["province"] = mo["district"].map(lambda d: DISTRICTS[d][0])
    mo["population"] = mo["district"].map(lambda d: DISTRICTS[d][3])
    mo["incidence_per_100k"] = mo["cases"] / mo["population"] * 1e5
    q.update(window_start=str(first.date()), window_end=str(last.date()), n_months=int(mo.month.nunique()),
             n_districts=int(mo.district.nunique()), total_cases_in_window=int(mo.cases.sum()))
    wk_out = wk[wk.month.between(first, last)][["district", "start_date", "cases"]]
    return mo, wk_out, q

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else None
    mo, wk, q = preprocess(load_raw(src))
    mo.to_csv(PROC / "monthly_district.csv", index=False)
    wk.to_csv(PROC / "weekly_district_window.csv", index=False)
    (OUT / "data_quality_report.json").write_text(json.dumps(q, indent=2))
    print(json.dumps(q, indent=2))
