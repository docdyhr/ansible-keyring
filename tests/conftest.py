"""
Shared pytest fixtures for ansible-keyring tests.
"""

import pytest


@pytest.fixture
def mock_keyring_service():
    """Mock keyring service name for testing."""
    return "test"


@pytest.fixture
def mock_keyring_username():
    """Mock keyring username for testing."""
    return "test"


@pytest.fixture
def mock_password():
    """Mock password for testing."""
    return "test_password_123"


@pytest.fixture
def mock_ansible_config():
    """Mock ansible configuration dict."""
    return {"vault": {"username": "test_user", "keyname": "ansible_key_test"}}
