# pyovf Build Guide

Build instructions for pyovf on macOS (ARM64 and x86_64).

## Quick Build

```bash
# Single Python version (current interpreter)
python -m build

# All Python versions, both architectures
./build_all_architectures.sh
```

## Requirements

### ARM64 (Native M1/M2)

```bash
# Python at /opt/homebrew/bin/python3.X
/opt/homebrew/bin/python3.11 -m pip install build twine
```

### x86_64 (Rosetta 2)

```bash
# Python at /usr/local/bin/python3.X
/usr/local/bin/python3.11 -m pip install build twine
```

## Build Commands

### Single Version

```bash
# ARM64 native
/opt/homebrew/bin/python3.11 -m build

# x86_64 compatible
/usr/local/bin/python3.11 -m build
```

### All Versions

```bash
# ARM64 only (fast)
./build_all_architectures.sh --arm64

# x86_64 only
./build_all_architectures.sh --x86_64

# Both architectures (12 wheels total)
./build_all_architectures.sh

# Specific Python version
./build_all_architectures.sh --python 3.11
```

## Output

Wheels are generated in `dist/`:

| Architecture | Wheel Pattern |
| ------------ | ------------- |
| ARM64 | `pyovf-X.Y.Z-cpXX-cpXX-macosx_14_0_arm64.whl` |
| x86_64 | `pyovf-X.Y.Z-cpXX-cpXX-macosx_14_0_x86_64.whl` |

## Release

```bash
# Tag version
git tag -a v0.2.7 -m "Release 0.2.7"
git push --tags

# Build all wheels
./build_all_architectures.sh

# Upload to PyPI
twine upload dist/*
```

## Python Paths

| Version | ARM64 Path | x86_64 Path |
| ------- | ---------- | ----------- |
| 3.9 | `/opt/homebrew/bin/python3.9` | `/usr/local/bin/python3.9` |
| 3.10 | `/opt/homebrew/bin/python3.10` | `/usr/local/bin/python3.10` |
| 3.11 | `/opt/homebrew/bin/python3.11` | `/usr/local/bin/python3.11` |
| 3.12 | `/opt/homebrew/bin/python3.12` | `/usr/local/bin/python3.12` |
| 3.13 | `/opt/homebrew/bin/python3.13` | `/usr/local/bin/python3.13` |
| 3.14 | `/opt/homebrew/bin/python3.14` | `/usr/local/bin/python3.14` |

## Verify Architecture

```bash
# Check Python architecture
python -c "import platform; print(platform.machine())"

# Check wheel architecture
unzip -p dist/*.whl '*/WHEEL' | grep Tag
```

## Troubleshooting

### "No module named build"

```bash
python -m pip install --break-system-packages build
```

### Wrong architecture in wheel

- Use the correct Python path for your target architecture
- ARM64: `/opt/homebrew/bin/python3.X`
- x86_64: `/usr/local/bin/python3.X`
