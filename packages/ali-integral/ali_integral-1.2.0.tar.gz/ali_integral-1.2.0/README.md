# The Ali Integral: Observable Future Information 🌌

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18135385.svg)](https://doi.org/10.5281/zenodo.18135385)
[![PyPI version](https://badge.fury.io/py/ali-integral.svg)](https://badge.fury.io/py/ali-integral)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Ali Integral** is a Python library implementing the "Vision Theory" — a framework for calculating the maximum observable information at the Cauchy Horizon of a Kerr Black Hole.

It combines **General Relativity** (gravitational blueshift) with **Information Theory** (Shannon-Hartley theorem & Landauer's limit) to solve the infinite energy paradox.

---

## 🚀 Quick Start

### 1. Installation
Install via pip:
```bash
pip install ali-integral
```

### 2. Usage (The "One-Liner")

You can run a full simulation for famous black holes with a single command:

```python
import ali_integral

# Run simulation for TON 618 (The largest black hole)
ali_integral.run("TON618")
```

### 3. Advanced Usage

You can calculate the integral for any custom mass:

```python
import ali_integral

# Calculate for a black hole with 1000 solar masses
ali_integral.run(1000.0)
```

---

## 📊 Features

 - **Catalog of Presets:** Built-in data for `SgrA*`, `M87*`, `TON618`, `CygnusX-1`.
 - **Physics Engine:** Calculates `g(tau)` (blueshift factor) and dynamic Bitrate.
 - **Crash Detection:** Simulates **Thermal Crash** (when energy flux > structural limit) and Lloyd Limit (computational bound).
 - **Visualization:** Automatically generates plots showing the "Information Horizon".

---

## 🔬 Scientific Background

This library implements the mathematical model described in the paper:
**"The Ali Integral: Observable Future Information" (2026)**.

The core metric ($I_{Ali}$) quantifies the total amount of bits a probe can decode before destruction:

$$ I_{Ali} = \int_{0}^{\tau_{crash}} \min(C_{in}(\tau), C_{Lloyd}) d\tau $$

Where:
*   **$C_{in}(\tau)$**: The incoming Shannon capacity, which grows exponentially due to gravitational blueshift ($g \to \infty$).
*   **$C_{Lloyd}$**: The ultimate physical limit of computation (Landauer's limit), determined by the probe's effective energy.
*   **$\tau_{crash}$**: The moment of Thermal or Structural failure (when Radiation Pressure > Material Strength).

### Observable Signature: "Perturbation.A"
Version 11.0 of the theory predicts a specific deformation of the black hole's photon sphere caused by internal information pressure. This library includes visualization tools to generate the expected EHT signature (Difference Map).

---

## 📄 Citation

If you use this code or the theoretical framework in your research, please cite it using the following BibTeX entry:

```bibtex
@misc{ali2026integral,
  author       = {Ali},
  title        = {The Ali Integral: Observable Future Information},
  year         = {2026},
  publisher    = {Zenodo},
  version      = {10.0},
  doi          = {10.5281/zenodo.18135385},
  url          = {https://doi.org/10.5281/zenodo.18135385}
}
```

---

## 👨‍💻 Author
Ali (Troxter222)

 - Independent Researcher in AI & Theoretical Physics.
 - GitHub: [Troxter222](https://github.com/Troxter222)
 - Research Profile: [Zenodo](https://zenodo.org/search?q=metadata.creators.person_or_org.name%3A%22Sultonov%2C%20Ali%22&l=list&p=1&s=10&sort=bestmatch)

---
*Licensed under the MIT License. Copyright © 2026 Ali.*