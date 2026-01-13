#!/usr/bin/env python3
"""Basic usage examples for Git-Auto Pro."""

import subprocess
import sys


def run_command(cmd):
    """Run a git-auto command."""
    print(f"\\n→ Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}", file=sys.stderr)
    return result.returncode


def main():
    """Demonstrate basic Git-Auto Pro usage."""
    print("=== Git-Auto Pro Basic Usage Examples ===\\n")

    # Example 1: Check version
    print("1. Check version:")
    run_command("git-auto version")

    # Example 2: Check configuration
    print("\\n2. View configuration:")
    run_command("git-auto config list")

    # Example 3: Git status
    print("\\n3. Check git status:")
    run_command("git-auto status")

    # Example 4: View commit history
    print("\\n4. View commit log:")
    run_command("git-auto log --limit 5")

    # Example 5: List branches
    print("\\n5. List branches:")
    run_command("git-auto branch --list")

    print("\\n=== Examples Complete ===")


if __name__ == "__main__":
    main()