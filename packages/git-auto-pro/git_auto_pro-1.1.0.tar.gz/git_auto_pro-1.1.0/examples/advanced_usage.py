#!/usr/bin/env python3
"""Advanced usage examples for Git-Auto Pro."""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, check=False):
    """Run a command and return result."""
    print(f"\\n→ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr and check:
        print(f"Error: {result.stderr}", file=sys.stderr)
    return result


def example_project_creation():
    """Example: Create a complete project."""
    print("\\n=== Creating a New Project ===")
    
    # Create project with Python template
    run_command("git-auto new example-project --template python --no-github")
    
    print("Project created with:")
    print("- Git initialized")
    print("- Python template structure")
    print("- README.md, LICENSE, .gitignore")
    print("- Initial commit")


def example_workflow_setup():
    """Example: Set up CI/CD workflows."""
    print("\\n=== Setting Up CI/CD Workflows ===")
    
    # Generate GitHub Actions CI workflow
    run_command("git-auto workflow ci")
    
    # Generate test workflow
    run_command("git-auto workflow test")
    
    # Set up pre-commit hooks
    run_command("git-auto hook pre-commit")
    
    print("CI/CD setup complete!")


def example_branch_workflow():
    """Example: Branch workflow."""
    print("\\n=== Branch Workflow Example ===")
    
    # Create feature branch
    run_command("git-auto branch feature/new-feature")
    
    # Switch to feature branch
    run_command("git-auto switch feature/new-feature")
    
    # Make changes and commit
    print("Make your changes...")
    run_command("git-auto add --all")
    run_command('git-auto commit "Add new feature"')
    
    # Switch back to main
    run_command("git-auto switch main")
    
    # Merge feature branch
    run_command("git-auto merge feature/new-feature")
    
    print("Branch workflow complete!")


def example_collaboration():
    """Example: Set up collaboration."""
    print("\\n=== Collaboration Setup ===")
    
    # Generate GitHub templates
    run_command("git-auto templates issue")
    run_command("git-auto templates pr")
    run_command("git-auto templates contributing")
    
    # Protect main branch
    run_command("git-auto protect main")
    
    print("Collaboration templates created!")


def example_configuration():
    """Example: Configuration management."""
    print("\\n=== Configuration Examples ===")
    
    # Set configuration values
    run_command('git-auto config set default_branch develop')
    run_command('git-auto config set default_license Apache-2.0')
    run_command('git-auto config set conventional_commits true')
    
    # View configuration
    run_command("git-auto config list")
    
    print("Configuration updated!")


def example_generators():
    """Example: Use generators."""
    print("\\n=== Generator Examples ===")
    
    # Generate README
    print("Generate README (will prompt for input):")
    # run_command("git-auto readme")
    
    # Generate LICENSE
    print("Generate LICENSE:")
    run_command('git-auto license --type MIT --author "Your Name"')
    
    # Generate .gitignore
    print("Generate .gitignore:")
    run_command("git-auto ignore --template python")
    
    print("Files generated!")


def example_statistics():
    """Example: View repository statistics."""
    print("\\n=== Repository Statistics ===")
    
    # Basic stats
    run_command("git-auto stats")
    
    # Detailed stats
    run_command("git-auto stats --detailed")
    
    print("Statistics displayed!")


def main():
    """Run all advanced examples."""
    print("=== Git-Auto Pro Advanced Usage Examples ===")
    
    examples = [
        ("Project Creation", example_project_creation),
        ("Workflow Setup", example_workflow_setup),
        ("Branch Workflow", example_branch_workflow),
        ("Collaboration", example_collaboration),
        ("Configuration", example_configuration),
        ("Generators", example_generators),
        ("Statistics", example_statistics),
    ]
    
    print("\\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    
    print("\\nNote: Some examples require a git repository")
    print("Run examples individually as needed")


if __name__ == "__main__":
    main()