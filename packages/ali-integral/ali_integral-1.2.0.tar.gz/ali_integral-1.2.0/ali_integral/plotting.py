import matplotlib.pyplot as plt
import os
import numpy as np

OUTPUT_DIR = "output"

def generate_plots(results):
    print("[INFO] Generating Plots (V12 Thermodynamics)...")
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    data = results["TON 618"]
    
    plt.style.use('grayscale')
    fig, ax = plt.subplots(figsize=(8, 4.5))
    
    ax.plot(data["tau"], data["Cin"], 'k-', lw=1.5, label=r'Input Capacity $C_{in}(\tau)$')
    ax.axhline(data["limit"], color='red', linestyle='--', lw=1.5, label=r'Lloyd Limit ($C_{limit}$)')
    
    ax.fill_between(data["tau"], data["limit"], 0, where=(data["Cin"] > data["limit"]), 
                    color='gray', alpha=0.3, label='Processed Information (OFI)')
    ax.fill_between(data["tau"], data["Cin"], 0, where=(data["Cin"] <= data["limit"]), 
                    color='gray', alpha=0.3)
    
    ax.set_yscale('log')
    ax.set_title(r'Fig 1: Information Horizon (TON 618)')
    ax.set_xlabel('Proper Time (Normalized)')
    ax.set_ylabel('Bitrate (bits/s)')
    ax.legend(loc='upper left')
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/fig1_capacity.png", dpi=300)
    plt.close()

    names = list(results.keys())
    ofis = [results[n]["I_Ali"] for n in names]
    base_ofi = ofis[0] if ofis[0] > 0 else 1.0
    norm_ofis = [x/base_ofi for x in ofis]
    
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar(names, norm_ofis, color='#444444', edgecolor='black')
    
    ax.set_yscale('log')
    ax.set_ylabel(r'Relative OFI ($I_{Ali}$)')
    ax.set_title('Fig 2: Scaling of Observable Information')
    
    for bar, val in zip(bars, norm_ofis):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height*1.1, f'x{val:.1e}', ha='center', fontsize=10)
        
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/fig2_scaling.png", dpi=300)
    plt.close()
    
    fig, ax = plt.subplots(figsize=(8, 4.5))
    
    # TON 618
    t_ton = results["TON 618"]["tau"]
    temp_ton = results["TON 618"]["temp"]
    t_ton_norm = np.linspace(0, 1, len(t_ton))
    
    # Stellar
    t_st = results["Stellar BH"]["tau"]
    temp_st = results["Stellar BH"]["temp"]
    t_st_norm = np.linspace(0, 1, len(t_st))
    
    ax.plot(t_ton_norm, temp_ton, 'k-', lw=2, label='TON 618 (a=0.99)')
    ax.plot(t_st_norm, temp_st, 'k:', lw=1.5, label='Stellar BH (a=0.0)')
    
    T_MELT = 3500.0
    ax.axhline(T_MELT, color='red', ls='--', label='Melting Point (3500 K)')
    
    ax.set_yscale('log')
    ax.set_title(r'Fig 3: Probe Heating (Thermal Crash Analysis)')
    ax.set_xlabel('Journey Progress (0% to Crash)')
    ax.set_ylabel('Probe Temperature (K)')
    ax.legend()
    ax.grid(True, which="both", ls="--", alpha=0.2)
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/fig3_thermal.png", dpi=300)
    plt.close()
    
    _render_eq(r"$T_{probe} \approx 2.7K \cdot \sqrt{g(\tau)}$", "eq_temp.png")

def _render_eq(latex, filename):
    plt.figure(figsize=(6, 1.5))
    plt.text(0.5, 0.5, latex, ha='center', fontsize=18)
    plt.axis('off')
    plt.savefig(f"{OUTPUT_DIR}/{filename}", dpi=300, bbox_inches='tight')
    plt.close()