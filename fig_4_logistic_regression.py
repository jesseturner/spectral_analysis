#--- Fitting a logistic regression to the training set and plotting the weight by wavelength.

from modules_cris import cris_utils as c_utils
import matplotlib.pyplot as plt
import numpy as np
import os
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import LeaveOneOut, cross_val_score
from sklearn.preprocessing import StandardScaler
from fig_2_training_testing_set import FLC_points, TLC_points

cris_dir = "data/cris/"
cris_file = "SNDR.J1.CRIS.20250312T0642.m06.g068.L1B.std.v03_08.G.250312132403.nc"
file_path = os.path.join(cris_dir, cris_file)
c_utils.set_plots_dark()

#--- Logistic regression (L2 regularization)

def get_category_Tb(ds_func, points, file_path):
    ds = ds_func(file_path)  # open once
    all_Tb = []

    for lat, lon in points:
        ds_point = c_utils.isolate_target_point(ds, target_lat=lat, target_lon=lon)
        df_cris = c_utils.get_brightness_temperature(ds_point)
        Tb = df_cris["Brightness Temperature (K)"].values
        all_Tb.append(Tb)

    Tb_all = np.array(all_Tb)
    wl = df_cris["Wavelength (um)"].values

    return wl, Tb_all

wl, Tb_TLC = get_category_Tb(c_utils.open_cris_data, TLC_points, file_path)
wl, Tb_FLC = get_category_Tb(c_utils.open_cris_data, FLC_points, file_path)

print("Tb_TLC shape:", Tb_TLC.shape)
print("Tb_FLC shape:", Tb_FLC.shape)
print("Number of wavelengths:", wl.shape)


X = np.vstack([Tb_TLC, Tb_FLC])  # shape: (20, 1000)
y = np.array([1]*Tb_TLC.shape[0] + [0]*Tb_FLC.shape[0]) 

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

plt.figure(figsize=(10,5))
plt.plot(wl, weights, zorder=3, linewidth=1)
plt.axhline(0, color='white', linestyle='--')
plt.xlabel("Wavelength (μm)")
plt.ylabel("Logistic regression weight")
plt.title("Feature weights across wavelength")
plt.savefig(f"plots/fig4_CrIS_logistic_regression_L2.png", dpi=200, bbox_inches='tight')
plt.close()