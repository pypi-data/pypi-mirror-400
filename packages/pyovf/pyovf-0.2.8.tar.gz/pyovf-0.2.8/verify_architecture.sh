#!/bin/zsh
# Verify architecture of built wheels

PROJECT_DIR="/Users/flavio/ownCloud/MyPythonLib/pyovf"
DIST_DIR="$PROJECT_DIR/dist"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Wheel Architecture Verification       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"

if [ ! -d "$DIST_DIR" ]; then
    echo -e "${RED}✗ dist/ directory not found${NC}"
    exit 1
fi

cd "$DIST_DIR" || exit 1

# Check if any wheels exist
if [ -z "$(ls *.whl 2>/dev/null)" ]; then
    echo -e "${YELLOW}⊘ No wheels found in $DIST_DIR${NC}"
    exit 1
fi

echo -e "${BLUE}Analyzing wheels...${NC}\n"

local arm64_wheels=0
local x86_64_wheels=0
local issues=0

for wheel in *.whl; do
    if [ -f "$wheel" ]; then
        # Extract metadata from filename
        platform_tag=$(echo "$wheel" | grep -oE "macosx_[0-9_]+_(arm64|x86_64)")
        py_version=$(echo "$wheel" | grep -oE "cp3[0-9]{1,2}" | head -1)
        
        if [ -z "$platform_tag" ]; then
            echo -e "${YELLOW}⊘ $wheel - No platform tag found${NC}"
            continue
        fi
        
        # Determine architecture from filename
        if echo "$platform_tag" | grep -q "arm64"; then
            arch="arm64"
            ((arm64_wheels++))
            mark="${GREEN}✓${NC}"
        else
            arch="x86_64"
            ((x86_64_wheels++))
            mark="${GREEN}✓${NC}"
        fi
        
        # Get wheel size
        size=$(ls -lh "$wheel" | awk '{print $5}')
        
        printf "%s %-55s %s (%s)\n" "$mark" "$wheel" "$arch" "$size"
        
        # Optional: Check .so binary compatibility (requires unzip)
        if command -v unzip &> /dev/null; then
            so_files=$(unzip -l "$wheel" | grep -c "\.so$" || echo 0)
            if [ "$so_files" -gt 0 ]; then
                echo "   └─ Contains $so_files .so binary extensions"
            fi
        fi
    fi
done

echo
echo -e "${BLUE}Summary:${NC}"
echo -e "  ${GREEN}ARM64:${NC}   $arm64_wheels wheels"
echo -e "  ${GREEN}x86_64:${NC}  $x86_64_wheels wheels"
echo

# Warnings
if [ $arm64_wheels -eq 0 ] && [ $x86_64_wheels -eq 0 ]; then
    echo -e "${RED}✗ No valid wheels found!${NC}"
    exit 1
elif [ $arm64_wheels -eq 0 ] && [ $x86_64_wheels -gt 0 ]; then
    echo -e "${YELLOW}⚠ Only x86_64 wheels found (M2 recommends native arm64)${NC}"
    echo -e "  Build with: ${YELLOW}/opt/homebrew/bin/python3.14 -m build${NC}"
fi

echo
echo -e "${BLUE}Test installation:${NC}"
echo -e "  ${YELLOW}pip install dist/*.whl --force-reinstall${NC}"
echo -e "  ${YELLOW}python -c \"import pyovf; print(pyovf.__version__)\"${NC}"
