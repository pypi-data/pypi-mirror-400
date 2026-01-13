"""Tests for CLI commands."""

import pytest
from typer.testing import CliRunner
from git_auto_pro.cli import app

runner = CliRunner()


class TestCLIBasics:
    """Test basic CLI functionality."""
    
    def test_help_command(self):
        """Test that help command works."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "git-auto" in result.output.lower()
    
    def test_version_command(self):
        """Test version command."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "Git-Auto Pro" in result.output
    
    def test_config_list_command(self):
        """Test config list command."""
        result = runner.invoke(app, ["config", "list"])
        assert result.exit_code == 0


class TestConfigCommands:
    """Test configuration commands."""
    
    def test_config_set_and_get(self):
        """Test setting and getting config values."""
        # Set a value
        result = runner.invoke(app, ["config", "set", "test_key", "test_value"])
        assert result.exit_code == 0
        
        # Get the value
        result = runner.invoke(app, ["config", "get", "test_key"])
        assert result.exit_code == 0
        assert "test_value" in result.output
    
    def test_config_set_boolean(self):
        """Test setting boolean config values."""
        result = runner.invoke(app, ["config", "set", "test_bool", "true"])
        assert result.exit_code == 0
    
    def test_config_set_integer(self):
        """Test setting integer config values."""
        result = runner.invoke(app, ["config", "set", "test_int", "42"])
        assert result.exit_code == 0


class TestGitCommands:
    """Test Git operation commands."""
    
    def test_status_no_repo(self, tmp_path, monkeypatch):
        """Test status command when not in a repo."""
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["status"])
        assert "Not a git repository" in result.output or result.exit_code != 0
    
    def test_branch_list_help(self):
        """Test branch command help."""
        result = runner.invoke(app, ["branch", "--help"])
        assert result.exit_code == 0
        assert "branch" in result.output.lower()

