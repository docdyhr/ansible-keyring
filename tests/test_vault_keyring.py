"""Behavioral tests for vault-keyring.py."""

import getpass
import sys
import types

import pytest

from tests.conftest import install_fake_ansible_modules, load_module


def install_fake_keyring(monkeypatch, secret="stored-secret"):
    """Install a minimal keyring shim and record calls."""
    calls = {"get": [], "set": []}
    keyring_module = types.ModuleType("keyring")

    def get_password(service, username):
        calls["get"].append((service, username))
        return secret

    def set_password(service, username, password):
        calls["set"].append((service, username, password))

    keyring_module.get_password = get_password
    keyring_module.set_password = set_password
    monkeypatch.setitem(sys.modules, "keyring", keyring_module)
    return calls


def test_vault_keyring_reads_password_from_ansible_config(monkeypatch, stdio_buffers):
    """Default execution should print the configured secret."""
    install_fake_ansible_modules(monkeypatch, username="ci-user", keyname="ci-vault")
    calls = install_fake_keyring(monkeypatch, secret="vault-secret")
    module = load_module("vault_keyring_read", "vault-keyring.py")
    monkeypatch.setattr(sys, "argv", ["vault-keyring.py"])

    with pytest.raises(SystemExit) as exc:
        module.main()

    stdout, stderr = stdio_buffers
    assert exc.value.code == 0
    assert stdout.getvalue() == "vault-secret\n"
    assert stderr.getvalue() == ""
    assert calls["get"] == [("ci-vault", "ci-user")]


def test_vault_keyring_set_stores_password(monkeypatch, stdio_buffers):
    """Set mode should persist the password after confirmation."""
    install_fake_ansible_modules(monkeypatch)
    calls = install_fake_keyring(monkeypatch)
    module = load_module("vault_keyring_set", "vault-keyring.py")
    prompts = iter(["new-secret", "new-secret"])
    monkeypatch.setattr(getpass, "getpass", lambda prompt="": next(prompts))
    monkeypatch.setattr(sys, "argv", ["vault-keyring.py", "set"])

    with pytest.raises(SystemExit) as exc:
        module.main()

    stdout, stderr = stdio_buffers
    assert exc.value.code == 0
    assert "Storing password" in stdout.getvalue()
    assert stderr.getvalue() == ""
    assert calls["set"] == [("ansible_key_test", "test_user", "new-secret")]


def test_vault_keyring_set_rejects_mismatched_confirmation(monkeypatch, stdio_buffers):
    """Set mode should fail fast when the confirmation does not match."""
    install_fake_ansible_modules(monkeypatch)
    calls = install_fake_keyring(monkeypatch)
    module = load_module("vault_keyring_mismatch", "vault-keyring.py")
    prompts = iter(["first-secret", "second-secret"])
    monkeypatch.setattr(getpass, "getpass", lambda prompt="": next(prompts))
    monkeypatch.setattr(sys, "argv", ["vault-keyring.py", "set"])

    with pytest.raises(SystemExit) as exc:
        module.main()

    stdout, stderr = stdio_buffers
    assert exc.value.code == 1
    assert "Storing password" in stdout.getvalue()
    assert "Passwords do not match" in stderr.getvalue()
    assert calls["set"] == []
