# Run and test the regression model 

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from modules_cris import cris_utils as c_utils
from fig_1_cris_modtran_overlay import file_path
from fig_2_testing_set import FLC_points, TLC_points, btd, extent, cmap, norm 
from fig_4_logistic_regression import get_category_Tb_from_ds, clf, scaler

c_utils.set_plots_dark()

def run_logreg_inference(
    ds_func,
    file_path,
    get_category_Tb_from_ds,
    FLC_points,
    TLC_points,
    clf,
    scaler,
    class_names={0: "FLC", 1: "TLC"}
):
    results = []

    # 🔑 OPEN ONCE
    ds = ds_func(file_path)

    for points, true_label in [(TLC_points, 1), (FLC_points, 0)]:
        wl, Tb = get_category_Tb_from_ds(ds, points)

        row_mask = ~np.isnan(Tb).any(axis=1)
        Tb = Tb[row_mask]
        clean_points = [p for p, keep in zip(points, row_mask) if keep]

        Tb_scaled = scaler.transform(Tb)

        y_pred = clf.predict(Tb_scaled)
        y_prob = clf.predict_proba(Tb_scaled)

        for (lat, lon), yp, prob in zip(clean_points, y_pred, y_prob):
            results.append({
                "lat": lat,
                "lon": lon,
                "true_label": class_names[true_label],
                "predicted_label": class_names[yp],
                "P(TLC)": prob[1],
                "P(FLC)": prob[0]
            })

    # Optional but good practice
    try:
        ds.close()
    except Exception:
        pass

    return pd.DataFrame(results)


df_predictions = run_logreg_inference(
    ds_func=c_utils.open_cris_data,
    file_path=file_path,
    get_category_Tb_from_ds=get_category_Tb_from_ds,
    FLC_points=FLC_points,
    TLC_points=TLC_points,
    clf=clf,
    scaler=scaler
)

# Confusion-like summary
print(
    df_predictions
    .groupby(["true_label", "predicted_label"])
    .size()
)

print(df_predictions)

#--- Confusion-style plot
counts = (
    df_predictions
    .groupby(["true_label", "predicted_label"])
    .size()
    .unstack(fill_value=0)
)

counts.plot(kind="bar", figsize=(6,4))
plt.ylabel("Number of points")
plt.xlabel("True label")
plt.title("Logistic regression classification results")
plt.legend(title="Predicted label")
plt.tight_layout()
plt.savefig(f"plots/fig5_confusion_bar.png", dpi=200, bbox_inches='tight')
plt.close()

#--- Probability distributions
plt.figure(figsize=(6,4))

for label, color in [("TLC", "tab:red"), ("FLC", "tab:blue")]:
    subset = df_predictions[df_predictions["true_label"] == label]
    plt.hist(
        subset["P(TLC)"],
        bins=15,
        alpha=0.6,
        label=f"True {label}"
    )

plt.axvline(0.5, color="k", linestyle="--", linewidth=1)
plt.xlabel("Predicted P(TLC)")
plt.ylabel("Count")
plt.title("Classification probability distributions")
plt.legend()
plt.tight_layout()
plt.savefig(f"plots/fig5_probability_distribution.png", dpi=200, bbox_inches='tight')
plt.close()


#--- Location of predictions
import cartopy.crs as ccrs

plot_title = f"Map of regression model results"

projection=ccrs.PlateCarree(central_longitude=0)
fig,ax=plt.subplots(1, figsize=(12,12),subplot_kw={'projection': projection})

pcm = plt.pcolormesh(btd.lon, btd.lat, btd, cmap=cmap, norm=norm, shading="nearest")

sc = plt.scatter(
    df_predictions["lon"],
    df_predictions["lat"],
    c=df_predictions["P(TLC)"],
    cmap="RdYlGn",
    s=80,
    transform=ccrs.PlateCarree(),
    edgecolors="white"
)

cbar = plt.colorbar(sc, fraction=0.045, pad=0.03)
cbar.ax.tick_params(labelsize=14)
cbar.set_label("P(TLC)", fontsize=16)

ax.legend(
    loc='lower left',
    fontsize=12,
    frameon=True,
    facecolor='black',
    edgecolor='white'
)

if extent: ax.set_extent(extent, crs=ccrs.PlateCarree())
ax.set_title(plot_title, fontsize=20, pad=10)
ax.coastlines(resolution='50m', color='white', linewidth=2)

plt.savefig(f"plots/fig5_map_of_results.png", dpi=200, bbox_inches='tight')
plt.close()