#!/bin/bash

echo "Installing AudioTee..."

# Check if AudioTee is already installed
if command -v audiotee &> /dev/null; then
    echo "AudioTee is already installed"
    exit 0
fi

# Clone and build AudioTee
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

git clone https://github.com/makeusabrew/audiotee.git
cd audiotee

# Build AudioTee
swift build -c release

# Install to /usr/local/bin
sudo cp .build/arm64-apple-macosx/release/audiotee /usr/local/bin/
sudo chmod +x /usr/local/bin/audiotee

echo "AudioTee installed successfully"
echo "Note: You may need to grant audio recording permissions when first running the application"

# Cleanup
rm -rf "$TEMP_DIR"
