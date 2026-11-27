"""District boundaries (geoBoundaries LKA ADM2, CC BY 4.0) and indicative polling-division points.

Sri Lanka has 160 polling divisions. Dengue case data is published only by district (and MOH area),
so polling divisions cannot be mapped with case data yet. This module places the correct NUMBER of
polling-division points inside each district at INDICATIVE positions (evenly spread with K-means),
so the dashboard layout is ready for when division-level data becomes available.
"""
import json
import numpy as np
from matplotlib.path import Path as MPath
from sklearn.cluster import KMeans
from config import GEO, norm_key, KEY2NAME

GEOJSON = GEO / "lka_districts_geoboundaries.geojson"

# Polling divisions per administrative district (160 in total).
# Jaffna electoral district (11) = Jaffna 10 + Kilinochchi 1; Vanni (3) = Mannar, Vavuniya, Mullaitivu;
# Digamadulla (4) = Ampara.
POLLING_DIVISIONS = {
    "Colombo": 15, "Gampaha": 13, "Kalutara": 8, "Kandy": 13, "Matale": 4, "Nuwara Eliya": 4,
    "Galle": 10, "Matara": 7, "Hambantota": 4, "Jaffna": 10, "Kilinochchi": 1, "Mannar": 1,
    "Vavuniya": 1, "Mullaitivu": 1, "Batticaloa": 3, "Ampara": 4, "Trincomalee": 3,
    "Kurunegala": 14, "Puttalam": 5, "Anuradhapura": 7, "Polonnaruwa": 3, "Badulla": 9,
    "Monaragala": 3, "Ratnapura": 8, "Kegalle": 9,
}
assert sum(POLLING_DIVISIONS.values()) == 160


def load_districts():
    """Return {district: [ring arrays (N x 2, lon/lat)]} using the project's district names."""
    g = json.loads(GEOJSON.read_text())
    out = {}
    for f in g["features"]:
        name = KEY2NAME[norm_key(f["properties"]["shapeName"].replace(" District", ""))]
        geom = f["geometry"]
        polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        out[name] = [np.asarray(p[0]) for p in polys]          # outer rings
    return out


def polling_division_points(districts, seed=42):
    """Indicative points: n evenly spread locations inside each district's largest polygon."""
    rng = np.random.default_rng(seed)
    pts = []
    for d, n in POLLING_DIVISIONS.items():
        ring = max(districts[d], key=len)
        path = MPath(ring)
        (x0, y0), (x1, y1) = ring.min(0), ring.max(0)
        cand = np.column_stack([rng.uniform(x0, x1, 6000), rng.uniform(y0, y1, 6000)])
        cand = cand[path.contains_points(cand)]
        if n == 1:
            c = cand.mean(0)
            centre = c if path.contains_point(c) else cand[np.argmin(((cand - c) ** 2).sum(1))]
            centres = [centre]
        else:
            km = KMeans(n, n_init=4, random_state=seed).fit(cand)
            centres = [cand[np.argmin(((cand - c) ** 2).sum(1))] for c in km.cluster_centers_]
        pts += [(d, i + 1, float(p[0]), float(p[1])) for i, p in enumerate(centres)]
    return pts
