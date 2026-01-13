"""Tests for interactive .gitignore manager."""

import pytest
from pathlib import Path
from git_auto_pro.gitignore_manager import (
    get_all_files,
    load_gitignore,
    save_gitignore,
    should_ignore,
)


def test_get_all_files(tmp_path):
    """Test getting all files in directory."""
    # Create test files
    (tmp_path / "file1.txt").write_text("content")
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "file2.py").write_text("code")
    
    files = get_all_files(tmp_path)
    
    assert len(files) == 2
    assert Path("file1.txt") in files
    assert Path("subdir/file2.py") in files


def test_load_gitignore(tmp_path, monkeypatch):
    """Test loading .gitignore patterns."""
    monkeypatch.chdir(tmp_path)
    
    # Create .gitignore
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("*.pyc\n__pycache__/\n# Comment\nvenv/\n")
    
    patterns = load_gitignore()
    
    assert "*.pyc" in patterns
    assert "__pycache__/" in patterns
    assert "venv/" in patterns
    assert "# Comment" not in patterns  # Comments excluded


def test_save_gitignore(tmp_path, monkeypatch):
    """Test saving .gitignore patterns."""
    monkeypatch.chdir(tmp_path)
    
    patterns = {"*.pyc", "__pycache__/", "venv/"}
    save_gitignore(patterns)
    
    gitignore = tmp_path / ".gitignore"
    assert gitignore.exists()
    
    content = gitignore.read_text()
    assert "*.pyc" in content
    assert "__pycache__/" in content


def test_should_ignore():
    """Test pattern matching."""
    patterns = {"*.pyc", "__pycache__/", "venv/", "config.local.py"}
    
    # Should ignore
    assert should_ignore(Path("test.pyc"), patterns)
    assert should_ignore(Path("__pycache__/file.py"), patterns)
    assert should_ignore(Path("config.local.py"), patterns)
    
    # Should not ignore
    assert not should_ignore(Path("test.py"), patterns)
    assert not should_ignore(Path("README.md"), patterns)
