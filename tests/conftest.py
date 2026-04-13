"""
Shared pytest fixtures for ansible-keyring tests.
"""

import importlib.util
import pathlib
import sys
import types

import pytest


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


def load_module(module_name, filename):
    """Load a repository script as a Python module for direct testing."""
    spec = importlib.util.spec_from_file_location(module_name, REPO_ROOT / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def install_fake_ansible_modules(
    monkeypatch, username="test_user", keyname="ansible_key_test"
):
    """Provide a minimal ansible.config.manager shim for script imports."""
    ansible_module = types.ModuleType("ansible")
    config_module = types.ModuleType("ansible.config")
    manager_module = types.ModuleType("ansible.config.manager")

    class DummyConfigManager:
        def __init__(self):
            self._config_file = "ansible.cfg"
            self._parsers = {
                self._config_file: {"vault": {"username": username, "keyname": keyname}}
            }

    def get_ini_config_value(parser, query):
        return parser.get(query["section"], {}).get(query["key"])

    manager_module.ConfigManager = DummyConfigManager
    manager_module.get_ini_config_value = get_ini_config_value
    config_module.manager = manager_module
    ansible_module.config = config_module

    monkeypatch.setitem(sys.modules, "ansible", ansible_module)
    monkeypatch.setitem(sys.modules, "ansible.config", config_module)
    monkeypatch.setitem(sys.modules, "ansible.config.manager", manager_module)


@pytest.fixture
def stdio_buffers(capsys):
    """Capture stdout and stderr for scripts that write directly to sys streams."""
    capsys.readouterr()  # clear any pre-test output
    _cache = {}

    def _read():
        if "captured" not in _cache:
            _cache["captured"] = capsys.readouterr()
        return _cache["captured"]

    class Buffer:
        def __init__(self, stream):
            self._stream = stream

        def getvalue(self):
            return getattr(_read(), self._stream)

    return Buffer("out"), Buffer("err")


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
