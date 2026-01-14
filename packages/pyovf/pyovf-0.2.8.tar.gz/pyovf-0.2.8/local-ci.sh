#!/bin/zsh
# Local CI/CD Pipeline Script for pyovf
# Mirrors .gitlab-ci.yml for local testing and debugging
# Usage: bash local-ci.sh [stage] [--python VERSION] [--skip-tests] [--deploy]
#
# Stages: prepare, build, test, deploy, all, clean
# Examples:
#   bash local-ci.sh all              # Run complete pipeline
#   bash local-ci.sh build            # Build wheels only
#   bash local-ci.sh test             # Test only
#   bash local-ci.sh build --python 3.14  # Build specific Python version

set -e  # Exit on error

# ============================================================================
# CONFIGURATION
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
OVF_RW_REPO="https://gitlab.flavio.be/flavio/ovf-rw.git"
OVF_RW_DIR="${PROJECT_DIR}/ovf-rw-src"
DIST_DIR="${PROJECT_DIR}/dist"
BUILD_VENV_DIR="${PROJECT_DIR}/.venv-build"
TEST_VENV_DIR="${PROJECT_DIR}/.venv-test"
DEPLOY_VENV_DIR="${PROJECT_DIR}/.venv-deploy"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Python versions to build
PYTHON_VERSIONS=(3.9 3.10 3.11 3.12 3.13 3.14)

# Optional prefix for per-version interpreters (macOS Homebrew default); leave empty to use PATH
# Example: "/opt/homebrew/bin/python" -> will try /opt/homebrew/bin/python3.11
PYTHON_BINARY=""

# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================

log_header() {
    echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC} $1"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}\n"
}

log_stage() {
    echo -e "${CYAN}→${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1" >&2
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

resolve_python_cmd() {
    local version=$1
    local candidates=()
    # If a prefix is provided, try it first
    if [ -n "$PYTHON_BINARY" ]; then
        candidates+=("${PYTHON_BINARY}${version}")
    fi
    # Fallback to PATH-discovered interpreters
    candidates+=("python${version}" "python${version%.*}")
    
    for cmd in "${candidates[@]}"; do
        if command -v "$cmd" >/dev/null 2>&1; then
            echo "$cmd"
            return 0
        fi
    done
    return 1
}

check_python() {
    local version=$1
    resolve_python_cmd "$version" >/dev/null 2>&1
}

create_venv() {
    local venv_path=$1
    local python_version=$2
    local python_cmd
    python_cmd=$(resolve_python_cmd "$python_version") || {
        log_warning "Python ${python_version} not found, skipping..."
        return 2
    }
    
    if [ -d "$venv_path" ]; then
        log_warning "Virtual environment already exists at $venv_path, skipping creation"
        return 0
    fi
    
    log_stage "Creating virtual environment at $venv_path"
    $python_cmd -m venv "$venv_path" || {
        log_error "Failed to create virtual environment"
        return 1
    }
    log_success "Virtual environment created"
}

activate_venv() {
    local venv_path=$1
    source "${venv_path}/bin/activate" || {
        log_error "Failed to activate virtual environment"
        return 1
    }
}

# ============================================================================
# TAG VALIDATION HELPER
# ============================================================================

validate_git_tag() {
    log_stage "Validating git tag for production release..."
    
    # Get current git commit
    local current_commit=$(git rev-parse HEAD 2>/dev/null || echo "")
    if [ -z "$current_commit" ]; then
        log_error "Not a git repository"
        return 1
    fi
    
    # Get tags pointing to current commit
    local tags=$(git tag --points-at HEAD 2>/dev/null || echo "")
    
    if [ -z "$tags" ]; then
        log_error "No git tag found on current commit"
        log_warning "Production deployments require a git tag"
        echo
        log_stage "To create a tag:"
        echo "  git tag v0.x.y"
        echo "  git push origin v0.x.y"
        return 1
    fi
    
    # Check if any tag contains dev/pre-release markers
    local has_dev_tag=0
    for tag in $tags; do
        if [[ "$tag" =~ \.dev[0-9]+ ]] || [[ "$tag" =~ a[0-9]+ ]] || [[ "$tag" =~ b[0-9]+ ]] || [[ "$tag" =~ rc[0-9]+ ]]; then
            log_warning "Found pre-release tag: $tag"
            has_dev_tag=1
        fi
    done
    
    if [ $has_dev_tag -eq 1 ]; then
        log_error "Cannot deploy pre-release versions to production"
        log_warning "Only stable versions (e.g., v1.0.0, v2.1.3) are allowed"
        return 1
    fi
    
    log_success "Git tag validated: $tags"
    return 0
}

# ============================================================================
# TAG CREATION HELPER
# ============================================================================

create_production_tag() {
    log_header "CREATE PRODUCTION TAG"
    
    # Get the last tag
    local last_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
    
    if [ -z "$last_tag" ]; then
        log_warning "No previous tags found"
        echo
        log_stage "Suggested first version: v0.1.0"
        read -p "Enter new tag (default: v0.1.0): " new_tag
        new_tag="${new_tag:-v0.1.0}"
    else
        # Extract version numbers from last tag
        if [[ "$last_tag" =~ ^v([0-9]+)\.([0-9]+)\.([0-9]+) ]]; then
            local major="${BASH_REMATCH[1]}"
            local minor="${BASH_REMATCH[2]}"
            local patch="${BASH_REMATCH[3]}"
            
            log_success "Last tag: $last_tag"
            echo
            log_stage "Version bump options:"
            echo "  1) Patch bump (${major}.${minor}.$((patch + 1))) - bug fixes"
            echo "  2) Minor bump (${major}.$((minor + 1)).0) - new features"
            echo "  3) Major bump ($((major + 1)).0.0) - breaking changes"
            echo "  4) Custom version"
            echo
            
            read -p "Choose option (1-4, default: 1): " choice
            choice="${choice:-1}"
            
            case $choice in
                1)
                    new_tag="v${major}.${minor}.$((patch + 1))"
                    ;;
                2)
                    new_tag="v${major}.$((minor + 1)).0"
                    ;;
                3)
                    new_tag="v$((major + 1)).0.0"
                    ;;
                4)
                    read -p "Enter custom tag: " new_tag
                    ;;
                *)
                    log_error "Invalid option"
                    return 1
                    ;;
            esac
        else
            log_warning "Could not parse version from tag: $last_tag"
            read -p "Enter new tag: " new_tag
        fi
    fi
    
    # Validate format
    if ! [[ "$new_tag" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        log_error "Invalid tag format: $new_tag"
        log_warning "Expected format: vX.Y.Z (e.g., v1.2.3)"
        return 1
    fi
    
    echo
    log_stage "Creating tag: $new_tag"
    
    # Show what's changed since last tag
    if [ -n "$last_tag" ]; then
        echo
        log_stage "Changes since $last_tag:"
        git log --oneline "${last_tag}..HEAD" | head -10 || true
    fi
    
    echo
    read -p "Confirm tag creation? (Y/n): " confirm
    confirm="${confirm:-Y}"  # Default to Y if empty
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        log_warning "Tag creation cancelled"
        return 1
    fi
    
    # Create and push tag
    log_stage "Creating tag..."
    if git tag "$new_tag"; then
        log_success "Tag created: $new_tag"
    else
        log_error "Failed to create tag"
        return 1
    fi
    
    echo
    read -p "Push tag to remote? (Y/n): " push_confirm
    push_confirm="${push_confirm:-Y}"  # Default to Y if empty
    if [ "$push_confirm" = "y" ] || [ "$push_confirm" = "Y" ]; then
        log_stage "Pushing tag..."
        if git push origin "$new_tag"; then
            log_success "Tag pushed to remote"
        else
            log_error "Failed to push tag"
            log_warning "You can push it manually with: git push origin $new_tag"
            return 1
        fi
    else
        log_warning "Tag not pushed. You can push it manually with: git push origin $new_tag"
    fi
    
    log_success "Ready for deployment!"
    return 0
}

# ============================================================================
# STAGE: PREPARE
# ============================================================================

stage_prepare() {
    log_header "PREPARE STAGE: Clone ovf-rw and prepare sources"
    
    log_stage "Cloning ovf-rw repository..."
    if [ -d "$OVF_RW_DIR" ]; then
        log_warning "ovf-rw already cloned, updating..."
        git -C "$OVF_RW_DIR" pull --depth 1 || {
            log_error "Failed to update ovf-rw"
            return 1
        }
    else
        git clone --depth 1 "$OVF_RW_REPO" "$OVF_RW_DIR" || {
            log_error "Failed to clone ovf-rw"
            return 1
        }
    fi
    log_success "ovf-rw cloned/updated"
    
    log_stage "Preparing ovf-rw sources..."
    mkdir -p "${PROJECT_DIR}/src/pyovf/ovf-rw/src_c++"
    cp "${OVF_RW_DIR}/src_c++/OVF_File.cpp" "${PROJECT_DIR}/src/pyovf/ovf-rw/src_c++/" || {
        log_error "Failed to copy OVF_File.cpp"
        return 1
    }
    cp "${OVF_RW_DIR}/src_c++/OVF_File.h" "${PROJECT_DIR}/src/pyovf/ovf-rw/src_c++/" || {
        log_error "Failed to copy OVF_File.h"
        return 1
    }
    log_success "ovf-rw sources prepared"
}

# ============================================================================
# STAGE: BUILD
# ============================================================================

build_wheel_for_version() {
    local python_version=$1
    local python_cmd
    python_cmd=$(resolve_python_cmd "$python_version") || {
        log_warning "Python ${python_version} not found, skipping..."
        return 2  # Special return code for "skipped"
    }
    local venv_path="${BUILD_VENV_DIR}_${python_version}"
    
    log_header "Building wheel for Python ${python_version}"
    
    log_stage "Setting up build environment..."
    create_venv "$venv_path" "$python_version" || {
        [ $? -eq 2 ] && return 2 || return 1
    }
    
    log_stage "Installing build dependencies..."
    activate_venv "$venv_path"
    pip install --quiet --upgrade pip setuptools wheel build || {
        log_error "Failed to install build tools"
        deactivate
        return 1
    }
    pip install --quiet pybind11 cmake numpy setuptools-scm || {
        log_error "Failed to install build dependencies"
        deactivate
        return 1
    }
    
    log_stage "Building wheel with Python ${python_version}..."
    cd "$PROJECT_DIR"
    # Use setup.py to properly build CMake extensions
    python setup.py bdist_wheel 2>&1 | grep -E "(Successfully built|error|Error)" || true
    local build_status=$?
    
    deactivate
    
    if [ $build_status -eq 0 ]; then
        log_success "Wheel built successfully for Python ${python_version}"
        return 0
    else
        log_error "Failed to build wheel for Python ${python_version}"
        return 1
    fi
}

stage_build() {
    log_header "BUILD STAGE: Build wheels for multiple Python versions"
    
    # Prepare sources first
    stage_prepare || {
        log_error "Prepare stage failed"
        return 1
    }
    
    # Create dist directory
    mkdir -p "$DIST_DIR"
    
    local target_version="${PYTHON_TARGET:-all}"
    local built=0
    local failed=0
    local skipped=0
    
    if [ "$target_version" = "all" ]; then
        for version in "${PYTHON_VERSIONS[@]}"; do
            build_wheel_for_version "$version"
            local status=$?
            if [ $status -eq 0 ]; then
                ((++built))
            elif [ $status -eq 2 ]; then
                ((++skipped))
            else
                ((++failed))
            fi
        done
    else
        build_wheel_for_version "$target_version"
        local status=$?
        if [ $status -eq 0 ]; then
            ((++built))
        elif [ $status -eq 2 ]; then
            ((++skipped))
        else
            ((++failed))
        fi
    fi
    
    log_stage "Building source distribution..."
    local venv_path="${BUILD_VENV_DIR}_sdist"
    create_venv "$venv_path" "3.14" || {
        log_warning "Could not create sdist venv, trying Python 3.12"
        create_venv "$venv_path" "3.12" || {
            log_warning "Skipping sdist build"
            return 0
        }
    }
    
    activate_venv "$venv_path"
    pip install --quiet --upgrade pip setuptools wheel build
    pip install --quiet pybind11 cmake numpy setuptools-scm
    cd "$PROJECT_DIR"
    python setup.py sdist 2>&1 | grep -E "(Successfully built|Copying|error|Error)" || true
    local sdist_status=$?
    deactivate
    
    if [ $sdist_status -eq 0 ]; then
        log_success "Source distribution built"
    else
        log_warning "Source distribution build failed"
    fi
    
    # Summary
    echo
    log_success "Build stage complete: $built built, $skipped skipped, $failed failed"
    [ $failed -eq 0 ] && return 0 || return 1
}

# ============================================================================
# STAGE: BUILD FOR PRODUCTION
# ============================================================================

stage_build_production() {
    log_header "PRODUCTION BUILD: Build wheels with exact tag version (no .dev suffix)"
    
    # Validate git tag first
    validate_git_tag || return 1
    
    # Get the current tag
    local current_tag=$(git tag --points-at HEAD 2>/dev/null | head -1)
    if [ -z "$current_tag" ]; then
        log_error "No tag found on current commit"
        return 1
    fi
    
    # Extract version from tag (remove 'v' prefix)
    local version="${current_tag#v}"
    log_success "Building for production version: $version"
    
    # Prepare sources first
    stage_prepare || {
        log_error "Prepare stage failed"
        return 1
    }
    
    # Create dist directory
    mkdir -p "$DIST_DIR"
    
    local target_version="${PYTHON_TARGET:-all}"
    local built=0
    local failed=0
    local skipped=0
    
    # Build wheels with SETUPTOOLS_SCM_PRETEND_VERSION to force exact tag version
    log_stage "Building wheels with exact version: $version"
    echo
    
    if [ "$target_version" = "all" ]; then
        for python_version in "${PYTHON_VERSIONS[@]}"; do
            build_production_wheel_for_version "$python_version" "$version"
            local status=$?
            if [ $status -eq 0 ]; then
                ((++built))
            elif [ $status -eq 2 ]; then
                ((++skipped))
            else
                ((++failed))
            fi
        done
    else
        build_production_wheel_for_version "$target_version" "$version"
        local status=$?
        if [ $status -eq 0 ]; then
            ((++built))
        elif [ $status -eq 2 ]; then
            ((++skipped))
        else
            ((++failed))
        fi
    fi
    
    # Build source distribution
    log_stage "Building source distribution with version: $version..."
    local venv_path="${BUILD_VENV_DIR}_sdist_prod"
    create_venv "$venv_path" "3.14" || {
        log_warning "Could not create sdist venv, trying Python 3.12"
        create_venv "$venv_path" "3.12" || {
            log_warning "Skipping sdist build"
            return 0
        }
    }
    
    activate_venv "$venv_path"
    pip install --quiet --upgrade pip setuptools wheel build
    pip install --quiet pybind11 cmake numpy setuptools-scm
    cd "$PROJECT_DIR"
    
    # Build with exact version
    SETUPTOOLS_SCM_PRETEND_VERSION="$version" python setup.py sdist 2>&1 | grep -E "(Successfully built|Copying|error|Error)" || true
    local sdist_status=$?
    deactivate
    
    if [ $sdist_status -eq 0 ]; then
        log_success "Source distribution built"
    else
        log_warning "Source distribution build failed"
    fi
    
    # Summary
    echo
    log_success "Production build complete: $built built, $skipped skipped, $failed failed"
    log_stage "Built wheels are ready for production deployment:"
    ls -lh "$DIST_DIR"/*.whl 2>/dev/null | awk '{print "  " $9, "(" $5 ")"}'
    [ $failed -eq 0 ] && return 0 || return 1
}

build_production_wheel_for_version() {
    local python_version=$1
    local version=$2
    local python_cmd="${PYTHON_BINARY}${python_version}"
    local venv_path="${BUILD_VENV_DIR}_${python_version}_prod"
    
    log_header "Building production wheel for Python ${python_version} (v${version})"
    
    if ! check_python "$python_version"; then
        log_warning "Python ${python_version} not found, skipping..."
        return 2  # Special return code for "skipped"
    fi
    
    log_stage "Setting up build environment..."
    create_venv "$venv_path" "$python_version" || return 1
    
    log_stage "Installing build dependencies..."
    activate_venv "$venv_path"
    pip install --quiet --upgrade pip setuptools wheel build || {
        log_error "Failed to install build tools"
        deactivate
        return 1
    }
    pip install --quiet pybind11 cmake numpy setuptools-scm || {
        log_error "Failed to install build dependencies"
        deactivate
        return 1
    }
    
    log_stage "Building production wheel with Python ${python_version}..."
    cd "$PROJECT_DIR"
    
    # Use SETUPTOOLS_SCM_PRETEND_VERSION to force exact version without .dev suffix
    SETUPTOOLS_SCM_PRETEND_VERSION="$version" python setup.py bdist_wheel 2>&1 | grep -E "(Successfully built|error|Error)" || true
    local build_status=$?
    
    deactivate
    
    if [ $build_status -eq 0 ]; then
        log_success "Production wheel built: pyovf-${version}-cp${python_version/./}*.whl"
        return 0
    else
        log_error "Failed to build wheel for Python ${python_version}"
        return 1
    fi
}

# ============================================================================
# STAGE: TEST# ============================================================================

test_wheel_for_version() {
    local python_version=$1
    local python_cmd
    python_cmd=$(resolve_python_cmd "$python_version") || {
        log_warning "Python ${python_version} not found, skipping tests..."
        return 2
    }
    local venv_path="${TEST_VENV_DIR}_${python_version}"
    
    # Clean up any egg-info that might cause editable install detection
    rm -rf "${PROJECT_DIR}/pyovf.egg-info" "${PROJECT_DIR}/src/pyovf.egg-info" 2>/dev/null || true
    
    log_stage "Setting up test environment for Python ${python_version}..."
    create_venv "$venv_path" "$python_version" || return 1
    
    log_stage "Installing test dependencies..."
    activate_venv "$venv_path"
    pip install --quiet --upgrade pip pytest pytest-cov numpy || {
        log_error "Failed to install test dependencies"
        deactivate
        return 1
    }
    
    # Try to install from wheel first, fall back to sdist
    log_stage "Installing pyovf..."
    local wheel_pattern="dist/*cp${python_version/./}*.whl"
    local sdist_pattern="dist/*.tar.gz"
    
    # Use bash-compatible glob expansion
    shopt -s nullglob 2>/dev/null || setopt NULL_GLOB 2>/dev/null || true
    local wheel_files=($wheel_pattern)
    local sdist_files=($sdist_pattern)
    shopt -u nullglob 2>/dev/null || true
    
    if [[ ${#wheel_files[@]} -gt 0 && -f "${wheel_files[0]}" ]]; then
        pip install --quiet --force-reinstall --no-deps "${wheel_files[@]}" || {
            log_error "Failed to install pyovf from wheel"
            deactivate
            return 1
        }
        # Reinstall dependencies after force-reinstall
        pip install --quiet numpy || true
    elif [[ ${#sdist_files[@]} -gt 0 && -f "${sdist_files[0]}" ]]; then
        pip install --quiet --force-reinstall "${sdist_files[@]}" || {
            log_error "Failed to install pyovf from sdist"
            deactivate
            return 1
        }
    else
        log_error "No wheel for Python ${python_version} or sdist found in dist/"
        log_warning "Available files: $(ls dist/ 2>/dev/null || echo 'none')"
        deactivate
        return 1
    fi
    
    log_stage "Running tests for Python ${python_version}..."
    # Run pytest from a temp directory to avoid importing the local pyovf/ source
    # instead of the installed package
    cd /tmp
    pytest "${PROJECT_DIR}/tests/" -v --tb=short 2>&1 | tee /tmp/test_${python_version}.log
    local test_result=${PIPESTATUS[0]}
    cd "$PROJECT_DIR"
    
    deactivate
    
    if [ $test_result -eq 0 ]; then
        log_success "Tests passed for Python ${python_version}"
        return 0
    else
        log_error "Tests failed for Python ${python_version}"
        return 1
    fi
}

stage_test() {
    log_header "TEST STAGE: Run tests for each Python version"
    
    # Check if wheels exist, if not build them
    if [ ! -d "$DIST_DIR" ] || [ -z "$(ls -A $DIST_DIR/*.whl 2>/dev/null)" ]; then
        log_warning "No wheels found, building first..."
        stage_build || {
            log_error "Failed to build wheels"
            return 1
        }
    fi
    
    local target_version="${PYTHON_TARGET:-all}"
    local passed=0
    local failed=0
    local skipped=0
    
    if [ "$target_version" = "all" ]; then
        for version in "${PYTHON_VERSIONS[@]}"; do
            test_wheel_for_version "$version"
            local status=$?
            if [ $status -eq 0 ]; then
                ((++passed))
            elif [ $status -eq 2 ]; then
                ((++skipped))
            else
                ((++failed))
            fi
        done
    else
        test_wheel_for_version "$target_version"
        local status=$?
        if [ $status -eq 0 ]; then
            ((++passed))
        elif [ $status -eq 2 ]; then
            ((++skipped))
        else
            ((++failed))
        fi
    fi
    
    # Coverage report
    if [ -f /tmp/test_3.14.log ]; then
        log_stage "Coverage summary:"
        grep "TOTAL" /tmp/test_3.14.log | head -1
    fi
    
    echo
    log_success "Test stage complete: $passed passed, $skipped skipped, $failed failed"
    [ $failed -eq 0 ] && return 0 || return 1
}

# ============================================================================
# STAGE: DEPLOY
# ============================================================================

stage_deploy() {
    log_header "DEPLOY STAGE: Publish to PyPI"
    
    # Validate git tag for production deployment
    validate_git_tag || return 1
    
    if [ ! -d "$DIST_DIR" ] || [ -z "$(ls -A $DIST_DIR 2>/dev/null)" ]; then
        log_error "No distribution files found in $DIST_DIR"
        log_warning "Run 'build' stage first"
        return 1
    fi
    
    # Check for PyPI credentials
    if [ -z "$PYPI_TOKEN" ] && [ ! -f "$HOME/.pypirc" ]; then
        log_error "PyPI credentials not found"
        log_warning "Set PYPI_TOKEN environment variable or configure ~/.pypirc"
        return 1
    fi

    # Resolve distribution artifacts (fail fast on empty glob)
    local artifacts=()
    for f in "$DIST_DIR"/*; do
        [ -e "$f" ] && artifacts+=("$f")
    done

    if [ ${#artifacts[@]} -eq 0 ]; then
        log_error "No distribution files found in $DIST_DIR"
        return 1
    fi
    
    log_stage "Setting up deploy environment..."
    local venv_path="$DEPLOY_VENV_DIR"
    create_venv "$venv_path" "3.14" || {
        log_warning "Could not create deploy venv with Python 3.14, trying 3.12"
        create_venv "$venv_path" "3.12" || {
            log_error "Failed to create deploy venv"
            return 1
        }
    }
    
    activate_venv "$venv_path"
    pip install --quiet --upgrade pip twine
    
    log_stage "Uploading to PyPI..."
    if [ -n "$PYPI_TOKEN" ]; then
        twine upload "${artifacts[@]}" \
            --username __token__ \
            --password "$PYPI_TOKEN" \
            --verbose
    else
        twine upload "${artifacts[@]}" --verbose
    fi
    
    local upload_status=$?
    deactivate
    
    if [ $upload_status -eq 0 ]; then
        log_success "Upload to PyPI successful"
        return 0
    else
        log_error "Upload to PyPI failed"
        return 1
    fi
}

# ============================================================================
# STAGE: DEPLOY TO GITLAB
# ============================================================================

stage_deploy_gitlab() {
    log_header "DEPLOY STAGE: Publish to GitLab Package Registry"
    
    # Validate git tag for production deployment
    validate_git_tag || return 1
    
    # GitLab configuration
    local GITLAB_URL="${GITLAB_URL:-https://gitlab.flavio.be}"
    local GITLAB_PROJECT_ID="${GITLAB_PROJECT_ID:-}"
    local GITLAB_TOKEN="${GITLAB_TOKEN:-}"
    
    if [ ! -d "$DIST_DIR" ] || [ -z "$(ls -A $DIST_DIR 2>/dev/null)" ]; then
        log_error "No distribution files found in $DIST_DIR"
        log_warning "Run 'build' stage first"
        return 1
    fi
    
    # Check for GitLab credentials
    if [ -z "$GITLAB_TOKEN" ]; then
        log_error "GitLab token not found"
        log_warning "Set GITLAB_TOKEN environment variable (Project or Personal Access Token with api scope)"
        return 1
    fi
    
    if [ -z "$GITLAB_PROJECT_ID" ]; then
        log_error "GitLab project ID not found"
        log_warning "Set GITLAB_PROJECT_ID environment variable (numeric project ID)"
        return 1
    fi
    
    log_stage "Setting up deploy environment..."
    local venv_path="${DEPLOY_VENV_DIR}_gitlab"
    create_venv "$venv_path" "3.14" || {
        log_warning "Could not create deploy venv with Python 3.14, trying 3.12"
        create_venv "$venv_path" "3.12" || {
            log_error "Failed to create deploy venv"
            return 1
        }
    }
    
    activate_venv "$venv_path"
    pip install --quiet --upgrade pip twine requests
    
    log_stage "Uploading to GitLab Package Registry..."
    local GITLAB_PYPI_URL="${GITLAB_URL}/api/v4/projects/${GITLAB_PROJECT_ID}/packages/pypi"
    
    # Use Python script for smart package detection and upload
    python3 << 'PYTHON_DEPLOY_SCRIPT'
import os
import sys
import requests
import subprocess
from pathlib import Path

gitlab_token = os.environ.get('GITLAB_TOKEN')
gitlab_url = os.environ.get('GITLAB_URL', 'https://gitlab.flavio.be')
project_id = os.environ.get('GITLAB_PROJECT_ID')
pypi_url = f"{gitlab_url}/api/v4/projects/{project_id}/packages/pypi"

print(f"Checking for existing packages at {pypi_url}")

# Get existing packages
headers = {"PRIVATE-TOKEN": gitlab_token}
try:
    response = requests.get(f"{pypi_url}/simple/pyovf/", headers=headers, timeout=10)
    existing_html = response.text if response.status_code == 200 else ""
except Exception as e:
    print(f"Warning: Could not fetch existing packages: {e}")
    existing_html = ""

# Check each file
dist_dir = Path("dist")
files_to_upload = []

for file_path in sorted(dist_dir.glob("*")):
    filename = file_path.name
    
    # Check if file exists in registry
    if filename in existing_html or f'href="{filename}"' in existing_html:
        print(f"  ✓ {filename} already exists, skipping")
        file_path.unlink()  # Delete the file
    else:
        print(f"  + {filename} is new, will upload")
        files_to_upload.append(str(file_path))

if files_to_upload:
    print(f"\nUploading {len(files_to_upload)} new packages...")
    # Use subprocess with environment variables for twine
    env = os.environ.copy()
    env['TWINE_USERNAME'] = 'gitlab-ci-token'
    env['TWINE_PASSWORD'] = gitlab_token
    env['TWINE_REPOSITORY_URL'] = pypi_url
    env['KEYRING_PROVIDER'] = 'fail'  # Disable keyring to prevent interactive prompts
    
    cmd = ['twine', 'upload', '--non-interactive', '--verbose'] + files_to_upload
    result = subprocess.run(cmd, env=env)
    sys.exit(result.returncode)
else:
    print("\nAll packages already exist in registry, nothing to upload")
PYTHON_DEPLOY_SCRIPT
    
    local upload_status=$?
    deactivate
    
    if [ $upload_status -eq 0 ]; then
        log_success "Upload to GitLab Package Registry successful"
        echo
        log_stage "Install with:"
        echo "  pip install pyovf --index-url ${GITLAB_URL}/api/v4/projects/${GITLAB_PROJECT_ID}/packages/pypi/simple"
        return 0
    else
        log_error "Upload to GitLab Package Registry failed"
        return 1
    fi
}

# ============================================================================
# CLEAN STAGE
# ============================================================================

stage_clean() {
    log_header "CLEAN STAGE: Remove build artifacts"
    
    log_stage "Removing dist/, build/, ovf-rw-src/, and eggs..."
    rm -rf "$PROJECT_DIR/dist" "$PROJECT_DIR/build" "$PROJECT_DIR/ovf-rw-src" "$PROJECT_DIR"/*.egg-info
    log_success "Removed distribution artifacts"
    
    log_stage "Removing __pycache__ directories..."
    find "$PROJECT_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    log_success "Cleaned __pycache__"
    
    log_stage "Removing .pyc files..."
    find "$PROJECT_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true
    log_success "Cleaned .pyc files"
    
    log_stage "Removing virtual environments..."
    rm -rf "${BUILD_VENV_DIR}"* "${TEST_VENV_DIR}"* "${DEPLOY_VENV_DIR}"*
    log_success "Cleaned virtual environments"
    
    log_header "Clean complete"
}

# ============================================================================
# MAIN
# ============================================================================

show_usage() {
    cat << 'EOF'
Local CI/CD Pipeline Script for pyovf

Usage: bash local-ci.sh [COMMAND] [OPTIONS]

COMMANDS:
  prepare          Prepare sources (clone ovf-rw)
  build            Build wheels for all Python versions (with .dev suffix)
  build-production Build production wheels (exact tag version, no .dev)
  test             Test wheels on all Python versions
  deploy           Deploy to PyPI (requires tag & dist/)
  deploy-gitlab    Deploy to GitLab Package Registry (requires tag & dist/)
  create-tag       Create and propose a new production tag
  all              Run complete pipeline (prepare → build → test)
  clean            Remove all build artifacts

OPTIONS:
  --python VERSION    Target specific Python version (e.g., 3.14)
  --skip-tests        Skip testing after build
  --help              Show this help message

EXAMPLES:
  bash local-ci.sh all                    # Full pipeline (dev wheels with .dev)
  bash local-ci.sh build --python 3.14    # Build only Python 3.14 (dev)
  bash local-ci.sh build-production       # Build production wheels (exact version)
  bash local-ci.sh test                   # Run tests only
  bash local-ci.sh create-tag             # Create a production tag interactively
  bash local-ci.sh deploy                 # Deploy current dist/ to PyPI only
  bash local-ci.sh deploy-gitlab          # Deploy current dist/ to GitLab only
  bash local-ci.sh clean                  # Clean artifacts

QUICK DEPLOY (already have wheels):
  # If you already built and tested wheels, just deploy:
  export PYPI_TOKEN="pypi-..."
  bash local-ci.sh deploy                 # Deploy to PyPI only (no build/test)
  
  # OR
  export GITLAB_TOKEN="xxxxxxxxxxxxx"
  export GITLAB_PROJECT_ID="123"
  bash local-ci.sh deploy-gitlab          # Deploy to GitLab only (no build/test)

DEPLOYMENT (PyPI):
  FULL WORKFLOW (build + test + deploy):
    bash local-ci.sh create-tag           # Create v0.x.y tag
    bash local-ci.sh build-production     # Build exact version wheels
    bash local-ci.sh test                 # Test production wheels
    export PYPI_TOKEN="pypi-..."
    bash local-ci.sh deploy               # Deploy to PyPI (validates tag)

  QUICK DEPLOY (wheels already built & tested):
    export PYPI_TOKEN="pypi-..."
    bash local-ci.sh deploy               # Deploy dist/ to PyPI only
    
  Manual approach:
    git tag v0.x.y
    git push origin v0.x.y
    export PYPI_TOKEN="pypi-..."
    bash local-ci.sh deploy

DEPLOYMENT (GitLab):
  FULL WORKFLOW (build + test + deploy):
    bash local-ci.sh create-tag           # Create v0.x.y tag
    bash local-ci.sh build-production     # Build exact version wheels
    bash local-ci.sh test                 # Test production wheels
    export GITLAB_TOKEN="xxxxxxxxxxxxx"
    export GITLAB_PROJECT_ID="123"
    bash local-ci.sh deploy-gitlab        # Deploy to GitLab (validates tag)

  QUICK DEPLOY (wheels already built & tested):
    export GITLAB_TOKEN="xxxxxxxxxxxxx"
    export GITLAB_PROJECT_ID="123"
    bash local-ci.sh deploy-gitlab        # Deploy dist/ to GitLab only
    
  To install from GitLab:
    pip install pyovf --index-url https://gitlab.flavio.be/api/v4/projects/123/packages/pypi/simple

TAG REQUIREMENTS:
  Production deployments require a git tag on the current commit:
  - Valid: v1.0.0, v2.1.3, v0.5.0 (stable versions)
  - Invalid: v1.0.0.dev5, v2.1.0a1, v2.1.0b2, v2.1.0rc1 (pre-releases)
  
  Pre-release versions can be deployed with release.sh for testing purposes

ENVIRONMENT:
  PYTHON_TARGET      Target Python version (default: all)
  PYPI_TOKEN         PyPI API token for deployment
  GITLAB_TOKEN       GitLab Personal/Project Access Token (api scope)
  GITLAB_PROJECT_ID  GitLab numeric project ID
  GITLAB_URL         GitLab instance URL (default: https://gitlab.flavio.be)

EOF
}

main() {
    # Parse arguments
    local command="${1:-all}"
    shift || true
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --python)
                PYTHON_TARGET="$2"
                shift 2
                ;;
            --skip-tests)
                SKIP_TESTS=1
                shift
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    case $command in
        prepare)
            stage_prepare
            ;;
        build)
            stage_build
            ;;
        build-production)
            stage_build_production
            ;;
        test)
            stage_test
            ;;
        deploy)
            stage_deploy
            ;;
        deploy-gitlab)
            stage_deploy_gitlab
            ;;
        create-tag)
            create_production_tag
            ;;
        all)
            stage_prepare || exit 1
            stage_build || exit 1
            [ -z "$SKIP_TESTS" ] && stage_test || true
            ;;
        clean)
            stage_clean
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            log_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

main "$@"
