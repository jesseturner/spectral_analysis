from modules_cris import cris_utils as c_utils
import matplotlib.pyplot as plt
import numpy as np
import os

#--- Training set
FLC_points = [(40, -67.75), (40.5, -67.80), (40.6,-67.18), (40.47, -66.63), (40.93, -66.79), (40.5, -68.4), (40, -68.8), (40, -69), (40, -69.4), (39.6, -70), (39.3, 70.6), (39.3, 71)]
TLC_points = [(41.99, -67.78), (42.56, 66.77), (42.53, -66.21), (43.02, -66.22), (42.98, -65.63), (42.84, -65.19), (42.91, -64.77), (42.57, -64.79), (42.50, -65.21)]

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

# TLC
wl, Tb_TLC = get_category_Tb(c_utils.open_cris_data, TLC_points, file_path)
n_repeat = 20 // Tb_TLC.shape[0] + 1  # ensure >= 20
Tb_TLC = np.tile(Tb_TLC, (n_repeat, 1))[:20, :]  # shape (20, n_wavelengths)

# FLC
wl, Tb_FLC = get_category_Tb(c_utils.open_cris_data, FLC_points, file_path)
n_repeat = 20 // Tb_FLC.shape[0] + 1
Tb_FLC = np.tile(Tb_FLC, (n_repeat, 1))[:20, :]

print("Tb_TLC shape:", Tb_TLC.shape)
print("Tb_FLC shape:", Tb_FLC.shape)
print("Number of wavelengths:", wl.shape)


from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import LeaveOneOut, cross_val_score
from sklearn.preprocessing import StandardScaler

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

# n_permutations = 1000
# perm_scores = np.zeros(n_permutations)

# for i in range(n_permutations):
#     y_perm = np.random.permutation(y)
#     perm_scores[i] = np.mean(cross_val_score(clf, X_scaled, y_perm, cv=loo))

# p_val = np.mean(perm_scores >= np.mean(scores))
# print(f"Permutation test p-value: {p_val:.3f}")

clf.fit(X_scaled, y)
weights = clf.coef_[0]  # shape (1000,)

plt.figure(figsize=(10,5))
plt.plot(wl, weights, zorder=3, linewidth=1)
plt.axhline(0, color='white', linestyle='--')
plt.xlabel("Wavelength (μm)")
plt.ylabel("Logistic regression weight")
plt.title("Feature weights across wavelength")
plt.savefig(f"plots/fig4_CrIS_linear_regression_L2.png", dpi=200, bbox_inches='tight')
plt.close()