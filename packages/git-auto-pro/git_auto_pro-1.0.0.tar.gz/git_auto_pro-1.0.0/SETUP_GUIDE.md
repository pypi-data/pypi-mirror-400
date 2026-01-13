# 🛠️ Git-Auto Pro - Complete Setup & Development Guide

This guide will help you set up, develop, test, and publish Git-Auto Pro.

## 📋 Table of Contents

1. [Project Structure](#project-structure)
2. [Development Setup](#development-setup)
3. [Running Locally](#running-locally)
4. [Testing](#testing)
5. [Building & Publishing](#building--publishing)
6. [Development Workflow](#development-workflow)
7. [Troubleshooting](#troubleshooting)

## 📁 Project Structure

```
git-auto-pro/
├── git_auto_pro/           # Main package directory
│   ├── __init__.py         # Package initialization
│   ├── cli.py              # CLI interface (Typer commands)
│   ├── github.py           # GitHub API integration
│   ├── git_commands.py     # Git operations (GitPython)
│   ├── gitignore_manager.py #Interactive .gitignore Manager
│   ├── config.py           # Configuration management
│   ├── backup.py           # Backup/restore functionality
│   └── scaffolding/        # Project generators
│       ├── __init__.py
│       ├── project.py      # Complete project creation
│       ├── readme.py       # README generator
│       ├── license.py      # LICENSE generator
│       ├── gitignore.py    # .gitignore generator
│       ├── templates.py    # Project templates
│       ├── workflows.py    # CI/CD workflow generator
│       ├── hooks.py        # Git hooks setup
│       └── github_templates.py  # Issue/PR templates
├── tests/                  # Test directory
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_github.py
│   ├── test_git_commands.py
│   └── test_config.py
├── docs/                   # Documentation
│   ├── usage.md
│   ├── api.md
│   └── examples.md
├── pyproject.toml          # Project metadata & dependencies
├── README.md               # Main documentation
├── SETUP_GUIDE.md          # This file
├── CONTRIBUTING.md         # Contribution guidelines
├── LICENSE                 # MIT License
└── .gitignore              # Git ignore rules
```

## 🚀 Development Setup

### Prerequisites

- Python 3.8 or higher
- Git installed
- GitHub account with Personal Access Token
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
# If you haven't created the repo yet, do this first
mkdir git-auto-pro
cd git-auto-pro

# Initialize git
git init

# Create all the files (copy the code from artifacts)
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Install package in development mode with all dependencies
pip install -e ".[dev]"

# Or install dependencies manually:
pip install typer[all] requests keyring rich gitpython pyyaml questionary
pip install pytest pytest-cov black ruff mypy
```

### Step 4: Verify Installation

```bash
# Check if git-auto is available
git-auto --help

# Should show the help menu
```

## 🏃 Running Locally

### Direct Python Execution

```bash
# Run the CLI directly
python -m git_auto_pro.cli --help

# Or use the installed command
git-auto --help
```

### Testing Individual Commands

```bash
# Test login (you'll need a GitHub token)
git-auto login

# Test project creation
git-auto new test-project --no-github

# Test git commands
cd test-project
git-auto status
git-auto add --all
git-auto commit "Test commit"
```

### File Management (NEW!)
````bash
- ✅ `git-auto ignore-manager` - Interactive .gitignore manager
  - Browse all files in project
  - Select files to ignore with checkboxes
  - Use preset patterns
  - Clean tracked files
````

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=git_auto_pro --cov-report=html

# Run specific test file
pytest tests/test_cli.py

# Run specific test
pytest tests/test_cli.py::test_login

# Run with verbose output
pytest -v

# Run tests in parallel (requires pytest-xdist)
pytest -n auto
```

### Writing Tests

Create test files in `tests/` directory:

```python
# tests/test_example.py
import pytest
from git_auto_pro.config import get_config, set_config


def test_config_operations():
    """Test configuration get and set."""
    set_config("test_key", "test_value")
    assert get_config("test_key") == "test_value"


def test_cli_help(cli_runner):
    """Test CLI help command."""
    result = cli_runner.invoke(["--help"])
    assert result.exit_code == 0
    assert "git-auto" in result.output
```

### Test Coverage

```bash
# Generate coverage report
pytest --cov=git_auto_pro --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=git_auto_pro --cov-report=html
# Open htmlcov/index.html in browser
```

## 📦 Building & Publishing

### Build the Package

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# This creates:
# dist/git_auto_pro-1.0.0-py3-none-any.whl
# dist/git_auto_pro-1.0.0.tar.gz
```

### Publish to PyPI

#### Test PyPI (Recommended First)

```bash
# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ git-auto-pro
```

#### Production PyPI

```bash
# Create PyPI account at https://pypi.org/account/register/

# Create API token at https://pypi.org/manage/account/token/

# Upload to PyPI
twine upload dist/*

# Or use token authentication
twine upload --username __token__ --password pypi-YOUR_TOKEN_HERE dist/*
```

### Automate with GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install build twine
      - name: Build package
        run: python -m build
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
        run: twine upload dist/*
```

## 🔄 Development Workflow

### Making Changes

```bash
# 1. Create feature branch
git-auto switch -c feature/new-feature

# 2. Make changes to code
# Edit files...

# 3. Run tests
pytest

# 4. Format code
black git_auto_pro/
ruff check git_auto_pro/ --fix

# 5. Type check
mypy git_auto_pro/

# 6. Commit changes
git-auto commit "Add new feature"

# 7. Push to GitHub
git-auto push
```

### Code Quality Checks

```bash
# Format with Black
black git_auto_pro/ tests/

# Lint with Ruff
ruff check git_auto_pro/ tests/

# Fix linting issues
ruff check git_auto_pro/ tests/ --fix

# Type checking with mypy
mypy git_auto_pro/

# Run all checks together
black git_auto_pro/ tests/ && \
ruff check git_auto_pro/ tests/ --fix && \
mypy git_auto_pro/ && \
pytest
```

### Pre-commit Hooks

Install pre-commit hooks:

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
EOF

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Import Errors

```bash
# Make sure package is installed in development mode
pip install -e .

# Or reinstall
pip uninstall git-auto-pro
pip install -e .
```

#### 2. Command Not Found

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall package
pip install -e .
```

#### 3. GitHub Authentication Fails

```bash
# Check token validity
git-auto login

# Token requirements:
# - Must have 'repo' scope
# - Must have 'workflow' scope
# - Must not be expired
```

#### 4. Keyring Issues

```bash
# On Linux, install gnome-keyring or kwallet
sudo apt-get install gnome-keyring  # Ubuntu/Debian
sudo dnf install gnome-keyring      # Fedora

# Or use file-based keyring (less secure)
pip install keyrings.alt
```

#### 5. Git Operations Fail

```bash
# Ensure Git is installed
git --version

# Configure Git if needed
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Debug Mode

Run commands with verbose output:

```bash
# Enable debug logging
export GIT_AUTO_DEBUG=1

# Run command
git-auto status

# Python debugging
python -m pdb -m git_auto_pro.cli status
```

### Clean Installation

```bash
# Remove virtual environment
rm -rf venv/

# Remove installed package
pip uninstall git-auto-pro

# Remove cache
rm -rf **/__pycache__
rm -rf **/*.pyc
rm -rf .pytest_cache/
rm -rf .ruff_cache/
rm -rf dist/
rm -rf build/
rm -rf *.egg-info/

# Start fresh
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

## 📚 Additional Resources

### Documentation

- [Typer Documentation](https://typer.tiangolo.com/)
- [GitPython Documentation](https://gitpython.readthedocs.io/)
- [Rich Documentation](https://rich.readthedocs.io/)
- [GitHub API Documentation](https://docs.github.com/en/rest)

### Python Packaging

- [Python Packaging Guide](https://packaging.python.org/)
- [setuptools Documentation](https://setuptools.pypa.io/)
- [PyPI Help](https://pypi.org/help/)

### Testing

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)

## 🎯 Next Steps

1. **Set up your development environment**
2. **Create a GitHub repository for the project**
3. **Test all commands locally**
4. **Write additional tests**
5. **Add more features or improvements**
6. **Build and publish to PyPI**
7. **Share with the community!**

## 💡 Tips

- Always work in a virtual environment
- Write tests for new features
- Follow PEP 8 style guide
- Use type hints for better code quality
- Document your code with docstrings
- Test on multiple Python versions (3.8, 3.9, 3.10, 3.11, 3.12)
- Use GitHub Actions for CI/CD

## 🤝 Need Help?

- Open an issue on GitHub
- Check existing issues and discussions
- Read the documentation
- Contact the maintainers

---

Happy coding! 🚀