import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import imageio
import os

def generate_eht_animation():
    """
    V11 Visualizer: Generates 'Perturbation.A' animation and static snapshot for PDF.
    """
    print("[INFO] Rendering 'Perturbation.A' Visualization...")
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    RES = 500
    x = np.linspace(-10, 10, RES)
    y = np.linspace(-10, 10, RES)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)
    THETA = np.arctan2(Y, X)
    
    frames = []
    steps = 45
    time_points = np.linspace(0, 2*np.pi, steps)
    R_BASE = 4.0
    
    max_breath = 0
    best_frame_path = f"{output_dir}/fig3_perturbation.png"
    
    for t in time_points:
        # 1. Physics
        intensity_gr = np.exp(-((R - R_BASE)**2) / 1.5)
        doppler = 1 + 0.5 * (X / np.sqrt(X**2 + Y**2 + 0.1))
        img_gr = intensity_gr * doppler
        
        # 2. Vision Theory (Perturbation.A)
        breath = 0.35 * (0.5 * np.sin(t) + 0.5) # Pulsation
        if breath > max_breath:
            max_breath = breath # Track max deformation
        
        bulge_angle = np.pi / 4
        bulge_shape = np.exp(-((THETA - bulge_angle)**2) / 0.6)
        R_dynamic = R_BASE + (R_BASE * breath * bulge_shape)
        
        intensity_ali = np.exp(-((R - R_dynamic)**2) / 1.5)
        img_ali = intensity_ali * doppler
        
        # 3. Plotting
        fig, axes = plt.subplots(1, 2, figsize=(14, 7), facecolor='black')
        
        # Left
        axes[0].imshow(img_gr, cmap='inferno', extent=[-10,10,-10,10], vmin=0, vmax=1.8)
        axes[0].set_title("Standard GR Model\n(Static)", color='white', fontsize=16, pad=20)
        axes[0].axis('off')
        
        # Right
        axes[1].imshow(img_ali, cmap='inferno', extent=[-10,10,-10,10], vmin=0, vmax=1.8)
        axes[1].set_title("Vision Theory Prediction\n(Information Pressure)", color='#00CCFF', fontsize=16, pad=20)
        axes[1].axis('off')
        
        # Reference Contour
        ref_circ = patches.Circle((0, 0), radius=R_BASE, edgecolor='white', facecolor='none', ls='--', lw=1, alpha=0.5)
        axes[1].add_patch(ref_circ)
        
        if breath > 0.05:
            target_x = (R_BASE + 1.5) * np.cos(bulge_angle)
            target_y = (R_BASE + 1.5) * np.sin(bulge_angle)
            
            axes[1].annotate('Perturbation.A', 
                             xy=(target_x, target_y), 
                             xytext=(target_x + 3, target_y + 3),
                             arrowprops=dict(facecolor='#00CCFF', edgecolor='none', arrowstyle='->', lw=2),
                             color='#00CCFF', fontsize=14, fontfamily='sans-serif', weight='bold')

        fig.text(0.5, 0.05, "Simulation Note: Deformation exaggerated 50x for clarity.", 
                 color='gray', fontsize=10, ha='center', style='italic')
        plt.subplots_adjust(top=0.85, bottom=0.1, left=0.05, right=0.95, wspace=0.1)
        
        # Render
        fig.canvas.draw()
        image = np.array(fig.canvas.renderer.buffer_rgba())[:, :, :3]
        frames.append(image)
        
        if breath >= 0.34: 
            plt.savefig(best_frame_path, dpi=300)
            
        plt.close()

    imageio.mimsave(f"{output_dir}/The_Perturbation_A.gif", frames, fps=15)
    print("[SUCCESS] Animation and PDF Snapshot saved.")