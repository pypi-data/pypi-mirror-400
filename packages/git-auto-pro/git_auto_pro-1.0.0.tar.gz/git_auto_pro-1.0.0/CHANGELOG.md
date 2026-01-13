# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release preparation

## [1.0.0] - 2026-01-03

### Added
- GitHub authentication with secure keyring storage
- Repository creation and management
- Complete Git command automation
- Project scaffolding with multiple templates
- Interactive README, LICENSE, and .gitignore generators
- CI/CD workflow generation (GitHub Actions, GitLab CI)
- Git hooks management (pre-commit, pre-push, commit-msg)
- GitHub issue and PR template generation
- Collaboration features (add collaborators, branch protection)
- Repository backup and restore functionality
- Configuration system with persistent storage
- Repository statistics and analytics
- Support for Python 3.8+
- Comprehensive documentation
- 30+ CLI commands
- Beautiful terminal output with Rich library

### Features by Category

#### Authentication
- Secure token storage using OS-level keyring
- GitHub API token validation
- Cross-platform support (macOS, Windows, Linux)

#### Repository Management
- Create public/private repositories
- Set descriptions, topics, and homepage URLs
- Automatic remote configuration
- Branch protection rules
- Collaborator management

#### Git Operations
- Simplified Git commands
- Branch management (create, switch, delete, list)
- Stash operations
- Merge with various strategies
- Clone with shallow copy support
- Interactive status and log display
- Conventional commit support

#### Project Scaffolding
- Python project template
- Node.js project template
- C++ project template
- Rust project template
- Go project template
- Web project template
- Custom templates support

#### Generators
- Professional README templates
- Multiple license types (MIT, Apache, GPL, BSD, etc.)
- Language-specific .gitignore templates
- GitHub Actions workflows
- GitLab CI configuration
- Git hooks
- Issue and PR templates

#### Configuration
- Persistent configuration storage
- Customizable defaults
- Per-user settings
- Branch name configuration
- License type defaults
- Commit message templates

### Documentation
- Comprehensive README with examples
- Detailed setup guide
- Contributing guidelines
- API documentation
- Troubleshooting guide
- Complete file structure reference

### Testing
- Test structure prepared
- Example test cases included
- Coverage configuration

## [0.1.0] - Development

### Added
- Initial project structure
- Basic CLI framework
- Core functionality implementation

---

## Release Notes

## [1.1.0] - 2026-01-04

### Added
- **Interactive .gitignore Manager** 🎉
  - `git-auto ignore-manager` command
  - Browse all project files with ignore status
  - Select files to ignore with checkbox interface
  - Add patterns by type (folder, extension, file, custom)
  - Common presets (Python, Node.js, IDEs, Build artifacts, Logs)
  - Remove patterns from .gitignore
  - Clean already-tracked files from git
  - Preview changes before saving
  - Show current .gitignore patterns

### Enhanced
- Better file management workflow
- More user-friendly .gitignore creation
- Visual feedback for ignore status

### Features
- 34 commands (up from 33)
- 7 core modules (up from 6)

---

## Future Releases

### [1.1.5] - Planned
- VS Code extension integration
- GitLab full support
- Bitbucket support
- Interactive TUI mode
- AI-powered commit messages

### [1.2.0] - Planned
- Plugin system for custom commands
- Team workspace management
- Advanced analytics dashboard
- Multi-repository operations

### [2.0.0] - Planned
- Major API redesign
- Performance improvements
- Extended language support
- Cloud integration features