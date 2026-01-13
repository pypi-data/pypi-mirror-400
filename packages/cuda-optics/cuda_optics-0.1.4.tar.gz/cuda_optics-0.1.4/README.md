# Welcome to cuda_optics!
[![PyPI version](https://badge.fury.io/py/cuda-optics.svg)](https://badge.fury.io/py/cuda-optics)
![Language](https://img.shields.io/badge/language-Python%20%7C%20C%2B%2B%20%7C%20CUDA-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)


**cuda_optics** is a high-performance ray-tracing simulation framework designed to bridge the gap between Python's approachability and raw hardware acceleration. It functions as a scriptable, 2D optical CAD library , optimized for simulating optical benches, lens barrels, and telescope/microscope designs.

The system features a hybrid architecture flexible enough for any hardware environment. It serves as a **physics sandbox**, offering students, educators, hobbyists, and researchers a large selection of built-in functionalities while maintaining maximum control over ray generation and element geometry. For detailed documentation, find the file `cuda_optics_documentation.ipynb` in the `examples` folder on my github linked below.

## Table of Contents
- [Why use this framework?](#why-use-this-framework)
- [Motivation & Design](#motivation-behind-the-framework-and-design)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Links](#links)

## Why use this framework?
1. **Cross-Platform Core:** Native support for both Linux and Windows systems ensures consistent deployment across diverse development environments.

2. **Hardware Acceleration & Optimization:** Optimized for NVIDIA GPUs (Compute Capability 6.1+), supporting architectures from Pascal to Hopper. This high-throughput capability allows iterative optimization workflows such as Monte Carlo tolerance analysis or global optimization loops (e.g., Genetic Algorithms).

3. **Hybrid Compatibility:** Includes a highly optimized C++ CPU engine that can be activated if a GPU is unavailable, ensuring code portability across high-performance workstations and standard educational laptops.

4. **Zero-Restriction Geometry & Synthetic Data:** Unlike standard matrix-optics tools, this framework poses no restrictions on element orientation or position. This geometric freedom makes it an ideal engine for procedurally generating massive synthetic datasets, crucial for training Machine Learning models in computational photography, depth estimation, and aberration correction.

5. **Rich Component Library:** Built-in OOP support for 11 optical elements including parabolic mirrors, thick lenses (meniscus/biconvex), prisms, and diffraction gratings. This modularity supports niche applications, such as designing folded spectrometers or simulating complex beam delivery systems for high-power lasers.

6. **Education & Visualization:** Integrated `matplotlib` plotting tools provide instant visual feedback. The library functions as a risk-free "Virtual Optical Bench",  allowing students to visualize abstract concepts like spherical aberration, chromatic dispersion, and spatial filtering in real-time. The framework can also be utilised by LLMs to generate nice plots while explaining topics related to optics.

7. **Pipeline Integration (Python Native):** A user-friendly Python interface utilizes intuitive commands that integrate natively with the scientific stack (NumPy, SciPy, PyTorch). This allows the ray tracer to act as a direct data generator within AI training pipelines or automated control loops without the bottleneck of file I/O or proprietary API wrappers.

8. **Open & Free:** Released under the MIT License, it is free for both educational instruction and commercial industrial use.


## Motivation behind the framework and design
While working on a project regarding spectroscopes, I required a software/library to simulate various configurations and validate my calculations. Even after spending a lot of time searching for such resources, I couldn't find one which could solve my very specific problem. This prompted me to write a python code for my immediate requirements and while doing that, I realised how I can code an actual generalised physics engine for optical system simulation. I then researched about various optical simulators available and found that 
existing resources were either too simplistic for niche problems or were expensive proprietary software inaccessible to students.

I focused on both educational and industrial value of this project. The plotting functionalities help in learning and build confidence through instant visualisation and easy to interpret feedback. The C++ and CUDA backends allow for high throughput ray tracing suitable for rigorous analysis. The OOP based architecture allows more optical elements and functionalities to be added as and when required.

Designed effectively as a virtual optical bench, the framework currently focuses on 2D arrangements to prioritize clarity and speed. This allows for precise Meridional Plane Analysis which is ideal for symmetric systems like telescopes or planar experiments. However, the core physics logic is built on dimension-agnostic vector algebra (Linear Algebra), meaning the simulation code is ready for N-dimensional expansion with minimal architectural changes.

## Installation

### Option 1: Install via Pip (Recommended)
The easiest way to install on **Windows** and **Linux**. This includes pre-compiled binaries for both CPU and GPU.

```bash
pip install cuda_optics
```

### Option 2: Build from Source
For **macOS** users or those interested in modifying the core engine:

```bash
git clone [https://github.com/Adityavardhan-Srivastava/cuda_optics.git](https://github.com/Adityavardhan-Srivastava/cuda_optics.git)
cd cuda_optics
```

Then compile the cpp/cuda file in `src_native/` and place them in `cuda_optics/bin/` and delete the binaries already present there. Compile using appropriate compilers.

## Quick Start
Here is a simple example of how to create a lens and trace a ray
```python
import cuda_optics as co
import matplotlib.pyplot as plt

# 1. Create Elements
# A lens centered at x=0.5, with radius of curvature 0.5 (front) and -0.5 (back)
lens = co.Lens(name="Lens", center=[0.5, 0.0], normal=[1.0, 0.0], 
               aperture=0.4, refractive_index=1.5, 
               R1=0.5, R2=-0.5, thickness=0.1)

screen = co.Screen(name="Sensor", center=[1.0, 0.0], normal=[-1.0, 0.0], aperture=0.5)

# 2. Create Rays
# Generating 3 parallel rays manually
rays = [
    co.Ray(pos=[0.0, -0.1], dir=[1.0, 0.0], wavelength=550, color='green'),
    co.Ray(pos=[0.0,  0.0], dir=[1.0, 0.0], wavelength=550, color='green'),
    co.Ray(pos=[0.0,  0.1], dir=[1.0, 0.0], wavelength=550, color='green')
]

# 3. Run Simulation 
# (Set use_gpu=True if you have an NVIDIA GPU)
co.run_simulation(rays, [lens, screen], bounces=5, use_gpu=False)

# 4. Visualize
fig, ax = plt.subplots()
co.plot_system(rays, [lens, screen], ax)
plt.title("Quick Start: Simple Lens")
plt.show()
```

For more such examples, explore the folder `examples/`. The python file `cuda_optics_original.py` contains all elements and functionalities in python to take reference from. The jupyter notebook `Documentation.ipynb` contains documentation and example codes for this library.

## Links
1. Github repo: https://github.com/Adityavardhan-Srivastava/cuda_optics

2. PyPI page: https://pypi.org/project/cuda-optics/#description