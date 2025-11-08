"""
Test Python scripts for syntax errors and basic structure.
"""

import pytest
import py_compile
import os
import subprocess


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.parametrize(
    "script",
    [
        "get_pass.py",
        "vault-keyring.py",
        "vault-keyring-client.py",
    ],
)
def test_python_syntax(script):
    """Test that Python scripts have valid syntax."""
    script_path = os.path.join(SCRIPT_DIR, script)

    try:
        py_compile.compile(script_path, doraise=True)
    except py_compile.PyCompileError as e:
        pytest.fail(f"Syntax error in {script}: {e}")


@pytest.mark.parametrize(
    "script",
    [
        "get_pass.py",
        "vault-keyring.py",
        "vault-keyring-client.py",
    ],
)
def test_script_has_shebang(script):
    """Test that Python scripts have proper shebang."""
    script_path = os.path.join(SCRIPT_DIR, script)

    with open(script_path, "r") as f:
        first_line = f.readline().strip()

    assert first_line.startswith("#!"), f"{script} missing shebang"
    assert "python" in first_line.lower(), f"{script} shebang doesn't reference python"


@pytest.mark.parametrize(
    "script",
    [
        "get_pass.py",
        "get_pass.sh",
        "vault-keyring.py",
        "vault-keyring-client.py",
    ],
)
def test_script_is_executable(script):
    """Test that scripts have executable permissions."""
    script_path = os.path.join(SCRIPT_DIR, script)

    if not os.path.exists(script_path):
        pytest.skip(f"{script} not found")

    is_executable = os.access(script_path, os.X_OK)
    assert is_executable, f"{script} is not executable. Run: chmod +x {script}"


@pytest.mark.parametrize(
    "playbook",
    [
        "playbook_keyring.yml",
        "playbook_pipe.yml",
        "playbook_vault.yml",
    ],
)
def test_ansible_playbook_syntax(playbook):
    """Test that Ansible playbooks have valid syntax."""
    playbook_path = os.path.join(SCRIPT_DIR, playbook)

    if not os.path.exists(playbook_path):
        pytest.skip(f"{playbook} not found")

    # Try to check playbook syntax with ansible-playbook
    # This will fail if ansible is not installed, which is acceptable
    try:
        result = subprocess.run(
            ["ansible-playbook", "--syntax-check", playbook_path],
            capture_output=True,
            text=True,
            timeout=10,
        )

        # We don't assert success because vault password file might not be set up
        # Just check that the file can be parsed
        if result.returncode != 0 and "syntax" in result.stderr.lower():
            pytest.fail(f"Syntax error in {playbook}: {result.stderr}")

    except FileNotFoundError:
        pytest.skip("ansible-playbook not installed")
    except subprocess.TimeoutExpired:
        pytest.fail(f"Playbook syntax check timed out for {playbook}")


def test_requirements_txt_exists():
    """Test that requirements.txt exists and is not empty."""
    requirements_path = os.path.join(SCRIPT_DIR, "requirements.txt")

    assert os.path.exists(requirements_path), "requirements.txt not found"

    with open(requirements_path, "r") as f:
        content = f.read().strip()

    # Should have at least ansible and keyring
    assert "ansible" in content.lower(), "ansible not in requirements.txt"
    assert "keyring" in content.lower(), "keyring not in requirements.txt"


def test_readme_exists():
    """Test that README.md exists and has content."""
    readme_path = os.path.join(SCRIPT_DIR, "README.md")

    assert os.path.exists(readme_path), "README.md not found"

    with open(readme_path, "r") as f:
        content = f.read().strip()

    assert len(content) > 100, "README.md seems too short"
    assert "ansible" in content.lower(), "README.md should mention ansible"
    assert "keyring" in content.lower(), "README.md should mention keyring"


def test_license_exists():
    """Test that LICENSE file exists."""
    license_path = os.path.join(SCRIPT_DIR, "LICENSE")

    assert os.path.exists(license_path), "LICENSE file not found"

    with open(license_path, "r") as f:
        content = f.read().strip()

    assert "MIT" in content or "Copyright" in content, "LICENSE file seems invalid"
