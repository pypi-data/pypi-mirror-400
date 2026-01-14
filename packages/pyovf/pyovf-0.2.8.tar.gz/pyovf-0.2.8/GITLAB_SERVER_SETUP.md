# GitLab Server Setup Guide (Ubuntu 22.04.5 LTS)

## Overview

This guide covers configuring your GitLab server (`gitlab.flavio.be`) running Ubuntu 22.04.5 LTS to support automated CI/CD pipeline execution for the pyovf project.

---

## Part 1: SSH Access & Basic Setup

### Initial Access

```bash
# SSH into your server
ssh flavio@gitlab.flavio.be

# Verify OS and Python versions
lsb_release -a
python3 --version
```

Expected output:

```txt
Ubuntu 22.04.5 LTS
Python 3.10.12
```

### System Updates

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y \
    build-essential \
    python3-dev \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    cmake \
    pkg-config
```

---

## Part 2: GitLab Runner Installation

### Install GitLab Runner

```bash
# Add GitLab runner repository
curl -L https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh | sudo bash

# Install runner
sudo apt install -y gitlab-runner

# Verify installation
gitlab-runner --version
```

### Register Runner

You need a registration token from your GitLab instance.

**Get Token:**

1. Go to `gitlab.flavio.be`
2. Navigate to **Admin** → **CI/CD** → **Runners** (or **Settings** → **CI/CD** → **Runners**)
3. Copy the registration token

**Register Runner:**

```bash
# Register new runner
sudo gitlab-runner register \
  --url https://gitlab.flavio.be/ \
  --registration-token <PASTE_TOKEN_HERE> \
  --executor shell \
  --shell bash \
  --description "Ubuntu 22.04 Python Builder" \
  --tag-list "bash,ubuntu,python" \
  --run-untagged false
```

**Interactive Registration (if above doesn't work):**

```bash
sudo gitlab-runner register
# Follow prompts:
# - GitLab URL: https://gitlab.flavio.be/
# - Registration token: (paste token)
# - Description: Ubuntu 22.04 Python Builder
# - Tags: bash,ubuntu,python
# - Executor: shell
# - Shell: bash
```

### Verify Runner Registration

```bash
# Check runner status
sudo gitlab-runner status

# List registered runners
sudo gitlab-runner list

# Or check via web UI:
# https://gitlab.flavio.be/admin/runners
```

---

## Part 3: Multi-Python Environment Setup

### Install Python Versions 3.9-3.13 (via APT)

```bash
# Install deadsnakes PPA for multiple Python versions
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update

# Install Python versions (3.9-3.13 recommended for Ubuntu 22.04)
for version in 3.10 3.11 3.12 3.13; do
  sudo apt install -y "python${version}" "python${version}-dev" "python${version}-venv"
done
```

### Install Python 3.14 (via pyenv)

Python 3.14 is not yet available in Ubuntu 22.04's APT repositories. Use `pyenv` to install it:

#### Step 1: Install pyenv Dependencies

```bash
# Install build dependencies for compiling Python from source
sudo apt install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    libncurses-dev \
    zlib1g-dev \
    libbz2-dev \
    liblzma-dev \
    libreadline-dev \
    libsqlite3-dev \
    uuid-dev \
    libgdbm-dev \
    tk-dev \
    libgdbm-compat-dev
```

#### Step 2: Install pyenv

```bash
# Clone pyenv
git clone https://github.com/pyenv/pyenv.git ~/.pyenv

# Add pyenv to PATH
cat >> ~/.bashrc << 'EOF'

# pyenv configuration
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
EOF

# Reload shell
source ~/.bashrc

# Verify pyenv installation
pyenv --version
```

#### Step 3: Install Python 3.14 with pyenv

```bash
# List available Python versions
pyenv install --list | grep "^  3.14"

# Install Python 3.14 (this will compile from source, takes ~5-10 minutes)
pyenv install 3.14.2

# Set as global version
pyenv global 3.14.2

# Rehash pyenv shims (important!)
pyenv rehash

# IMPORTANT: Reload shell to activate pyenv
exec $SHELL
# Or manually:
source ~/.bashrc

# Verify installation - use the full path if pyenv is not in PATH
~/.pyenv/versions/3.14.2/bin/python3.14 --version
~/.pyenv/versions/3.14.2/bin/pip --version

# Or use pyenv to find the path
pyenv which python3.14
```

### Install Python 3.9 (via pyenv)

Use this when you want a pyenv-managed 3.9 alongside the system Pythons (or if you prefer compiling from source instead of using APT):

```bash
# Install Python 3.9 (latest patch)
pyenv install 3.9.19

# Set it available (global or local as needed)
pyenv global 3.9.19      # or: pyenv local 3.9.19
pyenv rehash

# Bootstrap pip and tooling
python3.9 -m ensurepip --upgrade
python3.9 -m pip install --upgrade pip setuptools wheel

# (Optional) Expose through /usr/local for all users
sudo ln -sf "$(pyenv root)/versions/3.9.19/bin/python3.9" /usr/bin/python3.9
sudo ln -sf "$(pyenv root)/versions/3.9.19/bin/pip3.9" /usr/bin/pip3.9

# Verify
python3.9 --version
python3.9 -m pip --version
```

#### Step 4: Configure for gitlab-runner

```bash
# Configure pyenv for gitlab-runner user
sudo -u gitlab-runner bash << 'EOF'
# Clone pyenv for gitlab-runner
git clone https://github.com/pyenv/pyenv.git ~/.pyenv

# Add to bashrc
cat >> ~/.bashrc << 'BASHRC'

# pyenv configuration
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
BASHRC

# Install Python 3.14
source ~/.bashrc
~/.pyenv/bin/pyenv install 3.14.0
~/.pyenv/bin/pyenv global 3.14.0

# Verify
python3.14 --version
EOF
```

#### Alternative: Quick Installation (All Versions)

If you want to install all versions 3.9-3.14 at once:

```bash
# Install system versions 3.10-3.13
for version in 3.10 3.11 3.12 3.13; do
  sudo apt install -y "python${version}" "python${version}-dev" "python${version}-venv"
done

# Install 3.14 with pyenv
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(~/.pyenv/bin/pyenv init -)"
~/.pyenv/bin/pyenv install 3.14.0

# Create wrapper script for pyenv Python
sudo cat > /usr/local/bin/python3.14 << 'WRAPPER'
#!/bin/bash
$HOME/.pyenv/versions/3.14.0/bin/python "$@"
WRAPPER
sudo chmod +x /usr/local/bin/python3.14

# Verify
python3.14 --version
```

### Troubleshooting pyenv Installation

**Issue: `pyenv: python3.14: command not found` but the version exists**

This is the most common issue. The error message shows:

```txt
pyenv: python3.14: command not found
The `python3.14' command exists in these Python versions:
  3.14.2
```

**Root Cause:**

- pyenv is installed but not initialized in your current shell session
- The shell hasn't been reloaded after adding pyenv to `.bashrc`

**Solution:**

```bash
# Step 1: Verify pyenv is installed
~/.pyenv/bin/pyenv versions
# Should show:
#   system
# * 3.14.2 (set by /home/user/.pyenv/version)

# Step 2: Reload shell to initialize pyenv
exec $SHELL
# Or manually source bashrc:
source ~/.bashrc

# Step 3: Verify pyenv is in PATH
which pyenv
# Should output: /home/user/.pyenv/bin/pyenv

# Step 4: Rehash pyenv shims (creates symlinks)
pyenv rehash

# Step 5: Verify python3.14 is now found
python3.14 --version
# Should output: Python 3.14.2
```

**If issue persists, use the full path:**

```bash
# Find exact location
~/.pyenv/bin/pyenv which python3.14
# Output: /home/user/.pyenv/versions/3.14.2/bin/python3.14

# Use full path
/home/user/.pyenv/versions/3.14.2/bin/python3.14 --version

# Or create a symlink
sudo ln -sf /home/user/.pyenv/versions/3.14.2/bin/python3.14 /usr/local/bin/python3.14

# Now use the symlink
python3.14 --version
```

**Issue: `pyenv: command not found`**

```bash
# Make sure PATH is updated
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"

# Verify
pyenv --version
```

Issue: Python 3.14 compilation fails

```bash
# Ensure all dependencies are installed
sudo apt install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    libncurses-dev \
    zlib1g-dev \
    libbz2-dev \
    liblzma-dev \
    libreadline-dev \
    libsqlite3-dev \
    uuid-dev \
    libgdbm-dev \
    tk-dev

# Check build logs
pyenv install -v 3.14.2  # Verbose mode shows more details

# Try again
pyenv install 3.14.2
```

**Issue: `python3.14` not in PATH for CI/CD jobs**

```bash
# Update gitlab-runner's bashrc
sudo -u gitlab-runner bash -c 'cat >> ~/.bashrc << "EOF"

# pyenv configuration
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
EOF'

# Reload gitlab-runner's shell
sudo -u gitlab-runner bash -c 'exec $SHELL'

# Create symbolic link for easier access (for all users)
sudo ln -sf /home/gitlab-runner/.pyenv/versions/3.14.2/bin/python3.14 /usr/local/bin/python3.14
sudo ln -sf /home/gitlab-runner/.pyenv/versions/3.14.2/bin/pip /usr/local/bin/pip3.14

# Verify
python3.14 --version
python3.14 -m pip --version
```

#### If You Encounter Dependency Conflicts

If you see errors like:

```txt
dpkg: error processing archive ... trying to overwrite '...', which is also in package ...
E: Unmet dependencies
```

**Quick Fix:**

```bash
# Step 1: Fix broken packages
sudo apt --fix-broken install -y

# Step 2: Clean up
sudo apt clean
sudo apt autoclean

# Step 3: Remove all conflicting Python versions
sudo apt remove -y python3.11* libpython3.11* python3.12* libpython3.12* python3.13* libpython3.13* || true

# Step 4: Update and reinstall
sudo apt update
for version in 3.10 3.11 3.12 3.13; do
  sudo apt install -y "python${version}" "python${version}-dev" "python${version}-venv"
done
```

**Why This Happens:**

- Mixing RC (release candidate) versions with stable versions
- Package cache corruption
- PPA conflicts with system Python

**Prevention:**

- Always use `apt update && apt install` in one go
- Keep PPA deadsnakes updated: `sudo apt update`
- Avoid mixing RC versions with stable versions

### Verify Python Installations

```bash
# Check available Python versions
for py in 3.9 3.10 3.11 3.12 3.13 3.14; do
  which python${py} && python${py} --version || echo "Python ${py} not found"
done
```

Expected output:

```txt
/usr/bin/python3.9
Python 3.9.x

/usr/bin/python3.10
Python 3.10.12

/usr/bin/python3.11
Python 3.11.14

/usr/bin/python3.12
Python 3.12.12

/usr/bin/python3.13
Python 3.13.11

/usr/local/bin/python3.14
Python 3.14.0
```

**Note:** Python 3.14 may be in `/usr/local/bin` if installed via pyenv, while 3.9-3.13 are in `/usr/bin`

### Install pip for Each Python Version

```bash
# Install pip, setuptools, wheel for each version (3.9-3.13)
for version in 3.9 3.10 3.11 3.12 3.13; do
  python${version} -m pip install --upgrade pip setuptools wheel 2>/dev/null || true
done

# For Python 3.14 (if installed via pyenv)
python3.14 -m pip install --upgrade pip setuptools wheel 2>/dev/null || true
```

### Install Build Dependencies Globally

```bash
# Install build tools for all versions
sudo apt install -y \
    libssl-dev \
    libffi-dev \
    libncurses-dev \
    zlib1g-dev \
    libbz2-dev \
    liblzma-dev \
    libreadline-dev \
    libsqlite3-dev \
    uuid-dev \
    libgdbm-dev \
    tk-dev

# Install CMake
sudo apt install -y cmake

# Install system-wide pip packages
sudo python3 -m pip install --upgrade \
    build \
    twine \
    setuptools-scm \
    pybind11 \
    numpy
```

---

## Part 4: GitLab Runner Configuration

### Edit Runner Config

```bash
# Edit runner configuration
sudo nano /etc/gitlab-runner/config.toml
```

### Recommended Configuration

```toml
# /etc/gitlab-runner/config.toml

concurrent = 4
check_interval = 0
shutdown_timeout = 0

[session_server]
  session_timeout = 1800

[[runners]]
  name = "Ubuntu 22.04 Python Builder"
  url = "https://gitlab.flavio.be/"
  id = 1
  token = "glrt_xxxxxxxxxxxx"  # Auto-populated
  token_expiration_time = "0001-01-01T00:00:00Z"
  tls_ca_file = ""
  tls_cert_file = ""
  tls_key_file = ""
  tls_cert_and_key_file = ""
  tls_skip_verify = false
  executor = "shell"
  builds_dir = ""
  cache_dir = ""
  shell = "bash"
  post_build_script = ""
  pre_build_script = ""
  clone_url = ""
  debug = false
  
  [runners.custom_build_dir]
    enabled = false

  [runners.cache]
    [runners.cache.s3]
      server_address = ""
      access_key = ""
      secret_key = ""
      bucket_name = ""
      insecure = false
      transfer_acceleration = false
      path_style = false
      auth_type = "IAM"

  [runners.cache.gcs]
      bucket_name = ""
      access_id = ""
      private_key_file = ""

  [runners.cache.azure]
      account_name = ""
      account_key = ""
      container_name = ""

  # Environment variables for runner
  [runners.env]
    PATH = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
    PYTHONPATH = "/usr/lib/python3/site-packages"
    PIP_CACHE_DIR = "/tmp/.pip-cache"
```

### Restart Runner

```bash
# Restart GitLab Runner
sudo systemctl restart gitlab-runner

# Check logs
sudo journalctl -u gitlab-runner -f
```

---

## Part 5: Configure PyPI Credentials (Server-Side)

### Option A: GitLab CI/CD Variables (Recommended)

#### Method 1: Web Interface

1. Go to `gitlab.flavio.be` → Your project → **Settings** → **CI/CD** → **Variables**
2. Click **Add variable**
3. Add these variables:

| Key | Value | Protected | Masked | CI/CD |
| --- | --- | --- | --- | --- |
| `PYPI_TOKEN` | `pypi-your-token-here` | ✅ Yes | ✅ Yes | ✅ Yes |
| `PYPI_USERNAME` | `__token__` | ✅ Yes | ❌ No | ✅ Yes |

#### Method 2: API

```bash
PROJECT_ID="123456"  # Get from project settings
GITLAB_URL="https://gitlab.flavio.be"
GITLAB_TOKEN="your-gitlab-admin-token"

curl --request POST \
  --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "$GITLAB_URL/api/v4/projects/$PROJECT_ID/variables" \
  --form "key=PYPI_TOKEN" \
  --form "value=pypi-AgEIcHlwaS5vcmc..." \
  --form "protected=true" \
  --form "masked=true" \
  --form "ci=true"
```

### Option B: `.pypirc` File (Less Secure)

```bash
# Create ~/.pypirc on runner machine (only for manual deploys)
# NOT RECOMMENDED for CI/CD - use GitLab CI/CD Variables instead

cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmc...
EOF

chmod 600 ~/.pypirc
```

**WARNING:** Avoid storing `.pypirc` on production servers. Use GitLab CI/CD Variables instead.

---

## Part 6: Test Pipeline Locally on Server

### Clone Repository

```bash
cd /tmp
git clone https://gitlab.flavio.be/flavio/pyovf.git
cd pyovf
```

### Run Local CI Script

```bash
# Copy local CI script to server (if not already cloned)
# It should be in the repo

bash local-ci.sh all

# Or test specific components
bash local-ci.sh prepare
bash local-ci.sh build --python 3.10
bash local-ci.sh test --python 3.10
```

### Test Deployment

```bash
# Export token
export PYPI_TOKEN="pypi-your-test-token"

# Test dry-run
bash local-ci.sh deploy

# Or with twine
twine check dist/*
twine upload --repository testpypi dist/* --verbose
```

---

## Part 7: GitLab Runner Tags & Configuration

### Update Project CI/CD

In `.gitlab-ci.yml`, ensure tags match your runner:

```yaml
# Current configuration uses tags
tags:
  - bash  # Must match runner tags

# If your runner only accepts specific tags, update to:
tags:
  - ubuntu-22.04
  - python-builder
```

### Verify Runner Availability

```bash
# Check if runner accepts jobs
sudo gitlab-runner verify

# Monitor runner logs
sudo journalctl -u gitlab-runner -f

# Test by pushing commit
cd /tmp/pyovf
git push origin main
# Watch pipeline: https://gitlab.flavio.be/flavio/pyovf/pipelines
```

---

## Part 8: Environment Variables & Path Setup

### System-Wide Python Paths

Create `/etc/profile.d/python-paths.sh`:

```bash
sudo cat > /etc/profile.d/python-paths.sh << 'EOF'
#!/bin/bash

# Python paths for CI/CD runners
export PYTHONPATH="/usr/local/lib/python3/site-packages:/usr/lib/python3/site-packages"
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# PyPI cache location
export PIP_CACHE_DIR="${HOME}/.cache/pip"
EOF

sudo chmod 755 /etc/profile.d/python-paths.sh
source /etc/profile.d/python-paths.sh
```

### Configure gitlab-runner User

```bash
# Create dedicated gitlab-runner user (usually auto-created)
id gitlab-runner

# Set shell environment for gitlab-runner
sudo -u gitlab-runner bash << 'EOF'
  cat >> ~/.bashrc << 'BASHRC'

# Python environment
export PYTHONPATH="/usr/lib/python3/site-packages"
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

# PIP configuration
export PIP_CACHE_DIR="/tmp/.pip-cache"
export PIP_DEFAULT_TIMEOUT=100
BASHRC
EOF
```

---

## Part 9: Security Hardening

### Lock Down PyPI Token

```bash
# Ensure only gitlab-runner can read token
sudo chown gitlab-runner:gitlab-runner /etc/gitlab-runner/config.toml
sudo chmod 600 /etc/gitlab-runner/config.toml

# Don't store plain text tokens
# Use GitLab CI/CD Variables instead
```

### Firewall Rules

```bash
# If using UFW firewall
sudo ufw allow 22/tcp        # SSH
sudo ufw allow 80/tcp        # HTTP
sudo ufw allow 443/tcp       # HTTPS
sudo ufw enable

# Check status
sudo ufw status
```

### SSL/TLS Certificates

```bash
# Verify GitLab server has valid SSL
curl -I https://gitlab.flavio.be

# Update CA certificates if needed
sudo update-ca-certificates
```

---

## Part 10: Monitoring & Maintenance

### Check Runner Status

```bash
# Service status
sudo systemctl status gitlab-runner

# Logs
sudo journalctl -u gitlab-runner -n 50

# Continuous logs
sudo journalctl -u gitlab-runner -f
```

### Pipeline Monitoring

```bash
# Check job queue
curl -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  https://gitlab.flavio.be/api/v4/runners

# Monitor specific runner
curl -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  https://gitlab.flavio.be/api/v4/runners/1
```

### Disk Space

```bash
# Check available space (builds go in /tmp or ~/.gitlab-runner)
df -h /tmp
df -h /home

# Clean old builds if needed
sudo rm -rf /tmp/build_*
```

### Python Package Updates

```bash
# Periodically update build dependencies
sudo python3 -m pip install --upgrade pip setuptools wheel

# For all Python versions (3.9-3.13)
for version in 3.9 3.10 3.11 3.12 3.13; do
  python${version} -m pip install --upgrade pip setuptools wheel || true
done

# For Python 3.14 (if installed via pyenv)
python3.14 -m pip install --upgrade pip setuptools wheel || true
```

---

## Part 11: Troubleshooting

### Problem: Runner won't accept jobs

**Symptoms:** Jobs pending forever, runner shows offline

**Solution:**

```bash
# Verify runner is running
sudo systemctl status gitlab-runner

# Verify tags match
sudo gitlab-runner verify

# Check firewall/network
curl -I https://gitlab.flavio.be

# Restart runner
sudo systemctl restart gitlab-runner

# Check logs
sudo journalctl -u gitlab-runner -f
```

### Problem: Python package dependency conflicts

**Symptoms:**

```txt
dpkg: error processing archive ... trying to overwrite '/usr/lib/python3.11/...'
E: Unmet dependencies
libpython3.11-stdlib : Depends: libpython3.11-minimal (= 3.11.0~rc1-1~22.04) but 3.11.14-1+jammy1 is to be installed
```

**Root Cause:**

- RC (release candidate) Python packages mixed with stable versions
- Package cache corruption
- Incomplete upgrade from deadsnakes PPA

**Solution:**

```bash
# Step 1: Fix broken packages first
sudo apt --fix-broken install -y

# Step 2: Remove ALL conflicting Python versions
sudo apt remove -y \
  python3.11* libpython3.11* \
  python3.12* libpython3.12* \
  python3.13* libpython3.13* || true

# Step 3: Clean package manager cache
sudo apt clean
sudo apt autoclean
sudo apt autoupdate

# Step 4: Fresh install
sudo apt update
for version in 3.9 3.10 3.11 3.12 3.13; do
  echo "Installing Python ${version}..."
  sudo apt install -y "python${version}" "python${version}-dev" "python${version}-venv" || {
    echo "⚠️  Python ${version} installation failed, continuing..."
  }
done

# Step 5: Verify all installations
echo "Verifying Python installations:"
for py in 3.9 3.10 3.11 3.12 3.13; do
  if command -v python${py} &> /dev/null; then
    echo "✓ $(python${py} --version)"
  else
    echo "✗ Python ${py} NOT FOUND"
  fi
done
```

**If problem persists:**

```bash
# Nuclear option: Remove deadsnakes PPA and reinstall
sudo add-apt-repository --remove ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update

# Then reinstall specific versions
for version in 3.9 3.10 3.11 3.12 3.13; do
  sudo apt install -y "python${version}" "python${version}-dev" "python${version}-venv"
done
```

**Prevention:**

- ✅ Always run: `sudo apt update && sudo apt upgrade -y` before installing new Python versions
- ✅ Never install RC versions for production (3.11.0~rc1 should be 3.11.14)
- ✅ After adding deadsnakes PPA: Always `sudo apt update` first
- ✅ Test on staging server before running on production

### Problem: PyPI upload fails with "401 Unauthorized"

**Symptoms:** `401 Client Error: Unauthorized for url: https://upload.pypi.org/legacy/`

**Solution:**

```bash
# 1. Verify token
echo "Token: ${PYPI_TOKEN:0:10}..."

# 2. Test locally
export PYPI_TOKEN="your-token"
twine upload --username __token__ --password "$PYPI_TOKEN" dist/* --dry-run

# 3. Regenerate token if expired
# Visit https://pypi.org → Account settings → API tokens
```

### Problem: Build fails with "Permission denied"

**Symptoms:** Permission errors in build output

**Solution:**

```bash
# Check gitlab-runner user permissions
id gitlab-runner

# Fix directory permissions
sudo chown -R gitlab-runner:gitlab-runner /home/gitlab-runner

# Check PIP cache permissions
sudo mkdir -p /tmp/.pip-cache
sudo chown -R gitlab-runner:gitlab-runner /tmp/.pip-cache
```

---

## Part 12: Quick Reference

### Essential Commands

```bash
# Check runner status
sudo systemctl status gitlab-runner

# View runner logs
sudo journalctl -u gitlab-runner -f

# Restart runner
sudo systemctl restart gitlab-runner

# List runners
sudo gitlab-runner list

# Verify configuration
sudo gitlab-runner verify

# Test job execution
cd /tmp/pyovf && bash local-ci.sh all
```

### Environment Setup

```bash
# Install Python versions 3.9-3.13 (via APT)
for v in 3.9 3.10 3.11 3.12 3.13; do
  sudo apt install -y python${v} python${v}-dev python${v}-venv
done

# Install Python 3.14 (via pyenv - optional)
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(~/.pyenv/bin/pyenv init -)"
~/.pyenv/bin/pyenv install 3.14.0

# Install build tools
sudo apt install -y build-essential cmake pkg-config

# Update pip for versions 3.9-3.13
for v in 3.9 3.10 3.11 3.12 3.13; do
  python${v} -m pip install --upgrade pip
done

# Update pip for version 3.14 (if installed)
python3.14 -m pip install --upgrade pip || true
```

### Credential Management

```bash
# Set PyPI token in GitLab CI/CD Variables (web UI only)
# Never store in config files or environment

# For manual testing on server (temporary)
export PYPI_TOKEN="pypi-your-token"
bash local-ci.sh deploy
```

---

## Support & References

**Ubuntu 22.04:**

- <https://releases.ubuntu.com/22.04/>
- <https://wiki.ubuntu.com/Jammy/ReleaseNotes>

**GitLab Runner:**

- <https://docs.gitlab.com/runner/>
- <https://docs.gitlab.com/runner/install/linux-repository.html>

**Python on Ubuntu:**

- <https://wiki.ubuntu.com/Python/>

**PyPI & twine:**

- <https://pypi.org/>
- <https://twine.readthedocs.io/>

---

**Last Updated:** January 8, 2026  
**Status:** Production Ready ✅
