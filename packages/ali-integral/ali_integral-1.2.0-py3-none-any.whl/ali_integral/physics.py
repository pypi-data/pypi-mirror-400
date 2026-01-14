import numpy as np
from scipy.integrate import simpson
from .kerr_metric import calculate_horizons, kerr_blueshift_factor
try:
    from ali_integral.config import B0, SNR0, C_LIMIT, F_CRIT, STEPS, T_MELT, T_SPACE
except ImportError:
    B0 = 1.0e9
    SNR0 = 10.0
    C_LIMIT = 1.0e17
    T_SPACE = 2.7
    T_MELT = 3500.0

BLACK_HOLES = {
    "SgrA*": 4.1e6,
    "M87*": 6.5e9,
    "TON618": 6.6e10,
    "CygnusX-1": 14.8,
    "Sun": 1.0
}

HOLES = {
    "Stellar BH": {"M": 10.0, "a": 0.0},
    "Sgr A*":     {"M": 4.0e6, "a": 0.6},
    "TON 618":    {"M": 6.6e10, "a": 0.99}
}

def get_mass(mass_input):
    if isinstance(mass_input, str):
        if mass_input in BLACK_HOLES:
            return BLACK_HOLES[mass_input]
        else:
            raise ValueError(f"Unknown Black Hole. Available: {list(BLACK_HOLES.keys())}")
    return float(mass_input)

def calculate_ali_integral(mass):
    M = float(mass)
    
    # r normalized: 1.0 (Horizon) -> 0 (Singularity)
    r = np.linspace(1.0, 1e-5, STEPS)
    # Proper time tau scales with Mass M
    tau = np.linspace(0, M, STEPS)
    
    g_factor = 1.0 / r
    B_tau = B0 * g_factor
    Flux = 1.0 * (g_factor**2)
    SNR_tau = SNR0 * g_factor
    
    C_in = B_tau * np.log2(1 + SNR_tau)
    
    crash_mask = Flux > F_CRIT
    
    if np.any(crash_mask):
        crash_idx = np.argmax(crash_mask)
    else:
        crash_idx = STEPS - 1
        
    valid_tau = tau[:crash_idx]
    valid_Cin = C_in[:crash_idx]
    
    if len(valid_tau) < 2:
        return 0.0
    
    throughput = np.minimum(valid_Cin, C_LIMIT)
    
    I_Ali = simpson(throughput, x=valid_tau)
    
    return I_Ali

def run_simulation():
    results = {}

    for name, params in HOLES.items():
        M = params["M"]
        a = params["a"]
        
        r_plus, r_minus = calculate_horizons(1.0, a)
        
        r_start = r_plus * 0.99
        
        steps = 5000
        r = np.linspace(r_start, r_minus + 0.0001, steps)
        tau = np.linspace(0, M, steps)
        
        g_factor = kerr_blueshift_factor(r, 1.0, a)
        
        g_factor = np.nan_to_num(g_factor, nan=1.0)
        
        Temperature = T_SPACE * np.sqrt(g_factor) * 100 
        
        B_tau = B0 * g_factor
        SNR_tau = SNR0 * g_factor
        C_in = B_tau * np.log2(1 + SNR_tau)
        
        crash_mask = Temperature > T_MELT
        
        if np.any(crash_mask):
            crash_idx = np.argmax(crash_mask)
        else:
            crash_idx = steps - 1
            
        if crash_idx == 0:
            crash_idx = 1
            
        valid_tau = tau[:crash_idx]
        valid_Cin = C_in[:crash_idx]
        
        throughput = np.minimum(valid_Cin, C_LIMIT)
        
        # Integral Ali
        if len(valid_tau) > 1:
            I_Ali = simpson(throughput, x=valid_tau)
        else:
            I_Ali = 0.0
            
        last_val = valid_tau[-1] if len(valid_tau) > 0 else 0.0

        results[name] = {
            "I_Ali": I_Ali,
            "tau": valid_tau,
            "Cin": valid_Cin,
            "limit": C_LIMIT,
            "crash_val": last_val,
            "temp": Temperature[:crash_idx]
        }
        
    return results