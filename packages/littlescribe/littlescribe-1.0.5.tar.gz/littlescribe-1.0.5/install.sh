#!/bin/bash

set -e

echo "Installing AI Little Scribe..."

# Install AudioTee if not present
if ! command -v audiotee &> /dev/null; then
    echo "AudioTee not found. Installing..."
    ./install_audiotee.sh
fi

# Install dependencies with uv
uv sync

# Build binary with PyInstaller
uv run hatch run build:app

# Copy binary to /usr/local/bin
sudo cp dist/littlescribe /usr/local/bin/littlescribe

echo "Installation complete! Binary installed at /usr/local/bin/littlescribe"
echo ""
echo "Note: You may need to grant audio recording permissions when first running the application."
echo ""
echo "Usage examples:"
echo "  littlescribe --language fr-FR"
echo "  littlescribe --output my_meeting.txt --summary my_meeting_summary.txt"
