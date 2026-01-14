#!/bin/bash

#╔════════════════════════════════════════════════════════════════════════════╗
#║                    M2 Native ARM64 Setup Script                            ║
#║                   For pyovf Multi-Architecture Builds                      ║
#╚════════════════════════════════════════════════════════════════════════════╝

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC} $1"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    echo -e "${BLUE}→${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if we're on M2/M3/M4
check_architecture() {
    print_header "Step 1/4: Checking Architecture"
    
    ARCH=$(uname -m)
    if [[ "$ARCH" == "arm64" ]]; then
        print_success "Detected: Apple Silicon (ARM64)"
    else
        print_error "This script requires Apple Silicon (ARM64)"
        print_error "You have: $ARCH"
        exit 1
    fi
}

# Install native ARM64 Homebrew
install_native_homebrew() {
    print_header "Step 2/4: Setting Up Native ARM64 Homebrew"
    
    if [[ -x "/opt/homebrew/bin/brew" ]]; then
        print_success "ARM64 Homebrew already installed at /opt/homebrew"
        return
    fi
    
    print_step "Installing native ARM64 Homebrew..."
    
    # Download and install
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add to PATH for this session
    export PATH="/opt/homebrew/bin:$PATH"
    
    print_success "ARM64 Homebrew installed"
}

# Install Python versions with ARM64 native architecture
install_python_versions() {
    print_header "Step 3/4: Installing Native ARM64 Python Versions"
    
    HOMEBREW_PATH="/opt/homebrew/bin/brew"
    
    if [[ ! -x "$HOMEBREW_PATH" ]]; then
        print_error "ARM64 Homebrew not found at /opt/homebrew/bin/brew"
        exit 1
    fi
    
    PYTHON_VERSIONS=(3.9 3.10 3.11 3.12 3.13 3.14)
    
    print_step "This will install Python 3.9-3.14 (may take 10-15 minutes)..."
    
    for VERSION in "${PYTHON_VERSIONS[@]}"; do
        print_step "Installing Python $VERSION..."
        
        # Force ARM64 architecture
        arch -arm64 $HOMEBREW_PATH install python@${VERSION} 2>&1 | grep -E "Installing|Already installed|Error" || true
        
        print_success "Python $VERSION processed"
    done
    
    print_success "All Python versions installed"
}

# Verify installations
verify_installations() {
    print_header "Step 4/4: Verifying ARM64 Native Installations"
    
    HOMEBREW_PATH="/opt/homebrew/bin"
    PYTHON_VERSIONS=(3.9 3.10 3.11 3.12 3.13 3.14)
    
    ALL_GOOD=true
    
    for VERSION in "${PYTHON_VERSIONS[@]}"; do
        if [[ -x "$HOMEBREW_PATH/python$VERSION" ]]; then
            ARCH=$($HOMEBREW_PATH/python$VERSION -c "import platform; print(platform.machine())")
            if [[ "$ARCH" == "arm64" ]]; then
                print_success "Python $VERSION: ARM64 native"
            else
                print_error "Python $VERSION: $ARCH (NOT native)"
                ALL_GOOD=false
            fi
        else
            print_error "Python $VERSION: Not found at $HOMEBREW_PATH/python$VERSION"
            ALL_GOOD=false
        fi
    done
    
    if [[ "$ALL_GOOD" == true ]]; then
        print_success "All Python versions are ARM64 native!"
    else
        print_error "Some versions are not ARM64 native. Please reinstall them."
        return 1
    fi
}

# Update .zshrc to use native ARM64 Python
update_shell_config() {
    print_header "Step 5/5: Updating Shell Configuration"
    
    ZSHRC="$HOME/.zshrc"
    
    # Check if already updated
    if grep -q "# ARM64 Native Homebrew" "$ZSHRC"; then
        print_success "Shell already configured for ARM64 Homebrew"
        return
    fi
    
    print_step "Adding ARM64 Homebrew to PATH..."
    
    # Add ARM64 Homebrew to .zshrc
    cat >> "$ZSHRC" << 'EOF'

# ARM64 Native Homebrew (M2/M3/M4 Macs)
export PATH="/opt/homebrew/bin:$PATH"
export PATH="/opt/homebrew/sbin:$PATH"
export HOMEBREW_PREFIX="/opt/homebrew"

# Python 3.9-3.14 aliases (from ARM64 Homebrew)
alias python3.9="/opt/homebrew/bin/python3.9"
alias python3.10="/opt/homebrew/bin/python3.10"
alias python3.11="/opt/homebrew/bin/python3.11"
alias python3.12="/opt/homebrew/bin/python3.12"
alias python3.13="/opt/homebrew/bin/python3.13"
alias python3.14="/opt/homebrew/bin/python3.14"
EOF
    
    # Reload shell configuration
    source "$ZSHRC"
    
    print_success "Shell configuration updated"
    print_warning "Run: source ~/.zshrc"
}

# Main execution
main() {
    clear
    
    echo -e "${BLUE}"
    cat << 'EOF'
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║         M2 Native ARM64 Python Environment Setup                           ║
║                                                                            ║
║  This script will:                                                         ║
║  1. Verify you're on Apple Silicon (ARM64)                                 ║
║  2. Install native ARM64 Homebrew at /opt/homebrew                         ║
║  3. Install Python 3.9-3.14 as ARM64 native                                ║
║  4. Verify all installations are ARM64                                     ║
║  5. Configure your shell for native Python access                          ║
║                                                                            ║
║  This will produce native ARM64 wheels like:                               ║
║  - pyovf-...-macosx_14_0_arm64.whl ✓                                       ║
║  NOT Intel x86_64 wheels via Rosetta 2 emulation                           ║
║                                                                            ║
║  Time required: ~15 minutes (mostly waiting for downloads)                 ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    # Confirm before proceeding
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Setup cancelled"
        exit 0
    fi
    
    # Run setup steps
    check_architecture
    install_native_homebrew
    install_python_versions
    verify_installations
    update_shell_config
    
    print_header "Setup Complete! 🎉"
    
    echo -e "${GREEN}"
    cat << 'EOF'
Next steps:

1. Reload your shell:
   source ~/.zshrc

2. Verify Python is ARM64:
   /opt/homebrew/bin/python3.14 -c "import platform; print(platform.machine())"
   # Should print: arm64

3. Build native ARM64 wheels:
   cd /Users/flavio/ownCloud/MyPythonLib/pyovf
   /opt/homebrew/bin/python3.14 -m build
   
4. Check the wheel:
   ls -la dist/
   # Should show: pyovf-...-macosx_14_0_arm64.whl

5. For multiple architectures, see:
   cat MULTI_ARCH_GUIDE.md

EOF
    echo -e "${NC}"
}

# Run main function
main "$@"
