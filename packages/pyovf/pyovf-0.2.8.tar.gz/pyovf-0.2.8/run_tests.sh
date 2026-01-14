#!/bin/zsh
# Run tests with coverage report
# Tests are run in-place by building the extension for the current Python version

PYOVF_DIR="/Users/flavio/ownCloud/MyPythonLib/pyovf"
cd "$PYOVF_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║ Building and Testing pyovf                                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}\n"

# Get current Python version
PYTHON=$(which python3)
PYTHON_VERSION=$($PYTHON --version | awk '{print $2}')

echo -e "${BLUE}→ Python $PYTHON_VERSION${NC}"
echo -e "${BLUE}  Path: $PYTHON${NC}\n"

# Install build dependencies
echo -e "${BLUE}→ Installing dependencies...${NC}"
$PYTHON -m pip install -q --upgrade pip setuptools wheel 2>/dev/null || true
$PYTHON -m pip install -q pytest pytest-cov numpy pybind11 cmake build setuptools-scm pyproject_hooks 2>/dev/null || true

# Build and install in editable mode
echo -e "${BLUE}→ Building extension...${NC}"
if ! $PYTHON setup.py build_ext --inplace 2>&1 | grep -q "Built target _ovf_core"; then
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Build successful${NC}\n"

# Run tests with coverage
echo -e "${BLUE}→ Running tests...${NC}\n"
$PYTHON -m pytest tests/test_pyovf.py "$@"
TEST_RESULT=$?

if [ $TEST_RESULT -eq 0 ]; then
    echo -e "\n${GREEN}✓ All tests passed!${NC}"
else
    echo -e "\n${RED}✗ Some tests failed${NC}"
fi

exit $TEST_RESULT
