#!/bin/bash
# PyPI Deployment Script
# This script automates the complete production workflow for pyovf

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

validate_production_tag() {
    # Get tags pointing to current commit
    local tags=$(git tag --points-at HEAD 2>/dev/null || echo "")
    
    if [ -z "$tags" ]; then
        echo -e "${RED}✗ Error: No git tag found on current commit${NC}"
        echo -e "${YELLOW}Production deployments require a git tag${NC}"
        echo
        echo -e "${YELLOW}Options:${NC}"
        echo "  1. Create and push a tag:"
        echo "     bash local-ci.sh create-tag"
        echo
        echo "  2. Or manually:"
        echo "     git tag v0.x.y"
        echo "     git push origin v0.x.y"
        return 1
    fi
    
    # Check if any tag contains dev/pre-release markers
    local has_dev_tag=0
    for tag in $tags; do
        if [[ "$tag" =~ \.dev[0-9]+ ]] || [[ "$tag" =~ a[0-9]+ ]] || [[ "$tag" =~ b[0-9]+ ]] || [[ "$tag" =~ rc[0-9]+ ]]; then
            echo -e "${RED}✗ Error: Found pre-release tag: $tag${NC}"
            has_dev_tag=1
        fi
    done
    
    if [ $has_dev_tag -eq 1 ]; then
        echo -e "${RED}Cannot deploy pre-release versions to production${NC}"
        echo -e "${YELLOW}Only stable versions (e.g., v1.0.0, v2.1.3) are allowed${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✓ Production tag validated: $tags${NC}"
    return 0
}

# ============================================================================
# MAIN
# ============================================================================

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC} PyOVF PyPI Deployment Workflow                             ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}\n"

# Step 0: Validate production tag
echo -e "${GREEN}Step 0: Validating Production Tag${NC}"
validate_production_tag || {
    echo -e "\n${RED}Deployment cancelled: Not on a production tag commit${NC}"
    exit 1
}
echo

# Set required environment variables
export PYPI_TOKEN="${PYPI_TOKEN:-}"         # Your PyPI API token

# Check for PYPI_TOKEN
if [ -z "$PYPI_TOKEN" ]; then
    echo -e "${RED}Error: PYPI_TOKEN not set${NC}"
    echo -e "${YELLOW}Set your token:${NC}"
    echo "  export PYPI_TOKEN=\"pypi-AgEIcHlwaS5vcmc...\""
    echo
    echo -e "${YELLOW}Or configure ~/.pypirc:${NC}"
    echo "  [distutils]"
    echo "  index-servers = pypi"
    echo "  "
    echo "  [pypi]"
    echo "  username = __token__"
    echo "  password = pypi-AgEIcHlwaS5vcmc..."
    exit 1
fi

# Step 1: Build production wheels (exact version, no .dev)
echo -e "${GREEN}Step 1: Build Production Wheels${NC}"
bash local-ci.sh build-production
echo

# Step 2: Test production wheels
echo -e "${GREEN}Step 2: Test Production Wheels${NC}"
bash local-ci.sh test
echo

# Step 3: Deploy to PyPI
echo -e "${GREEN}Step 3: Deploy to PyPI${NC}"
bash local-ci.sh deploy
echo

echo -e "${GREEN}✓ Deployment complete!${NC}"
echo -e "\n${YELLOW}To install from PyPI:${NC}"
echo "  pip install pyovf"
