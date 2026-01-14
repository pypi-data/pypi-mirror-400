import numpy as np
import matplotlib.pyplot as plt

def generate_shadow_image(I_Ali_normalized, output_dir="output"):
    print("[INFO] Generating EHT Shadow Simulation...")
    
    RES = 500
    x = np.linspace(-10, 10, RES)
    y = np.linspace(-10, 10, RES)
    X, Y = np.meshgrid(x, y)
    
    R_impact = np.sqrt(X**2 + Y**2)
    
    R_shadow_classic = 5.196
    
    EPSILON = 0.05
    
    perturbation = EPSILON * I_Ali_normalized
    R_shadow_ali = R_shadow_classic * (1 + perturbation)
    
    # --- Image Generation ---
    
    def render_accretion_disk(r_shadow):
        intensity = np.zeros_like(R_impact)
        
        mask_light = R_impact > r_shadow
        
        intensity[mask_light] = 10.0 / (R_impact[mask_light]**2)
        
        ring_width = 0.5
        mask_ring = (R_impact > r_shadow) & (R_impact < r_shadow + ring_width)
        intensity[mask_ring] += 50.0
        
        doppler = 1 + 0.5 * (X / np.sqrt(X**2 + Y**2 + 0.1))
        intensity = intensity * doppler
        
        return intensity

    # Render
    img_classic = render_accretion_disk(R_shadow_classic)
    img_ali = render_accretion_disk(R_shadow_ali)
    
    # --- Visualization ---
    
    plt.style.use('dark_background')
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    ax1 = axes[0]
    ax1.imshow(img_classic, extent=[-10,10,-10,10], cmap='inferno')
    ax1.set_title('Standard GR Prediction')
    ax1.axis('off')
    
    ax2 = axes[1]
    ax2.imshow(img_ali, extent=[-10,10,-10,10], cmap='inferno')
    ax2.set_title(f'Ali Hypothesis (+{perturbation*100:.2f}%)')
    ax2.axis('off')
    
    ax3 = axes[2]
    ax3.set_title('The "Ali Deviation" Signal')
    ax3.axis('off')
    
    ax3.text(0, -8, "Look Here for Quantum Echo", color='cyan', ha='center')
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/fig3_eht_shadow.png", dpi=300)
    plt.close()
    
    print("[SUCCESS] EHT Shadow generated.")