# GitLab CI/CD Pipeline Protection

## Overview

The GitLab CI/CD pipeline now includes **automatic production tag validation** as the first stage. This ensures that no pipeline is launched unless the commit corresponds to a production tag.

## How It Works

### Stage Order (Updated)

```txt
1. validate     ← NEW: Production tag check (GATES ALL OTHER STAGES)
2. prepare      ← Depends on validate:production-tag
3. build        ← Depends on prepare
4. test         ← Depends on build
5. deploy       ← Depends on test
```

### Validation Job: `validate:production-tag`

**Location:** First stage in the pipeline (acts as a gate)

**Checks:**

1. ✅ Commit must have a git tag
   - ❌ Blocks if no tag exists
   - ⏸️ Pipeline stops before prepare stage

2. ✅ Tag must be a production version
   - ❌ Blocks if tag contains `.dev` suffix
   - ❌ Blocks if tag is alpha (`a1`, `a2`, etc.)
   - ❌ Blocks if tag is beta (`b1`, `b2`, etc.)
   - ❌ Blocks if tag is release candidate (`rc1`, `rc2`, etc.)

**Allowed versions:**

- ✅ `v1.0.0` (stable)
- ✅ `v2.1.3` (stable)
- ✅ `v0.2.11` (stable)

**Blocked versions:**

- ❌ `v1.0.0.dev5` (development)
- ❌ `v1.0.0a1` (alpha)
- ❌ `v1.0.0b2` (beta)
- ❌ `v1.0.0rc1` (release candidate)

## Workflow Examples

### ✅ Pushing a Production Tag (Pipeline Runs)

```bash
# Create and push a production tag
git tag v0.2.12
git push origin v0.2.12
```

**GitLab Pipeline Result:**

```txt
✓ Found tag: v0.2.12
✓ Production tag validated: v0.2.12
✓ Pipeline will proceed with all stages

→ prepare:sources (starts)
→ build:python3.9, build:python3.10, ... (start)
→ test:python3.9, test:python3.10, ... (start)
→ deploy:pypi (runs if tests pass)
→ deploy:gitlab-package (runs if tests pass)
```

### ❌ Pushing Without a Tag (Pipeline Blocked)

```bash
git push origin main
# OR
git commit -m "Fix bug" && git push
```

**GitLab Pipeline Result:**

```txt
❌ Error: No git tag found on commit abc123def
Production deployments require a git tag.
Only tagged commits trigger the pipeline.

Options:
  1. Create and push a tag to trigger the pipeline:
     git tag v1.0.0
     git push origin v1.0.0
  2. Or use the local-ci.sh script:
     bash local-ci.sh create-tag

Pipeline stopped at validate:production-tag ✗
```

### ❌ Pushing a Pre-release Tag (Pipeline Blocked)

```bash
git tag v0.2.12.dev5
git push origin v0.2.12.dev5
```

**GitLab Pipeline Result:**

```txt
❌ Error: Pre-release tag detected: v0.2.12.dev5 (.dev)
Cannot deploy development versions to production
Only stable versions (e.g., v1.0.0, v2.1.3) are allowed

Pipeline stopped at validate:production-tag ✗
```

## Security Benefits

✅ **Prevents Accidental Pipeline Runs**

- Pipeline requires explicit git tag
- No automatic builds from untagged commits
- Safe by default

✅ **Enforces Versioning Standards**

- Only stable versions reach production
- Pre-releases caught early
- Semantic versioning enforced

✅ **Clear Error Messages**

- Users know exactly why pipeline failed
- Instructions provided for fixing
- Guided toward correct workflow

## Creating a Production Tag

### Method 1: Interactive (Recommended)

```bash
cd /path/to/pyovf
bash local-ci.sh create-tag
```

This will:

- Show the last tag
- Suggest version bumps (patch/minor/major)
- Show commits since last tag
- Ask for confirmation
- Option to push to remote

### Method 2: Manual

```bash
# Create tag locally
git tag v0.2.12

# Push to GitLab (triggers pipeline)
git push origin v0.2.12
```

### Method 3: From GitLab Web UI

1. Go to **Repository → Tags**
2. Click **New tag**
3. Enter tag name: `v0.2.12`
4. Select target branch: `main`
5. Click **Create tag**

✅ This automatically triggers the pipeline!

## Integration with Deploy Scripts

The GitLab CI validation **complements** the local deployment scripts:

| Location | Validation |
| -------- | ---------- |
| `.gitlab-ci.yml` | Stage 1: `validate:production-tag` (blocks entire pipeline) |
| `deploy_pypi.sh` | Step 0: Validates before PyPI upload |
| `deploy_gitlab.sh` | Step 0: Validates before GitLab upload |
| `local-ci.sh` | Built into `stage_deploy()` and `stage_deploy_gitlab()` |

All layers ensure: **No deployment without a production tag**

## Troubleshooting

### "Pipeline didn't run but I pushed code"

**Check if you tagged the commit:**

```bash
git tag --points-at HEAD
# Should output: v0.2.12 (or your tag)
# If empty, you need to create a tag
```

### "I created a tag but pipeline still didn't run"

**Make sure you pushed the tag:**

```bash
git push origin v0.2.12
# Not just: git push origin main
```

### "I want to deploy but the tag is pre-release"

**Create a stable tag instead:**

```bash
# Instead of:
git tag v0.2.12.dev5

# Use:
git tag v0.2.12
git push origin v0.2.12
```

### "Pipeline should run but validation fails"

**Check the validation logs:**

1. Go to GitLab project
2. Select **CI/CD → Pipelines**
3. Click the pipeline run
4. Check `validate:production-tag` job logs
5. Look for the error message (provides guidance)

## YAML Structure

The validation is implemented as a GitLab job:

```yaml
validate:production-tag:
  stage: validate
  tags:
    - bash
  script:
    - |
      # Checks for production tag
      # Rejects pre-release versions
      # Exits with code 1 if validation fails
  rules:
    - when: always
```

## Comparison: Before vs After

### Before This Change

- Any push to `main` (tagged or not) could trigger pipeline
- Pre-release versions could reach production
- No gate before resource-intensive build stage

### After This Change

- ✅ Only tagged commits trigger pipeline
- ✅ Only production tags proceed
- ✅ Early validation (before any builds)
- ✅ Clear error guidance when blocked
- ✅ Resource-efficient (fails fast)

## Summary

The GitLab CI/CD pipeline is now protected by:

1. **`validate:production-tag` job** - Acts as pipeline gate
2. **Early validation** - Runs before prepare stage
3. **Production tag requirement** - Blocks untagged commits
4. **Pre-release rejection** - Blocks dev/alpha/beta/rc versions
5. **Clear feedback** - Error messages guide users

Result: No pipeline launches unless the commit has a production tag! 🔒
