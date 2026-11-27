from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
GEO = ROOT / "data" / "geo"
OUT = ROOT / "outputs"
FIG = OUT / "figures"
for p in (PROC, OUT, FIG):
    p.mkdir(parents=True, exist_ok=True)

N_MONTHS = 48                 # project definition: minimum 48 months
HORIZONS = [1, 3, 6, 12]
RANDOM_STATE = 42
MERGE_KALMUNAI_INTO_AMPARA = True   # Kalmunai is a health district carved out of Ampara

# Canonical 25 administrative districts: (province, lat, lon, 2012-census population)
# Centroids are approximate (for bubble maps when no boundary file is supplied).
# Population = 2012 Census (DCS), entered from memory - VERIFY against DCS tables before citing.
DISTRICTS = {
    "Colombo": ("Western", 6.93, 79.86, 2324349), "Gampaha": ("Western", 7.09, 80.00, 2304833),
    "Kalutara": ("Western", 6.58, 80.07, 1221948), "Kandy": ("Central", 7.29, 80.63, 1375382),
    "Matale": ("Central", 7.47, 80.62, 484531), "Nuwara Eliya": ("Central", 6.97, 80.77, 706588),
    "Galle": ("Southern", 6.05, 80.22, 1058248), "Matara": ("Southern", 5.95, 80.55, 814048),
    "Hambantota": ("Southern", 6.12, 81.12, 599903), "Jaffna": ("Northern", 9.66, 80.02, 583882),
    "Kilinochchi": ("Northern", 9.40, 80.40, 112875), "Mannar": ("Northern", 8.98, 79.91, 99570),
    "Vavuniya": ("Northern", 8.75, 80.50, 172115), "Mullaitivu": ("Northern", 9.27, 80.81, 92238),
    "Batticaloa": ("Eastern", 7.71, 81.69, 526567), "Ampara": ("Eastern", 7.30, 81.67, 649402),
    "Trincomalee": ("Eastern", 8.57, 81.23, 379541), "Kurunegala": ("North Western", 7.49, 80.36, 1618465),
    "Puttalam": ("North Western", 8.03, 79.83, 762396), "Anuradhapura": ("North Central", 8.34, 80.41, 860575),
    "Polonnaruwa": ("North Central", 7.94, 81.00, 403335), "Badulla": ("Uva", 6.99, 81.06, 815405),
    "Monaragala": ("Uva", 6.87, 81.35, 451058), "Ratnapura": ("Sabaragamuwa", 6.68, 80.40, 1082299),
    "Kegalle": ("Sabaragamuwa", 7.25, 80.35, 840648),
}
def norm_key(s: str) -> str:
    return "".join(ch for ch in str(s).lower() if ch.isalpha())
KEY2NAME = {norm_key(k): k for k in DISTRICTS}
KEY2NAME["kalmunai"] = "Kalmunai"
# spelling variants seen in the WER / denguedatahub data
KEY2NAME.update({"kalmune": "Kalmunai", "hambanthota": "Hambantota", "nuwaraeliya": "Nuwara Eliya",
                 "monaragala": "Monaragala", "moneragala": "Monaragala"})
