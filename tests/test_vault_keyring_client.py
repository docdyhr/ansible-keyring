"""Behavioral tests for vault-keyring-client.py."""

import getpass
import os
import sys
from unittest.mock import patch, MagicMock

import importlib.util

import pytest

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _import_vault_keyring_client():
    """Import vault-keyring-client.py as a module (handles hyphen in filename)."""
    spec = importlib.util.spec_from_file_location(
        "vault_keyring_client_behav",
        os.path.join(SCRIPT_DIR, "vault-keyring-client.py"),
    )
    module = importlib.util.module_from_spec(spec)
    with patch.dict("sys.modules", {"keyring": MagicMock()}):
        spec.loader.exec_module(module)
    return module


class TestVaultKeyringClientMain:
    """Behavioral tests for vault-keyring-client.py main()."""

    def test_uses_cli_overrides(self, capsys, monkeypatch):
        """CLI --vault-id and --username take precedence over ansible.cfg."""
        mod = _import_vault_keyring_client()
        mock_keyring = MagicMock()
        mock_keyring.get_password.return_value = "override-secret"
        monkeypatch.setattr(mod, "keyring", mock_keyring)
        monkeypatch.setattr(
            mod, "_get_vault_config", lambda: ("config-user", "config-key")
        )
        monkeypatch.setattr(
            sys,
            "argv",
            ["vault-keyring-client.py", "--vault-id", "cli-key", "--username", "cli-user"],
        )

        with pytest.raises(SystemExit) as exc:
            mod.main()

        out, err = capsys.readouterr()
        assert exc.value.code == 0
        assert out == "override-secret\n"
        assert err == ""
        mock_keyring.get_password.assert_called_once_with("cli-key", "cli-user")

    def test_returns_rc_2_when_secret_is_missing(self, capsys, monkeypatch):
        """Missing keyring entry exits with KEYNAME_UNKNOWN_RC (2)."""
        mod = _import_vault_keyring_client()
        mock_keyring = MagicMock()
        mock_keyring.get_password.return_value = None
        mock_keyring.get_keyring.return_value = MagicMock(name="ci-backend")
        mock_keyring.get_keyring.return_value.name = "ci-backend"
        monkeypatch.setattr(mod, "keyring", mock_keyring)
        monkeypatch.setattr(
            mod, "_get_vault_config", lambda: ("test_user", "ansible_key_test")
        )
        monkeypatch.setattr(
            sys, "argv", ["vault-keyring-client.py", "--vault-id", "missing-key"]
        )

        with pytest.raises(SystemExit) as exc:
            mod.main()

        out, err = capsys.readouterr()
        assert exc.value.code == mod.KEYNAME_UNKNOWN_RC
        assert out == ""
        assert 'key="missing-key"' in err
        assert 'backend="ci-backend"' in err

    def test_set_stores_password(self, capsys, monkeypatch):
        """Set mode writes the confirmed password to the keyring."""
        mod = _import_vault_keyring_client()
        mock_keyring = MagicMock()
        monkeypatch.setattr(mod, "keyring", mock_keyring)
        monkeypatch.setattr(
            mod, "_get_vault_config", lambda: ("test_user", "ansible_key_test")
        )
        prompts = iter(["new-client-secret", "new-client-secret"])
        monkeypatch.setattr(getpass, "getpass", lambda prompt="": next(prompts))
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "vault-keyring-client.py",
                "--vault-id", "project-secret",
                "--username", "override-user",
                "--set",
            ],
        )

        with pytest.raises(SystemExit) as exc:
            mod.main()

        out, err = capsys.readouterr()
        assert exc.value.code == 0
        assert "Storing password" in out
        assert err == ""
        mock_keyring.set_password.assert_called_once_with(
            "project-secret", "override-user", "new-client-secret"
        )

    def test_set_rejects_mismatched_confirmation(self, capsys, monkeypatch):
        """Set mode fails fast when confirmation does not match."""
        mod = _import_vault_keyring_client()
        mock_keyring = MagicMock()
        monkeypatch.setattr(mod, "keyring", mock_keyring)
        monkeypatch.setattr(
            mod, "_get_vault_config", lambda: ("test_user", "ansible_key_test")
        )
        prompts = iter(["first-secret", "second-secret"])
        monkeypatch.setattr(getpass, "getpass", lambda prompt="": next(prompts))
        monkeypatch.setattr(
            sys,
            "argv",
            ["vault-keyring-client.py", "--vault-id", "some-key", "--set"],
        )

        with pytest.raises(SystemExit) as exc:
            mod.main()

        out, err = capsys.readouterr()
        assert exc.value.code == 1
        assert "Storing password" in out
        assert "Passwords do not match" in err
        mock_keyring.set_password.assert_not_called()
