"""
Ali Integral Library
"""
from .physics import calculate_ali_integral, get_mass, BLACK_HOLES

def run(target="SgrA*", save=False):
    """Easy run function"""
    try:
        mass = get_mass(target)
        print(f"Target Mass: {mass:.2e}")
        
        result = calculate_ali_integral(mass)
        
        print(f"Ali Integral (OFI): {result:.2e} bits")
        return result
    except Exception as e:
        print(f"Error: {e}")