"""Dengue surveillance dashboard (Streamlit). Run:  streamlit run app.py
Reads the files produced by the pipeline (data/processed, outputs/). Not a substitute for official surveillance."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))
import pandas as pd, plotly.express as px, streamlit as st
from config import PROC, OUT, GEO, DISTRICTS

st.set_page_config(page_title="Sri Lanka Dengue Dashboard", layout="wide")

@st.cache_data
def load():
    d = pd.read_csv(PROC / "monthly_district.csv", parse_dates=["month"])
    cl = pd.read_csv(OUT / "district_clusters.csv").set_index("district")
    fc = pd.read_csv(OUT / "forecasts.csv", parse_dates=["target_month"])
    mt = pd.read_csv(OUT / "model_comparison_MAE.csv")
    return d, cl, fc, mt
d, cl, fc, mt = load()
coords = pd.DataFrame(DISTRICTS, index=["province", "lat", "lon", "pop"]).T[["lat", "lon"]].astype(float)

st.title("Dengue Surveillance, Risk Analysis & Forecasting - Sri Lanka")
st.caption(f"Data window: {d.month.min():%b %Y} - {d.month.max():%b %Y} (48 months, district level). "
           "Forecasts are estimates with 80% intervals, not guaranteed outcomes.")
tab1, tab2, tab3, tab4 = st.tabs(["Risk map", "Trends", "Clusters", "Forecast"])

with tab1:
    metric = st.radio("Colour by", ["incidence_per_100k", "cases"], horizontal=True)
    months = sorted(d.month.unique())
    sel = st.select_slider("Month", options=months, value=months[-1], format_func=lambda x: pd.Timestamp(x).strftime("%b %Y"))
    m = d[d.month == sel].set_index("district")
    c1, c2 = st.columns([3, 1])
    pick_d = c2.selectbox("Select district", sorted(m.index), index=sorted(m.index).index("Colombo"))
    show_pd = c2.checkbox("Show 160 polling divisions (indicative positions)", value=True)
    geo = GEO / "lka_districts_geoboundaries.geojson"
    if geo.exists():
        from config import KEY2NAME, norm_key
        from geo import load_districts, polling_division_points, POLLING_DIVISIONS
        gj = json.loads(geo.read_text())
        for f in gj["features"]:   # id = project district name, e.g. "Colombo District" -> "Colombo"
            f["id"] = KEY2NAME[norm_key(f["properties"]["shapeName"].replace(" District", ""))]
        fig = px.choropleth_mapbox(m.reset_index(), geojson=gj, locations="district", color=metric,
                                   hover_name="district", hover_data={"cases": True, "incidence_per_100k": ":.1f"},
                                   color_continuous_scale="YlOrRd", mapbox_style="carto-positron",
                                   zoom=6.3, center={"lat": 7.8, "lon": 80.7}, opacity=0.85)
        sel_gj = {"type": "FeatureCollection", "features": [f for f in gj["features"] if f["id"] == pick_d]}
        fig.update_layout(mapbox_layers=[{"source": sel_gj, "type": "line", "color": "#2563eb", "line": {"width": 4}}])
        if show_pd:
            P = pd.DataFrame(polling_division_points(load_districts()), columns=["district", "pd", "lon", "lat"])
            P["label"] = P.district + " polling division " + P.pd.astype(str) + " (case data not yet published)"
            fig.add_scattermapbox(lat=P.lat, lon=P.lon, mode="markers", text=P.label, hoverinfo="text",
                                  marker=dict(size=6, color="#111827"), name="Polling divisions (160)")
        r = m.loc[pick_d]
        c2.metric("Cases", f"{int(r.cases):,}"); c2.metric("Incidence /100k", f"{r.incidence_per_100k:.1f}")
        c2.metric("Polling divisions", POLLING_DIVISIONS[pick_d])
        c2.caption("Dengue cases are published by district only, so polling-division points carry no values yet.")
    else:
        mm = m.join(coords); st.info("No boundary file at data/geo/lka_districts.geojson - showing district centroids.")
        fig = px.scatter_mapbox(mm.reset_index(), lat="lat", lon="lon", size=mm[metric].clip(lower=0.1), color=metric,
                                hover_name="district", color_continuous_scale="YlOrRd", size_max=40,
                                mapbox_style="carto-positron", zoom=6.3, center={"lat": 7.8, "lon": 80.7})
    fig.update_layout(height=620, margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
    c1.plotly_chart(fig, use_container_width=True)

with tab2:
    opts = ["NATIONAL"] + sorted(d.district.unique()); pick = st.selectbox("Area", opts)
    s = d.groupby("month", as_index=False)["cases"].sum() if pick == "NATIONAL" else d[d.district == pick]
    st.plotly_chart(px.line(s, x="month", y="cases", markers=True, title=f"{pick}: monthly cases"), use_container_width=True)

with tab3:
    c = cl.reset_index(); c["lat"] = c.district.map(coords.lat); c["lon"] = c.district.map(coords.lon)
    st.plotly_chart(px.scatter_mapbox(c, lat="lat", lon="lon", color=c.cluster.astype(str), hover_name="district",
                    size=c.mean_incidence_100k.clip(lower=0.1), size_max=35, mapbox_style="carto-positron",
                    zoom=6.3, center={"lat": 7.8, "lon": 80.7}, height=560), use_container_width=True)
    st.dataframe(c.drop(columns=["lat", "lon"]).round(2), use_container_width=True)

with tab4:
    pick = st.selectbox("Area ", ["NATIONAL"] + sorted(d.district.unique()), key="fcarea")
    hist = (d.groupby("month", as_index=False)["cases"].sum() if pick == "NATIONAL" else d[d.district == pick][["month", "cases"]])
    f = fc[fc.district == pick].sort_values("horizon")
    import plotly.graph_objects as go
    fig = go.Figure()
    fig.add_scatter(x=hist.month, y=hist.cases, name="Observed", mode="lines+markers")
    fig.add_scatter(x=f.target_month, y=f.forecast, name="Forecast (1/3/6/12 mo)", mode="markers+lines")
    fig.add_scatter(x=list(f.target_month) + list(f.target_month[::-1]), y=list(f.upper80) + list(f.lower80[::-1]),
                    fill="toself", name="80% interval", line=dict(width=0), opacity=0.25)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(f[["horizon", "target_month", "forecast", "lower80", "upper80"]].round(0), use_container_width=True)
    st.subheader("Back-test comparison (MAE)"); st.dataframe(mt, use_container_width=True)
