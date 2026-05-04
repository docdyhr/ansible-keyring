# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Fixed
- Replace deprecated `lgtm[]` CodeQL suppression annotations with `codeql[]` format in `get_pass.py` and `vault-keyring-client.py`
- Drop Python 3.11 from CI matrix — `ansible>=13.6.0` requires Python ≥3.12; add Python 3.14

### Changed
- Migrated virtual environment from Homebrew Python 3.14.3 to pyenv Python 3.14.4
- Bumped dependency version floors to match current installed versions:
  - `keyring` >=25.6.0 → >=25.7.0
  - `ansible` >=11.0.0 → >=13.6.0
  - `pytest` >=8.0.0 → >=9.0.3
  - `pytest-cov` >=6.0.0 → >=7.1.0
  - `pytest-mock` >=3.14.0 → >=3.15.1
  - `black` >=25.1.0 → >=26.3.1
  - `flake8` >=7.0.0 → >=7.3.0
  - `pylint` >=3.0.0 → >=4.0.5
  - `pip-audit` >=2.7.0 → >=2.10.0
  - `mypy` >=1.8.0 → >=1.20.2
- pip-audit clean: no known vulnerabilities

## [Earlier changes]

- fix: move CodeQL suppression comments to flagged expression lines
- ci: drop Python 3.10, fix Black formatting, restore Ansible syntax check
- Fix 6 CodeQL code scanning alerts
- Fix test capture, add behavioral tests, bump GitHub Actions to Node 24
- Fix Issue #3: replace Ansible private API with configparser, fix CI/CD pipeline
- Fix CVE: update black to >=26.3.1 to patch arbitrary file write vulnerability
- Add testing infrastructure and contribution guidelines
