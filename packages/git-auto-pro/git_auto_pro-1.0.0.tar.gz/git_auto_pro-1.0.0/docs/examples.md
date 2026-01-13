# Examples - Git-Auto Pro

Real-world examples and use cases.

## Quick Start Example

```bash
# Install
pip install git-auto-pro

# Login
git-auto login

# Create new project
git-auto new my-awesome-app --template python

# Start developing
cd my-awesome-app
git-auto status
git-auto push "Initial implementation"
```

## Example 1: Python CLI Tool

```bash
# Create project
git-auto new my-cli-tool --template python --private

# Navigate to project
cd my-cli-tool

# Set up CI/CD
git-auto workflow ci
git-auto workflow test

# Set up hooks
git-auto hook pre-commit
git-auto hook pre-push

# Create feature
git-auto switch -c feature/add-command
# ... make changes ...
git-auto push "Add new command"

# Merge to main
git-auto switch main
git-auto merge feature/add-command
git-auto push
```

## Example 2: Web Application

```bash
# Create project
git-auto new my-web-app --template node

cd my-web-app

# Generate GitHub templates
git-auto templates issue
git-auto templates pr
git-auto templates contributing

# Set up branch protection
git-auto protect main

# Create development workflow
git-auto switch -c develop
git-auto push

# Add collaborators
git-auto collab teammate1
git-auto collab teammate2 --permission admin
```

## Example 3: Multi-Language Project

```bash
# Create project
git-auto new polyglot-project

cd polyglot-project

# Add multiple templates
mkdir backend frontend
cd backend
git-auto template python
cd ../frontend
git-auto template web

# Generate comprehensive .gitignore
cd ..
git-auto ignore --template python

# Add custom patterns
echo "frontend/node_modules/" >> .gitignore
echo "backend/.venv/" >> .gitignore

# Commit
git-auto push "Set up project structure"
```

## Example 4: Documentation Site

```bash
# Create project
git-auto new my-docs

cd my-docs

# Generate README
git-auto readme

# Create docs structure
mkdir -p docs/{guide,api,examples}
touch docs/guide/getting-started.md
touch docs/api/reference.md
touch docs/examples/basic.md

# Set up GitHub Pages workflow
git-auto workflow cd --platform github

# Push
git-auto push "Initialize documentation site"
```

## Example 5: Team Collaboration

```bash
# Create shared repository
git-auto create-repo team-project --private

# Clone and set up
git clone https://github.com/org/team-project.git
cd team-project

# Configure project
git-auto config set default_branch develop
git-auto config set conventional_commits true

# Set up workflows
git-auto workflow ci
git-auto workflow test

# Add team members
git-auto collab alice --permission push
git-auto collab bob --permission push
git-auto collab charlie --permission admin

# Protect branches
git-auto protect main
git-auto protect develop

# Create templates
git-auto templates issue
git-auto templates pr
git-auto templates contributing
```

## Example 6: Interactive .gitignore Setup

Clean up a project by managing ignored files interactively.
```bash
# You have a messy project with tracked files that shouldn't be
cd ~/messy-project

# Launch interactive manager
git-auto ignore-manager

# Select: "📦 Common presets"
# Choose: "Python" (adds __pycache__/, *.pyc, venv/, etc.)

# Select: "🎯 Browse and select files to ignore"
# Check these files:
#   ✓ .env
#   ✓ local_config.json
#   ✓ test_output/
#   ✓ .idea/
#   ✓ .DS_Store

# Select: "📊 Show current .gitignore"
# Review: 16 patterns total

# Select: "🧹 Clean: Remove ignored files from git"
# Confirm: Yes
# Result: Files removed from git tracking but kept on disk

# Select: "💾 Save and exit"
# ✓ Saved 16 patterns to .gitignore

# Commit the changes
git-auto commit "Clean up ignored files"
git-auto push

# Result: 
# - .gitignore properly configured
# - Unwanted files removed from git
# - Project is cleaner
```
---

