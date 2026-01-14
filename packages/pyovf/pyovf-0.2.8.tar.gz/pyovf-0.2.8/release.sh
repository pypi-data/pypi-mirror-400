#!/bin/bash

# ============================================================================
# Modern pyovf Release Script
# Uses setuptools-scm for automatic versioning via git tags
# No manual version files needed!
# ============================================================================

set -e  # Exit on error

PRJ="pyovf"
PYTHON="${PYTHON:-python3.12}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Ensure we're in the right directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}${YELLOW}pyovf Modern Release Script${NC}${BLUE}                  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# Step 1: Validate git status
# ============================================================================
echo -e "${BLUE}[1/6]${NC} Checking git status..."
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${RED}❌ Error: Working directory not clean!${NC}"
    echo "   Please commit or stash changes:"
    echo "   git status"
    exit 1
fi
echo -e "${GREEN}✓${NC} Git working directory is clean"
echo ""

# ============================================================================
# Step 2: Get version from user
# ============================================================================
echo -e "${BLUE}[2/6]${NC} Enter version information..."
read -p "📦 Enter version to release (e.g., 0.2.7): " VERSION

# Validate version format (semantic versioning)
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo -e "${RED}❌ Invalid version format!${NC}"
    echo "   Use semantic versioning: MAJOR.MINOR.PATCH"
    echo "   Example: 0.2.7, 1.0.0, 2.1.3"
    exit 1
fi

read -p "📝 Enter release message: " MESSAGE
if [ -z "$MESSAGE" ]; then
    MESSAGE="Release version $VERSION"
fi

echo -e "${GREEN}✓${NC} Version: $VERSION"
echo -e "${GREEN}✓${NC} Message: $MESSAGE"
echo ""

# ============================================================================
# Step 3: Run tests
# ============================================================================
echo -e "${BLUE}[3/6]${NC} Running tests..."

# Check if there's a wheel for the current Python version
PYTHON_VERSION=$($PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_TAG=$($PYTHON -c "import sys; print(f'cp{sys.version_info.major}{sys.version_info.minor}')")

# Look for a wheel in dist/
shopt -s nullglob
WHEEL_FILES=(dist/*${PYTHON_TAG}*.whl)
shopt -u nullglob

if [[ ${#WHEEL_FILES[@]} -eq 0 ]]; then
    echo -e "${YELLOW}⚠${NC}  No wheel found for Python ${PYTHON_VERSION}"
    echo "   Skipping tests (GitLab CI will run comprehensive tests)"
    echo "   To run local tests: bash local-ci.sh build && bash local-ci.sh test"
else
    # Create a temporary venv for testing
    TEST_VENV=$(mktemp -d)/test_venv
    $PYTHON -m venv "$TEST_VENV"
    source "$TEST_VENV/bin/activate"
    pip install --quiet --upgrade pip pytest pytest-cov numpy
    pip install --quiet --force-reinstall --no-deps "${WHEEL_FILES[0]}"
    
    # Run tests from /tmp to avoid importing local source
    cd /tmp
    if pytest "${SCRIPT_DIR}/tests/" -v --tb=short; then
        echo -e "${GREEN}✓${NC} All tests passed"
    else
        echo -e "${RED}❌ Tests failed!${NC}"
        echo "   Fix the failing tests before releasing."
        deactivate
        rm -rf "$(dirname $TEST_VENV)"
        cd "$SCRIPT_DIR"
        exit 1
    fi
    cd "$SCRIPT_DIR"
    deactivate
    rm -rf "$(dirname $TEST_VENV)"
fi
echo ""

# ============================================================================
# Step 4: Create git tag
# ============================================================================
echo -e "${BLUE}[4/6]${NC} Creating git tag v$VERSION..."
git tag -a "v$VERSION" -m "$MESSAGE"
echo -e "${GREEN}✓${NC} Tag created: v$VERSION"
echo ""

# ============================================================================
# Step 5: Push tag to GitLab
# ============================================================================
echo -e "${BLUE}[5/6]${NC} Pushing tag to GitLab..."
if git push origin --tags; then
    echo -e "${GREEN}✓${NC} Tag pushed to GitLab"
else
    echo -e "${RED}❌ Failed to push tag!${NC}"
    echo "   Rolling back tag..."
    git tag -d "v$VERSION"
    exit 1
fi
echo ""

# ============================================================================
# Step 6: Build and show status
# ============================================================================
echo -e "${BLUE}[6/6]${NC} Building package..."

# Clean up any egg-info to ensure setuptools-scm gets the right version
rm -rf pyovf.egg-info src/pyovf.egg-info build/ 2>/dev/null || true

# Build the package
$PYTHON -m build
BUILD_STATUS=$?

# Clean up egg-info again (it will be recreated)
rm -rf pyovf.egg-info src/pyovf.egg-info 2>/dev/null || true

if [ $BUILD_STATUS -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Package built successfully"
    echo ""
    echo -e "${GREEN}Build artifacts:${NC}"
    ls -lh dist/ | grep "$VERSION" || ls -lh dist/ | tail -5
else
    echo -e "${YELLOW}⚠${NC}  Build completed with issues (non-critical)"
fi

# ============================================================================
# Summary
# ============================================================================
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${NC}     ${YELLOW}✅ Release Process Complete!${NC}${GREEN}                  ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📍 What happens next:${NC}"
echo ""
echo "   1️⃣  GitLab CI/CD pipeline automatically starts"
echo "       → Go to: https://gitlab.flavio.be/flavio/pyovf/-/pipelines"
echo ""
echo "   2️⃣  Pipeline will:"
echo "       • Build the package"
echo "       • Run tests"
echo "       • Upload to GitLab Package Registry"
echo ""
echo "   3️⃣  Verify the release:"
echo "       python3.12 -c \"import pyovf; print(f'Version: {pyovf.__version__}')\""
echo ""
echo "   4️⃣  Package version will be: $VERSION"
echo ""
echo -e "${BLUE}═════════════════════════════════════════════════════════════${NC}"
echo ""
