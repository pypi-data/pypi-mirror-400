# COSBOS: COlor-Sensor-Based Occupancy Sensing

[![View COSBOS: COlor-Sensor-Based Occupancy Sensing on File Exchange](https://www.mathworks.com/matlabcentral/images/matlab-file-exchange.svg)](https://www.mathworks.com/matlabcentral/fileexchange/48428-cosbos-color-sensor-based-occupancy-sensing)
[![Octave application](https://github.com/wq2012/COSBOS/actions/workflows/octave.yml/badge.svg)](https://github.com/wq2012/COSBOS/actions/workflows/octave.yml)
[![Python CI](https://github.com/wq2012/COSBOS/actions/workflows/python.yml/badge.svg)](https://github.com/wq2012/COSBOS/actions/workflows/python.yml)

![logo](resources/logo.png)

COSBOS is a high-performance MATLAB/Octave toolbox for occupancy sensing using color sensors. It implements advanced Light Transport Matrix (LTM) recovery techniques and occupancy models, optimized for speed and reliability.

---

## Table of Contents
- [Project Overview](#project-overview)
- [Installation and Setup](#installation-and-setup)
- [Key Features](#key-features)
- [Modules](#modules)
  - [LTM Recovery](#ltm-recovery)
  - [Blockage Model](#blockage-model)
  - [Reflection Model](#reflection-model)
- [Running Demos](#running-demos)
- [Unit Testing](#unit-testing)
- [Citation](#citation)

---

## Project Overview
Color sensors can be used as low-cost, privacy-preserving alternatives to cameras for occupancy sensing. By measuring changes in the Light Transport Matrix (LTM) of a room, we can infer the presence and location of occupants. COSBOS provides the tools to:
1. Recover the LTM from sensor measurements, both overdetermined and underdetermined. This work
is described in [2].
2. Model occupancy using light blockage (for wall-mounted sensors). This work is
described in [1] and [3].
3. Model occupancy using light reflection (for ceiling-mounted sensors). This work is described in [1].

More information:
* [4] is not directly related to this package. It is about the new color
sensors that we have built for occupancy sensing.
* In each demo, we included example data. But the code for data collection
has too many dependencies: platform, hardware, driver, and other software
packages. Thus we are not including the code for data collection here.
* More information on this work can be found here:
  * https://sites.google.com/site/cosboswiki/
* This library is also available at MathWorks:
  * https://www.mathworks.com/matlabcentral/fileexchange/48428-cosbos-color-sensor-based-occupancy-sensing

## Installation and Setup
1. Clone the repository: `git clone https://github.com/wq2012/COSBOS.git`
2. Ensure you have MATLAB or Octave installed.
3. If using the Blockage Model, you need to compile the C++ MEX files:
   - Go to `BlockageModel/` and run `compile.m` in MATLAB/Octave.
   - Requires a C++ compiler (e.g., GCC, Clang, or MSVC).

## Key Features
- **High Performance**: Vectorized computations and optimized C++ MEX implementations.
- **Robust Modularity**: Module-specific configuration files (e.g., `coordinates_blockage.m`) to prevent name collisions.
- **Absolute Path Support**: All demos and tests are designed to run from any directory without path issues.
- **Clean Output**: Silenced runtime warnings and polished logs.

## Modules

### LTM Recovery
Located in `LTM_Recovery/`. Solves $Y = AX$ for the mapping $A$.
- `solve_A_fullrank.m`: Standard pseudo-inverse solution.
- `solve_A_Fnorm.m`: Stable low-rank approximation via SVD.
- `solve_A_0norm.m`: Sparse recovery using Orthogonal Matching Pursuit (OMP).
- `solve_A_1norm.m`: Sparse recovery using primal-dual interior point methods.

### Blockage Model
Located in `BlockageModel/`. For wall-mounted sensors.
- Uses `coordinates_blockage.m` for spatial configuration.
- `hashGaussians.cpp`: Optimized MEX code for distance hashing (no heap allocation in hot loops).
- `volumeFromHashing.cpp`: Fast volume rendering via optimized internal matrix management.

### Reflection Model
Located in `ReflectionModel/`. For ceiling-mounted sensors.
- Uses `coordinates_reflection.m` for spatial configuration.
- `getReflectionKernel.m`: Fully vectorized implementation for near-instant kernel generation.

## Running Demos
Each module includes a robust demo script:
- `LTM_Recovery/demo_LTM.m`: Demonstrates LTM recovery techniques.
- `BlockageModel/demo_Blockage.m`: Renders a 3D occupancy volume.
- `ReflectionModel/demo_Reflection.m`: Generates a floor-plane occupancy map.

## Unit Testing
Run the master test script from the project root:
```matlab
addpath('tests');
run_tests;
```
This verifies LTM recovery accuracy, MEX script correctness, and model performance.

## Python Package

COSBOS is also available as a Python package `cosbos`. It provides pure Python implementations of the core algorithms (Reflection Model, Blockage Model, LTM Recovery).

### Installation

```bash
pip install cosbos
```

### Usage

```python
from cosbos import reflection, blockage, ltm
import numpy as np

# Reflection Model
# Calculate reflection kernel for a light-sensor pair
# light: [x, y, z], sensor: [x, y, z], dim: [dx, dy, dz]
K = reflection.getReflectionKernel(light=[75, 22.5, 86.4], 
                                   sensor=[66, 22, 86.4], 
                                   dim=[87, 136, 88], 
                                   para=1)

# Blockage Model
# Hash Gaussians for occupancy volume
# sensors: [N, 3], lights: [M, 3]
H = blockage.hashGaussians(sensors, lights, dim, sigma=2.0)
# Reconstruct volume
V = blockage.volumeFromHashing(sensors, lights, dim, H, E)

# LTM Recovery
# Recover matrix A from measurements Y and training data X
# X: [m, N], Y: [l, N] (m: features, l: sensors, N: samples)
A = ltm.solve_A_1norm(X, Y)
```

### Development
To run tests locally:
```bash
cd python
pip install -e .
pytest tests/
```

## Citation
If you use this work in your research, please cite:

**Plain Text**:

> [1] Quan Wang, Xinchi Zhang, Kim L. Boyer, "Occupancy distribution estimation for smart light delivery with perturbation-modulated light sensing", Journal of Solid State Lighting 2014 1:17, ISSN 2196-1107,
doi:10.1186/s40539-014-0017-2.

> [2] Quan Wang, Xinchi Zhang, Meng Wang, Kim L. Boyer, "Learning Room Occupancy Patterns from Sparsely Recovered Light Transport Models", 22nd International Conference on Pattern Recognition (ICPR), 2014.

> [3] Quan Wang, Xinchi Zhang, Kim L. Boyer, "3D Scene Estimation with Perturbation-Modulated Light and Distributed Sensors", 10th IEEE Workshop on Perception Beyond the Visible Spectrum (PBVS).

> [4] Xinchi Zhang, Quan Wang, Kim L. Boyer, "Illumination Adaptation with Rapid-Response Color Sensors", SPIE Optical Engineering + Applications, 2014.

> [5] Quan Wang.
Exploiting Geometric and Spatial Constraints for Vision and Lighting Applications.
Ph.D. dissertation, Rensselaer Polytechnic Institute, 2014.


**BibTeX:**

```
@article{wang2014occupancy,
  title={Occupancy distribution estimation for smart light delivery with perturbation-modulated light sensing},
  author={Wang, Quan and Zhang, Xinchi and Boyer, Kim L},
  journal={Journal of solid state lighting},
  volume={1},
  number={1},
  pages={17},
  year={2014},
  publisher={Springer}
}

@inproceedings{wang2014learning,
  title={Learning room occupancy patterns from sparsely recovered light transport models},
  author={Wang, Quan and Zhang, Xinchi and Wang, Meng and Boyer, Kim L},
  booktitle={2014 22nd International Conference on Pattern Recognition},
  pages={1987--1992},
  year={2014},
  organization={IEEE}
}

@inproceedings{wang20143d,
  title={3d scene estimation with perturbation-modulated light and distributed sensors},
  author={Wang, Quan and Zhang, Xinchi and Boyer, Kim L},
  booktitle={Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition Workshops},
  pages={252--257},
  year={2014}
}

@inproceedings{zhang2014illumination,
  title={Illumination adaptation with rapid-response color sensors},
  author={Zhang, Xinchi and Wang, Quan and Boyer, Kim L},
  booktitle={Optics and Photonics for Information Processing VIII},
  volume={9216},
  pages={49--60},
  year={2014},
  organization={SPIE}
}

@phdthesis{wang2014exploiting,
  title={Exploiting Geometric and Spatial Constraints for Vision and Lighting Applications},
  author={Quan Wang},
  year={2014},
  school={Rensselaer Polytechnic Institute},
}
```
