# PyPI Credentials Setup for GitLab CI/CD

## Overview

This guide covers setting up secure PyPI credentials on your GitLab server (`gitlab.flavio.be`) running Ubuntu 22.04.5 LTS for automated package deployment via `.gitlab-ci.yml`.

**Security Principles:**

- ✅ Never commit credentials to Git
- ✅ Use GitLab CI/CD Variables for secrets
- ✅ Use PyPI API tokens instead of passwords
- ✅ Use masked variables in CI/CD logs
- ✅ Rotate tokens regularly

---

## Part 1: Create PyPI API Token

### Step 1: Log in to PyPI

1. Visit <https://pypi.org/>
2. Sign in with your account (create one if needed)

### Step 2: Generate API Token

1. Go to **Account settings** → **API tokens**
2. Click "Add API token"
3. Set **Scope**: "Entire account" (for new packages)
4. Optional: Set **Project** limit if you only publish `pyovf`
5. Click "Create token"
6. **Copy the token immediately** - you won't see it again!

Token format looks like: `pypi-AgEIcHlwaS5vcmc...`

### Step 3: Test Token Locally (Optional)

```bash
# Create ~/.pypirc for local testing
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmc...
EOF

chmod 600 ~/.pypirc

# Test upload (dry run with testpypi first is recommended)
twine upload --repository testpypi dist/pyovf-*.whl
```

---

## Part 2: Configure GitLab CI/CD Variables

### Method 1: Web UI (Recommended)

1. Go to your GitLab project: `gitlab.flavio.be/flavio/pyovf`
2. Navigate to **Settings** → **CI/CD** → **Variables**
3. Click **Add variable**

**Add three variables:**

| Variable Name | Value | Protected | Masked | CI/CD |
| --- | --- | --- | --- | --- |
| `PYPI_TOKEN` | `pypi-AgEIcHlwaS5vcmc...` | ✅ Yes | ✅ Yes | ✅ Yes |
| `PYPI_USERNAME` | `__token__` | ✅ Yes | ❌ No | ✅ Yes |
| `TWINE_REPOSITORY_URL` | `https://upload.pypi.org/legacy/` | ❌ No | ❌ No | ✅ Yes |

**Important Settings:**

- ✅ **Protect variable**: Prevent use in unprotected branches
- ✅ **Mask variable**: Hide in CI logs (PYPI_TOKEN only)
- ✅ **Expand variable**: Convert `$VAR` to value at runtime

### Method 2: GitLab API

```bash
# Set via API (requires access token)
GITLAB_URL="https://gitlab.flavio.be"
PROJECT_ID="123456"  # Get from project settings
GITLAB_TOKEN="your-gitlab-token"

curl --request POST \
  --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "$GITLAB_URL/api/v4/projects/$PROJECT_ID/variables" \
  --form "key=PYPI_TOKEN" \
  --form "value=pypi-AgEIcHlwaS5vcmc..." \
  --form "protected=true" \
  --form "masked=true"
```

### Method 3: Group-Level Variables (Organization)

For multiple projects under the same group:

1. Go to **Group** → **Settings** → **CI/CD** → **Variables**
2. Add variables that apply to all group projects
3. Project variables override group variables

---

## Part 3: Update .gitlab-ci.yml

### Current Deploy Job (Already Correct)

```yaml
deploy:pypi:
  stage: deploy
  tags:
    - bash
  needs:
    - test:python3.9
    - test:python3.10
    - test:python3.11
    - test:python3.12
    - test:python3.13
    - test:python3.14
    - build:sdist
  script:
    - echo "Publishing to PyPI..."
    - python3 -m venv venv_deploy
    - source venv_deploy/bin/activate
    - pip install --upgrade pip twine
    - twine upload dist/* --verbose
    - deactivate
  rules:
    - if: $CI_COMMIT_TAG
      when: on_success
    - when: never
  environment:
    name: production
    url: https://pypi.org/project/pyovf/
```

### Enhanced Deploy Job (With Explicit Credentials)

If you want explicit token usage:

```yaml
deploy:pypi:
  stage: deploy
  tags:
    - bash
  needs:
    - test:python3.9
    - test:python3.10
    - test:python3.11
    - test:python3.12
    - test:python3.13
    - test:python3.14
    - build:sdist
  script:
    - echo "Publishing to PyPI..."
    - python3 -m venv venv_deploy
    - source venv_deploy/bin/activate
    - pip install --upgrade pip twine
    - |
      twine upload dist/* \
        --username "${PYPI_USERNAME}" \
        --password "${PYPI_TOKEN}" \
        --verbose \
        --skip-existing
    - deactivate
  rules:
    - if: $CI_COMMIT_TAG
      when: on_success
    - when: never
  environment:
    name: production
    url: https://pypi.org/project/pyovf/
```

### For GitLab Package Registry (Optional)

```yaml
deploy:gitlab-package:
  stage: deploy
  tags:
    - bash
  needs:
    - build:sdist
  script:
    - echo "Publishing to GitLab Package Registry..."
    - python3 -m venv venv_deploy_gitlab
    - source venv_deploy_gitlab/bin/activate
    - pip install --upgrade pip twine
    - |
      TWINE_PASSWORD=${CI_JOB_TOKEN} \
      TWINE_USERNAME=gitlab-ci-token \
      twine upload \
        --repository-url "${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/packages/pypi" \
        dist/*
    - deactivate
  rules:
    - if: $CI_COMMIT_TAG
      when: on_success
    - when: never
  environment:
    name: gitlab-packages
    url: https://gitlab.flavio.be/flavio/pyovf/-/packages
```

---

## Part 4: Test the Pipeline Locally

### Run Full Pipeline

```bash
cd /Users/flavio/ownCloud/MyPythonLib/pyovf

# Build and test everything
bash local-ci.sh all

# This runs:
# 1. prepare  - Clone ovf-rw sources
# 2. build    - Build wheels for all Python versions
# 3. test     - Test wheels on all versions
```

### Test Deploy (Dry Run)

```bash
# Simulate deploy without uploading
export PYPI_TOKEN="pypi-your-test-token"
bash local-ci.sh deploy

# Or test with twine directly
twine check dist/*
twine upload --repository testpypi dist/* --verbose
```

### Build Specific Python Version

```bash
bash local-ci.sh build --python 3.14
bash local-ci.sh test --python 3.14
```

---

## Part 5: Trigger Pipeline in GitLab

### Method 1: Tag-Based Deployment (Recommended)

Your `.gitlab-ci.yml` already has:

```yaml
rules:
  - if: $CI_COMMIT_TAG
    when: on_success
  - when: never
```

This means deploy only runs on tagged commits.

```bash
# Create and push a version tag
git tag v0.2.5
git push origin v0.2.5

# Pipeline automatically runs:
# 1. prepare
# 2. build (all Python versions)
# 3. test (all Python versions)
# 4. deploy (only if all tests pass)
```

### Method 2: Manual Trigger

1. Go to GitLab project → **CI/CD** → **Pipelines**
2. Click **Run pipeline**
3. Select branch and variables
4. Click **Run pipeline**

### Method 3: Push to Trigger

```bash
# Push to main branch to trigger build+test
git push origin main

# Pipeline runs prepare → build → test (deploy skipped, no tag)
```

---

## Part 6: Secure Credential Management

### Best Practices

✅ **DO:**

- Use API tokens instead of passwords
- Rotate tokens every 3-6 months
- Use separate tokens for different environments
- Mask sensitive variables in logs
- Protect variables to specific branches
- Use GitLab environments for deployment gates

❌ **DON'T:**

- Commit credentials to Git (`.pypirc`, `.netrc`, etc.)
- Use your PyPI password directly
- Reuse tokens across multiple services
- Log credentials to console
- Store tokens in CI script files

### Token Rotation

```bash
# Every 3 months:
# 1. Generate new token on PyPI
# 2. Update PYPI_TOKEN in GitLab CI/CD Variables
# 3. Delete old token from PyPI
# 4. Verify new token works in next deployment
```

---

## Part 7: Troubleshooting

### Problem: "401 Unauthorized" on Deploy

**Cause:** Invalid or expired token

**Solution:**

```bash
# 1. Check token format
echo $PYPI_TOKEN | grep -o "^pypi-"

# 2. Test token locally
twine upload --username __token__ --password "$PYPI_TOKEN" dist/*

# 3. Regenerate token on PyPI if needed
```

### Problem: "400 Bad Request"

**Cause:** Package already exists or invalid filename

**Solution:**

```yaml
# Add --skip-existing to ignore existing versions
twine upload dist/* --skip-existing --verbose
```

### Problem: Pipeline doesn't run deploy

**Cause:** No tag or conditions not met

**Solution:**

```bash
# Check pipeline conditions
git tag v0.2.5
git push origin v0.2.5

# Or manually trigger in UI:
# CI/CD → Pipelines → Run pipeline
```

### Problem: Variable not visible in CI logs

**Cause:** Not masked in settings

**Solution:**

1. Go to **Settings** → **CI/CD** → **Variables**
2. Check **Mask variable** for `PYPI_TOKEN`
3. Check **Protect variable** if branch protection is set
4. Redeploy to verify masking

---

## Part 8: Security Audit Checklist

Before first deployment, verify:

- [ ] PYPI_TOKEN created on PyPI.org
- [ ] PYPI_TOKEN added to GitLab CI/CD Variables
- [ ] PYPI_TOKEN is **masked** in logs
- [ ] PYPI_TOKEN is **protected** to main/release branches
- [ ] No `.pypirc` file in Git repository
- [ ] No credentials in `.gitlab-ci.yml`
- [ ] Deploy job uses `$PYPI_TOKEN` environment variable
- [ ] Deploy only runs on tags (`if: $CI_COMMIT_TAG`)
- [ ] Test jobs all pass before deploy
- [ ] Dry run with `testpypi` successful

---

## Part 9: Ubuntu 22.04 Server-Specific Notes

On `gitlab.flavio.be` running Ubuntu 22.04.5 LTS:

### Ensure Python 3.9+ Installed

```bash
# SSH to server
ssh user@gitlab.flavio.be

# Check available Python versions
which python3.9 python3.10 python3.11 python3.12 python3.13 python3.14

# If missing, install:
sudo apt update
sudo apt install python3.9 python3.10 python3.11 python3.12 python3.13

# Install build dependencies
sudo apt install build-essential python3-dev cmake
```

### Configure GitLab Runner (If Self-Hosted)

```bash
# SSH to server, then:
sudo gitlab-runner verify

# Check registered runners
sudo gitlab-runner status

# If needed, register runner:
sudo gitlab-runner register \
  --url https://gitlab.flavio.be/ \
  --registration-token <TOKEN> \
  --executor shell \
  --shell bash
```

### Environment Variables in Runner

Create `/etc/gitlab-runner/env-file`:

```bash
# Set Python paths
export PATH="/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin"
export PYTHONPATH="/usr/local/lib/python3.11/site-packages"
```

Update `/etc/gitlab-runner/config.toml`:

```toml
[[runners]]
  [runners.env]
    PATH="/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin"
    PIP_CACHE_DIR="/tmp/.pip_cache"
```

---

## Part 10: Quick Reference

### Local Testing Commands

```bash
# Full pipeline
bash local-ci.sh all

# Build only
bash local-ci.sh build

# Test only
bash local-ci.sh test

# Clean artifacts
bash local-ci.sh clean

# Specific Python version
bash local-ci.sh build --python 3.14
bash local-ci.sh test --python 3.14

# Deploy
export PYPI_TOKEN="your-token-here"
bash local-ci.sh deploy
```

### GitLab CI/CD Triggers

```bash
# Create version tag to deploy
git tag v0.2.5
git push origin v0.2.5

# View pipeline status
# https://gitlab.flavio.be/flavio/pyovf/pipelines

# View job logs
# https://gitlab.flavio.be/flavio/pyovf/-/jobs
```

### Security Commands

```bash
# Verify token format
echo "Token starts with: $(echo $PYPI_TOKEN | cut -c1-10)..."

# List variables (locally)
env | grep -i pypi

# Don't do this (security risk):
# echo $PYPI_TOKEN  # Never log the full token
# git add .pypirc   # Never commit credentials
```

---

## Support & References

**PyPI Documentation:**

- <https://pypi.org/help/#apitoken>
- <https://packaging.python.org/tutorials/packaging-projects/#uploading-your-project-to-pypi>

**GitLab CI/CD Documentation:**

- <https://docs.gitlab.com/ee/ci/variables/>
- <https://docs.gitlab.com/ee/ci/secrets/>

**twine Documentation:**

- <https://twine.readthedocs.io/en/latest/>

**Ubuntu 22.04 Python:**

- <https://wiki.ubuntu.com/Jammy/ReleaseNotes>

---

**Last Updated:** January 8, 2026  
**Author:** GitHub Copilot  
**Status:** Production Ready ✅
