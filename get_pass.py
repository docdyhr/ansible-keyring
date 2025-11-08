#!/usr/bin/env python3

# Ansible-vault python keyring / keychain script
# https://docs.ansible.com/ansible/latest/user_guide/vault.html#storing-passwords-in-third-party-tools-with-vault-password-client-scripts

import sys
import logging
import keyring

# Configure logging
logging.basicConfig(
    level=logging.ERROR, format="%(levelname)s: %(message)s", stream=sys.stderr
)
logger = logging.getLogger(__name__)

LABEL = "test"
ACCOUNT_NAME = "test"

PASSWD = keyring.get_password(LABEL, ACCOUNT_NAME)

if PASSWD is None:
    logger.error(
        "Password not found for service '%s' and account '%s'", LABEL, ACCOUNT_NAME
    )
    logger.error(
        "Please set the password using: keyring set %s %s", LABEL, ACCOUNT_NAME
    )
    sys.exit(1)

print(PASSWD)
