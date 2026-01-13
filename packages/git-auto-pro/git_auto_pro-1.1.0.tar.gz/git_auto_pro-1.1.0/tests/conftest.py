import pytest
import tempfile
import shutil
from pathlib import Path
import git
import os


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    
    def remove_readonly(func, path, excinfo):
        """Error handler for Windows readonly files."""
        os.chmod(path, 0o777)
        func(path)
    
    try:
        shutil.rmtree(temp_path, onerror=remove_readonly)
    except Exception:
        import time
        time.sleep(0.1)
        try:
            shutil.rmtree(temp_path, onerror=remove_readonly)
        except Exception:
            pass


@pytest.fixture
def temp_repo(temp_dir):
    """Create a temporary Git repository."""
    repo = git.Repo.init(temp_dir)

    repo.config_writer().set_value("user", "name", "Test User").release()
    repo.config_writer().set_value("user", "email", "test@example.com").release()
    yield repo
    repo.close()
    

@pytest.fixture
def mock_github_token(monkeypatch):
    """Mock GitHub token for testing."""
    monkeypatch.setenv("GITHUB_TOKEN", "test_token_12345")
    return "test_token_12345"


@pytest.fixture
def change_test_dir(temp_dir, monkeypatch):
    """Change to temporary directory for tests."""
    monkeypatch.chdir(temp_dir)
    yield temp_dir