import numpy as np
import imageio
import os

def generate_starfield(width, height, num_stars=2000):
    stars_x = np.random.randint(0, width, num_stars)
    stars_y = np.random.randint(0, height, num_stars)
    brightness = np.random.uniform(0.5, 1.0, num_stars)
    
    universe = np.zeros((height, width, 3))
    
    for x, y, b in zip(stars_x, stars_y, brightness):
        if 0 <= x < width and 0 <= y < height:
            universe[y, x] = [b, b, b*0.9]
            
    return universe

def apply_lensing(universe, r_observer, M=1.0):
    h, w, _ = universe.shape
    y_grid, x_grid = np.mgrid[0:h, 0:w]
    
    cx, cy = w / 2, h / 2
    
    radius_px = np.sqrt((x_grid - cx)**2 + (y_grid - cy)**2)
    
    scale_factor = 500.0 / r_observer
    shadow_radius = 2.6 * scale_factor
    
    # --- EINSTEIN RING ---
    distortion = 1.0 - (shadow_radius / (radius_px + 1e-5))
    
    mask_shadow = radius_px < shadow_radius
    
    src_x = cx + (x_grid - cx) / (distortion + 1e-5)
    src_y = cy + (y_grid - cy) / (distortion + 1e-5)
    
    src_x = src_x % w
    src_y = src_y % h
    
    src_x = src_x.astype(int)
    src_y = src_y.astype(int)
    
    rendered_view = universe[src_y, src_x]
    
    # Fraw black hole
    rendered_view[mask_shadow] = [0, 0, 0]
    
    return rendered_view, shadow_radius

def apply_blueshift(image, r_observer, M=1.0):
    # g ~ 1 / sqrt(1 - 2M/r)
    if r_observer <= 2.1 * M:
        intensity = 100.0
    else:
        intensity = 1.0 / np.sqrt(1.0 - 2.0*M/r_observer)
    
    bright_image = image * intensity
    
    # 2. Blue Sheet
    # [R, G, B]
    shift_vector = [1.0/intensity, 1.0, intensity] 
    
    final_image = bright_image * shift_vector
    
    final_image = np.clip(final_image, 0, 1)
    
    return final_image, intensity

def create_animation():
    print("[INFO] Rendering 'Eyes of the Doomed' Simulation...")
    output_dir = "output/animation"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    width, height = 640, 360
    universe = generate_starfield(width, height)
    
    frames = []
    
    distances = np.linspace(15, 2.05, 60) # 60 frames
    
    for i, r in enumerate(distances):
        view, shadow_r = apply_lensing(universe, r)
        
        # 2. Energy (Vision)
        view, intensity = apply_blueshift(view, r)
        
        # Convert into uint8 for photos
        img_uint8 = (view * 255).astype(np.uint8)
        
        # save frames
        filename = f"{output_dir}/frame_{i:03d}.png"
        imageio.imwrite(filename, img_uint8)
        frames.append(img_uint8)
        
        # progress bar in bash
        if i % 10 == 0:
            print(f"Rendering frame {i}/60 | r = {r:.2f}M | Energy = x{intensity:.1f}")

    # --- SYSTEM CRASH ---
    white_screen = np.ones((height, width, 3), dtype=np.uint8) * 255
    for _ in range(5):
        frames.append(white_screen)
    
    black_screen = np.zeros((height, width, 3), dtype=np.uint8)
    for _ in range(10):
        frames.append(black_screen)

    # Save GIF
    gif_path = "output/Vision_Theory_Simulation.gif"
    imageio.mimsave(gif_path, frames, fps=15)
    print(f"[SUCCESS] Animation saved: {gif_path}")

if __name__ == "__main__":
    create_animation()