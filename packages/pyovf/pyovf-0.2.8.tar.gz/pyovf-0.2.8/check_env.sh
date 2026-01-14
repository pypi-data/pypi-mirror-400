#!/bin/zsh
# Quick environment check - use daily

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check for --install flag
AUTO_INSTALL=false
if [ "$1" = "--install" ]; then
    AUTO_INSTALL=true
fi

echo -e "${BLUE}=== Python Environment Status ===${NC}\n"

echo "Machine Type: $(uname -m)"
echo "Homebrew: $(brew --prefix)"
echo "Shell: $SHELL\n"

echo -e "${BLUE}Available Python Versions:${NC}"

for version in 3.9 3.10 3.11 3.12 3.13 3.14; do
    py_exe="/opt/homebrew/bin/python$version"
    
    if [ -f "$py_exe" ]; then
        ver=$($py_exe --version 2>&1 | awk '{print $2}')
        arch=$(file "$py_exe" | grep -o "arm64\|x86_64")
        
        if [ "$arch" = "arm64" ]; then
            mark="${GREEN}✓${NC}"
        else
            mark="${RED}✗${NC}"
        fi
        
        printf "%s python%-4s %s (%s)\n" "$mark" "$version" "$ver" "$arch"
    else
        printf "  %-16s ${YELLOW}not installed${NC}\n" "python$version"
    fi
done

echo
echo -e "${BLUE}Build Tools:${NC}"

tools=("build" "twine" "setuptools-scm" "cmake" "numpy" "pybind11")
missing_count=0

for tool in "${tools[@]}"; do
    if /opt/homebrew/bin/python3.14 -m pip list 2>/dev/null | grep -q "^${tool}"; then
        version=$(/opt/homebrew/bin/python3.14 -m pip show "$tool" 2>/dev/null | grep Version | awk '{print $2}')
        echo -e "  ${GREEN}✓${NC} $tool ($version)"
    else
        echo -e "  ${RED}✗${NC} $tool (not installed)"
        ((missing_count++))
    fi
done

# Show installation commands for missing tools
if [ $missing_count -gt 0 ]; then
    if [ "$AUTO_INSTALL" = true ]; then
        echo
        echo -e "${BLUE}Installing missing tools for all Python versions...${NC}"
        for py in 3.9 3.10 3.11 3.12 3.13 3.14; do
            echo "  Installing for Python $py..."
            /opt/homebrew/bin/python${py} -m pip install --break-system-packages \
                setuptools-scm build twine numpy pybind11 cmake -q 2>/dev/null || true
        done
        echo -e "${GREEN}✓ Installation complete${NC}"
    else
        echo
        echo -e "${YELLOW}Missing tools detected. Install with:${NC}"
        echo
        echo "  # Install for all Python versions"
        echo "  for py in 3.9 3.10 3.11 3.12 3.13 3.14; do"
        echo "    /opt/homebrew/bin/python\${py} -m pip install --break-system-packages \\"
        echo "      setuptools-scm build twine numpy pybind11 cmake"
        echo "  done"
        echo
        echo -e "${YELLOW}Or run:${NC} ./check_env.sh --install"
    fi
fi

echo
echo -e "${BLUE}Project Status:${NC}"

PROJECT_DIR="/Users/flavio/ownCloud/MyPythonLib/pyovf"
if [ -d "$PROJECT_DIR" ]; then
    cd "$PROJECT_DIR"
    
    # Git status
    if git rev-parse --git-dir > /dev/null 2>&1; then
        branch=$(git rev-parse --abbrev-ref HEAD)
        changes=$(git status --short | wc -l | xargs)
        echo -e "  Git: ${GREEN}✓${NC} branch=$branch changes=$changes"
    fi
    
    # Check for dist artifacts
    if [ -d "dist" ]; then
        wheel_count=$(ls dist/*.whl 2>/dev/null | wc -l | xargs)
        tar_count=$(ls dist/*.tar.gz 2>/dev/null | wc -l | xargs)
        echo -e "  Artifacts: ${GREEN}✓${NC} $wheel_count wheels, $tar_count tar.gz"
    fi
    
    # Check for build scripts
    for script in build_all_architectures.sh verify_architecture.sh release.sh; do
        if [ -x "$script" ]; then
            echo -e "  ${GREEN}✓${NC} $script"
        fi
    done
fi

echo
echo -e "${GREEN}Ready for development! 🚀${NC}"
