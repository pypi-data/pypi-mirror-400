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

## Example 3: Handling Divergent Branches

```bash
# Scenario: You have local commits and remote has new commits

# Option 1: Merge (default, safest)
git-auto pull --no-rebase
# Creates a merge commit, preserves all history

# Option 2: Rebase (cleaner history)
git-auto pull --rebase
# Replays your commits on top of remote changes

# Option 3: Fast-forward only (fails if not possible)
git-auto pull --ff-only
# Only succeeds if no divergence

# Pull specific branch with rebase
git-auto pull -b main --rebase
```

## Example 4: GitHub Issues Workflow

```bash
# Create a bug report
git-auto issue create \
  --title "Login button not working" \
  --body "Users can't click the login button on mobile" \
  --labels "bug,priority-high,mobile"

# List all open bugs
git-auto issue list --labels bug

# View issue details
git-auto issue view 42

# Work on the fix
git-auto switch -c fix/issue-42
# ... make changes ...
git-auto push "Fix login button on mobile (fixes #42)"

# Close the issue
git-auto issue close 42 --comment "Fixed in PR #123"

# List closed issues
git-auto issue list --state closed
```

## Example 5: Multi-Language Project

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

## Example 6: Documentation Site

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

## Example 7: Team Collaboration with Issues

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

# Create initial issues for team
git-auto issue create -t "Setup CI/CD" -l "infrastructure"
git-auto issue create -t "Write documentation" -l "documentation"
git-auto issue create -t "Add unit tests" -l "testing"

# Assign issues
git-auto issue update 1 --assignees alice
git-auto issue update 2 --assignees bob
```

## Example 8: Interactive .gitignore Setup

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

## Example 9: Issue-Driven Development

```bash
# Start with planning
git-auto issue create -t "Feature: User authentication" -l "enhancement"
git-auto issue create -t "Feature: Password reset" -l "enhancement"
git-auto issue create -t "Feature: Email verification" -l "enhancement"

# List all features
git-auto issue list --labels enhancement

# Work on first feature
git-auto switch -c feature/auth-issue-1
# ... implement authentication ...
git-auto push "Implement user authentication (closes #1)"

# The issue is automatically closed by GitHub when PR is merged

# Check remaining work
git-auto issue list --state open
```

---
