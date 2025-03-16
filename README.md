<p align="center">
    <img src="https://raw.githubusercontent.com/uwplasma/ESSOS/refs/heads/main/docs/ESSOS_logo.png" align="center" width="30%">
</p>
<p align="center">
    <em><code>❯ ESSOS: e-Stellarator Simulation and Optimization Suite</code></em>
</p>
<p align="center">
    <img src="https://img.shields.io/github/license/uwplasma/ESSOS?style=default&logo=opensourceinitiative&logoColor=white&color=0080ff" alt="license">
    <img src="https://img.shields.io/github/last-commit/uwplasma/ESSOS?style=default&logo=git&logoColor=white&color=0080ff" alt="last-commit">
    <img src="https://img.shields.io/github/languages/top/uwplasma/ESSOS?style=default&color=0080ff" alt="repo-top-language">
    <a href="https://github.com/uwplasma/ESSOS/actions/workflows/build_test.yml">
        <img src="https://github.com/uwplasma/ESSOS/actions/workflows/build_test.yml/badge.svg" alt="Build Status">
    </a>
    <a href="https://codecov.io/gh/uwplasma/ESSOS">
        <img src="https://codecov.io/gh/uwplasma/ESSOS/branch/main/graph/badge.svg" alt="Coverage">
    </a>
    <a href="https://essos.readthedocs.io/en/latest/?badge=latest">
        <img src="https://readthedocs.org/projects/essos/badge/?version=latest" alt="Documentation Status">
    </a>
</p>

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
    - [From PyPI](#from-pypi)
    - [From Source](#from-source)
- [Usage](#usage)
- [Testing](#testing)
- [Project Roadmap](#project-roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Overview
ESSOS is an open-source project in Python that uses JAX to optimize stellarator coils. Optimization can be applied to several objectives, such as alpha particle confinement, plasma boundaries and magnetic field equilibria (including near-axis expansions). It leverages automatic differentiation and efficient numerical methods to streamline optimization efforts, creating a specialized and fast numerical tool for optimizing force-free stellarator equilibria. It is parallelized using JAX's sharding tools. It can be imported in a Python script using the **essos** package, or run directly in the command line as `essos`. To install it, use

   ```sh
   pip install essos
   ```

Alternatively, you can download it and run the example scripts in the repository after downloading it as

   ```sh
   git clone https://github.com/uwplasma/ESSOS
   cd ESSOS
   pip install .
   python examples/trace_particles_from_coils.py
   ```

The project can be downloaded in its [GitHub repository](https://github.com/uwplasma/ESSOS).

## Features
- **JAX Integration**: Utilizes JAX for automatic differentiation and efficient numerical computations.
- **Optimization**: Implements optimization routines for stellarator coil design.
- **Particle Tracing**: Traces alpha particles in magnetic fields generated by coils.
- **Fieldline Tracing**: Traces magnetic field lines.
- **Coils and Near-Axis Fields**: Models and optimizes electromagnetic coils and near-axis magnetic fields.

## Project Structure
```
ESSOS/
├── essos/
│   ├── __init__.py
│   ├── __main__.py
│   ├── coils.py
│   ├── constants.py
│   ├── dynamics.py
│   ├── fields.py
│   ├── objective_functions.py
│   ├── optimization.py
│   ├── plot.py
│   └── surfaces.py
├── examples/
│   ├── create_stellarator_coils.py
│   ├── optimize_coils_and_nearaxis.py
│   ├── optimize_coils_for_nearaxis.py
│   ├── optimize_coils_particle_confinement_fullorbit.py
│   ├── optimize_coils_particle_confinement_guidingcenter.py
│   ├── optimize_coils_vmec_surface.py
│   ├── trace_fieldlines_coils.py
│   ├── trace_particles_coils_fullorbit.py
│   ├── trace_particles_coils_guidingcenter.py
│   ├── trace_particles_vmec.py
│   └── comparisons_SIMSOPT/
│   └── inputs/
│       ├── ESSOS_bio_savart_LandremanPaulQA.json
│       ├── SIMSOPT_bio_savart_LandremanPaulQA.json
│       ├── wout_n3are_R7.75B5.7.nc
│       └── wout_LandremanPaul2021_QA_reactorScale_lowres_reference.nc
├── tests/
│   ├── test_coils.py
│   ├── test_constants.py
│   ├── test_dynamics.py
│   ├── test_fields.py
├── README.md
├── LICENSE.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── setup.py
├── pyproject.toml
└── requirements.txt
```

## Getting Started

### Prerequisites
- Python 3.8 or higher

### Installation

#### From PyPI
To install ESSOS from PyPI, run:
```sh
pip install essos
```

#### From Source
To install ESSOS from source, clone the repository and install the package:
```sh
git clone https://github.com/uwplasma/ESSOS
cd ESSOS
pip install .
```

## Usage
ESSOS can be run directly in the command line as `essos`, or by following one of the examples in the `examples` folder. For example, to trace particles in a magnetic field generated from coils, run:
```sh
python examples/trace_particles_coils_guidingcenter.py
```

## Testing
To run the tests, use `pytest`:
```sh
pytest .
```

## Project Roadmap
- [ ] Allow several optimization algorithms
- [ ] Allow plotly and/or Mayavi visualization
- [ ] Add DESC and SPEC equilibria for tracing
- [ ] Add beam injection examples
- [ ] Add plotting for near-axis expansion
- [ ] Add particle collisions

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.

- **💬 [Join the Discussions](https://github.com/uwplasma/ESSOS/discussions)**: Share your insights, provide feedback, or ask questions.
- **🐛 [Report Issues](https://github.com/uwplasma/ESSOS/issues)**: Submit bugs found or log feature requests for the `ESSOS` project.
- **💡 [Submit Pull Requests](https://github.com/uwplasma/ESSOS/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your github account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone https://github.com/uwplasma/ESSOS
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to github**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

<details closed>
<summary>Contributor Graph</summary>
<br>
<p align="left">
   <a href="https://github.com{/uwplasma/ESSOS/}graphs/contributors">
      <img src="https://contrib.rocks/image?repo=uwplasma/ESSOS">
   </a>
</p>
</details>

---

##  License

This project is protected under the MIT License. For more details, refer to the [LICENSE](LICENSE) file.

---

##  Acknowledgments

- This project was developed as part of the New Talents in Physics Fellowship, awarded by the [Calouste Gulbenkian Foundation](https://gulbenkian.pt/en/).
- We acknowledge the help of the whole [UWPlasma](https://rogerio.physics.wisc.edu/) plasma group.

---

