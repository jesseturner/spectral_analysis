# Creating modtran training and testing sets for:
# 1. true low clouds (TLC, cloud layer and no inversion)
# 2. true low clouds with inversion (TLC_i, cloud layer and inversion)
# 3. false low clouds (FLC, clear sky and inversion)

import json
import os
import random
import numpy as np

# Output directory
output_dir = "data/modtran/fig_6_modtran_sets"
os.makedirs(output_dir, exist_ok=True)

# Base pressure levels (same as your example)
pressure_levels = [
    1020.0, 1010.0, 1000.0, 975.0, 950.0, 925.0, 900.0, 850.0, 800.0, 750.0,
    700.0, 650.0, 600.0, 550.0, 500.0, 450.0, 400.0, 350.0, 300.0, 250.0,
    200.0, 150.0, 100.0, 70.0, 50.0, 40.0, 30.0, 20.0, 15.0, 10.0, 7.0, 5.0,
    3.0, 2.0, 1.0
]

n_layers = len(pressure_levels)

# Base temperature and moisture profiles for simplicity
def base_temperature(category):
    """Return a base temperature profile (Kelvin) based on category."""
    t = np.linspace(288, 220, n_layers)  # general lapse rate
    if category == "TLC_i":  # inversion near surface
        t[0:3] += 5  # temperature increases slightly near surface
    elif category == "FLC":  # inversion
        t[0:5] += 5
    # TLC is normal lapse rate
    return t

def base_moisture(category):
    """Return a base moisture profile (H2O in ppmv)."""
    h2o = np.linspace(8000, 5, n_layers)  # decreasing with altitude
    if category == "TLC_i" or category == "TLC":
        h2o[7:10] += 2000  # moisture bump for cloud layer
    # FLC has no cloud
    return h2o

# Cloud layer per category
def cloud_setting(category):
    if category in ["TLC_i", "TLC"]:
        return "CLOUD_STRATUS"
    else:
        return "NO_CLOUD"
    
# Cloud layer per category
def aerosol_setting(category):
    if category in ["TLC_i", "TLC"]:
        return {
            "IHAZE": "AER_MARITIME",
            "ICLD": "CLOUD_STRATUS",
            "VIS": 1.0,
            "CALT": 0.5
        }
    else:  # FLC
        return {
            "IHAZE": "AER_MARITIME",
            "VIS": 0.0
        }

# Generate a single JSON
def generate_json(category, idx):
    name = f"{category.lower()}_{idx+1}"
    temp_profile = base_temperature(category) + np.random.normal(0, 1, n_layers)
    h2o_profile = base_moisture(category) + np.random.normal(0, 50, n_layers)
    
    data = {
        "MODTRAN": [
            {
                "MODTRANINPUT": {
                    "NAME": name,
                    "DESCRIPTION": "",
                    "CASE": 0,
                    "RTOPTIONS": {
                        "MODTRN": "RT_MODTRAN",
                        "LYMOLC": False,
                        "T_BEST": False,
                        "IEMSCT": "RT_THERMAL_ONLY",
                        "IMULT": "RT_NO_MULTIPLE_SCATTER"
                    },
                    "ATMOSPHERE": {
                        "MODEL": "ATM_USER_PRESS_PROFILE",
                        "MDEF": 1,
                        "CO2MX": 0.0,
                        "HMODEL": "New Atm Profile",
                        "NPROF": 3,
                        "NLAYERS": n_layers,
                        "PROFILES": [
                            {"TYPE": "PROF_PRESSURE", "UNITS": "UNT_PMILLIBAR", "PROFILE": pressure_levels},
                            {"TYPE": "PROF_TEMPERATURE", "UNITS": "UNT_TKELVIN", "PROFILE": temp_profile.tolist()},
                            {"TYPE": "PROF_H2O", "UNITS": "UNT_DPPMV", "PROFILE": h2o_profile.tolist()}
                        ]
                    },
                    "AEROSOLS": aerosol_setting(category),
                    "GEOMETRY": {},
                    "SURFACE": {"SURFTYPE": "REFL_CONSTANT", "NSURF": 1, "SALBFL": ""},
                    "SPECTRAL": {"V1": 650.0, "V2": 3125.0, "DV": 0.3125, "FWHM": 0.625, "LBMNAM": "T", "BMNAME": "p1_2013"},
                    "FILEOPTIONS": {}
                }
            }
        ]
    }

    # Write JSON file
    filepath = os.path.join(output_dir, f"{name}.json")
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

# Main loop: generate 30 files per category
categories = ["TLC_i", "TLC", "FLC"]
for cat in categories:
    for i in range(30):
        generate_json(cat, i)

print("JSON files generated successfully!")

