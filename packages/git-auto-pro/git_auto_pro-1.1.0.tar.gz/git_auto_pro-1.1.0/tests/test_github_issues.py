"""Tests for GitHub issues management."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from git_auto_pro.github_issues import (
    create_issue,
    list_issues,
    get_issue,
    close_issue,
    update_issue,
)

@pytest.fixture
def mock_session():
    with patch('git_auto_pro.github.get_authenticated_session') as mock:
        yield mock

@pytest.fixture
def mock_user():
    with patch('git_auto_pro.github.get_current_user') as mock:
        mock.return_value = {"login": "testuser"}
        yield mock

@pytest.fixture
def mock_git_repo():
    with patch('git.Repo') as mock:
        repo_instance = MagicMock()
        remote = MagicMock()
        remote.url = "https://github.com/testuser/testrepo.git"
        # Mock the remotes.origin.url access chain
        repo_instance.remotes.origin = remote
        mock.return_value = repo_instance
        yield mock

def test_create_issue(mock_session, mock_user, mock_git_repo):
    """Test creating an issue."""
    session = mock_session.return_value
    session.post.return_value.json.return_value = {
        "number": 1,
        "html_url": "https://github.com/testuser/testrepo/issues/1"
    }
    session.post.return_value.status_code = 201

    result = create_issue(
        title="Test Issue",
        body="Test Description",
        labels=["bug"],
        repo="testrepo"
    )

    assert result["number"] == 1
    session.post.assert_called_once()
    call_args = session.post.call_args
    assert call_args[0][0].endswith("/repos/testuser/testrepo/issues")
    assert call_args[1]["json"]["title"] == "Test Issue"

def test_list_issues(mock_session, mock_user, mock_git_repo):
    """Test listing issues."""
    session = mock_session.return_value
    session.get.return_value.json.return_value = [
        {"number": 1, "title": "Issue 1", "state": "open", "labels": []},
        {"number": 2, "title": "Issue 2", "state": "open", "labels": []}
    ]
    session.get.return_value.status_code = 200

    results = list_issues(repo="testrepo")

    assert len(results) == 2
    assert results[0]["number"] == 1
    session.get.assert_called_once()

def test_get_issue(mock_session, mock_user, mock_git_repo):
    """Test getting single issue."""
    session = mock_session.return_value
    session.get.return_value.json.return_value = {
        "number": 1,
        "title": "Test Issue",
        "state": "open",
        "user": {"login": "author"},
        "created_at": "2023-01-01T00:00:00Z",
        "html_url": "url"
    }
    session.get.return_value.status_code = 200

    result = get_issue(1, repo="testrepo")

    assert result["number"] == 1
    session.get.assert_called_once()
    assert session.get.call_args[0][0].endswith("/issues/1")

def test_close_issue(mock_session, mock_user, mock_git_repo):
    """Test closing an issue."""
    session = mock_session.return_value
    session.patch.return_value.status_code = 200

    result = close_issue(1, comment="Done", repo="testrepo")

    assert result is True
    # Should post comment and patch issue
    assert session.post.called
    assert session.patch.called
    assert session.patch.call_args[1]["json"]["state"] == "closed"

def test_update_issue(mock_session, mock_user, mock_git_repo):
    """Test updating an issue."""
    session = mock_session.return_value
    session.patch.return_value.json.return_value = {"number": 1}
    session.patch.return_value.status_code = 200

    result = update_issue(1, title="New Title", repo="testrepo")

    assert result is not None
    session.patch.assert_called_once()
    assert session.patch.call_args[1]["json"]["title"] == "New Title"
