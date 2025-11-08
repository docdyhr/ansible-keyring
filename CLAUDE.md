# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Ansible project that integrates macOS Keychain (via Python's `keyring` module) with Ansible Vault to securely manage passwords without storing them in files. The project provides multiple approaches to retrieve vault passwords from the system keychain.

## Architecture

### Core Components

1. **vault-keyring.py** - Legacy vault password script that reads from ansible.cfg `[vault]` section
   - Used with `--vault-password-file` or configured in ansible.cfg
   - Requires `username` and `keyname` settings in ansible.cfg
   - Command: `./vault-keyring.py set` to store password
   
2. **vault-keyring-client.py** - Modern vault password client with `--vault-id` support
   - Supports multiple vault IDs without ansible.cfg configuration
   - Falls back to ansible.cfg `[vault]` section if present
   - Command: `./vault-keyring-client.py --vault-id <id> --username <user> --set`
   
3. **get_pass.py** - Simple keyring retrieval script for pipe lookup plugin
   - Hardcoded LABEL and ACCOUNT_NAME (test/test by default)
   - Used with: `{{ lookup('pipe', './get_pass.py') }}`

### Configuration

**ansible.cfg** defines:
- `vault_password_file = vault-keyring.py` - Default vault password script
- `[vault]` section with `username` and `keyname` for vault-keyring.py

## Common Commands

### Prerequisites Setup

```bash
# Install keyring module
python3 -m pip install keyring

# Install community.general collection (for keyring lookup plugin)
ansible-galaxy collection install community.general

# Verify collection installation
ansible-galaxy collection verify community.general -vvv
ansible-doc -t lookup keyring
```

### Keyring Password Management

```bash
# Set password using vault-keyring.py (reads ansible.cfg)
./vault-keyring.py set

# Set password using vault-keyring-client.py (explicit vault-id)
./vault-keyring-client.py --vault-id ansible_key_test --username test_user --set

# Test password retrieval
./vault-keyring.py
./vault-keyring-client.py --vault-id ansible_key_test --username test_user

# Direct keyring CLI commands
keyring set <service> <username>    # Store password
keyring get <service> <username>    # Retrieve password
```

### Ansible Vault Operations

```bash
# Encrypt files
ansible-vault encrypt vars/api_key.yml

# View encrypted files (uses ansible.cfg vault_password_file)
ansible-vault view vars/api_key.yml

# View with explicit vault-keyring-client.py
ansible-vault view vars/api_key.yml --vault-id ansible_key_test@vault-keyring-client.py

# View with explicit vault-keyring.py
ansible-vault view vars/api_key.yml --vault-password-file vault-keyring.py
```

### Running Playbooks

```bash
# Test community.general.keyring lookup plugin
ansible-playbook playbook_keyring.yml

# Test pipe lookup plugin with various scripts
ansible-playbook playbook_pipe.yml

# Test vault with encrypted vars (uses ansible.cfg settings)
ansible-playbook playbook_vault.yml

# With explicit vault-keyring-client.py
ansible-playbook --vault-id ansible_key_test@vault-keyring-client.py playbook_vault.yml

# With explicit vault-keyring.py
ansible-playbook --vault-id vault-keyring.py playbook_vault.yml
```

## Key Technical Details

### Python Shebang

All Python scripts use `#!/usr/bin/env python3` - must match system Python 3 installation with keyring module.

### Executable Permissions

Vault scripts MUST have executable permissions or Ansible will treat them as password files:

```bash
chmod +x vault-keyring.py vault-keyring-client.py get_pass.py
```

### vault-keyring-client.py Behavior

- When called with `--vault-id`, uses that as the keyring service name
- Without `--vault-id`, defaults to 'ansible' as service name
- Username resolution order: `--username` arg > ansible.cfg `[vault].username` > `$USER`
- Exit code 2 if password not found in keyring

### Security Note

The project README recommends storing vault password scripts outside source control (e.g., `~/.ansible/`) for better security. The scripts in this repo are examples.

## Known Issues

**Issue #1**: community.general.keyring lookup fails on macOS systems with multiple Python versions installed. Use the pipe lookup method with get_pass.py or vault-keyring scripts as workaround.

## Testing Setup

Default test credentials (as documented):
- Service/Label: `test`
- Username: `test`
- Password: `test` (set via `keyring set test test`)

For vault-keyring scripts:
- Keyname: `ansible_key_test`
- Username: `test_user`
