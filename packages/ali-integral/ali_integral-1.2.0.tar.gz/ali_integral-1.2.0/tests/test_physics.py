import unittest
from ali_integral.physics import run_simulation

class TestAliIntegral(unittest.TestCase):
    def test_stellar_mass_integral(self):
        results = run_simulation()
        ofi = results["Stellar BH"]["I_Ali"]
        self.assertGreater(ofi, 0, "OFI должно быть больше 0")
        self.assertLess(ofi, 1e50, "OFI не должно быть бесконечным (физический предел)")

    def test_mass_scaling(self):
        results = run_simulation()
        small = results["Stellar BH"]["I_Ali"]
        huge = results["TON 618"]["I_Ali"]
        self.assertGreater(huge, small, "TON 618 должна давать больше данных, чем обычная дыра")

if __name__ == '__main__':
    unittest.main()