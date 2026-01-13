#!/bin/bash

set -e

PLATFORM=${1:-$(uname -s | tr '[:upper:]' '[:lower:]')}

echo "Building littlescribe binary for platform: $PLATFORM"

# Install dependencies
uv sync

# Build binary based on platform
case $PLATFORM in
    "darwin"|"macos")
        uv run hatch run build:macos
        ;;
    "linux")
        uv run hatch run build:linux
        ;;
    "windows"|"win32")
        uv run hatch run build:windows
        ;;
    *)
        echo "Building for current platform..."
        uv run hatch run build:app
        ;;
esac

echo "Binary built successfully in dist/ directory"