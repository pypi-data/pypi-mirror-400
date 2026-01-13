"""Tests for configuration management."""

import pytest
import json
from pathlib import Path
from git_auto_pro.config import (
    load_config,
    save_config,
    get_config,
    set_config,
    reset_config,
    get_default_branch,
    get_default_license,
    DEFAULT_CONFIG,
    CONFIG_FILE
)


class TestConfigLoading:
    """Test configuration loading."""
    
    def test_load_default_config(self, tmp_path, monkeypatch):
        """Test loading default configuration."""
        # Point to temporary config file
        temp_config = tmp_path / ".git-auto-config.json"
        monkeypatch.setattr("git_auto_pro.config.CONFIG_FILE", temp_config)
        
        config = load_config()
        assert config == DEFAULT_CONFIG
    
    def test_load_existing_config(self, tmp_path, monkeypatch):
        """Test loading existing configuration."""
        temp_config = tmp_path / ".git-auto-config.json"
        monkeypatch.setattr("git_auto_pro.config.CONFIG_FILE", temp_config)
        
        # Create a config file
        test_config = {"default_branch": "develop", "test_key": "test_value"}
        temp_config.write_text(json.dumps(test_config))
        
        config = load_config()
        assert config["default_branch"] == "develop"
        assert config["test_key"] == "test_value"


class TestConfigSaving:
    """Test configuration saving."""
    
    def test_save_config(self, tmp_path, monkeypatch):
        """Test saving configuration."""
        temp_config = tmp_path / ".git-auto-config.json"
        monkeypatch.setattr("git_auto_pro.config.CONFIG_FILE", temp_config)
        
        test_config = {"key": "value", "number": 42}
        save_config(test_config)
        
        assert temp_config.exists()
        loaded = json.loads(temp_config.read_text())
        assert loaded == test_config


class TestConfigOperations:
    """Test configuration get/set operations."""
    
    def test_set_and_get_string(self, tmp_path, monkeypatch):
        """Test setting and getting string values."""
        temp_config = tmp_path / ".git-auto-config.json"
        monkeypatch.setattr("git_auto_pro.config.CONFIG_FILE", temp_config)
        
        set_config("test_key", "test_value")
        value = get_config("test_key")
        assert value == "test_value"
    
    def test_set_and_get_boolean(self, tmp_path, monkeypatch):
        """Test setting and getting boolean values."""
        temp_config = tmp_path / ".git-auto-config.json"
        monkeypatch.setattr("git_auto_pro.config.CONFIG_FILE", temp_config)
        
        set_config("test_bool", "true")
        value = get_config("test_bool")
        assert value is True
        
        set_config("test_bool", "false")
        value = get_config("test_bool")
        assert value is False
    
    def test_set_and_get_integer(self, tmp_path, monkeypatch):
        """Test setting and getting integer values."""
        temp_config = tmp_path / ".git-auto-config.json"
        monkeypatch.setattr("git_auto_pro.config.CONFIG_FILE", temp_config)
        
        set_config("test_int", "42")
        value = get_config("test_int")
        assert value == 42
    
    def test_get_nonexistent_key(self, tmp_path, monkeypatch):
        """Test getting a non-existent key."""
        temp_config = tmp_path / ".git-auto-config.json"
        monkeypatch.setattr("git_auto_pro.config.CONFIG_FILE", temp_config)
        
        value = get_config("nonexistent")
        assert value is None


class TestConfigReset:
    """Test configuration reset."""
    
    def test_reset_config(self, tmp_path, monkeypatch):
        """Test resetting configuration to defaults."""
        temp_config = tmp_path / ".git-auto-config.json"
        monkeypatch.setattr("git_auto_pro.config.CONFIG_FILE", temp_config)
        
        # Set some custom values
        set_config("custom_key", "custom_value")
        
        # Reset
        reset_config()
        
        # Load and verify
        config = load_config()
        assert config == DEFAULT_CONFIG


class TestConfigHelpers:
    """Test configuration helper functions."""
    
    def test_get_default_branch(self, tmp_path, monkeypatch):
        """Test getting default branch."""
        temp_config = tmp_path / ".git-auto-config.json"
        monkeypatch.setattr("git_auto_pro.config.CONFIG_FILE", temp_config)
        
        branch = get_default_branch()
        assert branch == "main"
        
        set_config("default_branch", "develop")
        branch = get_default_branch()
        assert branch == "develop"
    
    def test_get_default_license(self, tmp_path, monkeypatch):
        """Test getting default license."""
        temp_config = tmp_path / ".git-auto-config.json"
        monkeypatch.setattr("git_auto_pro.config.CONFIG_FILE", temp_config)
        
        license_type = get_default_license()
        assert license_type == "MIT"
