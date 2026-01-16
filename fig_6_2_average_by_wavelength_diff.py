import os
import numpy as np
import matplotlib.pyplot as plt
from modules_modtran import modtran_utils as m_utils
from modules_cris import cris_utils as c_utils

c_utils.set_plots_dark()

# Directories where JSON files were saved
json_dir = "data/modtran/fig_6_modtran_sets"

# Collect JSON files for each category
TLC_i_json_list = sorted([os.path.join(json_dir, f) for f in os.listdir(json_dir) if f.startswith("tlc_i") and f.endswith(".json")])
TLC_json_list   = sorted([os.path.join(json_dir, f) for f in os.listdir(json_dir) if f.startswith("tlc_") and not f.startswith("tlc_i") and f.endswith(".json")])
FLC_json_list   = sorted([os.path.join(json_dir, f) for f in os.listdir(json_dir) if f.startswith("flc_") and f.endswith(".json")])

def average_spectra(json_list, category_name, overwrite=False):
    """
    Computes the average spectrum for a list of JSON files.
    Saves/loads the average to/from a .npz file for reuse.
    
    Parameters:
        json_list : list of str
            Paths to JSON files for this category.
        category_name : str
            Name of the category (used for saved filename).
        overwrite : bool
            If True, recompute averages even if saved file exists.
    """
    avg_file = f"avg_{category_name}.npz"

    # Load saved average if it exists and overwrite is False
    if os.path.exists(avg_file) and not overwrite:
        data = np.load(avg_file)
        wavelength_um = data["wavelength"]
        avg_spectrum = data["spectrum"]
        print(f"Loaded saved average for {category_name} from {avg_file}")
        return wavelength_um, avg_spectrum

    # --- Otherwise, compute the average ---
    spectra_list = []
    
    for json_path in json_list:
        # Run MODTRAN on this JSON
        m_utils.run_modtran(json_path)
        
        # Base name of the generated files
        base_name = os.path.splitext(os.path.basename(json_path))[0]
        sc_file = f"{base_name}.7sc"
        
        # Open the .7sc file
        df = m_utils.open_7sc_file(sc_file)
        spectra_list.append(df['BBODY_T[K]'].values)

        # Delete all generated files for this base_name
        for f in os.listdir("."):
            if f.startswith(base_name):
                try:
                    os.remove(f)
                except Exception as e:
                    print(f"Warning: Could not delete file {f}: {e}")

    # Compute average
    avg_spectrum = np.mean(spectra_list, axis=0)
    wavelength_um = 10000 / df['FREQ'].values

    # Save average for future runs
    np.savez(avg_file, wavelength=wavelength_um, spectrum=avg_spectrum)
    print(f"Saved average for {category_name} to {avg_file}")

    return wavelength_um, avg_spectrum



# Compute averages for each category
x_TLC_i, y_TLC_i = average_spectra(TLC_i_json_list, "TLC_i")
x_TLC,   y_TLC   = average_spectra(TLC_json_list, "TLC")
x_FLC,   y_FLC   = average_spectra(FLC_json_list, "FLC")

# Plotting
fig, ax = plt.subplots(figsize=(10, 5))
ax.set_facecolor('black')

linewidth = 0.5
xlim = (3, 12)  # example limits in μm
ylim = (200, 300)
fig_title = "Average MODTRAN Spectra"

# Plot average spectra
ax.plot(x_TLC_i, y_TLC_i, color="#1E90FF", linewidth=linewidth, label="TLC_i")
ax.plot(x_TLC, y_TLC, color="#FF4500", linewidth=linewidth, label="TLC")
ax.plot(x_FLC, y_FLC, color="#00FA9A", linewidth=linewidth, label="FLC")

ax.set_xlim(xlim)
ax.set_ylim(ylim)
ax.set_xlabel("Wavelength (μm)")
ax.set_ylabel("Brightness Temperature (K)")
ax.set_title(fig_title)
ax.legend()

plt.tight_layout()
os.makedirs("plots", exist_ok=True)
plt.savefig("plots/fig_6_avg_modtran.png", dpi=200, bbox_inches='tight')
plt.close()

# --- Difference between FLC and TLC ---
fig, ax = plt.subplots(figsize=(10, 5))
ax.set_facecolor('black')

plt.axhline(y=0, color="blue", linestyle="-", linewidth=1, zorder=0)
ax.plot(x_FLC, 
        y_TLC - y_FLC, 
        color="white", 
        linewidth=linewidth, 
        label="True Low Cloud - False Low Cloud", 
        zorder=3)
ax.set_ylim((-18,18))
plt.xlabel("Wavelength (μm)")
plt.ylabel("Brightness Temperature Difference (K)")
plt.title("Average IR Spectra to Distinguish Low Clouds in MODTRAN")
ax.legend()

plt.tight_layout()
plt.savefig("plots/fig_6_modtran_diff.png", dpi=200, bbox_inches='tight')
plt.close()
