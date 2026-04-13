"""Behavioral tests for vault-keyring-client.py."""

import getpass
import sys
import types

import pytest

from tests.conftest import install_fake_ansible_modules, load_module


def install_fake_keyring(
    monkeypatch, secret="client-secret", backend_name="mock-keyring"
):
    """Install a keyring shim with predictable behavior for client tests."""
    calls = {"get": [], "set": []}
    keyring_module = types.ModuleType("keyring")

    def get_password(service, username):
        calls["get"].append((service, username))
        return secret

    def set_password(service, username, password):
        calls["set"].append((service, username, password))

    def get_keyring():
        return types.SimpleNamespace(name=backend_name)

    keyring_module.get_password = get_password
    keyring_module.set_password = set_password
    keyring_module.get_keyring = get_keyring
    monkeypatch.setitem(sys.modules, "keyring", keyring_module)
    return calls


def test_vault_keyring_client_uses_cli_overrides(monkeypatch, stdio_buffers):
    """CLI values should take precedence over ansible.cfg defaults."""
    install_fake_ansible_modules(
        monkeypatch, username="config-user", keyname="config-key"
    )
    calls = install_fake_keyring(monkeypatch, secret="override-secret")
    module = load_module("vault_keyring_client_overrides", "vault-keyring-client.py")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "vault-keyring-client.py",
            "--vault-id",
            "cli-key",
            "--username",
            "cli-user",
        ],
    )

    with pytest.raises(SystemExit) as exc:
        module.main()

    stdout, stderr = stdio_buffers
    assert exc.value.code == 0
    assert stdout.getvalue() == "override-secret\n"
    assert stderr.getvalue() == ""
    assert calls["get"] == [("cli-key", "cli-user")]


def test_vault_keyring_client_returns_rc_2_when_secret_is_missing(
    monkeypatch, stdio_buffers
):
    """Missing keyring entries should exit with the documented return code."""
    install_fake_ansible_modules(monkeypatch)
    install_fake_keyring(monkeypatch, secret=None, backend_name="ci-backend")
    module = load_module("vault_keyring_client_missing", "vault-keyring-client.py")
    monkeypatch.setattr(
        sys, "argv", ["vault-keyring-client.py", "--vault-id", "missing-key"]
    )

    with pytest.raises(SystemExit) as exc:
        module.main()

    stdout, stderr = stdio_buffers
    assert exc.value.code == module.KEYNAME_UNKNOWN_RC
    assert stdout.getvalue() == ""
    assert 'key="missing-key"' in stderr.getvalue()
    assert 'backend="ci-backend"' in stderr.getvalue()


def test_vault_keyring_client_set_stores_password(monkeypatch, stdio_buffers):
    """Set mode should write the confirmed password to the selected key."""
    install_fake_ansible_modules(monkeypatch)
    calls = install_fake_keyring(monkeypatch)
    module = load_module("vault_keyring_client_set", "vault-keyring-client.py")
    prompts = iter(["new-client-secret", "new-client-secret"])
    monkeypatch.setattr(getpass, "getpass", lambda prompt="": next(prompts))
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "vault-keyring-client.py",
            "--vault-id",
            "project-secret",
            "--username",
            "override-user",
            "--set",
        ],
    )

    with pytest.raises(SystemExit) as exc:
        module.main()

    stdout, stderr = stdio_buffers
    assert exc.value.code == 0
    assert "Storing password" in stdout.getvalue()
    assert stderr.getvalue() == ""
    assert calls["set"] == [("project-secret", "override-user", "new-client-secret")]
