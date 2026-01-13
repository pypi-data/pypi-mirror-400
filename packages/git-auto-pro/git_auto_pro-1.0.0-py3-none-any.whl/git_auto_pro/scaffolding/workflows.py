"""CI/CD workflow generator."""

from pathlib import Path
from typing import Optional
from rich.console import Console

console = Console()


def generate_workflow(type: str, platform: str = "github") -> None:
    """Generate CI/CD workflow files."""
    console.print(f"[bold cyan]⚙️ Generating {type} workflow for {platform}[/bold cyan]\n")
    
    if platform == "github":
        generate_github_workflow(type)
    elif platform == "gitlab":
        generate_gitlab_workflow(type)
    else:
        console.print(f"[red]✗ Unsupported platform: {platform}[/red]")


def generate_github_workflow(type: str) -> None:
    """Generate GitHub Actions workflow."""
    workflows_dir = Path(".github/workflows")
    workflows_dir.mkdir(parents=True, exist_ok=True)
    
    workflows = {
        "ci": GITHUB_CI_WORKFLOW,
        "test": GITHUB_TEST_WORKFLOW,
        "cd": GITHUB_CD_WORKFLOW,
        "release": GITHUB_RELEASE_WORKFLOW,
    }
    
    content = workflows.get(type)
    if content:
        output_file = workflows_dir / f"{type}.yml"
        output_file.write_text(content)
        console.print(f"[green]✓ Workflow generated: {output_file}[/green]")
    else:
        console.print(f"[red]✗ Unknown workflow type: {type}[/red]")


GITHUB_CI_WORKFLOW = """name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', 3.11]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Lint with ruff
      run: |
        ruff check .
    
    - name: Format check with black
      run: |
        black --check .
    
    - name: Type check with mypy
      run: |
        mypy .
    
    - name: Test with pytest
      run: |
        pytest --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
"""

GITHUB_TEST_WORKFLOW = """name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: [3.8, 3.9, '3.10', 3.11]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest -v
"""

GITHUB_CD_WORKFLOW = """name: CD

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
      run: twine upload dist/*
"""

GITHUB_RELEASE_WORKFLOW = """name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Create Release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ github.ref }}
        release_name: Release ${{ github.ref }}
        draft: false
        prerelease: false
"""


def generate_gitlab_workflow(type: str) -> None:
    """Generate GitLab CI workflow."""
    content = GITLAB_CI_CONFIG
    
    Path(".gitlab-ci.yml").write_text(content)
    console.print("[green]✓ GitLab CI config generated: .gitlab-ci.yml[/green]")


GITLAB_CI_CONFIG = """stages:
  - test
  - build
  - deploy

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip

test:
  stage: test
  image: python:3.10
  script:
    - pip install -r requirements.txt
    - pip install pytest pytest-cov
    - pytest --cov=.
  coverage: '/TOTAL.*\\s+(\\d+%)$/'

build:
  stage: build
  image: python:3.10
  script:
    - pip install build
    - python -m build
  artifacts:
    paths:
      - dist/

deploy:
  stage: deploy
  image: python:3.10
  script:
    - pip install twine
    - twine upload dist/*
  only:
    - tags
"""