# Geoloop: A BHE Calculator for Python

[![PyPI](https://img.shields.io/pypi/v/geoloop.svg)](https://pypi.org/project/geoloop/)
[![Documentation](https://img.shields.io/badge/docs-latest-blue)](https://geoloop-8f7a36.ci.tno.nl/)

## What is **Geoloop**?

**Geoloop** is a Python package for simulating vertical borehole heat exchanger (BHE) systems,
with a focus on the impact of depth-dependent thermal properties and geothermal gradient and their impact on system performance.

**Geoloop** incorporates (uncertainty in) depth-variations in subsurface thermal conductivity, subsurface temperature, 
BHE design and diverse operational boundary conditions such as seasonal load variations or 
minimum fluid temperatures. It allows for deterministic or stochastic performance analyses with the opportunity
for optimization of the system design and operation. This makes Geoloop well suited for scenario analyses and sensitivity 
studies in both research and practical applications.

**Geoloop**  provides a novel depth-dependent approach for thermal response calculations. 
A detailed description and benchmark of this depth-dependent semi-analytical method is provided in Korevaar et al. (2026).
**Geoloop** uses the *pygfunction* package, developed by Cimmino & Cook (2022), including its implementation
of *g*-functions, time aggregation schemes for varying loads, borehole and fluid thermal properties, and various visualization capabilities

**Geoloop's** generic framework allows for easy switching between simulation methods, including the 
depth-dependent model, the depth-uniform implementation of g-functions as implemented in *pygfunction* and a numerical 
finite volume approach.

---

## Installation

Install from PyPI using:

```bash
pip install geoloop
```

For detailed setup instructions (including uv-based environments and development setup),
see the [Installation Guide](https://geoloop-8f7a36.ci.tno.nl/installation/install/).

---

## Requirements

Geoloop requires **Python 3.12 or higher**.

Core dependencies include:
- pygfunction
- matplotlib
- numpy
- scipy
- h5py
- xarray
- pandas
- seaborn
- tqdm
- netCDF4
- SecondaryCoolantProps
- openpyxl
- h5netcdf
- pathlib
- pydantic
- typer

---

## Quick Start

Explore the [Examples](docs/examples/) folder to get started quickly with Geoloop.

Read the full documenation [here](https://geoloop-8f7a36.ci.tno.nl/).

---

## License

This project is licensed under the Apache 2.0 License.  
See the [LICENSE.md](LICENSE.md) file for details.

---

## Acknowledgments

Developed with the support of the Dutch funding agency **RVO**, in a consortium project with grant nr. MOOI322009.

---


## References

- Cimmino, M. and Cook, J.: pygfunction 2.2: New features and improvements in accuracy and computational efficiency, 
        in: Proceedings of the IGSHPA Research Track 2022, International Ground Source Heat Pump Association, 
        https://doi.org/10.22488/okstate.22.000015, 2022. 
- Korevaar, Z., Brett, H., Van Wees, J.D.: Geoloop (v1.0) – a stochastic, depth-dependent borehole heat exchanger model, Geoscientific Model Development (in prep), 2026
