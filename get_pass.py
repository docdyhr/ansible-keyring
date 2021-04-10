#!/usr/bin/env python3

# Ansible-vault python keyring / keychain script 
# https://docs.ansible.com/ansible/latest/user_guide/vault.html#storing-passwords-in-third-party-tools-with-vault-password-client-scripts

import keyring

LABEL = "test"
ACCOUNT_NAME = "test"

PASSWD = keyring.get_password(LABEL, ACCOUNT_NAME)

print(PASSWD)
