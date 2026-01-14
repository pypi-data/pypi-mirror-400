import numpy as np

def calculate_horizons(M, a_spin):
    # r = M +/- sqrt(M^2 - a^2)
    
    if a_spin >= 1.0: 
        a_spin = 0.9999
        
    term = np.sqrt(1.0 - a_spin**2)
    r_plus = 1.0 + term
    r_minus = 1.0 - term
    
    return r_plus, r_minus

def kerr_blueshift_factor(r, M, a_spin):
    """
    g ~ 1 / sqrt(Delta)
    Delta = r^2 - 2Mr + a^2
    """
    
    Delta = r**2 - 2.0*r + a_spin**2
    
    Delta = np.maximum(np.abs(Delta), 1e-9) 
    
    g_factor = 1.0 / np.sqrt(Delta)
    
    return g_factor

if __name__ == "__main__":
    M = 1.0
    a = 0.9
    rp, rm = calculate_horizons(M, a)

    print(f"Mass: {M}, Spin: {a}")
    print(f"Outer Horizon (Blackness): {rp:.4f} M")
    print(f"Inner Horizon (Blue Sheet): {rm:.4f} M")
    
    r_test = rm + 0.001
    g = kerr_blueshift_factor(r_test, M, a)
    print(f"G-factor near inner horizon: {g:.2f}")