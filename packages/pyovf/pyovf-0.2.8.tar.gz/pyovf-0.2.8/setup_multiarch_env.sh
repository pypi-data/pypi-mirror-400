#!/bin/zsh
# One-time setup for multi-architecture Python development on M2

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  M2 Multi-Architecture Setup           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"

# Check if running on Apple Silicon
if [ "$(uname -m)" != "arm64" ]; then
    echo -e "${RED}✗ This script is designed for Apple Silicon (M2/M3/etc) Macs${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Detected: Apple Silicon (arm64)${NC}\n"

# Step 1: Update Homebrew
echo -e "${BLUE}Step 1/5: Updating Homebrew...${NC}"
brew update > /dev/null 2>&1
echo -e "${GREEN}✓ Homebrew updated${NC}\n"

# Step 2: Install Python versions
echo -e "${BLUE}Step 2/5: Installing Python 3.9-3.14 (ARM64 native)...${NC}"
echo -e "  This may take 5-10 minutes...\n"

for py_version in 3.9 3.10 3.11 3.12 3.13 3.14; do
    echo -n "  Installing python@$py_version... "
    if arch -arm64 brew install python@$py_version > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${YELLOW}⚠ (may already be installed)${NC}"
    fi
done

echo -e "${GREEN}✓ All Python versions installed${NC}\n"

# Step 3: Verify installations
echo -e "${BLUE}Step 3/5: Verifying Python installations...${NC}\n"

all_ok=true
for py_version in 3.9 3.10 3.11 3.12 3.13 3.14; do
    py_exe="/opt/homebrew/bin/python$py_version"
    
    if [ ! -f "$py_exe" ]; then
        echo -e "${RED}  ✗ python$py_version not found${NC}"
        all_ok=false
        continue
    fi
    
    version=$($py_exe --version 2>&1)
    arch=$(file "$py_exe" | grep -o "arm64\|x86_64")
    
    if [ "$arch" = "arm64" ]; then
        echo -e "${GREEN}  ✓${NC} $py_version ($arch) - $version"
    else
        echo -e "${RED}  ✗${NC} $py_version ($arch) - expected arm64"
        all_ok=false
    fi
done

if [ "$all_ok" = false ]; then
    echo -e "\n${RED}✗ Some Python versions are not ARM64 native${NC}"
    echo -e "  Reinstall with: ${YELLOW}arch -arm64 brew install python@3.X${NC}"
    exit 1
fi

echo -e "\n${GREEN}✓ All Python versions are ARM64 native${NC}\n"

# Step 4: Install build tools
echo -e "${BLUE}Step 4/5: Installing build tools...${NC}"
echo -n "  Installing pip packages... "
/opt/homebrew/bin/python3.14 -m pip install --upgrade pip build twine setuptools-scm > /dev/null 2>&1
echo -e "${GREEN}✓${NC}\n"

# Step 5: Setup shell aliases
echo -e "${BLUE}Step 5/5: Creating shell aliases...${NC}\n"

SHELL_RC="$HOME/.zshrc"

# Backup existing config
if [ -f "$SHELL_RC" ]; then
    cp "$SHELL_RC" "$SHELL_RC.backup.$(date +%s)"
fi

# Add aliases if not already present
if ! grep -q "alias py314=" "$SHELL_RC" 2>/dev/null; then
    cat >> "$SHELL_RC" << 'EOF'

# =================================================================
# pyovf Development Aliases (Added by setup_multiarch_env.sh)
# =================================================================

# Direct access to ARM64 Homebrew Pythons
alias py39="/opt/homebrew/bin/python3.9"
alias py310="/opt/homebrew/bin/python3.10"
alias py311="/opt/homebrew/bin/python3.11"
alias py312="/opt/homebrew/bin/python3.12"
alias py313="/opt/homebrew/bin/python3.13"
alias py314="/opt/homebrew/bin/python3.14"

# Convenience functions
check-python() {
    echo "Python Architecture Check:"
    for py in py39 py310 py311 py312 py313 py314; do
        printf "  %-10s " "$py:"
        $py -c "import platform; print(platform.machine())"
    done
}

# Build all pyovf wheels at once
build-pyovf() {
    cd /Users/flavio/ownCloud/MyPythonLib/pyovf
    ./build_all_architectures.sh "$@"
}

# Verify wheel architectures
verify-pyovf() {
    cd /Users/flavio/ownCloud/MyPythonLib/pyovf
    ./verify_architecture.sh
}
EOF
    
    echo -e "${GREEN}✓ Aliases added to $SHELL_RC${NC}"
else
    echo -e "${YELLOW}⊘ Aliases already present in $SHELL_RC${NC}"
fi

echo
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Setup Complete! ✓                     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"

echo -e "${BLUE}Next steps:${NC}"
echo -e "  1. Reload shell config:"
echo -e "     ${YELLOW}source ~/.zshrc${NC}"
echo -e "\n  2. Verify setup:"
echo -e "     ${YELLOW}check-python${NC}"
echo -e "\n  3. Build all wheels:"
echo -e "     ${YELLOW}cd /Users/flavio/ownCloud/MyPythonLib/pyovf${NC}"
echo -e "     ${YELLOW}./build_all_architectures.sh${NC}"
echo -e "\n  4. Verify wheels:"
echo -e "     ${YELLOW}./verify_architecture.sh${NC}"
echo -e "\n  5. Create release:"
echo -e "     ${YELLOW}./release.sh${NC}\n"

echo -e "${BLUE}Available commands (after sourcing .zshrc):${NC}"
echo -e "  ${YELLOW}py39, py310, py311, py312, py313, py314${NC} - Direct Python access"
echo -e "  ${YELLOW}check-python${NC} - Verify all Pythons are ARM64"
echo -e "  ${YELLOW}build-pyovf${NC} - Build all wheels"
echo -e "  ${YELLOW}verify-pyovf${NC} - Verify wheel architectures\n"
