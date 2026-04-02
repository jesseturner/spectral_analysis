from modules_modtran import modtran_utils as m_utils
import matplotlib.pyplot as plt

def main():

    modtran_low_cloud = "data/modtran/modtran_json/2025031206_40_67-75.json"
    modtran_inversion = "data/modtran/modtran_json/2025031206_40_67-75.json"
    modtran_clear = "data/modtran/modtran_json/2025031206_40_67-75.json"

    wl1, Tb1 = get_modtran_Tb(modtran_low_cloud)
    wl2, Tb2 = get_modtran_Tb(modtran_inversion)
    wl3, Tb3 = get_modtran_Tb(modtran_clear)

    Tb_lines = [
        {"Tb": Tb1, "label": "Low Cloud", "color": "blue"},
        {"Tb": Tb2, "label": "Inversion", "color": "red"},
        {"Tb": Tb3, "label": "Clear Sky", "color": "green"},
    ]

    plot_Tb_spectra(Tb_lines)

#------------------------

def get_modtran_Tb(modtran_json_path):
    m_utils.run_modtran(modtran_json_path)
    modtran_df1 = m_utils.open_tp7_file("flc_custom1.tp7")
    modtran_df2 = m_utils.open_7sc_file("flc_custom1.7sc")
    wl, Tb = 10000/modtran_df2['FREQ'], modtran_df2['BBODY_T[K]']
    return wl, Tb

def plot_Tb_spectra(Tb_lines):
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_facecolor('black')

    for line in Tb_lines:
        ax.plot(line["data"], label=line["label"], color=line["color"], linewidth=0.5,)
    
    ax.set_xlim((3,12))
    ax.set_ylim((180,300))

    ax.set_xlabel("Wavelength (μm)")
    ax.set_ylabel("Brightness Temperature (K)")
    ax.set_title("MODTRAN IR spectra")
    ax.legend()

    plt.savefig(f"plots/modtran_ir_compare.png", dpi=200, bbox_inches='tight')
    plt.close()

    return 

#------------------------

if __name__ == "__main__":
    main()