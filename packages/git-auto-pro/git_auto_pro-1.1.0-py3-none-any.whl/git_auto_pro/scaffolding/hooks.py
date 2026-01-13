"""Git hooks setup module."""

from pathlib import Path
from typing import Optional
from rich.console import Console
import stat

console = Console()


def setup_hook(type: str, script: Optional[str] = None) -> None:
    """Setup Git hooks."""
    console.print(f"[bold cyan]🪝 Setting up {type} hook[/bold cyan]\n")
    
    hooks_dir = Path(".git/hooks")
    if not hooks_dir.exists():
        console.print("[red]✗ Not a git repository[/red]")
        return
    
    hook_scripts = {
        "pre-commit": PRE_COMMIT_HOOK,
        "pre-push": PRE_PUSH_HOOK,
        "commit-msg": COMMIT_MSG_HOOK,
        "post-commit": POST_COMMIT_HOOK,
    }
    
    if script:
        # Use custom script
        hook_file = hooks_dir / type
        hook_file.write_text(Path(script).read_text())
    else:
        # Use default script
        content = hook_scripts.get(type)
        if content:
            hook_file = hooks_dir / type
            hook_file.write_text(content)
        else:
            console.print(f"[red]✗ Unknown hook type: {type}[/red]")
            return
    
    # Make executable
    hook_file.chmod(hook_file.stat().st_mode | stat.S_IEXEC)
    console.print(f"[green]✓ Hook installed: {type}[/green]")


PRE_COMMIT_HOOK = """#!/bin/sh
# Pre-commit hook

echo "Running pre-commit checks..."

# Run linting
if command -v ruff &> /dev/null; then
    echo "Linting with ruff..."
    ruff check .
    if [ $? -ne 0 ]; then
        echo "Linting failed. Please fix errors before committing."
        exit 1
    fi
fi

# Run formatting check
if command -v black &> /dev/null; then
    echo "Checking formatting with black..."
    black --check .
    if [ $? -ne 0 ]; then
        echo "Code not formatted. Run 'black .' to fix."
        exit 1
    fi
fi

# Run tests
if command -v pytest &> /dev/null; then
    echo "Running tests..."
    pytest
    if [ $? -ne 0 ]; then
        echo "Tests failed. Please fix before committing."
        exit 1
    fi
fi

echo "Pre-commit checks passed!"
exit 0
"""

PRE_PUSH_HOOK = """#!/bin/sh
# Pre-push hook

echo "Running pre-push checks..."

# Run full test suite
if command -v pytest &> /dev/null; then
    echo "Running full test suite..."
    pytest -v
    if [ $? -ne 0 ]; then
        echo "Tests failed. Push aborted."
        exit 1
    fi
fi

# Run type checking
if command -v mypy &> /dev/null; then
    echo "Type checking with mypy..."
    mypy .
    if [ $? -ne 0 ]; then
        echo "Type checking failed. Push aborted."
        exit 1
    fi
fi

echo "Pre-push checks passed!"
exit 0
"""

COMMIT_MSG_HOOK = """#!/bin/sh
# Commit message hook

commit_msg_file=$1
commit_msg=$(cat "$commit_msg_file")

# Check conventional commit format
if ! echo "$commit_msg" | grep -qE "^(feat|fix|docs|style|refactor|test|chore)(\\(.+\\))?: .+"; then
    echo "Invalid commit message format."
    echo "Use: <type>(<scope>): <message>"
    echo "Types: feat, fix, docs, style, refactor, test, chore"
    exit 1
fi

exit 0
"""

POST_COMMIT_HOOK = """#!/bin/sh
# Post-commit hook

echo "Commit successful!"

# Optional: Update changelog, send notification, etc.
"""


# ============================================================================
# FILE: git_auto_pro/scaffolding/github_templates.py
# ============================================================================
"""GitHub issue and PR template generator."""

from pathlib import Path
from rich.console import Console

console = Console()


def generate_github_templates(type: str) -> None:
    """Generate GitHub issue/PR templates."""
    console.print(f"[bold cyan]📋 Generating GitHub {type} template[/bold cyan]\n")
    
    if type == "issue":
        generate_issue_templates()
    elif type == "pr":
        generate_pr_template()
    elif type == "contributing":
        generate_contributing()
    else:
        console.print(f"[red]✗ Unknown template type: {type}[/red]")


def generate_issue_templates() -> None:
    """Generate issue templates."""
    templates_dir = Path(".github/ISSUE_TEMPLATE")
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    # Bug report
    (templates_dir / "bug_report.md").write_text(BUG_REPORT_TEMPLATE)
    
    # Feature request
    (templates_dir / "feature_request.md").write_text(FEATURE_REQUEST_TEMPLATE)
    
    console.print("[green]✓ Issue templates generated[/green]")


BUG_REPORT_TEMPLATE = """---
name: Bug Report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
 - OS: [e.g. Ubuntu 22.04]
 - Python Version: [e.g. 3.10]
 - Package Version: [e.g. 1.0.0]

**Additional context**
Add any other context about the problem here.
"""

FEATURE_REQUEST_TEMPLATE = """---
name: Feature Request
about: Suggest an idea for this project
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
"""


def generate_pr_template() -> None:
    """Generate pull request template."""
    github_dir = Path(".github")
    github_dir.mkdir(exist_ok=True)
    
    (github_dir / "PULL_REQUEST_TEMPLATE.md").write_text(PR_TEMPLATE)
    console.print("[green]✓ PR template generated[/green]")


PR_TEMPLATE = """## Description
Please include a summary of the changes and the related issue.

Fixes # (issue)

## Type of change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## How Has This Been Tested?
Please describe the tests that you ran to verify your changes.

- [ ] Test A
- [ ] Test B

## Checklist:
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
"""


def generate_contributing() -> None:
    """Generate CONTRIBUTING.md."""
    Path("CONTRIBUTING.md").write_text(CONTRIBUTING_TEMPLATE)
    console.print("[green]✓ CONTRIBUTING.md generated[/green]")


CONTRIBUTING_TEMPLATE = """# Contributing Guide

Thank you for your interest in contributing!

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a new branch for your feature
4. Make your changes
5. Run tests
6. Submit a pull request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/username/project.git
cd project

# Install dependencies
pip install -r requirements-dev.txt

# Run tests
pytest
```

## Code Style

- Follow PEP 8
- Use type hints
- Write docstrings
- Run `black` for formatting
- Run `ruff` for linting

## Testing

All new features should include tests:

```bash
pytest tests/
```

## Pull Request Process

1. Update documentation
2. Add tests for new features
3. Ensure all tests pass
4. Update the CHANGELOG.md
5. Request a review

## Questions?

Feel free to open an issue for any questions!
"""