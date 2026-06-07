"""Nature-quality manuscript figures — Natural Earth coastline + matplotlib."""
import json, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from pathlib import Path

out = Path("figures/generated"); out.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif", "font.size": 8,
    "axes.titlesize": 9, "axes.labelsize": 8,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
    "figure.dpi": 300, "savefig.dpi": 300, "savefig.bbox": "tight",
    "axes.spines.top": False, "axes.spines.right": False,
})
C = {"soil_moisture": "#2166ac", "vapour_pressure_deficit": "#b2182b",
     "2m_temperature": "#d6604d", "total_precipitation": "#4393c3",
     "surface_net_solar_radiation": "#f4a582"}

# ---- Load coastline ----
with open("data/aux/ne_50m_coastline.geojson") as f:
    coast = json.load(f)
aus_bbox = (108, 158, -45, -5)
aus_feats = []
for feat in coast["features"]:
    geom = feat["geometry"]; c = geom["coordinates"]
    if geom["type"]=="LineString": rings=[c]
    elif geom["type"]=="MultiLineString": rings=c
    elif geom["type"]=="Polygon": rings=c[:1]
    elif geom["type"]=="MultiPolygon": rings=[r for p in c for r in p[:1]]
    else: continue
    for ring in rings:
        if any(aus_bbox[0]<=pt[0]<=aus_bbox[1] and aus_bbox[2]<=pt[1]<=aus_bbox[3] for pt in ring):
            aus_feats.append((feat,geom["type"])); break  # dedupe via break
print(f"Coastline: {len(aus_feats)} features")

def plot_coast(ax):
    for feat, gtype in aus_feats:
        c = feat["geometry"]["coordinates"]
        if gtype=="LineString": rings=[c]
        elif gtype=="MultiLineString": rings=c
        elif gtype=="Polygon": rings=[c[0]]
        elif gtype=="MultiPolygon": rings=[r for p in c for r in p[:1]]
        else: continue
        for ring in rings:
            lons,lats = zip(*ring); ax.plot(lons,lats,"k-",lw=0.25)

def gridlines(ax):
    for lon in np.arange(110,155,5): ax.axvline(lon,color="#ddd",lw=0.15,zorder=0)
    for lat in np.arange(-40,-10,5): ax.axhline(lat,color="#ddd",lw=0.15,zorder=0)

# ===== Fig 1 =====
fig = plt.figure(figsize=(7.5, 3.8))
ax = fig.add_axes([0.05,0.12,0.52,0.82]); plot_coast(ax); gridlines(ax)
ax.add_patch(Rectangle((109.75,-40.25),40.5,30.25,lw=1.2,ec="#b2182b",fc="none",ls="--",zorder=5))
ax.text(130,-13.5,"Study domain\n0.25° × 0.25°\n162 × 121 grid cells",ha="center",fontsize=7,c="#b2182b",
    fontweight="bold",bbox=dict(facecolor="white",alpha=0.85,ec="none",pad=1))
for lon,lat,lbl in [(144.96,-37.81,"Melbourne"),(153.03,-27.47,"Brisbane"),(115.86,-31.95,"Perth")]:
    ax.plot(lon,lat,"o",color="#333",ms=2.5); ax.text(lon+1.5,lat+0.3,lbl,fontsize=6,
        bbox=dict(facecolor="white",alpha=0.7,ec="none",pad=0.5))
ax.set(xlim=(108.5,157.5),ylim=(-44.5,-4.5),xlabel="Longitude (°E)",ylabel="Latitude (°S)")
ax.set_title("a  Study domain",loc="left",fontweight="bold",fontsize=9)
ax2 = fig.add_axes([0.62,0.12,0.35,0.82]); ax2.axis("off")
y=0.93
for t,d in [("1  Data export","GEE: MODIS MOD13Q1/MYD13Q1 + ERA5-Land hourly"),
    ("2  Shared grid","0.25°, EPSG:4326; grid alignment audit"),
    ("3  Quality filter","VI Quality bitmask → 52.1% retention"),
    ("4  Anomalies + events","EVI DOY climatology; 10th pctl; ≥2 composites"),
    ("5  Lagged features","5 climate vars × 4 lead times (16–64 d)"),
    ("6  Validation","Temporal holdout (20%); Spatial (20 regions); Placebo")]:
    ax2.text(0.02,y,t,fontweight="bold",fontsize=7.5,transform=ax2.transAxes,va="top")
    ax2.text(0.02,y-0.040,d,fontsize=6.5,color="#555",transform=ax2.transAxes,va="top")
    y-=0.138
ax2.set_title("b  Analysis pipeline",loc="left",fontweight="bold",fontsize=9,pad=8)
fig.savefig(out/"fig1_study_domain.png",dpi=300); plt.close(); print("Fig 1 done")

# ===== Fig 2 =====
es = pd.read_csv("results/stress_events/event_catalogue_summary.csv")
es["year"]=pd.to_datetime(es["start_date"]).dt.year; es["month"]=pd.to_datetime(es["start_date"]).dt.month
fig,axes=plt.subplots(2,2,figsize=(7.5,5.5))
annual=es.groupby("year").size()
axes[0,0].bar(annual.index.astype(str),annual.values,color="#2166ac",alpha=0.85,width=0.7)
axes[0,0].set(xlabel="Year",ylabel="Events",title="a  Annual stress events")
axes[0,0].tick_params(axis="x",rotation=45,labelsize=6)
monthly=es.groupby("month").size()
axes[0,1].bar(monthly.index,monthly.values,color="#4393c3",alpha=0.85,width=0.7)
axes[0,1].set(xlabel="Month",ylabel="Events",title="b  Seasonal distribution",xticks=range(1,13))
pp=es.groupby("pixel_id").size()
axes[1,0].hist(np.log10(pp.values+1),bins=35,color="#f4a582",alpha=0.85,edgecolor="white",lw=0.3)
axes[1,0].set(xlabel="log10(events per pixel + 1)",ylabel="Pixel count",title="c  Per-pixel event frequency")
anom=pd.read_csv("data/processed/modis_anomalies.csv",nrows=30000)
vc=[c for c in anom.columns if "ndvi" in c.lower()][0] if any("ndvi" in c.lower() for c in anom.columns) else anom.select_dtypes("number").columns[-1]
v=anom[vc].dropna()
axes[1,1].hist(v,bins=80,color="#b2182b",alpha=0.7,edgecolor="white",lw=0.2)
axes[1,1].axvline(np.percentile(v,10),color="#333",ls="--",lw=1,label="10th pctile")
axes[1,1].set(xlabel=vc,ylabel="Count",title="d  Anomaly distribution (30k sample)")
axes[1,1].legend(fontsize=6)
plt.tight_layout(); fig.savefig(out/"fig2_stress_events.png",dpi=300); plt.close(); print("Fig 2 done")

# ===== Fig 3 =====
lr=pd.read_csv("results/modeling/lag_response_summary.csv"); ft=pd.read_csv("results/modeling/feature_attribution_table.csv")
fig,axes=plt.subplots(1,2,figsize=(7.5,3.5))
ax=axes[0]
for var in ["soil_moisture","vapour_pressure_deficit","2m_temperature","total_precipitation","surface_net_solar_radiation"]:
    sub=lr[lr["variable"]==var].sort_values("lag_days")
    ax.plot(sub["lag_days"],sub["mean_absolute_correlation"],"o-",color=C.get(var,"gray"),label=var.replace("_"," ").capitalize(),ms=4,lw=1.2)
ax.set(xlabel="Lead time (days)",ylabel="|r| with stress label",title="a  Precursor signal decay with lead time")
ax.legend(fontsize=6.5); ax.grid(True,alpha=0.2)
ax=axes[1]; top=ft.nlargest(12,"absolute_correlation")
lbls=[f"{r['variable'].replace('_',' ').capitalize()}  ({r['lag_days']}d)" for _,r in top.iterrows()]
ax.barh(range(12),top["absolute_correlation"].values,color=[C.get(v,"gray") for v in top["variable"]],alpha=0.85,height=0.65)
ax.set(yticks=range(12),yticklabels=lbls,xlabel="|r| with stress label",title="b  Top 12 lagged climate predictors")
ax.tick_params(axis="y",labelsize=6.5); ax.invert_yaxis(); ax.grid(True,alpha=0.2,axis="x")
plt.tight_layout(); fig.savefig(out/"fig3_precursor_discovery.png",dpi=300); plt.close(); print("Fig 3 done")

# ===== Fig 4 =====
pv=pd.read_csv("results/validation/predictive_validation_summary.csv")
bl=pv[pv["evidence_type"]=="baseline_holdout"]; bl=bl[~bl["model"].isin(["majority_class","training_prevalence"])]
models=[("persistence_previous_event","Persistence\n(prev. event)"),
    ("family_threshold:vpd_only","VPD\n(all lags)"),
    ("threshold:vapour_pressure_deficit_anomaly_lag_16d","VPD\n(16-day)"),
    ("threshold:soil_moisture_anomaly_lag_16d","Soil moisture\n(16-day)"),
    ("family_threshold:compound_heat_drought","Compound\nheat+drought"),
    ("family_threshold:temperature_only","Temperature\n(all lags)"),
    ("family_threshold:precipitation_only","Precipitation\n(all lags)")]
fig,ax=plt.subplots(figsize=(7.5,4))
xs,yp,yr=[],[],[]
for m,lbl in models:
    r=bl[bl["model"]==m]
    if len(r)>0: xs.append(lbl); yp.append(r["mean_precision"].values[0]); yr.append(r["mean_recall"].values[0])
x=np.arange(len(xs)); w=0.35
ax.bar(x-w/2,yr,w,label="Recall",color="#2166ac",alpha=0.85)
ax.bar(x+w/2,yp,w,label="Precision",color="#b2182b",alpha=0.85)
for i,(p,r) in enumerate(zip(yp,yr)):
    ax.text(i-w/2,r+0.012,f"{r:.2f}",ha="center",fontsize=6)
    ax.text(i+w/2,p+0.012,f"{p:.2f}",ha="center",fontsize=6)
ax.set(xticks=x,xticklabels=xs,ylabel="Score",ylim=(0,0.82),title="Model performance on temporal holdout (2019–2025)")
ax.tick_params(axis="x",labelsize=6.5); ax.legend(fontsize=7); ax.grid(True,alpha=0.2,axis="y")
plt.tight_layout(); fig.savefig(out/"fig4_model_performance.png",dpi=300); plt.close(); print("Fig 4 done")

# ===== Fig 5 =====
sh=pd.read_csv("results/validation/spatial_holdout_metrics.csv")
sg=sh[sh["heldout_region"].str.startswith("grid_",na=False)]
vpd=sg[sg["model"].str.contains("vapour_pressure_deficit_anomaly_lag_16d")]
smo=sg[sg["model"].str.contains("soil_moisture_anomaly_lag_16d")]
fig,axes=plt.subplots(1,2,figsize=(7.5,3.2))
for ax,df,ttl,clr in [(axes[0],vpd,"a  VPD (16-day lag)","#b2182b"),(axes[1],smo,"b  Soil moisture (16-day lag)","#2166ac")]:
    if len(df)>0:
        ax.scatter(df["precision"],df["recall"],alpha=0.55,c=clr,s=35,edgecolors="white",lw=0.3)
        ax.set(xlabel="Precision",ylabel="Recall",title=ttl); ax.grid(True,alpha=0.2)
        ax.text(0.95,0.05,f"n={len(df)} regions",transform=ax.transAxes,ha="right",fontsize=7,color="#888")
plt.tight_layout(); fig.savefig(out/"fig5_spatial_transfer.png",dpi=300); plt.close(); print("Fig 5 done")

# ===== Fig S1 =====
ts=pd.read_csv("results/validation/threshold_sensitivity.csv")
fig,ax=plt.subplots(figsize=(5,3))
ax.plot(ts["percentile"],ts["event_count"]/1e3,"o-",color="#b2182b",ms=5,lw=1.2,label="Event count")
ax.set(xlabel="Anomaly percentile threshold",ylabel="Events (×10³)",title="Sensitivity of stress-event count to anomaly threshold")
ax.grid(True,alpha=0.2)
ax2=ax.twinx()
ax2.plot(ts["percentile"],ts["units_with_events"],"s--",color="#2166ac",ms=4,lw=1,label="Pixels with events")
ax2.set_ylabel("Pixels with events",color="#2166ac"); ax2.tick_params(axis="y",colors="#2166ac")
h1,l1=ax.get_legend_handles_labels(); h2,l2=ax2.get_legend_handles_labels()
ax.legend(h1+h2,l1+l2,fontsize=7,loc="upper right")
plt.tight_layout(); fig.savefig(out/"figS1_threshold_sensitivity.png",dpi=300); plt.close(); print("Fig S1 done")

print(f"\nAll figures in {out}:")
for f in sorted(out.glob("fig*.png")): print(f"  {f.name}: {f.stat().st_size:>8,} bytes")
