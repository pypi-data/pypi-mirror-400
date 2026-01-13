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
        console.print("[yellow]Available types: issue, pr, contributing[/yellow]")


def generate_issue_templates() -> None:
    """Generate issue templates."""
    templates_dir = Path(".github/ISSUE_TEMPLATE")
    templates_dir.mkdir(parents=True, exist_ok=True)
    

    (templates_dir / "bug_report.md").write_text(BUG_REPORT_TEMPLATE)
    console.print(f"[green]✓ Created: {templates_dir / 'bug_report.md'}[/green]")
    

    (templates_dir / "feature_request.md").write_text(FEATURE_REQUEST_TEMPLATE)
    console.print(f"[green]✓ Created: {templates_dir / 'feature_request.md'}[/green]")
    

    (templates_dir / "config.yml").write_text(ISSUE_CONFIG_TEMPLATE)
    console.print(f"[green]✓ Created: {templates_dir / 'config.yml'}[/green]")
    
    console.print("\n[bold green]✓ Issue templates generated successfully![/bold green]")


BUG_REPORT_TEMPLATE = """---
name: Bug Report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

## 🐛 Bug Description
A clear and concise description of what the bug is.

## 📋 To Reproduce
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## ✅ Expected Behavior
A clear and concise description of what you expected to happen.

## 📸 Screenshots
If applicable, add screenshots to help explain your problem.

## 💻 Environment
**Desktop (please complete the following information):**
 - OS: [e.g. Ubuntu 22.04, macOS 13.0, Windows 11]
 - Python Version: [e.g. 3.10.5]
 - Package Version: [e.g. 1.0.0]
 - Git Version: [e.g. 2.40.0]

**Additional Environment Details:**
```bash
# Output of: git-auto version
# Output of: python --version
# Output of: git --version
```

## 📝 Additional Context
Add any other context about the problem here.

## 🔍 Logs
If applicable, add relevant logs or error messages:
```
Paste error logs here
```

## ✔️ Possible Solution
If you have suggestions on how to fix the bug, please describe them here.
"""


FEATURE_REQUEST_TEMPLATE = """---
name: Feature Request
about: Suggest an idea for this project
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

## 🚀 Feature Description
A clear and concise description of the feature you'd like to see.

## 🎯 Problem Statement
**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is. 
Ex. I'm always frustrated when [...]

## 💡 Proposed Solution
**Describe the solution you'd like**
A clear and concise description of what you want to happen.

```bash
# Example of how the feature would be used
git-auto new-command --option value
```

## 🔄 Alternatives Considered
**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

## 📊 Additional Context
Add any other context, mockups, or screenshots about the feature request here.

## ✅ Acceptance Criteria
What needs to be true for this feature to be considered complete?
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## 🎨 Would you like to implement this feature?
- [ ] Yes, I'd like to work on this
- [ ] No, just suggesting
- [ ] Need guidance on how to implement

## 📌 Priority
How important is this feature to you?
- [ ] Critical - Blocking my work
- [ ] High - Would significantly improve my workflow
- [ ] Medium - Nice to have
- [ ] Low - Minor improvement
"""


ISSUE_CONFIG_TEMPLATE = """blank_issues_enabled: false
contact_links:
  - name: 💬 Discussions
    url: https://github.com/yourusername/git-auto-pro/discussions
    about: Ask questions and discuss ideas with the community
  - name: 📚 Documentation
    url: https://github.com/yourusername/git-auto-pro#readme
    about: Read the documentation for usage guides and examples
"""


def generate_pr_template() -> None:
    """Generate pull request template."""
    github_dir = Path(".github")
    github_dir.mkdir(exist_ok=True)
    
    pr_file = github_dir / "PULL_REQUEST_TEMPLATE.md"
    pr_file.write_text(PR_TEMPLATE)
    
    console.print(f"[green]✓ Created: {pr_file}[/green]")
    console.print("\n[bold green]✓ PR template generated successfully![/bold green]")


PR_TEMPLATE = """## 📝 Description
Please include a summary of the changes and the related issue. Please also include relevant motivation and context.

Fixes # (issue)
Closes # (issue)

## 🔧 Type of Change
Please delete options that are not relevant.

- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 Documentation update
- [ ] 🎨 Style update (formatting, renaming)
- [ ] ♻️ Code refactoring (no functional changes)
- [ ] ⚡ Performance improvement
- [ ] ✅ Test update
- [ ] 🔨 Build/CI update
- [ ] 📦 Dependency update

## 🧪 How Has This Been Tested?
Please describe the tests that you ran to verify your changes. Provide instructions so we can reproduce.

**Test Configuration**:
* Python version:
* OS:
* Git version:

**Tests performed:**
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## 📸 Screenshots (if appropriate)
Add screenshots to help reviewers understand your changes.

## ✅ Checklist
Please check all that apply:

### Code Quality
- [ ] My code follows the style guidelines of this project (PEP 8)
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] My code passes all linting checks (black, ruff)
- [ ] My code passes type checking (mypy)

### Documentation
- [ ] I have made corresponding changes to the documentation
- [ ] I have updated the README if needed
- [ ] I have added docstrings to new functions/classes
- [ ] I have updated the CHANGELOG.md

### Testing
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] I have checked my code for edge cases

### Dependencies
- [ ] I have checked that no new dependencies are added unnecessarily
- [ ] If dependencies are added, I have justified them in this PR

## 🔗 Related Issues/PRs
List any related issues or pull requests:
- Related to #
- Depends on #
- Blocks #

## 📌 Additional Notes
Add any additional notes for reviewers here.

## 🎯 Post-Merge Actions
What should happen after this PR is merged?
- [ ] Update documentation site
- [ ] Announce in discussions
- [ ] Create release
- [ ] Update examples
- [ ] None

---

**Reviewer Guidelines:**
- Verify all checklist items are completed
- Test the changes locally if possible
- Check for potential breaking changes
- Ensure documentation is updated
- Verify tests are comprehensive
"""


def generate_contributing() -> None:
    """Generate CONTRIBUTING.md."""
    contributing_file = Path("CONTRIBUTING.md")
    contributing_file.write_text(CONTRIBUTING_TEMPLATE)
    
    console.print(f"[green]✓ Created: {contributing_file}[/green]")
    console.print("\n[bold green]✓ CONTRIBUTING.md generated successfully![/bold green]")


CONTRIBUTING_TEMPLATE = """# 🤝 Contributing to Git-Auto Pro

Thank you for your interest in contributing to Git-Auto Pro! We welcome contributions from everyone.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)
- [Questions](#questions)

## 📜 Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please be respectful and constructive in all interactions.

### Our Standards

- **Be Respectful**: Treat everyone with respect and kindness
- **Be Constructive**: Provide helpful feedback and suggestions
- **Be Collaborative**: Work together to improve the project
- **Be Patient**: Remember that everyone is learning

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a branch** for your changes
4. **Make your changes**
5. **Test your changes**
6. **Submit a pull request**

## 🛠️ Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- GitHub account

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/git-auto-pro.git
cd git-auto-pro

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -e ".[dev]"

# Verify installation
git-auto --help
```

### Development Dependencies

```bash
# Core dependencies (automatically installed)
typer[all]
requests
keyring
rich
gitpython
pyyaml
questionary

# Development dependencies
pytest
pytest-cov
black
ruff
mypy
```

## 💻 How to Contribute

### Types of Contributions

We welcome various types of contributions:

1. **🐛 Bug Fixes**: Fix issues in existing code
2. **✨ New Features**: Add new functionality
3. **📚 Documentation**: Improve or add documentation
4. **🧪 Tests**: Add or improve test coverage
5. **🎨 Code Quality**: Refactor or improve code quality
6. **🌐 Translations**: Help translate the tool

### First-Time Contributors

Look for issues labeled:
- `good first issue` - Easy issues for beginners
- `help wanted` - Issues where we need help
- `documentation` - Documentation improvements

## 📏 Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line Length**: 100 characters (not 79)
- **String Quotes**: Use double quotes for strings
- **Type Hints**: Always use type hints for function parameters and return values

### Code Formatting

```bash
# Format code with Black
black git_auto_pro/ tests/

# Lint with Ruff
ruff check git_auto_pro/ tests/

# Fix linting issues automatically
ruff check git_auto_pro/ tests/ --fix

# Type checking with mypy
mypy git_auto_pro/
```

### Docstring Format

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    '''Brief description of function.
    
    Detailed description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When param2 is negative
    
    Example:
        >>> example_function("test", 5)
        True
    '''
    pass
```

### File Organization

- One class per file when possible
- Related functions grouped together
- Clear separation of concerns
- Imports organized: stdlib, third-party, local

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

# Run tests in parallel
pytest -n auto
```

### Writing Tests

- Write tests for all new features
- Maintain or improve code coverage (target: >80%)
- Use descriptive test names
- Use fixtures for common setup
- Mock external dependencies (GitHub API, Git operations)

Example test:

```python
import pytest
from git_auto_pro.config import get_config, set_config


def test_config_set_and_get():
    '''Test setting and getting configuration values.'''
    # Arrange
    key = "test_key"
    value = "test_value"
    
    # Act
    set_config(key, value)
    result = get_config(key)
    
    # Assert
    assert result == value


@pytest.fixture
def temp_repo(tmp_path):
    '''Create a temporary Git repository for testing.'''
    import git
    repo = git.Repo.init(tmp_path)
    return repo
```

## 🔄 Pull Request Process

### Before Submitting

1. **Update your fork**: `git pull upstream main`
2. **Create a branch**: `git checkout -b feature/your-feature-name`
3. **Make changes**: Edit code
4. **Run tests**: Ensure all tests pass
5. **Format code**: Run black and ruff
6. **Update docs**: Update README/docs if needed
7. **Commit changes**: Use conventional commits

### Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks
- `perf`: Performance improvements

**Examples:**
```bash
feat(cli): add support for custom templates
fix(github): handle API rate limiting correctly
docs(readme): update installation instructions
test(config): add tests for configuration management
```

### Submitting a Pull Request

1. **Push your branch**: `git push origin feature/your-feature-name`
2. **Open PR**: Go to GitHub and create a pull request
3. **Fill out template**: Complete the PR template
4. **Link issues**: Reference related issues
5. **Request review**: Wait for maintainer review
6. **Address feedback**: Make requested changes
7. **Merge**: Once approved, your PR will be merged

### PR Checklist

Before submitting, ensure:

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] No merge conflicts
- [ ] PR description is complete

## 🐛 Reporting Bugs

### Before Reporting

1. **Check existing issues**: Search for similar issues
2. **Try latest version**: Update to the latest version
3. **Reproduce**: Ensure you can reproduce the bug
4. **Gather info**: Collect relevant information

### Bug Report Template

Use the bug report template when creating an issue. Include:

- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Error messages or logs
- Screenshots if applicable

## 💡 Suggesting Features

### Before Suggesting

1. **Check existing issues**: See if it's already suggested
2. **Consider scope**: Is it aligned with project goals?
3. **Think about implementation**: How might it work?

### Feature Request Template

Use the feature request template. Include:

- Clear description of the feature
- Problem it solves
- Proposed solution
- Alternatives considered
- Example usage

## ❓ Questions

### Where to Ask

- **GitHub Discussions**: For general questions and discussions
- **GitHub Issues**: For bugs and feature requests only
- **Email**: For private inquiries

### Getting Help

1. Check the [README](README.md)
2. Read the [Setup Guide](SETUP_GUIDE.md)
3. Search existing issues and discussions
4. Ask in GitHub Discussions

## 🏆 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

## 📞 Contact

- **GitHub**: [github.com/yourusername/git-auto-pro](https://github.com/yourusername/git-auto-pro)
- **Issues**: [github.com/yourusername/git-auto-pro/issues](https://github.com/yourusername/git-auto-pro/issues)
- **Discussions**: [github.com/yourusername/git-auto-pro/discussions](https://github.com/yourusername/git-auto-pro/discussions)

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Git-Auto Pro! 🚀

**Happy coding!** ✨
"""