#!/bin/bash

# Git-Auto Pro - Installation Script

set -e

echo "Installing Git-Auto Pro..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# # Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install package
pip install -e ".[dev]"

echo "✅ Installation complete!"
echo "Run 'git-auto --help' to get started"