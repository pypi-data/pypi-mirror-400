# Multi-Architecture Setup for pyovf on macOS

Complete guide for building pyovf wheels on Apple Silicon Macs (M1/M2/M3) for both ARM64 and x86_64 architectures.

## Overview

On Apple Silicon Macs, you can build wheels for two architectures:

| Architecture | Performance | Use Case |
| ------------ | ----------- | -------- |
| ARM64 | Native (fast) | Apple Silicon Macs |
| x86_64 | Rosetta 2 (slower) | Intel Macs compatibility |

## Prerequisites

### ARM64 Homebrew (Native)

Install Homebrew for ARM64 at `/opt/homebrew`:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Add to `~/.zshrc`:

```bash
eval "$(/opt/homebrew/bin/brew shellenv)"
```

Install Python versions:

```bash
brew install python@3.9 python@3.10 python@3.11 python@3.12 python@3.13 python@3.14
```

### x86_64 Homebrew (Rosetta 2)

Install Homebrew for x86_64 at `/usr/local`:

```bash
arch -x86_64 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Install Python versions:

```bash
arch -x86_64 /usr/local/bin/brew install python@3.9 python@3.10 python@3.11 python@3.12 python@3.13 python@3.14
```

### Build Tools

Install build tools for each Python version:

```bash
# ARM64
for py in 3.9 3.10 3.11 3.12 3.13 3.14; do
  /opt/homebrew/bin/python${py} -m pip install --break-system-packages build twine
done

# x86_64
for py in 3.9 3.10 3.11 3.12 3.13 3.14; do
  /usr/local/bin/python${py} -m pip install --break-system-packages build twine
done
```

## Python Installation Paths

| Version | ARM64 Path | x86_64 Path |
| ------- | ---------- | ----------- |
| 3.9 | `/opt/homebrew/bin/python3.9` | `/usr/local/bin/python3.9` |
| 3.10 | `/opt/homebrew/bin/python3.10` | `/usr/local/bin/python3.10` |
| 3.11 | `/opt/homebrew/bin/python3.11` | `/usr/local/bin/python3.11` |
| 3.12 | `/opt/homebrew/bin/python3.12` | `/usr/local/bin/python3.12` |
| 3.13 | `/opt/homebrew/bin/python3.13` | `/usr/local/bin/python3.13` |
| 3.14 | `/opt/homebrew/bin/python3.14` | `/usr/local/bin/python3.14` |

## Shell Configuration

Add these aliases to `~/.zshrc` for convenience:

```bash
# ARM64 Homebrew
eval "$(/opt/homebrew/bin/brew shellenv)"

# Python aliases (ARM64 native)
alias python3.9="/opt/homebrew/bin/python3.9"
alias python3.10="/opt/homebrew/bin/python3.10"
alias python3.11="/opt/homebrew/bin/python3.11"
alias python3.12="/opt/homebrew/bin/python3.12"
alias python3.13="/opt/homebrew/bin/python3.13"
alias python3.14="/opt/homebrew/bin/python3.14"

# x86_64 Python aliases
alias python3.9-x86="/usr/local/bin/python3.9"
alias python3.10-x86="/usr/local/bin/python3.10"
alias python3.11-x86="/usr/local/bin/python3.11"
alias python3.12-x86="/usr/local/bin/python3.12"
alias python3.13-x86="/usr/local/bin/python3.13"
alias python3.14-x86="/usr/local/bin/python3.14"
```

## Building Wheels

### Automated Build Script

Use `build_all_architectures.sh` for automated builds:

```bash
# Build all (12 wheels: 6 ARM64 + 6 x86_64)
./build_all_architectures.sh

# ARM64 only (6 wheels)
./build_all_architectures.sh --arm64

# x86_64 only (6 wheels)
./build_all_architectures.sh --x86_64

# Specific Python version, both architectures
./build_all_architectures.sh --python 3.11

# Specific version and architecture
./build_all_architectures.sh --arm64 --python 3.11
```

### Manual Build

```bash
# ARM64 wheel
/opt/homebrew/bin/python3.11 -m build -w

# x86_64 wheel
/usr/local/bin/python3.11 -m build -w
```

## Output Wheels

Wheels are generated in `dist/` with architecture-specific names:

```txt
dist/
├── pyovf-X.Y.Z-cp39-cp39-macosx_14_0_arm64.whl
├── pyovf-X.Y.Z-cp39-cp39-macosx_14_0_x86_64.whl
├── pyovf-X.Y.Z-cp310-cp310-macosx_14_0_arm64.whl
├── pyovf-X.Y.Z-cp310-cp310-macosx_14_0_x86_64.whl
├── pyovf-X.Y.Z-cp311-cp311-macosx_14_0_arm64.whl
├── pyovf-X.Y.Z-cp311-cp311-macosx_14_0_x86_64.whl
├── pyovf-X.Y.Z-cp312-cp312-macosx_14_0_arm64.whl
├── pyovf-X.Y.Z-cp312-cp312-macosx_14_0_x86_64.whl
├── pyovf-X.Y.Z-cp313-cp313-macosx_14_0_arm64.whl
├── pyovf-X.Y.Z-cp313-cp313-macosx_14_0_x86_64.whl
├── pyovf-X.Y.Z-cp314-cp314-macosx_14_0_arm64.whl
├── pyovf-X.Y.Z-cp314-cp314-macosx_14_0_x86_64.whl
└── pyovf-X.Y.Z.tar.gz
```

## Verification

### Check Python Architecture

```bash
# Verify ARM64
/opt/homebrew/bin/python3.11 -c "import platform; print(platform.machine())"
# Output: arm64

# Verify x86_64
/usr/local/bin/python3.11 -c "import platform; print(platform.machine())"
# Output: x86_64
```

### Check Wheel Architecture

```bash
# Extract WHEEL metadata
unzip -p dist/pyovf-*-cp311-*-arm64.whl '*/WHEEL' | grep Tag
# Output: Tag: cp311-cp311-macosx_14_0_arm64

unzip -p dist/pyovf-*-cp311-*-x86_64.whl '*/WHEEL' | grep Tag
# Output: Tag: cp311-cp311-macosx_14_0_x86_64
```

### Verify All Python Versions

```bash
for py in 3.9 3.10 3.11 3.12 3.13 3.14; do
  echo -n "Python $py ARM64: "
  /opt/homebrew/bin/python${py} -c "import platform; print(platform.machine())"
  echo -n "Python $py x86_64: "
  /usr/local/bin/python${py} -c "import platform; print(platform.machine())"
done
```

## Release Process

```bash
# 1. Tag the release
git tag -a v0.2.7 -m "Release 0.2.7"
git push --tags

# 2. Clean and build all wheels
rm -rf dist/ build/
./build_all_architectures.sh

# 3. Verify wheels
ls -lh dist/

# 4. Upload to PyPI
twine upload dist/*
```

## Troubleshooting

### "No module named build"

Install build tools for the specific Python:

```bash
/opt/homebrew/bin/python3.11 -m pip install --break-system-packages build
```

### "externally-managed-environment" Error

Use `--break-system-packages` flag:

```bash
python -m pip install --break-system-packages build twine
```

### Wrong Architecture in Wheel

Ensure you're using the correct Python path:

- ARM64 wheels: Use `/opt/homebrew/bin/python3.X`
- x86_64 wheels: Use `/usr/local/bin/python3.X`

### Build Script Exits Early

The build script should not have `set -e`. Check the first lines of `build_all_architectures.sh`.

### CMake Not Found

Install CMake:

```bash
brew install cmake
```

### Compiler Errors

Ensure Xcode Command Line Tools are installed:

```bash
xcode-select --install
```
