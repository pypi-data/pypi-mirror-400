[![PyPI](https://img.shields.io/pypi/v/pyovf)](https://pypi.org/project/pyovf) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyovf)](https://pypi.org/project/pyovf) [![PyPI - Wheel](https://img.shields.io/pypi/wheel/pyovf)](https://pypi.org/project/pyovf) [![PyPI - License](https://img.shields.io/pypi/l/pyovf)](https://pypi.org/project/pyovf) [![Downloads](https://pepy.tech/badge/pyovf)](https://pypi.org/project/pyovf) [![pipeline status](https://gitlab.flavio.be/flavio/pyovf/badges/main/pipeline.svg)](https://gitlab.flavio.be/flavio/pyovf/-/commits/main)

# pyOVF

A Python library for reading and writing OVF (OOMMF Vector Field) files used in micromagnetic simulations.

## Features

- **Fast I/O**: C++ backend for high-performance file operations (via [ovf-rw](https://gitlab.flavio.be/flavio/ovf-rw))
- **NumPy Integration**: Seamless conversion between OVF files and NumPy arrays
- **Pure Python Fallback**: Works even without the C++ extension (slower but functional)
- **OOMMF & mumax3 Compatible**: Supports files from both simulation packages
- **Binary Format**: Reads and writes OVF 2.0 Binary 4 format
- **Wide Python Support**: Python 3.8 - 3.14

## Installation

```bash
pip install pyovf
```

### From Source

```bash
git clone https://gitlab.flavio.be/flavio/pyovf.git
cd pyovf
pip install -e .
```

### Building with ovf-rw

The C++ bindings are built from the [ovf-rw](https://gitlab.flavio.be/flavio/ovf-rw) library. When building from source, the build system will automatically fetch the required sources.

```bash
# Clone both repositories
git clone https://gitlab.flavio.be/flavio/pyovf.git
git clone https://gitlab.flavio.be/flavio/ovf-rw.git

# Build pyovf (it will find ovf-rw in the parent directory)
cd pyovf
pip install -e .
```

## Quick Start

```python
import pyovf
import numpy as np

# Read an OVF file
ovf = pyovf.read("magnetization.ovf")
print(f"Data shape: {ovf.data.shape}")
print(f"Grid: {ovf.xnodes}x{ovf.ynodes}x{ovf.znodes}")

# Access and modify data
mx = ovf.data[..., 0]  # X component
my = ovf.data[..., 1]  # Y component
mz = ovf.data[..., 2]  # Z component

# Create a new OVF file from scratch
data = np.zeros((1, 100, 100, 3), dtype=np.float32)
data[..., 2] = 1.0  # Uniform mz = 1

ovf_new = pyovf.create(
    data,
    xstepsize=5e-9,  # 5 nm cells
    ystepsize=5e-9,
    zstepsize=10e-9,
    title="m"
)

pyovf.write("uniform_state.ovf", ovf_new)
```

## API Reference

### Functions

#### `pyovf.read(filename) -> OVFFile`

Read an OVF file and return an OVFFile object.

#### `pyovf.write(filename, ovf)`

Write an OVFFile object to disk.

#### `pyovf.create(data, **kwargs) -> OVFFile`

Create a new OVFFile from a NumPy array.

### OVFFile Properties

| Property | Type | Description |
| -------- | ---- | ----------- |
| `data` | np.ndarray | Field data (z, y, x, [dim]) |
| `xnodes`, `ynodes`, `znodes` | int | Grid dimensions |
| `xstepsize`, `ystepsize`, `zstepsize` | float | Cell sizes |
| `valuedim` | int | Components (1=scalar, 3=vector) |
| `Title` | str | Data description |
| `TotalSimTime` | float | Simulation time |

## Data Layout

OVF files store data in column-major order:

- For a vector field: `data[z, y, x, component]`
- For a scalar field: `data[z, y, x]`

## Supported Python Versions

| Python Version | Status |
| -------------- | ------ |
| 3.8 | ✅ Supported |
| 3.9 | ✅ Supported |
| 3.10 | ✅ Supported |
| 3.11 | ✅ Supported |
| 3.12 | ✅ Supported |
| 3.13 | ✅ Supported |
| 3.14 | ✅ Supported (experimental) |

## Project Structure

```txt
pyovf/
├── pyovf/              # Main package
│   ├── __init__.py     # Package initialization
│   ├── _version.py     # Dynamic version (auto-generated)
│   ├── helper_funcs.py # Helper functions
│   ├── ovf_handler.py  # OVF file handler
│   └── binaries/       # Compiled C++ bindings
├── src/                # Source for pybind11 bindings
├── tests/              # Unit tests
├── pyproject.toml      # Build configuration
├── setup.py            # Setup script with CMake integration
└── CMakeLists.txt      # CMake build configuration
```

## Related Projects

- **[ovf-rw](https://gitlab.flavio.be/flavio/ovf-rw)**: The underlying C++ library for OVF file I/O, providing:
  - MATLAB bindings via MEX
  - Python bindings via Cython
  - High-performance binary file operations

## Development

### Setting up a development environment

```bash
git clone https://gitlab.flavio.be/flavio/pyovf.git
cd pyovf
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Running tests

```bash
pytest tests/ -v --cov=pyovf
```

### Building wheels

```bash
pip install build
python -m build
```

## Versioning

This project uses [setuptools-scm](https://github.com/pypa/setuptools-scm) for dynamic versioning based on git tags. Version numbers are automatically determined from git history:

- Tagged commits (e.g., `v1.0.0`) produce release versions (`1.0.0`)
- Commits after a tag produce development versions (`1.0.1.dev3+g1234567`)

To create a new release:

```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Author

Prof. Flavio ABREU ARAUJO  
Email: <flavio.abreuaraujo@uclouvain.be>

## Citation

If you use this software in your research, please cite:

```bibtex
@software{pyovf,
  author = {Abreu Araujo, Flavio},
  title = {pyovf: Python library for OVF file I/O},
  year = {2021},
  url = {https://gitlab.flavio.be/flavio/pyovf}
}
```
