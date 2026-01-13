# API Reference - Git-Auto Pro

Complete API reference for all commands and options.

## Command Structure

```
git-auto [COMMAND] [ARGUMENTS] [OPTIONS]
```

## Commands

### Authentication

#### `git-auto login`

Login to GitHub using Personal Access Token.

**Options:**
- `--token, -t TEXT`: GitHub Personal Access Token

**Example:**
```bash
git-auto login
git-auto login --token ghp_xxxxxxxxxxxx
```

### Repository Management

#### `git-auto create-repo NAME`

Create a new GitHub repository.

**Arguments:**
- `NAME`: Repository name (required)

**Options:**
- `--private, -p`: Create private repository
- `--description, -d TEXT`: Repository description
- `--homepage, -h TEXT`: Homepage URL
- `--topics, -t TEXT`: Comma-separated topics
- `--auto-init`: Initialize with README

**Example:**
```bash
git-auto create-repo myproject \
  --private \
  --description "My awesome project" \
  --topics "python,cli"
```

#### `git-auto init`

Initialize Git repository.

**Options:**
- `--connect, -c URL`: Connect to remote URL

**Example:**
```bash
git-auto init
git-auto init --connect https://github.com/user/repo.git
```

### Git Operations

#### `git-auto add [FILES]`

Stage files for commit.

**Arguments:**
- `FILES`: Files to add (optional)

**Options:**
- `--all, -A`: Add all files

**Example:**
```bash
git-auto add file1.py file2.py
git-auto add --all
```

#### `git-auto commit MESSAGE`

Commit staged changes.

**Arguments:**
- `MESSAGE`: Commit message (required)

**Options:**
- `--conventional, -c`: Use conventional commit format
- `--amend`: Amend previous commit

**Example:**
```bash
git-auto commit "Add new feature"
git-auto commit "fix: resolve bug" --conventional
```

#### `git-auto push [MESSAGE]`

Push commits to remote.

**Arguments:**
- `MESSAGE`: Commit message (optional, auto add+commit+push)

**Options:**
- `--branch, -b TEXT`: Branch to push (default: main)
- `--force, -f`: Force push

**Example:**
```bash
git-auto push
git-auto push "Quick update"
git-auto push --force
```

### Configuration

#### `git-auto config set KEY VALUE`

Set configuration value.

**Example:**
```bash
git-auto config set default_branch develop
git-auto config set conventional_commits true
```

#### `git-auto config get KEY`

Get configuration value.

**Example:**
```bash
git-auto config get default_branch
```

#### `git-auto config list`

List all configuration values.

**Example:**
```bash
git-auto config list
```

### Project Scaffolding

#### `git-auto new PROJECT_NAME`

Create complete new project.

**Arguments:**
- `PROJECT_NAME`: Project name (required)

**Options:**
- `--template, -t TEXT`: Project template
- `--private, -p`: Create private repository
- `--no-github`: Skip GitHub repository creation

**Example:**
```bash
git-auto new myproject --template python
```

### Generators

#### `git-auto readme`

Generate README.md.

**Options:**
- `--interactive, -i`: Interactive mode (default: true)
- `--output, -o PATH`: Output file

**Example:**
```bash
git-auto readme
git-auto readme --output docs/README.md
```

#### `git-auto ignore-manager`

Launch interactive .gitignore file manager.

**Usage:**
```bash
git-auto ignore-manager
```

**Features:**
- Browse all project files
- Interactive checkbox selection
- Preset patterns (Python, Node, etc.)
- Add by type (folder, extension, file)
- View ignore status
- Remove patterns
- Clean tracked files

**Example:**
```bash
# Launch manager
git-auto ignore-manager

# Menu options:
# - View all files (with ignore status)
# - Add files/patterns to ignore
# - Remove patterns from ignore
# - Browse and select files to ignore
# - Show current .gitignore
# - Clean: Remove ignored files from git
# - Save and exit
```

## Configuration Options

### Available Keys

- `default_branch`: Default branch name
- `default_commit_message`: Default commit message
- `default_license`: Default license type
- `default_project_type`: Default project template
- `auto_push`: Automatically push after commit
- `conventional_commits`: Enforce conventional commits
- `editor`: Default text editor

---

