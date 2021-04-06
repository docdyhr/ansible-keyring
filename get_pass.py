#!/usr/bin/env python3

import keyring

LABEL = "test"
ACCOUNT_NAME = "test"

PASSWD = keyring.get_password(LABEL, ACCOUNT_NAME)

print(PASSWD)
