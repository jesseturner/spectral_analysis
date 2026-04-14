from modules_modtran import modtran_utils as m_utils
import matplotlib.pyplot as plt

def main():

    modtran_low_cloud = "data/modtran/modtran_json/04-02_low_cloud.json"
    modtran_inversion = "data/modtran/modtran_json/04-02_inversion.json"
    modtran_clear = "data/modtran/modtran_json/04-02_clear_sky.json"

    wl1, freq1, Tb1 = get_modtran_Tb(modtran_low_cloud)
    wl2, freq2, Tb2 = get_modtran_Tb(modtran_inversion)
    wl3, freq3, Tb3 = get_modtran_Tb(modtran_clear)

    Tb_lines = [
        {"wl": wl1, "freq": freq1, "Tb": Tb1, "label": "Low Cloud", "color": "blue"},
        {"wl": wl2, "freq": freq2, "Tb": Tb2, "label": "Inversion", "color": "red"},
        {"wl": wl3, "freq": freq3, "Tb": Tb3, "label": "Clear Sky", "color": "green"},
    ]
    
    plot_Tb_spectra(Tb_lines)

#------------------------

def get_modtran_Tb(modtran_json_path):
    m_utils.run_modtran(modtran_json_path)
    modtran_df1 = m_utils.open_tp7_file("flc_custom1.tp7")
    modtran_df2 = m_utils.open_7sc_file("flc_custom1.7sc")
    wl, Tb = 10000/modtran_df2['FREQ'], modtran_df2['BBODY_T[K]']
    freq = modtran_df2['FREQ']
    return wl, freq, Tb

def plot_Tb_spectra(Tb_lines):
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_facecolor('black')

    for line in Tb_lines:
        ax.plot(line["freq"], line["Tb"], label=line["label"], color=line["color"], linewidth=1,)
    
    # ax.set_xlim((3,12))
    ax.set_ylim((200,300))

    ax.set_xlabel("Wavenumber (cm$^{-1}$)")
    ax.set_ylabel("Brightness Temperature (K)")
    ax.set_title("MODTRAN IR spectra")
    ax.legend()

    plt.savefig(f"plots/modtran_ir_compare.png", dpi=300, bbox_inches='tight')
    plt.close()

    return 

#------------------------

if __name__ == "__main__":
    main()