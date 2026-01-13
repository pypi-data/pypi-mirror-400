#!/bin/bash

# Git-Auto Pro - Test Script

set -e

echo "Running tests..."

# # Activate virtual environment
# source venv/bin/activate

# Run tests with coverage
pytest --cov=git_auto_pro --cov-report=html --cov-report=term

echo "✅ Tests complete!"
echo "Coverage report: htmlcov/index.html"