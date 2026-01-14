# Quick Commands Setup

To use `pyovf-build` from anywhere, add this line to `~/.zshrc`:

```bash
alias pyovf-build="/Users/flavio/ownCloud/MyPythonLib/pyovf/pyovf-build"
```

Or run this once:

```bash
cat >> ~/.zshrc << 'EOF'
alias pyovf-build="/Users/flavio/ownCloud/MyPythonLib/pyovf/pyovf-build"
EOF
source ~/.zshrc
```

## Available Commands

| Command | Description |
| ------- | ----------- |
| `pyovf-build env` | Check environment and build tools |
| `pyovf-build install` | Auto-install missing dependencies |
| `pyovf-build verify` | Verify wheel architectures |
| `pyovf-build build` | Build all wheels (12 total) |
| `pyovf-build build --arm64` | Build ARM64 wheels only |
| `pyovf-build build --x86_64` | Build x86_64 wheels only |
| `pyovf-build release` | Release workflow |
| `pyovf-build help` | Show help |

## Usage Examples

```bash
# Check if everything is ready
pyovf-build env

# Install missing tools
pyovf-build install

# Build wheels for your architecture only
pyovf-build build --arm64

# Verify all wheels
pyovf-build verify

# Full build for release
pyovf-build build && pyovf-build verify
```
