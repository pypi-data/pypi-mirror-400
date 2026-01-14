# Local CI/CD & Deployment Quick Reference

## 🚀 Quick Start

### Local Pipeline Testing

```bash
cd /Users/flavio/ownCloud/MyPythonLib/pyovf

# Run complete pipeline (prepare → build → test)
bash local-ci.sh all

# Build wheels only
bash local-ci.sh build

# Test wheels only
bash local-ci.sh test

# Build specific Python version
bash local-ci.sh build --python 3.14

# Clean all artifacts
bash local-ci.sh clean
```

### Deployment to PyPI

```bash
# 1. Set your PyPI token (one-time setup in shell config)
export PYPI_TOKEN="pypi-AgEIcHlwaS5vcmc..."

# 2. Deploy locally (test first)
bash local-ci.sh deploy

# 3. Or tag for automatic GitLab deployment
git tag v0.2.5
git push origin v0.2.5
```

---

## 📋 Workflow

### Development Workflow

```bash
# Make changes
vim pyovf/ovf_handler.py

# Test locally on all Python versions
bash local-ci.sh test

# Commit and push
git add .
git commit -m "Fix bug in OVF handler"
git push origin main

# Pipeline runs: prepare → build → test (on GitLab)
```

### Release Workflow

```bash
# 1. Bump version (automatic with setuptools-scm via git tags)
git tag v0.2.5 -m "Release version 0.2.5"

# 2. Push tag to trigger deployment
git push origin v0.2.5

# Pipeline runs: prepare → build → test → deploy
```

### Debugging Workflow

```bash
# 1. Run local pipeline to find issue
bash local-ci.sh all

# 2. Build specific Python version if problem appears
bash local-ci.sh build --python 3.10

# 3. Test and fix
bash local-ci.sh test --python 3.10

# 4. Clean and retry
bash local-ci.sh clean
bash local-ci.sh all
```

---

## 🔧 Command Reference

### Build Commands

| Command | Purpose |
| --- | --- |
| `bash local-ci.sh prepare` | Clone ovf-rw sources |
| `bash local-ci.sh build` | Build wheels for all Python versions |
| `bash local-ci.sh build --python 3.14` | Build for specific Python version |

### Test Commands

| Command | Purpose |
| --- | --- |
| `bash local-ci.sh test` | Test all built wheels |
| `bash local-ci.sh test --python 3.10` | Test specific Python version |

### Utility Commands

| Command | Purpose |
| --- | --- |
| `bash local-ci.sh all` | Full pipeline: prepare → build → test |
| `bash local-ci.sh clean` | Remove all artifacts and venvs |
| `bash local-ci.sh deploy` | Upload to PyPI (requires PYPI_TOKEN) |

---

## 🔐 PyPI Credentials Setup

### Step 1: Create PyPI Token

```bash
# Visit https://pypi.org/ → Account settings → API tokens
# Create token with scope "Entire account"
# Copy token (format: pypi-AgEIcHlwaS5vcmc...)
```

### Step 2: Local Testing

```bash
# Set environment variable
export PYPI_TOKEN="pypi-AgEIcHlwaS5vcmc..."

# Test deploy locally
bash local-ci.sh deploy

# Or test with twine
twine upload --username __token__ --password "$PYPI_TOKEN" dist/*
```

### Step 3: GitLab CI/CD Variables

1. Go to: `gitlab.flavio.be/flavio/pyovf` → Settings → CI/CD → Variables
2. Click "Add variable"
3. Add `PYPI_TOKEN`:
   - Value: `pypi-AgEIcHlwaS5vcmc...`
   - **Protected**: ✅ Yes (only main branch)
   - **Masked**: ✅ Yes (hide in logs)
   - **CI/CD**: ✅ Yes (available in pipelines)

### Step 4: GitLab Automatic Deployment

```bash
# Create and push a version tag
git tag v0.2.5
git push origin v0.2.5

# GitLab pipeline automatically runs:
# 1. prepare - setup sources
# 2. build - build wheels for all Python versions
# 3. test - test wheels on all Python versions
# 4. deploy - upload to PyPI (only if all tests pass)
```

---

## 📊 Understanding the Pipeline

### Stage 1: Prepare

- Clones `ovf-rw` repository
- Copies C++ source files
- Prepares build environment

### Stage 2: Build

- Creates Python venv for each version (3.9-3.14)
- Installs build dependencies (build, pybind11, cmake, numpy)
- Builds wheels using `python -m build --wheel`
- Builds source distribution (sdist)
- **Output**: 12 wheels + 1 sdist in `dist/` directory

### Stage 3: Test

- Creates test venv for each Python version
- Installs pytest, pytest-cov, numpy
- Installs built wheel
- Runs test suite with coverage reporting
- **Requirement**: All tests must pass before deploy

### Stage 4: Deploy (GitLab CI/CD only)

- Triggered only on git tags (e.g., `git tag v0.2.5`)
- Activates only if all tests pass
- Uploads to PyPI using twine
- **Requirement**: PYPI_TOKEN must be set in CI/CD Variables

---

## ⚙️ Environment Details

### Python Locations (macOS with Homebrew)

```bash
# ARM64 native (fast, 3-4x performance)
/opt/homebrew/bin/python3.9
/opt/homebrew/bin/python3.10
/opt/homebrew/bin/python3.11
/opt/homebrew/bin/python3.12
/opt/homebrew/bin/python3.13
/opt/homebrew/bin/python3.14

# Verify
/opt/homebrew/bin/python3.14 --version
/opt/homebrew/bin/python3.14 -c "import sys; print(sys.platform, sys.maxsize)"
```

### Build Dependencies

Automatically installed in each venv:

- `build` - Python build tool
- `pip` - Package installer
- `setuptools` - Build utilities
- `wheel` - Wheel format support
- `pybind11` - C++ bindings
- `cmake` - C++ build system
- `numpy` - Numerical Python library

### Test Dependencies

Automatically installed:

- `pytest` - Test runner
- `pytest-cov` - Coverage reporting
- `numpy` - Required by pyovf

---

## 🐛 Troubleshooting

### Issue: "Python X.Y not found"

```bash
# Check available Python versions
ls /opt/homebrew/bin/python*

# Install missing version
brew install python@3.10

# Verify
/opt/homebrew/bin/python3.10 --version
```

### Issue: Build fails with "ImportError: numpy"

```bash
# Reinstall numpy in all Python versions
for py in 3.9 3.10 3.11 3.12 3.13 3.14; do
  /opt/homebrew/bin/python${py} -m pip install --force-reinstall numpy
done

# Retry build
bash local-ci.sh clean
bash local-ci.sh build
```

### Issue: Deploy fails with "401 Unauthorized"

```bash
# 1. Verify token format
echo $PYPI_TOKEN | grep -o "^pypi-"  # Should print "pypi-"

# 2. Test token locally
twine check dist/*
twine upload --username __token__ --password "$PYPI_TOKEN" dist/* --dry-run

# 3. Regenerate token if needed
# Visit https://pypi.org → Account settings → API tokens
```

### Issue: GitLab pipeline not running deploy stage

**Possible causes:**

1. No git tag (deploy requires `if: $CI_COMMIT_TAG`)
2. Tests failed (deploy only runs on success)
3. Branch not protected (if using protected variables)

**Solution:**

```bash
# Create proper tag and push
git tag v0.2.5 -m "Release version 0.2.5"
git push origin v0.2.5

# Check pipeline status at:
# https://gitlab.flavio.be/flavio/pyovf/pipelines
```

### Issue: Wheel has wrong architecture

```bash
# Check wheel architecture
cd dist && file *.whl

# For ARM64: Mach-O 64-bit
# For x86_64: Still Mach-O 64-bit but different architecture

# Verify with:
for whl in *.whl; do
  echo "=== $whl ===" 
  unzip -l "$whl" | grep ".so" | head -3
done
```

---

## 📝 Key Files

| File | Purpose |
| --- | --- |
| `local-ci.sh` | Local pipeline script (mirrors .gitlab-ci.yml) |
| `.gitlab-ci.yml` | GitLab CI/CD configuration |
| `pyproject.toml` | Build configuration |
| `setup.py` | Legacy setup script |
| `PYPI_CREDENTIALS_SETUP.md` | Detailed credentials guide |
| `run_tests.sh` | Multi-version test runner |

---

## 🔒 Security Checklist

Before first deployment:

- [ ] PYPI_TOKEN generated at <https://pypi.org>
- [ ] PYPI_TOKEN added to GitLab CI/CD Variables
- [ ] PYPI_TOKEN **masked** in CI/CD Variables
- [ ] PYPI_TOKEN **protected** to main/release branches
- [ ] No `.pypirc` file in Git
- [ ] No credentials in `.gitlab-ci.yml`
- [ ] Deploy job uses `$PYPI_TOKEN` environment variable
- [ ] Test jobs all pass before deploy
- [ ] Dry run with testpypi successful

---

## 📞 Support & Documentation

**Reference Materials:**

- `PYPI_CREDENTIALS_SETUP.md` - Detailed credentials setup
- `BUILD_GUIDE.md` - Build instructions
- `.gitlab-ci.yml` - CI/CD pipeline definition
- `local-ci.sh` - Source code of local pipeline

**External Resources:**

- PyPI API: <https://pypi.org/help/#apitoken>
- twine docs: <https://twine.readthedocs.io/>
- GitLab CI/CD: <https://docs.gitlab.com/ee/ci/>

**Quick Links:**

- PyPI account: <https://pypi.org/account/>
- GitLab project: <https://gitlab.flavio.be/flavio/pyovf>
- Pipelines: <https://gitlab.flavio.be/flavio/pyovf/pipelines>

---

## 🎯 Common Workflows

### Test Locally Before Pushing

```bash
bash local-ci.sh all   # Full pipeline on your Mac
git push origin main   # Push after passing locally
```

### Debug Specific Python Version

```bash
bash local-ci.sh build --python 3.10
bash local-ci.sh test --python 3.10
# Fix any issues
bash local-ci.sh test --python 3.10  # Verify fix
```

### Deploy to PyPI

```bash
# Option 1: Local deployment
export PYPI_TOKEN="pypi-..."
bash local-ci.sh deploy

# Option 2: Automatic GitLab deployment
git tag v0.2.5
git push origin v0.2.5
# Check https://gitlab.flavio.be/flavio/pyovf/pipelines
```

### Rotate PyPI Token (Security)

```bash
# 1. Generate new token at https://pypi.org
# 2. Update GitLab CI/CD Variables (Settings → CI/CD → Variables)
# 3. Update local env: export PYPI_TOKEN="new-token"
# 4. Delete old token from PyPI
# 5. Verify in next deployment
```

---

**Last Updated:** January 8, 2026  
**Status:** Production Ready ✅
