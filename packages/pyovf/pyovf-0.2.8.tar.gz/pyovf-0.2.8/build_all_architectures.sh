#!/bin/zsh

#╔════════════════════════════════════════════════════════════════════════════╗
#║             Multi-Architecture Build for pyovf (macOS)                     ║
#║  Builds native wheels for all Python versions on both ARM64 and x86_64     ║
#╚════════════════════════════════════════════════════════════════════════════╝

# Configuration
PYOVF_DIR="/Users/flavio/ownCloud/MyPythonLib/pyovf"
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
        --arm64)
            ARCH_FILTER="arm64"
            shift
            ;;
        --x86_64)
            ARCH_FILTER="x86_64"
            shift
            ;;
        --python)
            PYTHON_FILTER="$2"
            shift 2
            ;;
        *)
            echo "Usage: $0 [--arm64|--x86_64] [--python VERSION]"
            echo ""
            echo "Examples:"
            echo "  $0                          # Build all (arm64 + x86_64)"
            echo "  $0 --arm64                  # Build only ARM64"
            echo "  $0 --x86_64                 # Build only x86_64"
            echo "  $0 --python 3.14            # Build specific version (both archs)"
            echo "  $0 --arm64 --python 3.14    # Build ARM64 Python 3.14 only"
            exit 1
            ;;
    esac
done

# Main execution
main() {
    cd "$PYOVF_DIR"
    
    print_header "pyovf Multi-Architecture Build System"
    
    TOTAL_BUILDS=0
    SUCCESSFUL_BUILDS=0
    FAILED_BUILDS=0
    
    # Clean build artifacts
    print_step "Cleaning previous builds..."
    rm -rf build dist pyovf.egg-info 2>/dev/null || true
    print_success "Cleaned"
    
    # Build matrix - zsh compatible (no associative arrays)
    for arch_spec in "arm64:/opt/homebrew/bin/python" "x86_64:/usr/local/bin/python"; do
        arch="${arch_spec%%:*}"
        PYTHON_BASE="${arch_spec##*:}"
        
        # Skip if architecture filter is set
        if [[ -n "$ARCH_FILTER" && "$ARCH_FILTER" != "$arch" ]]; then
            continue
        fi
        
        print_header "$arch Architecture"
        
        for VERSION in "${PYTHON_VERSIONS[@]}"; do
            # Skip if version filter is set
            if [[ -n "$PYTHON_FILTER" && "$PYTHON_FILTER" != "$VERSION" ]]; then
                continue
            fi
            
            PYTHON="${PYTHON_BASE}${VERSION}"
            
            # Verify Python exists
            if [[ ! -x "$PYTHON" ]]; then
                print_error "Python $VERSION not found at $PYTHON"
                ((FAILED_BUILDS++))
                ((TOTAL_BUILDS++))
                continue
            fi
            
            # Verify architecture
            DETECTED_ARCH=$($PYTHON -c "import platform; print(platform.machine())" 2>/dev/null || echo "unknown")
            
            if [[ "$DETECTED_ARCH" != "$arch" ]]; then
                print_error "Python $VERSION: expected $arch but detected $DETECTED_ARCH"
                ((FAILED_BUILDS++))
                ((TOTAL_BUILDS++))
                continue
            fi
            
            # Install build dependencies for this Python version
            print_step "Installing build dependencies for Python $VERSION ($arch)..."
            if [[ "$arch" == "x86_64" ]]; then
                arch -x86_64 $PYTHON -m pip install --upgrade build setuptools setuptools-scm wheel pybind11 cmake numpy pyproject_hooks > /dev/null 2>&1
            else
                $PYTHON -m pip install --upgrade build setuptools setuptools-scm wheel pybind11 cmake numpy pyproject_hooks > /dev/null 2>&1
            fi
            
            if [[ $? -ne 0 ]]; then
                print_error "Failed to install dependencies for Python $VERSION ($arch)"
                ((FAILED_BUILDS++))
                ((TOTAL_BUILDS++))
                continue
            fi
            
            print_step "Building Python $VERSION ($arch)..."
            
            # Clean build artifacts between versions
            rm -rf build pyovf.egg-info 2>/dev/null || true
            
            # Build with architecture enforcement
            # For x86_64, use arch command to force the correct architecture
            if [[ "$arch" == "x86_64" ]]; then
                BUILD_CMD="arch -x86_64 $PYTHON -m build"
            else
                BUILD_CMD="$PYTHON -m build"
            fi
            
            if eval "$BUILD_CMD" > /dev/null 2>&1; then
                print_success "Python $VERSION ($arch) built"
                ((SUCCESSFUL_BUILDS++))
            else
                print_error "Python $VERSION ($arch) build failed"
                ((FAILED_BUILDS++))
            fi
            
            ((TOTAL_BUILDS++))
        done
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
    echo "Architecture breakdown:"
    if [[ -d "dist" ]]; then
        ARM64_COUNT=$(ls dist/ 2>/dev/null | grep -c "arm64" || echo 0)
        X86_64_COUNT=$(ls dist/ 2>/dev/null | grep -c "x86_64" || echo 0)
        echo "  ARM64:   $ARM64_COUNT wheels"
        echo "  x86_64:  $X86_64_COUNT wheels"
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
