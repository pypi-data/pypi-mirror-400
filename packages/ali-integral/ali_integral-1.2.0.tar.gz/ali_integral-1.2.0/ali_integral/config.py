# Configuration and Physical Constants

# --- Simulation Settings ---
STEPS = 5000            # Precision of the integration
R_START = 1.0           # Horizon (2M normalized)
R_END = 1e-5            # Singularity approach

# --- Physical Parameters ---
B0 = 1.0e9              # Base Detector Bandwidth (Hz)
SNR0 = 10.0             # Initial Signal-to-Noise Ratio
C_LIMIT = 1.0e17        # Lloyd Limit (bits/s) - Derived from Processor Energy
T_SPACE = 2.7   
T_MELT = 3500.0
F_CRIT = 1.0e14         # Critical Flux Threshold (W/m^2) - Thermal Crash

# --- Black Hole Masses (in Solar Masses) ---
HOLES = {
    "Stellar BH": 10.0,
    "Sgr A*": 4.0e6,
    "TON 618": 6.6e10
}