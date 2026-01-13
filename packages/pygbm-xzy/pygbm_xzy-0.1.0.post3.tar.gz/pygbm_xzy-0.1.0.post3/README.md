# pygbm — Geometric Brownian Motion Simulator

`pygbm` is a lightweight Python package for simulating **Geometric Brownian Motion (GBM)** paths.
It provides both a Python API and a command-line interface, with documentation hosted on Read the Docs.

**Documentation**  
https://geometric-brownian-motion-simulations.readthedocs.io/en/latest/

---

## Installation

### Install from PyPI

Once published on PyPI, the package can be installed directly via:

    pip install pygbm_xzy

---

### Install from Source (Editable Mode)

Alternatively, clone the repository and install the package in editable mode:

    git clone https://github.com/ZZZiyao/Geometric-Brownian-motion-simulations.git
    cd Geometric-Brownian-motion-simulations
    pip install -e .

---

## Description

Geometric Brownian Motion (GBM) is a stochastic process commonly used to model
multiplicative random dynamics. It satisfies the stochastic differential equation:

    dY(t) = μ Y(t) dt + σ Y(t) dB(t)

where μ is the drift coefficient and σ is the diffusion coefficient.

---

## Features

- Object-oriented design with a shared base class
- Simulation of GBM paths using the analytical solution
- Simple Python interface
- Command-line interface
- Automatically generated documentation using Sphinx and Read the Docs

---

## Usage

### Python Interface

    from pygbm.gbm_simulator import GBMSimulator

    simulator = GBMSimulator(y0=1.0, mu=0.05, sigma=0.2)
    t_values, y_values = simulator.simulate_path(T=1.0, N=100)
    simulator.plot_path(t_values, y_values, output="gbm_plot.png")

---

### Command-Line Interface

    pygbm simulate --y0 1.0 --mu 0.05 --sigma 0.2 --T 1.0 --N 100 --output gbm_plot.png

---

## Documentation

Full documentation, including the API reference and an example notebook, is available at:

https://geometric-brownian-motion-simulations.readthedocs.io/en/latest/pygbm

The documentation is automatically built and published using **Read the Docs**.

---

## Contributing

Contributions are welcome.  
Fork the repository and submit a pull request.

---

## License

This project is licensed under the MIT License.
