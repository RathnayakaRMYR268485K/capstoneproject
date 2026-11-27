"""SMOKE-TEST ONLY. Generates a SYNTHETIC weekly district dataset in the same schema as the real data,
so the pipeline can be tested offline. NEVER use outputs from this for the submission."""
import numpy as np, pandas as pd, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from config import DISTRICTS
rng = np.random.default_rng(0)
weeks = pd.date_range("2021-01-02", "2025-06-28", freq="7D")
rows = []
base = {d: DISTRICTS[d][3] / 1e6 for d in DISTRICTS}
for d, b in base.items():
    for i, w in enumerate(weeks):
        season = 1 + 0.6 * np.cos(2 * np.pi * (w.dayofyear - 170) / 182.5) + 0.5 * np.cos(2 * np.pi * (w.dayofyear - 30) / 365)
        lam = max(0.2, 12 * b * season * (1 + 0.3 * np.sin(i / 90)))
        rows.append((w.year, w.isocalendar().week, w.strftime("%m/%d/%Y"), (w + pd.Timedelta(days=6)).strftime("%m/%d/%Y"),
                     d.replace(" ", ""), rng.poisson(lam)))
df = pd.DataFrame(rows, columns=["year", "week", "start.date", "end.date", "district", "cases"])
df.to_csv(sys.argv[1], index=False); print("wrote", len(df), "synthetic rows ->", sys.argv[1])
