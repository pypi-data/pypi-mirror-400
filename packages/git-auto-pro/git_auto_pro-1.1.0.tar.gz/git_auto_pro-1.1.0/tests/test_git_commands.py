"""Tests for Git command operations."""

import pytest
import git
from pathlib import Path
from git_auto_pro.git_commands import (
    get_repo,
    git_init,
    git_add,
    git_commit,
    git_pull,
)
from unittest.mock import MagicMock, patch


class TestRepoOperations:
    """Test repository operations."""
    
    def test_get_repo_fails_outside_repo(self, temp_dir, monkeypatch):
        """Test that get_repo fails outside a repository."""
        monkeypatch.chdir(temp_dir)
        
        with pytest.raises(git.InvalidGitRepositoryError):
            get_repo()
    
    def test_get_repo_succeeds_in_repo(self, temp_repo, monkeypatch):
        """Test that get_repo works in a repository."""
        monkeypatch.chdir(temp_repo.working_dir)
        
        repo = get_repo()
        assert repo is not None
        assert isinstance(repo, git.Repo)


class TestGitInit:
    """Test git initialization."""
    
    def test_git_init_creates_repo(self, temp_dir, monkeypatch):
        """Test that git init creates a repository."""
        monkeypatch.chdir(temp_dir)
        
        git_init()
        
        assert (temp_dir / ".git").exists()
        assert (temp_dir / ".git").is_dir()
    
    def test_git_init_with_existing_repo(self, temp_repo, monkeypatch):
        """Test git init with existing repository."""
        monkeypatch.chdir(temp_repo.working_dir)
        
        # Should not raise error, just show message
        git_init()


class TestGitAdd:
    """Test staging files."""
    
    def test_git_add_all(self, temp_repo, monkeypatch):
        """Test adding all files."""
        monkeypatch.chdir(temp_repo.working_dir)
        
        # Create a test file
        test_file = Path(temp_repo.working_dir) / "test.txt"
        test_file.write_text("test content")
        
        git_add(all=True)
        
        # Check if file is staged
        assert "test.txt" in temp_repo.git.diff("--cached", "--name-only")
    
    def test_git_add_specific_files(self, temp_repo, monkeypatch):
        """Test adding specific files."""
        monkeypatch.chdir(temp_repo.working_dir)
        
        # Create test files
        file1 = Path(temp_repo.working_dir) / "file1.txt"
        file2 = Path(temp_repo.working_dir) / "file2.txt"
        file1.write_text("content 1")
        file2.write_text("content 2")
        
        git_add(files=["file1.txt"])
        
        staged = temp_repo.git.diff("--cached", "--name-only")
        assert "file1.txt" in staged
        assert "file2.txt" not in staged


class TestGitCommit:
    """Test committing changes."""
    
    def test_git_commit_basic(self, temp_repo, monkeypatch):
        """Test basic commit."""
        monkeypatch.chdir(temp_repo.working_dir)
        
        # Create and stage a file
        test_file = Path(temp_repo.working_dir) / "test.txt"
        test_file.write_text("test content")
        temp_repo.index.add(["test.txt"])
        
        git_commit("Test commit")
        
        # Verify commit
        commits = list(temp_repo.iter_commits())
        assert len(commits) == 1
        assert commits[0].message == "Test commit"


class TestGitPull:
    """Test pull command strategies."""

    def test_pull_default(self, temp_repo, monkeypatch):
        """Test default pull (merge)."""
        monkeypatch.chdir(temp_repo.working_dir)
        
        with patch('git_auto_pro.git_commands.get_repo') as mock_get_repo:
            mock_repo = MagicMock()
            mock_git = MagicMock()
            mock_repo.git = mock_git
            mock_get_repo.return_value = mock_repo
            
            git_pull()
            mock_git.pull.assert_called_with("--no-rebase")

    def test_pull_rebase(self, temp_repo, monkeypatch):
        """Test pull with rebase."""
        monkeypatch.chdir(temp_repo.working_dir)
        
        with patch('git_auto_pro.git_commands.get_repo') as mock_get_repo:
            mock_repo = MagicMock()
            mock_git = MagicMock()
            mock_repo.git = mock_git
            mock_get_repo.return_value = mock_repo
            
            git_pull(rebase=True)
            mock_git.pull.assert_called_with("--rebase")

    def test_pull_no_rebase(self, temp_repo, monkeypatch):
        """Test pull with no-rebase."""
        monkeypatch.chdir(temp_repo.working_dir)
        
        with patch('git_auto_pro.git_commands.get_repo') as mock_get_repo:
            mock_repo = MagicMock()
            mock_git = MagicMock()
            mock_repo.git = mock_git
            mock_get_repo.return_value = mock_repo
            
            git_pull(no_rebase=True)
            mock_git.pull.assert_called_with("--no-rebase")

    def test_pull_ff_only(self, temp_repo, monkeypatch):
        """Test pull with fast-forward only."""
        monkeypatch.chdir(temp_repo.working_dir)
        
        with patch('git_auto_pro.git_commands.get_repo') as mock_get_repo:
            mock_repo = MagicMock()
            mock_git = MagicMock()
            mock_repo.git = mock_git
            mock_get_repo.return_value = mock_repo
            
            git_pull(ff_only=True)
            mock_git.pull.assert_called_with("--ff-only")

    def test_pull_branch_rebase(self, temp_repo, monkeypatch):
        """Test pull specific branch with rebase."""
        monkeypatch.chdir(temp_repo.working_dir)
        
        with patch('git_auto_pro.git_commands.get_repo') as mock_get_repo:
            mock_repo = MagicMock()
            mock_git = MagicMock()
            mock_repo.git = mock_git
            mock_get_repo.return_value = mock_repo
            
            git_pull(branch="main", rebase=True)
            mock_git.pull.assert_called_with("origin", "main", "--rebase")