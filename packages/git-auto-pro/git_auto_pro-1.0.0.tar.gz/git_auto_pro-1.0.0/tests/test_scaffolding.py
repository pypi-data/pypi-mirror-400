"""Tests for scaffolding modules."""

import pytest
from pathlib import Path
from git_auto_pro.scaffolding.readme import generate_readme
from git_auto_pro.scaffolding.license import generate_license
from git_auto_pro.scaffolding.gitignore import generate_gitignore


class TestReadmeGeneration:
    """Test README generation."""
    
    def test_generate_readme_creates_file(self, temp_dir, monkeypatch):
        """Test that README is created."""
        monkeypatch.chdir(temp_dir)
        
        # Generate README in non-interactive mode
        generate_readme(interactive=False, output="README.md")
        
        readme_path = temp_dir / "README.md"
        assert readme_path.exists()
        content = readme_path.read_text()
        assert len(content) > 0
        assert "# " in content  # Should have a header


class TestLicenseGeneration:
    """Test LICENSE generation."""
    
    def test_generate_mit_license(self, temp_dir, monkeypatch):
        """Test MIT license generation."""
        monkeypatch.chdir(temp_dir)
        
        generate_license(type="MIT", author="Test Author", year=2024)
        
        license_path = temp_dir / "LICENSE"
        assert license_path.exists()
        content = license_path.read_text()
        assert "MIT License" in content
        assert "Test Author" in content
        assert "2024" in content
    
    def test_generate_apache_license(self, temp_dir, monkeypatch):
        """Test Apache license generation."""
        monkeypatch.chdir(temp_dir)
        
        generate_license(type="Apache-2.0", author="Test Author", year=2024)
        
        license_path = temp_dir / "LICENSE"
        assert license_path.exists()
        content = license_path.read_text()
        assert "Apache License" in content


class TestGitignoreGeneration:
    """Test .gitignore generation."""
    
    def test_generate_python_gitignore(self, temp_dir, monkeypatch):
        """Test Python .gitignore generation."""
        monkeypatch.chdir(temp_dir)
        
        generate_gitignore(template="python")
        
        gitignore_path = temp_dir / ".gitignore"
        assert gitignore_path.exists()
        content = gitignore_path.read_text()
        assert "__pycache__" in content
        assert "*.py[cod]" in content
        assert "venv/" in content
    
    def test_generate_node_gitignore(self, temp_dir, monkeypatch):
        """Test Node .gitignore generation."""
        monkeypatch.chdir(temp_dir)
        
        generate_gitignore(template="node")
        
        gitignore_path = temp_dir / ".gitignore"
        assert gitignore_path.exists()
        content = gitignore_path.read_text()
        assert "node_modules/" in content
        assert ".env" in content
