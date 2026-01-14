#!/bin/bash

#╔════════════════════════════════════════════════════════════════════════════╗
#║             Multi-Architecture Build for pyovf (Linux)                     ║
#║  Builds native wheels for all Python versions on Linux                     ║
#╚════════════════════════════════════════════════════════════════════════════╝

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYOVF_DIR="${SCRIPT_DIR}"
PYTHON_VERSIONS=(3.9 3.10 3.11 3.12 3.13 3.14)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Functions
print_header() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC} $1"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
}

print_step() {
    echo -e "${BLUE}→${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Parse arguments
ARCH_FILTER=""
PYTHON_FILTER=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --python)
            PYTHON_FILTER="$2"
            shift 2
            ;;
        *)
            echo "Usage: $0 [--python VERSION]"
            echo ""
            echo "Examples:"
            echo "  $0                          # Build all available Python versions"
            echo "  $0 --python 3.11            # Build only Python 3.11"
            exit 1
            ;;
    esac
done

# Main execution
main() {
    cd "$PYOVF_DIR"
    
    print_header "pyovf Multi-Architecture Build System (Linux)"
    
    TOTAL_BUILDS=0
    SUCCESSFUL_BUILDS=0
    FAILED_BUILDS=0
    
    # Clean build artifacts
    print_step "Cleaning previous builds..."
    rm -rf build dist pyovf.egg-info 2>/dev/null || true
    print_success "Cleaned"
    
    # Find available Python installations
    print_step "Discovering Python installations..."
    declare -a PYTHON_PATHS
    
    for VERSION in "${PYTHON_VERSIONS[@]}"; do
        # Try common installation paths
        for PYTHON_CMD in "python${VERSION}" "python${VERSION%.*}" "python"; do
            if command -v "$PYTHON_CMD" &> /dev/null; then
                DETECTED_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
                if [[ "$DETECTED_VERSION" == "$VERSION" ]]; then
                    PYTHON_PATHS+=("$PYTHON_CMD")
                    print_success "Found Python $VERSION: $($PYTHON_CMD -c "import sys; print(sys.executable)")"
                    break
                fi
            fi
        done
    done
    
    if [[ ${#PYTHON_PATHS[@]} -eq 0 ]]; then
        print_error "No compatible Python versions found"
        return 1
    fi
    
    # Build for each discovered Python version
    for PYTHON in "${PYTHON_PATHS[@]}"; do
        VERSION=$($PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
        
        # Skip if version filter is set
        if [[ -n "$PYTHON_FILTER" && "$PYTHON_FILTER" != "$VERSION" ]]; then
            continue
        fi
        
        print_header "Building Python $VERSION"
        
        # Detect architecture
        DETECTED_ARCH=$($PYTHON -c "import platform; print(platform.machine())" 2>/dev/null || echo "unknown")
        
        # Install build dependencies for this Python version
        print_step "Installing build dependencies for Python $VERSION ($DETECTED_ARCH)..."
        if $PYTHON -m pip install --upgrade build setuptools setuptools-scm wheel pybind11 cmake numpy pyproject_hooks > /dev/null 2>&1; then
            print_success "Dependencies installed"
        else
            print_error "Failed to install dependencies for Python $VERSION ($DETECTED_ARCH)"
            print_error "Skipping Python $VERSION (possible compatibility issue)"
            ((TOTAL_BUILDS++))
            continue
        fi
        
        print_step "Building Python $VERSION ($DETECTED_ARCH)..."
        
        # Clean build artifacts between versions
        rm -rf build pyovf.egg-info 2>/dev/null || true
        
        if $PYTHON -m build > /dev/null 2>&1; then
            print_success "Python $VERSION ($DETECTED_ARCH) built"
            ((SUCCESSFUL_BUILDS++))
        else
            print_error "Python $VERSION ($DETECTED_ARCH) build failed"
            ((FAILED_BUILDS++))
        fi
        
        ((TOTAL_BUILDS++))
    done
    
    # Summary
    print_header "Build Summary"
    
    echo -e "${GREEN}Successful:${NC} $SUCCESSFUL_BUILDS"
    echo -e "${RED}Failed:${NC} $FAILED_BUILDS"
    echo -e "${BLUE}Total:${NC} $TOTAL_BUILDS"
    
    echo ""
    echo "Wheels generated:"
    if [[ -d "dist" ]]; then
        ls -lh dist/ | tail -n +2 | awk '{printf "  %-50s %6s\n", $9, $5}'
    else
        echo "  None (no builds completed)"
    fi
    
    echo ""
    
    # Exit with error if any builds failed
    if [[ $FAILED_BUILDS -gt 0 ]]; then
        print_error "$FAILED_BUILDS build(s) failed"
        return 1
    else
        print_success "All builds completed successfully!"
        return 0
    fi
}

# Run main
main
