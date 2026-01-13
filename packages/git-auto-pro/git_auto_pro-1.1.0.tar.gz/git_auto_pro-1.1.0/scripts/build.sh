#!/bin/bash

# Git-Auto Pro - Build Script

set -e

echo "Building Git-Auto Pro..."

# # Activate virtual environment
# source venv/bin/activate

# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Run tests first
echo "Running tests..."
pytest

# Format and lint
echo "Formatting code..."
black git_auto_pro/ tests/
ruff check git_auto_pro/ tests/ --fix

# Type check
echo "Type checking..."
mypy git_auto_pro/

# Build package
echo "Building package..."
python -m build

echo "✅ Build complete!"
echo "Distribution files in dist/"