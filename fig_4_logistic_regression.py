# Fitting a logistic regression to the training set and plotting the weight by wavelength.

from modules_cris import cris_utils as c_utils
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import LeaveOneOut, cross_val_score
from sklearn.preprocessing import StandardScaler
from fig_1_cris_modtran_overlay import file_path
from fig_2_training_set import training_df

c_utils.set_plots_dark()

# Ensure labels are consistent (optional but recommended)
training_df["label"] = training_df["label"].str.strip()

# TLC points
TLC_points = (
    training_df
    .loc[training_df["label"] == "TLC", ["lat", "lon"]]
    .to_numpy()
)

# Non-low cloud (NLC) points: anything that is NOT TLC and NOT mixed
NLC_points = (
    training_df
    .loc[~training_df["label"].isin(["TLC", "mixed"]), ["lat", "lon"]]
    .to_numpy()
)

print("Number of low cloud points:", len(TLC_points))
print("Number of non-low cloud points:", len(NLC_points))


#--- Logistic regression (L2 regularization)

def get_category_Tb_from_ds(ds, points):
    all_Tb = []

    for lat, lon in points:
        ds_point = c_utils.isolate_target_point(
            ds, target_lat=lat, target_lon=lon
        )
        df_cris = c_utils.get_brightness_temperature(ds_point)
        all_Tb.append(df_cris["Brightness Temperature (K)"].values)

    Tb_all = np.array(all_Tb)
    wl = df_cris["Wavelength (um)"].values

    return wl, Tb_all

ds = c_utils.open_cris_data(file_path)
wl, Tb_TLC = get_category_Tb_from_ds(ds, TLC_points)
wl, Tb_NLC = get_category_Tb_from_ds(ds, NLC_points)

print("Tb_TLC shape:", Tb_TLC.shape)
print("Tb_NLC shape:", Tb_NLC.shape)
print("Number of wavelengths:", wl.shape)


X = np.vstack([Tb_TLC, Tb_NLC])  # shape: (20, 1000)
y = np.array([1]*Tb_TLC.shape[0] + [0]*Tb_NLC.shape[0]) 

row_mask = ~np.isnan(X).any(axis=1)
X = X[row_mask, :]
y = y[row_mask]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# L2 regularization (default), strong enough to handle p >> n
clf = LogisticRegression(
    solver='liblinear',  # fine for small datasets
    C=1.0,               # inverse regularization strength
    l1_ratio=0,          # l1_ratio=0 → pure L2
    max_iter=1000
)

loo = LeaveOneOut()
scores = cross_val_score(clf, X_scaled, y, cv=loo)

print(f"LOO CV Accuracy: {np.mean(scores)*100:.1f}%")

clf.fit(X_scaled, y)
weights = clf.coef_[0]  # shape (1000,)
#--- Only CrIS regions
mask = (
    ((wl >= 3.92) & (wl <= 4.64)) |
    ((wl >= 5.71) & (wl <= 8.26)) |
    ((wl >= 9.13) & (wl <= 15.4))
)
y_plot = np.where(mask, weights, np.nan)

plt.figure(figsize=(10,5))
plt.plot(wl, y_plot, zorder=3, linewidth=1)
plt.axhline(0, color='white', linestyle='--')
plt.xlabel("Wavelength (μm)", fontsize=15)
plt.ylabel("Logistic Regression Coefficient", fontsize=15)
plt.title("Logistic Regression Feature Weights from CrIS Spectra", fontsize=18)
plt.savefig(f"plots/fig4_CrIS_logistic_regression_L2.png", dpi=200, bbox_inches='tight')
plt.close()