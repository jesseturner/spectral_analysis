# Run and test the regression model 

import numpy as np
import pandas as pd
import os
from modules_cris import cris_utils as c_utils
from fig_1_cris_modtran_overlay import file_path
from fig_2_testing_set import FLC_points, TLC_points
from fig_4_logistic_regression import get_category_Tb

c_utils.set_plots_dark()

def predict_category(
    ds_func,
    points,
    file_path,
    scaler,
    clf,
    class_names={0: "FLC", 1: "TLC"}
):
    """
    Predict class labels and probabilities for new points.
    """
    wl, Tb = get_category_Tb(ds_func, points, file_path)

    # Remove rows with NaNs (same rule as training)
    row_mask = ~np.isnan(Tb).any(axis=1)
    Tb_clean = Tb[row_mask]
    points_clean = [p for p, keep in zip(points, row_mask) if keep]

    # Scale using TRAINING scaler
    Tb_scaled = scaler.transform(Tb_clean)

    # Predictions
    y_pred = clf.predict(Tb_scaled)
    y_prob = clf.predict_proba(Tb_scaled)[:, 1]  # P(TLC)

    # Package results
    results = []
    for (lat, lon), pred, prob in zip(points_clean, y_pred, y_prob):
        results.append({
            "lat": lat,
            "lon": lon,
            "predicted_label": class_names[pred],
            "P(TLC)": prob,
            "P(FLC)": 1 - prob
        })

    return pd.DataFrame(results)

df_test_preds = predict_category(
    c_utils.open_cris_data,
    test_points,
    file_path,
    scaler,
    clf
)
print(df_test_preds)