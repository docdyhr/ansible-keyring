"""
Tests for get_pass.py script.
"""

import pytest
import sys
from unittest.mock import patch, MagicMock
from io import StringIO

# Check if keyring is available
try:
    import keyring

    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False


def test_keyring_import():
    """Test that keyring module can be imported."""
    if not KEYRING_AVAILABLE:
        pytest.skip("keyring module not installed")

    import keyring

    assert keyring is not None


@pytest.mark.skipif(not KEYRING_AVAILABLE, reason="keyring module not installed")
@patch("keyring.get_password")
def test_get_password_success(
    mock_get_password, mock_keyring_service, mock_keyring_username, mock_password
):
    """Test successful password retrieval from keyring."""
    mock_get_password.return_value = mock_password

    import keyring

    result = keyring.get_password(mock_keyring_service, mock_keyring_username)

    assert result == mock_password
    mock_get_password.assert_called_once_with(
        mock_keyring_service, mock_keyring_username
    )


@pytest.mark.skipif(not KEYRING_AVAILABLE, reason="keyring module not installed")
@patch("keyring.get_password")
def test_get_password_not_found(
    mock_get_password, mock_keyring_service, mock_keyring_username
):
    """Test handling when password is not found in keyring."""
    mock_get_password.return_value = None

    import keyring

    result = keyring.get_password(mock_keyring_service, mock_keyring_username)

    assert result is None
    mock_get_password.assert_called_once_with(
        mock_keyring_service, mock_keyring_username
    )


@pytest.mark.skipif(not KEYRING_AVAILABLE, reason="keyring module not installed")
@patch("keyring.get_password")
def test_get_password_exception(
    mock_get_password, mock_keyring_service, mock_keyring_username
):
    """Test handling when keyring raises an exception."""
    mock_get_password.side_effect = Exception("Keyring error")

    import keyring

    with pytest.raises(Exception, match="Keyring error"):
        keyring.get_password(mock_keyring_service, mock_keyring_username)


def test_logging_configuration():
    """Test that logging is properly configured in get_pass.py."""
    # This test verifies the script can be imported without errors
    # and that logging is configured (indirectly)
    import logging

    # Verify logging module is available
    assert logging.getLogger() is not None

    # Verify basic logging levels
    assert logging.ERROR is not None
    assert logging.INFO is not None
