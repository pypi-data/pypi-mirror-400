# Troubleshooting - Git-Auto Pro

Common issues and solutions.

## Installation Issues

### Issue: Command not found after installation

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall package
pip install -e .

# Verify installation
which git-auto
git-auto --help
```

### Issue: Import errors

**Solution:**
```bash
# Install all dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Verify imports
python -c "import git_auto_pro; print('OK')"
```

## Authentication Issues

### Issue: "Not authenticated" error

**Solution:**
```bash
# Login again
git-auto login

# Verify token is stored
python -c "import keyring; print(keyring.get_password('git-auto-pro', 'github-token'))"
```

### Issue: Keyring errors on Linux

**Solution:**
```bash
# Install keyring backend
sudo apt-get install gnome-keyring  # Ubuntu/Debian
sudo dnf install gnome-keyring      # Fedora

# Or use alternative backend
pip install keyrings.alt
```

### Issue: API rate limiting

**Solution:**
- Wait for rate limit to reset (usually 1 hour)
- Use authenticated requests (make sure you're logged in)
- Check rate limit: https://github.com/settings/tokens

## Git Issues

### Issue: "Not a git repository"

**Solution:**
```bash
# Initialize repository
git-auto init

# Or navigate to existing repo
cd /path/to/repo
```

### Issue: Merge conflicts

**Solution:**
```bash
# Check status
git-auto status

# Resolve conflicts manually
# Edit conflicting files

# Mark as resolved
git-auto add --all
git-auto commit "Resolve merge conflicts"
```

### Issue: Detached HEAD state

**Solution:**
```bash
# Create branch from current state
git-auto branch temp-branch

# Or switch to existing branch
git-auto switch main
```

## GitHub Issues

### Issue: Repository already exists

**Solution:**
```bash
# Use different name
git-auto create-repo myrepo-v2

# Or connect to existing repo
git-auto init --connect https://github.com/user/existing-repo.git
```

### Issue: Permission denied

**Solution:**
- Verify token has correct scopes (`repo`, `workflow`)
- Check you have access to the organization
- Ensure repository visibility matches your permissions

## Command Issues

### Issue: Command hangs or freezes

**Solution:**
```bash
# Cancel with Ctrl+C

# Run with verbose logging
export GIT_AUTO_DEBUG=1
git-auto [command]

# Check network connectivity
ping github.com
```

### Issue: Unexpected behavior

**Solution:**
```bash
# Reset configuration
git-auto config reset --yes

# Clear cache
rm -rf ~/.git-auto-config.json

# Reinstall package
pip uninstall git-auto-pro
pip install -e .
```

## Platform-Specific Issues

### macOS

**Issue: SSL certificate errors**

**Solution:**
```bash
# Install certificates
/Applications/Python\ 3.x/Install\ Certificates.command

# Or use certifi
pip install --upgrade certifi
```

### Windows

**Issue: Path issues**

**Solution:**
```powershell
# Add to PATH
$env:Path += ";C:\path\to\python\Scripts"

# Or use full path
python -m git_auto_pro.cli --help
```

### Linux

**Issue: Permission errors**

**Solution:**
```bash
# Fix permissions
chmod +x scripts/*.sh

# Or run with bash explicitly
bash scripts/install.sh
```

## Getting Help

If issues persist:

1. Check [GitHub Issues](https://github.com/yourusername/git-auto-pro/issues)
2. Search [Discussions](https://github.com/yourusername/git-auto-pro/discussions)
3. Open a new issue with:
   - Your OS and Python version
   - Error message or logs
   - Steps to reproduce
   - Expected vs actual behavior

## Debug Mode

Enable debug logging:

```bash
# Set environment variable
export GIT_AUTO_DEBUG=1

# Run command
git-auto [command]

# Check logs
cat ~/.git-auto.log
```

## Clean Reinstall

Complete clean reinstall:

```bash
# Remove package
pip uninstall git-auto-pro

# Remove configuration
rm -rf ~/.git-auto-config.json

# Remove virtual environment
rm -rf venv/

# Start fresh
python -m venv venv
source venv/bin/activate
pip install -e .

# Test
git-auto --help
```