# Contributing to ansible-keyring

Thank you for your interest in contributing to ansible-keyring! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)

## Code of Conduct

This project follows a simple code of conduct: **Be respectful, be professional, be constructive.**

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ansible-keyring.git
   cd ansible-keyring
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/docdyhr/ansible-keyring.git
   ```
4. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

## How to Contribute

### Types of Contributions

We welcome several types of contributions:

- **Bug fixes** - Fix issues in existing code
- **Feature enhancements** - Add new functionality
- **Documentation improvements** - Fix typos, clarify instructions, add examples
- **Testing** - Add or improve test coverage
- **Platform support** - Extend to Linux, Windows, other keychains

### First Time Contributors

Look for issues tagged with `good first issue` or `help wanted`. These are great entry points for new contributors.

## Development Setup

### Prerequisites

- **Python 3.8+** (preferably from python.org on macOS)
- **Ansible 2.16+**
- **keyring library** (`pip install keyring`)
- **pytest** for testing (`pip install pytest`)

### Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

2. Set up test keyring entries:
   ```bash
   keyring set test test
   # Password: test
   
   keyring set ansible_key_test test_user
   # Password: (your test password)
   ```

3. Make scripts executable:
   ```bash
   chmod +x *.py *.sh
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_get_pass.py

# Run with coverage report
pytest --cov=. --cov-report=html
```

### Testing Playbooks

```bash
# Test playbook syntax
ansible-playbook --syntax-check playbook_*.yml

# Run playbooks (requires keyring setup)
ansible-playbook playbook_pipe.yml
ansible-playbook playbook_vault.yml
```

## Coding Standards

### Python Code Style

- **PEP 8** compliance for Python code
- **Line length**: Maximum 100 characters (prefer 88 for Black compatibility)
- **Indentation**: 4 spaces (no tabs)
- **Imports**: Group in order (stdlib, third-party, local)
- **Docstrings**: Use for all public functions and modules

### Example Code Style

```python
#!/usr/bin/env python3
"""
Brief module description.

Longer description if needed.
"""

import sys
import logging
from typing import Optional

import keyring
from ansible.config.manager import ConfigManager


def get_password(service: str, username: str) -> Optional[str]:
    """
    Retrieve password from system keyring.
    
    Args:
        service: The keyring service name
        username: The username to retrieve password for
        
    Returns:
        Password string if found, None otherwise
    """
    try:
        return keyring.get_password(service, username)
    except Exception as e:
        logging.error(f"Failed to retrieve password: {e}")
        return None
```

### Shell Script Style

- Use `#!/usr/bin/env bash` shebang
- Quote all variables: `"$VARIABLE"`
- Use meaningful variable names (UPPERCASE for environment vars)
- Add comments explaining non-obvious logic

### Ansible Playbook Style

- Use YAML document markers (`---` and `...`)
- Clear, descriptive task names
- Proper indentation (2 spaces)
- Comments for complex logic

## Testing

### Test Requirements

All contributions should include appropriate tests:

- **Bug fixes**: Add test that would have caught the bug
- **New features**: Add tests covering the new functionality
- **Code changes**: Ensure existing tests still pass

### Test Structure

```
tests/
├── test_get_pass.py          # Tests for get_pass.py
├── test_vault_keyring.py      # Tests for vault-keyring.py
├── test_vault_keyring_client.py  # Tests for vault-keyring-client.py
└── conftest.py                # Shared fixtures
```

### Writing Tests

```python
import pytest
from unittest.mock import patch, MagicMock


def test_get_password_success():
    """Test successful password retrieval."""
    with patch('keyring.get_password', return_value='test_password'):
        result = get_password('test', 'test')
        assert result == 'test_password'


def test_get_password_not_found():
    """Test handling of missing password."""
    with patch('keyring.get_password', return_value=None):
        result = get_password('test', 'test')
        assert result is None
```

## Pull Request Process

### Before Submitting

1. **Update your branch** with latest upstream:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests** and ensure they pass:
   ```bash
   pytest
   ```

3. **Check code style**:
   ```bash
   # If you have these tools installed:
   black --check .
   flake8 .
   ```

4. **Update documentation** if needed:
   - README.md for user-facing changes
   - CLAUDE.md for architectural changes
   - Docstrings for code changes

### Submitting Pull Request

1. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request** on GitHub with:
   - **Clear title**: "Fix: Issue with keyring on Python 3.12"
   - **Description**: What changed and why
   - **Related issues**: "Fixes #123" or "Relates to #456"
   - **Testing done**: How you tested the changes

3. **PR Template** (use this as a guide):
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Code refactoring
   
   ## Testing
   - [ ] Tests pass locally
   - [ ] Added new tests for changes
   - [ ] Tested on macOS [version]
   - [ ] Tested with Python [version]
   - [ ] Tested with Ansible [version]
   
   ## Checklist
   - [ ] Code follows project style guidelines
   - [ ] Documentation updated
   - [ ] No new warnings introduced
   ```

### Review Process

- Maintainer will review your PR
- Address any feedback or requested changes
- Once approved, maintainer will merge

### After Merge

1. **Update your local repository**:
   ```bash
   git checkout main
   git pull upstream main
   ```

2. **Delete your feature branch**:
   ```bash
   git branch -d feature/your-feature-name
   git push origin --delete feature/your-feature-name
   ```

## Reporting Bugs

### Before Reporting

1. **Search existing issues** to avoid duplicates
2. **Try latest version** - bug might already be fixed
3. **Verify it's a bug** - check documentation

### Bug Report Template

When creating an issue, include:

```markdown
**Environment:**
- macOS version: [e.g., macOS 14.0 Sonoma]
- Python version: [e.g., 3.11.5]
- Ansible version: [e.g., 12.2.0]
- keyring version: [e.g., 25.6.0]
- Installation method: [pip, homebrew, python.org, etc.]

**Description:**
Clear description of the bug

**Steps to Reproduce:**
1. Step one
2. Step two
3. See error

**Expected Behavior:**
What you expected to happen

**Actual Behavior:**
What actually happened

**Error Messages:**
```
Paste any error messages or logs here
```

**Additional Context:**
Any other relevant information
```

## Suggesting Enhancements

### Enhancement Request Template

```markdown
**Feature Description:**
Brief description of the proposed feature

**Use Case:**
Why is this feature needed? What problem does it solve?

**Proposed Solution:**
How would you implement this?

**Alternatives Considered:**
Other approaches you've thought about

**Additional Context:**
Any other relevant information, examples, screenshots, etc.
```

## Questions?

- **Issues**: Open an issue with the `question` label
- **Discussions**: Use GitHub Discussions for general questions
- **Email**: Contact the maintainer for private inquiries

## License

By contributing, you agree that your contributions will be licensed under the MIT License, the same license as the project.

---

Thank you for contributing to ansible-keyring! 🎉
