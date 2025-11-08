#!/usr/bin/env python3

# Ansible-vault python keyring / keychain script 
# https://docs.ansible.com/ansible/latest/user_guide/vault.html#storing-passwords-in-third-party-tools-with-vault-password-client-scripts

import sys
import keyring

LABEL = "test"
ACCOUNT_NAME = "test"

PASSWD = keyring.get_password(LABEL, ACCOUNT_NAME)

if PASSWD is None:
    sys.stderr.write(f"Error: Password not found for service '{LABEL}' and account '{ACCOUNT_NAME}'\n")
    sys.stderr.write(f"Please set the password using: keyring set {LABEL} {ACCOUNT_NAME}\n")
    sys.exit(1)

print(PASSWD)
