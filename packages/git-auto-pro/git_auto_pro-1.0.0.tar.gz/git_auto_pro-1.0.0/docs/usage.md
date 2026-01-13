# Usage Guide - Git-Auto Pro

Complete guide for using Git-Auto Pro in your daily workflow.

## Table of Contents

1. [Installation](#installation)
2. [Getting Started](#getting-started)
3. [Authentication](#authentication)
4. [Basic Commands](#basic-commands)
5. [Advanced Features](#advanced-features)
6. [Workflows](#workflows)
7. [Best Practices](#best-practices)

## Installation

```bash
pip install git-auto-pro
```

## Getting Started

### First Time Setup

```bash
# 1. Login to GitHub
git-auto login

# 2. Configure defaults
git-auto config set default_branch main
git-auto config set default_license MIT

# 3. Check configuration
git-auto config list
```

## Authentication

### GitHub Personal Access Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
   - `admin:org` (Full control of organizations)
4. Copy the token
5. Run `git-auto login` and paste the token

## Basic Commands

### Repository Management

```bash
# Create new repository
git-auto create-repo myrepo
git-auto create-repo myrepo --private

# Initialize local repository
git-auto init
git-auto init --connect https://github.com/user/repo.git
```

### Git Operations

```bash
# Status
git-auto status
git-auto status --short

# Add files
git-auto add file.py
git-auto add --all

# Commit
git-auto commit "Your message"
git-auto commit "Your message" --conventional

# Push
git-auto push
git-auto push "Quick commit and push"

# Pull
git-auto pull
git-auto pull --rebase

# Log
git-auto log
git-auto log --limit 20 --graph
```

### Branch Management

```bash
# List branches
git-auto branch
git-auto branch --list
git-auto branch --remote

# Create branch
git-auto branch feature/new-feature

# Switch branch
git-auto switch develop
git-auto switch -c feature/new-feature

# Delete branch
git-auto delete-branch old-feature
```

## Advanced Features

### Project Creation

```bash
# Create complete project
git-auto new myproject
git-auto new myproject --template python
git-auto new myproject --private --template node
```

### Generators

```bash
# README
git-auto readme

# LICENSE
git-auto license
git-auto license --type MIT

# .gitignore
git-auto ignore
git-auto ignore --template python

# Templates
git-auto template python
git-auto template node
```

### Interactive .gitignore Manager
The interactive manager lets you browse and select files to ignore:
```bash
# Launch interactive manager
git-auto ignore-manager

# Interactive features:
# 1. View all files with ignore status
# 2. Browse and select files with checkboxes
# 3. Add patterns by type (folder/extension/file)
# 4. Use common presets (Python, Node, IDEs, etc.)
# 5. Remove patterns from .gitignore
# 6. Clean already-tracked files from git
# 7. Preview changes before saving
```

**Common workflows:**
```bash
# New project setup
git-auto ignore-manager
# → Select "Common presets"
# → Choose "Python"
# → Browse and select project-specific files
# → Save

# Fix tracked files that should be ignored
git-auto ignore-manager
# → Add patterns for those files
# → Select "Clean: Remove ignored files"
# → Commit changes
```


### Workflows

```bash
# CI/CD
git-auto workflow ci
git-auto workflow test
git-auto workflow cd

# Git Hooks
git-auto hook pre-commit
git-auto hook pre-push
```

## Workflows

### Daily Development

```bash
# Morning: Start new feature
git-auto switch -c feature/login
git-auto pull

# During development
git-auto status
git-auto push "Implement login form"

# End of day
git-auto push "Add tests for login"
```

### Release Workflow

```bash
# Update version
git-auto config set version 1.1.0

# Create release branch
git-auto branch release/1.1.0
git-auto switch release/1.1.0

# Merge to main
git-auto switch main
git-auto merge release/1.1.0

# Push and tag
git-auto push
git tag v1.1.0
git push --tags
```

## Best Practices

1. **Use conventional commits** for better changelog generation
2. **Set up hooks** for code quality checks
3. **Protect main branch** to enforce reviews
4. **Regular backups** of important repositories
5. **Configure defaults** to speed up workflow

---
