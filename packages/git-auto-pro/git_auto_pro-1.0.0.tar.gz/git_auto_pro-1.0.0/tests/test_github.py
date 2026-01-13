"""Tests for GitHub integration."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from git_auto_pro.github import (
    validate_token,
    get_stored_token,
    store_token,
)


class TestTokenOperations:
    """Test token storage and retrieval."""
    
    @patch('git_auto_pro.github.keyring')
    def test_store_token(self, mock_keyring):
        """Test storing a token."""
        mock_keyring.set_password = Mock()
        mock_keyring.get_keyring = Mock()
        mock_keyring.delete_password = Mock()
        
        store_token("test_token_123")
        
        mock_keyring.set_password.assert_any_call('git-auto-pro', 'github-token', 'test_token_123')
    
    @patch('git_auto_pro.github.keyring')
    def test_get_stored_token(self, mock_keyring):
        """Test retrieving stored token."""
        mock_keyring.get_password = Mock(return_value="test_token_123")
        
        token = get_stored_token()
        
        assert token == "test_token_123"
    
    @patch('git_auto_pro.github.TOKEN_FILE')
    @patch('git_auto_pro.github.keyring')
    def test_get_stored_token_none(self, mock_keyring, mock_token_file):
        """Test retrieving token when none exists."""
        mock_keyring.get_password = Mock(return_value=None)
        mock_keyring.get_keyring = Mock()
        mock_keyring.set_password = Mock()
        mock_keyring.delete_password = Mock()
        mock_token_file.exists.return_value = False
        
        token = get_stored_token()
        
        assert token is None


class TestTokenValidation:
    """Test token validation."""
    
    @patch('git_auto_pro.github.requests')
    def test_validate_token_success(self, mock_requests):
        """Test successful token validation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"login": "testuser"}
        mock_requests.get.return_value = mock_response
        
        result = validate_token("valid_token")
        
        assert result is True
    
    @patch('git_auto_pro.github.requests')
    def test_validate_token_failure(self, mock_requests):
        """Test failed token validation."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_requests.get.return_value = mock_response
        
        result = validate_token("invalid_token")
        
        assert result is False
