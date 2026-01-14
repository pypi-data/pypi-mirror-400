#!/bin/bash

#╔════════════════════════════════════════════════════════════════════════════╗
#║           OS-Aware Build Wrapper for pyovf                                 ║
#║  Automatically selects macOS or Linux build script based on system         ║
#╚════════════════════════════════════════════════════════════════════════════╝

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OS_TYPE=$(uname -s)

if [[ "$OS_TYPE" == "Darwin" ]]; then
    # macOS
    exec "$SCRIPT_DIR/build_all_architectures.sh" "$@"
elif [[ "$OS_TYPE" == "Linux" ]]; then
    # Linux
    exec "$SCRIPT_DIR/build_all_architectures_linux.sh" "$@"
else
    echo "Unsupported operating system: $OS_TYPE"
    echo "Supported systems: macOS (Darwin), Linux"
    exit 1
fi
