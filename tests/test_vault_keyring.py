"""
Tests for vault-keyring.py script.
"""

import getpass
import os
import sys
from unittest.mock import patch, MagicMock

import importlib
import importlib.util

import pytest

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _import_vault_keyring():
    """Import vault-keyring.py as a module (handles hyphen in filename)."""
    spec = importlib.util.spec_from_file_location(
        "vault_keyring", os.path.join(SCRIPT_DIR, "vault-keyring.py")
    )
    module = importlib.util.module_from_spec(spec)
    with patch.dict("sys.modules", {"keyring": MagicMock()}):
        spec.loader.exec_module(module)
    return module


def _import_vault_keyring_client():
    """Import vault-keyring-client.py as a module."""
    spec = importlib.util.spec_from_file_location(
        "vault_keyring_client", os.path.join(SCRIPT_DIR, "vault-keyring-client.py")
    )
    module = importlib.util.module_from_spec(spec)
    with patch.dict("sys.modules", {"keyring": MagicMock()}):
        spec.loader.exec_module(module)
    return module


class TestFindAnsibleCfg:
    """Tests for _find_ansible_cfg function."""

    def test_finds_ansible_cfg_via_env_var(self, tmp_path):
        cfg_file = tmp_path / "custom_ansible.cfg"
        cfg_file.write_text("[defaults]\n")
        mod = _import_vault_keyring()
        with patch.dict(os.environ, {"ANSIBLE_CONFIG": str(cfg_file)}):
            result = mod._find_ansible_cfg()
        assert result == str(cfg_file)

    def test_env_var_missing_file_skipped(self, tmp_path):
        mod = _import_vault_keyring()
        with patch.dict(os.environ, {"ANSIBLE_CONFIG": "/nonexistent/ansible.cfg"}):
            with patch("os.getcwd", return_value=str(tmp_path)):
                result = mod._find_ansible_cfg()
        assert result is None

    def test_finds_ansible_cfg_in_cwd(self, tmp_path):
        cfg_file = tmp_path / "ansible.cfg"
        cfg_file.write_text("[defaults]\n")
        mod = _import_vault_keyring()
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("ANSIBLE_CONFIG", None)
            with patch("os.getcwd", return_value=str(tmp_path)):
                result = mod._find_ansible_cfg()
        assert result == str(cfg_file)

    def test_returns_none_when_no_config(self, tmp_path):
        mod = _import_vault_keyring()
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("ANSIBLE_CONFIG", None)
            with patch("os.getcwd", return_value=str(tmp_path)):
                with patch("os.path.isfile", return_value=False):
                    result = mod._find_ansible_cfg()
        assert result is None


class TestGetVaultConfig:
    """Tests for _get_vault_config function."""

    def test_reads_vault_section(self, tmp_path):
        cfg_file = tmp_path / "ansible.cfg"
        cfg_file.write_text(
            "[defaults]\n"
            "inventory = hosts\n\n"
            "[vault]\n"
            "username = test_user\n"
            "keyname = my_vault_key\n"
        )
        mod = _import_vault_keyring()
        with patch.object(mod, "_find_ansible_cfg", return_value=str(cfg_file)):
            username, keyname = mod._get_vault_config()
        assert username == "test_user"
        assert keyname == "my_vault_key"

    def test_missing_vault_section(self, tmp_path):
        cfg_file = tmp_path / "ansible.cfg"
        cfg_file.write_text("[defaults]\ninventory = hosts\n")
        mod = _import_vault_keyring()
        with patch.object(mod, "_find_ansible_cfg", return_value=str(cfg_file)):
            username, keyname = mod._get_vault_config()
        assert username is None
        assert keyname is None

    def test_no_config_file(self):
        mod = _import_vault_keyring()
        with patch.object(mod, "_find_ansible_cfg", return_value=None):
            username, keyname = mod._get_vault_config()
        assert username is None
        assert keyname is None

    def test_partial_vault_section(self, tmp_path):
        cfg_file = tmp_path / "ansible.cfg"
        cfg_file.write_text("[vault]\nusername = only_user\n")
        mod = _import_vault_keyring()
        with patch.object(mod, "_find_ansible_cfg", return_value=str(cfg_file)):
            username, keyname = mod._get_vault_config()
        assert username == "only_user"
        assert keyname is None


class TestVaultKeyringClientArgParser:
    """Tests for vault-keyring-client.py argument parser."""

    def test_build_arg_parser_defaults(self):
        mod = _import_vault_keyring_client()
        parser = mod.build_arg_parser()
        args = parser.parse_args([])
        assert args.vault_id is None
        assert args.username is None
        assert args.set_password is False

    def test_build_arg_parser_vault_id(self):
        mod = _import_vault_keyring_client()
        parser = mod.build_arg_parser()
        args = parser.parse_args(["--vault-id", "my_vault"])
        assert args.vault_id == "my_vault"

    def test_build_arg_parser_username(self):
        mod = _import_vault_keyring_client()
        parser = mod.build_arg_parser()
        args = parser.parse_args(["--username", "admin"])
        assert args.username == "admin"

    def test_build_arg_parser_set(self):
        mod = _import_vault_keyring_client()
        parser = mod.build_arg_parser()
        args = parser.parse_args(["--set"])
        assert args.set_password is True

    def test_build_arg_parser_all_options(self):
        mod = _import_vault_keyring_client()
        parser = mod.build_arg_parser()
        args = parser.parse_args(
            ["--vault-id", "prod", "--username", "deploy", "--set"]
        )
        assert args.vault_id == "prod"
        assert args.username == "deploy"
        assert args.set_password is True


class TestVaultKeyringMain:
    """Behavioral tests for vault-keyring.py main()."""

    def test_reads_password_from_config(self, capsys, monkeypatch):
        """Default execution prints the configured secret."""
        mod = _import_vault_keyring()
        mock_keyring = MagicMock()
        mock_keyring.get_password.return_value = "vault-secret"
        monkeypatch.setattr(mod, "keyring", mock_keyring)
        monkeypatch.setattr(mod, "_get_vault_config", lambda: ("ci-user", "ci-vault"))
        monkeypatch.setattr(sys, "argv", ["vault-keyring.py"])

        with pytest.raises(SystemExit) as exc:
            mod.main()

        out, err = capsys.readouterr()
        assert exc.value.code == 0
        assert out == "vault-secret\n"
        assert err == ""
        mock_keyring.get_password.assert_called_once_with("ci-vault", "ci-user")

    def test_set_stores_password(self, capsys, monkeypatch):
        """Set mode persists the password after confirmation."""
        mod = _import_vault_keyring()
        mock_keyring = MagicMock()
        monkeypatch.setattr(mod, "keyring", mock_keyring)
        monkeypatch.setattr(
            mod, "_get_vault_config", lambda: ("test_user", "ansible_key_test")
        )
        prompts = iter(["new-secret", "new-secret"])
        monkeypatch.setattr(getpass, "getpass", lambda prompt="": next(prompts))
        monkeypatch.setattr(sys, "argv", ["vault-keyring.py", "set"])

        with pytest.raises(SystemExit) as exc:
            mod.main()

        out, err = capsys.readouterr()
        assert exc.value.code == 0
        assert "Storing password" in out
        assert err == ""
        mock_keyring.set_password.assert_called_once_with(
            "ansible_key_test", "test_user", "new-secret"
        )

    def test_set_rejects_mismatched_confirmation(self, capsys, monkeypatch):
        """Set mode fails when confirmation does not match."""
        mod = _import_vault_keyring()
        mock_keyring = MagicMock()
        monkeypatch.setattr(mod, "keyring", mock_keyring)
        monkeypatch.setattr(
            mod, "_get_vault_config", lambda: ("test_user", "ansible_key_test")
        )
        prompts = iter(["first-secret", "second-secret"])
        monkeypatch.setattr(getpass, "getpass", lambda prompt="": next(prompts))
        monkeypatch.setattr(sys, "argv", ["vault-keyring.py", "set"])

        with pytest.raises(SystemExit) as exc:
            mod.main()

        out, err = capsys.readouterr()
        assert exc.value.code == 1
        assert "Storing password" in out
        assert "Passwords do not match" in err
        mock_keyring.set_password.assert_not_called()
